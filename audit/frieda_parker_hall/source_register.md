# Frieda Parker Hall source register

Retrieved/reviewed 2026-10-27 (America/Indianapolis). The building asset is
`modular/buildings/frieda_parker_hall.blend`; identity remains
`frieda_parker_hall` / `Asset_frieda_parker_hall` / `Building_frieda_parker_hall`.

## Primary sources

1. [Purdue University Housing — Parker North](https://www.housing.purdue.edu/my-housing/options/residence-halls/parker-north.html)
   - Official residence hall context, six-story scale, upper-class suites and
     semi-suites, common lounges/study spaces, and ground-floor dining/retail.
   - Local snapshot: `sources/purdue_housing_frieda_parker.html`.
   - The page describes the hall as opening in Fall 2020; it includes plans and
     room dimensions but no whole-building elevation drawings.
2. [Mackey Mitchell Architects — Griffin Hall (Frieda Parker Hall)](https://www.mackeymitchell.com/projects/griffin-hall/)
   - Original architect's project page and exterior photographs. The photos
     establish the red-brick volumes, glazed vertical connector/upper passage,
     and active ground-floor frontage. Page also gives 570 beds and 149,000 sf.
   - Local page snapshot: `sources/mackey_mitchell_project.html`.
   - Saved official image files: `18220_00_N59_jpg2000rgb-1920x1080.jpg`,
     `G2-1920x1080.jpg`, `G4-1920x1080.jpg`, `G7-1920x1080.jpg`, and
     `G9-1920x1080.jpg`, all in `sources/`.
3. [Purdue campus building-shape layer, feature 409](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D409&outFields=%2A&returnGeometry=true&outSR=4326&f=geojson)
   - Feature ID/FID 409; `BLDG_ABBR=PKRF`; “Frieda Parker Residence Hall”;
     address 401 N Russell Street; source attributes report occupied 2020-08-31
     and has one polygon exterior ring (43 coordinates including the repeated
     closing point). Requested
     response CRS is EPSG:4326. Raw response:
     `sources/purdue_arcgis_fid_409.geojson`.

## GIS comparison and placement

The project map uses an approximate local campus frame, not a surveyed CRS:

```text
X_project = (longitude + 86.9137) * 84810.60416539927 m/degree
Y_project = (latitude - 40.4274) * 111040.0 m/degree
Z = up, meters
X_local = X_project - (-499.7250061)
Y_local = Y_project - 97.475
```

The last two offsets are the supplied master placement origin; they were not
changed. Applying this transform to all 42 unique GIS vertices yields an
approximate local polygon envelope X [-35.4133, 24.4635] m, Y [-48.8670,
49.5754] m. Its center is approximately (-5.4749, 0.3542) m in the asset's
local frame. This differs from the supplied placement origin alignment and is
recorded as an unresolved map/model alignment uncertainty; this task retained
the assigned placement and did not shift the building. The GIS polygon's
source geometry may be generalized and its metadata does not state positional
accuracy. Do not treat the envelope as a certified survey.

## Model decisions and uncertainty

The source model's nonbuilding-inclusive detail bounds are about X
[-35.7600, 35.7250], Y [-49.7500, 49.7250], Z [0, 25.8] m. Those full bounds
include detached outdoor paving at the east side; they should not be treated as
the structural building envelope. Before the R2 plan correction, the four
major upper shell boxes had a union area of 3,180.12 m². Against the 2,315.24 m²
GIS polygon their approximate IoU was 0.69194. The retained three shells occupy
2,401.98 m², of which 2,232.65 m² intersects GIS (IoU 0.89860). Their combined
envelope is X [-35.475, 22.725], Y [-49.475, 49.525] m, close to the GIS
envelope above. The comparison is approximate and does not establish survey
accuracy.

Object-by-object comparison found the pre-existing `Frieda_NorthWing_Upper`
rectangle covered 778.14 m², but only 14.75 m² intersected the transformed GIS
polygon; 763.39 m² (98.1%) was outside. That unsupported upper block was
removed. The other upper blocks individually overlap the transformed GIS ring
over 88.4% (WestWing), 93.4% (EastWing South), and 97.1% (EastWing North) of
their plan areas. Their residual edge differences were retained because the
coordinate conversion is approximate and the GIS source does not publish
positional accuracy. The ground-ceiling plate is 89.5% within the polygon; the
CFA and Jersey Mike's floor rectangles are 96.4% and 100% within. The 391 m²
outdoor patio slab lies outside the building polygon and is classified as site
paving, not building shell. Per-object metrics and overlay are in
`footprint_comparison.json` and `footprint_overlay.png`.

The current source model includes the ground-floor shops, interior furnishing,
retained brick wings, main east facade, roof details, and open ground-level
passage. This pass also removes the opaque upper bridge block and rebuilds the
visible bridge envelope as glazing with mullions, based on official architect
exterior images. Repeated punched windows were added to previously blank side
elevations, based on the architect's oblique photographs and the hall's
documented residential use.

Exact side-elevation bay spacing, floor-to-floor heights, and mullion/shop
drawings were not found in the reviewed official sources. Side window rhythm
and bridge subdivision are therefore visual interpretations, not measured
claims. No external textures or linked assets are required. The evidence
images are Workbench previews from the saved asset, not photorealistic renders.
