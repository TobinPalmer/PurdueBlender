import bpy, math, os, json
expected=os.path.normcase(os.path.abspath('modular/buildings/mccutcheon_hall.blend'))
if os.path.normcase(os.path.abspath(bpy.data.filepath)) != expected: raise RuntimeError('Unexpected asset file')
scene=bpy.data.scenes['Building_mccutcheon_hall']
asset=bpy.data.collections['Asset_mccutcheon_hall']
world=scene.world or bpy.data.worlds.new('McCutcheon_Clear_Day_Sky')
scene.world=world; world.name='McCutcheon_Clear_Day_Sky'; world.use_nodes=True
nt=world.node_tree; nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputWorld'); out.name='World Output'; out.location=(340,0)
bg=nt.nodes.new('ShaderNodeBackground'); bg.name='Clear Sky Background'; bg.location=(100,0); bg.inputs['Strength'].default_value=1.2
sky=nt.nodes.new('ShaderNodeTexSky'); sky.name='Purdue Daylight Sky'; sky.location=(-180,0); sky.sky_type='HOSEK_WILKIE'; sky.sun_elevation=math.radians(47); sky.sun_rotation=math.radians(215); sky.turbidity=1.7; sky.ground_albedo=0.25; sky.sun_disc=True
nt.links.new(sky.outputs['Color'],bg.inputs['Color']); nt.links.new(bg.outputs['Background'],out.inputs['Surface'])
scene.camera=bpy.data.objects['Cam_Hero_Perspective']
scene.render.resolution_x=1920; scene.render.resolution_y=1080; scene.render.resolution_percentage=100
scene.render.filepath='//../../renders/mccutcheon_hall/'
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'; scene.view_settings.exposure=0.0; scene.view_settings.gamma=1.0
# Preserve the collection's existing light object parameters so a future master
# link does not inherit a changed sun. The world/camera are standalone-scene settings.
bpy.ops.wm.save_as_mainfile(filepath=expected)
print('MCUT_R3_SAVED='+json.dumps({'file':expected,'collection':asset.name,'objects':len(asset.all_objects),'scene_camera':scene.camera.name,'world':world.name,'sky':sky.sky_type,'background_strength':bg.inputs['Strength'].default_value,'sun_object_energy':bpy.data.objects['Sun_Purdue_Daylight'].data.energy,'sun_object_angle_rad':bpy.data.objects['Sun_Purdue_Daylight'].data.angle,'render_path':scene.render.filepath}))
