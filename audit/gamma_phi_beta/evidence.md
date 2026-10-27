# Gamma Phi Beta / Delta Iota — detailed asset R0

## Identity and assignment

- README assignment: **Gamma Phi Beta**, Tobin; FID 759; massing candidate `modular/buildings/massing_house_301841329_bed5cb6.blend`.
- Purdue ArcGIS BuildingShapesZip4, layer 0, FID 759 explicitly names **Gamma Phi Beta**, abbreviation `SOGFB`, address **810 David Ross Rd**, owner type `GREEK`. The raw feature response is preserved in [`gis_feature_fid_759.json`](gis_feature_fid_759.json), retrieved 2026-10-27. The query requested WGS84 (`outSR=4326`); the source geometry has no collection/survey date or stated positional tolerance.
- Gamma Phi Beta International's [Delta Iota Chapter (Purdue)](https://www.gammaphibeta.org/gpb/9f99b6a9-4119-4374-91f9-0ab935c0bb24/Delta-Iota-Chapter) identifies the chapter and displays the captioned “Delta Iota Chapter facility in fall 1979.” The captioned archival image is preserved as [`official_delta_iota_house_fall_1979.jpg`](official_delta_iota_house_fall_1979.jpg). The linked chapter site and image page HTML are preserved alongside it. The image archive page does not list a photographer or license; this copy is a modeling reference and is not used as a texture.
- The [Fall 1979 issue of *The Crescent*](https://www.gpbarchives.org/wp-content/uploads/2017/08/1979_Fall.pdf), Gamma Phi Beta's magazine, is preserved as [`the_crescent_fall_1979.pdf`](the_crescent_fall_1979.pdf). Its Delta Iota article describes a new 18,000-square-foot chapter house for 80 residents in a rolling hillside setting; contemporary steel construction, an acrylic-coated outside steel skin and aluminized-steel roof; a hand-carved front door; and dining, study, and second-/third-floor living spaces. The chapter house is credited to architect Drogo G. Panich and contractor McCarthy Davis Company. These details support the broad form and materials, not a measured elevation or exact floor plan.
- Purdue's [FSCL chapter roster](https://www.purdue.edu/fscl/councils/pha/chapters.php) lists Gamma Phi Beta and links its chapter site. A [Purdue BoilerLink event](https://boilerlink.purdue.edu/event/11563982) uses the chapter location 810 David Ross Rd. Snapshots are preserved in this folder. These establish the current chapter/location crosswalk; they do not establish that every 1979 facade detail remains unchanged.

## GIS footprint and frame

The official FID 759 ring has 12 unique WGS84 vertices. It was projected using the project's approximate local transform:

```text
X = (longitude + 86.9137) * 111412.84 * cos(radians(40.4274))
Y = (latitude - 40.4274) * 111040
```

The transformed GIS bounds center used as the detailed asset placement origin is `[-1030.3176174569167, 706.9364654213132]` metres. The candidate massing remains untouched and in campus coordinates. Its old world AABB was a screening proxy only; the exact FID 759 GIS polygon now defines the new asset shell. The `audit/master_building_audit.json` status had correctly treated that candidate as a spatial-only crosswalk, so identity is based on the GIS attributes plus the independent chapter sources above, not AABB similarity alone.

The transformed ring's shoelace area is 671.190 m². The ArcGIS response's `Shape__Area` attribute is 1160.34375 (advertised units: metres); these values conflict under the approximate project transform. The raw geometry has no survey tolerance, and this local transform is not a surveyed CRS. Accordingly the model records the ring match exactly against the transformed raw vertex coordinates, but does not claim the transformed area is survey-grade. The area-field discrepancy should remain visible to the master reviewer.

## Model

- Proposed stable manifest entry: `id=gamma_phi_beta`, `kind=detailed`, `file=buildings/gamma_phi_beta.blend`, `collection=Asset_gamma_phi_beta`, `scene=Building_gamma_phi_beta`, `placement_origin_xy_m=[-1030.3176174569167,706.9364654213132]`, `object_count=255`. A machine-readable proposal is [`manifest_proposal.json`](manifest_proposal.json). Shared files were not edited.
- The detailed asset contains 12 GIS-edge wall panels with the projected footprint ring, three modeled above-grade floor bands, vertically ribbed coated-metal cladding, grouped vertical windows, horizontal story bands, low flat aluminized-steel roof and parapet, and an understated entrance canopy/landing with a wood door. The material colors are estimates because the 1979 photograph is monochrome and no current authoritative color schedule was found.
- The entry is positioned by inference at the footprint's small projecting step, informed by the oblique house photograph. The image is not georegistered, so the exact entrance edge, orientation relative to the photo, and canopy dimensions remain uncertain.
- The interior has only plainly named schematic shared tables, benches, and partitions. The article supports dining/study and upper-floor living uses, but no georegisterable floor plan was found; no exact interior layout is claimed.
- Original massing source remains unchanged at [`massing_house_301841329_bed5cb6.blend`](../../modular/buildings/massing_house_301841329_bed5cb6.blend), SHA-256 `9564223f8dba92303781ea7f773dd2938d05aca903930f069c42d4f063e36f57`.

## Height and limits

The GIS feature gives `Extrution=12` and `NUM_LEVELS=1`; its source data do not document the height field's method. The 1979 chapter article mentions second- and third-floor living quarters, supporting three above-grade bands. The model uses three floors totaling approximately 12 m and treats the GIS extrusion value as a cross-check, not a measurement. The 1979 photo's hillside makes exposed lower-level count sensitive to viewing direction. No current georegistered facade image, measured elevation, survey, exact story-height data, or interior plan was available in this task. Absolute height, color, terrain response and facade bay dimensions remain estimated/unverified.

## Build and fresh-open validation

Blender 5.2.3 built and saved the dedicated asset. A separate background process reopened the exact saved file and rendered [`gamma_phi_beta_fresh_open.png`](gamma_phi_beta_fresh_open.png). Validation passed for scene/collection identity, 255 exported objects (all meshes), all 12 transformed GIS ring vertices appearing in the structural wall vertices at 0 m with 0.0 m maximum residual, unchanged original massing source, and zero missing external image textures. The measured detail-collection bounds are X `[-16.3078,16.3032]` m, Y `[-19.3935,19.8897]` m, Z `[-0.56,12.82]` m; the slight XY expansion is the modeled roof overhang and entrance stair/canopy envelope, not a changed GIS origin. Full machine-readable validation is in [`fresh_open_verification.json`](fresh_open_verification.json), build counts in [`build_summary.json`](build_summary.json), and the deterministic builder is [`build_gamma_phi_beta.py`](../../modular/buildings/build_gamma_phi_beta.py).

Exact saved asset SHA-256: `c9dbc1da41f87962022c39795751d797e0f5ff2a8aa0bf64cd89fa4257f89f25`.

The asset is ready for independent grading. No grade is claimed here. No README, manifest, index, master blend, other building, commit, or push was changed.
