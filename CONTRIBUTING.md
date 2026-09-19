# Contributing to Rubrol

Thank you for your interest in contributing to **Rubrol**! 

Rubrol is an open-core, high-throughput document engine designed to replace Headless Chrome and Puppeteer with mathematical typesetting in $< 8\text{ms}$. We believe that document generation should be deterministic, resource-efficient, and accessible across every programming language.

Whether you're writing a client library, authoring a new document template, improving Docker container performance, or optimizing sidecar concurrency, your contributions help developers eliminate compute waste worldwide.

---

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
  - [1. Community Client SDKs](#1-community-client-sdks)
  - [2. Document Templates](#2-document-templates)
  - [3. Engine & Sidecar Core](#3-engine--sidecar-core)
  - [4. Infrastructure & Deployments](#4-infrastructure--deployments)
- [Local Development Setup](#local-development-setup)
- [Testing & Verification](#testing--verification)
- [Commit & Pull Request Conventions](#commit--pull-request-conventions)
- [Community Recognition & Hall of Fame](#community-recognition--hall-of-fame)
- [Contributor Terms & License Grant](#contributor-terms--license-grant)
- [Code of Conduct](#code-of-conduct)

---

## Ways to Contribute

### 1. Community Client SDKs & Examples
We maintain ready-to-run client snippets in [`examples/`](examples/). If your language is missing or could be improved with a zero-dependency standard library implementation, submit a pull request adding:
- `examples/<language>/generate_invoice.<ext>`
- README instructions with command-line execution steps.
- An automated verification run confirming it receives a 200 OK from `http://localhost:8080/v1/render`.

### 2. Document Templates
We welcome high-quality, real-world document templates built with native Typst:
- **Criteria:** Clean typography, sensible margin defaults, multi-page page breaks (`break-inside: avoid`), and robust fallback values for missing JSON keys.
- **Data Ingestion Standard:** Must parse inputs dynamically:
  ```typst
  #let raw_data = sys.inputs.at("data", default: "{}")
  #let data = if type(raw_data) == str { json(bytes(raw_data)) } else { raw_data }
  ```
- **File Location:** Place community templates in `rubrol/templates/` accompanied by sample data fixtures in `rubrol/data/<template_name>.json`.

### 3. Engine & Sidecar Core
The core daemon lives in [`rubrol/core/`](rubrol/core/):
- **`engine.py`**: Multi-format compilation pool, template cache, and PDF/A post-processing.
- **`server.py`**: Threaded HTTP server handling telemetry headers, Factur-X packaging, and raw markup compilation.
- **Performance Guidelines:** Any change touching the compilation hot path must maintain the $< 8\text{ms}$ latency SLA and $< 28\text{MB}$ memory ceiling.

### 4. Infrastructure & Deployments
Help make Rubrol drop-in simple for modern cloud environments:
- Multi-architecture Docker builds (`linux/amd64`, `linux/arm64`).
- Distroless or Alpine-based container reductions.
- Kubernetes Helm charts and K8s sidecar manifests.
- Serverless deployment recipes (AWS Lambda container, Google Cloud Run, Fly.io).

---

## Local Development Setup

Rubrol is engineered with **zero heavy dependencies**. You do not need Node.js, databases, or Redis to develop locally.

### 1. Clone the Repository
```bash
git clone https://github.com/maxcomperatore/rubrol.git
cd rubrol
```

### 2. Create a Virtual Environment & Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install typst pypdf httpx pytest
```

### 3. Start the Development Server
```bash
python rubrol/core/server.py --port 8080
```
Open **`http://localhost:8080`** in your browser to verify the interactive studio.

### 4. Test a Local Render
```bash
python rubrol.py compile \
  --template rubrol/templates/b2b_invoice.typ \
  --data rubrol/data/b2b_invoice.json \
  --output test_invoice.pdf
```

---

## Testing & Verification

Run the automated test suite before opening any pull request:

```bash
# Run unit & compilation tests
pytest tests/

# Test sidecar endpoint latency
python -m pytest tests/test_latency.py -v
```

---

## Commit & Pull Request Conventions

We follow **Conventional Commits** to keep git history clean, informative, and automation-friendly:

| Prefix | Usage | Example |
| :--- | :--- | :--- |
| `feat:` | A new feature or client capability | `feat(sdk): add ruby client example for /v1/render` |
| `fix:` | A bug fix | `fix(engine): resolve font subsetting crash on arm64` |
| `perf:` | Performance optimization | `perf(compiler): improve cached compiler lookup by 1.2ms` |
| `docs:` | Documentation improvements | `docs: add kubernetes sidecar deployment guide` |
| `refactor:`| Code refactoring without behavioral change | `refactor(server): decouple factur-x request validation` |
| `template:`| New or updated Typst document template | `template: add international customs declaration form` |

### Pull Request Checklist
- [ ] Code follows PEP 8 for Python and idiomatic standards for other languages.
- [ ] No extraneous dependencies introduced without prior discussion.
- [ ] Tested locally against the sidecar (`POST /v1/render` returns HTTP 200 OK).
- [ ] If adding a new template, included a corresponding `.json` fixture in `rubrol/data/`.

---

## Community Recognition & Hall of Fame

Every contributor who submits an accepted pull request or publishes an ecosystem SDK will be:
- Listed in our **Contributors Hall of Fame** on GitHub and the website.
- Tagged and thanked in official release notes and changelogs.

---

## Contributor Terms & License Grant

By submitting a pull request, patch, or contribution to Rubrol:
1. **GNU LGPLv3 Inbound License**: You grant Rubrol, its maintainers, and its users an irrevocable, perpetual, worldwide, royalty-free license under the GNU Lesser General Public License v3.0 (LGPLv3).
2. **Developer Certificate of Origin (DCO 1.1)**: You certify that you authored the contribution in its entirety or otherwise have the full legal right and authority to license it under the GNU LGPLv3.

---

## Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free experience for everyone. We expect all contributors to:
- Be respectful, constructive, and collaborative in discussions, issues, and code reviews.
- Focus on what is best for the developer community and the long-term maintainability of the project.
- Respect diverse viewpoints, technical backgrounds, and experience levels.

---

<div align="center">
  <sub>Built with precision. Maintained by the community and the Rubrol Team.</sub>
</div>
