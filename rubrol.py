"""
Rubrol: The Anti-Puppeteer PDF Engine.
Sub-10ms dynamic PDF/A compilation engine powered by Apache 2.0 Typst.
Includes Turnkey EU Factur-X / ZUGFeRD 2.2 Enterprise Suite.
"""
import argparse, json, os, sys, time
from pathlib import Path
from typing import Optional, Union

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from rubrol.core.engine import RubrolEngine
from rubrol.core.server import serve as run_server
from rubrol.facturx.generator import FacturXProfile
from rubrol.facturx.packager import extract_facturx_xml
from rubrol.facturx.validator import validate_facturx_payload, validate_facturx_pdf

_PRO_FACTURX_TEMPLATE = ROOT_DIR / "rubrol" / "templates" / "facturx_invoice.typ"
DEFAULT_FACTURX_TEMPLATE = str(_PRO_FACTURX_TEMPLATE if _PRO_FACTURX_TEMPLATE.exists() else (ROOT_DIR / "rubrol" / "templates" / "b2b_invoice.typ"))
DEFAULT_FACTURX_DATA = ROOT_DIR / "rubrol" / "data" / "facturx_invoice.json"

def main():
    parser = argparse.ArgumentParser(prog="rubrol", description="Rubrol: The Anti-Puppeteer PDF Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. compile
    c = subparsers.add_parser("compile", help="Compile a Typst template + JSON payload to PDF")
    c.add_argument("-t", "--template", required=True, help="Path or name of .typ template")
    c.add_argument("-d", "--data", default=None, help="Path to JSON file or raw JSON string")
    c.add_argument("-o", "--output", default=None, help="Path to output .pdf file (stdout if omitted)")
    c.add_argument("-s", "--standard", default="a-2b", help="PDF standard (e.g. a-2b, a-3b, or none)")

    # 2. facturx
    fx = subparsers.add_parser("facturx", help="Compile & package EU Factur-X / ZUGFeRD 2.2 PDF/A-3b hybrid invoice")
    fx.add_argument("-t", "--template", default=str(DEFAULT_FACTURX_TEMPLATE), help="Typst template path or alias (default: b2b_invoice)")
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
    s = subparsers.add_parser("serve", help="Run local HTTP daemon sidecar with interactive playground")
    s.add_argument("--host", default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    s.add_argument("-p", "--port", type=int, default=8080, help="Port (default: 8080)")

    args = parser.parse_args()
    engine = RubrolEngine(default_standard=args.standard if hasattr(args, "standard") else "a-2b")

    if args.command == "compile":
        pdf_bytes, elapsed_ms = engine.render(
            template=args.template,
            data=args.data,
            output_format="pdf",
            pdf_standard=args.standard
        )
        if args.output:
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(pdf_bytes)
            print(f"[Rubrol] Compiled {args.output} ({len(pdf_bytes):,} bytes) in {elapsed_ms:.2f}ms")
        else:
            sys.stdout.buffer.write(pdf_bytes)

    elif args.command == "facturx":
        pdf_bytes, xml_bytes, elapsed_ms = engine.render_facturx(
            data=args.data,
            template=args.template,
            profile=args.profile
        )
        if args.output:
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(pdf_bytes)
        print(f"[Rubrol Factur-X] Successfully generated {args.output}")
        print(f"  Container: PDF/A-3b ({len(pdf_bytes):,} bytes)")
        print(f"  Embedded XML: factur-x.xml ({len(xml_bytes):,} bytes, profile: {args.profile})")
        print(f"  Execution Time: {elapsed_ms:.2f}ms")

    elif args.command == "extract-facturx":
        pdf_path = Path(args.pdf)
        if not pdf_path.exists():
            print(f"Error: File '{args.pdf}' not found.", file=sys.stderr)
            sys.exit(1)
        xml_bytes = extract_facturx_xml(pdf_path.read_bytes())
        if args.output:
            Path(args.output).write_bytes(xml_bytes)
            print(f"[Rubrol Factur-X] Extracted {len(xml_bytes):,} bytes to {args.output}")
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
                print("[Rubrol Factur-X] Input payload is 100% compliant with EN 16931 rules.")

    elif args.command == "serve":
        run_server(args.host, args.port)

if __name__ == "__main__":
    main()
