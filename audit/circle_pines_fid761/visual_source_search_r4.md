# Circle Pines visual evidence reconciliation — R4, 2026-10-28

## Current source located

The Purdue GIS FID 761 feature identifies Circle Pines at 1000 David Ross Rd. A Google Maps listing for Circle Pines exposes a Street View panorama captured in April 2026 (pano ID `ytu8Bz_eEp2xCv9QeF0xRw`). The supplied Maps URL places the camera at 40.4350711, -86.9250796, with heading 98.54251° clockwise from north. The 900×600 thumbnail is saved as `sources/google_streetview_panoid_ytu8Bz_eEp2xCv9QeF0xRw_2026-04.jpg`; the Maps listing URL and direct thumbnail URL are recorded in `streetview_target_reconciliation.json` and `source_record.json`. Retrieval was 2026-10-28. April 2026 is the date displayed in the Maps listing UI; it is not legible in the downloaded image itself.

## Target alignment and limits

The camera point is approximately 62.77 m from the transformed FID 761 ring centroid. The centroid bearing is 106.48°, only 7.93° from the supplied pano heading. The camera is about 42.53 m from the nearest polygon edge; candidate long edge 17 faces toward the camera within approximately 15.1°. These checks use the project approximate campus-local transform and the source GIS ring; they support the view looking toward FID 761 but are not survey control or an independent response from Google's panorama metadata API. The Maps listing itself is Circle Pines, and the image shows the house across the parking apron. Neighboring buildings at image margins are not included in the model.

## Observable content

The central target shows a red-brown brick facade, two visible horizontal bands of rectangular windows, a taller central vertical glazed entry bay, and a shallow light-colored projecting canopy. A low parapet-like roof edge is partly visible, but trees obscure most of the roof. The image does not establish the unseen elevations, exact dimensions, story count, roof construction, or interior plan.

R4 applies only the visible facade cues to the camera-facing GIS edge. The two window bands motivate an estimated 5.4 m wall height plus a 0.35 m neutral cap (5.75 m total); these are model estimates, not measured values. Purdue GIS `NUM_LEVELS=1` conflicts with the two visible window bands, and the record preserves that conflict rather than resolving it. Roof geometry beyond a conservative cap, other elevations, and upper interior remain unverified. The one-level interior is only a schematic visualization.

## Historical source retained as context only

The 1954–55 Purdue Debris page for Circle Pines remains in the packet as historical context. Its covered porch has no address and continuity with the current FID 761 building is unverified, so it is not used to model the current facade.

## Earlier unsuccessful source checks

Prior checks of Purdue FSCL links, the official house website, Instagram and exact-address searches are preserved in `visual_source_search_r3.md` and earlier audit history. The later Street View discovery supersedes the R3 statement that no current attributable exterior image was available.
