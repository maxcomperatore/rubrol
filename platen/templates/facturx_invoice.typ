// Platen Enterprise Template Vault: EU Factur-X / ZUGFeRD B2B Invoice
// Compliant with European Standard EN 16931 & Factur-X 1.0.07 (ZUGFeRD 2.2)

#let raw_data = sys.inputs.at("data", default: "{}")
#let data = if type(raw_data) == str { json(bytes(raw_data)) } else { raw_data }

#let invoice_number = data.at("invoice_number", default: "INV-2026-0042")
#let issued_date = data.at("issued_date", default: data.at("issue_date", default: "2026-09-15"))
#let due_date = data.at("due_date", default: "2026-10-15")
#let currency_symbol = data.at("currency_symbol", default: "€")
#let currency_code = data.at("currency", default: "EUR")
#let status = data.at("status", default: "PAID")
#let reverse_charge = data.at("reverse_charge", default: false)

#let vendor = data.at("vendor", default: (
  name: "Platen Engine Europe SAS",
  siret: "982 391 820 00014",
  vat_id: "FR82982391820",
  address: "10 Rue de la Paix",
  city: "75002 Paris",
  country: "France",
  email: "billing@platenengine.com"
))

#let customer = data.at("customer", default: (
  name: "Acme European Cloud GmbH",
  siret: "HRB 192847",
  vat_id: "DE391048291",
  address: "Friedrichstraße 42",
  city: "10117 Berlin",
  country: "Germany",
  email: "accounts.payable@acme-cloud.de"
))

#let payment = data.at("payment", default: (
  bank_name: "BNP Paribas Commercial",
  iban: "FR76 3000 6000 0112 3456 7890 189",
  bic: "BNPAFRPPXXX",
  reference: invoice_number
))

#let line_items = data.at("line_items", default: (
  (name: "Platen Enterprise Engine - Annual Cluster License", description: "Sub-8ms dynamic Typst sidecar with unlimited nodes & font cache reuse", qty: 1, unit_price: 2400.00, tax_rate: 0.20),
  (name: "Factur-X / ZUGFeRD 2.2 Turnkey Compliance Suite", description: "Automated EN 16931 XML embedding with PDF/A-3b container generation", qty: 1, unit_price: 490.00, tax_rate: 0.20)
))

// Compute totals and tax buckets
#let subtotal = line_items.fold(0.0, (sum, item) => sum + (item.at("qty", default: 1) * item.at("unit_price", default: 0.0)))
#let total_tax = line_items.fold(0.0, (sum, item) => {
  let item_tax_rate = item.at("tax_rate", default: data.at("tax_rate", default: 0.0))
  let rate = if item_tax_rate > 1.0 { item_tax_rate / 100.0 } else { item_tax_rate }
  sum + (item.at("qty", default: 1) * item.at("unit_price", default: 0.0) * rate)
})
#let grand_total = subtotal + total_tax

#set page(
  paper: "a4",
  margin: (x: 2cm, top: 2.2cm, bottom: 2.5cm),
  footer: [
    #set text(size: 7.5pt, fill: rgb("#94a3b8"))
    #line(length: 100%, stroke: 0.5pt + rgb("#e2e8f0"))
    #v(2mm)
    #grid(
      columns: (2fr, 1fr),
      align(left)[
        #vendor.name | SIRET: #vendor.at("siret", default: "N/A") | TVA Intracomm: #vendor.at("vat_id", default: "N/A")\
        Facture électronique conforme à la directive européenne 2014/55/UE et à la norme EN 16931 (Factur-X / ZUGFeRD 2.2).
      ],
      context align(right)[Page #counter(page).display("1 / 1", both: true)]
    )
  ]
)

#set text(font: ("Helvetica", "Arial", "Liberation Sans"), size: 9pt, fill: rgb("#1e293b"))

