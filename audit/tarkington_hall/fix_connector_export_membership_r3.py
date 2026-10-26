"""Move the intentionally modeled connector components into Tarkington's export collection."""
import bpy, json, math
from pathlib import Path

asset = bpy.data.collections.get('Asset_tarkington_hall')
if asset is None:
    raise RuntimeError('Missing Asset_tarkington_hall collection')
prefixes=('Tark_West_Connector_','Tark_East_Connector_')
objects=sorted([o for o in bpy.data.objects if o.name.startswith(prefixes)],key=lambda o:o.name)
counts={prefix:sum(o.name.startswith(prefix) for o in objects) for prefix in prefixes}
if len(objects)!=96 or counts[prefixes[0]]!=48 or counts[prefixes[1]]!=48:
    raise RuntimeError(f'Unexpected connector set; expected 48 per bridge, got {counts}')
before={o.name:[list(row) for row in o.matrix_world] for o in objects}
for obj in objects:
    if obj.name not in asset.objects:
        asset.objects.link(obj)
    for col in list(obj.users_collection):
        if col != asset:
            col.objects.unlink(obj)
    if len(obj.users_collection)!=1 or obj.users_collection[0]!=asset:
        raise RuntimeError(f'Unexpected collection membership for {obj.name}: {[c.name for c in obj.users_collection]}')
    if not obj.parent or obj.parent.name!='AssetRoot_tarkington_hall':
        raise RuntimeError(f'Unexpected parent for {obj.name}')
    after=[list(row) for row in obj.matrix_world]
    if any(abs(before[obj.name][i][j]-after[i][j])>1e-5 for i in range(4) for j in range(4)):
        raise RuntimeError(f'Matrix changed while relinking {obj.name}')

report={
 'asset_collection':'Asset_tarkington_hall',
 'intended_connector_meshes':len(objects),
 'per_bridge':counts,
 'all_linked_only_to_asset_collection':all(list(o.users_collection)==[asset] for o in objects),
 'all_parented_to_asset_root':all(o.parent and o.parent.name=='AssetRoot_tarkington_hall' for o in objects),
 'world_matrices_preserved':True,
 'materialless_connector_meshes':[o.name for o in objects if not any(m for m in o.data.materials)],
 'duplicate_names':sorted(n for n in set(o.name for o in objects) if sum(x.name==n for x in objects)>1),
 'asset_collection_total_objects':len(asset.objects),
}
out=Path(bpy.data.filepath).parent.parent.parent/'audit'/'tarkington_hall'/'connector_export_membership_r3.json'
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps(report,indent=2))
