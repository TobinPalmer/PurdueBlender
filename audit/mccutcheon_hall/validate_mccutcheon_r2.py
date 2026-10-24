import bpy, json, os
scene=bpy.data.scenes['Building_mccutcheon_hall']
asset=bpy.data.collections['Asset_mccutcheon_hall']
root=bpy.data.objects['AssetRoot_mccutcheon_hall']
overlay=bpy.data.objects['MCUT_Official_Footprint_Overlay']
assert overlay.hide_render is True and overlay.hide_viewport is False
assert all(bpy.data.objects[n].data.materials[0].name==expected for n,expected in [('Site_Lawn_Base','MCUT_Grass_Lawn_Qualitative'),('Site_McCutcheon_Drive','MCUT_Asphalt_Drive_Qualitative'),('Site_MacArthur_Drive','MCUT_Asphalt_Drive_Qualitative')])
scene.camera=bpy.data.objects['Cam_Hero_Perspective']
scene.render.filepath=os.path.abspath('audit/mccutcheon_hall/mccutcheon_r2_hero.png')
scene.render.resolution_x=1280; scene.render.resolution_y=720; scene.render.resolution_percentage=75
scene.render.image_settings.file_format='PNG'
bpy.ops.render.render(write_still=True,scene=scene.name)
images=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:
  resolved=bpy.path.abspath(im.filepath)
  images.append({'name':im.name,'path':im.filepath,'exists':os.path.exists(resolved),'packed':bool(im.packed_file)})
missing=[i for i in images if not i['exists'] and not i['packed']]
result={'asset':bpy.data.filepath,'version':bpy.app.version_string,'collection':asset.name,'direct_objects':len(asset.objects),'objects_including_children':len(asset.all_objects),'asset_root':{'location':list(root.location),'scale':list(root.scale)},'materials':{n:bpy.data.objects[n].data.materials[0].name for n in ['Site_Lawn_Base','Site_McCutcheon_Drive','Site_MacArthur_Drive']},'overlay':{'hide_render':overlay.hide_render,'hide_viewport':overlay.hide_viewport,'source_fid':overlay.get('source_fid')},'image_dependencies':images,'unresolved_unpacked_images':missing,'render':'audit/mccutcheon_hall/mccutcheon_r2_hero.png','render_exists':os.path.exists(scene.render.filepath)}
print('MCUT_R2_VALIDATION='+json.dumps(result))
if missing: raise RuntimeError('Missing unpacked image files')
