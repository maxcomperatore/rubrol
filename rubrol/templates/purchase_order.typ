// Rubrol Template Vault: Enterprise Purchase Order
#let raw_data = sys.inputs.at("data", default: "{}")
#let data = if type(raw_data) == str { json(bytes(raw_data)) } else { raw_data }

#let po_number = data.at("po_number", default: "PO-2026-4401")
#let po_date = data.at("po_date", default: "2026-09-15")
#let payment_terms = data.at("payment_terms", default: "Net 45 Days")
#let shipping_terms = data.at("shipping_terms", default: "FOB Destination")

#let buyer = data.at("buyer", default: (
  company: "Apex Global Defense Systems",
  address: "100 Aerospace Blvd, Building 4",
  city: "El Segundo, CA 90245",
  contact: "Procurement Dept <purchasing@apexdefense.com>"
))

#let vendor = data.at("vendor", default: (
  company: "Rubrol Technologies Inc.",
  address: "548 Market Street, Suite 300",
  city: "San Francisco, CA 94104",
  contact: "enterprise@rubrol.io"
))

#let items = data.at("items", default: (
  (line: 1, item_code: "PLT-ECR-AIRGAP", description: "Rubrol Enterprise Air-Gapped ECR License (Perpetual)", qty: 2, unit_cost: 4800.00),
  (line: 2, item_code: "PLT-ENG-SLA", description: "24/7 Dedicated Architecture SLA & Mission Support", qty: 1, unit_cost: 2400.00)
))

#let subtotal = items.fold(0.0, (sum, i) => sum + (i.qty * i.unit_cost))
#let tax = data.at("tax", default: 0.00)
#let total = subtotal + tax

#set page(
  paper: "a4",
  margin: (x: 2.5cm, top: 2.5cm, bottom: 2.5cm),
  footer: [
    #set text(size: 8pt, fill: rgb("#71717a"))
    #line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
    #v(2mm)
    #grid(
      columns: (1fr, 1fr),
      align(left)[Purchase Order #po_number | Authorized Procurement Document],
      context align(right)[Page #counter(page).display("1 of 1", both: true)]
    )
  ]
)

#set text(font: ("Helvetica", "Arial"), size: 9pt, fill: rgb("#0f172a"))

#grid(
  columns: (1.5fr, 1fr),
  [
    #text(size: 16pt, weight: "bold", fill: rgb("#0f172a"))[PURCHASE ORDER]
    #v(1mm)
    #text(size: 9pt, fill: rgb("#64748b"))[
      *Buyer:* #buyer.company\
      #buyer.address, #buyer.city
    ]
  ],
  align(right)[
    #rect(fill: rgb("#f1f5f9"), stroke: 0.5pt + rgb("#cbd5e1"), radius: 4pt, inset: 8pt)[
      #text(size: 8pt, font: ("JetBrains Mono", "Courier"), fill: rgb("#475569"))[P.O. NUMBER]\
      #text(weight: "bold", size: 12pt, fill: rgb("#0f172a"))[#po_number]\
      #v(1mm)
      #text(size: 8pt, fill: rgb("#64748b"))[Date: #po_date]\
      #text(size: 8pt, fill: rgb("#64748b"))[Terms: #payment_terms]
    ]
  ]
)

#v(6mm)

#grid(
  columns: (1fr, 1fr),
  gutter: 8mm,
  rect(width: 100%, fill: rgb("#f8fafc"), stroke: 0.5pt + rgb("#e2e8f0"), radius: 4pt, inset: 10pt)[
    #text(size: 8pt, weight: "bold", fill: rgb("#64748b"))[VENDOR]\
    #v(1mm)
    #text(weight: "bold", fill: rgb("#0f172a"))[#vendor.company]\
    #text(size: 8.5pt, fill: rgb("#475569"))[#vendor.address, #vendor.city]\
    #text(size: 8.5pt, fill: rgb("#475569"))[#vendor.contact]
  ],
  rect(width: 100%, fill: rgb("#f8fafc"), stroke: 0.5pt + rgb("#e2e8f0"), radius: 4pt, inset: 10pt)[
    #text(size: 8pt, weight: "bold", fill: rgb("#64748b"))[SHIP TO]\
    #v(1mm)
    #text(weight: "bold", fill: rgb("#0f172a"))[#buyer.company]\
    #text(size: 8.5pt, fill: rgb("#475569"))[#buyer.address, #buyer.city]\
    #text(size: 8.5pt, fill: rgb("#475569"))[#buyer.contact]
  ]
)

#v(6mm)

#table(
  columns: (0.5fr, 1.5fr, 3fr, 0.8fr, 1.2fr, 1.2fr),
  stroke: none,
  fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else if calc.odd(row) { rgb("#fafafa") } else { none },
  align: (col, row) => (if col <= 2 { left } else if col == 3 { center } else { right }),
  inset: (x: 8pt, y: 7pt),
  table.header([*\#*], [*Item Code*], [*Description*], [*Qty*], [*Unit Price*], [*Total*]),
  ..items.map(i => (
    [#str(i.line)],
    [#text(font: ("JetBrains Mono", "Courier"), size: 8pt)[#i.item_code]],
    [#i.description],
    [#str(i.qty)],
    [\$#str(i.unit_cost)],
    [\$#str(i.qty * i.unit_cost)]
  )).flatten()
)

#line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))

#v(4mm)
#align(right)[
  #block(width: 45%)[
    #grid(
      columns: (1fr, 1fr),
      gutter: 2.5mm,
      align(left)[#text(fill: rgb("#64748b"))[Subtotal:]],
      align(right)[\$#str(subtotal)],
      align(left)[#text(fill: rgb("#64748b"))[Authorized Total:]],
      align(right)[#text(size: 13pt, weight: "bold", fill: rgb("#0f172a"))[\$#str(total)]]
    )
  ]
]
