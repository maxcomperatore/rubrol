// Platen Template Vault: Stripe-Grade B2B SaaS Invoice
#let raw_data = sys.inputs.at("data", default: "{}")
#let data = if type(raw_data) == str { json(bytes(raw_data)) } else { raw_data }

#let invoice_number = data.at("invoice_number", default: "INV-2026-0001")
#let issued_date = data.at("issued_date", default: "2026-09-15")
#let due_date = data.at("due_date", default: "2026-10-15")
#let currency_symbol = data.at("currency_symbol", default: "$")
#let status = data.at("status", default: "PAID")

#let vendor = data.at("vendor", default: (
  name: "Platen Engine Inc.",
  tax_id: "US-849201948",
  address: "548 Market Street, Suite 300",
  city: "San Francisco, CA 94104",
  email: "billing@platenengine.com"
))

#let customer = data.at("customer", default: (
  name: "Acme Technologies LLC",
  tax_id: "EU-987654321",
  address: "742 Evergreen Terrace",
  city: "Springfield, OR 97477",
  email: "accounts@acme.com"
))

#let line_items = data.at("line_items", default: (
  (description: "Platen Pro Annual License (Unlimited Nodes)", qty: 1, unit_price: 490.00),
  (description: "Priority SLA & Custom Template Engineering", qty: 1, unit_price: 250.00)
))

#let subtotal = line_items.fold(0.0, (sum, item) => sum + (item.at("qty", default: 1) * item.at("unit_price", default: 0.0)))
#let tax_rate = data.at("tax_rate", default: 0.0)
#let tax_amount = subtotal * tax_rate
#let total = subtotal + tax_amount

#set page(
  paper: "a4",
  margin: (x: 2.2cm, top: 2.5cm, bottom: 2.2cm),
  footer: [
    #set text(size: 8pt, fill: rgb("#94a3b8"))
    #line(length: 100%, stroke: 0.5pt + rgb("#e2e8f0"))
    #v(2mm)
    #grid(
      columns: (1fr, 1fr),
      align(left)[#vendor.name | Tax ID: #vendor.tax_id],
      context align(right)[Page #counter(page).display("1 of 1", both: true)]
    )
  ]
)

#set text(font: ("Helvetica", "Arial", "Liberation Sans"), size: 9.5pt, fill: rgb("#1e293b"))

// Header Block
#grid(
  columns: (1fr, 1fr),
  align(left)[
    #text(size: 20pt, weight: "black", fill: rgb("#0f172a"))[#vendor.name]
    #v(1mm)
    #text(size: 9pt, fill: rgb("#64748b"))[
      #vendor.address\
      #vendor.city\
      #vendor.email
    ]
  ],
  align(right)[
    #rect(
      fill: if status == "PAID" { rgb("#f0fdf4") } else { rgb("#fffbeb") },
      stroke: 1pt + if status == "PAID" { rgb("#86efac") } else { rgb("#fde68a") },
      radius: 4pt,
      inset: (x: 10pt, y: 5pt)
    )[
      #text(weight: "bold", fill: if status == "PAID" { rgb("#15803d") } else { rgb("#b45309") })[#status]
    ]
    #v(2mm)
    #text(size: 14pt, weight: "bold", fill: rgb("#334155"))[INVOICE]
    #v(1mm)
    #text(size: 8.5pt, fill: rgb("#64748b"))[
      *Invoice \#:* #invoice_number\
      *Issued:* #issued_date\
      *Due:* #due_date
    ]
  ]
)

#v(8mm)

// Parties Grid
#grid(
  columns: (1fr, 1fr),
  gutter: 1cm,
  rect(width: 100%, fill: rgb("#f8fafc"), stroke: 0.5pt + rgb("#e2e8f0"), radius: 6pt, inset: 10pt)[
    #text(size: 7.5pt, weight: "bold", fill: rgb("#94a3b8"))[BILLED FROM]
    #v(1mm)
    #text(weight: "bold", fill: rgb("#0f172a"))[#vendor.name]\
    #text(size: 8.5pt, fill: rgb("#475569"))[Tax ID: #vendor.tax_id]
  ],
  rect(width: 100%, fill: rgb("#f8fafc"), stroke: 0.5pt + rgb("#e2e8f0"), radius: 6pt, inset: 10pt)[
    #text(size: 7.5pt, weight: "bold", fill: rgb("#94a3b8"))[BILLED TO]
    #v(1mm)
    #text(weight: "bold", fill: rgb("#0f172a"))[#customer.name]\
    #text(size: 8.5pt, fill: rgb("#475569"))[
      #customer.address, #customer.city\
      Tax ID: #customer.tax_id
    ]
  ]
)

#v(6mm)

// Line Items
#table(
  columns: (4fr, 1fr, 1.2fr, 1.2fr),
  stroke: none,
  fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else if calc.odd(row) { rgb("#fafafa") } else { none },
  align: (col, row) => (if col == 0 { left } else if col == 1 { center } else { right }),
  inset: (x: 10pt, y: 8pt),
  table.header([*Description*], [*Qty*], [*Unit Price*], [*Amount*]),
  ..line_items.map(item => (
    [#item.description],
    [#str(item.qty)],
    [#currency_symbol#str(item.unit_price)],
    [#currency_symbol#str(item.qty * item.unit_price)]
  )).flatten()
)

#v(2mm)
#line(length: 100%, stroke: 0.5pt + rgb("#e2e8f0"))
#v(3mm)

// Totals
#align(right)[
  #block(width: 48%)[
    #grid(
      columns: (1fr, 1fr),
      gutter: 2.5mm,
      align(left)[#text(fill: rgb("#64748b"))[Subtotal:]],
      align(right)[#currency_symbol#str(subtotal)],
      align(left)[#text(fill: rgb("#64748b"))[Tax (#str(tax_rate * 100)%):]],
      align(right)[#currency_symbol#str(tax_amount)],
      align(left)[#text(weight: "bold", size: 11pt, fill: rgb("#0f172a"))[Total Due:]],
      align(right)[#text(weight: "bold", size: 13pt, fill: rgb("#0f172a"))[#currency_symbol#str(total)]]
    )
  ]
]

#v(8mm)
#rect(width: 100%, stroke: (left: 3pt + rgb("#2563eb")), fill: rgb("#eff6ff"), inset: 10pt)[
  #text(size: 8.5pt, fill: rgb("#1e40af"))[
    *Payment Instructions:* Settlement accepted via Wire Transfer, ACH, or Corporate Credit Card.\
    Reference invoice *#invoice_number* on all remittances. Remit inquiries to #vendor.email.
  ]
]
