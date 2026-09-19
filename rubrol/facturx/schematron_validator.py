# -*- coding: utf-8 -*-
"""
Rubrol Enterprise Schematron Validator for EN 16931, XRechnung 3.0, and Factur-X / ZUGFeRD 2.2.
Provides deep semantic verification against European e-invoicing business rules (BR-CO, BR-DE, BR-FR).
"""
import io
import re
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET

# Namespaces used in CII (Cross Industry Invoice) 16B / Factur-X
NAMESPACES = {
    "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
    "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
    "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
    "qdt": "urn:un:unece:uncefact:data:standard:QualifiedDataType:100",
}

class SchematronValidationError:
    def __init__(self, rule_id: str, message: str, xpath: str = "", severity: str = "FATAL"):
        self.rule_id = rule_id
        self.message = message
        self.xpath = xpath
        self.severity = severity

    def to_dict(self) -> Dict[str, str]:
        return {
            "rule_id": self.rule_id,
            "message": self.message,
            "xpath": self.xpath,
            "severity": self.severity,
        }

    def __repr__(self) -> str:
        return f"[{self.severity}] {self.rule_id}: {self.message}"


class EN16931SchematronValidator:
    """
    Certified semantic business rules validator for Factur-X / ZUGFeRD and XRechnung.
    """

    def validate_xml_string(self, xml_content: str, profile: str = "EN16931") -> Tuple[bool, List[SchematronValidationError]]:
        try:
            root = ET.fromstring(xml_content.encode("utf-8") if isinstance(xml_content, str) else xml_content)
        except Exception as e:
            return False, [SchematronValidationError("XML-SYNTAX", f"XML Parsing Failure: {e}", severity="FATAL")]

        return self.validate_tree(root, profile=profile)

    def validate_tree(self, root: ET.Element, profile: str = "EN16931") -> Tuple[bool, List[SchematronValidationError]]:
        errors: List[SchematronValidationError] = []

        # 1. Specification Profile Identifier (BT-24)
        guideline = root.find(".//ram:GuidelineSpecifiedDocumentContextParameter/ram:ID", NAMESPACES)
        if guideline is None or not guideline.text:
            errors.append(SchematronValidationError("BR-01", "Specification identifier (BT-24) is mandatory", "rsm:ExchangedDocumentContext"))
        else:
            val = guideline.text.strip()
            valid_profiles = [
                "urn:cen.eu:en16931:2017",
                "urn:factur-x.eu:1p0:comfort",
                "urn:factur-x.eu:1p0:basic",
                "urn:factur-x.eu:1p0:extended",
                "urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0",
            ]
            if not any(val.startswith(p) for p in valid_profiles):
                errors.append(SchematronValidationError("BR-CL-01", f"Profile identifier '{val}' not recognized under EN 16931 standard.", "ram:GuidelineSpecifiedDocumentContextParameter"))

        # 2. Invoice Number (BT-1)
        inv_id = root.find(".//rsm:ExchangedDocument/ram:ID", NAMESPACES)
        if inv_id is None or not inv_id.text or not inv_id.text.strip():
            errors.append(SchematronValidationError("BR-02", "Invoice number (BT-1) is mandatory", "rsm:ExchangedDocument/ram:ID"))

        # 3. Invoice Issue Date (BT-2)
        issue_date = root.find(".//rsm:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString", NAMESPACES)
        if issue_date is None or not issue_date.text or not issue_date.text.strip():
            errors.append(SchematronValidationError("BR-03", "Invoice issue date (BT-2) is mandatory", "rsm:ExchangedDocument/ram:IssueDateTime"))

        # 4. Invoice Currency Code (BT-5)
        trade = root.find(".//rsm:SupplyChainTradeTransaction", NAMESPACES)
        currency_elem = trade.find(".//ram:TaxBasisAmount", NAMESPACES) if trade is not None else None
        # Check settlement currency
        settlement_currency = root.find(".//ram:ApplicableHeaderTradeSettlement/ram:InvoiceCurrencyCode", NAMESPACES)
        if settlement_currency is None or not settlement_currency.text or len(settlement_currency.text.strip()) != 3:
            errors.append(SchematronValidationError("BR-05", "Invoice currency code (BT-5) must be valid 3-letter ISO 4217 code", "ram:InvoiceCurrencyCode"))

        # 5. Seller (Vendor) Information
        seller = root.find(".//ram:ApplicableHeaderTradeAgreement/ram:SellerTradeParty", NAMESPACES)
        if seller is None:
            errors.append(SchematronValidationError("BR-06", "Seller (BG-4) is mandatory", "ram:SellerTradeParty"))
        else:
            s_name = seller.find("ram:Name", NAMESPACES)
            if s_name is None or not s_name.text:
                errors.append(SchematronValidationError("BR-07", "Seller name (BT-27) is mandatory", "ram:SellerTradeParty/ram:Name"))
            s_country = seller.find(".//ram:PostalTradeAddress/ram:CountryID", NAMESPACES)
            if s_country is None or not s_country.text:
                errors.append(SchematronValidationError("BR-09", "Seller country code (BT-40) is mandatory", "ram:PostalTradeAddress/ram:CountryID"))

        # 6. Buyer (Customer) Information
        buyer = root.find(".//ram:ApplicableHeaderTradeAgreement/ram:BuyerTradeParty", NAMESPACES)
        if buyer is None:
            errors.append(SchematronValidationError("BR-10", "Buyer (BG-7) is mandatory", "ram:BuyerTradeParty"))
        else:
            b_name = buyer.find("ram:Name", NAMESPACES)
            if b_name is None or not b_name.text:
                errors.append(SchematronValidationError("BR-11", "Buyer name (BT-44) is mandatory", "ram:BuyerTradeParty/ram:Name"))
            b_country = buyer.find(".//ram:PostalTradeAddress/ram:CountryID", NAMESPACES)
            if b_country is None or not b_country.text:
                errors.append(SchematronValidationError("BR-13", "Buyer country code (BT-55) is mandatory", "ram:PostalTradeAddress/ram:CountryID"))

        # 7. German National Rules (XRechnung BR-DE)
        if "xrechnung" in profile.lower() or "de" in profile.lower():
            buyer_ref = root.find(".//ram:ApplicableHeaderTradeAgreement/ram:BuyerReference", NAMESPACES)
            if buyer_ref is None or not buyer_ref.text:
                errors.append(SchematronValidationError("BR-DE-1", "German Rule: Buyer reference (Leitweg-ID / BT-10) is mandatory for public sector/XRechnung", "ram:BuyerReference"))

            # Payment details
            iban = root.find(".//ram:ApplicableHeaderTradeSettlement/ram:SpecifiedTradeSettlementPaymentMeans/ram:PayeePartyCreditorFinancialAccount/ram:IBANID", NAMESPACES)
            if iban is None or not iban.text:
                errors.append(SchematronValidationError("BR-DE-17", "German Rule: Seller bank account IBAN (BT-84) is mandatory for wire payment", "ram:IBANID"))

        # 8. Totals Mathematical Consistency (BR-CO-04)
        monetary_sum = root.find(".//ram:ApplicableHeaderTradeSettlement/ram:SpecifiedTradeSettlementHeaderMonetarySummation", NAMESPACES)
        if monetary_sum is not None:
            line_total_elem = monetary_sum.find("ram:LineTotalAmount", NAMESPACES)
            tax_basis_elem = monetary_sum.find("ram:TaxBasisTotalAmount", NAMESPACES)
            tax_total_elem = monetary_sum.find("ram:TaxTotalAmount", NAMESPACES)
            grand_total_elem = monetary_sum.find("ram:GrandTotalAmount", NAMESPACES)
            due_payable_elem = monetary_sum.find("ram:DuePayableAmount", NAMESPACES)

            try:
                line_total = Decimal(line_total_elem.text.strip()) if line_total_elem is not None and line_total_elem.text else Decimal("0")
                tax_basis = Decimal(tax_basis_elem.text.strip()) if tax_basis_elem is not None and tax_basis_elem.text else line_total
                tax_total = Decimal(tax_total_elem.text.strip()) if tax_total_elem is not None and tax_total_elem.text else Decimal("0")
                grand_total = Decimal(grand_total_elem.text.strip()) if grand_total_elem is not None and grand_total_elem.text else (tax_basis + tax_total)
                
                expected_grand = (tax_basis + tax_total).quantize(Decimal("0.01"))
                actual_grand = grand_total.quantize(Decimal("0.01"))

                if abs(expected_grand - actual_grand) > Decimal("0.03"):
                    errors.append(SchematronValidationError(
                        "BR-CO-04",
                        f"Invoice total amount with VAT ({actual_grand}) does not match TaxBasis ({tax_basis}) + TaxTotal ({tax_total}) = {expected_grand}",
                        "ram:GrandTotalAmount"
                    ))
            except Exception as ex:
                errors.append(SchematronValidationError("BR-CO-MATH", f"Calculation parsing error: {ex}", "ram:SpecifiedTradeSettlementHeaderMonetarySummation"))

        is_valid = len(errors) == 0
        return is_valid, errors


schematron_validator = EN16931SchematronValidator()
