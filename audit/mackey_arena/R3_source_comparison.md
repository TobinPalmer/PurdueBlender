# Mackey R3 source-comparison notes

## Facade reference

The two direct HNTB project photographs are linked in `evidence_r3.json` and in the [HNTB project page](https://www.hntb.com/projects/purdue-university-mackey-athletics-complex/). They are perspective photographs, not construction elevations; geometry dimensions were not reverse-measured from them.

`Purdue-2.jpg` shows the long brick wing, broad ground-floor glazing, two upper window levels with alternating single and paired narrow vertical openings, light horizontal courses, and the rounded glass lobby at the east end next to Mackey. `Purdue-3.jpg` gives a closer view of the two-storey curved curtain wall, ground-floor entry, horizontal frame members and stair behind the glazing. The R3 model now follows this directional arrangement: the lobby is on the east end of the south facade, the lower storefront band is wider, upper apertures alternate singles/pairs, and brick is mapped using a per-face metre-aligned UV projection so the courses remain horizontal on both north/south and east/west elevations.

The stair, door sizes, arc radius, precise opening widths and coursing dimensions remain illustrative because HNTB did not publish elevations or an as-built plan in the sources consulted.

## Registration exhibit

`orthophoto_registration_overlay.png` uses the exact export extent and dimensions from `orthophoto_export_metadata.json` (EPSG:3857; x `[-9675753,-9675103]` m; y `[4928874.778571429,4929431.921428571]` m; 1400x1200 px). The overlay now draws the original composite GIS ring, eight-point SDAC roof-seam trace, two visible partial low-roof traces, and the existing arena shell. A north arrow and 50 m scale bar are derived from that same extent. `north_sdac_registration_detail.png` enlarges the north roof area for inspection.

This is a visual registration check using the documented project-local approximation and its inverse, not independent survey control. No residual error or sub-metre precision is asserted. The area imagery is from 2023 and may not represent current conditions.
