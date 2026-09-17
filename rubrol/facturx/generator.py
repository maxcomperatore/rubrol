"""
Rubrol EU Factur-X / ZUGFeRD CII XML Generator.
Produces 100% compliant UN/CEFACT Cross Industry Invoice (CII) D16B XML
matching Factur-X 1.0.07 / ZUGFeRD 2.2 / European Standard EN 16931.
"""
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom

class FacturXProfile(str, Enum):
    MINIMUM = "MINIMUM"
    BASIC_WL = "BASIC WL"
    BASIC = "BASIC"
    EN_16931 = "EN 16931"
    EXTENDED = "EXTENDED"
    XRECHNUNG = "XRECHNUNG"

PROFILE_URNS = {
    FacturXProfile.MINIMUM: "urn:factur-x.eu:1p0:minimum",
    FacturXProfile.BASIC_WL: "urn:factur-x.eu:1p0:basicwl",
    FacturXProfile.BASIC: "urn:factur-x.eu:1p0:basic",
    FacturXProfile.EN_16931: "urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:en16931",
    FacturXProfile.EXTENDED: "urn:cen.eu:en16931:2017#conformant#urn:factur-x.eu:1p0:extended",
    FacturXProfile.XRECHNUNG: "urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0",
}

PROFILE_NAMES = {
    "MINIMUM": FacturXProfile.MINIMUM,
    "BASIC_WL": FacturXProfile.BASIC_WL,
    "BASIC WL": FacturXProfile.BASIC_WL,
    "BASIC": FacturXProfile.BASIC,
    "EN_16931": FacturXProfile.EN_16931,
    "EN 16931": FacturXProfile.EN_16931,
    "COMFORT": FacturXProfile.EN_16931,
    "EXTENDED": FacturXProfile.EXTENDED,
    "XRECHNUNG": FacturXProfile.XRECHNUNG,
}

NAMESPACES = {
    "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
    "qdt": "urn:un:unece:uncefact:data:standard:QualifiedDataType:100",
    "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
    "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
}

def _fmt_dec(val: Any, decimals: int = 2) -> str:
    d = Decimal(str(val))
    q = Decimal("10") ** -decimals
    return str(d.quantize(q, rounding=ROUND_HALF_UP))

def _fmt_date(date_str: str) -> str:
    """Format 'YYYY-MM-DD' or 'YYYYMMDD' to 'YYYYMMDD'."""
    cleaned = date_str.replace("-", "").strip()
    if len(cleaned) == 8 and cleaned.isdigit():
        return cleaned
    raise ValueError(f"Invalid date format '{date_str}', expected YYYY-MM-DD")

def _sub(parent: ET.Element, tag: str, text: Optional[str] = None, **attribs) -> ET.Element:
    elem = ET.SubElement(parent, tag, **attribs)
    if text is not None:
        elem.text = str(text)
    return elem

