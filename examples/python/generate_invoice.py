# -*- coding: utf-8 -*-
"""
Rubrol Python Client Example
Renders an invoice via the local Rubrol sidecar and writes the resulting PDF.
"""
import urllib.request
import json
import time

RUBROL_URL = "http://localhost:8080/v1/render"

payload = {
    "template": "b2b_invoice",
    "data": {
        "invoice_number": "INV-2026-PY01",
        "issued_date": "2026-09-17",
        "due_date": "2026-10-17",
        "currency": "USD",
        "currency_symbol": "$",
        "vendor": {
            "name": "Acme SaaS Cloud Inc.",
            "tax_id": "US-9918204",
            "address": "100 Pine Street, Suite 2400",
            "city": "San Francisco, CA 94111",
            "email": "billing@acme.dev"
        },
        "customer": {
            "name": "Global Logistics Corp",
            "tax_id": "US-5541092",
            "address": "450 Lexington Ave",
            "city": "New York, NY 10017",
            "email": "ap@globallogistics.com"
        },
        "line_items": [
            {
                "description": "Rubrol High-Throughput Sidecar Cluster (Annual)",
                "qty": 1,
                "unit_price": 490.00
            },
            {
                "description": "Zero-Copy Factur-X & PDF/A-2b Engine Integration",
                "qty": 1,
                "unit_price": 350.00
            }
        ]
    },
    "format": "pdf",
    "pdf_standard": "a-2b"
}

print(f"Sending render request to {RUBROL_URL}...")
start = time.perf_counter()

req = urllib.request.Request(
    RUBROL_URL,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

with urllib.request.urlopen(req) as resp:
    pdf_bytes = resp.read()
    render_time = resp.headers.get("X-Render-Time-Ms", "N/A")

output_file = "python_invoice.pdf"
with open(output_file, "wb") as f:
    f.write(pdf_bytes)

elapsed_ms = (time.perf_counter() - start) * 1000
print(f"Success! {len(pdf_bytes):,} bytes written to {output_file}")
print(f"Sidecar Compile Time: {render_time}ms | Total HTTP Latency: {elapsed_ms:.2f}ms")
