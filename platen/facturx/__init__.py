"""
Platen EU Factur-X / ZUGFeRD Turnkey Suite.
Zero-overhead UN/CEFACT CII XML generation, PDF/A-3b packaging, and validation.
"""
from .generator import generate_facturx_xml, FacturXProfile
from .packager import package_facturx_pdf, extract_facturx_xml
from .validator import validate_facturx_payload, validate_facturx_pdf

__all__ = [
    "generate_facturx_xml",
    "FacturXProfile",
    "package_facturx_pdf",
    "extract_facturx_xml",
    "validate_facturx_payload",
    "validate_facturx_pdf"
]
