import bpy, json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
ID = 'massing_islamic_societyof_greater_lafayette_0130012'
ASSET = ROOT / 'modular' / 'buildings' / f'{ID}.blend'
AUDIT = ROOT / 'audit' / ID
GIS = AUDIT / 'sources' / 'purdue_gis_FID771_SOMSA.json'
OUT = Path(__file__).resolve().parent / 'reopen_validation.json'
def lonlat_to_xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)), (lat - 40.4274) * 111040.0)
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
collection = bpy.data.collections.get('Asset_' + ID)
objects = list(collection.objects) if collection else []
meshes = [o for o in objects if o.type == 'MESH']
mesh = meshes[0] if len(meshes) == 1 else None
coords = [(mesh.matrix_world @ v.co) for v in mesh.data.vertices] if mesh else []
gis_doc = json.loads(GIS.read_text(encoding='utf-8'))
feature = gis_doc['features'][0]
ring = feature['geometry']['rings'][0]
if ring and ring[0] == ring[-1]: ring = ring[:-1]
ring_xy = [lonlat_to_xy(lon,lat) for lon,lat in ring]
base_xy = [(c.x,c.y) for c in coords if abs(c.z) < 1e-5]
nearest = [min((math.hypot(x-gx,y-gy) for x,y in base_xy),default=None) for gx,gy in ring_xy]
unpacked = [im.filepath for im in bpy.data.images if im.source == 'FILE' and not im.packed_file]
linked = [lib.filepath for lib in bpy.data.libraries]
bounds = [[min(c[i] for c in coords),max(c[i] for c in coords)] for i in range(3)] if coords else None
checks = {
 'expected_scene': scene.name == 'Building_' + ID,
 'expected_collection': collection is not None,
 'exactly_one_object': len(objects) == 1,
 'single_expected_mesh_object': len(meshes) == 1 and objects[0].name == 'Islamic Society of Greater Lafayette',
 'gis_shell_vertices_within_0_00002m': len(nearest)==11 and max(nearest,default=float('inf'))<=0.00002,
 'no_modifiers': mesh is not None and not mesh.modifiers,
 'no_external_images': not unpacked,
 'no_linked_libraries': not linked,
 'mesh_faces_present': mesh is not None and len(mesh.data.polygons)>0,
}
result = {
 'validation': 'passed' if all(checks.values()) else 'failed',
 'opened_asset': str(ASSET), 'blender_version': bpy.app.version_string,
 'scene': scene.name, 'collection': collection.name if collection else None,
 'objects': [{'name':o.name,'type':o.type,'dimensions':[float(v) for v in o.dimensions],'modifiers':[m.name for m in o.modifiers]} for o in objects],
 'mesh_vertices':len(mesh.data.vertices) if mesh else None, 'mesh_faces':len(mesh.data.polygons) if mesh else None,
 'bounds_world_m':bounds, 'gis_feature':{'fid':feature['attributes'].get('FID'),'abbr':feature['attributes'].get('BLDG_ABBR'),'ring_vertices':len(ring)},
 'gis_shell_vertex_nearest_error_m':{'per_vertex':nearest,'maximum':max(nearest,default=None)},
 'unpacked_external_images':unpacked,'linked_libraries':linked,'checks':checks
}
OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
if not all(checks.values()): raise RuntimeError('Direct reopen validation failed')
