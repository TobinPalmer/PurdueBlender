import bpy
from pathlib import Path

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET = ROOT / 'modular/buildings/knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))

note = (
    'Google Street View panorama at 417 Northwestern Ave (Aug 2025), camera '
    '40.4281078,-86.9106299, heading 244.316 degrees, converted into the project '
    'approximate XY frame. The sightline intersects GIS exterior edge 18 at about '
    '28.7 m. The image shows brick-heavy massing and interrupted narrow glazing, '
    'but vegetation and perspective prevent a defensible count or spacing of window '
    'groups. No geometry change was made; see audit/complete_knoy/evidence_round19.json '
    'and facade_glazing_assignment_r19.svg.'
)
glass = bpy.data.objects['KNOY_Fenestration_Ribbon_Glass']
glass['r19_source_sightline'] = note
glass['r19_geometry_decision'] = 'No R19 glazing edit: exact face sightline is narrowed to GIS edge 18, but interruption widths/intervals remain unresolved.'
walls = bpy.data.objects['KNOY_Exterior_Masonry_Walls']
walls['r19_source_sightline'] = note
scene = bpy.context.scene
scene['knoy_r19_review_status'] = 'Targeted facade/archive research; no geometry changes.'

notes = bpy.data.texts.get('EVIDENCE_AND_INTERIOR_NOTES.txt')
if notes is None:
    notes = bpy.data.texts.new('EVIDENCE_AND_INTERIOR_NOTES.txt')
notes.write(
    '\n\nROUND 19 — STREET VIEW / ARCHIVE SIGHTLINE CHECK\n'
    '------------------------------------------------------------\n'
    'A Google Street View panorama from 417 Northwestern Ave (Aug 2025; pano '
    '37BzxutMJc4KJ68n5M55xw) was checked at heading 244.316 degrees. Using the '
    'manifest origin and the GIS boundary in build_knoy_hall.py, the approximate '
    'camera ray reaches boundary segment 18 after 28.7 m. This gives a candidate '
    'face assignment for that Street View direction, summarized in '
    'audit/complete_knoy/facade_glazing_assignment_r19.svg. The pano, historic '
    'Purdue Archives photo, and 2017/2009 alternate Google Street View dates all '
    'show or are consistent with thin glazing ribbons within substantial brick '
    'areas. However, trees, perspective, and the camera position relative to the '
    'stepped footprint obscure exact bay count and where each interruption falls. '
    'No R19 facade geometry was added; selecting a precise brick pier/window interval '
    'would still be a guess.\n\n'
    'Source search found additional non-digitized primary material: Purdue Archives '
    'UA 141 lists 1984 construction records and a floor plan; UA 62 lists 1984 '
    'Technology Building / Knoy contact-sheet negatives; UA 149 lists Knoy slides '
    'dated 1984–2000. The 2018 Gateway source labels an Existing Knoy Elevations '
    'panel but provides floor-to-floor height marks only, not facade silhouettes or '
    'window segment locations. No downloadable as-built elevation, roof plan, or '
    'verified all-level stair plan was found in this pass. Current roof/L5 and '
    'interior route uncertainties remain unchanged. See evidence_round19.json.\n'
)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('R19_EVIDENCE_SAVED', ASSET)
