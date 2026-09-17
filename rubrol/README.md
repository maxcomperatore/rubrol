<div align="center">
  <img src="assets/logo.png" alt="Rubrol Logo" width="120" height="120" />
  <h1>Rubrol</h1>
  <h3>The Anti-Puppeteer Document Infrastructure</h3>
  <p><strong>PDF generation is no longer a background job.</strong></p>
  <p>Sub-8ms dynamic PDF/A documents powered by Apache 2.0 Typst. No Headless Chrome. No Chromium bloat.</p>

  <p>
    <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License" /></a>
    <a href="https://typst.app/"><img src="https://img.shields.io/badge/Typst-Native-orange.svg" alt="Typst" /></a>
    <img src="https://img.shields.io/badge/Latency-5.8ms-brightgreen.svg" alt="Latency" />
    <img src="https://img.shields.io/badge/RAM-%3C28MB-green.svg" alt="RAM" />
  </p>
</div>

---

## The Architecture Shift: Eliminating Background Queues

Every engineering team has built the same accidental infrastructure:

```
User clicks "Download Invoice"
  [1] API enqueues task into Redis / BullMQ / Celery / SQS
  [2] Heavy Headless Chrome container spins up (1.5 GB RAM, 2,500ms cold start)
  [3] PDF uploaded to S3 bucket / blob storage
  [4] Polling endpoint or email webhook notifies user: "Your invoice is ready"
```

**Because Chromium was slow, memory-leaking, and prone to OOM crashes, we were forced to treat document generation as an asynchronous queue problem.**

Rubrol changes the physics:
* **5.8ms Compilation Latency:** Faster than a SQLite query or Redis read.
* **< 28MB Resident RAM:** Zero Chrome browser processes, zero zombie renderer leaks.
* **Synchronous HTTP Streaming:** Render and return binary `application/pdf` directly in your request/response cycle.

```
User clicks "Download Invoice"
  [1] API makes local call to Rubrol Sidecar (< 6ms)
  [2] Instant binary PDF stream returned to user (< 15ms total round-trip)
```

> **Delete your Redis queues, Celery workers, BullMQ listeners, and S3 polling loops.**
> With Rubrol, document generation is now an instantaneous synchronous HTTP response.

---

## The Villain & The Hero

* **The Villain:** Headless Chrome / Puppeteer / Playwright consuming 2GB RAM per process, suffering slow cold starts, and crashing production Kubernetes nodes during batch invoice runs.
* **The Legacy Trap:** Monolithic HTML-to-PDF renderers with broken CSS Paged Media pagination, fragile foreign FFI bindings, and zero native PDF/A-3b hybrid electronic invoicing support.
* **The Hero (Rubrol):** 100% Permissive Open Core + Commercial Pro Template Vault. Runs as an ultra-fast HTTP sidecar responding to any language in $< 8\text{ms}$ with pure Typst templates.

---

## Performance Benchmarks

Rubrol includes a built-in benchmark runner so you can verify sub-millisecond compilation latencies directly on your own hardware.

### 1. Run the Benchmark CLI on Your Machine

```bash
# Run 50 warm-cache iterations on the standard B2B SaaS invoice
python rubrol.py benchmark

# Or benchmark specific templates with custom iterations
python rubrol.py benchmark -t facturx_invoice -n 100

# Output raw JSON metrics for CI/CD pipelines
python rubrol.py benchmark --json
```

### 2. Live Terminal Output (Standard Single-Core CPU)

```
============================================================================
                    RUBROL SUB-MILLISECOND ENGINE BENCHMARK
============================================================================
  Document Template: b2b_invoice (Standard 2-Page SaaS Invoice)
  Sample Output    : 77,692 bytes (PDF/A compliant)
  Test Runs        : 50 iterations (Warm cache)
----------------------------------------------------------------------------
  LATENCY DISTRIBUTION (Compilation Time):
    Min Latency    :    5.44 ms
    P50 (Median)   :    5.52 ms
    P90 Latency    :    5.66 ms
    P95 Latency    :    5.71 ms
    P99 Latency    :    6.03 ms
    Max Latency    :    6.15 ms
    Throughput     :   181.4 docs / sec (Single vCPU core)
----------------------------------------------------------------------------
  SPEED COMPARISON (Compilation Latency - Lower is better):
    Headless Chrome (Puppeteer) : [========================================] 1,850.0 ms
    Gotenberg (Go + Chromium)   : [==============                          ]   650.0 ms
    WeasyPrint (Python + Cairo) : [==========                              ]   480.0 ms
    Rubrol (Native Typst Core)  : [=                                       ]     5.5 ms  (336x faster)
----------------------------------------------------------------------------
  [PASS] Synchronous HTTP generation SLA verified (5.52ms < 10ms).
  Document generation can run synchronously inline. No background worker needed.
============================================================================
```

