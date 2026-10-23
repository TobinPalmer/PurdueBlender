import bpy,math,bmesh
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter')
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;c=bpy.data.collections['Asset_potter_engineering'];core=(10.5,35.2)
for o in bpy.data.objects:o.hide_render=True
# Show true floor slabs, cropped to a local cutaway window around stair core 1.
for nm in ['POTR_Interior_Slab_Level_1_EstimatedElevation','POTR_Interior_Slab_Level_2_EstimatedElevation','POTR_Interior_Slab_Level_3_EstimatedElevation','POTR_Official_864_Roof']:
 src=c.objects[nm];me=src.data.copy();bm=bmesh.new();bm.from_mesh(me);remove=[f for f in bm.faces if abs(f.calc_center_median().x-core[0])>3.4 or abs(f.calc_center_median().y-core[1])>2.8];bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(me);bm.free();me.update();ob=bpy.data.objects.new('POTR_Evidence_CutSlab_'+nm,me);s.collection.objects.link(ob);ob.hide_render=False
for o in c.all_objects:
 if o.name.startswith('POTR_2016_StairCore3_') and ('Level' in o.name or 'Handrails' in o.name):o.hide_render=False
# hide penthouse geometry and non-core details in this explanatory crop
for o in c.all_objects:
 if o.name.startswith('POTR_2016_StairCore3_') or o.name.startswith('POTR_4S04_') or o.name=='POTR_Historic2016_Room401_Penthouse_Massing':o.hide_render=False
# studio lighting
ld=bpy.data.lights.new('POTR_Evidence_Cutaway_Key','AREA');lo=bpy.data.objects.new('POTR_Evidence_Cutaway_Key',ld);s.collection.objects.link(lo);lo.location=(58,-8,19);ld.energy=1700;ld.shape='DISK';ld.size=11;lo.rotation_euler=(Vector((10.5,35.2,5))-lo.location).to_track_quat('-Z','Y').to_euler()
ld2=bpy.data.lights.new('POTR_Evidence_Cutaway_Fill','AREA');lo2=bpy.data.objects.new('POTR_Evidence_Cutaway_Fill',ld2);s.collection.objects.link(lo2);lo2.location=(43,9,15);ld2.energy=800;ld2.size=10;lo2.rotation_euler=(Vector((10.5,35.2,5))-lo2.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('POTR_Evidence_Cutaway_Camera');cam=bpy.data.objects.new('POTR_Evidence_Cutaway_Camera',camd);s.collection.objects.link(cam);tar=Vector((10.5,35.2,5));cam.location=tar+Vector((9,-16,8));cam.rotation_euler=(tar-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=23;s.camera=cam;s.render.resolution_x=1300;s.render.resolution_y=1250;s.render.resolution_percentage=85;s.render.filepath=str(D/'stairwell_cutaway.png');s.view_settings.exposure=-.7;bpy.ops.render.render(write_still=True)


