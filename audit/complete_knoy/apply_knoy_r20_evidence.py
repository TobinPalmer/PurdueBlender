import bpy
from pathlib import Path

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET = ROOT / 'modular/buildings/knoy_hall.blend'

bpy.ops.wm.open_mainfile(filepath=str(ASSET))

correction = (
    'R20 correction: the R19 evidence_round19.json primary sightline values were '
    'computed from the Aug 2025 panorama at 40.4281078,-86.9106299 (project XY '
    '260.377,78.594 m), whose 244.31604-degree ray hits GIS edge 18 at '
    '(234.472,66.136) m (28.745 m; u=0.692). The R19 SVG mistakenly plotted '
    'the June 2009 panorama at 40.4280957,-86.9106154 (XY 261.607,77.251 m), '
    'whose separate ray hits at (235.921,64.898) m (28.502 m; u=0.906), while '
    'labeling it as Aug 2025. R19 diagram is superseded by '
    'facade_glazing_assignment_r20.svg. This corrected approximate ray identifies '
    'only a candidate facade edge; it does not establish exact window count, '
    'spacing, segmentation, or dimensions. No mesh geometry or placement changed. '
    'See audit/complete_knoy/evidence_round20.json.'
)

glass = bpy.data.objects['KNOY_Fenestration_Ribbon_Glass']
glass['r20_sightline_correction'] = correction
glass['r20_geometry_decision'] = (
    'No glazing geometry change. Corrected Aug 2025 pano ray candidate edge is GIS '
    'segment 18; visual imagery remains too occluded/unregistered to assign exact '
    'slit interruptions or dimensions.'
)
walls = bpy.data.objects['KNOY_Exterior_Masonry_Walls']
walls['r20_sightline_correction'] = correction
scene = bpy.context.scene
scene['knoy_r20_review_status'] = 'Corrected R19 pano/ray mismatch; evidence-only revision, no geometry or placement changes.'

notes = bpy.data.texts.get('EVIDENCE_AND_INTERIOR_NOTES.txt')
if notes is None:
    notes = bpy.data.texts.new('EVIDENCE_AND_INTERIOR_NOTES.txt')
notes.write(
    '\n\nROUND 20 — SIGHTLINE COORDINATE CORRECTION\n'
    '------------------------------------------------------------\n'
    'The R19 JSON and SVG did not use the same Google Street View panorama '
    'position. The JSON values were based on the Aug 2025 pano at '
    '40.4281078,-86.9106299; the SVG accidentally plotted the June 2009 pano at '
    '40.4280957,-86.9106154 while labeling it as Aug 2025. The cameras differ by '
    'about 1.82 m and the calculated ray hits by about 1.91 m. R20 separates '
    'the observations and regenerates the diagram from the Aug 2025 JSON source: '
    'camera XY (260.377,78.594) m; approximate hit on GIS boundary segment 18 at '
    '(234.472,66.136) m, 28.745 m away, edge parameter u=0.692. The 2009 panorama '
    'has a distinct hit at (235.921,64.898) m, 28.502 m away, u=0.906. The R19 SVG '
    'is superseded; use facade_glazing_assignment_r20.svg and '
    'evidence_round20.json. These local coordinates use the project approximate '
    'tangent-plane conversion, not survey control; the segment is only a candidate '
    'facade assignment. Perspective and tree occlusion still prevent reliable '
    'measurement of glazing interruptions, counts, and spacing. No geometry or '
    'placement changed. Targeted image/archive research located no calibrated, '
    'face-registered elevation that resolves those window details. See the R20 '
    'evidence JSON for source URLs and limitations.\n'
)

bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('R20_EVIDENCE_SAVED', ASSET)
