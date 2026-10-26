# ISGL repair research checkpoint (no asset revision)

Stable ID: `massing_islamic_societyof_greater_lafayette_0130012`  
Review task: address r1 identity/area and roof findings.  
Date: 2026-10-26.

## Identity and address reconciliation

Purdue BuildingShapesZip4 FID 771 (`BLDG_ABBR=SOMSA`) is labeled `Muslim Student Association`, address `1021 FIRST ST.`. The official Islamic Society of Greater Lafayette (ISGL) website lists `1022 1st St.` at the First/Russell corner. These names and street numbers differ, so the GIS record alone does not prove ISGL identity.

Two additional sources make a same-site organizational match strong:

- Purdue Engineering’s Global Engineering Programs page records a 2022 event location as “Islamic Society of Greater Lafayette, 1022 1st Street” and states Purdue hosted it with the Muslim Student Association (MSA). This directly connects MSA activity with the official ISGL venue and address. Raw snapshot: `sources/purdue_gepp_ramadan_event_isgl_msa_2022.html`. URL: https://engineering.purdue.edu/GEP/events/2022/global-celebration-ramadan
- Tippecanoe County’s 2010–2024 judgments workbook lists `NORTH AMERICAN ISLAMIC TRUST INC ISGL` at `1022 FIRST ST`, West Lafayette. Raw snapshot: `sources/tippecanoe_county_judgments_2010_2024_2025-01.xlsx`. URL: https://www.tippecanoe.in.gov/DocumentCenter/View/48331/2010-2024-Judgments-Updated-1-31-25

Together with the labeled ISGL exterior photo, current orthophoto, and the exact First/Russell corner placement, this supports the interpretation that FID 771 maps the ISGL physical building while its legacy GIS organization label reflects MSA use/ownership context and a one-number address variation. It does not prove a formal parcel/address crosswalk. Keep the identity qualification explicit as “strong physical-site match; GIS naming/address differ,” rather than claiming the GIS name itself says ISGL.

## Area-field conflict

The FID 771 source ring has 11 unique vertices. Under the repository’s documented local geographic transform its shoelace area is 463.267 m² and its XY bounds span 22.614 m by 21.758 m. The resulting bounding rectangle is only about 491.8 m², so ArcGIS `Shape__Area=800.7890625` m² cannot describe that same transformed polygon ring as a planar square-meter area; it is about 1.63 times the bounding rectangle. The rendered shell vertices match the raw transformed ring in the saved reopen record to 0.00001437 m maximum nearest-vertex error.

The proper repair is to keep the source vertices and ring-derived fit, not scale the footprint to the unusable attribute. Preserve `Shape__Area` as a documented source-field conflict until Purdue GIS clarifies its calculation/provenance or an independent survey/parcel source resolves it. No area scale or geometry edit was made in this checkpoint.

## Roof and facade observations for the next Blender pass

The 2022–2025 Indiana orthophoto (`sources/indiana_current_imagery_isgl.jpg`, service metadata beside it) shows several distinct roof planes and a ridge/hip intersection on the building; it is more complex than the current single-center-apex fan roof. A next builder pass should form a low multi-plane hipped/intersecting roof with a main ridge and secondary ridge/hip junctions, matching only the visible plan pattern. The orthophoto does not establish ridge elevations, roof pitch, exact eave boundary, or measured heights.

The Home of Purdue/Visit Lafayette photo supports red-brown brick, two visible facade/window bands, a pale masonry entry surround, lettering/signage, and a small rounded/domed entrance canopy. It is a single oblique view without camera orientation, so modeled entrance compass side and bay spacing remain inferred. GIS reports one level (`NUM_LEVELS=1`, `CountOfFLO=1`), while the photo shows two facade bands; keep the modeled 6.05 m eave / 8.15 m peak explicitly estimated and do not claim a measured story count or height.

## Pause state

The Blender addon is offline (`Could not connect to Blender`) and no standalone Blender/bpy runtime is available in this environment. No asset revision was saved, no builder/evidence record/source catalog was changed, and no validation/render was produced for a new revision. Existing r1 grade and current asset remain untouched. Resume roof/facade edits and direct-reopen validation when Blender is available.
