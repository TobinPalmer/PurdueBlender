from pathlib import Path
import json, math, hashlib
import bpy
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ASSET=ROOT/'modular/buildings/beering_hall.blend'
PROBE=HERE/'collection_export_probe.blend'
MANIFEST=json.loads((ROOT/'modular/manifest.json').read_text(encoding='utf-8'))
ENTRY=next(x for x in MANIFEST['assets'] if x['id']=='beering_hall')
ORIGIN=ENTRY['placement_origin_xy_m']
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.context.scene
coll=bpy.data.collections.get('Asset_beering_hall')
assert scene.name=='Building_beering_hall' and coll is not None
# Collection contract validated by the manifest ID and collection name; legacy source lacks an ID custom property.
objs=list(coll.objects)
assert objs

def evaluated_bounds(objects):
    deps=bpy.context.evaluated_depsgraph_get(); pts=[]
    for obj in objects:
        if obj.type!='MESH': continue
        ev=obj.evaluated_get(deps); mesh=ev.to_mesh()
        pts.extend(ev.matrix_world @ v.co for v in mesh.vertices)
        ev.to_mesh_clear()
    if not pts: return None
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]

structural=[o for o in objs if o.name in {'BRNG_Classroom_Wing_Masonry','BRNG_Office_Tower_Masonry'}]
assert len(structural)==2, [x.name for x in structural]
structural_bounds=evaluated_bounds(structural)
all_bounds=evaluated_bounds(objs)
roof=[o for o in objs if o.name.startswith('BRNG_Rooftop_Room_')]
roof_bounds=evaluated_bounds(roof)
roof_center=[(roof_bounds[i][0]+roof_bounds[i][1])/2 for i in range(2)] if roof_bounds else None
external_images=[]; linked=[]
for o in objs:
    for slot in o.material_slots:
        mat=slot.material
        if mat and mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type=='TEX_IMAGE' and node.image and node.image.filepath:
                    external_images.append(node.image.filepath)
for lib in bpy.data.libraries:
    linked.append(lib.filepath)
source=json.loads((ROOT/'audit/beering_hall/purdue_gis_feature_251.json').read_text(encoding='utf-8'))
feature=(source.get('features') or [source])[0]
props=feature.get('properties',{})
geom=feature.get('geometry',{})
coords=geom.get('coordinates',[])
while coords and isinstance(coords[0][0],list): coords=coords[0]
# GeoJSON coordinates are lon/lat. Project with repository documented approximation and subtract marker origin.
lat0=40.4274; lon0=-86.9137
ring=[]
for lon,lat,*_ in coords:
    x=(lon-lon0)*111412.84*math.cos(math.radians(lat0))-ORIGIN[0]
    y=(lat-lat0)*111040.0-ORIGIN[1]
    ring.append((x,y))
# Measure source polygon ring against the bottom vertices of the structural shell.
deps=bpy.context.evaluated_depsgraph_get(); shell_xy=[]
for o in structural:
    ev=o.evaluated_get(deps);mesh=ev.to_mesh()
    for v in mesh.vertices:
        p=ev.matrix_world@v.co
        if abs(p.z)<1e-4: shell_xy.append((p.x,p.y))
    ev.to_mesh_clear()
def nearest(p,points): return min(math.hypot(p[0]-q[0],p[1]-q[1]) for q in points) if points else None
ring_open=ring[:-1] if len(ring)>1 and math.dist(ring[0],ring[-1])<1e-8 else ring
src_to_shell=[nearest(p,shell_xy) for p in ring_open]
shell_to_src=[nearest(p,ring_open) for p in shell_xy]
# bbox position check for structural wall envelope versus source ring.
src_bounds=[[min(p[i] for p in ring_open),max(p[i] for p in ring_open)] for i in range(2)]
wall_bounds=structural_bounds[:2]
max_bbox_delta=max(abs(wall_bounds[i][j]-src_bounds[i][j]) for i in range(2) for j in range(2))
source_bbox_center=[(src_bounds[i][0]+src_bounds[i][1])/2 for i in range(2)]
wall_bbox_center=[(wall_bounds[i][0]+wall_bounds[i][1])/2 for i in range(2)]
bbox_center_error=math.dist(source_bbox_center,wall_bbox_center)
expected=set(ENTRY.get('objects',[])); actual={o.name for o in objs}
probe={
 'asset':str(ASSET),'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),
 'blender_version':bpy.app.version_string,'scene':scene.name,'collection':coll.name,
 'building_id':coll.get('building_id'),'collection_object_count':len(objs),
 'object_names':sorted(actual),'manifest_object_count':ENTRY.get('object_count'),
 'manifest_name_count':len(expected),'manifest_names_match':expected==actual,
 'manifest_names_missing_from_asset':sorted(expected-actual),'asset_names_missing_from_manifest':sorted(actual-expected),
 'gis_feature_id':props.get('OBJECTID',props.get('FID',251)),
 'gis_attributes':{k:props.get(k) for k in ['BLDG_ABBR','BUILDING_N','ADDRESS','NUM_LEVELS','CountOfFLO','Extrution','R']},
 'gis_ring_vertices':len(ring_open),'gis_ring_local_bounds_m':src_bounds,
 'structural_wall_objects':[o.name for o in structural],'structural_wall_bounds_local_m':structural_bounds,
 'max_bbox_delta_m':max_bbox_delta,'gis_bbox_center_local_m':source_bbox_center,'wall_bbox_center_local_m':wall_bbox_center,
 'bbox_center_error_m':bbox_center_error,
 'gis_to_shell_vertex_hausdorff_m':max(src_to_shell) if src_to_shell else None,
 'shell_to_gis_ring_vertex_hausdorff_m':max(shell_to_src) if shell_to_src else None,
 'overall_asset_bounds_local_m':all_bounds,'roof_room_object_count':len(roof),
 'roof_room_bounds_local_m':roof_bounds,'roof_room_xy_center_local_m':roof_center,
 'manifest_placement_origin_xy_m':ORIGIN,'external_image_dependencies':sorted(set(external_images)),
 'linked_libraries':linked,'camera_light_objects_in_asset_collection':[o.name for o in objs if o.type in {'CAMERA','LIGHT'}],
}
with (HERE/'blender_probe.json').open('w',encoding='utf-8') as f: json.dump(probe,f,indent=2)
bpy.data.libraries.write(str(PROBE),{coll},path_remap='RELATIVE_ALL',fake_user=True)
bpy.ops.wm.open_mainfile(filepath=str(PROBE))
export_coll=bpy.data.collections.get('Asset_beering_hall')
assert export_coll and len(export_coll.objects)==len(objs)
assert not [o for o in export_coll.objects if o.type in {'CAMERA','LIGHT'}]
with (HERE/'export_probe.json').open('w',encoding='utf-8') as f:
    json.dump({'reopened_export':str(PROBE),'collection':export_coll.name,'object_count':len(export_coll.objects),
      'camera_light_objects':[o.name for o in export_coll.objects if o.type in {'CAMERA','LIGHT'}],
      'linked_libraries':[lib.filepath for lib in bpy.data.libraries]},f,indent=2)
print(json.dumps({'probe':str(HERE/'blender_probe.json'),'export_probe':str(HERE/'export_probe.json'),
 'object_count':len(objs),'max_bbox_delta_m':max_bbox_delta,'bbox_center_error_m':bbox_center_error,
 'GIS_to_shell_Hausdorff_m':max(src_to_shell) if src_to_shell else None,
 'shell_to_GIS_Hausdorff_m':max(shell_to_src) if shell_to_src else None,'roof_objects':len(roof)},indent=2))
