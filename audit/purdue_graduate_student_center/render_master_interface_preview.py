import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path.cwd();TEST=ROOT/'audit/purdue_graduate_student_center/garage_boolean_test_corrected.blend';ASSET=ROOT/'modular/buildings/massing_purdue_graduate_student_center_af9c5c7.blend';OUT=ROOT/'audit/purdue_graduate_student_center/preview_master_interface.png'
bpy.ops.wm.open_mainfile(filepath=str(TEST))
source=bpy.data.objects.get('Northwestern Parking Garage')
if source is not None: source.hide_render=True; source.hide_viewport=True
with bpy.data.libraries.load(str(ASSET),link=True) as(src,dst):dst.collections=['Asset_massing_purdue_graduate_student_center_af9c5c7']
col=dst.collections[0];inst=bpy.data.objects.new('PGSC preview collection instance',None);bpy.context.scene.collection.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=col;inst.location=(153.0099342025,261.436408951,0)
sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=1400;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(OUT);sc.render.film_transparent=False;sc.view_settings.view_transform='AgX'
world=bpy.data.worlds.new('PGSC Interface Preview World') if not sc.world else sc.world;sc.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.20,0.23,0.29,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.45
camdata=bpy.data.cameras.new('PGSC Interface Preview Camera');cam=bpy.data.objects.new('PGSC Interface Preview Camera',camdata);sc.collection.objects.link(cam);cam.location=(119,230,9);target=Vector((153,261,2.2));cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();camdata.lens=65;sc.camera=cam
ld=bpy.data.lights.new('PGSC interface key','AREA');lo=bpy.data.objects.new('PGSC interface key',ld);sc.collection.objects.link(lo);lo.location=(132,232,18);ld.energy=18000;ld.shape='DISK';ld.size=25;lo.rotation_euler=(target-Vector(lo.location)).to_track_quat('-Z','Y').to_euler()
# A soft fill keeps the garage cut edge and PGSC front readable.
ld2=bpy.data.lights.new('PGSC interface fill','AREA');lo2=bpy.data.objects.new('PGSC interface fill',ld2);sc.collection.objects.link(lo2);lo2.location=(178,264,14);ld2.energy=9000;ld2.size=30;lo2.rotation_euler=(target-Vector(lo2.location)).to_track_quat('-Z','Y').to_euler()
bpy.ops.render.render(write_still=True);print(str(OUT))



