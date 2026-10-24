import bpy,os,math
from mathutils import Vector
ROOT=os.path.abspath('.'); OUT=os.path.join(ROOT,'audit','texture_final_two')
configs=[
 ('mccutcheon_hall',Vector((-6.0,36.3,26.58)),Vector((0.0,22.0,41.0)),26.0,None),
 ('niswonger_aviation_tech',Vector((7.0,31.0,5.6)),Vector((22.0,13.0,20.0)),24.0,{'NISW_Flat_Roof_Membrane','NISW_Walls_Composite_Panel','NISW_Walls_Purdue_Brick'})]
for key,target,campos,scale,keep in configs:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'modular','buildings',key+'.blend')); scene=bpy.context.scene
 if keep:
  for o in bpy.data.objects: o.hide_render=(o.name not in keep)
  if bpy.data.objects.get('NISW_Flat_Roof_Membrane'): bpy.data.objects['NISW_Flat_Roof_Membrane'].hide_render=False
 for o in bpy.data.objects:
  if o.type=='LIGHT': o.hide_render=True
 camd=bpy.data.cameras.new('Roof detail review '+key); cam=bpy.data.objects.new('Roof detail review '+key,camd); scene.collection.objects.link(cam); cam.location=campos; cam.rotation_euler=(target-campos).to_track_quat('-Z','Y').to_euler(); camd.type='ORTHO'; camd.ortho_scale=scale; scene.camera=cam
 if not scene.world: scene.world=bpy.data.worlds.new('Roof detail QA world')
 scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.24,.29,.36,1); bg.inputs['Strength'].default_value=.55
 sd=bpy.data.lights.new('Roof detail key','SUN'); so=bpy.data.objects.new('Roof detail key',sd); scene.collection.objects.link(so); so.rotation_euler=(math.radians(28),math.radians(-22),math.radians(-38)); sd.energy=2.2; sd.angle=math.radians(10)
 ad=bpy.data.lights.new('Roof detail fill','AREA'); ao=bpy.data.objects.new('Roof detail fill',ad); scene.collection.objects.link(ao); ao.location=target+Vector((0,-9,13)); ad.energy=1200; ad.shape='DISK'; ad.size=18; ao.rotation_euler=(target-ao.location).to_track_quat('-Z','Y').to_euler()
 scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1400; scene.render.resolution_y=900; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(OUT,key+'_roof_close.png')
 scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=0; scene.view_settings.gamma=1
 print('RENDER',key,'roof mat',('Roof_Membrane' if key=='mccutcheon_hall' else 'NISW_Roof_Membrane'), 'QA isolation',bool(keep))
 bpy.ops.render.render(write_still=True)
