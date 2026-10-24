import bpy,json,os
asset=bpy.data.collections.get('Asset_mccutcheon_hall'); root=bpy.data.objects.get('AssetRoot_mccutcheon_hall'); overlay=bpy.data.objects.get('MCUT_Official_Footprint_Overlay')
assert asset and root and overlay and overlay.hide_render and not overlay.hide_viewport
expected={'Site_Lawn_Base':'MCUT_Grass_Lawn_Qualitative','Site_McCutcheon_Drive':'MCUT_Asphalt_Drive_Qualitative','Site_MacArthur_Drive':'MCUT_Asphalt_Drive_Qualitative'}
assigned={}
for objname,matname in expected.items():
 o=bpy.data.objects[objname]; assigned[objname]=[m.name for m in o.data.materials]; assert o.data.materials and o.data.materials[0].name==matname
missing=[]; dependencies=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:
  full=bpy.path.abspath(im.filepath); record={'name':im.name,'filepath':im.filepath,'resolved_exists':os.path.exists(full),'packed':bool(im.packed_file)}; dependencies.append(record)
  if not record['resolved_exists'] and not record['packed']: missing.append(record)
assert not missing,missing
result={'asset':os.path.abspath(bpy.data.filepath),'blender':bpy.app.version_string,'collection':asset.name,'direct_object_count':len(asset.objects),'child_inclusive_object_count':len(asset.all_objects),'asset_root_location':list(root.location),'asset_root_scale':list(root.scale),'diagnostic_overlay':{'name':overlay.name,'hide_render':overlay.hide_render,'hide_viewport':overlay.hide_viewport,'fid':overlay.get('source_fid')},'site_materials':assigned,'image_dependency_count':len(dependencies),'unresolved_unpacked_images':missing,'renders':['audit/mccutcheon_hall/mccutcheon_r1_hero.png','audit/mccutcheon_hall/mccutcheon_r2_hero.png'],'passed':True}
with open('audit/mccutcheon_hall/mccutcheon_r2_validation.json','w',encoding='utf-8') as f: json.dump(result,f,indent=2)
print('MCUT_R2_STRUCTURE_VALIDATION='+json.dumps(result))
