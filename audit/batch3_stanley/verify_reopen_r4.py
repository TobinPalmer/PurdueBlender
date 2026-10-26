import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
rootdir=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap');asset=rootdir/'modular/buildings/stanley_coulter_hall.blend';audit=rootdir/'audit/batch3_stanley'
bpy.ops.wm.open_mainfile(filepath=str(asset))
root=bpy.data.objects['AssetRoot_stanley_coulter_hall'];col=bpy.data.collections['Asset_stanley_coulter_hall']
def bounds(obj):
 pts=[obj.matrix_world@Vector(v) for v in obj.bound_box];return [[min(q[i] for q in pts) for i in range(3)],[max(q[i] for q in pts) for i in range(3)]]
frames=[o for o in col.all_objects if o.type=='MESH' and o.name.endswith('_BronzeFrame') and ('Level3_ThirdFloor' in o.name or '_F3_' in o.name)]
frame_max=max((max((o.matrix_world@v.co).z for v in o.data.vertices) for o in frames),default=None)
result={'reopen_verified':True,'file':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'asset_collection':'Asset_stanley_coulter_hall','asset_object_count':len(col.all_objects),'total_scene_objects':len(bpy.data.objects),'root_transform':{'location':list(root.location),'rotation_euler':list(root.rotation_euler),'scale':list(root.scale)},'foundation_bounds_local_m':bounds(bpy.data.objects['SC_Foundation_Limestone_Plinth']),'exterior_wall_bounds_local_m':bounds(bpy.data.objects['SC_Brick_Masonry_Exterior_Walls']),'repaired_level3_bronze_frame_count':len(frames),'max_level3_frame_vertex_z_m':frame_max,'cornice_bounds_local_m':bounds(bpy.data.objects['SC_Classical_Entablature_Cornice']),'roof_bounds_local_m':bounds(bpy.data.objects['SC_Historic_Slate_Roof']),'roof_height_status':'estimated; not GIS verified','interior_status':'schematic from historical 2022 plan/use descriptions; not a current as-built plan','placement_origin_xy_m':[-57.55689525604248,-99.14793586730957],'render_camera_names':[n for n in ['Cam_SC_02_MemorialMall_East_Hero','Cam_SC_03_East_Portico_Ground','Cam_SC_06_Interior_Schematic'] if bpy.data.objects.get(n)]}
(audit/'reopen_verification_r4.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))


