# Security Policy

Rubrol takes the security of our document generation engine and sidecar infrastructure seriously. We appreciate the responsible disclosure of any vulnerabilities discovered by researchers, operators, and community contributors.

## Supported Versions

Only the latest active minor release receives active security patches and hotfixes.

| Version | Supported          | Security Maintenance |
| :------ | :----------------- | :------------------- |
| 1.0.x   | :white_check_mark: | Active (Current GA)  |
| < 1.0.0 | :x:                | End of Life (EOL)    |

## Reporting a Vulnerability

Please do not disclose security vulnerabilities publicly through GitHub Issues, Discussions, or public social channels.

To report a vulnerability:

1. **GitHub Private Vulnerability Reporting (Recommended):**
   Navigate to the [Security Advisories](https://github.com/maxcomperatore/rubrol/security/advisories) tab and click **"Report a vulnerability"** to open a confidential report.
2. **Email Security Team:**
   Send an encrypted or plain report to **security@rubrol.com** with the subject line `[SECURITY] Vulnerability Report: <Brief Description>`.

### Information to Include

To help us triage and reproduce the issue quickly, please include:
- A description of the vulnerability and its potential attack vector.
- Minimal reproducible sample code, request payload, or `.typ` template.
- Exact environment details (Rubrol version, deployment model, operating system).
- Any proposed remediation or patch if available.

## Response Commitments

- **Initial Acknowledgement**: Within 24 hours of receiving the report.
- **Triage & Severity Assessment**: Within 72 hours.
- **Patch & Release**: Priority hotfix released via official channels and Docker Hub tags.
- **Public Disclosure**: Coordinated disclosure after affected users have had reasonable time to upgrade.

## Security Best Practices for Operators

When deploying Rubrol in production environments:
- Run the sidecar container with a non-root user (`USER nonroot`).
- Set explicit memory limits (`--memory=128m`) and CPU quotas in container orchestrators.
- Never mount untrusted host filesystem paths directly into template search directories.
- Utilize TLS termination in front of the HTTP sidecar (`POST /v1/render`) in public network environments.
