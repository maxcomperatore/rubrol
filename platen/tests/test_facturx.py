"""
Automated Test Suite for Platen EU Factur-X / ZUGFeRD Turnkey Suite.
Verifies UN/CEFACT CII XML generation, PDF/A-3b container packaging,
EN 16931 payload validator, extraction, and performance.
"""
import json
import os
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from platen.facturx.generator import generate_facturx_xml, FacturXProfile, PROFILE_URNS
from platen.facturx.packager import package_facturx_pdf, extract_facturx_xml
from platen.facturx.validator import validate_facturx_payload, validate_facturx_pdf
from platen.core.engine import PlatenEngine

SAMPLE_DATA_PATH = Path(__file__).parent.parent / "data" / "facturx_invoice.json"

class TestFacturXSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SAMPLE_DATA_PATH, "r", encoding="utf-8") as f:
            cls.sample_data = json.load(f)
        cls.engine = PlatenEngine()

    def test_xml_generator_en16931(self):
        xml_bytes = generate_facturx_xml(self.sample_data, profile=FacturXProfile.EN_16931)
        self.assertTrue(len(xml_bytes) > 0)
        
        root = ET.fromstring(xml_bytes)
        self.assertTrue(root.tag.endswith("CrossIndustryInvoice"))

        # Verify profile URN
        found_urn = False
        for el in root.iter():
            if el.tag.endswith("GuidelineSpecifiedDocumentContextParameter"):
                for sub in el:
                    if sub.tag.endswith("ID") and sub.text == PROFILE_URNS[FacturXProfile.EN_16931]:
                        found_urn = True
        self.assertTrue(found_urn, "EN 16931 guideline URN not found in XML")

        # Verify Seller and Buyer VAT IDs
        vat_ids = []
        for el in root.iter():
            if el.tag.endswith("SpecifiedTaxRegistration"):
                for sub in el:
                    if sub.tag.endswith("ID"):
                        vat_ids.append(sub.text)
        self.assertIn("FR82982391820", vat_ids)
        self.assertIn("DE391048291", vat_ids)

        # Verify Monetary Summation
        grand_total = None
        for el in root.iter():
            if el.tag.endswith("GrandTotalAmount"):
                grand_total = el.text
        self.assertEqual(grand_total, "3468.00")

    def test_xml_generator_profiles(self):
        all_profiles = [
            FacturXProfile.MINIMUM,
            FacturXProfile.BASIC_WL,
            FacturXProfile.BASIC,
            FacturXProfile.EN_16931,
            FacturXProfile.EXTENDED,
            FacturXProfile.XRECHNUNG,
        ]
        for prof in all_profiles:
            xml = generate_facturx_xml(self.sample_data, profile=prof)
            self.assertIn(PROFILE_URNS[prof].encode("utf-8"), xml)

    def test_payload_validator_success(self):
        errors = validate_facturx_payload(self.sample_data)
        self.assertEqual(errors, [])

    def test_payload_validator_failure(self):
        bad_data = dict(self.sample_data)
        del bad_data["invoice_number"]
        errors = validate_facturx_payload(bad_data)
        self.assertTrue(any("invoice_number" in e for e in errors))

        bad_currency = dict(self.sample_data)
        bad_currency["currency"] = "EUROPEAN_DOLLAR"
        errors = validate_facturx_payload(bad_currency)
        self.assertTrue(any("currency" in e for e in errors))

        bad_subtotal = dict(self.sample_data)
        bad_subtotal["subtotal"] = 9999.99
        errors = validate_facturx_payload(bad_subtotal)
        self.assertTrue(any("Subtotal mismatch" in e for e in errors))

    def test_end_to_end_packager_and_extraction(self):
        # 1. Compile base PDF/A-3b
        pdf_base, _ = self.engine.render(
            template="facturx_invoice",
            data=self.sample_data,
            pdf_standard="a-3b"
        )
        self.assertTrue(pdf_base.startswith(b"%PDF"))

        # 2. Generate XML
        xml_bytes = generate_facturx_xml(self.sample_data, profile="EN 16931")

        # 3. Package
        packaged_pdf = package_facturx_pdf(pdf_base, xml_bytes, profile="EN 16931")
        self.assertTrue(len(packaged_pdf) > 50000)
        self.assertIn(b"/EmbeddedFiles", packaged_pdf)

        # 4. Extract
        extracted = extract_facturx_xml(packaged_pdf)
        self.assertEqual(extracted, xml_bytes)

        # 5. Validate Container
        report = validate_facturx_pdf(packaged_pdf)
        self.assertTrue(report["valid"])
        self.assertTrue(report["embedded_xml_found"])
        self.assertTrue(report["af_relationship_valid"])
        self.assertTrue(report["xmp_metadata_valid"])
        self.assertEqual(report["conformance_level"], "EN 16931")
        self.assertEqual(report["invoice_number"], "FA-2026-0842")
        self.assertEqual(report["grand_total"], "3468.00")
        self.assertEqual(report["currency"], "EUR")

    def test_engine_render_facturx_method(self):
        pdf_bytes, xml_bytes, elapsed_ms = self.engine.render_facturx(
            data=self.sample_data,
            template="facturx_invoice",
            profile="EN 16931"
        )
        self.assertTrue(len(pdf_bytes) > 0)
        self.assertTrue(len(xml_bytes) > 0)
        self.assertLess(elapsed_ms, 500.0) # sub-500ms even on cold unoptimized run

if __name__ == "__main__":
    unittest.main()
