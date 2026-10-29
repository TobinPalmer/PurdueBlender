# Neil Armstrong Hall — change log

## r1 (2026-10-28) — asset SHA-256 `4e03dcb057a6b6d018e8d81c3be03b7d2fd637140dc9571df1294453b3fa1eff`

Built by `modular/buildings/build_neil_armstrong_hall_second_pass.py`. Per the second-pass rule, it does not patch the first-pass geometry: it deletes the first-pass exterior shell (`DELETE_PREFIX`) and rebuilds the exterior independently. Interior objects are kept and offset by (−4.0, +18.0, 0) m to sit inside the corrected main bar. The statue is moved in front of the entrance corner.

### Geometry (dimensions are estimates unless stated)

- **Plan and heights.** These come from the lean-free 2017–2019 QL2 LiDAR height model (`sources/na_ndhm_2018.*`), cross-checked with the 2018 and 2023 aerials. The two aerials lean in opposite directions (≈±4 m at roof height).
- **Main bar** (walls y = −13…17).
  - Flat top at 21.6 m with glazed clerestory steps.
  - North facade:
    - a 34 m full-height curtain wall east of the entrance corner, with pale fins at its east end
    - punched paired windows on four floors east of that
  - South facade:
    - curtain wall with horizontal sun-shade blades (x −44…−22) and ground-floor doors
    - blank brick return
    - single punched windows
    - full-height glass rear main entrance mid-facade (x 2…16) with pale pilasters
- **Red Mayflower ACM roof.** One continuous piece with a flat underside (17.8 m). Its top falls from ~20 m inside to ~18.4 m at the edge, per the LiDAR slope. Its NW point is narrow-armed with a symmetric triangular hole, a support beam down its middle and the red sloped panel visible through it. A small east point oversails the east end.
- **Main entrance.** A square inward corner under the NW point: the glazed main-bar west end plus a glazed doors bay in the west wing's north face.
- **East entrance.** A smaller inward rectangular notch at the main bar's SE corner, with glass sides and doors, under the east point. The diagonal east face is mostly blank brick with limestone bands, a glazed slot and a few windows.
- **West wing.** A plain brick rectangle with:
  - two-storey limestone-framed window units
  - a SW entrance with steps
  - name letters on the north face
  - a separate curved glass top floor with a white roof

  It tops out at about 15.5 m (LiDAR).
- **SE wing.** Brick with evenly spaced single windows, a glass top floor and a white overhang (ECN webcam).

### How the shape was settled

Several pre-review iterations followed the user's visual reviews and the photos they supplied:

- **NW point.** It is flat, not rising; it is one continuous piece with the rest of the roof and has a flat underside. Its arms are narrower, with a triangle hole and a centre beam.
- **Entrance.** It is a square inward corner, with more glass to its left.
- **West wing.** It is a rectangle, made longer, with a separate curved top.
- **East end.** It follows the building outline with only a small overhang. The east entrance is a smaller version of the front entrance.
- **Rear main entrance.** It sits mid-facade.

### Colours

Colours come from `sources/color_samples.json` (valid samples only). Limestone and the white overhang are visual estimates.

### Unresolved

- SE wing window counts are not verified photo-by-photo.
- The north facade brick portion is seen only obliquely.
- The east roof point outline is not confirmed by a ground photo of its full plan.

## r2 (2026-10-28) — asset SHA-256 `0baafbd18a2f6079fb7b3064079d479fcf01ab5b61caf39ddba79c985322736d`

This revision responds to the user's visual review of the plan retrace in commit `754dc309`. It also uses the published floor plan and entrance photo, Sensors 2020 fig. 4 (`sources/researchgate_sensors2020_fig4_*`), and re-reads the LiDAR height model. Renders are in `r2/`. Close-up cameras are in `r2/closeup_cameras.json`. The asset reopens cleanly (`r2/validation_r2.json`).

### Red roof

- **Uniform band.** The roof is now one band, 8 m wide on every side. It projects 2 m past the north, south and east walls.
- **Top surface.** The top slopes straight from the eave (18.4 m) up to the flat main-bar top (21.6 m). The clerestory glazing on the roof is removed, because the aerial photo shows no windows there.
- **NW point.** The west arm now reaches 11 m beyond the glazed west end, previously about 7 m. It runs out over the west wing, as photo (a) and DD_22/24 show.
- **Tilt.** The point is hinged at the east end of the north glass section and rises 4 m toward its tip.
- **Hole and beam.** The triangular hole and the red panel stay at the arms' inner corner. The centre beam is now part of the band: it has the same soffit and top surface as the arms, so it no longer hangs below the underside.

