# Elliott Hall of Music reference notes — round 3

Research date: 2026-10-23.

## Verified from primary or architectural sources

- Purdue Convocations says patrons can use the north or south access doors with black-and-gold awnings to reach main-floor seating without steps; Elliott has no elevators. It also documents wheelchair seating with companion seats nearby and identifies an accessible restroom by the south entrance. [Accessibility page](https://convocations.purdue.edu/accessibility/)
- Purdue Convocations' parking information distinguishes the north accessible lot and the south/southwest accessible lot. [Directions and parking](https://convocations.purdue.edu/parking-directions-elliott-hall-of-music/)
- SAH Archipedia describes the building's red-brick and Indiana-limestone exterior, red-clay-tile roof, cubic mass with flytower and apsidal projection behind the stage, curving entry canopy, secondary entrance surrounds, stepped side-exit walls and two sculpture groups. [SAH Archipedia](https://sah-archipedia.org/buildings/IN-01-157-0079)
- The published seating chart depicts the levels, section divisions and accessible-seat symbols but is not scaled. [Purdue seating charts](https://convocations.purdue.edu/seating-charts/)
- Official Purdue GIS FeatureServer FID 617 supports the 188-point horizontal footprint. It does not establish facade openings or any vertical dimension. [BuildingShapes FeatureServer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0)
- Purdue's anniversary article describes the roughly 6,000-seat proscenium auditorium and includes historical exterior imagery. [Elliott 75th anniversary](https://convocations.purdue.edu/elliott-hall-of-music-75th-anniversary-1940-2015/)

## Modeling decisions tied to evidence

- Two entrance openings are included because Purdue explicitly identifies two accessible access doors. Approximate positions were selected on the north and south portions of the GIS ring; exact coordinates and dimensions are not provided by Purdue.
- A black canopy and gold fascia are included at each door because Purdue identifies these colors. Their profiles/dimensions are estimated.
- The level interior traces are conceptual geometry connecting doors to two chart-informed main-floor wheelchair areas. No dimensioned interior access plan was found, and the published chart cannot verify these alignments or clearances.
- Procedural regularized window holes were removed because no trustworthy elevation/window schedule was found. The new pass does not claim a verified count or spacing.
- Red brick, limestone bands/pilasters, tile courses and flytower form follow published material/architectural descriptions. Their location, distribution, size, roof form, and height remain estimates.

## Evidence limitation

The search surfaced Purdue historical photos and a Maps search page, but this pass did not inspect a current Google Maps facade image or obtain a current dimensioned elevation. Those sources were not used to claim precise opening placement or a measured facade rhythm. The provided door locations and all vertical values are modeled hypotheses awaiting review against an authoritative drawing or field survey.
