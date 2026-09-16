// Rubrol Template Vault: SaaS Subscription Receipt
#let raw_data = sys.inputs.at("data", default: "{}")
#let data = if type(raw_data) == str { json(bytes(raw_data)) } else { raw_data }

#let receipt_id = data.at("receipt_id", default: "REC-849204")
#let charge_date = data.at("charge_date", default: "September 15, 2026")
#let amount = data.at("amount", default: 49.00)
#let currency = data.at("currency", default: "USD")
#let payment_method = data.at("payment_method", default: "Mastercard ending in 4022")
#let plan_name = data.at("plan_name", default: "Rubrol Pro Annual Plan")
#let billing_period = data.at("billing_period", default: "Sep 15, 2026 - Sep 15, 2027")

#let company = data.at("company", default: (
  name: "Rubrol Engine Inc.",
  address: "548 Market Street, Suite 300, San Francisco, CA",
  support_email: "billing@rubrol.io"
))

#let customer = data.at("customer", default: (
  name: "Sarah Jenkins",
  email: "sarah.jenkins@acme.dev",
  account_id: "usr_9918204"
))

#set page(
  paper: "a4",
  margin: (x: 3.5cm, top: 3.5cm, bottom: 3cm),
  footer: [
    #set text(size: 8pt, fill: rgb("#71717a"))
    #line(length: 100%, stroke: 0.5pt + rgb("#27272a"))
    #v(2mm)
    #grid(
      columns: (1fr, 1fr),
      align(left)[#company.name | Questions? Contact #company.support_email],
      align(right)[Receipt #receipt_id]
    )
  ]
)

#set text(font: ("Helvetica", "Arial"), size: 10pt, fill: rgb("#f4f4f6"))

#grid(
  columns: (1fr, 1fr),
  [
    #text(size: 16pt, weight: "bold", fill: rgb("#ffffff"))[#company.name]
    #v(1mm)
    #text(size: 9pt, fill: rgb("#a1a1aa"))[#company.address]
  ],
  align(right)[
    #text(size: 10pt, weight: "bold", font: ("JetBrains Mono", "Courier"), fill: rgb("#93c5fd"))[RECEIPT]
    #v(1mm)
    #text(size: 8.5pt, fill: rgb("#71717a"))[#charge_date]
  ]
)

#v(1cm)

#rect(width: 100%, fill: rgb("#111114"), stroke: 0.5pt + rgb("#27272a"), radius: 6pt, inset: 16pt)[
  #grid(
    columns: (1fr, 1fr),
    [
      #text(size: 8pt, font: ("JetBrains Mono", "Courier"), fill: rgb("#71717a"))[BILLED TO]
      #v(2mm)
      #text(weight: "bold", size: 11pt, fill: rgb("#ffffff"))[#customer.name] \
      #text(size: 9pt, fill: rgb("#a1a1aa"))[#customer.email] \
      #text(size: 8.5pt, fill: rgb("#71717a"))[Account ID: #customer.account_id]
    ],
    align(right)[
      #text(size: 8pt, font: ("JetBrains Mono", "Courier"), fill: rgb("#71717a"))[PAYMENT APPLIED]
      #v(2mm)
      #text(size: 22pt, weight: "bold", fill: rgb("#ffffff"))[\$#str(amount)] \
      #text(size: 8.5pt, fill: rgb("#86efac"))[Paid via #payment_method]
    ]
  )
]

#v(8mm)

#table(
  columns: (3fr, 2fr, 1fr),
  stroke: none,
  fill: (col, row) => if row == 0 { rgb("#16161a") } else { none },
  align: (col, row) => (if col == 0 { left } else if col == 1 { left } else { right }),
  inset: (x: 12pt, y: 10pt),
  table.header([*Description*], [*Period*], [*Amount*]),
  [#text(weight: "medium")[#plan_name]], [#text(size: 9pt, fill: rgb("#a1a1aa"))[#billing_period]], [\$#str(amount)]
)

#line(length: 100%, stroke: 0.5pt + rgb("#27272a"))

#v(4mm)
#align(right)[
  #block(width: 40%)[
    #grid(
      columns: (1fr, 1fr),
      gutter: 3mm,
      align(left)[#text(fill: rgb("#a1a1aa"))[Total Paid:]],
      align(right)[#text(weight: "bold", size: 12pt, fill: rgb("#ffffff"))[\$#str(amount) #currency]]
    )
  ]
]