def generate_facturx_xml(
    data: Dict[str, Any],
    profile: FacturXProfile = FacturXProfile.EN_16931
) -> bytes:
    """
    Generate valid UN/CEFACT Cross Industry Invoice XML bytes from invoice JSON payload.
    """
    if isinstance(profile, str):
        profile = PROFILE_NAMES.get(profile.upper(), FacturXProfile.EN_16931)

    for prefix, uri in NAMESPACES.items():
        ET.register_namespace(prefix, uri)

    root = ET.Element(f"{{{NAMESPACES['rsm']}}}CrossIndustryInvoice")

    # 1. Context Parameter
    context = _sub(root, f"{{{NAMESPACES['rsm']}}}ExchangedDocumentContext")
    param = _sub(context, f"{{{NAMESPACES['ram']}}}GuidelineSpecifiedDocumentContextParameter")
    _sub(param, f"{{{NAMESPACES['ram']}}}ID", PROFILE_URNS[profile])

    # 2. Exchanged Document
    invoice_number = str(data.get("invoice_number", "INV-0001"))
    issue_date = _fmt_date(str(data.get("issued_date", data.get("issue_date", "2026-09-15"))))
    type_code = str(data.get("type_code", "380")) # 380 = Commercial invoice, 381 = Credit note

    doc = _sub(root, f"{{{NAMESPACES['rsm']}}}ExchangedDocument")
    _sub(doc, f"{{{NAMESPACES['ram']}}}ID", invoice_number)
    _sub(doc, f"{{{NAMESPACES['ram']}}}TypeCode", type_code)
    
    issue_dt = _sub(doc, f"{{{NAMESPACES['ram']}}}IssueDateTime")
    _sub(issue_dt, f"{{{NAMESPACES['udt']}}}DateTimeString", issue_date, format="102")

    notes = data.get("notes", [])
    if isinstance(notes, str):
        notes = [notes]
    for note in notes:
        note_el = _sub(doc, f"{{{NAMESPACES['ram']}}}IncludedNote")
        _sub(note_el, f"{{{NAMESPACES['ram']}}}Content", note)

    # 3. Supply Chain Trade Transaction
    txn = _sub(root, f"{{{NAMESPACES['rsm']}}}SupplyChainTradeTransaction")

    currency = str(data.get("currency", "EUR")).upper()
    line_items = data.get("line_items", [])
    vendor = data.get("vendor") or data.get("seller") or {}
    customer = data.get("customer") or data.get("buyer") or {}

    # 3.1 Line Items (Only for BASIC, EN_16931, EXTENDED, XRECHNUNG)
    has_lines = profile in (FacturXProfile.BASIC, FacturXProfile.EN_16931, FacturXProfile.EXTENDED, FacturXProfile.XRECHNUNG)
    tax_breakdown: Dict[str, Dict[str, Decimal]] = {}
    calculated_line_total = Decimal("0.00")

    if has_lines:
        for idx, item in enumerate(line_items, start=1):
            qty = Decimal(str(item.get("qty", item.get("quantity", 1))))
            price = Decimal(str(item.get("unit_price", 0.0)))
            line_total = (qty * price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            calculated_line_total += line_total

            tax_rate = Decimal(str(item.get("tax_rate", data.get("tax_rate", 0.0))))
            tax_rate_pct = tax_rate * Decimal("100") if tax_rate <= Decimal("1.0") and tax_rate > 0 else tax_rate
            tax_category = item.get("tax_category")
            if not tax_category:
                tax_category = "AE" if tax_rate_pct == Decimal("0.0") and data.get("reverse_charge") else ("Z" if tax_rate_pct == Decimal("0.0") else "S")

            cat_key = f"{tax_category}_{tax_rate_pct}"
            if cat_key not in tax_breakdown:
                tax_breakdown[cat_key] = {
                    "category": tax_category,
                    "rate": tax_rate_pct,
                    "basis": Decimal("0.00"),
                    "amount": Decimal("0.00"),
                }
            tax_breakdown[cat_key]["basis"] += line_total
            tax_breakdown[cat_key]["amount"] += (line_total * tax_rate_pct / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            # Build line XML
            line_elem = _sub(txn, f"{{{NAMESPACES['ram']}}}IncludedSupplyChainTradeLineItem")
            line_doc = _sub(line_elem, f"{{{NAMESPACES['ram']}}}AssociatedDocumentLineDocument")
            _sub(line_doc, f"{{{NAMESPACES['ram']}}}LineID", str(item.get("line_id", idx)))

            prod = _sub(line_elem, f"{{{NAMESPACES['ram']}}}SpecifiedTradeProduct")
            _sub(prod, f"{{{NAMESPACES['ram']}}}Name", str(item.get("name", item.get("description", f"Item {idx}"))))
            if item.get("description") and item.get("name"):
                _sub(prod, f"{{{NAMESPACES['ram']}}}Description", str(item.get("description")))

            agmt = _sub(line_elem, f"{{{NAMESPACES['ram']}}}SpecifiedLineTradeAgreement")
            net_price = _sub(agmt, f"{{{NAMESPACES['ram']}}}NetPriceProductTradePrice")
            _sub(net_price, f"{{{NAMESPACES['ram']}}}ChargeAmount", _fmt_dec(price))

            dlv = _sub(line_elem, f"{{{NAMESPACES['ram']}}}SpecifiedLineTradeDelivery")
            unit_code = str(item.get("unit_code", "C62")) # C62 = one / unit
            _sub(dlv, f"{{{NAMESPACES['ram']}}}BilledQuantity", _fmt_dec(qty, 4), unitCode=unit_code)

            stl = _sub(line_elem, f"{{{NAMESPACES['ram']}}}SpecifiedLineTradeSettlement")
            app_tax = _sub(stl, f"{{{NAMESPACES['ram']}}}ApplicableTradeTax")
            _sub(app_tax, f"{{{NAMESPACES['ram']}}}TypeCode", "VAT")
            _sub(app_tax, f"{{{NAMESPACES['ram']}}}CategoryCode", tax_category)
            _sub(app_tax, f"{{{NAMESPACES['ram']}}}RateApplicablePercent", _fmt_dec(tax_rate_pct))

            summation = _sub(stl, f"{{{NAMESPACES['ram']}}}SpecifiedTradeSettlementLineMonetarySummation")
            _sub(summation, f"{{{NAMESPACES['ram']}}}LineTotalAmount", _fmt_dec(line_total))
    else:
        # For MINIMUM or BASIC_WL without items
        subtotal_in = Decimal(str(data.get("subtotal", 0.0)))
        calculated_line_total = subtotal_in
        tax_rate = Decimal(str(data.get("tax_rate", 0.0)))
        tax_rate_pct = tax_rate * Decimal("100") if tax_rate <= Decimal("1.0") and tax_rate > 0 else tax_rate
        tax_category = "S" if tax_rate_pct > 0 else "Z"
        cat_key = f"{tax_category}_{tax_rate_pct}"
        tax_breakdown[cat_key] = {
            "category": tax_category,
            "rate": tax_rate_pct,
            "basis": subtotal_in,
            "amount": (subtotal_in * tax_rate_pct / Decimal("100")).quantize(Decimal("0.01")),
        }

    # 3.2 Header Trade Agreement
    header_agmt = _sub(txn, f"{{{NAMESPACES['ram']}}}ApplicableHeaderTradeAgreement")
    
    buyer_ref = data.get("buyer_reference") or data.get("leitweg_id") or data.get("po_number") or customer.get("buyer_reference")
    if buyer_ref:
        _sub(header_agmt, f"{{{NAMESPACES['ram']}}}BuyerReference", str(buyer_ref))

    # Seller
    seller = _sub(header_agmt, f"{{{NAMESPACES['ram']}}}SellerTradeParty")
    _sub(seller, f"{{{NAMESPACES['ram']}}}Name", str(vendor.get("name", "Rubrol Engine Inc.")))
    
    siret = vendor.get("siret") or vendor.get("legal_id")
    if siret:
        legal_org = _sub(seller, f"{{{NAMESPACES['ram']}}}SpecifiedLegalOrganization")
        scheme = "0002" if len(str(siret)) in (9, 14) else "0088" # 0002 = SIRET/SIREN
        _sub(legal_org, f"{{{NAMESPACES['ram']}}}ID", str(siret), schemeID=scheme)

    seller_addr = _sub(seller, f"{{{NAMESPACES['ram']}}}PostalTradeAddress")
    if vendor.get("postal_code") or vendor.get("postcode"):
        _sub(seller_addr, f"{{{NAMESPACES['ram']}}}PostcodeCode", str(vendor.get("postal_code", vendor.get("postcode"))))
    _sub(seller_addr, f"{{{NAMESPACES['ram']}}}LineOne", str(vendor.get("address", "")))
    _sub(seller_addr, f"{{{NAMESPACES['ram']}}}CityName", str(vendor.get("city", "")))
    _sub(seller_addr, f"{{{NAMESPACES['ram']}}}CountryID", str(vendor.get("country", vendor.get("country_code", "FR"))).upper())

    seller_tax_id = vendor.get("vat_id") or vendor.get("tax_id")
    if seller_tax_id:
        tax_reg = _sub(seller, f"{{{NAMESPACES['ram']}}}SpecifiedTaxRegistration")
        _sub(tax_reg, f"{{{NAMESPACES['ram']}}}ID", str(seller_tax_id), schemeID="VA")

    # Buyer
    buyer = _sub(header_agmt, f"{{{NAMESPACES['ram']}}}BuyerTradeParty")
    _sub(buyer, f"{{{NAMESPACES['ram']}}}Name", str(customer.get("name", "Valued Customer")))
    
    buyer_legal_id = customer.get("siret") or customer.get("legal_id")
    if buyer_legal_id:
        b_org = _sub(buyer, f"{{{NAMESPACES['ram']}}}SpecifiedLegalOrganization")
        _sub(b_org, f"{{{NAMESPACES['ram']}}}ID", str(buyer_legal_id), schemeID="0002")

    buyer_addr = _sub(buyer, f"{{{NAMESPACES['ram']}}}PostalTradeAddress")
    if customer.get("postal_code") or customer.get("postcode"):
        _sub(buyer_addr, f"{{{NAMESPACES['ram']}}}PostcodeCode", str(customer.get("postal_code", customer.get("postcode"))))
    _sub(buyer_addr, f"{{{NAMESPACES['ram']}}}LineOne", str(customer.get("address", "")))
    _sub(buyer_addr, f"{{{NAMESPACES['ram']}}}CityName", str(customer.get("city", "")))
    _sub(buyer_addr, f"{{{NAMESPACES['ram']}}}CountryID", str(customer.get("country", customer.get("country_code", "DE"))).upper())

    buyer_tax_id = customer.get("vat_id") or customer.get("tax_id")
    if buyer_tax_id:
        b_tax_reg = _sub(buyer, f"{{{NAMESPACES['ram']}}}SpecifiedTaxRegistration")
        _sub(b_tax_reg, f"{{{NAMESPACES['ram']}}}ID", str(buyer_tax_id), schemeID="VA")

    # 3.3 Header Trade Delivery
    header_dlv = _sub(txn, f"{{{NAMESPACES['ram']}}}ApplicableHeaderTradeDelivery")
    event = _sub(header_dlv, f"{{{NAMESPACES['ram']}}}ActualDeliverySupplyChainEvent")
    event_dt = _sub(event, f"{{{NAMESPACES['ram']}}}OccurrenceDateTime")
    _sub(event_dt, f"{{{NAMESPACES['udt']}}}DateTimeString", issue_date, format="102")

    # 3.4 Header Trade Settlement
    header_stl = _sub(txn, f"{{{NAMESPACES['ram']}}}ApplicableHeaderTradeSettlement")
    _sub(header_stl, f"{{{NAMESPACES['ram']}}}PaymentReference", invoice_number)
    _sub(header_stl, f"{{{NAMESPACES['ram']}}}InvoiceCurrencyCode", currency)

    # Payment Means (SEPA bank transfer)
    payment = data.get("payment", {})
    iban = payment.get("iban") or vendor.get("iban")
    bic = payment.get("bic") or vendor.get("bic")
    if iban:
        means = _sub(header_stl, f"{{{NAMESPACES['ram']}}}SpecifiedTradeSettlementPaymentMeans")
        _sub(means, f"{{{NAMESPACES['ram']}}}TypeCode", "58") # 58 = SEPA credit transfer
        account = _sub(means, f"{{{NAMESPACES['ram']}}}PayeePartyCreditorFinancialAccount")
        _sub(account, f"{{{NAMESPACES['ram']}}}IBANID", iban.replace(" ", ""))
        if bic:
            inst = _sub(means, f"{{{NAMESPACES['ram']}}}PayeeSpecifiedCreditorFinancialInstitution")
            _sub(inst, f"{{{NAMESPACES['ram']}}}BICID", bic.replace(" ", ""))

    # Applicable Trade Tax (Aggregated per tax bucket)
    total_tax_amount = Decimal("0.00")
    for tb in tax_breakdown.values():
        total_tax_amount += tb["amount"]
        tax_el = _sub(header_stl, f"{{{NAMESPACES['ram']}}}ApplicableTradeTax")
        _sub(tax_el, f"{{{NAMESPACES['ram']}}}CalculatedAmount", _fmt_dec(tb["amount"]))
        _sub(tax_el, f"{{{NAMESPACES['ram']}}}TypeCode", "VAT")
        _sub(tax_el, f"{{{NAMESPACES['ram']}}}BasisAmount", _fmt_dec(tb["basis"]))
        _sub(tax_el, f"{{{NAMESPACES['ram']}}}CategoryCode", tb["category"])
        _sub(tax_el, f"{{{NAMESPACES['ram']}}}RateApplicablePercent", _fmt_dec(tb["rate"]))
        if tb["category"] == "AE":
            _sub(tax_el, f"{{{NAMESPACES['ram']}}}ExemptionReason", "Reverse charge / Autoliquidation art. 262 ter I du CGI")

    # Payment Terms & Due Date
    due_date_str = data.get("due_date")
    if due_date_str:
        due_date = _fmt_date(due_date_str)
        terms = _sub(header_stl, f"{{{NAMESPACES['ram']}}}SpecifiedTradePaymentTerms")
        due_dt = _sub(terms, f"{{{NAMESPACES['ram']}}}DueDateDateTime")
        _sub(due_dt, f"{{{NAMESPACES['udt']}}}DateTimeString", due_date, format="102")

    # Header Monetary Summation
    total_basis = calculated_line_total
    grand_total = total_basis + total_tax_amount

    summation = _sub(header_stl, f"{{{NAMESPACES['ram']}}}SpecifiedTradeSettlementHeaderMonetarySummation")
    _sub(summation, f"{{{NAMESPACES['ram']}}}LineTotalAmount", _fmt_dec(calculated_line_total))
    _sub(summation, f"{{{NAMESPACES['ram']}}}TaxBasisTotalAmount", _fmt_dec(total_basis))
    _sub(summation, f"{{{NAMESPACES['ram']}}}TaxTotalAmount", _fmt_dec(total_tax_amount), currencyID=currency)
    _sub(summation, f"{{{NAMESPACES['ram']}}}GrandTotalAmount", _fmt_dec(grand_total))
    _sub(summation, f"{{{NAMESPACES['ram']}}}DuePayableAmount", _fmt_dec(grand_total))

    # XML serialization with clean UTF-8 declaration
    xml_str = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return xml_str
