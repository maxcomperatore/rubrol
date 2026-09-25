<div align="center">

# ⚡ Rubrol

### The Anti-Puppeteer Document Infrastructure

**Sub-10ms Native Rust Document Engine Powered by Typst. Zero Headless Browsers. Pure Deterministic Performance.**

[![GitHub License](https://img.shields.io/badge/license-LGPL--3.0-blue.svg)](https://github.com/maxcomperatore/rubrol/blob/main/LICENSE)
[![Rust](https://img.shields.io/badge/built%20with-Rust-orange.svg)](https://www.rust-lang.org/)
[![Engine](https://img.shields.io/badge/powered%20by-Typst-239dad.svg)](https://typst.app/)
[![Compliance](https://img.shields.io/badge/standards-PDF%2FA--3b%20%7C%20Factur--X%20%7C%20ZUGFeRD-success.svg)](https://rubrol.com/#compliance)
[![Latency](https://img.shields.io/badge/p99%20latency-%3C10ms-brightgreen.svg)](https://rubrol.com/#studio)
[![Memory](https://img.shields.io/badge/RAM-%3C28MB-blueviolet.svg)](https://rubrol.com/#benchmarks)

[Website](https://rubrol.com) • [Live Studio](https://rubrol.com/#studio) • [Benchmarks](https://rubrol.com/#benchmarks) • [Documentation](https://rubrol.com/docs) • [Sponsor](https://github.com/sponsors/maxcomperatore)

</div>

---

## 🏛️ About the Organization

**Rubrol** develops modern, resource-efficient developer infrastructure designed to permanently replace multi-gigabyte headless Chromium clusters, legacy wkhtmltopdf instances, and heavy Java runtimes with native, memory-safe compiled binaries.

Every month, thousands of companies burn hundreds of thousands of dollars on cloud computing just running browser instances to generate simple PDF invoices and reports. We engineer native systems software that solves document compilation at the root.

---

## 🚀 Performance Benchmarks

Tested on standard production cloud instances (2 vCPU, 4GB RAM, 100 concurrent requests):

| Metric | Rubrol (Native Typst) | Puppeteer / Chromium | Gotenberg | WeasyPrint | wkhtmltopdf (Deprecated) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Execution Latency** | **8.4 ms** | 1,420 ms | 980 ms | 2,150 ms | 680 ms |
| **Idle Memory (RAM)** | **18 MB** | 420 MB | 550 MB | 140 MB | 95 MB |
| **Peak Concurrency RAM** | **< 32 MB** | 1,850 MB (OOM risk) | 1,200 MB | 820 MB | 450 MB |
| **Cold Start Time** | **< 1 ms** | ~2,500 ms | ~1,800 ms | ~450 ms | ~300 ms |
| **PDF/A-3b Compliance** | **Native ISO 19005-3** | Requires ghostscript | Plugin dependent | Partial | Broken / Non-compliant |
| **Factur-X / ZUGFeRD** | **Native Built-in** | Manual injection | None | None | None |

---

## 🧩 Architectural Blueprint

```
   ┌────────────────────────────────────────────────────────┐
   │        Your Application (Python / Go / Node / PHP)      │
   └───────────────────────────┬────────────────────────────┘
                               │ JSON Payload + Raw Data
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │             Rubrol High-Throughput Sidecar              │
   │  ┌───────────────────────┬───────────────────────────┐  │
   │  │ Typst Layout Engine   │ XML CII / UBL Embedder    │  │
   │  │ (Sub-10ms Compilation)│ (EN 16931 Validation)    │  │
   │  └───────────────────────┴───────────────────────────┘  │
   └───────────────────────────┬────────────────────────────┘
                               │ Native PDF/A-3b Output
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │ Compliant E-Invoice / Document (Deterministic, <28MB)   │
   └────────────────────────────────────────────────────────┘
```

---

## 📦 Organization Repositories

| Repository | Description | Status |
| :--- | :--- | :--- |
| [`rubrol/rubrol`](https://github.com/maxcomperatore/rubrol) | Core high-performance document compiler, CLI, and WASM studio. | Active / Core |
| [`rubrol/docker-sidecar`](https://github.com/maxcomperatore/rubrol) | Ultra-lean container sidecar (<40MB) for Kubernetes and Docker Compose. | Production |
| `rubrol/rubrol-python` | Idiomatic Python client with Pydantic typing and asynchronous streaming. | In Development |
| `rubrol/rubrol-go` | Zero-CGO Go client with native concurrency and connection pooling. | In Development |
| `rubrol/rubrol-node` | TypeScript / Node.js client replacing Puppeteer child processes. | In Development |

---

## ⚡ 30-Second Quickstart

### Run with Docker Sidecar:
```bash
docker run -d -p 8080:8080 --name rubrol ghcr.io/maxcomperatore/rubrol:latest
```

### Compile an invoice via HTTP:
```bash
curl -X POST http://localhost:8080/v1/compile \
  -H "Content-Type: application/json" \
  -d '{
    "template": "invoice",
    "data": { "invoice_id": "INV-2026-001", "total": 1250.00 }
  }' \
  --output invoice.pdf
```

---

## 🌐 Community & Ecosystem

- **Documentation & Playground:** [rubrol.com/#studio](https://rubrol.com/#studio)
- **Bug Reports & Feature Requests:** [GitHub Issues](https://github.com/maxcomperatore/rubrol/issues)
- **Security Inquiries:** [SECURITY.md](https://github.com/maxcomperatore/rubrol/blob/main/SECURITY.md)
- **Sponsorship & Enterprise Inquiries:** [funding.json](https://github.com/maxcomperatore/rubrol/blob/main/funding.json) or email `maxcomperatore@gmail.com`

<div align="center">
  <sub>Built with mechanical sympathy from Mendoza, Argentina. Copyright © 2026 Rubrol.</sub>
</div>
