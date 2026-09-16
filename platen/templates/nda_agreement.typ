// Platen Template Vault: Mutual Non-Disclosure Agreement
#let raw_data = sys.inputs.at("data", default: "{}")
#let data = if type(raw_data) == str { json(bytes(raw_data)) } else { raw_data }

#let agreement_date = data.at("agreement_date", default: "September 15, 2026")
#let governing_law = data.at("governing_law", default: "State of California")

#let party_a = data.at("party_a", default: (
  name: "Platen Engine Inc.",
  jurisdiction: "Delaware",
  address: "548 Market Street, Suite 300, San Francisco, CA 94104",
  signatory: "Alexander Hayes, CEO"
))

#let party_b = data.at("party_b", default: (
  name: "Vanguard Analytics Corp.",
  jurisdiction: "New York",
  address: "350 5th Avenue, 42nd Floor, New York, NY 10118",
  signatory: "Evelyn Reed, General Counsel"
))

#set page(
  paper: "a4",
  margin: (x: 2.5cm, top: 2.8cm, bottom: 2.8cm),
  footer: [
    #set text(size: 8pt, fill: rgb("#71717a"))
    #line(length: 100%, stroke: 0.5pt + rgb("#e2e8f0"))
    #v(2mm)
    #grid(
      columns: (1fr, 1fr),
      align(left)[MUTUAL NON-DISCLOSURE AGREEMENT],
      context align(right)[Page #counter(page).display("1 of 1", both: true)]
    )
  ]
)

#set text(font: ("Times New Roman", "Liberation Serif"), size: 10pt, fill: rgb("#0f172a"))

#align(center)[
  #text(size: 14pt, font: ("Helvetica", "Arial"), weight: "bold")[MUTUAL NON-DISCLOSURE AGREEMENT]
  #v(2mm)
  #text(size: 9pt, fill: rgb("#64748b"))[Effective Date: #agreement_date]
]

#v(6mm)

This Mutual Non-Disclosure Agreement ("Agreement") is executed as of *#agreement_date*, by and between *#party_a.name*, a #party_a.jurisdiction corporation ("Party A"), and *#party_b.name*, a #party_b.jurisdiction corporation ("Party B").

#v(3mm)
*1. Purpose.* The parties intend to engage in discussions concerning potential commercial and technical integration ("Transaction"). In connection therewith, each party may disclose proprietary confidential information to the other.

#v(3mm)
*2. Confidential Information.* "Confidential Information" encompasses all non-public intellectual property, software source code, compiler architectures, business metrics, and financial records disclosed whether orally, in writing, or electronically.

#v(3mm)
*3. Duty of Non-Disclosure.* The receiving party agrees to maintain confidentiality using the standard of care reasonable to protect its own similar confidential information, and shall not disclose Confidential Information to any third party without prior written consent.

#v(3mm)
*4. Governing Law.* This Agreement shall be governed and construed in accordance with the substantive laws of the *#governing_law*, without regard to conflict of laws principles.

#v(1.2cm)

#grid(
  columns: (1fr, 1fr),
  gutter: 2cm,
  [
    #text(weight: "bold")[#party_a.name]\
    #v(1.2cm)
    #line(length: 100%, stroke: 0.5pt + rgb("#64748b"))
    #v(1mm)
    #text(size: 9pt)[By: #party_a.signatory]\
    #text(size: 8.5pt, fill: rgb("#64748b"))[Date: #agreement_date]
  ],
  [
    #text(weight: "bold")[#party_b.name]\
    #v(1.2cm)
    #line(length: 100%, stroke: 0.5pt + rgb("#64748b"))
    #v(1mm)
    #text(size: 9pt)[By: #party_b.signatory]\
    #text(size: 8.5pt, fill: rgb("#64748b"))[Date: #agreement_date]
  ]
)
