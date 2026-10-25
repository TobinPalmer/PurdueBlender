# Morgan J. Burke Boilermaker Aquatic Center — R8 review candidate

R7 remained at **7.9/10**. The independent review asked for less block-like seating, readable integrated lights, wall-attached banners, and more facade depth. R8 follows the building-specific Arsee Engineers interior photo and the existing north-approach Street View evidence. No roof-height or campus-master placement claim is made.

## R8 changes

- Replaced the repeated tan seat blocks with 24 continuous satin-aluminum bleacher rows, dark nosings, and a center stair aisle. Purdue's published capacity is 625; the modeled tiers remain representative, not an as-built seating plan.
- Replaced short fixture blocks with 18 long linear diffusers and matching area lights. The specific fixture geometry/count/spacing/output are visual estimates, not a contractor schedule.
- Replaced floating overhead signs with six black wall panels and standoffs, spelling PURDUE in large gold letters. Their pattern, scale, and wall placement follow the Arsee photo qualitatively.
- Darkened and desaturated the ribbon glazing and added head/jamb reveals to north-facing glazing. Street View supports brick and ribbon glazing; the reveals are estimated architectural depth, not measured elevation data.
- Retained the existing roof/truss geometry and approximate site dressing without implying verified roof height or site placement.

## Sources and limitations

The [Arsee Engineers Aquatic Center photo](https://www.arsee-engineers.com/images/project/athletic/Purdue%20Aquatic%20Center.JPG) shows the exposed white trusses, linear pool lights, large black/gold wall lettering, aluminum bleacher banks, and central stair aisle. [Huston Electric](https://hustonelectric.com/project/purdue-aquatic-center/) documents LED fixtures installed above the competition and diving pools. The [north-approach Street View](https://www.google.com/maps/@?api=1&map_action=pano&pano=TdL92OGnlFSS8CxGuVLKDA) provides qualitative brick/ribbon-glazing/entry context but is not calibrated. Purdue RecWell publishes a 625-person spectator capacity.

The roof section/profile and eave/ridge heights remain unverified. Truss geometry, panel and fixture dimensions, seating capacity/layout, aisle details, and lighting schedule remain schematic or estimated. The facade reveal widths are visual estimates from uncalibrated imagery. The optional site collection remains approximate and un-georeferenced. The GIS check validates local footprint outline only; root is doing any master marker check separately.

## Validation and renders

Blender 5.2.3 reopened the saved source and passed the R8 validator. The asset contains 1,080 building objects, 96 objects in the R8 improvement collection, and no external image dependencies. All mesh objects have material assignments. The official GIS FID 896 polygon and structural shell each have 70 perimeter segments; the maximum bidirectional sampled outline error is 0.000002 m. This establishes local outline correspondence only, not campus-master placement or survey accuracy.

SHA-256: `eec37c28a65fc0c3d48feea6791bb4bbe92b0f218a4f8099689abca078b6aa9a`.

The four current R8 renders are `aquatic_r8_interior_lighting_banners.png`, `aquatic_r8_bleacher_aisle_detail.png`, `aquatic_r8_north_entry_approach.png`, and `aquatic_r8_north_facade_reveals.png` in this audit folder. The saved source, validation JSON, hash record, and renders are ready for an independent full-building review. No score is claimed yet.
