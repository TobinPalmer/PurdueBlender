import bpy,os,math,json
from mathutils import Vector
base=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch3_stanley'
asset=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=asset)
sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=1500;sc.render.resolution_y=850;sc.render.resolution_percentage=75;sc.eevee.taa_render_samples=48
for c in bpy.data.collections:
 if c.name.startswith('Reference_Incompatible'): c.hide_render=True
for nm in ['Cam_SC_01_Footprint_TopDown','Cam_SC_02_MemorialMall_East_Hero','Cam_SC_03_East_Portico_Ground','Cam_SC_04_South_Courtyard_Perspective','Cam_SC_05_West_OvalDrive_Hero']:
 cam=bpy.data.objects.get(nm)
 if cam:
  sc.camera=cam;sc.render.filepath=os.path.join(base,nm+'_round1.png');bpy.ops.render.render(write_still=True);print('RENDERED',nm)
# Interior presentation camera for evidence only; scene save is not altered.
def look_at(cam, target): cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('Cam_SC_06_Interior_Schematic_Data');cam=bpy.data.objects.new('Cam_SC_06_Interior_Schematic',cam_data);sc.collection.objects.link(cam);cam.location=(37,-7,9);cam_data.lens=54;look_at(cam,(21.5,-7,2.7));sc.camera=cam
for nm in ['SC_Brick_Masonry_Exterior_Walls','SC_Foundation_Limestone_Plinth','SC_Limestone_Corner_Quoins','SC_Historic_Slate_Roof']:
 o=bpy.data.objects.get(nm)
 if o: o.hide_render=True
sc.render.filepath=os.path.join(base,'Cam_SC_06_Interior_Schematic_round1.png');bpy.ops.render.render(write_still=True);print('RENDERED interior')
# Placement/extent check from source GIS reference and asset root transform.
root=bpy.data.objects['AssetRoot_stanley_coulter_hall']
info={'building_id':'stanley_coulter_hall','asset':'modular/buildings/stanley_coulter_hall.blend','asset_collection':'Asset_stanley_coulter_hall','asset_object_count':len(bpy.data.collections['Asset_stanley_coulter_hall'].all_objects),'root_location':list(root.location),'root_rotation':list(root.rotation_euler),'root_scale':list(root.scale),'render_paths':[os.path.join(base,n+'_round1.png') for n in ['Cam_SC_01_Footprint_TopDown','Cam_SC_02_MemorialMall_East_Hero','Cam_SC_03_East_Portico_Ground','Cam_SC_04_South_Courtyard_Perspective','Cam_SC_05_West_OvalDrive_Hero','Cam_SC_06_Interior_Schematic']]}
with open(os.path.join(base,'round1_geometry_check.json'),'w') as f:json.dump(info,f,indent=2)
print('GEOMETRY',json.dumps(info))