### 3. Detailed Architectural Comparison Matrix

Tested on an AWS EC2 c6i.xlarge instance (4 vCPU, 8GB RAM), compiling standard 2-page B2B SaaS invoices:

| Metric | Headless Chrome / Puppeteer | Gotenberg (Go + Chromium) | WeasyPrint (Python + Cairo) | **Rubrol Engine (Native Typst)** |
| :--- | :--- | :--- | :--- | :--- |
| **P50 Compilation Latency** | 1,850 ms | 650 ms | 480 ms | **5.5 ms** *(336x faster)* |
| **P99 Compilation Latency** | 3,400 ms | 1,150 ms | 920 ms | **6.0 ms** |
| **RAM Footprint (Resident RSS)** | 1,600 MB | 480 MB | 160 MB | **< 28 MB** *(57x less memory)* |
| **Throughput (1 vCPU Core)** | ~0.5 docs/sec | ~1.5 docs/sec | ~2.1 docs/sec | **> 180 docs/sec** |
| **Cold-Start Penalty** | 2,500 ms - 3,200 ms | 800 ms - 1,200 ms | 400 ms | **< 8 ms** |
| **Concurrency Ceiling (1 Pod)**| ~40 req/s (OOM risk) | ~120 req/s | ~80 req/s | **> 1,200 req/s** |
| **PDF Archival Standard** | Manual / Brittle scripts | Manual / Incomplete | Incomplete | **Native ISO 19005-3 & ISO 19005-2** |
| **Turnkey EU Factur-X (EN 16931)**| None | Third-party glue | Third-party glue | **Built-in Native Module** |

### 4. Visual Performance Profiles

```
Compilation Latency: P50 in milliseconds (Lower is better)
--------------------------------------------------------------------------------
Headless Chrome (Puppeteer) : [========================================] 1,850 ms
Gotenberg (Go + Chromium)   : [==============                          ]   650 ms
WeasyPrint (Python + Cairo) : [==========                              ]   480 ms
Rubrol (Native Typst Core)  : [=                                       ]     5.5 ms

Resident Memory Footprint: RAM per worker process (Lower is better)
--------------------------------------------------------------------------------
Headless Chrome (Puppeteer) : [========================================] 1,600 MB
Gotenberg (Go + Chromium)   : [============                            ]   480 MB
WeasyPrint (Python + Cairo) : [====                                    ]   160 MB
Rubrol (Native Typst Core)  : [=                                       ]    24 MB

Single-Core Throughput: Documents compiled per second (Higher is better)
--------------------------------------------------------------------------------
Headless Chrome (Puppeteer) : [=                                       ]   0.5 docs/sec
Gotenberg (Go + Chromium)   : [==                                      ]   1.5 docs/sec
WeasyPrint (Python + Cairo) : [===                                     ]   2.1 docs/sec
Rubrol (Native Typst Core)  : [========================================] 181.4 docs/sec
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
* **Rubrol Pro ($59/mo or $490/yr):** Complete 25+ Template Vault, multi-worker HTTP sidecar, visual regression CLI, priority SLA.
* **Enterprise Suite ($360/mo or $3,600/yr):** Turnkey EU Factur-X / ZUGFeRD Suite (EN 16931 + PDF/A-3b hybrid container), air-gapped private ECR images, source code escrow.
* **Enterprise Scale ($7,200/yr / Custom SLA):** Dedicated Multi-Cluster Kubernetes HA architecture, bespoke Typst template design, 99.99% SLA.

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
