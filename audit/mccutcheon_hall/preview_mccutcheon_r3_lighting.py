import bpy, math, os
scene=bpy.data.scenes['Building_mccutcheon_hall']
world=scene.world
world.use_nodes=True
nt=world.node_tree; nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputWorld'); out.location=(400,0)
bg=nt.nodes.new('ShaderNodeBackground'); bg.location=(160,0); bg.inputs['Strength'].default_value=1.2
sky=nt.nodes.new('ShaderNodeTexSky'); sky.location=(-100,0); sky.sky_type='HOSEK_WILKIE'; sky.sun_elevation=math.radians(48); sky.sun_rotation=math.radians(215); sky.turbidity=2.2; sky.ground_albedo=0.25; sky.sun_disc=True
nt.links.new(sky.outputs['Color'],bg.inputs['Color']); nt.links.new(bg.outputs['Background'],out.inputs['Surface'])
sun=bpy.data.objects.get('Sun_Purdue_Daylight')
if sun:
 sun.data.energy=3.8; sun.data.angle=math.radians(3.0); sun.data.color=(1.0,0.97,0.92)
scene.view_settings.view_transform='AgX'; scene.view_settings.exposure=0.0; scene.view_settings.gamma=1.0
scene.render.resolution_x=1440; scene.render.resolution_y=810; scene.render.resolution_percentage=75; scene.render.image_settings.file_format='PNG'
for camname,outname in [('Cam_Hero_Perspective','mccutcheon_r3_hero_preview.png'),('Cam_East_Entrance','mccutcheon_r3_entrance_preview.png')]:
 cam=bpy.data.objects[camname]; scene.camera=cam
 if camname=='Cam_Hero_Perspective': cam.data.lens=40.0
 scene.render.filepath=os.path.abspath('audit/mccutcheon_hall/'+outname)
 bpy.ops.render.render(write_still=True,scene=scene.name)
print('MCUT_R3_PREVIEW_RENDERED')


