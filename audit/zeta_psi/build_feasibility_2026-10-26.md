# FID 748 build feasibility assessment

**Assessment date:** 2026-10-26
**Assigned asset:** `massing_house_301841600_c1351aa`
**Candidate site:** Purdue GIS FID 748, 950 David Ross Road
**Decision:** A neutral model of the physical structure is conceptually possible without naming an exclusive occupant, but the available evidence is not sufficient to deliver and pass a detailed building asset now. Keep the Rossen Zeta Psi assignment open. Do not label the structure exclusively as Zeta Psi or Chi Psi.

## What the evidence supports

- Purdue GIS FID 748 identifies a Greek-owned building named Zeta Psi at 950 David Ross Road. The official county parcel query independently returns that situs address.
- An Indiana Geographic Information Office footprint from 2018 (OBJECTID 409718) spatially matches the existing massing shell well: IoU 0.829 and centroid separation 1.61 m. The local-coordinate comparison is approximate, not a survey.
- Chi Psi's July 2024 official Purdue Alpha Epsilon Tau newsletter identifies the pictured two-story brick lodge as its new lodge at 950 David Ross Road. This is usable visual evidence for the photographed facade and broad roof silhouette.
- Zeta Psi's 2023 official chapter report says Tau Gamma moved its house during 2022. A Purdue-linked chapter profile self-lists the same 950 address. The 2025 IRS return supports an active Purdue student-housing program but gives no address. Chi Psi's 2024â€“25 and 2025â€“26 official dues schedules classify its Purdue chapter as rental housing, without naming a property.

These sources establish a physical candidate and provide one facade view. They do not establish whether Zeta Psi occupies this structure, whether it shares space with Chi Psi, or which chapter's housing program the address represents. See `crosswalk_resolution.md` and `occupancy_recheck_2026-10-26_addendum2.md` for the detailed source chain.

## Why a completed detailed asset is not ready

1. **Crosswalk conflict:** Two chapters have first-party claims connected to the one mapped building. Occupancy and the meaning/date of each address claim remain unresolved. The stable asset ID is explicitly assigned to Zeta Psi, so a physical-site model alone cannot establish that this assignment is complete.
2. **Conflicting footprint geometry:** The existing candidate has only 0.422 IoU with Purdue's FID 748 ring, while it has 0.829 IoU with the independent 2018 LiDAR outline. The LiDAR outline is a roof/building footprint proxy and is dated. The discrepancy needs source matching and review before choosing structural wall lines; fitting one polygon to the other would be an unsupported correction.
3. **Vertical evidence gap:** The retained LiDAR footprint service has no elevation/Z values. No measured eave, ridge, or overall height is available. The newsletter photo suggests two stories but perspective does not support a measured floor count or height.
4. **Incomplete facade coverage:** The official newsletter supplies one front view, useful for the paired gables, brick character and centered entry. It does not document the other elevations, rear additions, window spacing across every wall, or roof intersections. Those would otherwise have to be invented.
5. **Current artifact is only massing:** The saved 16 m-high rectangular shell is unverified and does not encode the photographed facade. Its existing height is a generator fallback, not evidence.

Under the project rubric, identity/footprint, dimensions and orientation, evidence-backed height/roof, facade, and export/evidence all must be considered independently. A more detailed-looking render cannot fill the missing source evidence. I therefore do not recommend submitting the current candidate or a speculative rebuild for an independent grade as a completed Zeta Psi building.

## Safe next build plan

1. Keep the candidate classified as the **physical building at 950 David Ross Road; occupant unresolved**. Retain the existing stable asset path and do not create a second structure at the same site.
2. Obtain dated, geolocatable exterior imagery for multiple sides or an authoritative architectural plan/elevation. Prefer Purdue FSCL, either chapter, or an identifiable contemporary street-level source. Do not contact people without coordinator/user authorization.
3. Obtain vertical measurements or a suitable elevation/point-cloud source, and resolve whether the 2018 footprint represents roof outline, structural wall line, or an older configuration. Compare the sources in a consistent projected CRS and document the transform.
4. Seek a dated source that resolves whether Zeta Psi occupied, shared, or moved from 950 in the relevant academic years. If it confirms a different Zeta Psi site, crosswalk that facility to its own GIS feature before building it.
5. Once those sources are available, model the physical structure once, using neutral site-based naming while the occupant remains uncertain. Save the geometry changes and provenance under `audit/zeta_psi/`, reopen and inspect the exported library, then request the independent grader required by `AGENT.md`. The assignment remains open until the identity crosswalk and grade threshold are supportable.

## Source records

Raw snapshots and exact source metadata are retained under `audit/zeta_psi/sources/`. The quantitative footprint comparison and project-local coordinate approximation are recorded in `footprint_comparison.json`. This assessment makes no edits to the asset, manifest, shared trackers, or campus master.\n