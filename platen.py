"""
Platen: The Anti-Puppeteer PDF Engine.
Sub-10ms dynamic PDF/A compilation engine powered by Apache 2.0 Typst.
Includes Turnkey EU Factur-X / ZUGFeRD 2.2 Enterprise Suite.
"""
import argparse, json, os, sys, time, tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import typst

from platen.facturx.generator import generate_facturx_xml, FacturXProfile
from platen.facturx.packager import package_facturx_pdf, extract_facturx_xml
from platen.facturx.validator import validate_facturx_payload, validate_facturx_pdf

DEFAULT_FACTURX_TEMPLATE = Path(__file__).parent / "platen" / "templates" / "facturx_invoice.typ"
DEFAULT_FACTURX_DATA = Path(__file__).parent / "platen" / "data" / "facturx_invoice.json"

class PlatenEngine:
    """High-performance Typst compiler wrapper with font-cache reuse & Factur-X packaging."""
    def __init__(self, default_standard: Optional[str] = "a-2b"):
        self.default_standard = default_standard
        self._compilers: Dict[str, typst.Compiler] = {}

    def get_compiler(self, template_path: Union[str, Path]) -> typst.Compiler:
        path = str(Path(template_path).resolve())
        if path not in self._compilers:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Template not found: {path}")
            self._compilers[path] = typst.Compiler(path)
        return self._compilers[path]

    def render(
        self,
        template: Union[str, Path],
        data: Optional[Union[Dict[str, Any], str]] = None,
        output_path: Optional[Union[str, Path]] = None,
        pdf_standard: Optional[str] = None
    ) -> bytes:
        standard = pdf_standard if pdf_standard is not None else self.default_standard
        standards = [standard] if standard and standard.lower() != "none" else None
        
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data)
        elif isinstance(data, str) and (data.strip().startswith("{") or data.strip().startswith("[")):
            data_str = data
        elif data:
            with open(data, "r", encoding="utf-8") as f:
                data_str = f.read()
        else:
            data_str = "{}"

        compiler = self.get_compiler(template)
        pdf_bytes = compiler.compile(
            sys_inputs={"data": data_str},
            pdf_standards=standards
        )

        if output_path:
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(pdf_bytes)

        return pdf_bytes

    def render_facturx(
        self,
        data: Union[Dict[str, Any], str],
        template: Union[str, Path] = DEFAULT_FACTURX_TEMPLATE,
        output_path: Optional[Union[str, Path]] = None,
        profile: str = "EN 16931",
        validate_input: bool = True
    ) -> Tuple[bytes, bytes]:
        if isinstance(data, str) and (data.strip().startswith("{") or data.strip().startswith("[")):
            payload = json.loads(data)
        elif isinstance(data, str) and os.path.exists(data):
            with open(data, "r", encoding="utf-8") as f:
                payload = json.load(f)
        elif isinstance(data, dict):
            payload = data
        else:
            raise ValueError("Invalid data provided for Factur-X invoice")

        if validate_input:
            errors = validate_facturx_payload(payload)
            if errors:
                raise ValueError(f"EN 16931 validation failed: {'; '.join(errors)}")

        pdf_base = self.render(
            template=template,
            data=payload,
            pdf_standard="a-3b"
        )

        xml_bytes = generate_facturx_xml(payload, profile=profile)
        packaged_pdf = package_facturx_pdf(pdf_base, xml_bytes, profile=profile)

        if output_path:
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(packaged_pdf)

        return packaged_pdf, xml_bytes

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class PlatenRequestHandler(BaseHTTPRequestHandler):
    engine = PlatenEngine()

    def do_GET(self):
        if self.path in ("/health", "/v1/health", "/"):
            res = json.dumps({
                "status": "healthy",
                "service": "platen",
                "engine": "typst",
                "typst_version": getattr(typst, "__version__", "0.15.0"),
                "cached_templates": len(self.engine._compilers),
                "facturx_suite": True,
                "supported_profiles": ["MINIMUM", "BASIC_WL", "BASIC", "EN 16931", "EXTENDED"]
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/v1/render":
            self._handle_render()
        elif self.path == "/v1/facturx/render":
            self._handle_facturx_render()
        elif self.path == "/v1/facturx/validate":
            self._handle_facturx_validate()
        elif self.path == "/v1/facturx/extract":
            self._handle_facturx_extract()
        else:
            self.send_error(404, "Unknown endpoint")

    def _handle_render(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_length).decode("utf-8"))
            template = body.get("template")
            template_src = body.get("template_src")
            data = body.get("data", {})
            pdf_standard = body.get("pdf_standard", "a-2b")

            t0 = time.perf_counter()
            tmp_file = None
            try:
                if template_src:
                    tmp_file = tempfile.NamedTemporaryFile(suffix=".typ", delete=False, mode="w", encoding="utf-8")
                    tmp_file.write(template_src)
                    tmp_file.flush()
                    tmp_file.close()
                    target_tmpl = tmp_file.name
                elif template:
                    target_tmpl = template
                else:
                    raise ValueError("Either 'template' path or 'template_src' is required")

                pdf_bytes = self.engine.render(target_tmpl, data=data, pdf_standard=pdf_standard)
            finally:
                if tmp_file:
                    try: os.unlink(tmp_file.name)
                    except OSError: pass

            render_ms = (time.perf_counter() - t0) * 1000.0

            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", 'inline; filename="document.pdf"')
            self.send_header("Content-Length", str(len(pdf_bytes)))
            self.send_header("X-Render-Time-Ms", f"{render_ms:.2f}")
            self.end_headers()
            self.wfile.write(pdf_bytes)
        except Exception as e:
            self._send_json_error(e)

    def _handle_facturx_render(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_length).decode("utf-8"))
            data = body.get("data", body)
            template = body.get("template", DEFAULT_FACTURX_TEMPLATE)
            profile = body.get("profile", "EN 16931")

            t0 = time.perf_counter()
            pdf_bytes, xml_bytes = self.engine.render_facturx(
                data=data,
                template=template,
                profile=profile
            )
            render_ms = (time.perf_counter() - t0) * 1000.0

            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", 'inline; filename="factur-x-invoice.pdf"')
            self.send_header("Content-Length", str(len(pdf_bytes)))
            self.send_header("X-Render-Time-Ms", f"{render_ms:.2f}")
            self.send_header("X-FacturX-Profile", profile)
            self.send_header("X-FacturX-XML-Bytes", str(len(xml_bytes)))
            self.end_headers()
            self.wfile.write(pdf_bytes)
        except Exception as e:
            self._send_json_error(e)

    def _handle_facturx_validate(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            content_type = self.headers.get("Content-Type", "")
            raw = self.rfile.read(content_length)

            if "application/pdf" in content_type or raw.startswith(b"%PDF"):
                report = validate_facturx_pdf(raw)
                res = json.dumps(report).encode()
            else:
                data = json.loads(raw.decode("utf-8"))
                errors = validate_facturx_payload(data)
                res = json.dumps({"valid": len(errors) == 0, "errors": errors}).encode()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
        except Exception as e:
            self._send_json_error(e)

    def _handle_facturx_extract(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(content_length)
            xml_bytes = extract_facturx_xml(raw)

            self.send_response(200)
            self.send_header("Content-Type", "text/xml; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="factur-x.xml"')
            self.send_header("Content-Length", str(len(xml_bytes)))
            self.end_headers()
            self.wfile.write(xml_bytes)
        except Exception as e:
            self._send_json_error(e)

    def _send_json_error(self, exc: Exception):
        err = json.dumps({"error": str(exc)}).encode()
        self.send_response(400)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(err)))
        self.end_headers()
        self.wfile.write(err)

    def log_message(self, format, *args):
        sys.stderr.write(f"[Platen] {self.address_string()} - {format % args}\n")

def run_server(host: str = "0.0.0.0", port: int = 8080):
    server = ThreadedHTTPServer((host, port), PlatenRequestHandler)
    print(f"[Platen] Daemon listening on http://{host}:{port} (PID: {os.getpid()})")
    print(f"[Platen] Factur-X / ZUGFeRD Suite ready on /v1/facturx/render")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Platen] Stopping daemon...")
        server.shutdown()

