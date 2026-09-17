# Rubrol: High-Performance Typst Document & E-Invoicing Engine

[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/maxcomperatore/rubrol/docker-publish.yml?branch=main&style=flat-square&logo=github)](https://github.com/maxcomperatore/rubrol)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square)](https://github.com/maxcomperatore/rubrol/blob/main/LICENSE)
[![Standards: EN 16931](https://img.shields.io/badge/Standards-EN%2016931%20%2F%20Factur--X-amber?style=flat-square)](https://rubrol.com)
[![Docker Multi-Arch](https://img.shields.io/badge/Architecture-amd64%20%7C%20arm64-success?style=flat-square&logo=docker)](https://github.com/maxcomperatore/rubrol)

**Rubrol** is a lightweight, memory-safe, sub-15ms document compilation sidecar and e-invoicing engine powered by **Apache 2.0 Typst**. Designed as a drop-in replacement for bloated Headless Chrome, Puppeteer, Gotenberg, and Ghostscript pipelines.

---

## ⚡ Key Highlights
* **🏎️ Sub-15ms Warm Compilation:** Generates dual-layer PDF/A-3b documents with embedded XML 70x faster than headless browser clusters.
* **🛡️ Zero-Chrome Architecture:** <28MB memory footprint. No V8 garbage collection storms, zero zombie processes, no container OOM (exit code 137).
* **🇪🇺 Built for European Compliance:** Native validation and embedding for **EN 16931**, **Factur-X 1.0**, **ZUGFeRD 2.2**, and German *Wachstumschancengesetz* / French *PDP/PPF* mandates.
* **🔒 100% Self-Hosted & Air-Gapped:** Runs entirely inside your VPC. Zero data egress, GDPR-compliant by design.
* **📦 Multi-Arch Docker:** Pre-built for `linux/amd64` and `linux/arm64` (Apple Silicon & AWS Graviton).

---

## 🚀 Quickstart (Under 60 Seconds)

### 1. Run the Docker Container
```bash
docker run -d -p 8080:8080 --name rubrol ghcr.io/maxcomperatore/rubrol:latest
```

### 2. Verify Health
```bash
curl http://localhost:8080/health
# {"status": "ok", "engine": "typst", "version": "0.1.0"}
```

### 3. Generate a Certified Factur-X / ZUGFeRD E-Invoice
```bash
curl -X POST http://localhost:8080/v1/facturx/render \
  -H "Content-Type: application/json" \
  -d '{
    "template": "b2b_invoice",
    "profile": "EN 16931",
    "data": {
      "invoice_number": "FA-2026-0842",
      "issued_date": "2026-09-17",
      "due_date": "2026-10-17",
      "currency_symbol": "€",
      "status": "PAID",
      "seller": {
        "name": "Acme Europe SAS",
        "vat_id": "FR12345678901",
        "address": "15 Rue de la Paix",
        "city": "75002 Paris, France"
      },
      "buyer": {
        "name": "Deutsche Cloud GmbH",
        "vat_id": "DE987654321",
        "address": "Friedrichstraße 42",
        "city": "10117 Berlin, Germany"
      },
      "line_items": [
        {
          "name": "Cloud Infrastructure Dedicated Node",
          "qty": 1,
          "unit_price": 1000.00,
          "tax_rate": 0.20
        }
      ],
      "grand_total": 1200.00
    }
  }' --output invoice_facturx.pdf
```

---

## 📊 Benchmark Comparison

| Metric | Puppeteer / Gotenberg | Mustangproject (Java) | Ghostscript | **Rubrol (Typst)** |
| :--- | :--- | :--- | :--- | :--- |
| **Warm Render Latency** | 900ms – 1,800ms | 450ms – 1,100ms | 350ms – 850ms | **14ms (70x faster)** |
| **RAM Footprint** | 500MB – 2,000MB | 350MB – 650MB | ~80MB | **< 28MB** |
| **Container Image** | ~1.8 GB | ~450 MB | ~120 MB | **~42 MB** |
| **Visual Document Layout** | HTML/CSS | ❌ None (external PDF) | ❌ None (external PDF) | **✅ Mathematical Typst** |
| **ISO 19005-3 (PDF/A-3b)** | ❌ Needs post-processors | ✅ Supported | ⚠️ Fragile PS script | **✅ Native in-memory** |
| **EN 16931 Validation** | ❌ None | ✅ Saxon Schematron | ❌ Blind byte embed | **✅ In-memory validator** |

---

## 🔗 Official Links & Resources
* **Website & Studio:** [https://rubrol.com](https://rubrol.com)
* **GitHub Repository:** [https://github.com/maxcomperatore/rubrol](https://github.com/maxcomperatore/rubrol)
* **Engineering Teardowns & Architecture Guides:**
  * [Why Puppeteer Fails EN 16931 E-Invoicing](https://rubrol.com/articles/why-puppeteer-fails-en16931)
  * [Stripe Invoices to Factur-X / ZUGFeRD in 5 Minutes](https://rubrol.com/articles/stripe-facturx-zugferd)
  * [Rubrol vs Mustangproject: Retiring the 300MB Java JVM](https://rubrol.com/articles/rubrol-vs-mustangproject)
  * [Rubrol vs Ghostscript: Why PostScript Scripts Are an Infrastructure Hazard](https://rubrol.com/articles/rubrol-vs-ghostscript)
  * [Rubrol vs Gotenberg: Why Headless Chromium Clusters Are the Wrong Tool](https://rubrol.com/articles/rubrol-vs-gotenberg)

---

## 📄 License
Rubrol is open-source under the [Apache 2.0 License](https://github.com/maxcomperatore/rubrol/blob/main/LICENSE).
