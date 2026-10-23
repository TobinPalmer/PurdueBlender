import bpy,json
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/hovde_hall.blend'))
c=bpy.data.collections.get('Asset_hovde_hall');root=bpy.data.objects.get('HOVD_Root')
meshes=[o for o in c.all_objects if o and o.type=='MESH']
missing=[o.name for o in meshes if not o.data.materials]
used=sorted({m.name for o in meshes for m in o.data.materials if m})
rows=[]
for o in meshes:
 for v in o.bound_box:rows.append(o.matrix_world @ __import__('mathutils').Vector(v))
result={'file':str(P/'modular/buildings/hovde_hall.blend'),'scene':bpy.data.scenes.get('Building_hovde_hall').name if bpy.data.scenes.get('Building_hovde_hall') else None,'export_collection':c.name,'export_objects':len(c.all_objects),'mesh_objects':len(meshes),'material_slots_used':used,'unmaterialed_meshes':missing,'root_transform':{'location':list(root.location),'rotation_euler':list(root.rotation_euler),'scale':list(root.scale)},'asset_local_bounds_m':[[min(v[i] for v in rows),max(v[i] for v in rows)] for i in range(3)]}
(P/'audit/batch3_hovde/final_asset_check.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
