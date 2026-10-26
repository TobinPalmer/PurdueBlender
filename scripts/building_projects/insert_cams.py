report_path = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25\purdue_digital_twin_report.md"
with open(report_path, "r", encoding="utf-8") as f:
    content = f.read()

target = """| Camera Identifier | Coordinates $(X, Y, Z)$ | Target Angle & View | Key Landmark & Architectural Features Framed |
| :--- | :--- | :--- | :--- |"""

new_rows = """| Camera Identifier | Coordinates $(X, Y, Z)$ | Target Angle & View | Key Landmark & Architectural Features Framed |
| :--- | :--- | :--- | :--- |
| **`Cam_82_CL50_OvalDrive_Hero`** | $(-71.19, -128.95, 4.2)$ | Facing North-West ($82^\\circ$ pitch) | Hero Oval Drive Arrival: 7 colossal brick piers, Bedford limestone capitals and plinths, cantilevered entrance canopy with recessed downlights, 3D Old Gold building lettering (`\"CLASS OF 1950 LECTURE HALL\"`), 2nd-floor ribbon window curtain wall, Oval Drive granite plaza, teak benches, 12 Sheffield bike racks, and Victorian lantern posts. |
| **`Cam_83_CL50_224_Auditorium_Interior`** | $(-111.99, -107.75, 6.4)$ | Facing South-West ($76^\\circ$ pitch) | CL50 224 Major Lecture Hall: 470-seat tiered auditorium, 10 stepped semi-circular seating risers in navy carpet, curved continuous oak student tables, 470 articulating navy swivel chairs, signature 50-foot green porcelain chalkboard with chalk scientific formulations, dual 150\" motorized projection screens, instructor dais, and oak smart lectern with Purdue seal. |
| **`Cam_84_CL50_EinsteinBagels_Atrium_Interior`** | $(-97.19, -107.45, 2.2)$ | Facing South-West ($84^\\circ$ pitch) | Ground-Floor Student Atrium & Einstein Bros Bagels: 2-story light-filled atrium volume with polished cream terrazzo flooring and gray border trim, Einstein Bros Bagels warm wood service counter with quartz top, POS registers, glass pastry showcase, illuminated yellow menu boards, cafe dining with 6 circular high-top tables, 24 blue swivel barstools, and front curtain wall daylight. |
| **`Cam_85_CL50_Stage_Instructor_Interior`** | $(-98.79, -115.15, 5.7)$ | Facing North-West ($84^\\circ$ pitch) | 2nd-Floor Gallery & Bronze Sculpture: 3/4 museum gallery showcase of John Seward Johnson Jr.'s 700-lb bronze sculpture *\"The Way It Was\"*, depicting two post-WWII classmates seated on a park bench studying open textbooks atop a polished granite display plinth with dedication plaque, under a focused warm 3500K museum gallery spotlight with gallery balustrade overlook. |
| **`Cam_86_CL50_MemorialMall_Precinct_Aerial`** | $(-51.19, -164.95, 56.0)$ | Facing North-West ($62^\\circ$ pitch) | Memorial Mall & Oval Drive Precinct Aerial Context: Class of 1950 Lecture Hall modern collegiate brick massing ($43.8\\text{m} \\times 37.9\\text{m}$), rooftop mechanical penthouse with HVAC louvers, Oval Drive carriage loop, and continuous pedestrian network connecting to Elliott Hall of Music, Stanley Coulter Hall, and University Hall. |
| **`Cam_77_Hovde_South_Hero`** | $(-84.0, 56.0, 2.8)$ | Facing North-East ($82^\\circ$ pitch) | Hero South Arrival View: 6 fluted Bedford limestone columns ($1.1\\text{m}$ dia, $10.5\\text{m}$ height), monumental pediment, 3D Old Gold lettering (`\"FREDERICK L. HOVDE HALL OF ADMINISTRATION\"`), 12-tier grand granite entrance staircase with limestone balustrades and bronze urns, and Memorial Mall granite arrival concourse. |
| **`Cam_78_Hovde_PresidentOffice_Interior`** | $(-56.5, 87.5, 5.6)$ | Facing South-East ($84^\\circ$ pitch) | Office of the University President: dark walnut parquet and wainscoting, Persian area rug, monumental mahogany partner desk with green leather blotter, glowing brass banker's lamp, president's black leather high-back swivel chair, limestone fireplace with glowing embers, US and Indiana flags, and portico colonnade Mall vistas. |
| **`Cam_79_Hovde_Boardroom_Interior`** | $(-69.5, 99.0, 5.6)$ | Facing South ($84^\\circ$ pitch) | Board of Trustees Boardroom: monumental 24-seat boat-shaped mahogany conference table, 24 articulated executive black leather swivel chairs, 24 delegate gooseneck mics with red tally rings, burgundy leather folios, witness lectern, dual 120\" screens, and north feature wall with acoustic walnut fluting and $2.6\\text{m}$ 3D gold Purdue seal. |
| **`Cam_80_Hovde_Rotunda_Interior`** | $(-62.85, 82.5, 2.2)$ | Facing North ($84^\\circ$ pitch) | Art Deco Grand Rotunda & Marble Foyer: 2-story public atrium volume, polished cream marble tile floor, central $4.4\\text{m}$ circular terrazzo Purdue seal medallion with concentric gold inlay rings and 3D Motion 'P', twin sweeping marble staircases with bronze balusters and walnut handrails, three arched walnut double portals on the north corridor wall, and dual Art Deco brass ring chandeliers. |
| **`Cam_81_Hovde_Precinct_Aerial`** | $(-115.0, 20.0, 48.0)$ | Facing North-East ($62^\\circ$ pitch) | Memorial Mall Apex Precinct Aerial Overview: Hovde Hall neoclassical massing ($21.6\\text{m} \\times 71.0\\text{m}$), rooftop mechanical penthouse, grand stairs, and civic integration terminating Memorial Mall, flanked by Elliott Hall of Music, Centennial Mall, and WALC. |"""

if target in content:
    content = content.replace(target, new_rows, 1)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Camera table updated successfully!")
else:
    print("Target table header not found!")
