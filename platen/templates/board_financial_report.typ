// Platen Template Vault: Board Financial Report & Executive Update
#let raw_data = sys.inputs.at("data", default: "{}")
#let data = if type(raw_data) == str { json(bytes(raw_data)) } else { raw_data }

#let company_name = data.at("company_name", default: "Bipluk Autonomous Systems Inc.")
#let reporting_period = data.at("reporting_period", default: "Q3 2026 Executive Financial Update")
#let report_date = data.at("report_date", default: "September 15, 2026")
#let security_class = data.at("security_class", default: "STRICTLY CONFIDENTIAL // BOARD OF DIRECTORS ONLY")

#let kpis = data.at("kpis", default: (
  (label: "ARR", value: "\$8.42M", delta: "+142% YoY", status: "positive"),
  (label: "NET RETENTION", value: "138%", delta: "+400 bps", status: "positive"),
  (label: "GROSS MARGIN", value: "86.2%", delta: "+310 bps", status: "positive"),
  (label: "CASH RUNWAY", value: "29 Mo", delta: "\$14.2M Cash", status: "neutral"),
  (label: "BURN MULTIPLE", value: "0.62x", delta: "Best-in-class", status: "positive"),
  (label: "RULE OF 40", value: "68%", delta: "Top decile", status: "positive")
))

#let financial_rows = data.at("financial_rows", default: (
  (category: "Recurring SaaS Revenue", q1: "\$1,620K", q2: "\$1,940K", q3: "\$2,310K", yoy: "+142%"),
  (category: "Cost of Goods Sold (Compute / Infra)", q1: "(\$230K)", q2: "(\$270K)", q3: "(\$318K)", yoy: "+38%"),
  (category: "Gross Profit", q1: "\$1,390K", q2: "\$1,670K", q3: "\$1,992K", yoy: "+143%"),
  (category: "Research & Engineering", q1: "(\$620K)", q2: "(\$690K)", q3: "(\$780K)", yoy: "+25%"),
  (category: "Sales & Enterprise Growth", q1: "(\$380K)", q2: "(\$420K)", q3: "(\$490K)", yoy: "+29%"),
  (category: "General & Administrative", q1: "(\$160K)", q2: "(\$180K)", q3: "(\$195K)", yoy: "+22%"),
  (category: "Operating Net Cash Flow", q1: "\$230K", q2: "\$380K", q3: "\$527K", yoy: "+129%")
))

#let commentary = data.at("commentary", default: (
  "Platen core engine deployment expanded into 14 Fortune 500 pipelines without increasing cloud node footprint.",
  "Sub-8ms latency benchmark established as primary competitive moat versus legacy headless Chromium infrastructure.",
  "Net expansion driven by high-volume automated document generation in healthcare, finance, and logistics tiers."
))

#set page(
  paper: "a4",
  margin: (x: 2.2cm, top: 2.2cm, bottom: 2.2cm),
  footer: [
    #set text(size: 8pt, fill: rgb("#71717a"))
    #line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
    #v(2mm)
    #grid(
      columns: (1fr, 1fr),
      align(left)[#company_name | #security_class],
      context align(right)[Page #counter(page).display("1 of 1", both: true)]
    )
  ]
)

#set text(font: ("Helvetica", "Arial"), size: 9pt, fill: rgb("#0f172a"))

#grid(
  columns: (2fr, 1fr),
  [
    #text(size: 8pt, font: ("JetBrains Mono", "Courier"), weight: "bold", fill: rgb("#dc2626"))[#security_class]\
    #v(1mm)
    #text(size: 16pt, weight: "bold", fill: rgb("#0f172a"))[#company_name]\
    #text(size: 11pt, fill: rgb("#475569"))[#reporting_period]
  ],
  align(right)[
    #rect(fill: rgb("#f8fafc"), stroke: 0.5pt + rgb("#e2e8f0"), radius: 4pt, inset: 8pt)[
      #text(size: 8pt, fill: rgb("#64748b"))[DATE AS OF]\
      #text(weight: "bold", size: 9.5pt, fill: rgb("#0f172a"))[#report_date]\
      #v(1mm)
      #text(size: 7.5pt, font: ("JetBrains Mono", "Courier"), fill: rgb("#16a34a"))[AUDIT COMPLETED]
    ]
  ]
)

#v(6mm)

#text(size: 9pt, weight: "bold", fill: rgb("#475569"))[EXECUTIVE KEY PERFORMANCE METRICS]
#v(2mm)

#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 3mm,
  ..kpis.map(k => (
    rect(
      width: 100%,
      fill: rgb("#f8fafc"),
      stroke: 0.5pt + rgb("#e2e8f0"),
      radius: 4pt,
      inset: 8pt,
      [
        #text(size: 7.5pt, font: ("JetBrains Mono", "Courier"), fill: rgb("#64748b"))[#k.label]\
        #v(1mm)
        #text(size: 15pt, weight: "bold", fill: rgb("#0f172a"))[#k.value]\
        #v(0.5mm)
        #text(size: 8pt, weight: "medium", fill: if k.status == "positive" { rgb("#15803d") } else { rgb("#64748b") })[#k.delta]
      ]
    )
  ))
)

#v(6mm)

#text(size: 9pt, weight: "bold", fill: rgb("#475569"))[CONDENSED CONSOLIDATED FINANCIAL PERFORMANCE]
#v(2mm)

#table(
  columns: (3fr, 1fr, 1fr, 1fr, 1fr),
  stroke: none,
  fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else if calc.odd(row) { rgb("#fafafa") } else { none },
  align: (col, row) => (if col == 0 { left } else { right }),
  inset: (x: 8pt, y: 7pt),
  table.header([*Financial Metric*], [*Q1 2026*], [*Q2 2026*], [*Q3 2026*], [*YoY Growth*]),
  ..financial_rows.map(r => (
    [#text(weight: if r.category.starts-with("Gross") or r.category.starts-with("Operating") { "bold" } else { "regular" })[#r.category]],
    [#r.q1],
    [#r.q2],
    [#text(weight: "bold")[#r.q3]],
    [#text(fill: if r.yoy.starts-with("+") { rgb("#15803d") } else { rgb("#64748b") })[#r.yoy]]
  )).flatten()
)

#v(6mm)

#text(size: 9pt, weight: "bold", fill: rgb("#475569"))[EXECUTIVE STRATEGY & COMMENTARY]
#v(2mm)

#rect(
  width: 100%,
  fill: rgb("#f8fafc"),
  stroke: 0.5pt + rgb("#e2e8f0"),
  radius: 4pt,
  inset: 10pt,
  [
    #list(
      ..commentary.map(c => [#text(size: 8.5pt, fill: rgb("#334155"))[#c]])
    )
  ]
)
