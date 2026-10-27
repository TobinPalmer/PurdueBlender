# Zeta Beta Tau / 900 David Ross crosswalk review

**Review date:** 2026-10-26  
**Assigned organization:** Zeta Beta Tau, Alpha Alpha Chapter, Purdue University  
**Candidate site:** 900 David Ross Road, West Lafayette, Indiana 47906

## Finding

The evidence supports one physical chapter-house site at 900 David Ross Rd. Purdue's building GIS returns a single footprint there, FID 762, but labels it `Phi Kappa Theta` (`SOFKH`). That label is historically supported: Purdue's 2007 investigation names the Phi Kappa Theta house at this address. Later evidence identifies the same address as Zeta Beta Tau: ZBT's national chapter-house photo, uploaded in 2017, visibly shows its Alpha Alpha sign with the 900 David Ross address; a Purdue Exponent 2018 FSCL report lists ZBT at 900 David Ross; and ZBT's current Purdue contact and rush pages identify this address for the chapter and Fall 2026 rush events.

The most plausible explanation is an occupancy transition or a stale Purdue GIS organization label. The sources do not document when the transition occurred, and they do not prove whether the recently re-established Purdue Phi Kappa Theta colony ever temporarily shared the facility. They do not support creating a second physical building at this address. Keep the identity and asset crosswalk flagged for coordinator review.

## GIS source and geometry

- Provider: Purdue University GIS, `BuildingShapesZip4` ArcGIS FeatureServer layer 0.
- Feature: FID 762; `BUILDING_N=Phi Kappa Theta`, `BLDG_ABBR=SOFKH`, `ADDRESS=900 David Ross Rd`, `OWNER=GREEK`, `Layer=BLDG Building Private Owned`.
- Query URL: <https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D762&outFields=*&returnGeometry=true&outSR=4326&f=pjson>
- Snapshot: [Purdue GIS FID 762 JSON](sources/purdue_gis_fid762_2026-10-26_wgs84.json), retrieved 2026-10-26; geometry returned as WGS84 longitude/latitude.
- Applying the project's documented local approximation (X = (longitude + 86.9137) × 111412.84 × cos(40.4274°); Y = (latitude − 40.4274) × 111040) gives bounds X −994.483…−952.059 m, Y 721.324…775.790 m and ring area about 892.49 m². This is a map-footprint comparison, not surveyed wall geometry. The GIS `Shape__Area` attribute is 1542.914 in undocumented source units and conflicts with area recomputed from the returned ring; the ring is the geometry used for the bounds/area estimate.
- The GIS record has no `BUILT`, `OCCUPIED`, `DEMO`, or edit timestamps. `PU_Occupie=N` and `OWNER=GREEK`; neither field resolves chapter occupancy.
- The county assessor parcel response contains one address record, 900 DAVID ROSS RD, parcel 79-06-13-476-004.000-029. This supports the address site but does not identify the occupant. See [county parcel snapshot](sources/tippecanoe_assessor_parcel_900_david_ross_2026-10-26.json).

## Identity evidence, in date order

1. **2007, Phi Kappa Theta.** Purdue's official investigative report, page 6, places the house of Phi Kappa Theta at 900 David Ross Road. See [source PDF](sources/purdue_2007_official_investigation.pdf) and [Purdue report page](https://www.purdue.edu/uns/x/2007b/070702RimkusFinal.pdf).
2. **2017, Zeta Beta Tau.** ZBT's national Alpha Alpha locator identifies the photograph as that chapter's house photo. The photo itself bears the `ZBT`, `ALPHA ALPHA CHAPTER`, and `900 David Ross Road` signs. See [captured locator page](sources/zbt_national_alpha_alpha_locator_2026-10-26.html), [photo snapshot](sources/zbt_alpha_alpha_chapter_house_photo.jpg), and [live locator](https://zbt.org/undergraduates/chapter-locator/alpha-alpha-purdue-university/). The upload path contains `2017/10`; no capture date is asserted.
3. **2018, Zeta Beta Tau.** The Purdue Exponent's FSCL report lists Zeta Beta Tau at 900 David Ross Road. See the source PDF in [sources](sources/purdue_exponent_2018_fscl_report.pdf) and the [Exponent article PDF](https://bloximages.newyork1.vip.townnews.com/purdueexponent.org/content/tncms/assets/v3/editorial/c/c7/cc7ac664-843e-11e7-bdd5-335a6bc6456b/5bc88e6c8b486.pdf.pdf), page 20.
4. **2026, Zeta Beta Tau.** ZBT's current Purdue contact page states 900 David Ross Road, and its current homepage says Fall 2026 rush events will be at 900 David Ross Road. See [captured contact page](sources/zbt_purdue_contact_2026-10-26.html), [captured homepage](sources/zbt_purdue_homepage_2026-10-26.html), [live contact page](https://zbtpurdue.com/contact/), and [live homepage](https://zbtpurdue.com/).
5. **Current Phi Kappa Theta listing does not confirm the same facility.** Purdue BoilerLink describes Phi Kappa Theta as the newest fraternity and lists its contact email, but its public address field is blank. See [Purdue BoilerLink organization listing](https://boilerlink.purdue.edu/organization/phikappatheta). This leaves a possible new occupancy unresolved; it is not affirmative evidence that Phi Kappa Theta currently uses 900 David Ross.

## Existing candidate assets and ownership constraint

The nearest manifest asset is `massing_house_301841332_9b3bd1f`, whose center is about 8.4 m from the FID 762 bounds center. The current root README assigns that unverified candidate to Tobin as Phi Kappa Theta. A second unverified candidate, `massing_house_301841334_fa7e5a2`, is also nearby, with its center about 15.9 m from FID 762's bounds center. Both are outside this agent's write assignment and were inspected read-only.

`massing_house_301841332_9b3bd1f` is an eight-vertex, four-corner extrusion. Its base ring is near part of FID 762, but it does not represent all of the returned 13-vertex GIS ring: the directed vertex-to-vertex Hausdorff distances are about 1.85 m from the asset ring to the GIS ring and 33.62 m from the GIS ring to the asset ring. This shows the candidate deserves a geometry review; it does not establish the correct physical wall footprint. The read-only extraction is preserved in `candidate_base_rings.json` and `inspect_existing_candidates.py` / `export_existing_candidate_rings.py`.

No existing asset or shared tracker was changed. **Coordinator action is required before assigning FID 762 to ZBT, modifying the Tobin-owned candidate, or creating a second asset at the same site.** If this assignment represents the building currently used by ZBT, the clean resolution is a coordinated crosswalk/ownership handoff for the existing physical building, with Phi Kappa Theta's current facility independently checked before the Rossen assignment is closed.
