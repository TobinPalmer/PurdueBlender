import bpy
from pathlib import Path
from mathutils import Vector
m=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated'];nt=m.node_tree;brick=next(n for n in nt.nodes if n.type=='TEX_BRICK');bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
for l in list(nt.links):
 if l.to_node==bs and l.to_socket.name in {'Base Color','Emission Color'}:nt.links.remove(l)
# A restrained tile color modulation over a constant red-clay field removes the large
# faceted tonal jumps while retaining a readable tile pattern.
bs.inputs['Base Color'].default_value=(0.003,0.0005,0.0002,1);bs.inputs['Emission Strength'].default_value=3.0;bs.inputs['Roughness'].default_value=0.98
mix=nt.nodes.new('ShaderNodeMix');mix.data_type='RGBA';mix.blend_type='MIX';mix.inputs[0].default_value=0.35;mix.inputs[6].default_value=(0.06,0.007,0.002,1)
nt.links.new(brick.outputs['Color'],mix.inputs[7]);nt.links.new(mix.outputs['Result'],bs.inputs['Emission Color'])
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.samples=8;S.cycles.use_denoising=True;S.render.resolution_x=1200;S.render.resolution_y=960;S.render.resolution_percentage=100;S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=-3.0
for n in ['HAAS_R9_Key','HAAS_R9_Fill','HAAS Round9 QA Camera','HAAS Round10 preview']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True)
for name,loc,energy,size in [('HAAS_R9_Key',(60,-50,65),300,72),('HAAS_R9_Fill',(0,0,80),5000,100)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-6,0,5))-o.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('HAAS Round10 preview');cam=bpy.data.objects.new('HAAS Round10 preview',camd);S.collection.objects.link(cam);S.camera=cam;camd.type='ORTHO';cam.location=(55,-55,38);cam.rotation_euler=(Vector((-6,0,6))-cam.location).to_track_quat('-Z','Y').to_euler();camd.ortho_scale=82
for o in bpy.data.objects:
 if any(col.name=='Asset_felix_haas_hall' for col in o.users_collection):o.hide_render=o.name.startswith('HAAS_Plan_')
S.render.filepath='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/roof_uniform_preview.png';bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
