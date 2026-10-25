# eRank log (free plan: 5 keyword lookups, 5 listing audits, 1 AI helper per day)

## 2026-10-22 (setup day, done manually)
Keyword lookups (Etsy US, Sep-2026 data = pre-season; Dec volumes will be several times higher):
| keyword | avg searches | clicks | CTR | competition |
|---|---|---|---|---|
| christmas bingo | 705 | 714 | 101% | 11,474 | <- best ratio, big opportunity
| christmas coloring pages | 400 | 396 | 99% | 38,828 |
| christmas activities for kids | 199 | 197 | 99% | 70,434 |
| thanksgiving coloring pages | 114 | 111 | 97% | 9,121 |
| advent calendar kids | 101 | 99 | 98% | 12,989 |

Changes:
- 4599374187 Christmas Party Games: title "Christmas Party Games Printable Pack, Kids Activities, Bingo, Scavenger Hunt (PDF)"
  -> "Christmas Bingo for Kids Printable, Christmas Party Games Pack, Scavenger Hunt, Would You Rather, Classroom Holiday Party Activities PDF";
  tag "christmas countdown" -> "holiday party games" (countdown now has its own book).
Idea: a standalone $2.99 "Christmas Picture Bingo" listing (bingo cards + caller cards from the party pack).



## 2026-10-22 (run 2, scheduled task)
Keyword lookups: 0 left (all 5 used in setup run above). Extra keyword data from audits + AI helper (Sep-2026, US):
| keyword | searches | CTR | competition |
|---|---|---|---|
| kids coloring pages | 494 | 98% | 223,025 |
| christmas countdown | 410 | 130% | 22,413 |
| thanksgiving art | 218 | 100% | 347,572 |
| christmas activities | 208 | 99% | 94,489 |
| preschool christmas | 191 | 99% | 35,744 |
| fall coloring pages | 122 | 93% | 16,692 |
| christmas activity | 107 | 102% | 95,528 |
| thanksgiving print | 103 | 97% | 185,683 |
| advent activities | 100 | 98% | 8,816 | <- low comp
| holiday printable | 100 | 97% | 464,759 |
| thanksgiving fun | 96 | 98% | 25,574 |
| thanksgiving pumpkin | 35 | 149% | 385,319 |
Zero/<20 volume: kids christmas pdf, toddler activities, homeschool december, christmas party kids, bold coloring pages, turkey day kids, kids table activity, autumn printable, november printable, kids thanksgiving, new year kids, thanksgiving pages, december activities, holiday activities.

Audits (5/5) + changes (all published):
- 4599336007 xmas_activity
  title "Christmas Activity Book for Kids Ages 3-6, Coloring, Mazes, Tracing (PDF)"
  -> "Christmas Activities for Kids, Christmas Activity Book Ages 3-6, Coloring Pages, Mazes, Tracing Worksheets PDF"
  tags: -kids christmas pdf, -toddler activities, -homeschool december; +christmas activity, +kids coloring pages, +holiday printable
- 4599339201 xmas_coloring
  title "Big Easy Christmas Coloring Book for Toddlers Ages 2-5 (PDF Download)"
  -> "Christmas Coloring Pages for Toddlers, Big Easy Christmas Coloring Book Ages 2-5, Preschool Holiday Printable PDF"
  tags: -kids christmas pdf, -christmas party kids, -bold coloring pages; +kids coloring pages, +christmas activity, +holiday printable, +christmas activities (filled 13/13)
- 4599340187 thanksgiving (weakest; AI Listing Helper used on it)
  title "Thanksgiving Coloring Book for Toddlers, Fall Turkey Pumpkin Pages (PDF)"
  -> "Thanksgiving Coloring Pages for Toddlers and Preschool, Fall Turkey Pumpkin Coloring Book, Kids Thanksgiving Activity PDF"
  tags: -kids thanksgiving, -autumn printable, -turkey day kids, -kids table activity, -november printable;
        +kids coloring pages, +thanksgiving art, +thanksgiving fun, +thanksgiving print, +thanksgiving pumpkin
- 4600569765 countdown (title kept, grade B)
  tags: -toddler activities, -holiday activities, -december activities; +advent activities, +christmas activities, +christmas coloring
- 4599391756 bundle_holiday (title kept)
  tags: -thanksgiving pages, -new year kids, -classroom christmas, -kids party games; +fall coloring pages, +preschool christmas, +christmas printable, +kids coloring pages
Audit notes for all 5: attributes missing (no attribute fields offered for digital coloring books besides width/height), main-image alt text missing.

Audit rotation (next up): numbers, shapes, preschool, animals, kindergarten, then the rest of links.json["etsy"] in order
(abc, dinosaurs, vehicles... follow; skip valcards 4600588895 + ramadan 4600589623 until January).

## 2026-10-22 (run 3, Mohamed asked: do the suggestions + fix alt text)
- Fall sampler idea: already exists (sampler_fall 4600700353, $1.49), so no new listing was created. Retagged it instead:
  -kids table activity, -kids coloring pdf, -autumn worksheets; +kids coloring pages, +thanksgiving art, +thanksgiving fun.
