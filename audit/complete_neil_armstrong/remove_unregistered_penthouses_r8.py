import bpy,hashlib,json,os
root=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
asset=os.path.join(root,'modular','buildings','neil_armstrong_hall.blend')
base=os.path.join(root,'audit','complete_neil_armstrong')
prior=json.load(open(os.path.join(base,'validation_r7.json'),encoding='utf-8'))
sha=hashlib.sha256(open(asset,'rb').read()).hexdigest()
if sha!=prior['source_hash']:
 raise RuntimeError(f'R7 source drift: {sha}')
bpy.ops.wm.open_mainfile(filepath=asset)
col=bpy.data.collections['Asset_neil_armstrong_hall']
root_obj=bpy.data.objects['AssetRoot_neil_armstrong_hall']
if root_obj.location[:]!= (0.0,0.0,0.0) or len(col.objects)!=449: raise RuntimeError('Unexpected R7 baseline')
remove_names=['ARMS_East_Roof_Penthouse','ARMS_East_Penthouse_Louvers','ARMS_West_Roof_Penthouse','ARMS_West_Penthouse_Louvers']
removed=[]
for name in remove_names:
 obj=bpy.data.objects.get(name)
 if obj is None or obj.name not in col.objects: raise RuntimeError('Expected roof volume missing: '+name)
 removed.append({'name':name,'bounds_local_m':[[float(v) for v in obj.bound_box[i]] for i in []]})
 bpy.data.objects.remove(obj,do_unlink=True)
root_obj['r8_roof_revision']='Removed two unregistered high rooftop box assemblies from R7. FRP confirms a mechanical penthouse exists; 2018 LiDAR places only two >22m 5-ft cells inside FID 642 at X≈-13.53m, Y≈5.75–7.27m, so no large end-located penthouse footprint is modeled. Exact penthouse form/location remain unknown.'
bpy.ops.wm.save_as_mainfile(filepath=asset)
print(json.dumps({'revision':'R8','removed_objects':remove_names,'collection_objects':len(col.objects),'asset_sha256':hashlib.sha256(open(asset,'rb').read()).hexdigest()},indent=2))
