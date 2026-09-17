"""
Rubrol Production Server & Sidecar
Fast, multi-format Typst compilation daemon with built-in interactive playground,
template registry, and Turnkey EU Factur-X / ZUGFeRD 2.2 Suite.
"""
import argparse, json, mimetypes, os, sys, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from rubrol.core.engine import RubrolEngine
from rubrol.facturx.validator import validate_facturx_payload, validate_facturx_pdf
from rubrol.facturx.packager import extract_facturx_xml

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class RubrolServerHandler(BaseHTTPRequestHandler):
    engine = RubrolEngine()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            index_file = STATIC_DIR / "index.html"
            if index_file.exists():
                content = index_file.read_bytes()
                self._send_response(200, "text/html; charset=utf-8", content)
            else:
                self.send_error(404, "Index not found")

        elif path in ("/health", "/v1/health"):
            data = {
                "status": "healthy",
                "service": "rubrol-engine",
                "version": "1.0.0",
                "templates_loaded": len(self.engine.template_registry),
                "cached_compilers": len(self.engine._compilers),
                "facturx_suite": True,
                "facturx_version": "1.0.07 / ZUGFeRD 2.2 (EN 16931)"
            }
            self._send_json(200, data)

        elif path == "/v1/templates":
            templates = list(self.engine.template_registry.keys())
            self._send_json(200, {"templates": templates})

        elif path == "/api/sample-data":
            qs = parse_qs(parsed.query)
            tmpl = qs.get("template", ["b2b_invoice"])[0]
            aliases = {
                "facturx_zugferd_invoice": "facturx_invoice",
                "b2b_saas_invoice": "b2b_invoice",
                "proforma_invoice": "b2b_invoice",
                "standard_invoice": "b2b_invoice"
            }
            target_tmpl = aliases.get(tmpl, tmpl)
            json_path = DATA_DIR / f"{target_tmpl}.json"
            if json_path.exists():
                payload = json.loads(json_path.read_text(encoding="utf-8"))
                self._send_json(200, payload)
            else:
                self._send_json(200, {})

        else:
            req_path = path.lstrip("/")
            if req_path in ("favicon.ico", "assets/logo.png"):
                safe_file = ROOT_DIR / "assets" / "logo.png"
            elif req_path.startswith("assets/"):
                safe_file = ROOT_DIR / req_path
            else:
                safe_file = STATIC_DIR / req_path
                if not safe_file.exists() and (STATIC_DIR / f"{req_path}.html").exists():
                    safe_file = STATIC_DIR / f"{req_path}.html"

            if safe_file.exists() and safe_file.is_file():
                mime, _ = mimetypes.guess_type(str(safe_file))
                self._send_response(200, mime or "application/octet-stream", safe_file.read_bytes())
            else:
                self.send_error(404, f"File Not Found: {path}")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/v1/render", "/v1/render/raw"):
            self._handle_render()
        elif path == "/v1/facturx/render":
            self._handle_facturx_render()
        elif path == "/v1/facturx/validate":
            self._handle_facturx_validate()
        elif path == "/v1/facturx/extract":
            self._handle_facturx_extract()
        elif path in ("/api/webhooks/stripe", "/v1/webhooks/stripe"):
            self._handle_stripe_webhook()
        else:
            self.send_error(404, f"Endpoint '{path}' not found")

    def _handle_stripe_webhook(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length).decode("utf-8")
            event = json.loads(raw_body) if raw_body else {}
            from rubrol.webhooks.stripe_fulfillment import process_stripe_event
            result = process_stripe_event(event)
            self._send_json(200, result)
        except Exception as e:
            self._send_json(400, {"error": str(e)})

    def _handle_render(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length).decode("utf-8")
            body = json.loads(raw_body) if raw_body else {}

            template = body.get("template")
            template_src = body.get("template_src")
            data = body.get("data", {})
            out_format = body.get("format", "pdf").lower()
            pdf_standard = body.get("pdf_standard", "a-2b")

            if template_src:
                output_bytes, elapsed_ms = self.engine.render_source(
                    source_code=template_src,
                    data=data,
                    output_format=out_format,
                    pdf_standard=pdf_standard
                )
            elif template:
                output_bytes, elapsed_ms = self.engine.render(
                    template=template,
                    data=data,
                    output_format=out_format,
                    pdf_standard=pdf_standard
                )
            else:
                raise ValueError("Either 'template' or 'template_src' is required.")

            content_type = "application/pdf" if out_format == "pdf" else "image/svg+xml" if out_format == "svg" else "image/png"
            filename = f"document.{out_format}"

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Disposition", f'inline; filename="{filename}"')
            self.send_header("Content-Length", str(len(output_bytes)))
            self.send_header("X-Render-Time-Ms", f"{elapsed_ms:.2f}")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(output_bytes)

        except Exception as e:
            err = {"error": str(e), "status": "failed"}
            self._send_json(400, err)

    def _handle_facturx_render(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length).decode("utf-8")
            body = json.loads(raw_body) if raw_body else {}

            data = body.get("data", body)
            template = body.get("template", "facturx_invoice")
            profile = body.get("profile", "EN 16931")

            pdf_bytes, xml_bytes, elapsed_ms = self.engine.render_facturx(
                data=data,
                template=template,
                profile=profile
            )

            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", 'inline; filename="factur-x-invoice.pdf"')
            self.send_header("Content-Length", str(len(pdf_bytes)))
            self.send_header("X-Render-Time-Ms", f"{elapsed_ms:.2f}")
            self.send_header("X-FacturX-Profile", profile)
            self.send_header("X-FacturX-XML-Bytes", str(len(xml_bytes)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(pdf_bytes)

        except Exception as e:
            err = {"error": str(e), "status": "failed"}
            self._send_json(400, err)

    def _handle_facturx_validate(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            content_type = self.headers.get("Content-Type", "")
            raw = self.rfile.read(length)

            if "application/pdf" in content_type or raw.startswith(b"%PDF"):
                report = validate_facturx_pdf(raw)
                self._send_json(200, report)
            else:
                data = json.loads(raw.decode("utf-8"))
                errors = validate_facturx_payload(data)
                self._send_json(200, {"valid": len(errors) == 0, "errors": errors})

        except Exception as e:
            self._send_json(400, {"error": str(e), "status": "failed"})

    def _handle_facturx_extract(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            xml_bytes = extract_facturx_xml(raw)

            self.send_response(200)
            self.send_header("Content-Type", "text/xml; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="factur-x.xml"')
            self.send_header("Content-Length", str(len(xml_bytes)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(xml_bytes)
        except Exception as e:
            self._send_json(400, {"error": str(e), "status": "failed"})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, status: int, obj: dict):
        content = json.dumps(obj).encode("utf-8")
        self._send_response(status, "application/json; charset=utf-8", content)

    def _send_response(self, status: int, mime: str, content: bytes):
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        sys.stderr.write(f"[Rubrol] {self.address_string()} - {format % args}\n")

def serve(host: str = "0.0.0.0", port: int = 8080):
    server = ThreadedHTTPServer((host, port), RubrolServerHandler)
    print(f"[Rubrol Engine] Serving at http://{host}:{port} (PID: {os.getpid()})")
    print(f"[Rubrol Engine] Playground: http://localhost:{port}/")
    print(f"[Rubrol Engine] API Endpoint: POST http://localhost:{port}/v1/render")
    print(f"[Rubrol Engine] Factur-X Endpoint: POST http://localhost:{port}/v1/facturx/render")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Rubrol Engine] Shutting down server...")
        server.shutdown()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rubrol PDF Engine Server")
    parser.add_argument("--host", default="0.0.0.0", help="Binding host")
    parser.add_argument("-p", "--port", type=int, default=8080, help="Port")
    args = parser.parse_args()
    serve(args.host, args.port)