### East end

- **No notch.** The rectangular notch is removed.
- **SE wing.** The SE wing is a right-angled wedge: west corner (40.5, −12.5), tip (54, −34.5). Its east side runs straight into the bar's diagonal east face, meeting it at a flush point near (83, −11). This follows the floor plan and the LiDAR wing-roof edges.
- **East entrance.** The east entrance is now a glazed bay with doors and a canopy at the point, on the diagonal face.
- **Wall above the SE wing.** The bar wall above the SE wing roof is now closed.

### Rear (courtyard) facade

- **Mid-facade glass removed.** The full-height glass entrance at x 2–16 is removed. That stretch is brick.
- **Loading dock.** A small loading dock now sits further east, at x 16–21. It has an overhead door at truck-bed height, bumpers, a man door with steps and a canopy. There are no ground-floor windows around it.
- **Rear entrance.** The rear entrance is now at the base of the sun-shade curtain wall next to the west wing, user photo 2. It has four pairs of glass doors (8 m) in dark aluminium frames with push bars, set in a shallow vestibule at the east end under the Sea Wolf canopy, with an entry pad.

### West wing

- **Glass top floor.** The glass top floor sits on the brick block, set back 1 m. Its white cap projects back out flush with the brick, so it no longer overhangs.
- **Curve.** The SW side is a convex arc inscribed in the block. It touches the face line only at mid-span. The top floor covers only the part of the wing outside the main bar.
- **Side entrance.** The side entrance is back on the SW face, 13 m from the W corner, as in r1 and photo DD_24. It has double doors, a flat canopy, a tall limestone pier rising to the cap, a window unit above, steps and rails. The SE face no longer has an entrance.
- **Other.** Bar walls now close the gap above the wing roof along the bar's west edges. A pale fascia band runs between the bar wall tops and the red soffit.

### Still uncertain

- **Upper floors over the dock.** The user said there are no windows at the dock. Ground-floor windows there are removed, but the upper floors keep the facade's punched windows. Photo 1 shows punched windows continuing along this facade.
- **NW point.** The amount of tilt (4 m) and the west-arm reach (11 m) are photo estimates. The LiDAR cannot separate the arm's eave from the wing roof below it.
- **East entrance.** Its exact width and position at the point are unverified. The plan shows a vestibule and stair there.

## r3 (2026-10-28) — asset SHA-256 `cc66df5e13253ff8e1447506a2a7b85a89bd37348d129e24dd527b62165f4370`

This revision fixes the top five findings of the quick independent review r02 (6.95/10, `review_r02/`). Renders are in `r3/`, and `r3/closeup_cameras.json` adds a match for 2016_01 and a view of the west wing's courtyard face. The asset reopens cleanly (`r3/validation_r3.json`).

1. **West wing, courtyard (SE) face.** The face is now mostly blank brick, with one row of small windows (1.2 × 1.6 m) under thin sunshade fins (rear photos 1 and 2).
2. **NW point from below.**
   - **Hole.** The triangular hole now sits between the two arms. Its base is the top edge of the glazed bar west end, and its apex points toward the tip. It lies outside the building, so sky shows through it from the plaza (2016_01, fig. 4a).
   - **Through the hole.** You see the red edge panel beyond.
   - **Beam.** The beam runs from the apex to the middle of the base and stays flush with the band.
   - **Soffit.** The soffit is red everywhere it shows.
   - **Panel joints.** The red cladding has panel joints (about 3.0 × 1.5 m panels).
3. **Colour.**
   - **Brick.** Darker red-brown with purple-toned headers. The sources are DD_24 brick in overcast light, about sRGB (96, 71, 59), and the sunlit rear photo, about (212, 159, 139).
   - **Glass.** Lighter and reflective blue-green-grey. The sources are DD_24 at about (98, 106, 109) and the rear curtain wall at about (41, 84, 86).
4. **Main bar windows.**
   - **Brick facades.** Punched windows are spaced at 2.2 m, previously 3.0 m. They now have limestone sills and heads.
   - **North facade, ground floor.** The windows are taller (0.8–3.7 m), with limestone surrounds.
