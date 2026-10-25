# Morgan J. Burke Boilermaker Aquatic Center — R9 review candidate

R8 received an independent **7.9/10**. This revision focuses on the remaining interior image issues: a cutaway review showing the existing roof trusses over the pool and seating, connected bleacher tiers, and a continuous accessible aisle route. No roof dimensions or heights were added or changed.

## R9 changes

- Added continuous riser plates beneath the two existing 12-row aluminum bleacher banks. The 24 risers visually connect the representative seat rows into stepped stands; the layout and dimensions remain schematic.
- Added a post at each center-aisle stair tread on both rail lines, and increased the existing rail profile slightly. In the detail view, each post meets the stair tread and the sloped handrail. Rail geometry and accessibility compliance remain unverified.
- Saved a dedicated cutaway review camera. The render setup temporarily hides roof surface objects so the existing 21 truss meshes, long fixtures, pool, wall panels and bleachers can be viewed together. The roof is restored in the saved asset and remains visible after reopening.
- The coordinator independently inspected the master placement marker read-only: translation `(-808.6829834, 80.3369980, 0)`, unit scale, zero rotation. The manifest origin is `(-808.683, 80.337)`, a difference of about **0.000017 m**. This task did not open or save the master.

## Limits

The roof profile, eave/ridge elevations, truss members and overall height remain unverified. The trusses are the preexisting schematic geometry; this cutaway does not establish their as-built dimensions. Seating layout, aisle dimensions, handrail geometry and accessibility compliance also remain uncertain. The GIS comparison establishes local outline correspondence only, not survey accuracy.

## Validation and renders

Blender 5.2.3 reopened the saved asset successfully. The asset contains 1,129 objects, 21 existing trusses, 24 continuous bleacher risers, 24 center-aisle rail posts, and two existing sloped handrails. The full roof remains visible in the reopened source. The local GIS outline check reports a maximum sampled error of 0.000002 m in each direction; materials are assigned, and there are no external image dependencies.

- `aquatic_r9_interior_truss_cutaway.png`
- `aquatic_r9_bleacher_aisle_detail.png`

SHA-256: `136c7c7ee7d9d69f8bd1ac84e6e9269c00297a9c464bdd42ef13009bba66f497`.

The fresh independent R9 grade is pending.
