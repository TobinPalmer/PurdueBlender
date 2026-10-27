# Heine Pharmacy — R1 facade revision

## Asset and scope

- Manifest ID: `heine_pharmacy`
- Stable source library: `modular/buildings/heine_pharmacy.blend`
- Export collection: `Asset_heine_pharmacy` (retained)
- GIS feature: Purdue campus BuildingShapesZip4, layer 0, FID 606, `BLDG_ABBR=RHPH`
- Local frame: retained. The GIS-derived shell remains within X `[-36.1687, 36.1687]` m, Y `[-33.9912, 33.9912]` m, Z `[-1.0, 22.0]` m; manifest campus origin remains `[-193.8421863, 259.6049600]` m.

## Evidence

1. **Purdue GIS footprint** — official Purdue University ArcGIS FeatureServer layer 0, FID 606. Retrieved 2026-10-22; the raw WGS84 response is preserved in [`heine_pharmacy_gis_feature.json`](heine_pharmacy_gis_feature.json). The source response requested `outSR=4326`; source date and survey tolerance are not supplied. Geometry was transformed using the repository's approximate local geographic mapping: `X=(longitude + 86.9137) × 84810.6041654`, `Y=(latitude - 40.4274) × 111040`, metres. This is not a surveyed CRS. The existing mesh retains this footprint; the facade revision did not change the shell, origin, or master placement.
2. **Exterior composition** — Nothda, “Purdue University Robert E Heine Pharmacy Building,” photograph taken 2023-10-18, retrieved 2026-10-27 from [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Purdue_University_Robert_E_Heine_Pharmacy_Building.jpg), CC BY-SA 4.0. The source image is [`heine_exterior_2023.jpg`](heine_exterior_2023.jpg). The visible southeast elevation shows seven narrow, vertically repeated dark window bays, red/orange brick fields, pale horizontal masonry courses, and a tall stone arcade at the public entrance. Bay count and broad composition are photo-supported; exact dimensions and stationing are not, because the photo is perspective-distorted and partly occluded by trees.
3. **Stories and uses** — Purdue Office of Emergency Preparedness, [RHPH Building Emergency Plan](https://www.purdue.edu/operations/emergency-preparedness/rhph/), page revision dated 2026-03-13. Retrieved 2026-10-27; a raw HTML snapshot is preserved as [`purdue_oep_rhph.html`](purdue_oep_rhph.html). It describes five above-ground floors, one lower G-floor, a basement, and uses including offices, classrooms, student/research laboratories, Pharmacy Stores, and a licensed Pharmacy. The model uses five window rows on the photographed elevation to represent the five above-grade floors. It does not infer the lower floor's buried/exposed extent from the GIS level fields.
4. **Interior character** — [Design Collaborative's Heine renovation project](https://designcollaborative.com/dc-project/purdue-university-robert-e-heine-pharmacy-building/) describes a 7,500-square-foot library renovation with study and collaboration zones. This supports general student-study uses, not exact room boundaries. Interior partitions, lab/work cues, and furniture in the asset remain explicitly schematic. An older first-floor plan URL recorded in the inherited batch evidence no longer resolves; no exact floor-plan registration was available for this revision.

## R1 edits

- Replaced the 54 generic window panes on the photographed entry elevation and removed its oversized full-height curtainwall bay and 11 overly dense pale vertical strips.
- Added seven narrow vertical window stacks with five above-grade rows each (35 glazing panels), slim mullions, limestone reveals/sills, and selected stone spandrels. The remaining elevations retain their previous GIS-derived window distribution pending comparable imagery.
- Rebuilt the shell masonry shader with a face-relative procedural brick bond and shallow mortar relief. Its projection follows each slanted wall elevation, so horizontal courses stay horizontal instead of stretching into vertical streaks. No external texture dependency was added.
- Retained the GIS shell, flat parapet/roof, entry canopy/arcade, pharmacy signage, and schematic interior. No coordinates or master files were edited.

## Fresh-open validation

Blender 5.2.3 LTS reopened the saved library in a separate background process. Validation passed for the stable collection, preserved shell bounds, 35 new facade panes, 63 stone surround/spandrel faces, 35 mullion faces, removal of the superseded facade objects, connected brick color/bump nodes, and absence of missing external texture paths. The reopened render is [`heine_pharmacy_fresh_open.png`](heine_pharmacy_fresh_open.png); structured results are in [`fresh_open_verification.json`](fresh_open_verification.json).

The façade's exact window sizes, dimensions of the historic entrance arcade, unseen elevations, absolute wall/roof height, extent of lower levels, and room-by-room interior remain estimated or unverified. R1 is ready for independent grading; no independent grade is claimed in this record.

## R2 response to independent review

The independent R1 review scored the asset **7.6/10** and identified two concrete facade gaps: the model still read as five small panes per bay, and the entrance arcade was too small and light. The R2 edit targets those points. It does not claim a new score; the asset is ready for a fresh independent R2 review.

- Replaced the five-level grid on the photographed elevation with seven narrow vertical glazing slots. Each slot now has two long glass sections and one broad pale stone spandrel panel between them. Fourteen long glazing faces, 21 pale-stone faces (spandrels plus side reveals), and 14 restrained center rails make the facade read vertically instead of as a small-window matrix.
- Rebuilt the entrance as four large, extruded stone arches with five substantial supporting piers and a broad crown beam. The arcade is approximately 17.25 m wide and reaches 7.35 m in the local frame, about 45% of the selected 38.088 m facade edge. Its position reuses the existing entry center. Its scale is an estimate guided by the visible proportions of the dated oblique photograph, not a surveyed measurement.
- Preserved the GIS structural shell, local frame, exported collection name, and master campus origin. The structural shell still has bounds X `[-36.1687, 36.1687]` m, Y `[-33.9912, 33.9912]` m, Z `[-1, 22]` m. No manifest, shared index, README, or master blend was changed.
- Rebuilt and saved with Blender 5.2.3, then reopened the exact saved asset in a separate background Blender process. Fresh-open validation passed: 108 objects / 105 mesh objects in `Asset_heine_pharmacy`, 14 long glazing faces, 21 stone spandrel/reveal faces, four modeled arches (328 arch-band faces), 78 pier faces, six crown-beam faces, and zero missing external texture files. The fresh-open render is [`heine_pharmacy_fresh_open_r2.png`](heine_pharmacy_fresh_open_r2.png); machine-readable results are in [`fresh_open_verification_r2.json`](fresh_open_verification_r2.json), and build measurements are in [`r2_build_summary.json`](r2_build_summary.json).
- Exact saved asset SHA-256: `962fe3572903061e9d590759118ea945b28d32c338a0a5f6b8ce40da18e7d9d7`.

### Remaining limits

The photo supports the visible seven-slot/four-arch composition but is oblique and partly occluded. It does not establish exact opening widths, arch radii, parapet details, hidden elevations, absolute height, lower-level exposure, or interior room boundaries. Those remain estimated or unverified. The shared manifest still has its historical object count; the coordinator should synchronize it after accepting this asset during integration.
