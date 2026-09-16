// Platen Invoice Template - Modern B2B SaaS / Stripe-style
#let data_raw = sys.inputs.at("data", default: "{}")
#let data = if type(data_raw) == str { json(bytes(data_raw)) } else { data_raw }

#let invoice_number = data.at("invoice_number", default: "INV-0001")
#let issued_date = data.at("issued_date", default: "2026-01-01")
#let due_date = data.at("due_date", default: issued_date)
#let company = data.at("company", default: (
  name: "Acme Cloud Inc.",
  address: "100 Market Street, Suite 400",
  city_state: "San Francisco, CA 94105",
  email: "billing@acmecloud.io"
))
#let customer = data.at("customer", default: (
  name: "Client Corp",
  tax_id: "N/A"
))
#let line_items = data.at("line_items", default: ())
#let total = data.at("total", default: 0.00)
#let status = data.at("status", default: "PAID")

#set page(
  paper: "a4",
  margin: (x: 2.5cm, top: 2.5cm, bottom: 2.5cm),
  footer: [
    #set text(size: 8pt, fill: rgb("#9ca3af"))
    #line(length: 100%, stroke: 0.5pt + rgb("#e5e7eb"))
    #v(2mm)
    #grid(
      columns: (1fr, 1fr),
      align(left)[#company.at("name", default: "") - Thank you for your business!],
      context align(right)[Page #counter(page).display("1 of 1", both: true)]
    )
  ]
)

#set text(font: ("Helvetica", "Arial", "Liberation Sans"), size: 9.5pt, fill: rgb("#111827"))

// --- Header ---
#grid(
  columns: (1fr, 1fr),
  gutter: 1cm,
  align(left)[
    #text(size: 18pt, weight: "bold", fill: rgb("#0f172a"))[#company.at("name", default: "")]
    #v(1mm)
    #text(size: 9pt, fill: rgb("#64748b"))[
      #company.at("address", default: "")\
      #company.at("city_state", default: "")\
      #company.at("email", default: "")
    ]
  ],
  align(right)[
    #rect(
      fill: if status == "PAID" { rgb("#ecfdf5") } else { rgb("#fffbeb") },
      stroke: if status == "PAID" { 1pt + rgb("#a7f3d0") } else { 1pt + rgb("#fde68a") },
      radius: 4pt,
      inset: (x: 10pt, y: 5pt)
    )[
      #text(
        size: 9pt,
        weight: "bold",
        fill: if status == "PAID" { rgb("#065f46") } else { rgb("#92400e") }
      )[#status]
    ]
    #v(2mm)
    #text(size: 16pt, weight: "bold", fill: rgb("#334155"))[INVOICE]
    #v(1mm)
    #text(size: 9pt, fill: rgb("#64748b"))[
      *Invoice \#:* #invoice_number\
      *Date Issued:* #issued_date\
      *Date Due:* #due_date
    ]
  ]
)

#v(8mm)

// --- Bill To ---
#rect(
  width: 100%,
  fill: rgb("#f8fafc"),
  stroke: 0.5pt + rgb("#e2e8f0"),
  radius: 6pt,
  inset: 12pt
)[
  #text(size: 8pt, weight: "bold", fill: rgb("#64748b"))[BILLED TO]
  #v(1.5mm)
  #text(size: 11pt, weight: "bold", fill: rgb("#0f172a"))[#customer.at("name", default: "")]
  #if "tax_id" in customer [
    #v(0.5mm)
    #text(size: 8.5pt, fill: rgb("#475569"))[Tax ID / VAT: #customer.at("tax_id")]
  ]
  #if "email" in customer [
    #v(0.5mm)
    #text(size: 8.5pt, fill: rgb("#475569"))[#customer.at("email")]
  ]
]

#v(6mm)

// --- Line Items Table ---
#table(
  columns: (3fr, 1fr, 1.2fr, 1.2fr),
  stroke: none,
  fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else if calc.odd(row) { rgb("#fafafa") } else { none },
  align: (col, row) => (
    if col == 0 { left }
    else if col == 1 { center }
    else { right }
  ),
  inset: (x: 10pt, y: 8pt),
  table.header(
    [*Description*], [*Qty*], [*Unit Price*], [*Amount*]
  ),
  ..line_items.map(item => (
    [#text(weight: "medium")[#item.at("description", default: "-")]],
    [#str(item.at("qty", default: 1))],
    [\$#str(item.at("unit_price", default: 0.00))],
    [\$#str(item.at("qty", default: 1) * item.at("unit_price", default: 0.00))]
  )).flatten()
)

#v(2mm)
#line(length: 100%, stroke: 0.5pt + rgb("#e2e8f0"))
#v(4mm)

// --- Totals Summary ---
#align(right)[
  #block(width: 45%)[
    #grid(
      columns: (1fr, 1fr),
      gutter: 3mm,
      align(left)[#text(fill: rgb("#64748b"))[Total Due:]],
      align(right)[#text(size: 14pt, weight: "bold", fill: rgb("#0f172a"))[\$#str(total)]]
    )
  ]
]

#v(10mm)
#rect(
  width: 100%,
  stroke: (left: 2pt + rgb("#3b82f6")),
  fill: rgb("#eff6ff"),
  inset: 10pt
)[
  #text(size: 8.5pt, fill: rgb("#1e40af"))[
    *Payment Terms:* Net 30 days. Payments can be settled via Wire or Credit Card.
    Please reference invoice *#invoice_number* on all remittances.
  ]
]
