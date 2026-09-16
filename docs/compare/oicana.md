# Rubrol vs Oicana: Architecture & Licensing Comparison

A technical comparison between **Rubrol** and **Oicana** for high-throughput PDF generation.

---

## At a Glance

| Evaluation Vector | Oicana | **Rubrol Engine** |
| :--- | :--- | :--- |
| **Open-Source License** | PolyForm Noncommercial 1.0.0 *(Source-Available)* | **Apache 2.0 Open Core** *(100% Permissive)* |
| **Enterprise Scanner Risk** | Flagged by Snyk / FOSSA / Black Duck | Zero compliance flags |
| **Deployment Model** | Language FFI bindings / Custom microservice | **Universal HTTP Sidecar & CLI** |
| **Template Format** | Custom `.zip` archives (`oicana pack`) | **Plain `.typ` files in Git / volume mounts** |
| **EU e-Invoicing** | Not supported | **Turnkey EU Factur-X / ZUGFeRD 2.2 Suite** |
| **Engine Foundation** | Typst | **Typst (with warm compiler cache pooling)** |
| **Remote Dynamic Assets** | Manual blob mapping | **SSRF-guarded in-memory stream buffers** |
| **Pricing Model** | Per-app recurring fee (€19–€199/mo) | **$490/yr Vault or $990 Lifetime** |

---

## 1. Licensing & Security Compliance

* **Oicana:** Employs the `PolyForm Noncommercial` license. Corporate security scanners and procurement teams routinely block source-available software from production pipelines.
* **Rubrol:** 100% permissive **Apache 2.0**. You can embed, self-host, and deploy Rubrol without legal review or automated scanner rejections.

## 2. Packaging & Dev Experience

* **Oicana:** Requires compiling templates into proprietary zip archives using an external CLI (`oicana pack`), shipping them to an artifact store (e.g. S3), and unpacking them during container boot.
* **Rubrol:** Treats templates as standard code. Keep your `.typ` files directly in your repository or mount a directory volume into the container (`-v ./templates:/app/rubrol/templates`).

## 3. EU Factur-X / ZUGFeRD Compliance

* **Oicana:** Offers no native electronic invoice generator or PDF/A-3b XML packager.
* **Rubrol:** Ships with a complete, validated Factur-X / ZUGFeRD 2.2 suite supporting all 6 conformance profiles (`MINIMUM` to `XRECHNUNG`) with automated PDF/A-3b container generation.
