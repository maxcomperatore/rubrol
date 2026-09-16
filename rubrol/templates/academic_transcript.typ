// Rubrol Template Vault: Official University Academic Transcript
#let raw_data = sys.inputs.at("data", default: "{}")
#let data = if type(raw_data) == str { json(bytes(raw_data)) } else { raw_data }

#let institution = data.at("institution", default: (
  name: "Massachusetts Institute of Advanced Technology",
  office: "Office of the University Registrar",
  address: "77 Massachusetts Avenue, Cambridge, MA 02139",
  accreditation: "NECHE Accredited Institution"
))

#let student = data.at("student", default: (
  name: "Marcus Aurelius Vance",
  id: "MIT-2022-89410",
  dob: "2003-04-12",
  program: "Bachelor of Science in Computer Systems Engineering",
  conferral_date: "June 05, 2026",
  honors: "Summa Cum Laude (Highest Distinction)",
  cumulative_gpa: "3.96",
  total_credits: 128
))

#let terms = data.at("terms", default: (
  (
    term_name: "Fall 2025 Semester",
    courses: (
      (code: "CS 450", title: "Distributed Consensus Algorithms", credits: 4, grade: "A", points: 16.0),
      (code: "CS 480", title: "Compiler Design & Code Generation", credits: 4, grade: "A+", points: 16.0),
      (code: "MATH 412", title: "Abstract Algebra & Category Theory", credits: 4, grade: "A", points: 16.0),
      (code: "EE 340", title: "VLSI Architecture & Microcode", credits: 4, grade: "A-", points: 14.8)
    ),
    term_gpa: "3.92",
    term_credits: 16
  ),
  (
    term_name: "Spring 2026 Semester (Final)",
    courses: (
      (code: "CS 499", title: "Senior Capstone: High-Throughput Sub-8ms Renderers", credits: 4, grade: "A+", points: 16.0),
      (code: "CS 475", title: "Cryptographic Engineering & Zero-Knowledge", credits: 4, grade: "A+", points: 16.0),
      (code: "PHYS 310", title: "Quantum Information Theory", credits: 4, grade: "A", points: 16.0),
      (code: "ECON 320", title: "Industrial Organization & Tech Monopolies", credits: 4, grade: "A", points: 16.0)
    ),
    term_gpa: "4.00",
    term_credits: 16
  )
))

#set page(
  paper: "a4",
  margin: (x: 2.2cm, top: 2.2cm, bottom: 2.2cm),
  footer: [
    #set text(size: 8pt, fill: rgb("#71717a"))
    #line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
    #v(2mm)
    #grid(
      columns: (1.5fr, 1fr),
      align(left)[#institution.name | OFFICIAL ACADEMIC TRANSCRIPT],
      context align(right)[Page #counter(page).display("1 of 1", both: true)]
    )
    #v(1mm)
    #text(size: 7pt, fill: rgb("#94a3b8"))[Record is authentic if verified via Rubrol cryptographic signature chain. Alteration invalidates this document.]
  ]
)

#set text(font: ("Helvetica", "Arial"), size: 8.5pt, fill: rgb("#0f172a"))

#grid(
  columns: (2fr, 1fr),
  [
    #text(size: 14pt, weight: "bold", fill: rgb("#0f172a"))[#institution.name]\
    #text(size: 10pt, weight: "medium", fill: rgb("#1e3a8a"))[#institution.office]\
    #text(size: 8pt, fill: rgb("#64748b"))[#institution.address | #institution.accreditation]
  ],
  align(right)[
    #rect(fill: rgb("#f8fafc"), stroke: 0.5pt + rgb("#cbd5e1"), radius: 4pt, inset: 6pt)[
      #text(size: 7.5pt, font: ("JetBrains Mono", "Courier"), fill: rgb("#475569"))[RECORD STATUS]\
      #text(weight: "bold", size: 9pt, fill: rgb("#15803d"))[OFFICIAL TRANSCRIPT]\
      #text(size: 7.5pt, fill: rgb("#64748b"))[Conferred: #student.conferral_date]
    ]
  ]
)

#v(4mm)

#rect(width: 100%, fill: rgb("#f8fafc"), stroke: 0.5pt + rgb("#e2e8f0"), radius: 4pt, inset: 8pt)[
  #grid(
    columns: (1fr, 1fr),
    gutter: 2mm,
    [
      #text(size: 8pt, fill: rgb("#64748b"))[Student Name:] *#student.name*\
      #text(size: 8pt, fill: rgb("#64748b"))[Student ID:] `#student.id`\
      #text(size: 8pt, fill: rgb("#64748b"))[Degree Program:] #student.program
    ],
    [
      #text(size: 8pt, fill: rgb("#64748b"))[Cumulative GPA:] *#student.cumulative_gpa / 4.00*\
      #text(size: 8pt, fill: rgb("#64748b"))[Credits Earned:] *#str(student.total_credits) Units*\
      #text(size: 8pt, fill: rgb("#64748b"))[Academic Honors:] *#student.honors*
    ]
  )
]

#v(4mm)

#for t in terms [
  #v(2mm)
  #text(weight: "bold", size: 9pt, fill: rgb("#1e293b"))[#t.term_name]
  #v(1mm)
  #table(
    columns: (1fr, 3fr, 0.8fr, 0.8fr, 1fr),
    stroke: none,
    fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else if calc.odd(row) { rgb("#fafafa") } else { none },
    align: (col, row) => (if col == 0 { left } else if col == 1 { left } else { right }),
    inset: (x: 6pt, y: 5pt),
    table.header([*Course*], [*Course Title*], [*Credits*], [*Grade*], [*Points*]),
    ..t.courses.map(c => (
      [#text(font: ("JetBrains Mono", "Courier"), size: 8pt)[#c.code]],
      [#c.title],
      [#str(c.credits)],
      [#text(weight: "bold")[#c.grade]],
      [#str(c.points)]
    )).flatten()
  )
  #align(right)[
    #text(size: 8pt, fill: rgb("#64748b"))[Term GPA: *#t.term_gpa* | Term Credits: *#str(t.term_credits)*]
  ]
]

#v(5mm)

#grid(
  columns: (1fr, 1fr),
  gutter: 10mm,
  rect(width: 100%, stroke: 0.5pt + rgb("#e2e8f0"), radius: 4pt, inset: 8pt)[
    #text(size: 8pt, weight: "bold", fill: rgb("#475569"))[GRADING BASIS & AUTHENTICATION]\
    #text(size: 7.5pt, fill: rgb("#64748b"))[
      A+ (4.0), A (4.0), A- (3.7), B+ (3.3), B (3.0).\
      This transcript was compiled directly by the Rubrol sub-8ms engine with cryptographically anchored record integrity.
    ]
  ],
  rect(width: 100%, stroke: 0.5pt + rgb("#e2e8f0"), radius: 4pt, inset: 8pt)[
    #text(size: 8pt, weight: "bold", fill: rgb("#475569"))[OFFICIAL REGISTRAR ENDORSEMENT]\
    #v(3mm)
    #line(length: 80%, stroke: 0.5pt + rgb("#94a3b8"))
    #text(size: 7.5pt, fill: rgb("#64748b"))[Dr. Eleanor Vance, University Registrar]
  ]
)
