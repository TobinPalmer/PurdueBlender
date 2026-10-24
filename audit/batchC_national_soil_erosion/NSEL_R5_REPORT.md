# National Soil Erosion Research Laboratory — R5

## Revision summary

R5 responds to the independent R4 grade of 7.9/10. It reduces the uniformly gray interior read with a warmer, more differentiated material palette and adds restrained panel bands, wall girts, and upper liner fields. It also adds a street-distance exterior render that includes the roof profile, a broad portion of the building facade, entrance, and readable laboratory lettering.

The interior uses warm mineral green-gray on the lower wall bands, soft green-gray upper panels, warm-metal trim, a warmer ceiling, teal lab cabinets, clearer stainless work surfaces, and clay-colored sample trays. The new wall divisions provide scale and structure without adding unsupported windows, doors, skylights, or rooftop details. Render lighting now uses warmer key light with neutral fill; the model itself retains its reusable interior luminaires.

The exterior camera sits at an illustrative street-distance view, using a 48 mm perspective lens to keep the main facade and roof legible while enlarging the raised lettering relative to the full-building R3 view. It frames the building sign and entrance alongside the facade and roof. This is a visualization composition, not a verified Google Street View camera position. No exterior building geometry or sign size changed in R5.

## Validation

`nsel_revision_r5_validation.json` records a fresh Blender 5.2.3 LTS reopen, asset SHA-256, R4 enclosure and circulation checks, R5 wall-band/girt/cladding/material checks, required render presence, and the previously recorded FID 242 footprint comparison. All recorded checks pass. The roof outline remains within about 0.000006 m of the retained FID 242 GIS polygon at 0.2 m sample spacing. That is a comparison to the supplied GIS snapshot, not a statement of survey accuracy.

SHA-256: `a6d3b84af0c5c3efd0ddab6d20f223eca7723a7f3736c5330021d3b2956f6a02`

## Renders

- `nsel_revision_r5_street_distance.png` — broad exterior view with facade, roof profile, entrance, and lettering
- `nsel_revision_r5_high_bay_context.png` — warmer cutaway of flume, enclosure, work area, and circulation

## Sources and uncertainty

- [USDA ARS K7567-11 hydraulics-lab photo](https://www.ars.usda.gov/oc/images/photos/apr97/k7567-11/) supports a comparable enclosed flume-lab type and general work context; it does not document NSEL's interior finishes or dimensions.
- [2018 Purdue NSEL exterior photograph](https://ppgta.ufms.br/files/2018/02/Grupo-Purdue.jpg) supports the entrance lettering and blank-brick facade relationship; its lettering dimensions are estimates.
- [Purdue BuildingShapes feature service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0), FID 242, remains the footprint reference.
- [Indiana Current Imagery](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer) supports broad roof plan only.

No NSEL interior plan or interior photo has been found in the evidence set. R5 wall bands, cladding colors, girts, station locations, and lighting are interpretive, not verified original finishes or fixtures. The east/west roof heights remain approximate (about 5.20 m and 7.32 m) from 5-ft DSM samples and interpolated DTM ground.

R5 is ready for an independent grade; no R5 score has been received. Only the NSEL source blend and `audit/batchC_national_soil_erosion/` were edited. No master, shared index, README, manifest, other building asset, or commit was changed.
