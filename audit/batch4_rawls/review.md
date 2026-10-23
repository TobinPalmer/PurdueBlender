# Rawls Hall independent review

Reviewed the proposed improvement script, supplied 2024 first-floor plan and archived interior photograph. This is a provisional source review; a finished saved-model render has not yet been independently inspected.

Provisional rating: 5.7/10 (exterior 17/30, textures 12/20, interior 12/30, technical 8/10, evidence 8/10). This is not a 9/10 completion certification.

The first-floor classroom curves and several boundaries are meaningfully supported by the published plan. The registration uses an approximate similarity transform with stated 1–2 m uncertainty; it must not be described as surveyed or exact. The archived interior photo supports warm ochre walls, pale masonry/plaster, dark framing and wood, but is dated 2003 and does not certify current finishes throughout all rooms.

Required fixes identified in initial script:

- Brick texture projects X/Z only, collapsing courses on perpendicular walls. Use two vertical projections blended by surface normal or verified UV mapping.
- Classroom desks and chairs are initially unsupported slabs. Add legs and chair backs with floor contact.
- Complete the 1054 perimeter and core/circulation boundaries visible in the first-floor plan, while retaining documented door gaps.
- Verify that partitions and furniture lie within the saved exterior envelope after the approximate plan registration.
- Upper-floor offices, rooms and circulation are unresolved. Photo-observed atrium stairs, bridges, glazing and railings require checking against the actual model.
- Noise on wood is generic surface roughness, not convincing directional grain; inspect material render at room scale.
- Google Maps was unavailable and has not verified the building. Do not claim that it has.

Evidence limitations prevent a 9/10 rating even after the straightforward geometry defects are fixed. Additional floor plans, exterior imagery and rendered model inspection are necessary for that claim.

## Render followup

Inspected exterior.png, interior_plan.png and classroom.png. Desks now have supports and chairs have backs; some chairs still lack evident floor supports in the supplied render. First-floor partitions visually reproduce the main classroom arrangement and curves, but several boundaries remain open and stair/core/toilet interiors are not completed. Exterior image has black patches at entrance/plaza surfaces requiring an overlap/normals check. Upper floors remain unsupported by evidence. Revised score remains 5.7/10; these images demonstrate useful partial progress, not full interior completion. A later chair-support repair can resolve that specific defect without removing the evidence and coverage limitations.

## Final source and registration followup

The registration_overlay.png shows the red GIS exterior outline broadly following the plan's asymmetric perimeter, including the stepped northern edge, slanted classroom wing and southern projections. This supports approximate placement of the traced partitions. Small offsets remain, particularly at the northern classroom and some perimeter edges; the overlay does not establish survey precision or vertical accuracy.

The owner reports final chair legs and separated apron surfaces, 518 exported objects and no missing images. These address specific construction and dependency defects but do not justify increasing the rating without a fresh final render. The dark entrance/plaza patches visible in the reviewed exterior render remain a visual concern until a final image establishes that they are resolved.

A more significant unresolved issue is the original atrium void: the owner identified overlap with classroom area documented on the first-floor plan. The attempted replacement was not saved, and its broad rectangular shape was rejected. The inherited atrium geometry therefore requires further reconstruction using upper-floor plans or other reliable spatial evidence. The first-floor plan alone cannot certify the upper-floor void, bridges or circulation. Rating remains 5.7/10.

## Final correction (supersedes atrium contradiction and surface concerns above)

Re-inspected the final exterior.png and classroom.png. The black apron triangles have disappeared from the exterior view; the rebuilt apron resolves that visible defect. Chairs now visibly include legs, and desks retain their supports. Final source export count is 518 objects, reported by the owner.

Correction to the earlier atrium wording: the inherited slab openings affect L2–L5 only. The ground-floor slab at elevation 0 is complete and supports the documented first-floor classroom furniture. The first-floor plan therefore does not directly contradict the upper-level opening. The shape and location of that upper-level atrium still need upper-floor spatial evidence before certification. The attempted alternative void was rejected and not saved.

Final independent rating remains 5.7/10 because upper-floor interior completeness, facade details, material closeups and current dimensional verification remain unresolved. The specific furniture-support and visible apron defects are now resolved in the reviewed final images.