// 1. Header Bar with Enterprise Badge
#grid(
  columns: (1fr, 1fr),
  align(left)[
    #text(size: 19pt, weight: "black", fill: rgb("#0f172a"))[#vendor.name]
    #v(1mm)
    #text(size: 8.5pt, fill: rgb("#64748b"))[
      #vendor.address\
      #vendor.city, #vendor.country\
      TVA: *#vendor.vat_id* | SIRET: *#vendor.at("siret", default: "N/A")*\
      #text(fill: rgb("#2563eb"))[#vendor.email]
    ]
  ],
  align(right)[
    #stack(
      spacing: 6pt,
      [
        #rect(
          fill: rgb("#eff6ff"),
          stroke: 0.5pt + rgb("#bfdbfe"),
          radius: 4pt,
          inset: (x: 7pt, y: 3.5pt)
        )[
          #text(size: 7.5pt, weight: "bold", fill: rgb("#1d4ed8"))[🇪🇺 FACTUR-X / ZUGFeRD 2.2 EN 16931]
        ]
        #h(4pt)
        #rect(
          fill: if status == "PAID" { rgb("#f0fdf4") } else { rgb("#fffbeb") },
          stroke: 0.5pt + if status == "PAID" { rgb("#86efac") } else { rgb("#fde68a") },
          radius: 4pt,
          inset: (x: 8pt, y: 3.5pt)
        )[
          #text(size: 8pt, weight: "bold", fill: if status == "PAID" { rgb("#15803d") } else { rgb("#b45309") })[#status]
        ]
      ],
      [
        #text(size: 16pt, weight: "bold", fill: rgb("#0f172a"))[FACTURE / INVOICE]
      ],
      [
        #text(size: 8.5pt, fill: rgb("#64748b"))[
          *N° Facture:* #invoice_number\
          *Date d'émission:* #issued_date\
          *Échéance:* #due_date
        ]
      ]
    )
  ]
)

#v(6mm)

// 2. Parties Grid (Vendor & Customer Details)
#grid(
  columns: (1fr, 1fr),
  gutter: 1cm,
  rect(width: 100%, fill: rgb("#f8fafc"), stroke: 0.5pt + rgb("#e2e8f0"), radius: 5pt, inset: 9pt)[
    #text(size: 7.5pt, weight: "bold", fill: rgb("#64748b"))[ÉMETTEUR (SELLER)]
    #v(1mm)
    #text(weight: "bold", size: 9.5pt, fill: rgb("#0f172a"))[#vendor.name]\
    #text(size: 8.5pt, fill: rgb("#475569"))[
      #vendor.address\
      #vendor.city, #vendor.country\
      N° TVA Intracommunautaire: *#vendor.vat_id*
    ]
  ],
  rect(width: 100%, fill: rgb("#f8fafc"), stroke: 0.5pt + rgb("#e2e8f0"), radius: 5pt, inset: 9pt)[
    #text(size: 7.5pt, weight: "bold", fill: rgb("#64748b"))[DESTINATAIRE (BUYER)]
    #v(1mm)
    #text(weight: "bold", size: 9.5pt, fill: rgb("#0f172a"))[#customer.name]\
    #text(size: 8.5pt, fill: rgb("#475569"))[
      #customer.address\
      #customer.city, #customer.country\
      N° TVA / USt-IdNr: *#customer.vat_id*\
      #if "siret" in customer [N° Enreg: #customer.siret]
    ]
  ]
)

#v(5mm)

