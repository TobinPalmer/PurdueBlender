import bpy, json, os
path=os.path.abspath(bpy.data.filepath)
scene=bpy.data.scenes['Building_mccutcheon_hall']
overlay=bpy.data.objects['MCUT_Official_Footprint_Overlay']
assert overlay.hide_render is True and overlay.hide_viewport is False
cam=bpy.data.objects['Cam_TopDown_Footprint']
# Temporarily expose the overlay for footprint diagnostics, then restore its saved state.
scene.camera=cam
overlay.hide_render=False
scene.render.filepath=os.path.abspath('audit/mccutcheon_hall/mccutcheon_r1_footprint_diagnostic.png')
scene.render.resolution_x=1200; scene.render.resolution_y=1200; scene.render.resolution_percentage=70
scene.render.image_settings.file_format='PNG'
bpy.ops.render.render(write_still=True, scene=scene.name)
overlay.hide_render=True
assert overlay.hide_render is True
print('MCUT_FOOTPRINT_RENDER='+json.dumps({'render':os.path.relpath(scene.render.filepath,os.getcwd()),'saved_asset_overlay_still_hidden':overlay.hide_render,'camera':cam.name}))
