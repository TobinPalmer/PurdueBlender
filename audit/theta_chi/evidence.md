# Theta Chi (Alpha Delta Chapter) — FID 760

**Stable asset:** `massing_house_301841328_39f169f`  
**Asset path:** `modular/buildings/massing_house_301841328_39f169f.blend`  
**Build script:** `modular/buildings/build_massing_house_301841328_39f169f.py`  
**Evidence retrieved:** 2026-10-26

## Identity and spatial match

Purdue campus GIS FID 760 names the building **Theta Chi**, gives `800 David Ross Rd`, and labels its owner `GREEK`. The chapter's [official housing page](https://purduethetachi.com/about-us/housing-information/) independently identifies its Alpha Delta house at 800 David Ross Road. The [chapter history page](https://purduethetachi.com/about-us/) says the present house was built in 1966 and renovated in 1999. This verifies the physical house/FID assignment independently of proximity.

The GIS geometry was queried in WGS 84 and transformed with the local approximation documented in `modular/AGENTS.md`; its projected polygon is the shell footprint in the rebuilt asset. The source polygon is about 770.08 m² in that local ground approximation, with bounds X −1099.351 to −1060.033 m and Y 668.341 to 698.449 m. The GIS layer's `Shape__Area` value is 1331.30 m², a planar Web Mercator value; it is not used as ground area. `Extrution=12` is not treated as a measured height.

The legacy OSM way 301841328 has only the generic tag `building=school` and no address or fraternity identity. Its seven-point shape is therefore a spatial candidate only. Compared with GIS FID 760 after the same coordinate conversion, its polygon has 0.681 intersection-over-union (IoU); after aligning centroids by 0.669 m east and 3.217 m north, IoU is 0.863 and Hausdorff distance is 2.819 m. This supports the assigned asset association but does not establish identity on its own. The rebuilt shell follows the Purdue GIS ring directly.

## Exterior form and modeling choices

The [official national Theta Chi Alpha Delta page](https://thetachi.org/chapter/alpha-delta/) supplies a winter oblique photograph saved as `sources/theta_chi_national_alpha_delta_house.jpg`. The archived [Purdue-hosted chapter-house page](https://web.ics.purdue.edu/~thetachi/index_files/Page474.htm) describes the house and gives 800 David Ross Drive; its exterior image `sources/image316.jpg` has EXIF date 2004-05-02. Both pictures show a two-level, red-brick house with a pale masonry base and trim, a low dark hipped roof, a tall entrance feature with an arched upper window and chapter panel, and three arched porch bays. The model uses those visible elements on the best-fit long GIS facade. Repeated window bays and cream sills are simplified representations of the photographed rhythm.

The photos provide no scale, measured elevations, or north-bearing registration. The modeled 7.1 m eave, 8.8 m roof ridge, story heights, roof framing/silhouette, window dimensions, and which GIS wall corresponds to the photographed front are estimates. Purdue GIS reports `NUM_LEVELS=1`, which conflicts with the two visible occupied levels in both exterior photos; the photo evidence is used for visible storey count and the GIS value is recorded as a source conflict. No unseen rear elevations or interior spaces are asserted as verified. The roof is intentionally low-pitched and simplified; no unsubstantiated chimneys, dormers, or other ornament were added.

## Build and validation record

- The dedicated build script reads the saved FID 760 source snapshot and asserts its building name and address before generating geometry.
- The project local coordinate approximation was used as documented in `modular/AGENTS.md`; the original stable asset ID, file path, collection name, object name, and campus-world coordinate convention are preserved.
- The saved library collection contains one joined mesh object with brick, masonry, roof, trim, glazing, and entry-shadow materials. The project preview is `renders/theta_chi_preview.png`.
- A new Blender 5.2.3 LTS background process opened the saved `.blend`. It confirmed the expected collection and object, identity object transform, no modifiers, no external images or linked libraries, and the report in `reopen_validation.json`. The report SHA-256 identifies the frozen file.
- Root indexes and TODO/master integration handoff remain coordinator-owned and were not changed here.

## Remaining uncertainty

Position and source footprint are tied directly to the named Purdue feature. Building height, exact wall-vs-roof footprint, roof framing, facade bearing, window dimensions, and unseen sides remain estimated or unverified. The current object is awaiting independent grading and master-blend integration.
