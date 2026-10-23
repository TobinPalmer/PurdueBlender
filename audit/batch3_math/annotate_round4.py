import bpy, json
from pathlib import Path
src=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/math_sciences.blend')
bpy.ops.wm.open_mainfile(filepath=str(src))
asset=bpy.data.collections['Asset_math_sciences']
status='Profile/height is not established by a dimensioned roof plan or elevation in the reviewed sources. Geometry retained as an estimated visualization.'
for name in ['MATH_Corrected_GIS_Roof_Slab','MATH_Rooftop_Penthouse_Base','MATH_Rooftop_Penthouse_Copings','MATH_Penthouse_Louver_North','MATH_Penthouse_Louver_South','MATH_Penthouse_Louver_East']:
 o=bpy.data.objects.get(name)
 if o:
  o['source_status']=status
  o['estimated_dimensions_m']=json.dumps([round(float(x),2) for x in o.dimensions])
  o['evidence_limit']='No sourced roof configuration; retained from baseline for massing continuity, not asserted as measured.'
shell=bpy.data.objects['MATH_Corrected_GIS_Wall_Envelope']
shell['source_status']=shell.get('source_status','')+' Purdue Admissions tour note and independent 2019 ground-level photo support a pedestrian passage under MATH. Exact tunnel bearing, opening dimensions and support locations are not verified; current ground-level opening geometry remains inferred.'
for o in asset.all_objects:
 if o.name.startswith('MATH_2026_Floor_') or o.name.startswith('MATH_2026_Typical_Floor'):
  o['source_status']='Typical floor elevations and slabs are inferred from an unsourced ten-story count; no measured section/height evidence.'
bpy.ops.wm.save_as_mainfile(filepath=str(src))
print('saved annotations',len([o for o in asset.all_objects if o.get('source_status')]))
