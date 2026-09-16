"""
Platen Factur-X / ZUGFeRD In-Flight Validator.
Validates input invoice JSON against EN 16931 European e-invoicing business rules,
and verifies generated PDF/A-3b containers for ISO 19005-3 and Factur-X compliance.
"""
from decimal import Decimal
import io
import re
from typing import Any, Dict, List, Tuple
import xml.etree.ElementTree as ET
import pypdf

from .packager import extract_facturx_xml

def validate_facturx_payload(data: Dict[str, Any]) -> List[str]:
    """
    Validate input JSON data against European Standard EN 16931 business rules.
    Returns list of error messages (empty if valid).
    """
    errors: List[str] = []

    # 1. Invoice Number & Dates
    if not data.get("invoice_number"):
        errors.append("Missing mandatory 'invoice_number' (BT-1)")

    issued_date = data.get("issued_date") or data.get("issue_date")
    if not issued_date:
        errors.append("Missing mandatory 'issued_date' (BT-2)")
    elif not re.match(r"^\d{4}-?\d{2}-?\d{2}$", str(issued_date).strip()):
        errors.append(f"Invalid 'issued_date' format '{issued_date}', expected YYYY-MM-DD")

    # 2. Currency
    currency = data.get("currency", "EUR")
    if not isinstance(currency, str) or len(currency.strip()) != 3:
        errors.append(f"Invalid ISO 4217 currency code '{currency}' (BT-5)")

    # 3. Seller (Vendor)
    vendor = data.get("vendor")
    if not vendor or not isinstance(vendor, dict):
        errors.append("Missing mandatory 'vendor' object (BG-4)")
    else:
        if not vendor.get("name"):
            errors.append("Missing vendor 'name' (BT-27)")
        if not vendor.get("country") and not vendor.get("country_code"):
            errors.append("Missing vendor country ISO code (BT-40)")
        if not vendor.get("vat_id") and not vendor.get("tax_id") and not vendor.get("siret"):
            errors.append("Missing vendor tax registration (VAT ID or SIRET/Tax ID) (BT-31 / BT-32)")

    # 4. Buyer (Customer)
    customer = data.get("customer")
    if not customer or not isinstance(customer, dict):
        errors.append("Missing mandatory 'customer' object (BG-7)")
    else:
        if not customer.get("name"):
            errors.append("Missing customer 'name' (BT-44)")
        if not customer.get("country") and not customer.get("country_code"):
            errors.append("Missing customer country ISO code (BT-55)")

    # 5. Line items & Mathematical precision
    line_items = data.get("line_items", [])
    if not line_items or not isinstance(line_items, list):
        errors.append("Missing mandatory 'line_items' array (BG-25)")
    else:
        computed_subtotal = Decimal("0.00")
        for i, item in enumerate(line_items, start=1):
            if not item.get("name") and not item.get("description"):
                errors.append(f"Line item #{i} missing 'name' or 'description' (BT-153)")
            
            try:
                qty = Decimal(str(item.get("qty", item.get("quantity", 1))))
                if qty <= 0:
                    errors.append(f"Line item #{i} quantity must be positive")
            except Exception:
                errors.append(f"Line item #{i} has invalid quantity")
                qty = Decimal("1")

            try:
                price = Decimal(str(item.get("unit_price", 0)))
                if price < 0:
                    errors.append(f"Line item #{i} price must be non-negative")
            except Exception:
                errors.append(f"Line item #{i} has invalid unit price")
                price = Decimal("0")

            computed_subtotal += (qty * price).quantize(Decimal("0.01"))

        # Check explicit subtotal if provided
        if "subtotal" in data:
            try:
                given_subtotal = Decimal(str(data["subtotal"])).quantize(Decimal("0.01"))
                if abs(given_subtotal - computed_subtotal) > Decimal("0.05"):
                    errors.append(
                        f"Subtotal mismatch: given {given_subtotal}, computed sum of lines is {computed_subtotal}"
                    )
            except Exception:
                errors.append("Invalid subtotal value")

    return errors

def validate_facturx_pdf(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Validate a generated PDF/A-3b container for Factur-X / ZUGFeRD compliance.
    """
    result: Dict[str, Any] = {
        "valid": False,
        "pdf_standard": None,
        "embedded_xml_found": False,
        "af_relationship_valid": False,
        "xmp_metadata_valid": False,
        "conformance_level": None,
        "invoice_number": None,
        "grand_total": None,
        "currency": None,
        "xml_bytes": 0,
        "errors": []
    }

    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    except Exception as e:
        result["errors"].append(f"Invalid PDF file: {str(e)}")
        return result

    # 1. Check /AF (Associated Files) in Catalog
    catalog = reader.trailer.get("/Root", {})
    if "/AF" in catalog:
        result["af_relationship_valid"] = True
    else:
        result["errors"].append("Catalog missing '/AF' (Associated Files) array required by PDF/A-3")

    # 2. Check XMP Metadata for Factur-X schema
    if "/Metadata" in catalog:
        try:
            xmp = catalog["/Metadata"].get_object().get_data().decode("utf-8", errors="replace")
            if "urn:factur-x:pdfa:CrossIndustryDocument:invoice:1p0#" in xmp:
                result["xmp_metadata_valid"] = True
                m = re.search(r"<fx:ConformanceLevel>([^<]+)</fx:ConformanceLevel>", xmp)
                if m:
                    result["conformance_level"] = m.group(1).strip()
            else:
                result["errors"].append("PDF XMP metadata missing Factur-X namespace")
        except Exception as e:
            result["errors"].append(f"Failed to inspect XMP metadata: {str(e)}")

    # 3. Extract and Validate embedded XML
    try:
        xml_bytes = extract_facturx_xml(pdf_bytes)
        result["embedded_xml_found"] = True
        result["xml_bytes"] = len(xml_bytes)

        # Parse XML
        root = ET.fromstring(xml_bytes)
        tag = root.tag
        if not tag.endswith("CrossIndustryInvoice"):
            result["errors"].append(f"Expected root 'CrossIndustryInvoice', found '{tag}'")
        
        # Extract invoice ID
        for elem in root.iter():
            if elem.tag.endswith("ExchangedDocument"):
                for child in elem:
                    if child.tag.endswith("ID"):
                        result["invoice_number"] = child.text
            elif elem.tag.endswith("GrandTotalAmount"):
                result["grand_total"] = elem.text
            elif elem.tag.endswith("InvoiceCurrencyCode"):
                result["currency"] = elem.text
            elif elem.tag.endswith("GuidelineSpecifiedDocumentContextParameter"):
                for sub in elem:
                    if sub.tag.endswith("ID") and not result["conformance_level"]:
                        result["conformance_level"] = sub.text

    except Exception as e:
        result["errors"].append(f"Embedded XML validation failed: {str(e)}")

    result["valid"] = (
        result["embedded_xml_found"]
        and result["af_relationship_valid"]
        and len(result["errors"]) == 0
    )
    return result
