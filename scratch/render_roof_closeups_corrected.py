import bpy, os, math
from mathutils import Vector
ROOT=os.path.abspath('.'); OUT=os.path.join(ROOT,'audit','texture_final_two')
shots=[
 ('mccutcheon_hall',Vector((-6.0,36.3,26.58)),Vector((0.0,22.0,41.0)),26.0,[]),
 ('niswonger_aviation_tech',Vector((-10.0,27.0,5.6)),Vector((4.0,7.0,21.0)),33.0,['NISW_Flat_Roof_Membrane'])]
for key,target,campos,scale,unhide in shots:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'modular','buildings',key+'.blend'))
 scene=bpy.context.scene
 # Re-enable the actual membrane only for this review render; the saved cutaway asset remains unchanged.
 for name in unhide:
  obj=bpy.data.objects.get(name)
  if obj: obj.hide_render=False
 for o in bpy.data.objects:
  if o.type=='LIGHT': o.hide_render=True
 camd=bpy.data.cameras.new('Roof detail review '+key); cam=bpy.data.objects.new('Roof detail review '+key,camd); scene.collection.objects.link(cam); cam.location=campos; cam.rotation_euler=(target-campos).to_track_quat('-Z','Y').to_euler(); camd.type='ORTHO'; camd.ortho_scale=scale; scene.camera=cam
 if not scene.world: scene.world=bpy.data.worlds.new('Roof detail review world')
 scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.24,.29,.36,1); bg.inputs['Strength'].default_value=.34
 sd=bpy.data.lights.new('Roof detail grazing sun','SUN'); so=bpy.data.objects.new('Roof detail grazing sun',sd); scene.collection.objects.link(so); so.rotation_euler=(math.radians(28),math.radians(-22),math.radians(-38)); sd.energy=1.55; sd.angle=math.radians(8)
 # broad low-energy fill keeps shadows legible and the membrane below highlight clipping
 ad=bpy.data.lights.new('Roof detail soft fill','AREA'); ao=bpy.data.objects.new('Roof detail soft fill',ad); scene.collection.objects.link(ao); ao.location=target+Vector((0,-9,13)); ad.energy=900; ad.shape='DISK'; ad.size=18; ao.rotation_euler=(target-ao.location).to_track_quat('-Z','Y').to_euler()
 scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1400; scene.render.resolution_y=900; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(OUT,key+'_roof_close.png')
 scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=0; scene.view_settings.gamma=1
 print('RENDER',key,'camera_target',tuple(round(x,2) for x in target),'scale',scale,'unhidden',unhide)
 bpy.ops.render.render(write_still=True)
