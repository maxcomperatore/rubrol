// Platen Template Vault: Clinical Summary & Medical Intake Form (HIPAA)
#let raw_data = sys.inputs.at("data", default: "{}")
#let data = if type(raw_data) == str { json(bytes(raw_data)) } else { raw_data }

#let patient = data.at("patient", default: (
  name: "Eleanor Vance",
  dob: "1988-04-12",
  mrn: "MRN-849204",
  gender: "Female",
  blood_type: "O+"
))

#let provider = data.at("provider", default: (
  clinic: "MetroHealth Precision Medical Group",
  physician: "Dr. Julian Montgomery, MD",
  npi: "1948201942",
  encounter_date: "2026-09-15"
))

#let vitals = data.at("vitals", default: (
  bp: "118/76 mmHg",
  hr: "72 bpm",
  temp: "98.6 °F",
  weight: "68.5 kg",
  spo2: "99%"
))

#let diagnoses = data.at("diagnoses", default: (
  (code: "E11.9", description: "Type 2 diabetes mellitus without complications"),
  (code: "I10", description: "Essential (primary) hypertension"),
  (code: "Z71.3", description: "Dietary counseling and surveillance")
))

#let medications = data.at("medications", default: (
  (name: "Metformin HCl", dosage: "500 mg", frequency: "Twice daily with meals"),
  (name: "Lisinopril", dosage: "10 mg", frequency: "Once daily in morning")
))

#set page(
  paper: "a4",
  margin: (x: 2cm, top: 2.2cm, bottom: 2cm),
  header: [
    #grid(
      columns: (1fr, 1fr),
      align(left)[#text(size: 8pt, weight: "bold", fill: rgb("#0284c7"))[CLINICAL ENCOUNTER REPORT | CONFIDENTIAL]],
      align(right)[#text(size: 8pt, fill: rgb("#64748b"))[MRN: #patient.mrn]]
    )
    #line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
  ],
  footer: [
    #line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
    #v(1mm)
    #grid(
      columns: (1fr, 1fr),
      align(left)[#text(size: 7.5pt, fill: rgb("#94a3b8"))[HIPAA Safeguarded Record - Authorized Clinical Personnel Only]],
      context align(right)[#text(size: 7.5pt, fill: rgb("#94a3b8"))[Page #counter(page).display("1 of 1", both: true)]]
    )
  ]
)

#set text(font: ("Helvetica", "Arial"), size: 9pt, fill: rgb("#1e293b"))

// Provider Header
#grid(
  columns: (2fr, 1fr),
  [
    #text(size: 15pt, weight: "bold", fill: rgb("#0f172a"))[#provider.clinic]\
    #text(size: 9.5pt, fill: rgb("#475569"))[Attending Physician: *#provider.physician* (NPI: #provider.npi)]
  ],
  align(right)[
    #text(size: 9pt, fill: rgb("#64748b"))[
      *Encounter Date:* #provider.encounter_date\
      *Facility ID:* MH-OR-04
    ]
  ]
)

#v(4mm)

// Patient Info Box
#rect(width: 100%, fill: rgb("#f0f9ff"), stroke: 0.5pt + rgb("#bae6fd"), radius: 5pt, inset: 10pt)[
  #text(size: 7.5pt, weight: "bold", fill: rgb("#0369a1"))[PATIENT DEMOGRAPHICS]
  #v(1.5mm)
  #grid(
    columns: (1.5fr, 1fr, 1fr, 1fr, 1fr),
    [*Name:* #patient.name],
    [*DOB:* #patient.dob],
    [*MRN:* #patient.mrn],
    [*Sex:* #patient.gender],
    [*Blood Type:* #patient.blood_type]
  )
]

#v(4mm)

// Vital Signs Panel
#text(size: 10.5pt, weight: "bold", fill: rgb("#0f172a"))[Vital Signs Summary]
#v(1.5mm)
#grid(
  columns: (1fr, 1fr, 1fr, 1fr, 1fr),
  gutter: 2.5mm,
  ..("Blood Pressure": vitals.bp, "Heart Rate": vitals.hr, "Temperature": vitals.temp, "Weight": vitals.weight, "SpO2": vitals.spo2).pairs().map(pair => (
    rect(width: 100%, fill: rgb("#f8fafc"), stroke: 0.5pt + rgb("#e2e8f0"), radius: 4pt, inset: 6pt)[
      #align(center)[
        #text(size: 7pt, weight: "bold", fill: rgb("#64748b"))[#pair.at(0)]\
        #v(1mm)
        #text(size: 10pt, weight: "bold", fill: rgb("#0f172a"))[#pair.at(1)]
      ]
    ]
  ))
)

#v(4mm)

// Diagnoses
#text(size: 10.5pt, weight: "bold", fill: rgb("#0f172a"))[Clinical Diagnoses (ICD-10-CM)]
#v(1.5mm)
#table(
  columns: (1fr, 4fr),
  stroke: none,
  fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else if calc.odd(row) { rgb("#f8fafc") } else { none },
  inset: (x: 8pt, y: 6pt),
  table.header([*ICD-10 Code*], [*Condition / Description*]),
  ..diagnoses.map(d => ([#text(weight: "bold", fill: rgb("#0284c7"))[#d.code]], [#d.description])).flatten()
)

#v(4mm)

// Medications
#text(size: 10.5pt, weight: "bold", fill: rgb("#0f172a"))[Active Pharmacotherapy]
#v(1.5mm)
#table(
  columns: (2fr, 1fr, 3fr),
  stroke: none,
  fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else if calc.odd(row) { rgb("#f8fafc") } else { none },
  inset: (x: 8pt, y: 6pt),
  table.header([*Medication*], [*Dosage*], [*Instructions / Frequency*]),
  ..medications.map(m => ([#text(weight: "medium")[#m.name]], [#m.dosage], [#m.frequency])).flatten()
)

#v(8mm)
#grid(
  columns: (1fr, 1fr),
  gutter: 2cm,
  [
    #line(length: 100%, stroke: 0.5pt + rgb("#94a3b8"))
    #v(1mm)
    #text(size: 8pt, fill: rgb("#64748b"))[Electronically Signed: #provider.physician (MD)]
  ],
  [
    #line(length: 100%, stroke: 0.5pt + rgb("#94a3b8"))
    #v(1mm)
    #text(size: 8pt, fill: rgb("#64748b"))[Timestamp: 2026-09-15 14:22:08 UTC (Verified)]
  ]
)
