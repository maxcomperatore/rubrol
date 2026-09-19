"""
Rubrol Production Engine
High-performance Typst compiler pool with font cache reuse, template registry, and multi-format export.
Includes turnkey EU Factur-X / ZUGFeRD PDF/A-3b hybrid compilation pipeline.
"""
import json, os, sys, tempfile, time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import typst
from rubrol.facturx.generator import generate_facturx_xml, FacturXProfile
from rubrol.facturx.packager import package_facturx_pdf, extract_facturx_xml
from rubrol.facturx.validator import validate_facturx_payload, validate_facturx_pdf

BUILTIN_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

class RubrolEngine:
    def __init__(self, default_standard: Optional[str] = "a-2b"):
        self.default_standard = default_standard
        self._compilers: Dict[str, typst.Compiler] = {}
        self.template_registry: Dict[str, Path] = {}
        self._discover_templates()

    def _discover_templates(self):
        if BUILTIN_TEMPLATES_DIR.exists():
            for f in BUILTIN_TEMPLATES_DIR.glob("*.typ"):
                self.template_registry[f.stem] = f
            vault_dir = BUILTIN_TEMPLATES_DIR / "vault"
            if vault_dir.exists():
                for f in vault_dir.glob("*.typ"):
                    self.template_registry[f.stem] = f

    def resolve_template(self, template_ident: str) -> Path:
        # Check alias in registry
        if template_ident in self.template_registry:
            return self.template_registry[template_ident]
        
        # Fallback aliases for legacy or alternate naming
        aliases = {
            "facturx_zugferd_invoice": "b2b_invoice",
            "facturx_invoice": "b2b_invoice",
            "b2b_saas_invoice": "b2b_invoice",
            "proforma_invoice": "b2b_invoice",
            "standard_invoice": "b2b_invoice"
        }
        if template_ident in aliases and aliases[template_ident] in self.template_registry:
            return self.template_registry[aliases[template_ident]]
        
        p = Path(template_ident)
        if p.exists():
            return p.resolve()
        
        # Check relative to templates dir
        alt = BUILTIN_TEMPLATES_DIR / template_ident
        if alt.exists():
            return alt.resolve()
        alt_typ = BUILTIN_TEMPLATES_DIR / f"{template_ident}.typ"
        if alt_typ.exists():
            return alt_typ.resolve()

        if p.stem in self.template_registry:
            return self.template_registry[p.stem]
        if p.stem in aliases and aliases[p.stem] in self.template_registry:
            return self.template_registry[aliases[p.stem]]

        # Check if requested template is part of the Rubrol Pro Vault
        pro_vault_catalog = {
            "facturx_invoice": "European Standard EN 16931 / Factur-X 1.0 E-Invoice",
            "board_financial_report": "Executive Board Financial Update",
            "compliance_certificate": "SOC 2 & ISO 27001 Certificate",
            "medical_intake": "HIPAA Clinical Intake Record",
            "nda_agreement": "Mutual Non-Disclosure Agreement",
            "academic_transcript": "University Academic Transcript",
            "packing_slip": "Multi-Box Logistics Packing Slip",
            "paystub_statement": "Itemized Payroll Statement",
            "purchase_order": "Enterprise Procurement Order"
        }
        if template_ident in pro_vault_catalog:
            raise FileNotFoundError(
                f"Template '{template_ident}' ({pro_vault_catalog[template_ident]}) is part of the private Rubrol Pro Vault.\n"
                f"Unlock access at https://buy.stripe.com/fZu5kEcpvcZQehJdgE0Ba0j (or clone https://github.com/maxcomperatore/rubrol-pro-vault into rubrol/templates/vault/)."
            )

        raise FileNotFoundError(f"Template '{template_ident}' not found in registry or filesystem.")

    def get_compiler(self, template_path: Path) -> typst.Compiler:
        key = str(template_path.resolve())
        if key not in self._compilers:
            self._compilers[key] = typst.Compiler(key)
        return self._compilers[key]

    def _parse_data_dict(self, data: Optional[Union[Dict[str, Any], str]]) -> Tuple[Dict[str, Any], str]:
        if isinstance(data, (dict, list)):
            return data if isinstance(data, dict) else {"items": data}, json.dumps(data)
        elif isinstance(data, str) and (data.strip().startswith("{") or data.strip().startswith("[")):
            parsed = json.loads(data)
            return parsed if isinstance(parsed, dict) else {"items": parsed}, data
        elif data:
            with open(data, "r", encoding="utf-8") as f:
                content = f.read()
            parsed = json.loads(content)
            return parsed if isinstance(parsed, dict) else {"items": parsed}, content
        else:
            return {}, "{}"

    def render(
        self,
        template: Union[str, Path],
        data: Optional[Union[Dict[str, Any], str]] = None,
        output_format: str = "pdf",
        pdf_standard: Optional[str] = None
    ) -> Tuple[bytes, float]:
        t0 = time.perf_counter()
        _, data_str = self._parse_data_dict(data)

        target_path = self.resolve_template(str(template))
        compiler = self.get_compiler(target_path)

        standard = pdf_standard if pdf_standard is not None else self.default_standard
        standards = [standard] if standard and standard.lower() != "none" and output_format == "pdf" else None

        res = compiler.compile(
            sys_inputs={"data": data_str},
            format=output_format,
            pdf_standards=standards
        )

        render_ms = (time.perf_counter() - t0) * 1000.0
        return res, render_ms

    def render_source(
        self,
        source_code: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        output_format: str = "pdf",
        pdf_standard: Optional[str] = None
    ) -> Tuple[bytes, float]:
        t0 = time.perf_counter()
        _, data_str = self._parse_data_dict(data)

        standard = pdf_standard if pdf_standard is not None else self.default_standard
        standards = [standard] if standard and standard.lower() != "none" and output_format == "pdf" else None

        with tempfile.NamedTemporaryFile(suffix=".typ", mode="w", encoding="utf-8", delete=False) as f:
            f.write(source_code)
            tmp_name = f.name

        try:
            res = typst.compile(
                tmp_name,
                sys_inputs={"data": data_str},
                format=output_format,
                pdf_standards=standards
            )
        finally:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass

        render_ms = (time.perf_counter() - t0) * 1000.0
        return res, render_ms

    def render_facturx(
        self,
        data: Union[Dict[str, Any], str, Path],
        template: Union[str, Path] = "facturx_invoice",
        profile: str = "EN 16931",
        validate_input: bool = True
    ) -> Tuple[bytes, bytes, float]:
        """
        Turnkey EU Factur-X / ZUGFeRD compilation pipeline.
        Returns: (pdf_a3_bytes, facturx_xml_bytes, render_ms)
        """
        t0 = time.perf_counter()
        data_dict, _ = self._parse_data_dict(data)

        if validate_input:
            errors = validate_facturx_payload(data_dict)
            if errors:
                raise ValueError(f"EN 16931 validation failed: {'; '.join(errors)}")

        # 1. Compile base Typst document with PDF/A-3b profile
        pdf_base, _ = self.render(
            template=template,
            data=data_dict,
            output_format="pdf",
            pdf_standard="a-3b"
        )

        # 2. Generate compliant UN/CEFACT CII XML
        xml_bytes = generate_facturx_xml(data_dict, profile=profile)

        # 3. Package into PDF/A-3b container with /AF relationship and XMP metadata
        packaged_pdf = package_facturx_pdf(
            pdf_bytes=pdf_base,
            xml_bytes=xml_bytes,
            profile=profile,
            filename="factur-x.xml"
        )

        render_ms = (time.perf_counter() - t0) * 1000.0
        return packaged_pdf, xml_bytes, render_ms