def main():
    parser = argparse.ArgumentParser(prog="platen", description="Platen: The Anti-Puppeteer PDF Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. compile
    c = subparsers.add_parser("compile", help="Compile a Typst template + JSON payload to PDF")
    c.add_argument("-t", "--template", required=True, help="Path to .typ template")
    c.add_argument("-d", "--data", default=None, help="Path to JSON file or raw JSON string")
    c.add_argument("-o", "--output", default=None, help="Path to output .pdf file (stdout if omitted)")
    c.add_argument("-s", "--standard", default="a-2b", help="PDF standard (e.g. a-2b, or none)")

    # 2. facturx
    fx = subparsers.add_parser("facturx", help="Compile & package EU Factur-X / ZUGFeRD 2.2 PDF/A-3b hybrid invoice")
    fx.add_argument("-t", "--template", default=str(DEFAULT_FACTURX_TEMPLATE), help="Typst template path (default: facturx_invoice.typ)")
    fx.add_argument("-d", "--data", default=str(DEFAULT_FACTURX_DATA), help="JSON invoice payload path")
    fx.add_argument("-o", "--output", default="facturx_invoice.pdf", help="Output PDF/A-3b path")
    fx.add_argument("-p", "--profile", default="EN 16931", choices=["EN 16931", "BASIC", "BASIC_WL", "MINIMUM", "EXTENDED", "XRECHNUNG"], help="Factur-X profile")

    # 3. extract-facturx
    ext = subparsers.add_parser("extract-facturx", help="Extract embedded factur-x.xml from a PDF container")
    ext.add_argument("pdf", help="Path to input PDF/A-3 container")
    ext.add_argument("-o", "--output", default=None, help="Path to save extracted XML (stdout if omitted)")

    # 4. validate-facturx
    val = subparsers.add_parser("validate-facturx", help="Validate a Factur-X PDF container or JSON payload")
    val.add_argument("target", help="Path to PDF container or JSON file")

    # 5. serve
    s = subparsers.add_parser("serve", help="Run local HTTP daemon sidecar")
    s.add_argument("--host", default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    s.add_argument("-p", "--port", type=int, default=8080, help="Port (default: 8080)")

    args = parser.parse_args()
    engine = PlatenEngine(default_standard=args.standard if hasattr(args, "standard") else "a-2b")

    if args.command == "compile":
        t0 = time.perf_counter()
        pdf_bytes = engine.render(args.template, data=args.data, output_path=args.output, pdf_standard=args.standard)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        if args.output:
            print(f"[Platen] Compiled {args.output} ({len(pdf_bytes):,} bytes) in {elapsed_ms:.2f}ms")
        else:
            sys.stdout.buffer.write(pdf_bytes)

    elif args.command == "facturx":
        t0 = time.perf_counter()
        pdf_bytes, xml_bytes = engine.render_facturx(
            data=args.data,
            template=args.template,
            output_path=args.output,
            profile=args.profile
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        print(f"[Platen Factur-X] Successfully generated {args.output}")
        print(f"  Container: PDF/A-3b ({len(pdf_bytes):,} bytes)")
        print(f"  Embedded XML: factur-x.xml ({len(xml_bytes):,} bytes, profile: {args.profile})")
        print(f"  Execution Time: {elapsed_ms:.2f}ms")

    elif args.command == "extract-facturx":
        xml_bytes = extract_facturx_xml(args.pdf)
        if args.output:
            Path(args.output).write_bytes(xml_bytes)
            print(f"[Platen Factur-X] Extracted {len(xml_bytes):,} bytes to {args.output}")
        else:
            sys.stdout.buffer.write(xml_bytes)

    elif args.command == "validate-facturx":
        p = Path(args.target)
        if not p.exists():
            print(f"Error: Target '{args.target}' does not exist.", file=sys.stderr)
            sys.exit(1)
        
        if p.suffix.lower() == ".pdf":
            report = validate_facturx_pdf(p.read_bytes())
            print(json.dumps(report, indent=2))
            if not report.get("valid"):
                sys.exit(1)
        else:
            payload = json.loads(p.read_text(encoding="utf-8"))
            errors = validate_facturx_payload(payload)
            if errors:
                print(f"FAILED with {len(errors)} error(s):", file=sys.stderr)
                for err in errors:
                    print(f"  - {err}", file=sys.stderr)
                sys.exit(1)
            else:
                print("[Platen Factur-X] Input payload is 100% compliant with EN 16931 rules.")

    elif args.command == "serve":
        run_server(args.host, args.port)

if __name__ == "__main__":
    main()
