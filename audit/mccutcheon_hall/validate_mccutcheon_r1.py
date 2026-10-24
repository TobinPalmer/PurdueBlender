import bpy, json, os
from mathutils import Vector
path=os.path.abspath(bpy.data.filepath)
asset=bpy.data.collections.get('Asset_mccutcheon_hall')
assert asset and asset.name=='Asset_mccutcheon_hall'
overlay=bpy.data.objects.get('MCUT_Official_Footprint_Overlay')
assert overlay and overlay.type=='CURVE' and overlay.hide_render and not overlay.hide_viewport
assert overlay.get('source_fid')==57
root=bpy.data.objects.get('AssetRoot_mccutcheon_hall')
assert root and root.location.length < 1e-6 and all(abs(v-1)<1e-6 for v in root.scale)
scene=bpy.data.scenes.get('Building_mccutcheon_hall')
assert scene
cam=bpy.data.objects.get('Cam_Hero_Perspective')
assert cam and cam.type=='CAMERA'
# Capture saved file state first; render uses a temporary scene camera only.
imgs=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:
  resolved=bpy.path.abspath(im.filepath)
  imgs.append({'name':im.name,'path':im.filepath,'exists':os.path.exists(resolved),'packed':bool(im.packed_file)})
unpacked=[x for x in imgs if not x['exists'] and not x['packed']]
scene.camera=cam
scene.render.filepath=os.path.abspath('audit/mccutcheon_hall/mccutcheon_r1_hero.png')
scene.render.resolution_x=1280
scene.render.resolution_y=720
scene.render.resolution_percentage=75
scene.render.image_settings.file_format='PNG'
bpy.ops.render.render(write_still=True, scene=scene.name)
result={
 'asset':path,'blender_version':bpy.app.version_string,'scene':scene.name,
 'collection':asset.name,'objects_in_collection_including_children':len(asset.all_objects),
 'direct_objects':len(asset.objects),'asset_root_origin':[round(v,6) for v in root.location],
 'asset_root_scale':[round(v,6) for v in root.scale],
 'diagnostic_overlay':{'name':overlay.name,'type':overlay.type,'hide_render':overlay.hide_render,'hide_viewport':overlay.hide_viewport,'feature_id':overlay.get('source_fid')},
 'image_dependencies':imgs,'unresolved_unpacked_image_dependencies':unpacked,
 'render':'audit/mccutcheon_hall/mccutcheon_r1_hero.png','render_success':os.path.exists(scene.render.filepath)
}
print('MCUT_R1_VALIDATION='+json.dumps(result))
if unpacked: raise RuntimeError('Unpacked image dependency unresolved')
