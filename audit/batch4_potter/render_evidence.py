import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/batch4_potter';P=R/'modular/buildings/potter_engineering.blend'
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;c=bpy.data.collections['Asset_potter_engineering']
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1400;s.render.resolution_y=1160;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.35
s.world.color=(.22,.22,.22);s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.38,.42,.48,1);s.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.32
ld=bpy.data.lights.new('POTR_Evidence_Sun','SUN');lo=bpy.data.objects.new('POTR_Evidence_Sun',ld);s.collection.objects.link(lo);lo.rotation_euler=(math.radians(27),math.radians(-36),math.radians(-32));ld.energy=2.0
ld2=bpy.data.lights.new('POTR_Evidence_Fill','AREA');lo2=bpy.data.objects.new('POTR_Evidence_Fill',ld2);s.collection.objects.link(lo2);lo2.location=(5,-15,30);ld2.energy=2200;ld2.shape='DISK';ld2.size=28;lo2.rotation_euler=(Vector((29,25,6))-lo2.location).to_track_quat('-Z','Y').to_euler()
ground=bpy.data.materials.new('POTR_Evidence_Grade_Temporary');ground.diffuse_color=(.29,.31,.27,1);ground.use_nodes=True;ground.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.29,.31,.27,1);ground.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.95
bpy.ops.mesh.primitive_plane_add(size=220,location=(29,25,-.10));plane=bpy.context.object;plane.name='POTR_Evidence_Grade_Temporary';plane.data.materials.append(ground)
# campus-wide exterior view
camd=bpy.data.cameras.new('POTR_Exterior_Evidence_Camera');cam=bpy.data.objects.new('POTR_Exterior_Evidence_Camera',camd);s.collection.objects.link(cam);target=Vector((29.65,25.68,7.6));cam.location=target+Vector((88,-115,83));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=102;s.camera=cam;s.render.filepath=str(D/'exterior_current.png');bpy.ops.render.render(write_still=True)
# interior closeup: a deliberately labelled 2016 room evidence view, isolated from uncertain partitions
for o in bpy.data.objects:
    if o.name.startswith('POTR_Historic2016_Lab205') or o.name.startswith('POTR_R205_'): continue
    o.hide_render=True
# temporary evidence floor and rear wall
wallmat=bpy.data.materials.get('POTR_2016_Lab205_Enamel')
bpy.ops.mesh.primitive_plane_add(size=9,location=(43.3,9.3,4.87));fl=bpy.context.object;fl.name='POTR_Temporary_LabFloor';fl.data.materials.append(wallmat)
bpy.ops.mesh.primitive_plane_add(size=6,location=(43.3,10.4,6.3),rotation=(math.radians(90),0,0));wa=bpy.context.object;wa.name='POTR_Temporary_LabWall';wa.data.materials.append(wallmat)
ld3=bpy.data.lights.new('POTR_Lab_Evidence_Area','AREA');l3=bpy.data.objects.new('POTR_Lab_Evidence_Area',ld3);s.collection.objects.link(l3);l3.location=(43.4,7.0,9.0);ld3.energy=750;ld3.shape='RECTANGLE';ld3.size=4;ld3.size_y=3;l3.rotation_euler=(Vector((43.4,9.7,6.2))-l3.location).to_track_quat('-Z','Y').to_euler()
cam2d=bpy.data.cameras.new('POTR_Lab_Evidence_Camera');cam2=bpy.data.objects.new('POTR_Lab_Evidence_Camera',cam2d);s.collection.objects.link(cam2);tar=Vector((43.4,9.8,6.25));cam2.location=tar+Vector((3.8,-5.8,2.2));cam2.rotation_euler=(tar-cam2.location).to_track_quat('-Z','Y').to_euler();cam2d.type='ORTHO';cam2d.ortho_scale=6.4;s.camera=cam2;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.filepath=str(D/'interior_room205_current.png');bpy.ops.render.render(write_still=True)
# details and material evidence (close facade, windows and brick courses)
for o in bpy.data.objects:o.hide_render=False
cam3d=bpy.data.cameras.new('POTR_Facade_Detail_Camera');cam3=bpy.data.objects.new('POTR_Facade_Detail_Camera',cam3d);s.collection.objects.link(cam3);tar=Vector((32.5,51.8,8.0));cam3.location=tar+Vector((7,-10,5));cam3.rotation_euler=(tar-cam3.location).to_track_quat('-Z','Y').to_euler();cam3d.type='ORTHO';cam3d.ortho_scale=13;s.camera=cam3;s.render.resolution_x=1100;s.render.resolution_y=900;s.render.filepath=str(D/'facade_detail_current.png');bpy.ops.render.render(write_still=True)
print(json.dumps({'renders':['exterior_current.png','interior_room205_current.png','facade_detail_current.png'],'saved_asset_unchanged':True},indent=2))
