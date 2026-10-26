import re

report_path = r'C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25\purdue_digital_twin_report.md'

with open(report_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update header object count
text = re.sub(r'\*\*Total Scene Objects:\*\* \d+ objects across \d+ collections',
              '**Total Scene Objects:** 12,182 objects across 74 collections', text)

# 2. Update Executive Summary text
stew_exec_summary = '''2. **Stewart Center (STEW - 1958) & Memorial Mall / State Street Gateway**: Modeled across **1,361 high-detail objects** in collections `48_Stewart_Center_Exterior` (401 objects), `49_Stewart_Center_Interiors` (923 objects), and `50_Stewart_Center_Plaza_and_Site` (37 objects), plus dedicated inspection cameras `Cam_72` through `Cam_76`. Sited at georeferenced coordinates $X = 83.89\\text{m}, Y = -257.14\\text{m}$ ($X \\in [16.5\\text{m}, 151.3\\text{m}]$, $Y \\in [-303.3\\text{m}, -211.0\\text{m}]$, width $134.8\\text{m}$, length $92.2\\text{m}$, main parapet $16.5\\text{m}$, stage fly loft $22.2\\text{m}$). Features Walter Scholer & Associates Mid-Century Modern Collegiate Civic architecture in textured Purdue Red Brick and Bedford Limestone dressings, continuous $1.5\\text{m}$ limestone water table, 4 horizontal beltcourses, South Monumental Colonnade Portico on State Street with 4 fluted piers ($1.4\\text{m} \\times 1.2\\text{m} \\times 9.0\\text{m}$), 2-story recessed glazed lobby entry with triple bronze doors, cantilevered canopy with recessed downlights and 3D gold building lettering (`"STEWART CENTER"`), vertical limestone fins framing 4 floors of ribbon windows, North Monumental Entrance facing Memorial Mall with 2-story glass curtain wall (`"BOILERMAKER STATION"`) and grand canopy, and East Concourse Portal linking directly to PMU West Courtyard. Completely fitted with 4 photorealistic interior destinations elevated on impermeable $Z = 0.40\\text{m}$ foundation slabs: **Loeb Playhouse** (1,011-seat proscenium theatre with dark oak stage deck at $Z = 1.6\\text{m}$, footlights, honey oak proscenium arch with Purdue seal, crimson velvet grand curtain with valance and gold tiebacks, 12 stepped curved seating riser terraces in navy carpet with aisle track lights, over 200 individual crimson velvet cushioned theatre seats with backrests and armrests, cantilevered balcony, and acoustic ceiling clouds with stage show lights); **HSSE Library** (double-height reading hall with honey oak study tables, glowing green glass banker's lamps, open textbooks, student laptops with emissive screens, task chairs, and 6 double-sided book stack ranges loaded with multi-colored book bindings and brass aisle markers); **Robert L. Ringel Gallery** (polished cream terrazzo flooring with sharp specular reflections, open exhibition promenade, 4 staggered minimalist white pedestals with bronze and marble modern art sculptures, and flanking exhibition walls with gold-framed canvas oil paintings and brass picture lights); and the **Main Civic Concourse & Boilermaker Station** (curved oak welcome desk, quartz countertop, digital information monitor, and gold directional signage). Integrated with the North Memorial Mall grand stepped terrace, lawn panels, seatwalls, teak benches, 3 Victorian lanterns, and South State Street brick plaza with 12 Sheffield bike racks (**Certified Gold Standard Pass 95.5/100, 9.6/10**).
'''

# Replace '2. **Guy J. "Red" Mackey Arena' with stewart center + renumbered mackey
text = text.replace('2. **Guy J. "Red" Mackey Arena', stew_exec_summary + '3. **Guy J. "Red" Mackey Arena')
# Renumber remaining executive items 3-16 to 4-17
for old_num in range(16, 2, -1):
    text = text.replace(f'{old_num}. **', f'{old_num+1}. **')

# 3. Insert Section 3 for Stewart Center and renumber existing sections
stewart_section = '''
## 3. Stewart Center (STEW - 1958) & Memorial Mall / State Street Gateway

**Digital Twin Coordinates:** Center at $X = 83.89\\text{m}, Y = -257.14\\text{m}$ (Elevation $Z = 0.0\\text{m}$)  
**Historical Background:** Dedicated in 1958, designed by Walter Scholer & Associates; named in honor of Vice President and Treasurer R.B. Stewart who orchestrated Purdue\\'s mid-century physical and academic expansion. Serves as Purdue\\'s central cultural, conference, and academic crossroads, unifying the historic South Gateway with Memorial Mall.  
**Georeferenced Footprint:** $134.8\\text{m} \\times 92.2\\text{m}$ ($X \\in [16.5\\text{m}, 151.3\\text{m}]$, $Y \\in [-303.3\\text{m}, -211.0\\text{m}]$), matching OpenStreetMap Way 24209587. Main parapet $16.5\\text{m}$, central Loeb Playhouse stage fly loft rising to $22.2\\text{m}$.  
**Collections:** `48_Stewart_Center_Exterior` (401 objects), `49_Stewart_Center_Interiors` (923 objects), `50_Stewart_Center_Plaza_and_Site` (37 objects) — **Total Stewart Center Objects: 1,361 objects** (+ 5 inspection cameras `Cam_72` through `Cam_76` in `00_Inspection_Cameras` = **1,366 objects**).  
**Evaluation Score:** **95.5 / 100 (Certified Gold Standard Exemplar — Grade: A+ / 9.6 out of 10)**  
**QA Audit Report:** [`stewart_center_architectural_evaluation_report.md`](file:///C:/Users/Tobin/.gemini/antigravity/brain/7d054314-203a-4c1a-bb2d-ad8b0fc54e25/stewart_center_architectural_evaluation_report.md)  

### A. Progressive Architecture Audit & Multi-Pass Score Trajectory

```mermaid
xychart-beta
    title "Stewart Center Progression Score Trajectory"
    x-axis ["Attempt 1 (Prior Box)", "Attempt 2 (Initial Build)", "Attempt 3 (Refinement)", "Attempt 4 (Gold Remediation)"]
    y-axis "Total Score (/100)" 0 --> 100
    bar [16, 71, 85, 96]
    line [16, 71, 85, 96]
```

| Evaluation Dimension | Max Points | Attempt 1 (Prior Box) | Attempt 2 (Initial Build) | Attempt 3 (Refinement) | Attempt 4 (Gold Remediation) | Cumulative Delta | Quality Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Massing & Proportions** | 20 | 6.0 | 15.5 | 18.0 | **19.5** | $+13.5$ | Exemplar |
| **2. Architectural Details & Fenestration** | 20 | 1.0 | 14.0 | 16.5 | **19.0** | $+18.0$ | Exemplar |
| **3. Material & Texture Fidelity** | 20 | 3.0 | 14.0 | 16.0 | **18.5** | $+15.5$ | Exemplar |
| **4. Interior / Circulation Realism** | 20 | 0.0 | 12.5 | 17.0 | **19.5** | $+19.5$ | Exemplar |
| **5. Environmental & Site Integration** | 20 | 6.0 | 15.0 | 17.5 | **19.0** | $+13.0$ | Exemplar |
| **Total Composite Score** | **100** | **16.0 / 100** | **71.0 / 100** | **85.0 / 100** | **95.5 / 100** | **$+79.5$** | **GOLD STANDARD EXEMPLAR (>= 9.5/10)** |

### B. Visual Progression Carousel

````carousel
![Cam 72: South Hero State Street View, Colonnade Portico, Canopy & Signage](stewart_cam72_south_hero.png)
<!-- slide -->
![Cam 73: Loeb Playhouse Proscenium Theatre Interior, Stage Deck, Crimson Curtain & Curved Seating Tiers](stewart_cam73_loeb_playhouse.png)
<!-- slide -->
![Cam 74: HSSE Library Reading Hall Interior, Honey Oak Study Tables, Banker's Lamps & Book Stacks](stewart_cam74_hsse_library.png)
<!-- slide -->
![Cam 75: Robert L. Ringel Gallery Interior, Polished Terrazzo Reflections, Sculpture Pedestals & Oil Paintings](stewart_cam75_ringel_gallery.png)
<!-- slide -->
![Cam 76: North Memorial Mall Precinct Aerial Context, Grand Terrace, Stewart Center & PMU](stewart_cam76_precinct_aerial.png)
````

### C. Architectural & Interior Space Breakdown

1. **Exterior Mid-Century Civic Architecture (`48_Stewart_Center_Exterior` — 401 objects)**:
   - **Mid-Century Brick & Limestone Masonry**: Textured Purdue Red Brick masonry with continuous $1.5\\text{m}$ Indiana Bedford Limestone water table base and 4 horizontal beltcourses ($Z = 4.2\\text{m}, 8.4\\text{m}, 12.6\\text{m}, 16.5\\text{m}$ parapet coping).
   - **South Monumental Portico on State Street**: Sited at $X = 84.0\\text{m}, Y = -303.3\\text{m}$, featuring 4 monumental fluted Bedford limestone colonnade piers ($1.4\\text{m} \\times 1.2\\text{m} \\times 9.0\\text{m}$), capitals, plinths, 2-story recessed glazed lobby entrance with bronze frames, triple bronze-framed doors, cantilevered entrance canopy ($32\\text{m} \\times 8\\text{m}$) with recessed warm downlights, and 3D extruded gold serif lettering (`\"STEWART CENTER\"`).
   - **Vertical Limestone Solar Fins & Ribbon Fenestration**: Rhythmic vertical limestone fins along the South and West facades framing 4 floor levels of solar-tinted ribbon glass windows.
   - **North Memorial Mall Grand Entrance**: 2-story glass curtain wall entrance pavilion (`\"BOILERMAKER STATION WELCOME CENTER\"`), structural limestone columns, grand entrance canopy at $Z = 4.5\\text{m}$, and triple bronze doors.
   - **East Concourse Covered Portal**: Ground-floor portal linking directly to the Purdue Memorial Union West Courtyard promenade.
   - **Roof System & Loeb Stage Fly Loft**: Main flat gravel membrane roof ($133.4\\text{m} \\times 90.8\\text{m}$) at $Z = 16.3\\text{m}$, central Loeb Playhouse stage fly loft tower ($26\\text{m} \\times 28\\text{m} \\times 5.8\\text{m}$, rising to $Z = 22.2\\text{m}$) with vertical brick pilasters and limestone coping, and dual rooftop mechanical penthouses with bronze HVAC louvers.

2. **Finished Photorealistic Interiors (`49_Stewart_Center_Interiors` — 923 objects)**:
   - **Loeb Playhouse (1,011-Seat Proscenium Theatre)**:
     * Dark oak tongue-and-groove proscenium stage deck ($24\\text{m} \\times 11\\text{m}$) elevated to $Z = 1.6\\text{m}$, limestone apron edge, and 11 proscenium footlight luminaires.
     * Monumental acoustic honey oak proscenium arch with gold leaf inner trim and central Purdue gold seal medallion.
     * Grand stage curtain in rich crimson velvet with scalloped valance, side swags, and gold tassel tiebacks.
     * 12 stepped curved seating riser terraces in acoustic navy carpet with illuminated floor track lights.
     * Over 200 individual cushioned crimson velvet theatre seats with backrests and armrests across all rows.
     * Cantilevered balcony level with brass safety railings and velvet seating.
     * 3 suspended acoustic ceiling clouds with recessed stage spotlights, key lighting ($E=5500$), and house ambient illumination ($E=3800$).
   - **HSSE Library (Humanities, Social Science and Education Library)**:
     * Double-height academic reading hall with elevated finished floor slab ($Z = 0.40\\text{m}$) and navy carpet runner.
     * 6 rows of double-sided mahogany book stacks loaded with multi-colored book bindings (crimson, blue, gold, green, leather) and brass aisle markers.
     * Collaborative study tables in solid honey oak with edge banding, classic brass banker's lamps with glowing green glass shades, open textbooks, student laptops with emissive screens, and dark oak task chairs.
     * North-facing curtain wall windows overlooking Memorial Mall.
   - **Robert L. Ringel Gallery (Fine Arts Exhibition Hall)**:
     * Polished cream terrazzo flooring ($0.08$ roughness, $0.98$ specular) casting sharp specular reflections of the overhead gallery track lights.
     * Open $30\\text{m}$ gallery promenade with 4 staggered minimalist white display pedestals holding bronze and marble modern art sculptures.
     * Flanking exhibition walls with 6 large gold-framed canvas oil paintings and dedicated brass picture lights.
     * Gold gallery title board (`\"ROBERT L. RINGEL GALLERY\"`).
   - **Main Civic Concourse & Boilermaker Station**:
     * Polished terrazzo concourse floor, curved oak welcome desk with quartz countertop, digital information screen, and directional signage bar.

3. **Civic Plaza & Site Integration (`50_Stewart_Center_Plaza_and_Site` — 37 objects)**:
   - **North Memorial Mall Grand Terrace**: $60\\text{m} \\times 16\\text{m}$ stepped Bedford limestone terrace facing Founders Park and Loeb Play Fountain, wide grand staircases, manicured lawn panels with boxwood hedges, curved limestone seatwalls, teak wood benches, and 3 Victorian cast-iron lantern posts with warm luminaires.
   - **South State Street Plaza**: Brick paver concourse along State Street, 12 Sheffield bicycle racks, and limestone planter beds.
   - **East Concourse Walkway**: Seamlessly meets the PMU West Courtyard promenade and loggia arcade.
'''

# Renumber sections 3 through 13 to 4 through 14
for s_num in range(13, 2, -1):
    text = text.replace(f'## {s_num}. ', f'## {s_num+1}. ')

# Insert Stewart Center as Section 3 right before Section 4
text = text.replace('## 4. Guy J. "Red" Mackey Arena', stewart_section + '\n## 4. Guy J. "Red" Mackey Arena')

# 4. Add Cam 72 through 76 to the Master Camera Inspection Gallery table
cam_rows = '''| **`Cam_72_Stewart_South_Hero`** | $(58.0, -308.0, 3.0)$ | Facing North-East ($82^\\circ$ pitch) | Hero State Street South Arrival: Stewart Center 4-pier limestone colonnade portico, cantilevered entrance canopy with recessed downlights, 3D gold building lettering (`"STEWART CENTER"`), vertical limestone solar fins, Sheffield bike racks, and State Street concourse. |
| **`Cam_73_Stewart_LoebPlayhouse_Interior`** | $(52.0, -266.0, 2.4)$ | Facing North ($84^\\circ$ pitch) | Loeb Playhouse Proscenium Theatre: dark oak stage deck ($Z=1.6\\text{m}$), footlights, proscenium arch with Purdue seal, crimson velvet grand curtain with valance and gold tassels, 12 stepped curved seating riser terraces in navy carpet, cushioned velvet theatre seats, and acoustic ceiling clouds. |
| **`Cam_74_Stewart_HSSE_Library_Interior`** | $(95.0, -242.0, 2.5)$ | Facing North-East ($83^\\circ$ pitch) | HSSE Library Reading Hall: honey oak collaborative study tables, glowing green glass banker's lamps, open textbooks, laptops with glowing screens, task chairs, and 6 double-sided book stack ranges loaded with multi-colored books. |
| **`Cam_75_Stewart_RingelGallery_Interior`** | $(94.0, -263.0, 2.0)$ | Facing East ($85^\\circ$ pitch) | Robert L. Ringel Gallery: polished cream terrazzo flooring with sharp specular reflections, open exhibition promenade, 4 staggered white display pedestals with bronze and marble sculptures, and gold-framed oil paintings with brass picture lights. |
| **`Cam_76_Stewart_North_Aerial`** | $(35.0, -145.0, 48.0)$ | Facing South-East ($58^\\circ$ pitch) | North Memorial Mall Precinct Aerial Context: Stewart Center mid-century brick massing ($134.8\\text{m} \\times 92.2\\text{m}$), central Loeb Playhouse stage fly loft ($Z=22.2\\text{m}$), dual mechanical penthouses, North Boilermaker Station glass entrance, grand limestone terrace, and PMU West Courtyard interface. |
'''

target_table_header = '| Camera Identifier | Coordinates $(X, Y, Z)$ | Target Angle & View | Key Landmark & Architectural Features Framed |\n| :--- | :--- | :--- | :--- |\n'
text = text.replace(target_table_header, target_table_header + cam_rows)

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('purdue_digital_twin_report.md updated successfully via script!')
