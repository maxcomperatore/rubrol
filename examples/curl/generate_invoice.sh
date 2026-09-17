#!/usr/bin/env bash
# Rubrol cURL Example — Instant Single-Command PDF Generation

curl -s -X POST http://localhost:8080/v1/render \
  -H "Content-Type: application/json" \
  -d '{
    "template": "b2b_invoice",
    "format": "pdf",
    "pdf_standard": "a-2b",
    "data": {
      "invoice_number": "INV-2026-CURL01",
      "issued_date": "2026-09-17",
      "due_date": "2026-10-17",
      "currency": "USD",
      "currency_symbol": "$",
      "vendor": {
        "name": "Rubrol Engine Inc.",
        "tax_id": "US-481902948",
        "address": "548 Market Street",
        "city": "San Francisco, CA 94104",
        "email": "billing@rubrol.com"
      },
      "customer": {
        "name": "Stripe Atlas Startup",
        "tax_id": "US-1102948",
        "address": "354 Oyster Point Blvd",
        "city": "South San Francisco, CA 94080",
        "email": "finance@startup.dev"
      },
      "line_items": [
        {
          "description": "Rubrol Pro Sidecar Engine License",
          "qty": 1,
          "unit_price": 490.00
        }
      ]
    }
  }' \
  -o curl_invoice.pdf

echo "Rendered curl_invoice.pdf successfully."
