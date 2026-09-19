// Rubrol Enterprise Template: French Factur-X / Chorus Pro Standard
#let raw_data = sys.inputs.at("data", default: "{}")
#let data = if type(raw_data) == str { json(bytes(raw_data)) } else { raw_data }

#let invoice_number = data.at("invoice_number", default: "FAC-2026-0891")
#let issued_date = data.at("issued_date", default: "15/09/2026")
#let due_date = data.at("due_date", default: "15/10/2026")
#let currency_symbol = data.at("currency_symbol", default: "€")

#let vendor = data.at("vendor", default: data.at("seller", default: (:)))
#let customer = data.at("customer", default: data.at("buyer", default: (:)))

#let vendor_name = vendor.at("name", default: "Rubrol France SAS")
#let vendor_siret = vendor.at("siret", default: "891 234 567 00012")
#let vendor_tva = vendor.at("vat_id", default: "FR32891234567")
#let vendor_address = vendor.at("address", default: "14 Rue de la Paix")
#let vendor_city = vendor.at("city", default: "75002 Paris")
#let vendor_iban = vendor.at("iban", default: "FR76 3000 6000 0112 3456 7890 189")
#let vendor_bic = vendor.at("bic", default: "BNPAFRPP")

#let customer_name = customer.at("name", default: "Société Générale de Logistique SAS")
#let customer_siret = customer.at("siret", default: "512 890 123 00045")
#let customer_tva = customer.at("vat_id", default: "FR45512890123")
#let customer_address = customer.at("address", default: "25 Boulevard Haussmann")
#let customer_city = customer.at("city", default: "75009 Paris")

#let line_items = data.at("line_items", default: (
  (description: "Abonnement Annuel Rubrol Enterprise - Moteur Factur-X", qty: 1, unit_price: 4800.00, tva_rate: 0.20),
  (description: "Passerelle Chorus Pro & Validation Schematron EN 16931", qty: 1, unit_price: 0.00, tva_rate: 0.20)
))

#let get_desc(item) = item.at("description", default: item.at("name", default: "Article"))
#let get_qty(item) = float(item.at("qty", default: 1))
#let get_price(item) = float(item.at("unit_price", default: 0.0))
#let get_rate(item) = float(item.at("tva_rate", default: 0.20))

#let subtotal = line_items.fold(0.0, (sum, item) => sum + (get_qty(item) * get_price(item)))
#let tva_amount = line_items.fold(0.0, (sum, item) => sum + (get_qty(item) * get_price(item) * get_rate(item)))
#let total = subtotal + tva_amount

#set page(
  paper: "a4",
  margin: (left: 2.2cm, right: 2.2cm, top: 3.5cm, bottom: 3.0cm),
  footer: [
    #set text(size: 7.5pt, fill: rgb("#64748b"))
    #line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
    #v(2mm)
    #grid(
      columns: (1fr, 1fr),
      align(left)[
        *#vendor_name* · SAS au capital de 50 000 € · SIRET: #vendor_siret\
        RCS Paris B 891 234 567 · N° TVA Intracommunautaire: #vendor_tva
      ],
      align(right)[
        *Coordonnées bancaires:*\
        IBAN: #vendor_iban · BIC: #vendor_bic
      ]
    )
  ]
)

#set text(font: ("Liberation Sans", "Helvetica", "Arial"), size: 9pt, fill: rgb("#1e293b"))

#grid(
  columns: (1fr, 1fr),
  [
    #text(size: 16pt, weight: "bold", fill: rgb("#0f172a"))[#vendor_name]\
    #v(1mm)
    #vendor_address\
    #vendor_city\
    SIRET: #vendor_siret\
    N° TVA: #vendor_tva
  ],
  align(right)[
    #block(fill: rgb("#f8fafc"), inset: 12pt, stroke: 0.5pt + rgb("#e2e8f0"), radius: 4pt, width: 85%)[
      #align(left)[
        #text(size: 8pt, fill: rgb("#64748b"))[DESTINATAIRE / CLIENT]\
        #v(1mm)
        #text(weight: "bold", size: 10.5pt)[#customer_name]\
        #customer_address\
        #customer_city\
        SIRET: #customer_siret\
        TVA: #customer_tva
      ]
    ]
  ]
)

#v(8mm)
#grid(
  columns: (1fr, 1fr),
  [
    #text(size: 15pt, weight: "bold", fill: rgb("#0f172a"))[FACTURE N° #invoice_number]\
    #text(size: 8.5pt, fill: rgb("#15803d"), weight: "bold")[Format certifié Factur-X / ZUGFeRD 2.2 (Profil EN 16931)]
  ],
  align(right)[
    #text(size: 8.5pt)[
      *Date d'émission:* #issued_date\
      *Date d'échéance:* #due_date\
      *Mode de règlement:* Virement bancaire
    ]
  ]
)

#v(6mm)

#table(
  columns: (1fr, auto, auto, auto, auto),
  stroke: (x, y) => if y == 0 { (bottom: 1.5pt + rgb("#0f172a")) } else { (bottom: 0.5pt + rgb("#e2e8f0")) },
  fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else { none },
  inset: (x: 8pt, y: 7pt),
  align: (col, row) => if col == 0 { left } else { right },
  [*Désignation des prestations*], [*Qté*], [*Prix Unitaire HT*], [*Taux TVA*], [*Total HT*],
  ..line_items.map(item => (
    get_desc(item),
    str(get_qty(item)),
    currency_symbol + " " + str(calc.round(get_price(item), digits: 2)),
    str(int(get_rate(item) * 100)) + " %",
    currency_symbol + " " + str(calc.round(get_qty(item) * get_price(item), digits: 2))
  )).flatten()
)

#v(4mm)
#align(right)[
  #block(width: 45%)[
    #grid(
      columns: (1fr, 1fr),
      row-gutter: 6pt,
      align(left)[Total HT:], align(right)[#currency_symbol #calc.round(subtotal, digits: 2)],
      align(left)[TVA (20%):], align(right)[#currency_symbol #calc.round(tva_amount, digits: 2)],
      grid.hline(stroke: 1pt + rgb("#0f172a")),
      align(left)[*Total TTC:*], align(right)[*#currency_symbol #calc.round(total, digits: 2)*]
    )
  ]
]

#v(6mm)
#block(fill: rgb("#f8fafc"), inset: 8pt, stroke: 0.5pt + rgb("#e2e8f0"), radius: 4pt)[
  #set text(size: 8pt, fill: rgb("#475569"))
  *Conditions de paiement :* Règlement à 30 jours net date de facture. Aucun escompte pour paiement anticipé. En cas de retard de paiement, une indemnité forfaitaire de 40 € pour frais de recouvrement sera due (Article L.441-6 du code de commerce), en sus des pénalités de retard au taux directeur de la BCE majoré de 10 points.
]
