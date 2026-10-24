# National Soil Erosion Research Laboratory — R4

## Revision summary

R4 responds to the independent R3 score of 7.8/10. It encloses the flume display in a high-bay room and adds a small, legible soil-preparation/work zone with clear circulation. A separate exterior detail render uses warm key and soft fill lighting so the raised address and laboratory lettering read clearly.

The R4 scene adds four high-bay liner walls, a ceiling plane, panel joints, and base guards around the existing R3 floor and portal frame concept. It retains the east-side service walkway. A stainless preparation bench, shallow sample trays, a smaller instrument table, sample cart, aisle-edge markings, and overhead diffusers supply visible work context. The model leaves an estimated 1.9 m aisle between the preparation bench and flume work zone. These additions make the flume read as equipment inside a bounded research-lab space and make the operator route easier to follow.

The USDA ARS K7567-11 photograph is a comparable hydraulics-lab reference. It shows an enclosed industrial bay, a hard floor, a long flume with working platforms and supports, and nearby research activity. It supports the typology and work context, not the exact NSEL room dimensions, station placement, fixtures, or circulation. No NSEL interior plan or interior photograph is present in the current evidence set. The new interior arrangement is therefore explicitly illustrative.

The exterior sign geometry is unchanged in R4. The new close render uses a front-facing perspective, warm directional key, and cool fill to improve relief and legibility. The 2018 visitor photograph remains the source for the building name, agency lettering, address plaque, and blank brick field. Its sign dimensions are estimated from the photo rather than measured.

I made no roof or exterior wall height changes. The 5-ft DSM and interpolated DTM do not support survey-precision roof heights. The approximate east/west split remains 5.20 m and 7.32 m.

## Validation

`nsel_revision_r4_validation.json` records a fresh reopen in Blender 5.2.3 LTS, the source asset SHA-256, legacy footprint/roof-edge checks, the new enclosure and work-context checks, and render-file presence. Every recorded check passes. The roof outline continues to match the retained FID 242 GIS polygon within about 0.000006 m at 0.2 m sampling; this is a comparison against the supplied GIS snapshot, not proof of survey accuracy.

SHA-256: `9d4504aa3c00bf9381a107f77cc455efd9cf2b661c1f821250876fb0db1b643c`

## Renders

- `nsel_revision_r4_enclosed_high_bay_cutaway.png` — flume, enclosure, work zones, and clear aisle
- `nsel_revision_r4_exterior_sign_lit.png` — exterior entrance and readable lettering under warm/cool soft lighting

## Sources and limitations

- [USDA ARS K7567-11 hydraulics-lab photo](https://www.ars.usda.gov/oc/images/photos/apr97/k7567-11/) — comparable flume-lab setting; does not establish NSEL room layout or dimensions.
- [2018 Purdue NSEL exterior photograph](https://ppgta.ufms.br/files/2018/02/Grupo-Purdue.jpg) — facade lettering and blank brick relationship; no interior view or measured elevations.
- [Purdue BuildingShapes feature service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0) — FID 242 footprint reference.
- [Indiana Current Imagery](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer) — roof plan context, not detailed height or interior evidence.

The room envelope, fixtures, benches, work locations, cart, and circulation paint are schematic and should not be mistaken for a surveyed or verified NSEL interior. Existing lidar-derived roof heights remain approximate. R4 is ready for a fresh independent grade; no R4 score has been received.

Files changed for R4: `modular/buildings/national_soil_erosion_laboratory.blend` and the R4 script, validation, render, data, and report files in `audit/batchC_national_soil_erosion/`. No master, shared index, README, manifest, other building asset, or commit was changed.