5. **West wing, SW face.**
   - **Left of the limestone pier.** This part is now blank brick with the name letters and two near-square upper windows under fins (DD_24).
   - **Side entrance.** It now reads as two pairs of framed glass doors.
   - **Corner window.** The window by the W corner on the NW face is now a two-storey window with a limestone surround.

### Still uncertain

- The 2.2 m window spacing is a photo estimate from an oblique view.
- Colours were sampled from photos that are not colour-calibrated.
- No photo covers the east end.

## r4 (2026-10-28) — asset SHA-256 `60b8e82c2719a00559691969428255e7f111b43a78688d0df070fa3a06d10c60`

The user found the red roof blocky and wanted it to read as one continuous piece. It is rebuilt as a single thin plate (`build_high_roof`). Renders are in `r4/` and the asset reopens cleanly (`r4/validation_r4.json`).

- **Plate.** The band is one 0.5 m sheet whose underside runs parallel to its top. It was a flat-bottomed wedge with 3.8 m-tall inner faces, glued-on skirts and boxes. One constrained triangulation now covers the whole roof plan. Its constraints are the outer edge, the edge of the flat top, the hole and the four hip lines, with a 1.5 m interior grid so the NW tilt bends smoothly.
- **Hipped band.** The band is 10 m wide on every side. It rises evenly at about 23° from a thin eave 2 m past the walls (top at 17.4 m) to the flat top at 21.6 m. Its underside meets the wall tops exactly. The flat top now spans y −4.5…9, which matches the LiDAR flat top (y −4…10).
- **NW point.** The west arm's inner edge is now the glazed bar west end itself, and the arm reaches 10 m beyond it. The point is a thin blade that tilts up 4 m toward its tip.
- **Hole and beam.** The triangular hole has its base along the top of the entrance glass, so sky shows through it. The beam is flush with the plate.
- **Glazing under the point.** Where the underside rises above the wall tops (the NW point), the entrance and north glass now run up to meet it (2016_01, photo 5). The separate grey skirts and edge walls are gone.

## r5 (2026-10-29) — asset SHA-256 `f32edfe2209530c947a9d368e40a1c60f0f41eb643c6c8d15c9f2409f8ae113d`

Only the red roof, its hole and strut, and what closes the gap under it changed (`red_geometry`, `build_high_roof`, `build_roof_infill`, and the `RED_W`, `STRUT_U`, `STRUT_HW` and `RED_DIP` constants). Walls, wings, facades, materials and the flat top's height are untouched. Renders and plates are in `r5/` (`before/` is r4 and `after/` is r5, from the same cameras in `r5/cams_r5.json`; plates are in `r5/plates/`, made with `r5/make_plates.py`). The reopen check passes (`r5/validation_r5.json`).

- **Uniform width (user review).** The band is a parallelogram frame of one width on every side. The NW point is the frame's outer corner, and its two arms are the north and west sides at that same width (`RED_W` = 7.0 m, was 10 m). The width is measured, not chosen to fit:
  - **2023 ortho.** The red north strip and the west arm are both 6–7 m wide.
  - **LiDAR.** The flat-top edge sits about 8 m in from the north and south eaves (y≈11 and y≈−6.5 at x = −20…0). The previous "y −4…10" figure did not hold up when re-profiled.
  - **Why it matters for the hole.** A 10 m band puts the north arm's inner edge south of the entrance corner, so no hole could reach the entrance glass.
- **Hole.** The hole is the frame's inner corner cut off by the top of the entrance glass. Its apex is where the arms' inner edges meet. Its base runs from the last 2.4 m of the glazed bar west end through the entrance corner to the end of the doors bay (2016_01, DD_22, fig. 4a, 2023 ortho).
  - **West arm.** To get the base across the whole doors bay, the west arm's inner edge now passes the end of the bay. The arm therefore sits about 6 m further out over the west wing.
