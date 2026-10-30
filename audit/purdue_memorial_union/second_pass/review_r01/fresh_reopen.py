import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
p=Path(bpy.data.filepath);c=bpy.data.collections.get('Asset_purdue_memorial_union');root=bpy.data.objects.get('AssetRoot_purdue_memorial_union')
r={'asset':str(p),'asset_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'expected_collection':c is not None,'collection_objects':len(c.all_objects),'direct_objects':len(c.objects),'unit_system':bpy.context.scene.unit_settings.system,'unit_scale':bpy.context.scene.unit_settings.scale_length,'root_matrix':[list(v) for v in root.matrix_world],'root_identity':all(abs(root.matrix_world[i][j]-(1 if i==j else 0))<1e-7 for i in range(4) for j in range(4)),'external_unpacked_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file],'libraries':[l.filepath for l in bpy.data.libraries],'materialless_meshes':[o.name for o in c.all_objects if o.type=='MESH' and not o.data.materials],'preserved_interior':{'count':len(bpy.data.collections['PMU_Preserved_FirstPass_Interior'].objects),'hide_render':bpy.data.collections['PMU_Preserved_FirstPass_Interior'].hide_render,'hide_viewport':bpy.data.collections['PMU_Preserved_FirstPass_Interior'].hide_viewport}}
pts=[o.matrix_world@Vector(x) for o in c.objects if o.type=='MESH' for x in o.bound_box];r['exterior_mesh_bounds']=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
source=json.loads(Path('C:/Users/gotse/Documents/Codex/2026-10-28/in-x20/work/PurdueBlender-second-pass/research/second_pass/buildings/purdue_memorial_union/sources/purdue_footprint.json').read_text())['features'][0]['geometry']['rings'][0][:-1]
xy=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274))-205.75,(lat-40.4274)*111040+271.65) for lon,lat in source]
errors=[]
for i,pt in enumerate(xy):
 o=bpy.data.objects.get('PMU_SP_Inventory_Wall_'+str(i));v=o.matrix_world@o.data.vertices[0].co
 errors.append(math.hypot(v.x-pt[0],v.y-pt[1]))
r['inventory_wall_first_vertex_max_xy_error_m']=max(errors);r['inventory_wall_count']=len(errors)
Path('C:/Users/gotse/Documents/Codex/2026-10-28/in-x20/work/PurdueBlender-second-pass/audit/purdue_memorial_union/second_pass/review_r01/fresh_reopen.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
