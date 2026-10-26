# Editable Name Tracing Worksheets - LISTED 2026-10-26: etsy.com/listing/4603338038

- `Name_Tracing_Editable_US_Letter.pdf` + `Name_Tracing_Editable_A4.pdf` (PAGESIZE=A4) = the product (1 text field "ChildName", 23 widgets on 6 pages; typing on page 1 fills all pages).
- `name_1..5.jpg` = listing images (1500x1875), sample names Emma / Liam.
- Fonts: Colorbloop Trace (dotted, from Andika), Colorbloop Print (Andika, metrics changed), Colorbloop Outline (from Fredoka Bold). All SIL OFL 1.1, renamed per Reserved Font Name rules; embedding in PDFs is allowed.
- Tested in PDFium (Chrome engine): typing updates every page. Best viewer for buyers: Adobe Acrobat Reader. Still to test by hand: Adobe Reader desktop + phone, Mac Preview.
- Rebuild: python3 make_fonts.py DL OUT; python3 make_pdf.py DL FONTDIR out.pdf [sample name]; make_mockups.py
