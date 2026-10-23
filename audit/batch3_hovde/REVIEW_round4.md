# Hovde Hall — round 4 building-side update

**Self-review: 6.9/10; independent review requested.** The exterior is now better lit and the portico fascia is slimmer, with more visible separation between the shafts and façade. The interior plan evidence remains schematic, and the exact roof form is still unverified. This is not a 9/10 completion claim.

## Round 4 changes

- Reduced the portico entablature height and projection, reset the cornice/pediment elevations for contact, and narrowed the six column shafts and capitals/bases. Updated the stone base color to a neutral limestone. The existing six-column arrangement and triangle pediment remain.
- The earlier round 4 edit also moved the portico assembly forward to clarify its relationship to the façade, reduced the fascia/pediment widths, deepened column flutes, and adjusted column spacing. These changes are in `round4_portico_refine.py` and `round4_final_refine.py`.
- Improved the illustrative presidential office and trustees room furnishings: desk/table/chair arrangement, shelving/books, records credenza, and boardroom storage/wayfinding. No interior plan source was found, so these placements remain interpretive.
- Did not edit `purdue_campus_master.blend`, the GIS placement marker, manifest, or shared master scripts. The internal `HOVD_Root` transform remains `[-62.85, 93, 0]`, Z rotation `0.689754 rad`, scale `[1,1,1]`.

## Reopen and evidence

Blender 5.2.3 reopened the saved canonical asset for the new renders and final asset check. The check reports `Asset_hovde_hall` with 727 objects / 715 meshes and no unmaterialed meshes. Root transform is unchanged. Reopen-check output is in `final_check_round4.log` and `final_asset_check.json`.

- `exterior_round4_verified.png` — balanced exterior; brick reads deep red-brown. The entrance/portico is small in the full-building view.
- `portico_detail_round4_verified.png` — full entrance detail with brighter exposure; the triangular pediment and column group are visible. The tympanum/fascia remains broad and visually flat at this scale, and the lettering overlaps the stone face.
- `presidential_office_round4_verified.png` — room-plan render without exterior-shell occlusion; furnishings and circulation are visible from above, but this reads as an interpretive schematic rather than a finished interior.
- `trustees_boardroom_round4.png` — prior round 4 cutaway shows the long board table and chairs; blank wall/slab areas remain. The new top-plan capture attempt in `trustees_boardroom_round4_verified.png` is blank and should not be treated as evidence.
- `round4_final_refine.py` and `render_round4_verified.py` — reproducible geometry and evidence steps. The interior render uses a temporary neutral floor for presentation only; it is not saved into the asset.

## Sources and uncertainty

- [Wikimedia Commons, Hovde Hall exterior 01](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg), photo dated 2016-09-18, geotag 40.428660, -86.913958. Used for the red brick wings, central stone portico, broad stairs, roof silhouette, and six-column frontage; it is perspective evidence, not a measured elevation.
- [Wikimedia Commons, Hovde Hall exterior 02](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_02.jpg), winter exterior corroboration.
- [West Lafayette visitor guide](https://assets.simpleviewinc.com/simpleview/image/upload/v1/clients/westlafayettein/2022_Visitors_Guide_0481c246-c159-4d01-a3a6-e00c4eddae3e.pdf), depicts the classical column-and-pediment façade.
- [Purdue Archives Hovde Hall record](https://archives.lib.purdue.edu/agents/corporate_entities/573), checked 2026-10-23; administration-building context and overall building dimensions, not an interior plan.
- Official Purdue GIS feature FID 618 in `audit/official_purdue_buildings_wgs84.json`, WGS84/EPSG:4326 snapshot retrieved 2026-10-22. This building-side pass did not perform a current master/GIS overlay; the master agent remains responsible for contextual placement confirmation.

**Remaining issues:** exact roof profile and roof access structure; measured portico proportions and façade relationship; supported interior dimensions/circulation; improved enclosure and furniture detail; text/stone-face legibility; master/GIS alignment review. Request independent round 4 review of the reopened asset and evidence above.
