// Rubrol Enterprise Template: German DIN 5008 Standard E-Rechnung
#let raw_data = sys.inputs.at("data", default: "{}")
#let data = if type(raw_data) == str { json(bytes(raw_data)) } else { raw_data }

#let invoice_number = data.at("invoice_number", default: "RE-2026-1042")
#let issued_date = data.at("issued_date", default: "15.09.2026")
#let delivery_date = data.at("delivery_date", default: issued_date)
#let due_date = data.at("due_date", default: "15.10.2026")
#let currency_symbol = data.at("currency_symbol", default: "€")
#let leitweg_id = data.at("buyer_reference", default: data.at("leitweg_id", default: "04011000-12345-67"))

#let vendor = data.at("vendor", default: data.at("seller", default: (:)))
#let customer = data.at("customer", default: data.at("buyer", default: (:)))

#let vendor_name = vendor.at("name", default: "Rubrol Systems GmbH")
#let vendor_ustid = vendor.at("vat_id", default: vendor.at("tax_id", default: "DE345678901"))
#let vendor_address = vendor.at("address", default: "Friedrichstraße 120")
#let vendor_city = vendor.at("city", default: "10117 Berlin")
#let vendor_iban = vendor.at("iban", default: "DE89 3704 0044 0532 0130 00")
#let vendor_bic = vendor.at("bic", default: "DBBADEFFXXX")
#let vendor_hrb = vendor.at("hrb", default: "Amtsgericht Charlottenburg, HRB 198420 B")

#let customer_name = customer.at("name", default: "Valitool Prüfsysteme AG")
#let customer_ustid = customer.at("vat_id", default: customer.at("tax_id", default: "DE123456789"))
#let customer_address = customer.at("address", default: "Hauptstraße 45")
#let customer_city = customer.at("city", default: "80331 München")

#let line_items = data.at("line_items", default: (
  (description: "Rubrol Enterprise Lizenz (Unbegrenzte Container-Instanzen)", qty: 1, unit_price: 4800.00, tax_rate: 0.19),
  (description: "EN 16931 Schematron Validierungsmodul 2026", qty: 1, unit_price: 0.00, tax_rate: 0.19)
))

#let get_desc(item) = item.at("description", default: item.at("name", default: "Position"))
#let get_qty(item) = float(item.at("qty", default: 1))
#let get_price(item) = float(item.at("unit_price", default: 0.0))
#let get_rate(item) = float(item.at("tax_rate", default: 0.19))

#let subtotal = line_items.fold(0.0, (sum, item) => sum + (get_qty(item) * get_price(item)))
#let vat_amount = line_items.fold(0.0, (sum, item) => sum + (get_qty(item) * get_price(item) * get_rate(item)))
#let total = subtotal + vat_amount

#set page(
  paper: "a4",
  margin: (left: 2.5cm, right: 2.0cm, top: 3.0cm, bottom: 3.5cm),
  footer: [
    #set text(size: 7.5pt, fill: rgb("#64748b"))
    #line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
    #v(2mm)
    #grid(
      columns: (1fr, 1fr, 1fr),
      [
        *Sitz der Gesellschaft:* #vendor_city\
        *Registergericht:* #vendor_hrb\
        *Geschäftsführung:* Max Comperatore
      ],
      [
        *USt-IdNr.:* #vendor_ustid\
        *Steuernummer:* 27/123/45678\
        *E-Rechnungs-Standard:* EN 16931 / Factur-X
      ],
      [
        *Bankverbindung:*\
        *IBAN:* #vendor_iban\
        *BIC:* #vendor_bic
      ]
    )
  ]
)

#set text(font: ("Liberation Sans", "Helvetica", "Arial"), size: 9pt, fill: rgb("#1e293b"))

// Header Logo and Company Info
#grid(
  columns: (1fr, 1fr),
  align(left)[
    #text(size: 7.5pt, fill: rgb("#64748b"))[#vendor_name · #vendor_address · #vendor_city]
  ],
  align(right)[
    #text(size: 16pt, weight: "bold", fill: rgb("#0f172a"))[#vendor_name]
  ]
)

#v(8mm)

// Anschriftenfeld (DIN 5008 Typ B)
#grid(
  columns: (1.2fr, 1fr),
  [
    #v(3mm)
    #text(weight: "bold", size: 10pt)[#customer_name]\
    #customer_address\
    #customer_city\
    #if customer_ustid != "N/A" [USt-IdNr.: #customer_ustid]
  ],
  align(right)[
    #block(stroke: 0.5pt + rgb("#e2e8f0"), inset: 10pt, radius: 4pt, fill: rgb("#f8fafc"))[
      #set text(size: 8.5pt)
      #grid(
        columns: (auto, auto),
        row-gutter: 5pt,
        column-gutter: 12pt,
        align(left)[*Rechnungsnummer:*], align(right)[#invoice_number],
        align(left)[*Rechnungsdatum:*], align(right)[#issued_date],
        align(left)[*Lieferdatum:*], align(right)[#delivery_date],
        align(left)[*Leitweg-ID (BT-10):*], align(right)[#leitweg_id],
        align(left)[*Zahlungsziel:*], align(right)[#due_date],
      )
    ]
  ]
)

#v(8mm)
#text(size: 14pt, weight: "bold", fill: rgb("#0f172a"))[Rechnung Nr. #invoice_number]
#v(2mm)
#text(size: 8.5pt)[Sehr geehrte Damen und Herren,\nvielen Dank für Ihren Auftrag. Wir berechnen Ihnen vereinbarungsgemäß folgende Leistungen:]

#v(4mm)

// Positionen-Tabelle
#table(
  columns: (auto, 1fr, auto, auto, auto, auto),
  stroke: (x, y) => if y == 0 { (bottom: 1.5pt + rgb("#0f172a")) } else { (bottom: 0.5pt + rgb("#e2e8f0")) },
  fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else { none },
  inset: (x: 8pt, y: 7pt),
  align: (col, row) => (
    if col == 0 { center }
    else if col == 1 { left }
    else { right }
  ),
  [*Pos.*], [*Bezeichnung*], [*Menge*], [*Einzelpreis*], [*USt.*], [*Gesamtbetrag*],
  ..line_items.enumerate().map(((idx, item)) => (
    str(idx + 1),
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
      align(left)[Nettobetrag:], align(right)[#currency_symbol #calc.round(subtotal, digits: 2)],
      align(left)[zzgl. 19 % USt.:], align(right)[#currency_symbol #calc.round(vat_amount, digits: 2)],
      grid.hline(stroke: 1pt + rgb("#0f172a")),
      align(left)[*Gesamtbetrag:*], align(right)[*#currency_symbol #calc.round(total, digits: 2)*]
    )
  ]
]

#v(6mm)
#block(fill: rgb("#f8fafc"), inset: 10pt, stroke: 0.5pt + rgb("#cbd5e1"), radius: 4pt)[
  *Zahlungshinweis:* Bitte überweisen Sie den Gesamtbetrag von *#currency_symbol #calc.round(total, digits: 2)* bis zum *#due_date* auf unser angegebenes Bankkonto unter Angabe der Rechnungsnummer *#invoice_number*.
]
