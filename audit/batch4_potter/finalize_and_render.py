import bpy,math
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/batch4_potter';P=R/'modular/buildings/potter_engineering.blend'
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;c=bpy.data.collections['Asset_potter_engineering']
# A restrained matte roof tone; rooftop equipment is omitted without dated close evidence.
roof=next(o for o in c.objects if 'Official_864_Roof' in o.name)
roofmat=bpy.data.materials.get('POTR_Current_Roof_Membrane_Estimate') or bpy.data.materials.new('POTR_Current_Roof_Membrane_Estimate');roofmat.use_nodes=True;roofmat.diffuse_color=(.035,.045,.05,1);rbs=next(n for n in roofmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');rbs.inputs['Base Color'].default_value=(.035,.045,.05,1);rbs.inputs['Roughness'].default_value=.95
roof.data.materials.clear();roof.data.materials.append(roofmat);roof['evidence']='Flat membrane material is a visual estimate; current roof equipment was not verified'
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1160;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-1.15
s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.35,.39,.45,1);s.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.2
# render-only evidence lighting
for o in list(s.objects):
 if o.name.startswith('POTR_Evidence_'): bpy.data.objects.remove(o,do_unlink=True)
ld=bpy.data.lights.new('POTR_Evidence_Sun','SUN');lo=bpy.data.objects.new('POTR_Evidence_Sun',ld);s.collection.objects.link(lo);lo.rotation_euler=(math.radians(25),math.radians(-35),math.radians(-32));ld.energy=1.45
ld2=bpy.data.lights.new('POTR_Evidence_Fill','AREA');lo2=bpy.data.objects.new('POTR_Evidence_Fill',ld2);s.collection.objects.link(lo2);lo2.location=(5,-15,30);ld2.energy=550;ld2.shape='DISK';ld2.size=25;lo2.rotation_euler=(Vector((29,25,6))-lo2.location).to_track_quat('-Z','Y').to_euler()
mat=bpy.data.materials.get('POTR_Evidence_Grade_Temporary') or bpy.data.materials.new('POTR_Evidence_Grade_Temporary');mat.use_nodes=True;mat.use_nodes=True; mb=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');mb.inputs['Base Color'].default_value=(.29,.31,.27,1);mb.inputs['Roughness'].default_value=.95
bpy.ops.mesh.primitive_plane_add(size=220,location=(29,25,-.10));plane=bpy.context.object;plane.name='POTR_Evidence_Grade_Temporary';plane.data.materials.append(mat)
camd=bpy.data.cameras.new('POTR_Exterior_Evidence_Camera');cam=bpy.data.objects.new('POTR_Exterior_Evidence_Camera',camd);s.collection.objects.link(cam);target=Vector((29.65,25.68,7.6));cam.location=target+Vector((100,-95,48));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=100;s.camera=cam;s.render.filepath=str(D/'exterior_current.png');bpy.ops.render.render(write_still=True)
# room205 interior proof view from the 2016 photograph, explicitly isolated from unverified plan walls
for o in bpy.data.objects:
    if o.name.startswith('POTR_Historic2016_Lab205') or o.name.startswith('POTR_R205_'): o.hide_render=False
    else:o.hide_render=True
s.view_settings.exposure=-.65;s.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.12
bpy.ops.mesh.primitive_plane_add(size=9,location=(43.3,9.3,4.87));fl=bpy.context.object;fl.name='POTR_Temporary_LabFloor';fl.data.materials.append(bpy.data.materials['POTR_2016_Lab205_Enamel'])
bpy.ops.mesh.primitive_plane_add(size=6,location=(43.3,10.4,6.3),rotation=(math.radians(90),0,0));wa=bpy.context.object;wa.name='POTR_Temporary_LabWall';wa.data.materials.append(bpy.data.materials['POTR_2016_Lab205_Enamel'])
ld3=bpy.data.lights.new('POTR_Lab_Evidence_Area','AREA');l3=bpy.data.objects.new('POTR_Lab_Evidence_Area',ld3);s.collection.objects.link(l3);l3.location=(43.4,7.0,9.0);ld3.energy=280;ld3.shape='RECTANGLE';ld3.size=4;ld3.size_y=3;l3.rotation_euler=(Vector((43.4,9.7,6.2))-l3.location).to_track_quat('-Z','Y').to_euler()
cam2d=bpy.data.cameras.new('POTR_Lab_Evidence_Camera');cam2=bpy.data.objects.new('POTR_Lab_Evidence_Camera',cam2d);s.collection.objects.link(cam2);tar=Vector((43.4,9.8,6.25));cam2.location=tar+Vector((3.0,-6.6,1.8));cam2.rotation_euler=(tar-cam2.location).to_track_quat('-Z','Y').to_euler();cam2d.type='ORTHO';cam2d.ortho_scale=6.6;s.camera=cam2;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.filepath=str(D/'interior_room205_current.png');bpy.ops.render.render(write_still=True)
# close facade detail on the east elevation (targeted from outside the GIS outline)
for o in bpy.data.objects:o.hide_render=False
s.view_settings.exposure=-.85
ld4=bpy.data.lights.new('POTR_Facade_Fill','AREA');l4=bpy.data.objects.new('POTR_Facade_Fill',ld4);s.collection.objects.link(l4);l4.location=(72,24,17);ld4.energy=900;ld4.shape='DISK';ld4.size=8;l4.rotation_euler=(Vector((58.4,30,8))-l4.location).to_track_quat('-Z','Y').to_euler()
cam3d=bpy.data.cameras.new('POTR_Facade_Detail_Camera');cam3=bpy.data.objects.new('POTR_Facade_Detail_Camera',cam3d);s.collection.objects.link(cam3);tar=Vector((58.3,30.0,8.5));cam3.location=tar+Vector((15,-1,5));cam3.rotation_euler=(tar-cam3.location).to_track_quat('-Z','Y').to_euler();cam3d.type='ORTHO';cam3d.ortho_scale=16;s.camera=cam3;s.render.resolution_x=1100;s.render.resolution_y=900;s.render.filepath=str(D/'facade_detail_current.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];print('FINAL_REOPEN',len(c.all_objects),c.objects['AssetRoot_potter_engineering'].location[:],len([im for im in bpy.data.images if im.source=='FILE' and not im.packed_file]))



