---
name: rubrol
description: Add sub-millisecond, lightweight (<28MB RAM) PDF document generation, SaaS billing invoices, and EU Factur-X / ZUGFeRD compliance to your application using Rubrol.
---

# Rubrol PDF Engine Skill

Rubrol is an open-core, sub-8ms PDF compilation engine powered by native Apache 2.0 Typst. It eliminates Headless Chrome, Puppeteer, and Gotenberg memory bloat.

## Quick Start Guide

### 1. Run Rubrol via Docker
```bash
docker run -d -p 8000:8000 --name rubrol ghcr.io/maxcomperatore/rubrol:latest
```

### 2. Generate a Document from any Backend
Make an HTTP POST request to `http://localhost:8000/v1/render`:

```bash
curl -X POST http://localhost:8000/v1/render \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "invoice",
    "data": {
      "invoice_number": "INV-2026-001",
      "customer": "Acme Corp",
      "total": "$1,250.00"
    }
  }' \
  --output invoice.pdf
```

### 3. Generate Ad-Hoc Typst Documents (`/v1/render/raw`)
Pass arbitrary Typst code with `sys.inputs`:

```json
{
  "content": "#let data = sys.inputs\n#set page(paper: \"a4\", margin: 2cm)\n= Report: #data.title\nDate: #data.date\n\n#table(columns: (1fr, 1fr), [Item], [Price], ..data.items.map(it => (it.name, str(it.price))).flatten())",
  "inputs": {
    "title": "Quarterly Financials",
    "date": "2026-09-17",
    "items": [{"name": "Compute", "price": 120}, {"name": "Storage", "price": 45}]
  }
}
```

### 4. EU Factur-X & ZUGFeRD E-Invoicing
For legally certified European hybrid e-invoices (PDF/A-3b + embedded XML):
Endpoint: `POST /v1/facturx/render`
