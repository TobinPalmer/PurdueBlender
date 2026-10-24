import bpy, os, math
from mathutils import Vector
ROOT=os.path.abspath('.'); out=os.path.join(ROOT,'audit','texture_final_two','niswonger_aviation_tech_roof_close.png')
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'modular','buildings','niswonger_aviation_tech.blend'))
scene=bpy.context.scene
keep={'NISW_Flat_Roof_Membrane','NISW_Walls_Composite_Panel','NISW_Walls_Purdue_Brick'}
for o in bpy.data.objects:
 o.hide_render=(o.name not in keep)
 if o.name=='NISW_Flat_Roof_Membrane': o.hide_render=False
# Focus on the northeastern membrane edge; retain the wall edge for scale and a clear surface boundary.
target=Vector((7.0,31.0,5.6)); campos=Vector((22.0,13.0,20.0))
camd=bpy.data.cameras.new('Niswonger roof surface detail'); cam=bpy.data.objects.new('Niswonger roof surface detail',camd); scene.collection.objects.link(cam); cam.location=campos; cam.rotation_euler=(target-campos).to_track_quat('-Z','Y').to_euler(); camd.type='ORTHO'; camd.ortho_scale=24; scene.camera=cam
for o in bpy.data.objects:
 if o.type=='LIGHT': o.hide_render=True
if not scene.world: scene.world=bpy.data.worlds.new('Niswonger roof close QA'); scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.18,.22,.28,1); bg.inputs['Strength'].default_value=.28
ld=bpy.data.lights.new('Niswonger roof grazing light','SUN'); lo=bpy.data.objects.new('Niswonger roof grazing light',ld); scene.collection.objects.link(lo); lo.rotation_euler=(math.radians(28),math.radians(-22),math.radians(-38)); ld.energy=1.15; ld.angle=math.radians(5)
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1400; scene.render.resolution_y=900; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=out; scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=-.25; scene.view_settings.gamma=1
print('isolated roof QA target',tuple(target),'included',keep,'roof finish',bpy.data.materials['NISW_Roof_Membrane'].get('texture_finish_final_two'))
bpy.ops.render.render(write_still=True)
