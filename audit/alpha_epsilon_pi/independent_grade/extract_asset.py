import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[3]
asset=root/'modular'/'buildings'/'alpha_epsilon_pi.blend'
out=Path(__file__).resolve().parent/'asset_geometry_snapshot.json'
bpy.ops.wm.open_mainfile(filepath=str(asset))
col=bpy.data.collections['Asset_alpha_epsilon_pi']; scene=bpy.data.scenes['Building_alpha_epsilon_pi']; obj=bpy.data.objects['AEPi_Foundation_GIS_754']
xy=[(round(v.co.x,7),round(v.co.y,7)) for v in list(obj.data.vertices)[:60]]
meshes=[o for o in col.all_objects if o.type=='MESH']
missing=[o.name for o in meshes if not o.data.materials]
parent_issues=[o.name for o in meshes if o.parent!=bpy.data.objects['AssetRoot_alpha_epsilon_pi']]
external=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file]
bounds=[[float('inf')]*3,[-float('inf')]*3]
for o in meshes:
 for corner in o.bound_box:
  p=o.matrix_world@Vector(corner)
  for i in range(3): bounds[0][i]=min(bounds[0][i],p[i]);bounds[1][i]=max(bounds[1][i],p[i])
res={'scene':scene.name,'collection':col.name,'asset_objects':len(list(col.all_objects)),'mesh_objects':len(meshes),'foundation_xy_local':xy,'placement_origin_xy_m':list(col['placement_origin_xy_m']),'world_bounds_local_m':bounds,'missing_material_meshes':missing,'parent_issues':parent_issues,'unpacked_external_images':external,'fresh_open':True}
out.write_text(json.dumps(res,indent=2),encoding='utf-8')
print(json.dumps(res,indent=2))

