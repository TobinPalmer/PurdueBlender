# Independent master integration grade: Beta Sigma Psi

**Score: 9.00/10 — pass**

## Criteria

- **Correct identity and source-backed footprint**: 1.85/2.0. Fresh master links the same stable Beta Sigma Psi asset ID whose exact Purdue GIS FID 793 name/address and 14-vertex source footprint were independently checked. Current April 2026 exact-address pano shows the Beta Sigma Psi sign. WGS84 and EPSG:2968 vertex calculations agree within about 0.2 m².
- **Position, orientation, and scale/dimensions**: 1.90/2.0. The final marker is at [-287.77410888671875, 289.8915710449219] m, matching the manifest by 0.000015 m. The localized linked collection is instantiated once and not directly parented in the master root. Applying the marker and source-local parent transforms yields campus-world bounds [[-300.47247314453125, -275.0757141113281], [278.157470703125, 301.62567138671875], [-0.15000000596046448, 9.0]]; maximum difference from the independently graded pre-localization campus-world bounds [[-300.47247314453125, -275.0757141113281], [278.157470703125, 301.62567138671875], [-0.15000000596046448, 9.0]] is 0.000000 m.
- **Evidence-backed height, floors, and roof form**: 1.50/2.0. Integrated geometry is unchanged from the previously graded model. The April 2026 Street View supports two visible stories, the left gable, shallow dark roof and small dormers; the old exact-address listing also describes bathrooms on each floor.
- **Facade, entrance, and distinctive architecture**: 1.80/2.0. The saved exact-address panorama and exterior preview support the model’s red brick, left gabled wing, white-columned portico, red entry door, pale trim, shutters and roof dormers. The asset also contains a cutaway interior with schematic rooms and circulation.
- **Modular export, portability, and evidence completeness**: 1.95/2.0. Fresh-open master links the expected source path C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_house_301841254_29ab02d.blend; manifest type is detailed/local-coordinate; marker and collection references resolve; exactly one collection-instance object exists and no duplicate direct-linked child is present. The integrated source collection contains 1 mesh objects and 12 materials. The previous fresh-open asset check found no external image dependencies; master-linked image paths checked here: [].

## Findings

- Purdue GIS Shape__Area/Shape__Length fields materially disagree with geometry-derived area/perimeter; the vertex polygon is used, but the official attribute discrepancy remains unresolved.
- Purdue GIS NUM_LEVELS/CountOfFlo fields report one level, conflicting with the facade photo and historical listing. Heights and roof pitch remain estimates; no measured elevation or construction drawings are available.
- Hidden elevations and exact facade dimensions are not verified; interior room layout is schematic without an as-built floor plan.
