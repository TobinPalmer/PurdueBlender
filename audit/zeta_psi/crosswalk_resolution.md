# Zeta Psi / FID 748 crosswalk review

**Review date:** 2026-10-26  
**Assigned candidate:** Purdue GIS FID 748, stable asset `massing_house_301841600_c1351aa`  
**Candidate file:** `modular/buildings/massing_house_301841600_c1351aa.blend`  
**Disposition:** The candidate is the physical building at 950 David Ross Road. Do not detail it as an exclusively Zeta Psi building or relabel it as Chi Psi yet: Purdue's current IFC-linked Zeta Psi account self-reports the same address and says “Rechartered 2024,” while Chi Psi's July 2024 newsletter identifies the same single building as its new Lodge. The unique current occupant/arrangement is unresolved.

## Evidence

1. **Purdue GIS identity and address.** The raw FID 748 query (`sources/purdue_gis_FID748_2026-10-26.json`) returns `BUILDING_N=Zeta Psi`, `BLDG_ABBR=SOZY`, `OWNER=GREEK`, and `ADDRESS=950 David Ross Rd`. The Purdue BuildingShapes query layer metadata is preserved alongside it. The feature polygon's source `Shape__Area` is 1,177.92, while its ring area after applying the project's approximate local conversion is 681.35 m². That GIS polygon does not tightly match the candidate's base shell.

2. **Candidate-to-current-footprint match.** The old candidate shell's four ground vertices, read from the saved Blender file with Blender 5.2.3, define an approximately 464.54 m² rectangle. Against the Purdue GIS FID 748 ring, candidate IoU is 0.422 and centroid separation is 6.24 m. Against Indiana's 2018 LiDAR footprint at the same address (`sources/indiana_lidar_footprints_near_fid748_2026-10-26.json`, OBJECTID 409718), IoU is 0.829, 91.4% of the candidate is covered, and centroid separation is 1.61 m. This establishes that the asset models the structure at the parcel, but does not establish the occupant.

3. **Parcel location.** The Tippecanoe County GIS parcel query (`sources/tippecanoe_parcel_at_fid748_2026-10-26.json`) independently returns `950 DAVID ROSS RD`, parcel `79-06-13-476-005.000-029`, around this structure. County parcel GIS is the parcel source linked from Tippecanoe County's official property-tax/GIS information page.

4. **Chi Psi identifies the address and the pictured lodge.** Chi Psi's own July 17, 2024 Purdue Alpha Epsilon Tau newsletter (`sources/chipsi_alumni_newsletter_summer_2024.pdf`; page 3 rendering at `sources/chipsi_newsletter_p3_preview.png`) announces a lodge-opening ceremony for September 14, 2024, gives the address as `950 David Ross Rd`, and captions the pictured two-story brick building “The new Chi Psi Lodge at Purdue University.” The page's photo shows a broad two-story brick house with paired tall front gables and a centered entrance. The original PDF is retained.

5. **Both chapters' primary sources point to 950, and Zeta Psi reports a move.** The official Zeta Psi 2023 chapter report (`sources/zetapsi_tau_gamma_2023_chapter_report.pdf`, p. 10) says Tau Gamma “This year we moved our chapter house and had a fresh start.” It does not identify the old or new street address. Separately, the official Tau Gamma Instagram account linked by Purdue's current IFC chapter page has a captured profile snapshot (`sources/zetapsipurdue_instagram_page.html`) whose self-description says `950 David Ross Rd` and `Rechartered 2024`. Chi Psi's own dated 2024 newsletter also places its Lodge at 950 David Ross Rd. Both claims therefore point to the same parcel and sole mapped building, but contradict each other as exclusive occupancy claims. The Zeta Psi profile capture does not expose dated post captions sufficient to tell whether its bio is stale, whether organizations share the facility, or whether the chapter relocated again after Chi Psi's opening.

6. **Parcel scope contains one mapped building.** A 2018 Indiana LiDAR query over the 950 parcel area returned three nearby footprints. Point queries through Tippecanoe County parcel GIS place the other two at 900 David Ross Rd and 925 Hilltop Dr; only OBJECTID 409718 is on 950 DAVID ROSS RD, parcel `79-06-13-476-005.000-029`. Thus the address overlap is not explained by two separate mapped buildings within this parcel.

7. **Official chapter presence is distinct from sole occupancy.** The national Zeta Psi Indiana page lists Tau Gamma at Purdue, est. 1968, but does not give a street address or house photo. Purdue's current IFC page lists Zeta Psi and links the account that self-reports 950 David Ross Rd; the historical Fall 2021 Purdue roster also names a Zeta Psi officer. These prove chapter presence at the respective source times and a current-looking self-reported address, but do not reconcile the explicit Chi Psi Lodge use at the same address. The national chapter page and current Purdue IFC HTML are preserved.

## Crosswalk recommendation

- Keep `FID 748 → physical building at 950 David Ross Rd → massing_house_301841600_c1351aa` as a **spatial** crosswalk only. The candidate strongly matches the 2018 LiDAR outline, but its mismatch to the Purdue FID ring must remain visible.
- Change the semantic status from “confirmed active Zeta Psi house” to **shared-address identity conflict / exclusive occupancy unverified**. Available primary records support Chi Psi lodge use and Zeta Psi's self-reported address simultaneously; the Zeta Psi 2023 chapter report additionally records a house move.
- No other active Zeta Psi facility/address was identified from the available official sources. The official report's “new facility” street is unspecified. Do not infer a different building or geocode a third-party “West St.” reference.
- Coordinator should keep the Rossen Zeta Psi assignment unresolved pending direct clarification from the chapters/Purdue, or a dated and independently geolocated source that reconciles the shared address. Do not detail, grade, or claim this candidate completes Zeta Psi while exclusive identity is unclear. If coordinator accepts an explicit dual-occupancy record or a later source resolves current occupants, reassess then.

## Reproducible comparison

Measurements and matching ratios are in `footprint_comparison.json`. Candidate Blender file SHA-256 at review time: `7e6194d86eb4ce7a75303ba27605d0a907425b81ffd9d0b14204e6dbcc8a77e4`. No edits were made to the asset, shared indexes, or the master blend.
