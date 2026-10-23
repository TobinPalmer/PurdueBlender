import bpy,os,json,math
from mathutils import Vector
base=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch3_stanley'
asset=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=asset);sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=1500;sc.render.resolution_y=850;sc.render.resolution_percentage=75;sc.eevee.taa_render_samples=48
for c in bpy.data.collections:
 if c.name.startswith('Reference_Incompatible'): c.hide_render=True
for nm in ['Cam_SC_01_Footprint_TopDown','Cam_SC_02_MemorialMall_East_Hero','Cam_SC_03_East_Portico_Ground','Cam_SC_04_South_Courtyard_Perspective','Cam_SC_05_West_OvalDrive_Hero']:
 o=bpy.data.objects.get(nm)
 if o:
  sc.camera=o;sc.render.filepath=os.path.join(base,nm+'_round2.png');bpy.ops.render.render(write_still=True);print('RENDERED',nm)
# Ground-floor hub cutaway. Hide exterior shell and upper slabs for this evidence view only.
for nm in ['SC_Brick_Masonry_Exterior_Walls','SC_Foundation_Limestone_Plinth','SC_Limestone_Corner_Quoins','SC_Historic_Slate_Roof','SC_Official_GIS_Footprint_Overlay_Ribbon']:
 o=bpy.data.objects.get(nm)
 if o:o.hide_render=True
for o in bpy.data.objects:
 if o.name.startswith('SC_Portico_') or o.name.startswith('SC_Main_') or o.name.startswith('SC_Door_') or o.name.startswith('SC_Lantern_'):o.hide_render=True
for nm in ['SC_Shell_Floor_0_Basement','SC_Shell_Floor_2','SC_Shell_Floor_3','SC_Shell_Floor_4_Attic']:
 o=bpy.data.objects.get(nm)
 if o:o.hide_render=True
cam=bpy.data.objects['Cam_SC_06_Interior_Schematic'];sc.camera=cam;sc.render.filepath=os.path.join(base,'Cam_SC_06_Interior_Schematic_round2.png');bpy.ops.render.render(write_still=True);print('RENDERED interior')
# Source footprint/base shell shape and marker transform evidence.
root=bpy.data.objects['AssetRoot_stanley_coulter_hall'];baseobj=bpy.data.objects['SC_Foundation_Limestone_Plinth']
world=[baseobj.matrix_world @ v.co for v in baseobj.data.vertices]
info={'reopened_asset':asset,'building_id':'stanley_coulter_hall','official_source':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','official_feature_id':56,'gis_snapshot_date':'2026-10-22','footprint_status':'prior structural-masonry audit measured source vs official GIS AABB extrema discrepancy <0.004 m; shape comparison on imported 12-vertex ring used in asset; no footprint or placement edits this pass','building_origin_xy':[-57.55689525604248,-99.14793586730957],'asset_root_location':list(root.location),'asset_root_rotation':list(root.rotation_euler),'asset_root_scale':list(root.scale),'structural_foundation_vertices':len(baseobj.data.vertices),'structural_foundation_bounds_local':[list(min(v[i] for v in world) for i in range(3)),list(max(v[i] for v in world) for i in range(3))],'asset_object_count':len(bpy.data.collections['Asset_stanley_coulter_hall'].all_objects),'screenshots':[os.path.join(base,n+'_round2.png') for n in ['Cam_SC_01_Footprint_TopDown','Cam_SC_02_MemorialMall_East_Hero','Cam_SC_03_East_Portico_Ground','Cam_SC_04_South_Courtyard_Perspective','Cam_SC_05_West_OvalDrive_Hero','Cam_SC_06_Interior_Schematic']]}
with open(os.path.join(base,'geometry_and_reopen_check.json'),'w') as f:json.dump(info,f,indent=2)
print('CHECK',json.dumps(info))