- Main-image alt text written by hand (describes the actual cover + sample pages, ages, page count) and published on ALL 37 active listings.
  ~12 of them had only Etsy's auto "May include: ..." text, the rest were empty. Inactive valcards/ramadan untouched.
- Note for Mohamed: xmas_activity (4599336007) cover image says 34 pages, description says 38 pages; check which is right.

## 2026-10-22 (run 4, Mohamed: check page counts from the real files + alt text on ALL photos)
- Downloaded each listing's US Letter PDF (to Mohamed's Downloads) and counted pages with pdfinfo/pdftotext.
  - xmas_activity 4599336007: PDF = 38 pages = 34 activity pages + cover, grown-ups note, answer key, thank-you. Cover "34 FUN PAGES" and old desc "38 pages" were both right; desc now explains the split.
  - "WHAT'S INSIDE (N pages)" line rewritten to "N-page PDF: X pages + cover, grown-ups note, thank-you..." on: xmas_activity, thanksgiving (29=26+3), ABC (31), numbers (29), shapes (29), preschool (84), animals (70), kindergarten (78), dinosaurs (29), vehicles (29), unicorns (29), scissors (55), sight words (77), letter tracing (70), cursive (77), space (35), feelings (43), valentines (34), easter (43). All totals matched the PDFs; only the wording was unclear.
  - Noted, not changed: Big Easy Christmas Coloring cover says "32 designs", PDF has 34 coloring pages (desc says 37 = total, OK).
  - countdown (31), myyear (33-page/30), winter (46 PDF vs desc "43 pages" ~ activity pages 41+key+cert=43 OK), busy book (37), routine (23), party games (35 PDF; 32 party pages), bingo (14): already OK.
- Alt text written by hand for EVERY photo (not only main) on all 37 active listings: what's inside grid, sample pages, close-up, how it works, extra feature images. Published each.

## 2026-10-24 (scheduled run; Chrome was offline at first, ran after Mohamed reconnected it)
Keyword lookups (5/5, Etsy US, Sep-2026 data):
| keyword | searches | clicks | CTR | competition |
|---|---|---|---|---|
| preschool worksheets | 1,200 | 1,245 | 104% | 66,040 | <- big, not in any tag yet
| kindergarten worksheets | 221 | 195 | 88% | 41,640 | (23 chars: title only, too long for a tag)
| tracing worksheets | 128 | 183 | 143% | 29,273 | <- low comp, high CTR
| animal coloring pages | 22 | <20 | 91% | 64,573 |
| preschool activities | <20 | <20 | - | 144,367 | (dead)
From audits: preschool curriculum 1,283 (comp 15,459), kids coloring book 707 (147,364), toddler worksheets 107, preschool printable 108, farm animals 171, sight words 40, kindergarten math 24.
Long-tails seen (no volume yet): christmas tracing worksheets, shape tracing worksheets, preschool tracing worksheets, farm animal coloring pages.

Audits (5/5): all grade A, 0 sales, ~4-5 views each, attributes missing on all.
AI Listing Helper (1/1): used on shapes (weakest tags: 12/13 tags ~0 searches). Its ideas: toddler worksheets, preschool shapes; rejected "educational toys" (not accurate for a PDF).

Proposals P1-P6: APPROVED+APPLIED 2026-10-24 (Mohamed: "موافق على الكل"), published in Shop Manager and re-checked in the editor:
P1 numbers 4599341653
  title "Numbers 1-20 Tracing Worksheets, Count, Color & Trace Math Book (PDF)"
  -> "Number Tracing Worksheets 1-20, Preschool Worksheets Printable, Count Color and Trace Math Book Ages 3-5, Kindergarten Math PDF" (127)
  tags: -numbers 1 20, -trace numbers; +preschool worksheets, +tracing worksheets
P2 shapes 4599342777
  title "Preschool Shapes and Colors Activity Book, Trace and Color Learning (PDF Download)"
  -> "Shapes and Colors Worksheets for Toddlers and Preschool, Tracing Worksheets Ages 2-5, Learn 12 Shapes and 11 Colors Printable PDF" (129)
  tags: -colors worksheets, -shape tracing, -shapes coloring, -2 year old activity; +toddler worksheets, +tracing worksheets, +preschool worksheets, +preschool shapes
P3 preschool 4599368748
  title "Preschool Workbook Printable, Letters Numbers Shapes Colors (PDF Download)"
  -> "Preschool Worksheets Printable, Preschool Workbook 3-in-1 Ages 3-5, Letters Numbers Shapes Colors Tracing, Pre K Curriculum PDF" (127)
  tags: -busy book pages, -learning binder; +preschool worksheets, +tracing worksheets
P4 animals 4599346493
  title "Jumbo Animal Coloring Book for Toddlers, 60 Big & Easy Pages (PDF Download)"
  -> "Kids Coloring Book Animals, Jumbo Animal Coloring Pages for Toddlers Ages 2-5, 60 Big Easy Farm Safari Ocean Forest Pets PDF" (124)
  tags: -coloring pages kids; +kids coloring pages
