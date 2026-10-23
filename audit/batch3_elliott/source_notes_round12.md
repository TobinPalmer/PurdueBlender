# Elliott Hall of Music — round 12 source notes

Checked 2026-10-23. Scope: Elliott modular source and `audit/batch3_elliott` only. The master, manifest, BUILDINGS.md, and Hovde source were not edited.

## Geometry pass

1. Widened the central longitudinal seating aisle by moving the two center seat banks and carpet sections outward 0.40 m per side; extended the central stair treads to match. This is a visible modeled route through the existing seating banks. The result is an estimated roughly 1.45 m lane, not a measured width from the inaccessible plan and not an accessibility/egress compliance claim. Other aisle dimensions and exit routes remain schematic.
2. Added a simple floor-level stage pit-lift platform and perimeter seam at the front of the stage. Sheet R101's indexed callout states the pit lift must remain accessible for scheduled staff use. Exact size, elevation, location, and operating state are not legible from the indexed page; all modeled dimensions and its precise position remain schematic.
3. No window schedule, facade opening cadence, side-exit geometry, backstage rooms, or exterior massing was guessed. The exterior photo links are described by the official page, but the actual facade pixels were not available for verification during this pass.

Fresh images: `interior_main_floor_plan_round12.png` isolates the modeled main-floor seating, center aisle, stage and pit-lift concept; `interior_central_aisle_round12.png` shows the updated interior in section-like perspective. These are model renders, not plan/photo overlays.

## R101 plan evidence and limits

- Official source target: [Indiana IDOA project drawing binder](https://www.in.gov/idoa/mwbe/files/C4011859-Elliott-Hall-of-MusicBinder1.pdf). Direct open on 2026-10-23 returned IN.gov 404. Search index still exposes sheet R101 metadata: “Elliot Hall of Music Main Floor,” scale 3/32"=1'-0", dated Dec. 15, 2025; it lists the stage floor, a pit lift, seat/row markers, loading dock, and temporary construction barricades/egress door. The indexed text does not expose legible permanent aisle or lift dimensions. The sheet is tied to the ceiling-tile replacement project; temporary barricades, door impairment, and contractor egress markings are construction logistics, not permanent architectural features. No coordinates or sizes were measured from the indexed result.
- Official [Addendum No. 1](https://www.in.gov/idoa/mwbe/files/C.40.11859-ELLIOTT-HALL-OF-MUSIC-ACOUSTIC-CEILING-TILE-REPLACEMENT-2026-_-Addendum-1-_-dtd-01-14-26.pdf) is accessible and confirms this is a ceiling-tile replacement / scaffolding project. It discusses stage-end material hoists and five scaffold runs but does not provide a permanent circulation or facade design. Do not model the temporary scaffold/barriers as permanent building features.
- Search indexing also identifies R102 Balcony Floor Plan and R103 Gallery Floor Plan at 3/32"=1'-0" with aisle ways, seating, stairs and egress labels. Direct Binder1 page images are unavailable, so those are source labels only, not a pixel-verified geometry match.

## Official photos and Google Maps check

- [Purdue Convocations' Elliott anniversary page](https://convocations.purdue.edu/elliott-hall-of-music-75th-anniversary-1940-2015/) contains images labeled as exterior/construction imagery and describes sturdy brick walls. Image pixels were not available here for checking window cadence, openings, or flytower/apse proportions.
- [SAH Archipedia's Elliott entry](https://sah-archipedia.org/buildings/IN-01-157-0079) supports the broad feature families (brick/limestone, tile roof, flytower/apse, entry canopy, secondary entrances, stepped side exits) but does not provide dimensions. The page could not be opened directly in this environment; previously indexed text is used only for those general claims.
- Google Maps satellite/Street View comparison requested by the parent was attempted on 2026-10-23. The web tool cannot open the Google Maps place URL, and the workstation browser inventory exposed no browser session. Purdue's venue page embeds an address map for 712 3rd St but supplies no readable satellite/Street View image. No Maps imagery date or facade observation can be verified, so no Maps-based geometry edits were made.
- Purdue's [current seating chart](https://convocations.purdue.edu/wp-content/uploads/2022/09/Elliott-Seat-Map.pdf) supports the curved seat blocks and three levels, but not dimensioned aisles. Purdue Convocations' [directions page](https://convocations.purdue.edu/directions/) describes a wide central aisle in its current auditorium photo; this supports the feature type only, not a numeric width.

## Reopen and placement

Blender 5.2.3 LTS reopened the saved asset. The Elliott collection has 137 mesh objects, including the two new R12 pit-lift schematic objects; no `TEMP_R12_` objects remain. The GIS shell object bounds are unchanged at x -46.42..44.08, y -38.13..46.93, z 0..22.5. Prior FID 617 footprint comparison remains unchanged and is horizontal-footprint evidence only.

## Remaining gaps

Facade window/opening schedule, elevations, flytower/apse proportions, exterior secondary exits, stage/backstage layout, true measured circulation, accessible routes, and Hovde portal/connector remain unresolved. The direct plan and Google Maps imagery limitations prevent a dimensioned round12 match. Keep the aisle and pit lift labeled schematic; do not claim a 9/10 score pending independent review.
