import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/knoy_hall.blend')
text=bpy.data.texts.get('EVIDENCE_AND_INTERIOR_NOTES.txt')
print(json.dumps({'textblock_found':bool(text),'contains_28_panel_source':bool(text and '28 PV panels' in text.as_string()),'contains_L5_uncertainty':bool(text and 'L5' in text.as_string() and 'remain uncertain' in text.as_string()),'contains_tower_caveat':bool(text and 'No cooling-tower geometry' in text.as_string()),'prefix':text.as_string()[:1000] if text else None},indent=2))
