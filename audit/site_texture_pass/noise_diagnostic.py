import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'audit'/'site_texture_pass'/'05_coordinate_noise_diagnostic.png'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modular'/'site'/'campus_site.blend'))
s=bpy.context.scene
for o in s.objects: o.hide_render=True
terrain=bpy.data.objects['Purdue_Terrain_Ground']; terrain.hide_render=False
m=bpy.data.materials.new('QA_Terrain_Noise_Diagnostic'); m.use_nodes=True
n=m.node_tree.nodes; l=m.node_tree.links; n.clear()
geo=n.new('ShaderNodeNewGeometry'); noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=.8; noise.inputs['Detail'].default_value=2
l.new(geo.outputs['Position'],noise.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(0,0,0,1); ramp.color_ramp.elements[1].color=(1,1,1,1); l.new(noise.outputs['Fac'],ramp.inputs['Fac'])
em=n.new('ShaderNodeEmission'); l.new(ramp.outputs['Color'],em.inputs['Color']); out=n.new('ShaderNodeOutputMaterial'); l.new(em.outputs[0],out.inputs['Surface'])
terrain.data.materials.clear(); terrain.data.materials.append(m)
s.render.engine='BLENDER_EEVEE'; s.render.resolution_x=960; s.render.resolution_y=640; s.render.resolution_percentage=100; s.render.image_settings.file_format='PNG'; s.render.filepath=str(OUT)
s.view_settings.view_transform='Standard'; s.view_settings.look='Medium High Contrast'; s.view_settings.exposure=0
camd=bpy.data.cameras.new('QA_Noise_Cam'); cam=bpy.data.objects.new('QA_Noise_Cam',camd); s.collection.objects.link(cam); cam.location=(1000,990,25); cam.rotation_euler=(Vector((1000,1000,0))-cam.location).to_track_quat('-Z','Y').to_euler(); camd.lens=55; camd.clip_end=5000; s.camera=cam
bpy.ops.render.render(write_still=True)
print('DIAGNOSTIC',OUT)
