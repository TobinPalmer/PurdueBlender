"""Fresh-process validation for the saved Niswonger round-2 asset."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/niswonger_aviation_tech_refine')
a=bpy.data.collections.get('Asset_niswonger_aviation_tech'); assert a
objs=list(a.all_objects)
root=bpy.data.objects.get('AssetRoot_niswonger_aviation_tech')
missing=[]
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists():missing.append(im.filepath)
unmaterialed=[o.name for o in objs if o.type=='MESH' and len(o.data.materials)==0]
new=[]
for name in ['NISW_R2_Roof_Brick_Wing','NISW_R2_Roof_Classroom_Wing']:
 o=bpy.data.objects.get(name); assert o and o in objs
 coords=[o.matrix_world@Vector(c) for c in o.bound_box]
 new.append({'name':name,'materials':[m.name if m else None for m in o.data.materials],
  'bounds':[[round(min(v[i] for v in coords),3) for i in range(3)],[round(max(v[i] for v in coords),3) for i in range(3)]],
  'mesh_vertices':len(o.data.vertices),'faces':len(o.data.polygons),'source_basis':o.get('source_basis'),'dimensions_basis':o.get('dimensions_basis')})
assert not missing,missing
assert not unmaterialed,unmaterialed
assert root and tuple(round(v,6) for v in root.location)==(0,0,0)
assert not [o.name for o in bpy.data.objects if o.name.startswith('Refine_')]
assert not [o.name for o in objs if o.name.startswith('NISW_R2') and o.type!='MESH']
summary={'reopened_in_fresh_blender':True,'filepath':bpy.data.filepath,'asset_collection':a.name,'objects':len(objs),'mesh_objects':sum(o.type=='MESH' for o in objs),'root_location':list(root.location),'new_roofs':new,'unmaterialed_meshes':unmaterialed,'missing_external_images':missing,'review_objects_in_asset':[o.name for o in objs if 'Review' in o.name or 'Refine_Camera' in o.name]}
(P/'reopen_validation_r2.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
