# Krannert Building batch2 review

Source: modular/buildings/krannert_building.blend, Asset_krannert_building. Existing official FID54 footprint and local placement origin (234.534500122,-412.719009399) retained. Original backup before.blend. No master edits.

Evidence retrieved 2026-10-22: https://business.purdue.edu/undergraduate/visit/self-guided-tour.pdf (Purdue Daniels School official, undated source; archived PDF and rendered pages0,4,5,6). Page6 Drawing Room first floor photo: blue/lime upholstered chairs, pale counters, warm wood tables, acoustic dividers. Page4 Parrish Library second floor photo: low oak bookshelves, books, dark counter and booth seating. These room identities/floors are supported; furniture dimensions, counts and XY placement are inferred. No surveyed interior plan was found. Photo supports materials qualitatively, not calibrated color.

Google Maps: parent independently viewed https://www.google.com/maps/search/Krannert+Building+Purdue on2026-10-22, StreetView Mar2026: limestone broadpiers/narrowdarkverticalwindows, reddishbrickgroundbase, flatroof louverparapet. Parent records map evidence. Our web opening failed; no claim of standalone maps snapshot here.

Edits:350 new furniture/carpet/shelf/book components,383 exportedobjects total. Six tables,18 DrawingRoom chairs/stools,6 blue dividers,study counter,3 low library bookcases with156 bookspines,6 library desks/seats. Procedural oak directionalgrain,blue/lime fabric,carpet; no external texture dependencies. Original material bump distances reduced from default1m to0.0006m. Material viewport colors synchronized.669 existing glazing panel rectangles cut through previously opaque masonry ring; inward0.2m solidify added. Original envelope reference,heights,markers retained.

Validation: file saved and reopened via CLI; shader exterior,DrawingRoom,Parrish renders generated. checks.json confirms no missing images. Interior render camera was initially in solid staircore and black; corrected camera produces visible furnishings. Source core geometry remains simplified solid blocks. Opposed chair backs and floating stool legs corrected in refine.py after reviewer comments.

Unfinished: precise room boundaries/circulation, doors,stairs/elevators,ceilings/lightfixtures,remaining floors,classrooms/advising. Furniture is blocky schematic; booth seating not reconstructed. Limestone block joints and groundbrickband not yet confirmed/rebuilt. Existing fullheight facade gap needs closer source review. Heights from legacy attributes remain estimates. Basement is visible below standalone grade plate in exterior preview; master terrain should conceal subsurface. This is partial reconstruction and does not achieve requested9/10.

Final reviewer5.7/10 (reviewer.md). Reviewer identified six floating Parrish desktops; added24 metal legs, source now407objects. Latest interior renders prior supports; geometry fixed and reopened on final render run.
