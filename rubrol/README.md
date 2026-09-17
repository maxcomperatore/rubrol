<div align="center">
  <img src="assets/logo.png" alt="Rubrol Logo" width="120" height="120" />
  <h1>Rubrol: The Anti-Puppeteer PDF Engine</h1>
  <p><strong>Sub-8ms dynamic PDF/A documents powered by Apache 2.0 Typst. No Headless Chrome. No Chromium bloat.</strong></p>

  <p>
    <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License" /></a>
    <a href="https://typst.app/"><img src="https://img.shields.io/badge/Typst-Native-orange.svg" alt="Typst" /></a>
    <img src="https://img.shields.io/badge/Latency-5.8ms-brightgreen.svg" alt="Latency" />
    <img src="https://img.shields.io/badge/RAM-%3C28MB-green.svg" alt="RAM" />
  </p>
</div>

---

## The Villain & The Hero

* **The Villain:** Headless Chrome / Puppeteer / Playwright consuming 2GB RAM per process, suffering slow cold starts, and crashing production Kubernetes nodes during batch invoice runs.
* **The Legacy Trap:** Monolithic HTML-to-PDF renderers with broken CSS Paged Media pagination, fragile foreign FFI bindings, and zero native PDF/A-3b hybrid electronic invoicing support.
* **The Hero (Rubrol):** 100% Permissive Open Core + Commercial Pro Template Vault. Runs as an ultra-fast HTTP sidecar responding to any language in $< 8\text{ms}$ with pure Typst templates.

---

## Quick Comparison

| Vector | Headless Chrome / Puppeteer | Traditional Engines (Gotenberg/Weasy) | **Rubrol Engine** |
| :--- | :--- | :--- | :--- |
| **Execution Latency** | 1,800ms – 3,500ms | 450ms – 850ms | **5.8ms (Sub-8ms SLA)** |
| **RAM Footprint** | 1.5 GB – 2.2 GB | ~480 MB | **< 28 MB** |
| **Licensing** | Apache / Proprietary Infra | MIT / LGPL | **Apache 2.0 Open Core** |
| **Architecture** | Heavy Node.js / Headless Browser | Monolithic Web Service | **Universal Docker Sidecar + CLI** |
| **EU e-Invoicing** | None (Raw HTML) | Manual Attachment Scripts | **Turnkey Factur-X / ZUGFeRD 2.2** |
| **Template Formatting** | Brittle CSS print media | Complex HTML/CSS hacks | **Git-Native Plain `.typ` Files** |
| **Commercial Pricing** | Ballooning AWS/GCP node bills | Maintenance overhead | **$490 / yr or $990 Lifetime** |

### Benchmark Resource Profiles

```
RAM Footprint (Lower is better)
Chromium (Puppeteer)   ████████████████████████████████████████ 1,600 MB
Gotenberg (Chrome)     ████████████ 480 MB
Rubrol (Typst Native)  █ 22 MB

Compilation Time (Lower is better)
Chromium (Puppeteer)   ████████████████████████████████████████ 1,850 ms
Gotenberg              ████████████ 650 ms
Rubrol (Typst Native)  █ 8 ms
```

---

## Getting Started in 30 Seconds

### 1. Installation
```bash
pip install typst
```

### 2. Run the Interactive Web Playground & HTTP Sidecar
```bash
python rubrol/core/server.py --port 8080
```
Open **`http://localhost:8080`** in your browser to test the live split-pane playground, SVG vector preview, and Puppeteer cost calculator.

### 3. CLI Mode
```bash
python rubrol.py compile \
  --template rubrol/templates/b2b_invoice.typ \
  --data rubrol/data/b2b_invoice.json \
  --output invoice.pdf \
  --standard a-2b
```

### 4. HTTP Sidecar Request (from Python, Node, Go, or cURL)
```bash
curl -X POST http://localhost:8080/v1/render \
  -H "Content-Type: application/json" \
  -d '{
    "template": "b2b_invoice",
    "data": {
      "invoice_number": "INV-2026-0042",
      "total": 2500.00
    },
    "pdf_standard": "a-2b"
  }' --output invoice.pdf
```

---

## Turnkey Template Vault

Rubrol comes with production-tested, multi-page templates:
1. **`b2b_invoice`**: Stripe/Linear-grade SaaS invoice with multi-currency, tax calculation, and payment terms.
2. **`compliance_certificate`**: SOC 2 / ISO 27001 / HIPAA attestation certificate with cryptographic signature markers.
3. **`medical_intake`**: Healthcare clinical encounter summary and vital signs grid (HIPAA-compliant formatting).

---

## Docker Sidecar Deployment

Run Rubrol as a hardened sidecar next to your application:

```bash
docker build -f rubrol/docker/Dockerfile -t rubrol:latest .
docker run -d -p 8080:8080 --name rubrol-sidecar rubrol:latest
```

Resource footprint in Kubernetes / ECS:
```yaml
resources:
  limits:
    cpu: 500m
    memory: 128Mi
  requests:
    cpu: 50m
    memory: 32Mi
```

---

## Commercial Licensing

* **Community Core ($0 / Apache 2.0):** CLI compiler, local daemon, unlimited documents, free forever.
* **Rubrol Pro ($490 / year):** Complete 25+ Template Vault, multi-worker HTTP sidecar, visual regression CLI, priority SLA.
* **Enterprise Suite ($2,400 / year):** Turnkey EU Factur-X / ZUGFeRD Suite (EN 16931 + PDF/A-3b hybrid container), air-gapped private ECR images, source code escrow, bespoke template design service.

---

## Enterprise Tier: EU Factur-X / ZUGFeRD Turnkey Suite

> **Solve the 2026/2027 French & German B2B E-Invoicing Legal Mandate overnight.**

European B2B transactions legally require hybrid electronic invoices compliant with **EN 16931** (Factur-X in France, ZUGFeRD in Germany). Rubrol packages human-readable PDF/A-3b containers with automatically generated, schema-validated UN/CEFACT CII XML (`factur-x.xml`) in $< 20\text{ms}$.

### 1. Compile Factur-X Invoice via CLI
```bash
python rubrol.py facturx \
  --template rubrol/templates/facturx_invoice.typ \
  --data rubrol/data/facturx_invoice.json \
  --output invoice_facturx.pdf \
  --profile "EN 16931"
```

### 2. Sidecar HTTP Request
```bash
curl -X POST http://localhost:8080/v1/facturx/render \
  -H "Content-Type: application/json" \
  -d @rubrol/data/facturx_invoice.json \
  --output invoice_facturx.pdf
```

Response Headers:
```http
HTTP/1.1 200 OK
Content-Type: application/pdf
X-FacturX-Profile: EN 16931
X-FacturX-XML-Bytes: 6040
X-Render-Time-Ms: 18.20
```

### 3. Validate Any Factur-X PDF Container
```bash
python rubrol.py validate-facturx invoice_facturx.pdf
```

Outputs:
```json
{
  "valid": true,
  "embedded_xml_found": true,
  "af_relationship_valid": true,
  "xmp_metadata_valid": true,
  "conformance_level": "EN 16931",
  "invoice_number": "FA-2026-0842",
  "grand_total": "3468.00",
  "currency": "EUR",
  "xml_bytes": 6040,
  "errors": []
}
```

### 4. Extract Embedded `factur-x.xml`
```bash
python rubrol.py extract-facturx invoice_facturx.pdf -o factur-x.xml
```
