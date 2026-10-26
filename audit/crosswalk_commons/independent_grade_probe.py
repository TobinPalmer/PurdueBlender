import bpy, json, math
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset = root / 'modular/buildings/massing_crosswalk_commons_7c01ecd.blend'
source = json.loads((root / 'audit/crosswalk_commons/sources/osm_way_231217849_full.json').read_text(encoding='utf-8-sig'))
way = next(e for e in source['elements'] if e.get('type') == 'way' and e.get('id') == 231217849)
nodes = {e['id']: e for e in source['elements'] if e.get('type') == 'node'}
ring = []
for nid in way['nodes'][:-1]:
    n = nodes[nid]
    ring.append(((n['lon'] + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)), (n['lat'] - 40.4274) * 111040.0))
bpy.ops.wm.open_mainfile(filepath=str(asset))
col = bpy.data.collections.get('Asset_massing_crosswalk_commons_7c01ecd')
objs = list(col.objects) if col else []
obj = next((o for o in objs if o.name == 'Crosswalk Commons' and o.type == 'MESH'), None)
verts = [obj.matrix_world @ v.co for v in obj.data.vertices] if obj else []
ground = [(v.x, v.y) for v in verts if abs(v.z) < 1e-5]
errors = [min((math.hypot(x-p[0], y-p[1]) for x,y in ground), default=float('inf')) for p in ring]
report = {
  'asset_reopened': bpy.data.filepath.lower() == str(asset).lower(),
  'scene_name': bpy.context.scene.name,
  'collection_name': col.name if col else None,
  'collection_objects': [o.name for o in objs],
  'mesh_count': sum(o.type == 'MESH' for o in objs),
  'dimensions_m': list(obj.dimensions) if obj else None,
  'world_bounds_m': [[min(v[i] for v in verts), max(v[i] for v in verts)] for i in range(3)] if verts else None,
  'source_ring_vertex_count': len(ring),
  'asset_ground_vertex_count': len(ground),
  'max_source_vertex_nearest_error_m': max(errors, default=None),
  'materials': [m.name if m else None for m in obj.data.materials] if obj else [],
  'modifiers': [m.type for m in obj.modifiers] if obj else [],
  'external_images': [i.filepath for i in bpy.data.images if i.source == 'FILE' and i.filepath],
}
out = root / 'audit/crosswalk_commons/independent_grade_probe.json'
out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
