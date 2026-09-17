# Rubrol PDF Engine - Cursor Rules & Agent Guidelines

You are an expert software engineer integrating Rubrol into modern web applications and microservices.
Rubrol is an Apache 2.0 sub-millisecond, memory-efficient (<28MB RAM, <8ms compile) PDF engine powered by native Typst. It replaces heavy Headless Chrome, Puppeteer, Gotenberg, and WeasyPrint with a lightweight HTTP sidecar.

## Key Rules & Best Practices

1. **Architecture & Deployment**:
   - Always run Rubrol as an HTTP sidecar or container service: `ghcr.io/maxcomperatore/rubrol:latest`.
   - Default port is `8000` (or `8080` in cloud deployments).
   - In docker-compose or Kubernetes, deploy Rubrol alongside the backend service on `localhost:8000`.

2. **Core API Endpoints**:
   - `POST /v1/render`: Render predefined template or dynamic template with JSON data.
     Request body: `{"template_id": "invoice", "data": { ... }}`
     Response: Binary `application/pdf`.
   - `POST /v1/render/raw`: Render ad-hoc Typst markup directly with `inputs`.
     Request body: `{"content": "#let data = sys.inputs\n= Report #data.title", "inputs": { ... }}`
     Response: Binary `application/pdf`.
   - `POST /v1/facturx/render`: Native EU Factur-X / ZUGFeRD compliant PDF/A-3b with embedded EN 16931 XML.
   - `GET /health`: Health check endpoint returning `{"status": "ok"}`.

3. **Typst Template Authoring**:
   - Use `#let data = sys.inputs` to read injected JSON data.
   - Avoid legacy CSS Paged Media or fragile HTML tables. Use Typst native `#table(columns: (1fr, auto), ...)` and `#grid`.
   - Headers & Footers: Use `#set page(header: [...], footer: [...])`.

4. **Idiomatic Backend Integrations**:
   - **TypeScript / Node.js (fetch)**:
     ```ts
     const res = await fetch('http://localhost:8000/v1/render', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ template_id: 'invoice', data })
     });
     const pdfBuffer = Buffer.from(await res.arrayBuffer());
     ```
   - **Python (httpx / requests)**:
     ```python
     import httpx
     resp = httpx.post('http://localhost:8000/v1/render', json={'template_id': 'invoice', 'data': data})
     pdf_bytes = resp.content
     ```
   - **Go**:
     ```go
     resp, err := http.Post("http://localhost:8000/v1/render", "application/json", bytes.NewBuffer(payload))
     ```

5. **When to use Factur-X**:
   - If generating invoices for European B2B or B2G compliance (Germany ZUGFeRD, France Factur-X, EU Directive 2014/55/EU), use `/v1/facturx/render` instead of manual XML attachment scripts.