// 3. Line Items Table
#table(
  columns: (4.2fr, 0.8fr, 1.2fr, 0.8fr, 1.3fr),
  stroke: none,
  fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else if calc.odd(row) { rgb("#fafafa") } else { none },
  align: (col, row) => (if col == 0 { left } else if col == 1 or col == 3 { center } else { right }),
  inset: (x: 8pt, y: 7pt),
  table.header(
    [*Désignation / Description*],
    [*Qté*],
    [*Prix Unitaire H.T.*],
    [*TVA*],
    [*Montant H.T.*]
  ),
  ..line_items.map(item => {
    let q = item.at("qty", default: 1)
    let p = item.at("unit_price", default: 0.0)
    let tr = item.at("tax_rate", default: data.at("tax_rate", default: 0.0))
    let tr_pct = if tr <= 1.0 { tr * 100.0 } else { tr }
    let line_amt = q * p
    (
      [
        #text(weight: "semibold", fill: rgb("#0f172a"))[#item.name]\
        #if "description" in item and item.description != "" [
          #text(size: 7.5pt, fill: rgb("#64748b"))[#item.description]
        ]
      ],
      [#str(q)],
      [#currency_symbol#str(p)],
      [#str(tr_pct)%],
      [#currency_symbol#str(line_amt)]
    )
  }).flatten()
)

#v(1mm)
#line(length: 100%, stroke: 0.5pt + rgb("#e2e8f0"))
#v(3mm)

// 4. Financial Totals & VAT Breakdown
#grid(
  columns: (1.2fr, 1fr),
  gutter: 1cm,
  [
    // Left: VAT Breakdown Table
    #text(size: 8pt, weight: "bold", fill: rgb("#475569"))[VENTILATION DE LA TVA (TAX BREAKDOWN)]
    #v(1.5mm)
    #table(
      columns: (1fr, 1fr, 1fr),
      stroke: 0.5pt + rgb("#e2e8f0"),
      fill: (col, row) => if row == 0 { rgb("#f8fafc") } else { none },
      inset: (x: 6pt, y: 4pt),
      align: (col, row) => if col == 0 { left } else { right },
      table.header([*Taux*], [*Base H.T.*], [*Montant TVA*]),
      [20.00% (Standard)], [#currency_symbol#str(subtotal)], [#currency_symbol#str(total_tax)]
    )
    #if reverse_charge [
      #v(2mm)
      #text(size: 7.5pt, fill: rgb("#b45309"), weight: "bold")[
        *Autoliquidation de la TVA:* Application de l'article 262 ter I du Code Général des Impôts (Reverse Charge).
      ]
    ]
  ],
  [
    // Right: Summary
    #align(right)[
      #block(width: 100%)[
        #grid(
          columns: (1fr, 1fr),
          gutter: 2.2mm,
          align(left)[#text(fill: rgb("#64748b"))[Total Hors Taxes (H.T.):]],
          align(right)[#currency_symbol#str(subtotal)],
          align(left)[#text(fill: rgb("#64748b"))[Total TVA (#currency_code):]],
          align(right)[#currency_symbol#str(total_tax)],
          align(left)[#text(weight: "bold", size: 10.5pt, fill: rgb("#0f172a"))[Total T.T.C. à Payer:]],
          align(right)[#text(weight: "bold", size: 12.5pt, fill: rgb("#0f172a"))[#currency_symbol#str(grand_total)]]
        )
      ]
    ]
  ]
)

#v(5mm)

// 5. SEPA Payment & Remittance Box
#rect(width: 100%, stroke: 0.5pt + rgb("#cbd5e1"), fill: rgb("#f8fafc"), radius: 5pt, inset: 9pt)[
  #grid(
    columns: (1.5fr, 1fr),
    [
      #text(size: 8pt, weight: "bold", fill: rgb("#1e3a8a"))[COORDONNÉES BANCAIRES SEPA (BANK REMITTANCE)]
      #v(1.5mm)
      #text(size: 8pt, fill: rgb("#334155"))[
        *Banque:* #payment.bank_name\
        *IBAN:* #text(font: "Courier", weight: "bold")[#payment.iban]\
        *BIC / SWIFT:* #text(font: "Courier", weight: "bold")[#payment.bic]\
        *Référence Obligatoire:* #text(weight: "bold", fill: rgb("#0f172a"))[#payment.reference]
      ]
    ],
    [
      #text(size: 8pt, weight: "bold", fill: rgb("#475569"))[CONDITIONS DE RÈGLEMENT]
      #v(1.5mm)
      #text(size: 7.5pt, fill: rgb("#64748b"))[
        Paiement à 30 jours par virement SEPA.\
        En cas de retard: taux d'intérêt légal de 3x + indemnité forfaitaire de 40€ pour frais de recouvrement (Art. D441-5 C. Com).
      ]
    ]
  )
]
