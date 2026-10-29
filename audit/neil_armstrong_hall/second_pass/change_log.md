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
