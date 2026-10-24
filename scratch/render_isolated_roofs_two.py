import bpy,os,math
from mathutils import Vector
ROOT=os.path.abspath('.'); OUT=os.path.join(ROOT,'audit','texture_final_two')
configs=[('mccutcheon_hall','MCUT_Center_Roof_Main'),('niswonger_aviation_tech','NISW_Flat_Roof_Membrane')]
for key,oname in configs:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'modular','buildings',key+'.blend'))
 obj=bpy.data.objects.get(oname)
 if not obj: raise RuntimeError('Missing '+oname)
 # isolate exactly the roof mesh for a legible finish close-up; source file stays unchanged
 for o in bpy.data.objects: o.hide_render=(o!=obj)
 worldpts=[obj.matrix_world@Vector(c) for c in obj.bound_box]
 mn=Vector(tuple(min(p[i] for p in worldpts) for i in range(3))); mx=Vector(tuple(max(p[i] for p in worldpts) for i in range(3))); center=(mn+mx)*.5; dims=mx-mn
 scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.type=='LIGHT': o.hide_render=True
 camd=bpy.data.cameras.new('Isolated roof finish QA'); cam=bpy.data.objects.new('Isolated roof finish QA',camd); scene.collection.objects.link(cam)
 # Close top three-quarter view crops a 22m square patch to make subtle meter-scale texture readable.
 cam.location=center+Vector((14,-20,max(dims.z,1)+65)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); camd.type='ORTHO'; camd.ortho_scale=24; scene.camera=cam
 if not scene.world: scene.world=bpy.data.worlds.new('Roof QA World')
 scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.24,.30,.38,1); bg.inputs['Strength'].default_value=.55
 ld=bpy.data.lights.new('Roof QA Sun','SUN'); lo=bpy.data.objects.new('Roof QA Sun',ld); scene.collection.objects.link(lo); lo.rotation_euler=(math.radians(12),math.radians(-20),math.radians(-35)); ld.energy=3.5; ld.angle=math.radians(12)
 scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1200; scene.render.resolution_y=850; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(OUT,key+'_roof_close.png'); scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=.2
 print('ISOLATED',key,oname,'dimensions',tuple(round(v,2) for v in dims),'materials',[m.name for m in obj.data.materials])
 bpy.ops.render.render(write_still=True)
