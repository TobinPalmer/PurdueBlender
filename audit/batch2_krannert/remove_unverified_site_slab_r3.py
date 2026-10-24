import bpy, os

path = os.path.abspath('modular/buildings/krannert_building.blend')
bpy.ops.wm.open_mainfile(filepath=path)
asset = bpy.data.collections['Asset_krannert_building']
root = bpy.data.objects['AssetRoot_krannert_building']
assert all(abs(v) < 1e-9 for v in root.location)
assert all(abs(v) < 1e-9 for v in root.rotation_euler)
assert all(abs(v-1) < 1e-9 for v in root.scale)
removed = bpy.data.objects.get('KRAN_Surrounding_Plaza_Paving')
if removed:
    bpy.data.objects.remove(removed, do_unlink=True)
s = bpy.context.scene
s['site_context_note'] = 'The unsupported rectangular paving plate was removed in round 3. Streets, sidewalks, landscape and terrain are master-context responsibilities; no site grade or paving extent is claimed by this source asset.'
bpy.ops.wm.save_as_mainfile(filepath=path)
print('removed_unverified_plaza', bool(removed), 'asset_objects', len(asset.objects))
