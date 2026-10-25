# Neil Armstrong Hall source review R12

Review date: 2026-10-25

## Findings

No publicly available, dimensioned as-built roof plan, facade elevation, or architectural section was located in this search. Purdue Archives catalogs an item titled “Neil Armstrong Hall of Engineering, Purdue University, development plans, September 2004.” It is an archival item, not a digitized drawing set, and access requires consultation with the Flight and Space Archivist. This record is a lead for future evidence, not geometry evidence.

The public sources support the following features:

- Purdue’s architectural account describes a distinctive cantilever evoking an aircraft wing and says the location was intended to serve as the northern gateway to campus.
- A Purdue engineering newsletter says the roof extensions are winglike, identifies four occupied floors including a lower level, and gives a 53-foot atrium lobby ceiling.
- A 2009 Alcoa/Reynobond product advertisement names RATIO architect Chris Boardman and describes the roof color as deep red to match campus terracotta; this supports red metallic cladding as a material cue, not a measured roof profile.
- Purdue’s construction progress page and Engineering Computer Network webcam archive provide construction imagery, but no dimensioned drawings or image poses suitable for geometric registration were found.
- Wikimedia Commons contains several high-resolution 2016 exterior views by Julian Herzog under CC BY 4.0. Files 01, 02, 03, 04, and 05 include camera coordinates (the point of view) and lens focal lengths, so camera starting positions can be placed approximately for comparable renders. Their heading/roll and camera control points are absent, so the photos do not yield a calibrated facade registration by themselves.

Using the previously established local-frame origin (lat/lon 40.4274, -86.9137; offset marker -109.0, 400.1893 m), their approximate camera positions in asset-local meters are: 01 (-95.4, 43.8), 02 (-19.1, -14.9), 03 (-152.1, 48.8), 04 (-98.4, 29.0), and 05 (-98.4, 29.0). File 02's point falls in the U-shaped open courtyard in the top-down aerial, consistent with an interior-courtyard view. These are useful starting points for matching view positions; they are not full camera calibration because heading and roll are not given.
- The publicly indexed Purdue floorplan/emergency information confirms room/level labels but does not expose measured plans or locate facade openings, atrium bridges, or stairs in the local asset coordinate frame.

## Modeling implications

Use the orthophoto/GIS only for the building-site footprint context. GIS feature FID642 is a generalized building polygon and does not distinguish walls, canopies, or roof edges; it cannot independently justify stretching the modeled wall shell to its boundary. Treat the photographic roof silhouette as visual evidence for a wing-shaped cantilever, but label any inferred three-dimensional surface as photo-based and unmeasured. Do not assign exact edge lengths or facade stationing without the archival drawings or a registered image.

## Sources

- Purdue Archives item record: https://archives.lib.purdue.edu/repositories/2/archival_objects/41754
- Purdue College of Engineering award coverage describing the aircraft-wing cantilever: https://www.ibj.com/articles/71-depauw-ball-state-purdue-buildings-among-top-aia-design-winners
- Purdue Ray W. Herrick Laboratories, Fall 2007 newsletter: https://engineering.purdue.edu/Herrick/about/news/Newsletter/fall-07.pdf
- Alcoa/Reynobond advertisement in *Architectural Record*, July 2009: https://www.usmodernist.org/AR/AR-2009-07.pdf
- Purdue Materials Engineering construction progress page: https://engineering.purdue.edu/MSE/news/2000-2009-news/ContinuedProgressonConstructionofTheNeilArmstrongHa
- Purdue Engineering Computer Network webcam archive: https://engineering.purdue.edu/ECN/WebCam/cam01
- Purdue Engineering facilities/space information: https://engineering.purdue.edu/Engr/AboutUs/Facilities/images
- Commons 2016 exterior photo 01 (5,433 × 6,992 px, 38 mm stitched panorama, POV 40.431388, -86.916112): https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_01.jpg
- Commons 2016 exterior photo 02 (5,207 × 3,476 px, 24 mm, POV 40.430861, -86.915212): https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_02.jpg
- Commons 2016 exterior photo 03 (5,607 × 3,761 px, 48 mm, POV 40.431433, -86.916781): https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_03.jpg
- Commons 2016 exterior photo 04 (3,896 × 3,118 px, 24 mm, POV 40.431256, -86.916147): https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_04.jpg
- Commons 2016 exterior photo 05 (5,981 × 3,993 px, 24 mm, POV 40.431256, -86.916147): https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_05.jpg

## Search outcome

Search queries included Neil Armstrong Hall Purdue architectural plans/elevations, RATIO project records, Purdue engineering floor plans, and construction images. The only archival plan citation located was the September 2004 item above. No public drawing or raster plan with scale/north arrow/control points was found. This search result does not establish that no plans exist; the archive record indicates that development plans may be consulted through Purdue Archives.
