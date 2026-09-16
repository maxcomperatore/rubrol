// Rubrol Template Vault: Employee Payroll Earnings Statement
#let raw_data = sys.inputs.at("data", default: "{}")
#let data = if type(raw_data) == str { json(bytes(raw_data)) } else { raw_data }

#let pay_period = data.at("pay_period", default: "Sep 01, 2026 - Sep 15, 2026")
#let pay_date = data.at("pay_date", default: "September 15, 2026")

#let employer = data.at("employer", default: (
  name: "Rubrol Engine Inc.",
  ein: "94-8291044",
  address: "548 Market Street, Suite 300, San Francisco, CA 94104"
))

#let employee = data.at("employee", default: (
  name: "David Kim",
  id: "EMP-4081",
  ssn_last4: "9821",
  department: "Compiler Infrastructure"
))

#let gross_pay = data.at("gross_pay", default: 6250.00)
#let fed_tax = data.at("fed_tax", default: 940.00)
#let state_tax = data.at("state_tax", default: 420.00)
#let social_security = data.at("social_security", default: 387.50)
#let medicare = data.at("medicare", default: 90.63)
#let health_insurance = data.at("health_insurance", default: 180.00)
#let deductions_total = fed_tax + state_tax + social_security + medicare + health_insurance
#let net_pay = gross_pay - deductions_total

#set page(
  paper: "a4",
  margin: (x: 2.5cm, top: 2.5cm, bottom: 2.5cm),
  footer: [
    #set text(size: 8pt, fill: rgb("#71717a"))
    #line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
    #v(2mm)
    #grid(
      columns: (1fr, 1fr),
      align(left)[#employer.name | CONFIDENTIAL PAYROLL RECORD],
      align(right)[Employee ID: #employee.id]
    )
  ]
)

#set text(font: ("Helvetica", "Arial"), size: 9pt, fill: rgb("#0f172a"))

#grid(
  columns: (1.5fr, 1fr),
  [
    #text(size: 15pt, weight: "bold", fill: rgb("#0f172a"))[#employer.name] \
    #text(size: 8.5pt, fill: rgb("#64748b"))[#employer.address | EIN: #employer.ein]
  ],
  align(right)[
    #text(size: 13pt, weight: "bold", fill: rgb("#0284c7"))[EARNINGS STATEMENT] \
    #text(size: 8.5pt, fill: rgb("#64748b"))[Pay Date: #pay_date] \
    #text(size: 8.5pt, fill: rgb("#64748b"))[Period: #pay_period]
  ]
)

#v(6mm)

#rect(width: 100%, fill: rgb("#f8fafc"), stroke: 0.5pt + rgb("#e2e8f0"), radius: 4pt, inset: 10pt)[
  #grid(
    columns: (1.5fr, 1fr, 1.2fr),
    [*Employee:* #employee.name],
    [*SSN:* XXX-XX-#employee.ssn_last4],
    [*Department:* #employee.department]
  )
]

#v(6mm)

#grid(
  columns: (1fr, 1fr),
  gutter: 8mm,
  [
    #text(weight: "bold", size: 10pt, fill: rgb("#0f172a"))[Earnings Breakdown]
    #v(2mm)
    #table(
      columns: (2fr, 1fr),
      stroke: none,
      fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else { none },
      inset: (x: 8pt, y: 6pt),
      table.header([*Description*], [*Amount*]),
      [Base Salary], [\$#str(gross_pay)],
      [Total Gross], [\$#str(gross_pay)]
    )
  ],
  [
    #text(weight: "bold", size: 10pt, fill: rgb("#0f172a"))[Statutory & Voluntary Deductions]
    #v(2mm)
    #table(
      columns: (2fr, 1fr),
      stroke: none,
      fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else { none },
      inset: (x: 8pt, y: 6pt),
      table.header([*Tax / Deduction*], [*Amount*]),
      [Federal Withholding], [\$#str(fed_tax)],
      [State Withholding], [\$#str(state_tax)],
      [Social Security (FICA)], [\$#str(social_security)],
      [Medicare], [\$#str(medicare)],
      [Pre-Tax Medical (401k/Health)], [\$#str(health_insurance)],
      [*Total Deductions*], [#strong[\$#str(deductions_total)]]
    )
  ]
)

#v(6mm)
#rect(width: 100%, fill: rgb("#f0fdf4"), stroke: 1pt + rgb("#86efac"), radius: 4pt, inset: 12pt)[
  #grid(
    columns: (1fr, 1fr),
    [
      #text(weight: "bold", size: 11pt, fill: rgb("#15803d"))[NET DIRECT DEPOSIT] \
      #text(size: 8.5pt, fill: rgb("#475569"))[Settled to Bank Account on Record]
    ],
    align(right)[
      #text(size: 18pt, weight: "bold", fill: rgb("#15803d"))[\$#str(net_pay)]
    ]
  )
]

