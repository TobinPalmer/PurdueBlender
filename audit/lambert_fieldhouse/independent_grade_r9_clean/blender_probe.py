import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
COLLECTION_NAME = 'Asset_lambert_fieldhouse'
collection = bpy.data.collections.get(COLLECTION_NAME)
if collection is None:
    raise RuntimeError(f'Missing {COLLECTION_NAME}')
objects = list(collection.all_objects)
meshes = [o for o in objects if o.type == 'MESH']
materialless = [o.name for o in meshes if not o.data.materials or any(p.material_index >= len(o.data.materials) or o.data.materials[p.material_index] is None for p in o.data.polygons)]
external_images = [{'name': im.name, 'filepath': im.filepath, 'packed': bool(im.packed_file)} for im in bpy.data.images if im.source == 'FILE']
libraries = [str(lib.filepath) for lib in bpy.data.libraries]
context_names = ['LAMB | Stadium sidewalk round4', 'LAMB | Stadium curb round4', 'LAMB | Stadium Avenue roadway round4']
context_remaining = [name for name in context_names if any(o.name == name for o in objects)]

def bounds_for(objs):
    pts=[]
    dg=bpy.context.evaluated_depsgraph_get()
    for ob in objs:
        ev=ob.evaluated_get(dg)
        pts.extend(ev.matrix_world @ Vector(c) for c in ev.bound_box)
    if not pts:
        return None
    return {'min':[min(p[i] for p in pts) for i in range(3)], 'max':[max(p[i] for p in pts) for i in range(3)]}

track = bpy.data.objects.get('LAMB | 6-lane 200 m stadium track surface')
track_perimeter = None
track_vertex_count = None
if track and len(track.data.vertices) % 2 == 0:
    half = len(track.data.vertices)//2
    centers=[(track.data.vertices[i].co + track.data.vertices[i+half].co)*0.5 for i in range(half)]
    track_perimeter=sum((centers[(i+1)%half]-centers[i]).length for i in range(half))
    track_vertex_count=len(track.data.vertices)
footprint = bpy.data.objects.get('Lambert Fieldhouse | official GIS footprint ground floor')
footprint_bounds = bounds_for([footprint]) if footprint else None
source_path = ROOT / 'audit' / 'batchC_lambert_official_footprint.json'
source_data = json.loads(source_path.read_text(encoding='utf-8'))
source_ring = source_data['features'][0]['geometry']['rings'][0][:-1]
source_world = [((p[0] + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                 (p[1] - 40.4274) * 111040.0) for p in source_ring]
anchor = ((min(p[0] for p in source_world) + max(p[0] for p in source_world)) * 0.5,
          (min(p[1] for p in source_world) + max(p[1] for p in source_world)) * 0.5)
source_local = [(p[0] - anchor[0], p[1] - anchor[1]) for p in source_world]
asset_xy = sorted({(round(float((footprint.matrix_world @ v.co).x), 6),
                    round(float((footprint.matrix_world @ v.co).y), 6))
                   for v in footprint.data.vertices}) if footprint else []
source_xy = sorted({(round(x, 6), round(y, 6)) for x, y in source_local})
def directed_nearest_error(left, right):
    if not left or not right:
        return None
    return max(min(math.hypot(a[0]-b[0], a[1]-b[1]) for b in right) for a in left)
source_to_mesh = directed_nearest_error(source_xy, asset_xy)
mesh_to_source = directed_nearest_error(asset_xy, source_xy)
source_bounds = {'min':[min(p[i] for p in source_local) for i in range(2)],
                 'max':[max(p[i] for p in source_local) for i in range(2)]}
footprint_xy_bounds = None
if footprint_bounds:
    footprint_xy_bounds = {'min':footprint_bounds['min'][:2], 'max':footprint_bounds['max'][:2]}
    footprint_xy_bounds_error = max(abs(footprint_xy_bounds[k][i] - source_bounds[k][i]) for k in ('min','max') for i in range(2))
else:
    footprint_xy_bounds_error = None
mesh_bounds = bounds_for(meshes)
hurdles = [o for o in meshes if 'hurdle' in o.name.lower()]
materials_used = sorted({m.name for o in meshes for m in o.data.materials if m})
packed_count=sum(bool(im.packed_file) for im in bpy.data.images if im.source=='FILE')
blend_path=Path(bpy.data.filepath)
report={
 'review_type':'read-only fresh-open asset probe',
 'blend':str(blend_path),
 'sha256':hashlib.sha256(blend_path.read_bytes()).hexdigest(),
 'blender_version':bpy.app.version_string,
 'scene':bpy.context.scene.name,
 'collection':collection.name,
 'collection_objects':len(objects),
 'mesh_objects':len(meshes),
 'materialless_meshes':materialless,
 'materials_used':materials_used,
 'external_images':external_images,
 'packed_external_image_count':packed_count,
 'linked_libraries':libraries,
 'bounds_world_m':mesh_bounds,
 'gis_footprint_object_found':bool(footprint),
 'gis_footprint_bounds_world_m':footprint_bounds,
 'source_footprint':{'source_path':'audit/batchC_lambert_official_footprint.json','feature_id':source_data['features'][0]['attributes']['FID'],'source_crs':source_data['spatialReference'],'ring_vertices_excluding_closure':len(source_ring),'converted_bbox_anchor_xy_m':[anchor[0],anchor[1]],'local_bounds_m':source_bounds},
 'footprint_comparison':{'unique_asset_xy_vertices':len(asset_xy),'unique_source_xy_vertices':len(source_xy),'bounds_max_abs_error_m':footprint_xy_bounds_error,'source_to_mesh_max_nearest_vertex_error_m':source_to_mesh,'mesh_to_source_max_nearest_vertex_error_m':mesh_to_source},
 'track_object_found':bool(track),
 'track_vertex_count':track_vertex_count,
 'track_lane_one_centerline_perimeter_m':track_perimeter,
 'hurdle_mesh_count':len(hurdles),
 'materialless_hurdles':[o.name for o in hurdles if not o.data.materials or any(p.material_index >= len(o.data.materials) or o.data.materials[p.material_index] is None for p in o.data.polygons)],
 'removed_context_objects_still_in_export':context_remaining,
 'status':'PASS' if not materialless and not libraries and not context_remaining and track_perimeter is not None and abs(track_perimeter-200.0)<0.05 and footprint_xy_bounds_error is not None and footprint_xy_bounds_error<0.001 and source_to_mesh is not None and source_to_mesh<0.001 and mesh_to_source is not None and mesh_to_source<0.001 else 'FAIL'
}
(OUT/'fresh_open_probe.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
if report['status']!='PASS':
    raise RuntimeError('Independent fresh-open probe failed')
