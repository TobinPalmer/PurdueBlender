import json
from pathlib import Path
p=Path('audit/neil_armstrong_hall_refine/evidence_r12_1.json')
d=json.loads(p.read_text(encoding='utf-8-sig'))
d['validation_pending']='Fresh Blender 5.2.3 reopen validation passed at SHA fd6a8c7dcbdd21eab4d94ae3a9b38d72d87069260e059996ab689d432927c62e; 445 objects, 415 meshes, no unassigned/null mesh materials, no external file images, root transform identity. Geometry heights remain inferred, orthophoto edges are roof/eaves only, and no dimensioned public plan was located.'
d['validation']='validation_r12_4.json'
d['comparison_plate']='comparison_plate_r12_1.png'
p.write_text(json.dumps(d,indent=2),encoding='utf-8')
notes='''# R12 source-to-render notes

## Evidence used

- The 2023 Indiana orthophoto shows a red ACM roof/eaves band around a large, pale roof/courtyard region. `roof_trace_overlay_r12.png` records the five-point outer and inner pixel traces. This locates roof edges, not walls.
- Wikimedia Commons 2016 photos by Julian Herzog (CC BY 4.0) show a folded, wing-like red metal roof over the glazed entrance. They are geotagged, but heading and roll are unavailable, so renders from those points are comparative only, not camera calibration.
- Photo 02 shows the glazed inner facade from a courtyard position and indicates a substantial open-sky region.
- The 2018 5-ft NDHM high band median is 21.55 m. It provides only a coarse ceiling, not a measured roof elevation.
- Purdue Archives lists September 2004 development plans, but the item is not digitized and requires archival consultation. No public dimensioned plan or elevation was located in this review.

## R12 geometry

The existing `ARMS_Cantilever_Canopy_Deck` mesh was replaced in place, preserving 445 objects. Its orthophoto-traced roof/eaves loop spans approximately X [-70.3, 77.8] m, Y [-7.8, 27.5] m in the asset-local frame. The inferred shell uses heights from 16.45 to 21.50 m, a 1.25 m warp, and 0.30 m thickness. The shape is photo-based inference and not a surveyed roof profile.

R12.1 added a shallow triangular dark patch at the northwest roof pocket visible in the 2023 aerial; whether this reads as a structural aperture is unverified. R12.4 darkened only the new wing ACM material to linear base color (0.085, 0.025, 0.014), metallic 0.08, roughness 0.50. Shared materials are unchanged. This is a visual match decision, not a calibrated measured reflectance.

## Current validation and renders

Current asset SHA-256: `fd6a8c7dcbdd21eab4d94ae3a9b38d72d87069260e059996ab689d432927c62e`. Fresh-process Blender 5.2.3 validation is in `validation_r12_4.json`. It reopens with 445 collection/scene objects and 415 meshes, identity root transform, no mesh missing/null materials, and no external image dependencies. Canopy object has 371 vertices and 357 polygons.

Updated geotag-start, courtyard, four cardinal side views, and orthographic roof view are in `renders_r12_1/`. `comparison_plate_r12_1.png` aligns photo 03, photo 02, and orthophoto with corresponding current renders.

## Remaining uncertainty

The renders still show visible roof-profile and facade differences from the photographs. The orthophoto loop is a roof/eaves trace and cannot validate wall centerlines. The geotagged camera positions have unknown heading and roll. Height, folded surface curvature, and structural interpretation remain inferred. Do not present this as exact geometry; an independent reviewer should evaluate whether the visual fit is actually improved and whether it reaches 8/10.
'''
Path('audit/neil_armstrong_hall_refine/comparison_notes_r12.md').write_text(notes,encoding='utf-8')
