"""Read-only independent reopen and export-collection extraction for R3."""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
ASSET = ROOT / 'modular/buildings/tarkington_hall.blend'
EXPECTED = '825d57329797fd45b6eb7784c8a6011f99a575bed6a97c11ed06e098eb618ee1'
if Path(bpy.data.filepath).resolve() != ASSET.resolve():
    raise RuntimeError(f'Wrong file opened: {bpy.data.filepath}')
sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if sha != EXPECTED: raise RuntimeError(f'Hash mismatch: {sha}')
asset = bpy.data.collections.get('Asset_tarkington_hall')
root = bpy.data.objects.get('AssetRoot_tarkington_hall')
if not asset or not root: raise RuntimeError('Missing export collection or root')
objects = list(asset.objects)
meshes = [o for o in objects if o.type == 'MESH']
connectors = [o for o in objects if o.name.startswith(('Tark_West_Connector_', 'Tark_East_Connector_'))]
membership = {
 'collection_object_count': len(objects), 'mesh_count': len(meshes),
 'connector_count': len(connectors),
 'west_connector_count': sum(o.name.startswith('Tark_West_Connector_') for o in connectors),
 'east_connector_count': sum(o.name.startswith('Tark_East_Connector_') for o in connectors),
 'all_connectors_only_in_asset_collection': all(list(o.users_collection)==[asset] for o in connectors),
 'all_connectors_parented_to_root': all(o.parent == root for o in connectors),
 'connector_meshes_missing_materials': sorted(o.name for o in connectors if o.type=='MESH' and not any(o.data.materials)),
 'duplicate_object_names_in_asset': sorted(n for n in {o.name for o in objects} if sum(x.name==n for x in objects)>1),
 'nonfinite_mesh_vertices': sorted(o.name for o in meshes if any(not all(math.isfinite(float(c)) for c in v.co) for v in o.data.vertices)),
 'materialless_meshes': sorted(o.name for o in meshes if not any(o.data.materials)),
 'invalid_material_indices': sorted(o.name for o in meshes if any(p.material_index >= len(o.data.materials) for p in o.data.polygons)),
 'external_linked_libraries': sorted(l.filepath for l in bpy.data.libraries),
 'used_materials': sorted(m.name for m in bpy.data.materials if m.users),
}
ledger = json.loads((ROOT/'audit/master_building_audit.json').read_text(encoding='utf-8'))
rec = next(r for r in ledger['records'] if r.get('id') == 'tarkington_hall')
names=set(rec['shell_candidates'])
connector_shell_prefixes=('Tark_West_Connector_Limestone_Base','Tark_West_Connector_Brick_Shaft','Tark_West_Connector_Limestone_Belt_','Tark_West_Connector_Roof_Membrane','Tark_West_Connector_Roof_Parapet','Tark_East_Connector_Limestone_Base','Tark_East_Connector_Brick_Shaft','Tark_East_Connector_Limestone_Belt_','Tark_East_Connector_Roof_Membrane','Tark_East_Connector_Roof_Parapet')
selected=[]
for o in objects:
    if o.type=='MESH' and (o.name in names or o.name.startswith(connector_shell_prefixes)):
        selected.append({'name':o.name,'vertices_xy':[[float((o.matrix_world@v.co).x),float((o.matrix_world@v.co).y)] for v in o.data.vertices]})
shell = {'asset':str(ASSET),'sha256':sha,'asset_local_xy_origin_m':[-591.6124877929688,348.0], 'export_collection':'Asset_tarkington_hall','export_objects_count':len(objects),'selected_shell_object_count':len(selected),'objects':selected,'extraction':'Fresh Blender subprocess; only objects linked to Asset_tarkington_hall; master audit shell candidate list plus structural connector objects.'}
(OUT/'independent_shell_vertices_r3.json').write_text(json.dumps(shell,indent=2)+'\n',encoding='utf-8')
world_points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
world_bounds=[[min(float(p[i]) for p in world_points),max(float(p[i]) for p in world_points)] for i in range(3)]
images=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.users and not im.packed_file:
        p=Path(bpy.path.abspath(im.filepath,library=im.library))
        if not p.exists(): images.append({'name':im.name,'path':str(p)})
report={'fresh_process_reopen':True,'asset':str(ASSET),'sha256':sha,'blender_version':bpy.app.version_string,'scene':bpy.context.scene.name,'export_collection':asset.name,'root_transform_identity':all(abs(float(v)-1)<1e-6 for v in root.scale) and all(abs(float(v))<1e-6 for v in root.rotation_euler),'membership':membership,'used_material_count':len(membership['used_materials']),'missing_external_images':images,'world_bounds_xyz_m':world_bounds,'shell_vertices_file':str(OUT/'independent_shell_vertices_r3.json')}
(OUT/'independent_reopen_r3.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