- **Arms down to the glass.** Around the hole the arms fold down onto the glass top, so the hole's sides run straight down to it, as in 2016_01, DD_22 and fig. 4a. Behind the base a short red slope (3 m) climbs back up to the flat top. That slope is the sunlit red seen through the lower part of the hole, with sky above it (2016_01, photos 2, 3 and 4). The fold is built as a few flat facets of the same 0.5 m plate, so the roof stays one smooth sheet.
- **Strut.** The strut runs from the hole's apex to the top of the doors-bay glass, 58% of the way from the entrance corner. That is where its foot lands in 2016_01, fig. 4a and the ortho. It was previously attached to the wrong glass face, high up in the plate. It is a 0.8 m-wide strip as thick as the plate, its top flush with the plate at the apex. Because the plate itself comes down to the glass there, the strut follows the hole's sides and never hangs below the plate.
- **No invented glazing (user review).** The r4 glass strip and mullions between the wall tops and the soffit (`ARMS_SP_RoofInfill_glass`/`_frame`) are removed. Under the point the soffit stands clear of the north glass and the bar west end, as photos 2 and 4 show.
  - **What closes gaps instead.** A 0.75 m red strip closes the gap between the doors-bay glass top (17.0 m) and the plate's underside (17.75 m) along the hole's base. Along the bar's west walls above the west wing (seen in no photo), the red soffit is carried down to the wall tops.
  - **Soffit over the west wing.** The flat top between the bar's west wall and the moved west arm gets a red underside, so from the west it reads as the dark soffit seen in photo 5.

### Still uncertain

- The model's doors bay is 6 m wide. The ortho suggests the real hole base is about 11 m. With the entrance walls fixed, the hole is therefore smaller relative to the arms than in the photos.
- The strut's exact cross-section is a photo estimate.
- Moving the west arm out to the end of the doors bay leaves a 6–8 m strip of flat top over the west wing's north-east part, outside the bar footprint. The real bar is probably wider there (ortho: the flat top runs right up to the west arm), but the footprint was not to be changed.

## r6 (2026-10-29) — asset SHA-256 `ef4bb7f14e0ed4bf68258bfbe161d9c3d265cb8814507b2bfa7a87255b10b6da`

This revision makes the user's r5 review changes, marked on a top-down screenshot, and nothing else. Renders are in `r6/`; `r6_top_NW_user.png` matches the user's screenshot. The asset reopens cleanly (`r6/validation_r6.json`).

- **Entrance.** The glazed doors bay is now 8 m wide, up from 6 m. The red west arm's inner edge still runs through the bay's far end.
- **West wing.**
  - The W corner moves 10.9 m further out along the NW face line, so the west wall's chord runs at 45° in plan.
  - The wall bows out in one convex curve, 8 m past the chord. Brick block and glass top floor follow it alike.
  - The NW face grows from 26.4 m to 37.3 m, and the plan area grows by about 50%.
  - The side entrance, the name and the two small windows keep their positions from the W corner along the curve.
- **Red wing.**
  - The underside is flat, sitting on the wall-top deck at 17.75 m; it lifts only where the NW point tilts up.
  - The top rises evenly from the eave (18.35 m) to the flat top and is flush with it.
  - The r5 "dip" facets around the hole are removed. These were the trapezoid the user circled.
  - The strut has the band's flat underside and top.

### Uncertain

- The LiDAR and the satellite trace place the west wing's west wall at about 60–64°. The 45° curve follows the user's direction.

## r7 (2026-10-29) — asset SHA-256 `c15a738ceaf1c4d9ce56e8da0c9d26931575242ddb0c5bdf0b2a12bba1ee328d`

This revision makes the user's minor r6 changes and nothing else. Renders are in `r7/` and the asset reopens cleanly (`r7/validation_r7.json`).

- **Red wing thickness.** The wing is 30% thinner. The flat underside stays on the wall tops; the eave is now 0.42 m thick (was 0.6 m), and the flat top, still flush with the band, is at 20.45 m (was 21.6 m). The flat top is now about 1.2 m below the LiDAR flat-top height.
- **Red wing width.** The band is 6.5 m wide, down from 7 m.
- **Front doors.** The glazed doors bay is 9.6 m, up from 8 m: six 1.6 m panes, one more than before.
- **West wing.** Only the glass top floor is curved. The brick block below is a plain rectangle. Its straight 45° west wall touches the top floor's curve at the peak, so the curve sits on the block with no overhang. The side entrance, the name and the small windows are on that straight wall.

## r8 (2026-10-29) — asset SHA-256 `e899a2878020ad556822b073aa34902907cd50c9bc0220ac58f439887e950915`

This revision makes the user's r7 change and nothing else: the west side was slightly too wide and its curve too strong. Renders are in `r8/` and the asset reopens cleanly (`r8/validation_r8.json`).

- **Curve.** The glass top floor's west curve now bows out 4 m past its chord, down from 8 m.
- **Width.** The brick block's straight 45° west wall still touches the curve's peak, so it moves 4 m in and the west side is that much narrower.
