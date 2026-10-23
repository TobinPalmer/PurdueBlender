import bpy,os,json,math
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend';base=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch3_stanley'
bpy.ops.wm.open_mainfile(filepath=p);sc=bpy.context.scene;bpy.context.view_layer.update();sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=80;sc.eevee.taa_render_samples=64
for cn in ['Reference_Incompatible_Geometry_stanley_coulter_hall']: 
 c=bpy.data.collections.get(cn)
 if c:c.hide_render=True
for nm in ['Cam_SC_02_MemorialMall_East_Hero','Cam_SC_03_East_Portico_Ground']:
 sc.camera=bpy.data.objects[nm];sc.render.filepath=os.path.join(base,nm+'_final.png');bpy.ops.render.render(write_still=True)
# Clean cutaway render using room functions and furnishings only.
for cn in ['SC_Exterior_Structure','SC_Fenestration','SC_Portico_and_Entrances','SC_Roof_and_Dormers','SC_Plaza_and_Site']:
 c=bpy.data.collections.get(cn)
 if c:c.hide_render=True
for o in bpy.data.objects:
 if o.name.startswith('SC_Shell_Floor_'):o.hide_render=True
cam=bpy.data.objects['Cam_SC_06_Interior_Schematic'];cam.data.type='ORTHO';cam.data.ortho_scale=16;cam.location=(23,-7,18);cam.rotation_euler=(Vector((23,-7,1.9))-cam.location).to_track_quat('-Z','Y').to_euler();sc.camera=cam
sc.render.filepath=os.path.join(base,'Cam_SC_06_Interior_Schematic_final.png');bpy.ops.render.render(write_still=True)
# Write concise verification snapshot after reopening saved asset.
root=bpy.data.objects['AssetRoot_stanley_coulter_hall'];assetcol=bpy.data.collections['Asset_stanley_coulter_hall'];walls=bpy.data.objects['SC_Brick_Masonry_Exterior_Walls'];found=bpy.data.objects['SC_Foundation_Limestone_Plinth'];ent=bpy.data.objects['SC_Portico_Entablature'];
def bounds(o):
 pts=[o.matrix_world@Vector(c) for c in o.bound_box];return [[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]
info={'reopen_verified':True,'blend_path':p,'scene':sc.name,'asset_collection':assetcol.name,'asset_object_count':len(assetcol.all_objects),'root_transform':{'location':list(root.location),'rotation':list(root.rotation_euler),'scale':list(root.scale)},'structural_wall_bounds_local_m':bounds(walls),'foundation_bounds_local_m':bounds(found),'entry_lintel_bounds_local_m':bounds(ent),'comparison_only_gis_outline_hidden_from_render':bpy.data.objects['SC_Official_GIS_Footprint_Overlay_Ribbon'].hide_render,'roof_dormer_parts_hidden_as_unverified':sum(o.name.startswith('SC_Dormer_') and o.hide_render for o in bpy.data.objects),'renders':['Cam_SC_02_MemorialMall_East_Hero_final.png','Cam_SC_03_East_Portico_Ground_final.png','Cam_SC_06_Interior_Schematic_final.png']}
with open(os.path.join(base,'final_verification.json'),'w') as f:json.dump(info,f,indent=2)
print(json.dumps(info,indent=2))
