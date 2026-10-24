import bpy, json, os
from mathutils import Vector
asset=bpy.data.collections['Asset_mccutcheon_hall']; scene=bpy.data.scenes['Building_mccutcheon_hall']; root=bpy.data.objects['AssetRoot_mccutcheon_hall']; overlay=bpy.data.objects['MCUT_Official_Footprint_Overlay']
assert len(asset.all_objects)==235 and len(asset.objects)==1
assert root.location.length<1e-6 and all(abs(x-1)<1e-6 for x in root.scale)
assert overlay.hide_render is True and overlay.hide_viewport is False and overlay.get('source_fid')==57
assert scene.camera and scene.camera.name=='Cam_Hero_Perspective' and abs(scene.camera.data.lens-30.0)<1e-4
assert scene.world and scene.world.name=='McCutcheon_Clear_Day_Sky'
assert any(n.type=='TEX_SKY' and n.sky_type=='HOSEK_WILKIE' for n in scene.world.node_tree.nodes)
assert abs(bpy.data.objects['Sun_Purdue_Daylight'].data.energy-3.6)<1e-4
expected={'Site_Lawn_Base':'MCUT_Grass_Lawn_Qualitative','Site_McCutcheon_Drive':'MCUT_Asphalt_Drive_Qualitative','Site_MacArthur_Drive':'MCUT_Asphalt_Drive_Qualitative'}
materials={}
for name,mname in expected.items():
 obj=bpy.data.objects[name]; materials[name]=[m.name for m in obj.data.materials]; assert obj.data.materials and obj.data.materials[0].name==mname
images=[]; missing=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:
  rp=bpy.path.abspath(im.filepath); item={'name':im.name,'filepath':im.filepath,'resolved_exists':os.path.exists(rp),'packed':bool(im.packed_file)}; images.append(item)
  if not item['resolved_exists'] and not item['packed']: missing.append(item)
assert not missing,missing
scene.render.resolution_x=1440; scene.render.resolution_y=810; scene.render.resolution_percentage=75; scene.render.image_settings.file_format='PNG'
for camname,out in [('Cam_Hero_Perspective','mccutcheon_r3_hero.png'),('Cam_East_Entrance','mccutcheon_r3_entrance.png')]:
 scene.camera=bpy.data.objects[camname]; scene.render.filepath=os.path.abspath('audit/mccutcheon_hall/'+out)
 bpy.ops.render.render(write_still=True,scene=scene.name)
# Store stable validation, not temporary render camera settings.
result={'asset':os.path.abspath(bpy.data.filepath),'blender_version':bpy.app.version_string,'collection':asset.name,'direct_objects':len(asset.objects),'child_inclusive_objects':len(asset.all_objects),'root_location':list(root.location),'root_scale':list(root.scale),'saved_scene_camera':'Cam_Hero_Perspective','saved_hero_camera_lens_mm':30.0,'saved_world':'McCutcheon_Clear_Day_Sky','saved_sky_type':'HOSEK_WILKIE','saved_world_strength':1.2,'sun_parameters_unchanged':True,'diagnostic_overlay':{'hide_render':overlay.hide_render,'hide_viewport':overlay.hide_viewport,'source_fid':overlay.get('source_fid')},'site_materials':materials,'packed_foliage_image_count':sum(x['packed'] for x in images),'unresolved_unpacked_images':missing,'renders':['audit/mccutcheon_hall/mccutcheon_r3_hero.png','audit/mccutcheon_hall/mccutcheon_r3_entrance.png'],'passed':True,'master_edited':False}
with open('audit/mccutcheon_hall/mccutcheon_r3_validation.json','w',encoding='utf-8') as f: json.dump(result,f,indent=2)
print('MCUT_R3_VALIDATION='+json.dumps(result))

