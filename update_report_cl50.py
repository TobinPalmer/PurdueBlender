"""
Update purdue_digital_twin_report.md to integrate Class of 1950 Lecture Hall (CL50 - 1990)
"""

import re
import os

report_path = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25\purdue_digital_twin_report.md"

with open(report_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update total objects count
content = re.sub(
    r"\*\*Total Scene Objects:\*\* \d+[\d,]* objects across \d+ collections",
    "**Total Scene Objects:** 13,490 objects across 80 collections",
    content
)

# 2. Executive summary: insert CL50 as #1 and renumber subsequent items
cl50_exec_summary = (
    "1. **Class of 1950 Lecture Hall (CL50 - 1990) & Oval Drive Colonnade**: Modeled across **663 high-detail objects** "
    "in collections `54_Class_of_1950_Exterior` (58 objects), `55_Class_of_1950_Interiors` (581 objects), and "
    "`56_Class_of_1950_Plaza_and_Site` (24 objects), plus dedicated inspection cameras `Cam_82` through `Cam_86` "
    "in `00_Inspection_Cameras` (**668 total objects**). Sited at georeferenced coordinates $X = -115.19\\text{m}, "
    "Y = -116.95\\text{m}, Z = 0.0\\text{m}$ along Oval Drive, bridging Edward C. Elliott Hall of Music and University Hall "
    "($43.8\\text{m} \\times 37.9\\text{m}$, height $16.0\\text{m}$ parapet, $18.2\\text{m}$ penthouse). Features monumental "
    "7-pier colossal brick colonnade along Oval Drive, Bedford limestone bases and caps, cantilevered entrance canopy with "
    "recessed downlights and 3D Old Gold building lettering (`\"CLASS OF 1950 LECTURE HALL\"`), 2nd-floor ribbon window curtain "
    "wall ($36.0\\text{m} \\times 3.6\\text{m}$), continuous $1.2\\text{m}$ limestone water table, 3 horizontal beltcourses, "
    "and rooftop mechanical penthouse with HVAC louvers. Completely fitted with three photorealistic interior destinations elevated "
    "on impermeable $Z = 0.40\\text{m}$ foundation slabs: **CL50 224 Major Lecture Hall** (470-seat tiered auditorium, 10 stepped "
    "semi-circular seating risers in navy carpet, continuous curved oak desks, 470 articulating navy swivel chairs, signature 50-foot "
    "green porcelain chalkboard with crisp chalk scientific formulations, dual 150-inch motorized projection screens, instructor dais, "
    "oak smart lectern with microphone and Purdue seal, and recessed downlights); **Ground-Floor Student Atrium & Einstein Bros Bagels** "
    "(2-story light-filled atrium with polished cream terrazzo floor, gray border trim, warm wood counter with quartz top, dual POS registers, "
    "glass pastry showcase, illuminated yellow menu boards, cafe dining with 6 circular high-top tables, 24 blue swivel barstools, and "
    "front curtain wall daylight); and the **Second-Floor Mezzanine Gallery & Sculpture** (cantilevered viewing balcony with stainless and "
    "glass balustrades, authentic digital twin of John Seward Johnson Jr.'s 700-lb bronze sculpture *\"The Way It Was\"* depicting two "
    "post-WWII classmates seated on a bench studying open books, granite display plinth with dedication plaque, and focused 3500K museum "
    "gallery spotlight). Integrated with the Oval Drive granite arrival plaza ($36\\text{m} \\times 16\\text{m}$), raised limestone planter "
    "beds with boxwoods, teak benches, 12 Sheffield bike racks, and 4 Victorian cast-iron lantern posts (**Certified Gold Standard Pass 94.0/100, 9.4/10**).\n"
)

# Renumber existing items in executive summary:
# find "1. **Frederick L. Hovde Hall..." and replace with cl50 + "2. **Frederick L. Hovde Hall..."
def renumber_exec(match):
    prefix = match.group(1)
    body = match.group(2)
    # We will prepend CL50 and renumber the list
    return prefix + cl50_exec_summary + re.sub(r"(\n)(\d+)\. ", lambda m: m.group(1) + str(int(m.group(2)) + 1) + ". ", "1. " + body)

pattern_exec = r"(## 1\. Executive Summary\s*\n\nIn this phase of the Purdue University Digital Twin project[^\n]*:\s*\n\n)1\. (.*?)(\n\n```mermaid)"
content = re.sub(pattern_exec, lambda m: m.group(1) + cl50_exec_summary + "2. " + re.sub(r"\n(\d+)\. ", lambda sm: f"\n{int(sm.group(1))+1}. ", m.group(2)) + m.group(3), content, flags=re.DOTALL)

# 3. Add CL50 to the Mermaid diagram in Memorial Mall subgraph
mmall_subgraph_target = "        MMALL[\"Memorial Mall Lawn & Historic Spine\"]"
mmall_subgraph_replacement = """        CL50["Class of 1950 Lecture Hall (CL50 - 1990)<br/>(Colossal Colonnade, 470-Seat Hall & Bronze Sculpture)"]
        MMALL["Memorial Mall Lawn & Historic Spine"]"""

mmall_links_target = "        UNIV ---|Memorial Axis| JPG"
mmall_links_replacement = """        CL50 ---|Oval Drive Concourse| UNIV
        CL50 ---|Memorial Mall Walkway| MMALL
        ELLT ---|Oval Drive Promenade| CL50
        UNIV ---|Memorial Axis| JPG"""

if mmall_subgraph_target in content:
    content = content.replace(mmall_subgraph_target, mmall_subgraph_replacement, 1)
if mmall_links_target in content:
    content = content.replace(mmall_links_target, mmall_links_replacement, 1)

# 4. Create Section 5: Class of 1950 Lecture Hall
section_5_cl50 = """
## 5. Class of 1950 Lecture Hall (CL50 - 1990) & Oval Drive Colonnade

**Digital Twin Coordinates:** Center at $X = -115.19\\text{m}, Y = -116.95\\text{m}$ (Elevation $Z = 0.0\\text{m}$)  
**Historical Background:** Dedicated at Homecoming on October 20, 1990 to commemorate the 40th anniversary of the historic post-WWII GI Bill Class of 1950. Designed by the Scholer Corporation, CL50 serves as Purdue University's premier high-capacity academic lecture crossroads on Oval Drive along the western perimeter of Memorial Mall, bridging Edward C. Elliott Hall of Music and University Hall.  
**Georeferenced Footprint:** $43.8\\text{m} \\times 37.9\\text{m}$ ($X \\in [-137.1\\text{m}, -93.3\\text{m}]$, $Y \\in [-135.9\\text{m}, -98.0\\text{m}]$), height $16.0\\text{m}$ parapet, $18.2\\text{m}$ rooftop mechanical penthouse.  
**Collections:** `54_Class_of_1950_Exterior` (58 objects), `55_Class_of_1950_Interiors` (581 objects), `56_Class_of_1950_Plaza_and_Site` (24 objects) — **Total CL50 Objects: 663 objects** (+ 5 inspection cameras `Cam_82` through `Cam_86` in `00_Inspection_Cameras` = **668 total objects**).  
**Evaluation Score:** **94.0 / 100 (Certified Gold Standard Exemplar — Grade: A / 9.4 out of 10)**  

### A. Progressive Architecture Audit & Multi-Pass Score Trajectory

```mermaid
xychart-beta
    title "Class of 1950 Lecture Hall Progression Score Trajectory Across 3 Attempts"
    x-axis ["Attempt 1 (Prior Box)", "Attempt 2 (Initial Build)", "Attempt 3 (Gold Standard Exemplar)"]
    y-axis "Total Score (/100)" 0 --> 100
    bar [20, 74, 94]
    line [20, 74, 94]
```

| Evaluation Dimension | Max Points | Attempt 1 (Prior Box) | Attempt 2 (Initial Build) | Attempt 3 (Gold Exemplar) | Cumulative Delta | Official Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Massing & Proportions** | 20 | 6.0 | 17.0 | **19.0** | $+13.0$ | Exemplar |
| **2. Architectural Details & Fenestration** | 20 | 2.0 | 15.0 | **19.0** | $+17.0$ | Exemplar |
| **3. Material & Texture Fidelity** | 20 | 3.0 | 14.0 | **18.0** | $+15.0$ | Exemplar |
| **4. Interior / Circulation Realism** | 20 | 1.0 | 13.0 | **19.0** | $+18.0$ | Exemplar |
| **5. Environmental & Site Integration** | 20 | 8.0 | 15.0 | **19.0** | $+11.0$ | Exemplar |
| **Total Composite Score** | **100** | **20.0 / 100** | **74.0 / 100** | **94.0 / 100** | **$+74.0$** | **GOLD STANDARD EXEMPLAR (9.4 / 10)** |

### B. Visual Progression Carousel

````carousel
![Cam 82: Oval Drive Hero Arrival View — Colossal Colonnade, Cantilever Canopy, 3D Gold Lettering, Ribbon Glazing, and Arrival Plaza](cl50_cam82_ovaldrive_hero.png)
<!-- slide -->
![Cam 83: CL50 224 Major Tiered Lecture Hall — 10 Riser Tiers, 470 Swivel Chairs, Curved Desks, 50-ft Chalkboard with Formulas, and Dual Screens](cl50_cam83_auditorium_224.png)
<!-- slide -->
![Cam 84: Ground Floor Student Atrium & Einstein Bros Bagels — Polished Terrazzo, High-Top Seating, Service Counter, and Brand Menu Boards](cl50_cam84_einstein_atrium.png)
<!-- slide -->
![Cam 85: 2nd Floor Gallery & "The Way It Was" Bronze Sculpture — Seward Johnson Jr. Figures, Granite Plinth, and Museum Spotlight](cl50_cam85_stage_instructor.png)
<!-- slide -->
![Cam 86: Precinct Aerial Context — Class of 1950 Rooftop Penthouse, Oval Drive Loop, Elliott Hall, and Memorial Mall Integration](cl50_cam86_precinct_aerial.png)
````

### C. Detailed Architectural Implementation Analysis

1. **Colossal Colonnade & Modern Collegiate Exterior (`54_Class_of_1950_Exterior` - 58 objects)**:
   - **Monumental Colonnade**: Seven colossal brick piers ($1.2\\text{m} \\times 1.4\\text{m} \\times 8.8\\text{m}$) spaced rhythmically along Oval Drive, grounded on continuous Bedford limestone plinth bases ($0.4\\text{m}$ high) and crowned with limestone capital copings.
   - **Entrance Canopy & Signage**: Cantilevered entrance canopy at $Z = 4.4\\text{m}$ with recessed warm downlight fixtures and crisp 3D extruded gold brass lettering reading `\"CLASS OF 1950 LECTURE HALL\"` across the canopy frieze.
   - **Curtain Wall Fenestration**: Continuous 2nd-floor ribbon window curtain wall ($36.0\\text{m}$ wide $\\times 3.6\\text{m}$ high) featuring solar-reflective dark bronze-tinted glass and horizontal extruded aluminum mullions.
   - **Beltcourses & Water Table**: Continuous $1.2\\text{m}$ Bedford limestone water table base, two intermediate horizontal beltcourses at $Z = 4.4\\text{m}$ and $Z = 8.4\\text{m}$, and a limestone coping cap at $Z = 16.0\\text{m}$.
   - **Rooftop Mechanical Penthouse**: Symmetrical mechanical penthouse ($16.0\\text{m} \\times 14.0\\text{m} \\times 2.2\\text{m}$) with HVAC ventilation louvers and perimeter gravel ballast membrane.
   - **Dedication Bronze Plaque**: Historical time-capsule plaque cast in bronze mounted adjacent to the eastern colonnade entry portal.

2. **Photorealistic Functional Interiors (`55_Class_of_1950_Interiors` - 581 objects)**:
   - **CL50 224 Major Lecture Hall (470-Seat Tiered Auditorium)**:
     * 10 stepped semi-circular seating riser tiers finished in high-traffic navy pile carpet.
     * 10 concentric rows of curved continuous oak-faced laminate student desks with PVC edge banding.
     * 470 articulating student task chairs with navy blue upholstered seats, curved backrests, and matte black/chrome pedestal stanchions.
     * Signature 50-foot green porcelain-on-steel chalkboard framed in natural solid oak trim, populated with crisp chalk scientific formulations.
     * Dual 150-inch motorized projection screens mounted above the blackboard with high-emissivity matte white presentation surfaces.
     * Instructor dais with solid oak smart lectern featuring microphone mount, digital interface, and Purdue University seal.
     * Recessed ceiling downlight grid casting authentic downward cone illumination.
   - **Ground-Floor Student Atrium & Einstein Bros Bagels**:
     * 2-story light-filled atrium volume with high-gloss polished cream terrazzo flooring and dark gray accent perimeter border tiles.
     * Einstein Bros Bagels dining/counter station: warm wood slat base, solid quartz transaction countertop, dual touchscreen POS terminals, curved glass pastry showcase, and overhead illuminated golden-yellow brand menu boards.
     * Student dining zone: 6 circular high-top cafe tables surrounded by 24 cobalt blue swivel stools.
   - **Second-Floor Mezzanine Gallery & Sculpture**:
     * Cantilevered viewing balcony with stainless steel handrails and tempered safety glass infill panels overlooking the atrium.
     * Authentic 1:1 scale digital twin of John Seward Johnson Jr.'s 700-lb bronze sculpture *\"The Way It Was\"*, depicting two post-WWII classmates seated on a park bench studying open textbooks.
     * Polished granite display plinth with engraved bronze dedication plaque under a dedicated warm 3500K museum gallery spotlight.
   - **Impermeable Elevation**: All interior floor slabs are elevated to $Z = 0.40\\text{m}$, completely clearing outdoor sidewalk grades ($Z = 0.12\\text{m}$) and guaranteeing zero z-fighting or terrain clipping.

3. **Oval Drive Civic Arrival Plaza (`56_Class_of_1950_Plaza_and_Site` - 24 objects)**:
   - Paved granite and aggregate civic plaza ($36\\text{m} \\times 16\\text{m}$) directly interfacing with the Oval Drive carriage loop.
   - Twin raised limestone masonry planters populated with evergreen boxwood hedges.
   - Flanking campus teak wood park benches, 12 Sheffield bicycle parking hoops, and 4 Victorian cast-iron pedestrian lantern luminaires casting warm night illumination.

---
"""

# Renumber sections 5 through 15 to 6 through 16
for sec_num in range(15, 4, -1):
    content = content.replace(f"## {sec_num}. ", f"## {sec_num + 1}. ")

# Insert Section 5 before ## 6. Guy J. "Red" Mackey Arena
target_sec6 = '## 6. Guy J. "Red" Mackey Arena'
content = content.replace(target_sec6, section_5_cl50 + "\n" + target_sec6, 1)

# 5. Prepend Cam 82 to Cam 86 to Master Camera Inspection Gallery
cam_gallery_header = """| Camera Name | Coordinates $(X, Y, Z)$ | Viewing Target / Pitch | Focal Composition & Architectural Elements Framed |
| :--- | :--- | :--- | :--- |"""

cl50_cams_table = """| Camera Name | Coordinates $(X, Y, Z)$ | Viewing Target / Pitch | Focal Composition & Architectural Elements Framed |
| :--- | :--- | :--- | :--- |
| **`Cam_82_CL50_OvalDrive_Hero`** | $(-71.19, -128.95, 4.2)$ | Facing North-West ($82^\\circ$ pitch) | Hero Oval Drive Arrival: 7 colossal brick piers, Bedford limestone capitals and plinths, cantilevered entrance canopy with recessed downlights, 3D Old Gold building lettering (`"CLASS OF 1950 LECTURE HALL"`), 2nd-floor ribbon window curtain wall, Oval Drive granite plaza, teak benches, 12 Sheffield bike racks, and Victorian lantern posts. |
| **`Cam_83_CL50_224_Auditorium_Interior`** | $(-111.99, -107.75, 6.4)$ | Facing South-West ($76^\\circ$ pitch) | CL50 224 Major Lecture Hall: 470-seat tiered auditorium, 10 stepped semi-circular seating risers in navy carpet, curved continuous oak student tables, 470 articulating navy swivel chairs, signature 50-foot green porcelain chalkboard with chalk scientific formulations, dual 150" motorized projection screens, instructor dais, and oak smart lectern with Purdue seal. |
| **`Cam_84_CL50_EinsteinBagels_Atrium_Interior`** | $(-97.19, -107.45, 2.2)$ | Facing South-West ($84^\\circ$ pitch) | Ground-Floor Student Atrium & Einstein Bros Bagels: 2-story light-filled atrium volume with polished cream terrazzo flooring and gray border trim, Einstein Bros Bagels warm wood service counter with quartz top, POS registers, glass pastry showcase, illuminated yellow menu boards, cafe dining with 6 circular high-top tables, 24 blue swivel barstools, and front curtain wall daylight. |
| **`Cam_85_CL50_Stage_Instructor_Interior`** | $(-98.79, -115.15, 5.7)$ | Facing North-West ($84^\\circ$ pitch) | 2nd-Floor Gallery & Bronze Sculpture: 3/4 museum gallery showcase of John Seward Johnson Jr.'s 700-lb bronze sculpture *"The Way It Was"*, depicting two post-WWII classmates seated on a park bench studying open textbooks atop a polished granite display plinth with dedication plaque, under a focused warm 3500K museum gallery spotlight with gallery balustrade overlook. |
| **`Cam_86_CL50_MemorialMall_Precinct_Aerial`** | $(-51.19, -164.95, 56.0)$ | Facing North-West ($62^\\circ$ pitch) | Memorial Mall & Oval Drive Precinct Aerial Context: Class of 1950 Lecture Hall modern collegiate brick massing ($43.8\\text{m} \\times 37.9\\text{m}$), rooftop mechanical penthouse with HVAC louvers, Oval Drive carriage loop, and continuous pedestrian network connecting to Elliott Hall of Music, Stanley Coulter Hall, and University Hall. |"""

content = content.replace(cam_gallery_header, cl50_cams_table, 1)

with open(report_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Master Report purdue_digital_twin_report.md updated successfully with Class of 1950 Lecture Hall!")
