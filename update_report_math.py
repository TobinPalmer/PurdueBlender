"""
Update purdue_digital_twin_report.md with Mathematical Sciences Building (MATH - 1967)
- Update Executive Summary with MATH details and new totals (15,269 objects / 86 collections)
- Insert Section 7: Mathematical Sciences Building (MATH - 1967) & Oval Drive / University Street Concourse
- Prepend Cam_92 through Cam_96 to Section 17 (Master Camera Inspection Gallery)
"""

import re

REPORT_PATH = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25\purdue_digital_twin_report.md"

def update_report():
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update Object Count in Header
    content = re.sub(
        r"\*\*Total Scene Objects:\*\* \d+ objects across \d+ collections",
        "**Total Scene Objects:** 15,269 objects across 86 collections",
        content
    )

    # 2. Update Executive Summary list
    math_exec_summary = """1. **Mathematical Sciences Building (MATH - 1967) & University Street / Oval Drive Concourse**: Modeled across **805 high-detail objects** in collections `60_Math_Sciences_Exterior` (150 objects), `61_Math_Sciences_Interiors` (593 objects), and `62_Math_Sciences_Plaza_and_Site` (62 objects), plus dedicated inspection cameras `Cam_92` through `Cam_96` in `00_Inspection_Cameras` (**810 total objects**). Sited at georeferenced coordinates $X = -180.62\\text{m}, Y = -127.29\\text{m}, Z = 0.0\\text{m}$ along University Street and Oval Drive, directly opposite Class of 1950 Lecture Hall ($37.3\\text{m} \\times 68.2\\text{m}$, height $36.3\\text{m}$ roof parapet, $42.2\\text{m}$ antenna mast). Features Scholer Corporation mid-century Brutalist architecture with 10 full stories, four monumental Purdue Red Brick & Bedford Limestone corner stair towers ($33.3\\text{m}$), open ground-floor pilotis colonnade with 14 colossal board-formed concrete columns ($1.4\\text{m} \\times 1.2\\text{m} \\times 4.0\\text{m}$) creating the famous pedestrian "bridge" breezeway, recessed ground-floor glass curtain wall, entrance canopies with 3D Old Gold lettering (`"MATHEMATICAL SCIENCES BUILDING"`) and numerals (`"150"`), and long East & West facades defined by an authentic 23-column precast concrete solar fin waffle grid across all 9 upper stories with deeply recessed solar ribbon glass. Completely fitted with three photorealistic interior destinations elevated on impermeable foundation slabs: **MATH 175 Major Tiered Lecture Hall** (8 stepped semi-circular risers in navy carpet, curved oak desks, navy task chairs, oak stage dais, smart podium with gold Purdue seal and mic, quadruple sliding green porcelain blackboards with illuminated mathematical derivations ($e^{i\\pi}+1=0$, $\\zeta(s)$, Navier-Stokes, calculus), and dual 120" projection screens); the **Mathematical Sciences Library & Math Resource Room** (Floor 3 / Room 311, double-height academic study hall with polished cream terrazzo floor, collaborative honey-oak study tables with green-glass banker's lamps, open laptops, dark oak chairs, multiple double-sided mahogany book stacks loaded with multi-colored books, and ribbon window daylight); and the **10th-Floor Faculty Colloquium Sky Lounge & Library** (Floor 10, dark walnut parquet, rose-burgundy Persian area rug, monumental 16-seat mahogany conference table, 16 executive burgundy leather swivel armchairs, meeting folios and laptops, suspended 8-arm brass chandelier, colloquium proof blackboard, Chesterfield leather lounge sofa, coffee bar credenza with espresso machine, and 360-degree panoramic ribbon windows overlooking Memorial Mall, Bell Tower, and Elliott Hall). Integrated with the East sunken outdoor courtyard with 5 stepped concrete terraces, University Street arrival plaza with brick accents, limestone planters with boxwoods, teak benches, 12 Sheffield bike racks, and Victorian lantern posts (**Certified Gold Standard Pass 94.0/100, 9.4/10**).
2. **Purdue Armory"""

    content = content.replace("1. **Purdue Armory", math_exec_summary, 1)

    # 3. Insert Section 7 for MATH
    math_section = """

## 7. Mathematical Sciences Building (MATH - 1967) & University Street / Oval Drive Concourse

**Digital Twin Coordinates:** Center at $X = -180.62\\text{m}, Y = -127.29\\text{m}$ (Elevation $Z = 0.0\\text{m}$)  
**Historical Background:** Completed in 1967; designed by the Scholer Corporation. Serves as the central 10-story high-rise headquarters for the Department of Mathematics, Department of Statistics, and College of Science administration. Prominently sited along University Street and Oval Drive, it functions as a primary academic crossroads on campus, famous for its open ground-floor breezeway colonnade (giving rise to the long-standing campus legend that it is legally classified as a "bridge" over pedestrian walkways).  
**Georeferenced Footprint:** $37.3\\text{m} \\times 68.2\\text{m}$ ($X \\in [-199.27\\text{m}, -161.97\\text{m}]$, $Y \\in [-161.37\\text{m}, -93.21\\text{m}]$), height $33.0\\text{m}$ main parapet, $36.3\\text{m}$ rooftop mechanical penthouse, $42.2\\text{m}$ communications mast.  
**Collections:** `60_Math_Sciences_Exterior` (150 objects), `61_Math_Sciences_Interiors` (593 objects), `62_Math_Sciences_Plaza_and_Site` (62 objects) — **Total MATH Objects: 805 objects** (+ 5 inspection cameras `Cam_92` through `Cam_96` in `00_Inspection_Cameras` = **810 total objects**).  
**Evaluation Score:** **94.0 / 100 (Certified Gold Standard Exemplar — Grade: A / 9.4 out of 10)**  

### A. Progressive Architecture Audit & Multi-Pass Score Trajectory

```mermaid
xychart-beta
    title "Mathematical Sciences Building Progression Score Trajectory Across 3 Attempts"
    x-axis ["Attempt 1 (Prior Box)", "Attempt 2 (Initial Build)", "Attempt 3 (Gold Standard Exemplar)"]
    y-axis "Total Score (/100)" 0 --> 100
    bar [18, 73, 94]
    line [18, 73, 94]
```

| Evaluation Dimension | Max Points | Attempt 1 (Prior Box) | Attempt 2 (Initial Build) | Attempt 3 (Gold Exemplar) | Cumulative Delta | Official Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Massing & Proportions** | 20 | 6.0 | 17.0 | **19.0** | $+13.0$ | Exemplar |
| **2. Architectural Details & Fenestration** | 20 | 1.0 | 15.0 | **19.0** | $+18.0$ | Exemplar |
| **3. Material & Texture Fidelity** | 20 | 2.0 | 14.0 | **18.0** | $+16.0$ | Exemplar |
| **4. Interior / Circulation Realism** | 20 | 1.0 | 13.0 | **19.0** | $+18.0$ | Exemplar |
| **5. Environmental & Site Integration** | 20 | 8.0 | 14.0 | **19.0** | $+11.0$ | Exemplar |
| **Total Composite Score** | **100** | **18.0 / 100** | **73.0 / 100** | **94.0 / 100** | **$+76.0$** | **GOLD STANDARD EXEMPLAR (9.4 / 10)** |

### B. Visual Progression Carousel

````carousel
![Cam 92: Hero South-West University Street Arrival — 10-Story Tower, 23-Column Precast Waffle Grid, Entrance Canopy, Double Doors, and Pilotis Colonnade](math_cam92_universityst_hero.png)
<!-- slide -->
![Cam 93: MATH 175 Major Tiered Lecture Hall — Center Aisle View, 8 Stepped Risers, Smart Podium, and Quadruple Blackboards with Illuminated Formulas](math_cam93_lecturehall_175.png)
<!-- slide -->
![Cam 94: Mathematical Sciences Library (Floor 3) — Terrazzo Study Promenade, Honey Oak Tables, Glowing Green Banker's Lamps, Laptops, and Book Stacks](math_cam94_library_study.png)
<!-- slide -->
![Cam 95: 10th-Floor Faculty Colloquium Sky Lounge — 16-Seat Mahogany Table, Brass Chandelier, Burgundy Leather Chairs, Proof Board, and Panoramic Ribbon Windows](math_cam95_10thfloor_skylounge.png)
<!-- slide -->
![Cam 96: Precinct Aerial Context — Full 10-Story Envelope, East Waffle Grid, Rooftop Penthouse, Antenna Mast, Sunken Plaza, and Oval Drive Integration](math_cam96_precinct_aerial.png)
````

### C. Detailed Architectural Implementation Analysis

1. **Precast Concrete & Brick High-Rise Exterior (`60_Math_Sciences_Exterior` - 150 objects)**:
   - **Monumental High-Rise Envelope**: Footprint $37.3\\text{m} \\times 68.2\\text{m}$ rising 10 full stories ($Z = 0.0\\text{m}$ to $33.0\\text{m}$), topped with a $3.3\\text{m}$ mechanical penthouse ($Z = 33.0\\text{m}$ to $36.3\\text{m}$) and communications antenna mast ($Z = 36.3\\text{m}$ to $42.2\\text{m}$).
   - **Precast Concrete Window Waffle Grid**: 23 vertical precast concrete solar fins / shadow box ribs spaced every $2.4\\text{m}$ along the long East and West facades ($54.4\\text{m}$ span), integrated with 10 continuous horizontal concrete spandrel beams and deeply recessed solar ribbon glass panes across Floors 2 to 10.
   - **Four Brick & Limestone Corner Towers**: Monumental utility and stair towers at NE, NW, SE, SW corners ($5.2\\text{m} \\times 6.8\\text{m} \\times 33.3\\text{m}$) in textured Purdue Red Brick masonry with Indiana Bedford Limestone water table plinths and coping parapet caps.
   - **Open Ground-Floor Pilotis Colonnade**: 14 massive board-formed concrete pilotis ($1.4\\text{m} \\times 1.2\\text{m} \\times 4.0\\text{m}$) framing an open pedestrian walkway underneath the 9-story tower structure.
   - **Entrance Portals & 3D Signage**: Ground-floor curtain wall recessed $3.2\\text{m}$ with dark bronze mullions, double glass entrance doors with bronze frames and gold pull handles, limestone entrance canopies on University St (West) and Oval Drive (East) carrying 3D Old Gold building lettering (`"MATHEMATICAL SCIENCES BUILDING"`) and numerals (`"150"`).
   - **Rooftop Mechanical Penthouse**: $20.0\\text{m} \\times 44.0\\text{m} \\times 3.3\\text{m}$ brick and limestone enclosure with dark bronze HVAC ventilation louvers and gravel roof ballast membrane.

2. **Photorealistic Functional Interiors (`61_Math_Sciences_Interiors` - 593 objects)**:
   - **MATH 175 Major Tiered Lecture Hall (Ground Floor, $Z = 0.42\\text{m}$ to $4.35\\text{m}$)**:
     * 8 stepped semi-circular seating riser tiers finished in high-traffic navy pile carpet.
     * 8 continuous concentric rows of curved laminate student desks with bronze leg stanchions.
     * Articulating navy student task chairs with contoured backrests.
     * Front lecture stage dais in tongue-and-groove honey oak ($13.0\\text{m} \\times 3.0\\text{m} \\times 0.36\\text{m}$).
     * Solid walnut smart instructor podium with gooseneck microphone and gold Purdue seal medallion.
     * Quadruple sliding green porcelain blackboard system ($11.0\\text{m} \\times 2.2\\text{m}$) with oak frame and 4 dedicated high-intensity spotlight wash fixtures.
     * Emissive chalk mathematical derivations: Euler's identity $e^{i\\pi}+1=0$, Riemann zeta function $\\zeta(s)=\\sum n^{-s}$, Navier-Stokes fluid equations $\\rho(\\partial_t v + v\\cdot\\nabla v)=-\\nabla p+\\mu\\nabla^2 v$, and fundamental theorem of calculus $\\int_a^b f'(x)dx = f(b)-f(a)$.
     * Dual 120-inch motorized projection screens mounted above the blackboard.
   - **Mathematical Sciences Library & Math Resource Room (Floor 3, $Z = 10.62\\text{m}$ to $13.75\\text{m}$)**:
     * Polished cream terrazzo flooring with charcoal border trim.
     * Collaborative study tables in solid honey oak with edge banding, glowing green-glass banker's desk lamps ($280\\text{W}$ warm light), open student laptops with emissive screens, and dark oak task chairs.
     * 4 double-sided mahogany book stacks loaded with multi-colored mathematical monographs, bound journals, and brass aisle tags.
     * Floor-to-ceiling ribbon windows overlooking Memorial Mall and University Street with natural daylight reflections.
   - **10th-Floor Faculty Colloquium Sky Lounge & Library (Floor 10, $Z = 29.82\\text{m}$ to $32.95\\text{m}$)**:
     * Polished dark walnut parquet flooring with dark walnut wainscoting.
     * Rose-burgundy Persian area rug beneath a monumental 16-seat solid mahogany conference table ($3.4\\text{m} \\times 9.8\\text{m}$) on 3 fluted pedestal bases.
     * 16 executive burgundy leather swivel armchairs.
     * Leather meeting portfolios, gold executive pens, and laptops on the table.
     * Suspended 8-arm brass ring chandelier casting warm amber illumination ($3200\\text{K}$).
     * Colloquium proof blackboard on the North feature wall: `"FACULTY COLLOQUIUM: RIEMANN HYPOTHESIS & SPECTRAL THEORY"`.
     * Chesterfield leather lounge sofa, walnut coffee table, and coffee bar credenza with espresso machine.
     * Floor-to-ceiling 360-degree panoramic ribbon windows with unobstructed vistas of Memorial Mall, Purdue Bell Tower, and Elliott Hall.
   - **Impermeable Elevation**: All interior floor slabs are elevated to $Z = 0.42\\text{m}$, $Z = 10.62\\text{m}$, and $Z = 29.82\\text{m}$, completely clearing terrain and outdoor sidewalks.

3. **Civic Hardscape & Site Integration (`62_Math_Sciences_Plaza_and_Site` - 62 objects)**:
   - **Sunken Outdoor Courtyard / Plaza (East side)**: Descends from $Z = 0.0\\text{m}$ to $Z = -2.15\\text{m}$ with concrete retaining walls, 5 stepped seating terraces ($0.35\\text{m}$ risers), and direct approach to the lower level.
   - **Ground-Level Arrival Concourse**: Granite and red brick paved arrival plazas connecting University Street on the west ($11.0\\text{m} \\times 64.0\\text{m}$) and Oval Drive on the east ($10.0\\text{m} \\times 26.0\\text{m}$).
   - Raised Bedford limestone planter beds populated with evergreen boxwood shrubs.
   - Campus teak wood park benches, bank of 12 Sheffield bronze bicycle parking racks, and 4 Victorian cast-iron lantern posts with warm point light luminaires.

---
"""

    # We will insert math_section right before "## 7. Guy J. \"Red\" Mackey Arena"
    target = '## 7. Guy J. "Red" Mackey Arena'
    if target in content:
        content = content.replace(target, math_section + '\n## 8. Guy J. "Red" Mackey Arena', 1)
        # Renumber subsequent headers
        content = content.replace("## 8. Neil Armstrong Hall", "## 9. Neil Armstrong Hall", 1)
        content = content.replace("## 9. University Hall", "## 10. University Hall", 1)
        content = content.replace("## 10. Edward C. Elliott Hall", "## 11. Edward C. Elliott Hall", 1)
        content = content.replace("## 11. Wilmeth Active Learning Center", "## 12. Wilmeth Active Learning Center", 1)
        content = content.replace("## 12. Frieda Parker Hall", "## 13. Frieda Parker Hall", 1)
        content = content.replace("## 13. Winifred Parker Hall", "## 14. Winifred Parker Hall", 1)
        content = content.replace("## 14. Ross-Ade Stadium", "## 15. Ross-Ade Stadium", 1)
        content = content.replace("## 15. West Campus Residential", "## 16. West Campus Residential", 1)
        content = content.replace("## 16. Purdue Engineering Fountain", "## 17. Purdue Engineering Fountain", 1)
        content = content.replace("## 17. Master Camera Inspection Gallery", "## 18. Master Camera Inspection Gallery", 1)

    # 4. Prepend Cam_92 through Cam_96 to Master Camera Inspection Gallery
    math_cams_table = """| Camera Identifier | Coordinates $(X, Y, Z)$ | Target Angle & View | Key Landmark & Architectural Features Framed |
| :--- | :--- | :--- | :--- |
| **`Cam_92_MATH_UniversitySt_Hero`** | $(-238.0, -145.0, 11.5)$ | Facing North-East ($83^\\circ$ pitch) | Hero University Street Arrival: Full 10-story tower, 23-column precast concrete solar fin waffle grid across West facade, double glass entrance doors with bronze hardware, entrance canopy with 3D Old Gold lettering (`"MATHEMATICAL SCIENCES BUILDING"`) and numerals (`"150"`), concrete pilotis colonnade, sidewalks, benches, bike racks, and lanterns. |
| **`Cam_93_MATH_175_LectureHall_Interior`** | $(-185.62, -137.0, 2.85)$ | Facing South down center aisle ($97^\\circ$ pitch) | MATH 175 Major Tiered Lecture Hall: Center aisle perspective, 8 stepped seating riser tiers in navy carpet, concentric curved student desks, navy task chairs, oak stage dais, smart podium with microphone, and quadruple sliding green porcelain blackboards with illuminated derivations ($e^{i\\pi}+1=0$, $\\zeta(s)$, Navier-Stokes, calculus). |
| **`Cam_94_MATH_Library_Study_Interior`** | $(-181.0, -121.5, 12.3)$ | Facing North-Northwest ($78^\\circ$ pitch) | Mathematical Sciences Library (Floor 3 / Room 311): Open study promenade, collaborative oak tables with glowing green-glass banker's lamps, open laptops with emissive screens, task chairs, multiple double-sided mahogany book stacks loaded with multi-colored books and brass tags, terrazzo floor reflections, and ribbon window daylight. |
| **`Cam_95_MATH_10thFloor_SkyLounge_Interior`** | $(-185.12, -133.79, 31.2)$ | Facing North-East ($75^\\circ$ pitch) | 10th-Floor Faculty Colloquium Sky Lounge: Monumental 16-seat solid mahogany conference table, suspended 8-arm brass chandelier, executive burgundy leather swivel armchairs, meeting portfolios and laptops, rose-burgundy Persian area rug, colloquium blackboard (`"FACULTY COLLOQUIUM: RIEMANN HYPOTHESIS & SPECTRAL THEORY"`), and panoramic ribbon windows overlooking campus. |
| **`Cam_96_MATH_Precinct_Aerial`** | $(-115.0, -210.0, 68.0)$ | Facing North-West ($56^\\circ$ pitch) | Precinct Aerial Context Overview: Complete 10-story tower envelope, East facade precast concrete waffle grid, mechanical rooftop penthouse with bronze louvers and antenna mast, sunken outdoor courtyard with 5 stepped concrete terraces, Oval Drive loop, and campus connectivity to CL50, Armory, and Beering Hall. |"""

    content = content.replace(
        "| Camera Identifier | Coordinates $(X, Y, Z)$ | Target Angle & View | Key Landmark & Architectural Features Framed |\n| :--- | :--- | :--- | :--- |",
        math_cams_table,
        1
    )

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("Master Report updated successfully with Mathematical Sciences Building (MATH)!")

if __name__ == "__main__":
    update_report()
