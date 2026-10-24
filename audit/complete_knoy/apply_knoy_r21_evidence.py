import bpy
from pathlib import Path

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET = ROOT / 'modular/buildings/knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))

source_note = (
    'Purdue Polytechnic Condensed Building Emergency Plan, revised 2019-03-14 '
    '(https://polytechnic.purdue.edu/sites/default/files/files/BEP%20March%2015%202019.pdf), '
    'retrieved 2026-10-24. The plan names lower-basement shelter areas for '
    'Administration/Business Office/CMT/ECN and upper-basement areas for CGT/CIT/SOET; '
    'it lists rooms KNOY G-011 and KNOY 457. It contains no measured floor plan or '
    'registered stair layout. The source confirms operational upper/lower basement '
    'distinctions as of 2019, but does not map either level to this local model frame. '
    'The source library has one slab named KNOY_FloorSlab_Basement at z approximately '
    '-6.7 m; the distinction/geometry of any upper basement is therefore unresolved. '
    'Do not infer room outlines, slab positions, or stair connections from the emergency '
    'plan. No geometry or placement changed in R21.'
)
basement = bpy.data.objects['KNOY_FloorSlab_Basement']
basement['r21_source_check'] = source_note
basement['r21_geometry_status'] = 'One schematic basement slab is present; official 2019 emergency plan distinguishes upper and lower basements, but does not provide plan geometry. Basement-level count/registration and vertical circulation remain unverified.'
scene = bpy.context.scene
scene['knoy_r21_review_status'] = 'Added official 2019 emergency-plan cross-check for named basement levels; evidence-only, no geometry/material/transform/placement changes.'

notes = bpy.data.texts.get('EVIDENCE_AND_INTERIOR_NOTES.txt')
if notes is None:
    notes = bpy.data.texts.new('EVIDENCE_AND_INTERIOR_NOTES.txt')
notes.write(
    '\n\nROUND 21 — OFFICIAL EMERGENCY PLAN LEVEL CROSS-CHECK\n'
    '------------------------------------------------------------\n'
    'Purdue Polytechnic’s Condensed Building Emergency Plan for Knoy Hall, revised '
    'March 14, 2019, identifies separate lower-basement and upper-basement shelter '
    'areas for different departments and gives room references KNOY G-011 and KNOY '
    '457. This confirms the building was described operationally with more than one '
    'basement area and a fourth-floor room reference in 2019. The public document is '
    'an emergency procedure, not a floor plan: it does not provide floor outlines, '
    'room coordinates, stair geometry, vertical connections, or dimensions. The source '
    'asset contains one schematic slab named KNOY_FloorSlab_Basement at approximately '
    'z=-6.7 m in the building-local frame; the source does not establish whether that '
    'slab represents the upper or lower basement or how the missing distinction should '
    'be modeled. Keep the basement-level split and route explicitly unverified until '
    'a suitable authorized plan is available. No geometry or placement changed. See '
    'audit/complete_knoy/evidence_round21.json.\n'
)

bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('R21_EVIDENCE_SAVED', ASSET)
