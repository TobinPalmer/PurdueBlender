import bpy
from mathutils import Vector
backup='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/felix_haas_hall_round9_backup.blend'
with bpy.data.libraries.load(backup,link=False) as (src,dst): dst.materials=['HAAS_GooglePhotos_RedClayTiles_estimated']
m=dst.materials[0];m.name='HAAS_GooglePhotos_RedClayTiles_R10'
bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');out=next(n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL');nt=m.node_tree
for l in list(nt.links):
 if l.to_node==out and l.to_socket.name=='Surface':nt.links.remove(l)
bs.inputs['Roughness'].default_value=.98
for n in nt.nodes:
 if n.type=='BUMP':n.inputs['Strength'].default_value=.004;n.inputs['Distance'].default_value=.00035
em=nt.nodes.new('ShaderNodeEmission');em.name='R10 Uniform red clay contribution';em.inputs['Color'].default_value=(.35,.025,.004,1);em.inputs['Strength'].default_value=1.0
mix=nt.nodes.new('ShaderNodeMixShader');mix.name='R10 Shading equalizer';mix.inputs[0].default_value=.72
nt.links.new(em.outputs['Emission'],mix.inputs[1]);nt.links.new(bs.outputs['BSDF'],mix.inputs[2]);nt.links.new(mix.outputs['Shader'],out.inputs['Surface'])
for o in ['HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof']:
 ob=bpy.data.objects[o];ob.data.materials.clear();ob.data.materials.append(m)
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.samples=8;S.cycles.use_denoising=True;S.render.resolution_x=1200;S.render.resolution_y=960;S.render.resolution_percentage=100;S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=-3.0
for n in ['HAAS_R9_Key','HAAS_R9_Fill','HAAS Round9 QA Camera','HAAS Round10 preview']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True)
for name,loc,energy,size in [('HAAS_R9_Key',(60,-50,65),300,72),('HAAS_R9_Fill',(0,0,80),5000,100)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-6,0,5))-o.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('HAAS Round10 preview');cam=bpy.data.objects.new('HAAS Round10 preview',camd);S.collection.objects.link(cam);S.camera=cam;camd.type='ORTHO';cam.location=(55,-55,38);cam.rotation_euler=(Vector((-6,0,6))-cam.location).to_track_quat('-Z','Y').to_euler();camd.ortho_scale=82
for o in bpy.data.objects:
 if any(col.name=='Asset_felix_haas_hall' for col in o.users_collection):o.hide_render=o.name.startswith('HAAS_Plan_')
S.render.filepath='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/roof_uniform_preview.png';bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
