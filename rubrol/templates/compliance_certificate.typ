// Rubrol Template Vault: SOC 2 & Security Compliance Certificate
#let raw_data = sys.inputs.at("data", default: "{}")
#let data = if type(raw_data) == str { json(bytes(raw_data)) } else { raw_data }

#let recipient = data.at("recipient", default: "CloudScale Infrastructure Corp.")
#let standard_name = data.at("standard_name", default: "SOC 2 Type II Compliance & Security Standard")
#let certificate_id = data.at("certificate_id", default: "CERT-2026-9812-SOC")
#let issue_date = data.at("issue_date", default: "September 15, 2026")
#let valid_until = data.at("valid_until", default: "September 14, 2027")
#let audit_firm = data.at("audit_firm", default: "Apex Global Assurance LLP")
#let verification_hash = data.at("verification_hash", default: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

#set page(
  paper: "a4",
  flipped: true,
  margin: (x: 2.5cm, y: 2cm),
  fill: rgb("#fcfdfd")
)

#set text(font: ("Georgia", "Times New Roman", "Liberation Serif"), size: 11pt, fill: rgb("#1e293b"))

#place(top + left, dx: -1.5cm, dy: -1cm)[
  #rect(width: 28.7cm, height: 20cm, stroke: 2pt + rgb("#0f172a"), radius: 0pt)[
    #place(center + horizon)[
      #rect(width: 28.1cm, height: 19.4cm, stroke: 0.75pt + rgb("#94a3b8"))[]
    ]
  ]
]

#v(1cm)
#align(center)[
  #text(size: 11pt, font: ("Helvetica", "Arial"), tracking: 4pt, weight: "bold", fill: rgb("#64748b"))[CERTIFICATE OF ATTESTATION]
  #v(2mm)
  #text(size: 26pt, weight: "bold", fill: rgb("#0f172a"))[#standard_name]
  #v(4mm)
  #text(size: 11pt, style: "italic", fill: rgb("#475569"))[This document officially certifies that]
  #v(4mm)
  #text(size: 22pt, weight: "bold", fill: rgb("#1d4ed8"))[#recipient]
  #v(4mm)
  #block(width: 75%)[
    #text(size: 10.5pt, fill: rgb("#334155"))[
      has successfully undergone rigorous independent third-party examination and verified full conformity with established security, availability, confidentiality, and data integrity controls in accordance with international attestation standards.
    ]
  ]
]

#v(1.2cm)

#grid(
  columns: (1fr, 1.2fr, 1fr),
  align: (center, center, center),
  [
    #line(length: 5.5cm, stroke: 0.5pt + rgb("#64748b"))
    #v(1mm)
    #text(font: ("Helvetica", "Arial"), size: 9pt, weight: "bold", fill: rgb("#0f172a"))[#audit_firm]\
    #text(font: ("Helvetica", "Arial"), size: 7.5pt, fill: rgb("#64748b"))[Authorized Lead Auditor]
  ],
  [
    #rect(
      width: 3.2cm,
      height: 3.2cm,
      stroke: 1.5pt + rgb("#d97706"),
      fill: rgb("#fffbeb"),
      radius: 50%
    )[
      #align(center + horizon)[
        #text(font: ("Helvetica", "Arial"), size: 7.5pt, weight: "black", fill: rgb("#92400e"))[
          VERIFIED\
          SECURITY\
          ★ 2026 ★
        ]
      ]
    ]
  ],
  [
    #line(length: 5.5cm, stroke: 0.5pt + rgb("#64748b"))
    #v(1mm)
    #text(font: ("Helvetica", "Arial"), size: 9pt, weight: "bold", fill: rgb("#0f172a"))[#issue_date]\
    #text(font: ("Helvetica", "Arial"), size: 7.5pt, fill: rgb("#64748b"))[Valid Through: #valid_until]
  ]
)

#v(6mm)
#align(center)[
  #text(font: ("Courier New", "Courier"), size: 7pt, fill: rgb("#94a3b8"))[
    Certificate ID: #certificate_id | SHA-256 Digest: #verification_hash
  ]
]
