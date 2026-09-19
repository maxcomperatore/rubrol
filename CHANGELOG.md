# Changelog

All notable changes to Rubrol will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-19

### Added
- Multi-format compilation engine powered by Typst and PyPDF.
- Turnkey EU Factur-X / ZUGFeRD 2.2 compliant PDF/A-3b generator.
- Multi-page page budgeting algorithm preventing layout overflows and orphan rows.
- Dynamic JSON input parser supporting both CLI and HTTP execution modes.
- High-throughput threaded HTTP sidecar server (`POST /v1/render`, `POST /v1/compile`).
- Interactive web studio UI served directly from the engine binary.
- Built-in telemetry headers (`X-Engine`, `X-Render-Time-Ms`, `X-Memory-Alloc-MB`).
- Docker container specification with unprivileged execution.
- Comprehensive test suite covering Factur-X XML packaging, PDF/A-3 attachments, and Schematron validation.
- Standardized open-source community policies (LGPLv3 license, Contributor Covenant v2.1, Security Policy, Conventional Commits).

### Performance
- Sub-10ms mean compilation latency on standard business documents.
- 96% lower peak RSS memory footprint compared to headless Chromium sidecars.
- Zero external runtime daemons required (no Node.js, Chromium, or Redis).
