# National Soil Erosion Research Laboratory — R3

## Revision summary

R3 responds to the independent R2 score of 7.6/10. It gives the hydraulics flume a bounded high-bay lab context and makes the photographed exterior name legible in an exterior view.

The flume now sits on a concrete high-bay floor with three portal frames and a side service walkway. Existing A-frame supports, rails, controls, and test instrumentation remain around the channel. The USDA ARS K7567-11 photo supports this type of industrial research context: a long flume, hard floor, access platforms, structural supports, and related testing equipment. The new room dimensions and exact internal layout are illustrative estimates.

The 2018 exterior photo shows large raised lettering. The title lettering is now modeled about 0.50 m high and 11.8 m wide, with the two agency lines and address enlarged proportionally. Letter relief increased to make the sign read as raised metal letters. The size and position are still estimates from a visitor photo without a measured elevation. A closer exterior render makes the name readable; a separate full-building render preserves the overall model view.

I made no additional roof geometry changes. The current orthophoto supports the roof outline and broad zones, but not trustworthy roof heights, parapet dimensions, or rooftop equipment sizes. The high/low height split stays explicitly approximate.

## Validation

`nsel_revision_r3_validation.json` records a successful reopen in Blender 5.2.3, footprint-edge checks, presence of the new floor/frame/walkway, and the saved blend’s SHA-256.

SHA-256: `a3f8a7737e9d7b4e813ca5a0d19b8b784ddb0a7d4a842cb64c726f1c521ed95d`

The asset hash was independently checked after the validation record was written. Roof outlines still match the supplied FID 242 geometry to approximately 0.000006 m at 0.2 m sample spacing. That measures the model against the retained GIS snapshot and does not establish the snapshot’s real-world accuracy. The roof tops remain about 5.20 m on the east and 7.32 m on the west, estimated from 5-ft DSM cells and interpolated bare-earth DTM samples.

## Renders

- `nsel_revision_r3_exterior.png` — full exterior
- `nsel_revision_r3_exterior_name.png` — exterior name and entrance close view
- `nsel_revision_r3_roof_outline.png` — overhead roof view
- `nsel_revision_r3_hydraulics_high_bay.png` — flume with floor and high-bay frame context

## Sources and remaining uncertainty

- [Purdue BuildingShapes feature service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0), FID 242, supplies the footprint comparison.
- [2018 visitor photo](https://ppgta.ufms.br/files/2018/02/Grupo-Purdue.jpg) supports the enlarged lab name, USDA lines, address, and blank brick field. It does not provide survey dimensions.
- [USDA ARS K7567-11](https://www.ars.usda.gov/oc/images/photos/apr97/k7567-11/) supports the hydraulics-lab equipment type and general industrial setting, but not exact NSEL room dimensions, flume placement, or circulation.
- [Indiana Current Imagery ImageServer](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer), 2023 Tippecanoe imagery, supports the roof plan form. Its overhead imagery does not settle height or detailed facade depth.

R2’s independent score was 7.6/10. R3 is ready for a fresh independent grade; no R3 score has been received. The DSM-derived height split remains approximate, and interior circulation remains schematic. Only the NSEL asset and its dedicated audit folder were edited. No master, shared index, README, manifest, or other building was changed; no commit was made.