P5 kindergarten 4599372316
  title "Kindergarten Activity Book Printable, 75 Worksheets, Mazes, Tracing, Counting (PDF)"
  -> "Kindergarten Worksheets Printable, Kindergarten Activity Book Ages 4-6, 75 Pages Mazes Tracing Counting Sight Words PDF" (119)
  tags: -kinder printable, -homeschool kinder, -summer workbook; +tracing worksheets, +kindergarten math, +preschool worksheets
P6 all 5: fill any attributes Etsy offers in the editor (eRank flags "attributes missing").
  Applied: only Occasion + Holiday are offered. Occasion = "Back to school" set on numbers, shapes, preschool, kindergarten. Animals: no accurate option, left empty. Holiday left empty on all (not holiday products).
No PENDING proposals left.
Idea: $2.99 "Christmas Preschool Worksheets" mini pack (tracing + counting, Christmas theme) for preschool worksheets 1,200 + preschool christmas 191.

Audit rotation (next up): abc 4599362140, dinosaurs, vehicles, unicorns, scissors.

## 2026-10-25 (scheduled run)
Keyword lookups (5/5, Etsy US, Sep-2026 data) - all weak on Etsy right now:
| keyword | searches | CTR | competition | note |
|---|---|---|---|---|
| christmas worksheets | <20 | - | 9,977 | trend shows Nov-Dec spike; long-tails: preschool/kindergarten christmas worksheets |
| alphabet tracing | <20 | <20% | 18,580 | Google 4,400/mo |
| dinosaur coloring pages | <20 | <20% | 5,742 | Google 40,500/mo (23 chars, title only) |
| unicorn coloring pages | <20 | - | 5,956 | |
| scissor skills | <20 | - | 3,248 | long-tails: christmas/winter scissor skills |
From audits / AI helper: abc coloring pages 100 (comp 9,900, 93% CTR) <- best find; alphabet worksheets 28 (118%); fine motor skills 45 (142%);
dragon coloring 21 (129%); unicorn birthday 105 (not used: buyers want party decor); coloring sheets 197; coloring book pdf 21 (95%); fire truck coloring comp only 171.

Audits (5/5): abc, dinosaurs, vehicles, unicorns, scissors. All 0 sales, 4-5 views, attributes missing.
AI Listing Helper (1/1): vehicles (weakest: 11/13 tags ~0 searches). Used: coloring book pdf, fire truck coloring, easy coloring book. Its titles ignored (colon style, weaker lead keyword).

PENDING proposals (sent to Mohamed 2026-10-25):
P1 abc 4599362140
  title "ABC Coloring & Tracing Book for Kids, Letter A-Z Worksheets (PDF Download)"
  -> "ABC Coloring Pages for Kids, Alphabet Worksheets Printable, Letter Tracing A-Z Ages 3-5, Preschool Coloring Book PDF" (116)
  tags: -kindergarten prep, -homeschool alphabet, -learn to write, -busy book pages; +preschool worksheets, +tracing worksheets, +kids coloring pages, +coloring sheets
P2 dinosaurs 4599373502
  title "Dinosaur Coloring Book for Kids, 24 Big Friendly Dinosaurs (PDF Download)"
  -> "Dinosaur Coloring Pages for Kids, Dinosaur Coloring Book Printable, 24 Big Easy Dinos, T-Rex Triceratops Ages 3-6 PDF" (117)
  tags: -dino printable, -boys coloring; +coloring book pdf, +easy coloring book
P3 vehicles 4599374544
  title "Trucks Trains Planes Coloring Book for Toddlers (PDF Download)"
  -> "Truck Coloring Pages for Toddlers, Vehicle Coloring Book Printable, 24 Big Easy Trucks Trains Planes Fire Truck Ages 2-5 PDF" (124)
  tags: -boys coloring, -digger coloring, -construction party; +coloring book pdf, +fire truck coloring, +easy coloring book
P4 unicorns 4599351423
  title "Unicorns & Magical Friends Coloring Book, Dragons, Fairies, Castles (PDF Download)"
  -> "Unicorn Coloring Pages for Kids, Unicorn Coloring Book Printable, 24 Magical Pages Dragons Fairies Castles Rainbows Ages 3-6 PDF" (128)
  tags: -girls coloring, -magical coloring; +coloring book pdf, +easy coloring book
P5 scissors 4599352519
  title "Scissor Skills Activity Book, Cut & Paste for Toddlers (Ages 3-5) (PDF)"
  -> "Scissor Skills Worksheets for Preschool, Cutting Practice Activity Book Ages 3-5, Cut and Paste Fine Motor Skills Printable PDF" (127)
  tags: -ot activities (eRank flags typo), -homeschool preschool; +preschool worksheets, +toddler worksheets
P6 all 5: Occasion attribute (only option Etsy offers): "Back to school" on abc + scissors; leave dinosaurs/vehicles/unicorns empty (no accurate option).
Idea: $1.99-2.99 "Christmas Scissor Skills" mini pack (cutting lines + Christmas shapes) - eRank shows christmas/winter scissor skills long-tails, comp only 3,248.

Audit rotation (next up): sightwords 4599377768, handwriting, cursive, space, feelings.
