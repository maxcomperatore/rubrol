// Rubrol Template Vault: Warehouse Logistics Packing Slip
#let raw_data = sys.inputs.at("data", default: "{}")
#let data = if type(raw_data) == str { json(bytes(raw_data)) } else { raw_data }

#let order_number = data.at("order_number", default: "ORD-94821")
#let ship_date = data.at("ship_date", default: "2026-09-15")
#let tracking_number = data.at("tracking_number", default: "1Z9999999999999999")
#let carrier = data.at("carrier", default: "UPS Ground")

#let warehouse = data.at("warehouse", default: (
  name: "Rubrol Logistics Hub West",
  location: "Dock 4B - Reno Distribution Center"
))

#let recipient = data.at("recipient", default: (
  name: "Marcus Vance",
  company: "Apex Hardware Systems",
  address: "1200 Industrial Parkway, Suite 8",
  city: "Austin, TX 78758"
))

#let packages = data.at("packages", default: (
  (sku: "PLT-SRV-1U", description: "Rubrol 1U Rack Engine Appliance", qty: 2, weight: "14.2 lbs"),
  (sku: "CBL-OPT-10M", description: "10-Meter OM4 Fiber Patch Cable", qty: 4, weight: "1.1 lbs"),
  (sku: "SFP-PLUS-10G", description: "10G SFP+ Optical Transceiver Pair", qty: 2, weight: "0.4 lbs")
))

#set page(
  paper: "a4",
  margin: (x: 2.5cm, top: 2.5cm, bottom: 2.5cm),
  footer: [
    #set text(size: 8pt, fill: rgb("#71717a"))
    #line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
    #v(2mm)
    #grid(
      columns: (1fr, 1fr),
      align(left)[Order #order_number | Carrier: #carrier],
      context align(right)[Page #counter(page).display("1 of 1", both: true)]
    )
  ]
)

#set text(font: ("Helvetica", "Arial"), size: 9.5pt, fill: rgb("#0f172a"))

#grid(
  columns: (1.5fr, 1fr),
  [
    #text(size: 16pt, weight: "bold", fill: rgb("#0f172a"))[PACKING SLIP]
    #v(1mm)
    #text(size: 9pt, fill: rgb("#64748b"))[
      *Facility:* #warehouse.name\
      *Location:* #warehouse.location
    ]
  ],
  align(right)[
    #rect(width: 100%, fill: rgb("#f1f5f9"), stroke: 0.5pt + rgb("#cbd5e1"), radius: 4pt, inset: 8pt)[
      #text(size: 8pt, font: ("JetBrains Mono", "Courier"), fill: rgb("#475569"))[ORDER NUMBER]\
      #text(weight: "bold", size: 12pt, fill: rgb("#0f172a"))[#order_number]\
      #v(1mm)
      #text(size: 8pt, fill: rgb("#64748b"))[Ship Date: #ship_date]\
      #text(size: 8pt, fill: rgb("#64748b"))[Tracking: #tracking_number]
    ]
  ]
)

#v(8mm)

#rect(width: 100%, fill: rgb("#f8fafc"), stroke: 0.5pt + rgb("#e2e8f0"), radius: 6pt, inset: 12pt)[
  #text(size: 8pt, weight: "bold", fill: rgb("#64748b"))[DELIVER TO]
  #v(1mm)
  #text(weight: "bold", size: 11pt, fill: rgb("#0f172a"))[#recipient.name]\
  #text(size: 9.5pt, fill: rgb("#334155"))[#recipient.company]\
  #text(size: 9.5pt, fill: rgb("#475569"))[#recipient.address, #recipient.city]
]

#v(6mm)

#table(
  columns: (1.5fr, 3fr, 1fr, 1fr),
  stroke: none,
  fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else if calc.odd(row) { rgb("#fafafa") } else { none },
  align: (col, row) => (if col == 0 { left } else if col == 1 { left } else { center }),
  inset: (x: 10pt, y: 8pt),
  table.header([*SKU*], [*Item Description*], [*Qty*], [*Weight*]),
  ..packages.map(p => (
    [#text(font: ("JetBrains Mono", "Courier"), size: 8.5pt)[#p.sku]],
    [#p.description],
    [#str(p.qty)],
    [#p.weight]
  )).flatten()
)

#line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))

#v(8mm)
#rect(width: 100%, stroke: 0.5pt + rgb("#cbd5e1"), inset: 10pt)[
  #text(size: 8.5pt, fill: rgb("#475569"))[
    *Inspection Verification:* All listed items inspected and packed in accordance with ISO 9001 QA protocols. 
    Report damaged or missing parcels within 48 hours of carrier delivery timestamp.
  ]
]
