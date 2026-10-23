# Math Sciences score status

**Independent rating: pending.** No score is claimed until a separate reviewer inspects the saved asset.

The two main wall elevations now have 81 real through-openings with glazing and stone surrounds. A reopened-file ray check passed all 81 window centers and six solid-wall control points. Purdue's current library photo and third-floor plan support the modeled carrels, shelves, carpet, study area, and room 352 testing-room type.

The exact current third-floor furniture and group-room layout is not publicly documented by the sources found. Upper floors contain estimated slabs only; measured elevations, floor heights, upper-floor rooms, and other facade dimensions remain unverified. Do not treat the building as a 9/10 until the independent reviewer confirms that rating against those limits.

## Follow-up status after first independent review

The first independent review scored the earlier pass **6.5/10**. This update has not been independently scored; no 9/10 rating is claimed. The saved model now has six plan-aligned third-floor boundary segments with inferred door gaps, three inferred glass-front group rooms, room 352 moved to the southeast zone on the 2022 plan, and core features placed from that plan. The source plan supports the renovated area and core relationships; the 2025 article supports the room and furniture types. Current exact room boundaries and furniture positions remain unverified.

The builder saved the blend, and both the render and opening-check processes reopened that saved file. Updated exterior renders include four orthographic sides and a brighter overall view. The GIS footprint audit now samples 50 source shell centerlines and the FID 227 boundary at up to 0.25 m: GIS-to-shell median 0.091 m, 87.7% within 0.25 m, P95 0.838 m; this is edge distance, not polygon IoU or survey accuracy. See `REVIEW.md`, `plan_layout_overlay.png`, and `structural_edge_comparison.json`.

West/north façade detail, current library as-built arrangement, and exact upper-story elevations remain unresolved. The 33.2 m wall envelope, 42.9 m maximum, nine intermediate slabs, and typical floor interval remain estimates; GIS level attributes are not treated as measured heights.

## Third builder pass status

The second independent review scored the prior saved asset **7.0/10**. Round-three changes are saved, reopened, and awaiting another independent review; no new rating is claimed. The embedded procedural brick material now has visible .25 m by .078 m courses and .008 m mortar joints in a close detail render. This scale is a visual estimate. The brick treatment applies to the current envelope and rebuilt east/south facades. No unsupported window patterns were added to north/west faces; their facades remain uncertain.

The three shelf runs now sit within the 2022 plan-labeled library footprint. A warmer timber palette, muted carpet, low partition base trim, brighter library fill, and shadow-free top-down diagram make the 2022 room divisions and inferred openings easier to compare. Current post-2025 room boundaries, furniture positions, group-room dimensions/count and routes are still inferred from available documentation.

The fresh renderer and opening-check processes reopened the saved blend. `geometry_checks.json`: 551 direct objects / 593 including children, all 81 sampled window centers clear and all 6 brick controls blocked. See `REVIEW.md`, `brick_detail_after.png`, `library_plan_diagram.png`, and the complete refreshed exterior/interior render set. The 33.2 m wall top, 42.9 m overall maximum, floor spacing, upper slabs and roof remain estimates pending independent review.

## Round four builder handoff (2026-10-23)

Saved changes in `modular/buildings/math_sciences.blend`: roof/penthouse and floor slabs now carry explicit estimated/source-status properties; 33 old illustrative library objects are hidden to prevent overlap with the newer study furniture. The base floor/border/perimeter walls and GIS shell/placement are retained. `audit/batch3_math/library_plan_round4.png` is the clearest current plan-reading render. `geometry_checks_round4.log` confirms saved-file reopen; 81 pane-center rays are clear and 6 solid-wall controls hit brick.

The passage is source-confirmed but its position, dimensions and support layout are not verified by the accessible references. A low camera trial did not locate it and is excluded from evidence claims. Google Maps imagery could not be inspected in this session; the already-recorded place pin remains an unsurveyed entrance marker. A Purdue Archives catalog listing identifies 1968 west-side photos, but the catalog did not provide viewable images. North/west facade pattern and roof/height remain unknown. Latest independent score remains 7.2/10; no new rating is claimed pending independent review.

Round four also includes the lower campus-eye render xterior_round4.png, which makes the supported elevations read more clearly. Camera composition reduces roof-face dominance but does not change the estimated roof geometry. The review remains pending; 7.2/10 is the previous independent score only.

## Round five status — independent review pending

Saved round-five changes remove the unsourced east-facade lettering, clean up window-reveal joints and produce a less occluded library cutaway. The passage remains unmodeled because accessible sources do not locate it on a specific facade or supply dimensions. The saved/reopened geometry check still reports 81 clear window-center samples and 6 solid-wall controls. GIS footprint and placement are preserved.

The latest score is 7.1/10 from round four. Round five has not been scored. North/west facades, roof shape, and all metric vertical dimensions beyond the sourced 10-story identity remain uncertain or estimated.

## Round six correction — awaiting independent review

Round five scored 6.9/10. Its reviewer found the east gold sign remained because the cleanup code was commented out. Round six removes the saved `MATH_Signage_East` object directly. Reopening confirms it is absent, and the east elevation was rerendered from the saved blend (`verify_sign_round6.log`, `render_round6.log`). No new independent score is claimed yet.
