from pathlib import Path
import json, math, hashlib
import bpy

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BUILDING='bindley_bioscience_center'
ASSET=ROOT/'modular/buildings'/f'{BUILDING}.blend'
EVIDENCE=ROOT/'audit'/BUILDING/'evidence.json'
GIS=ROOT/'audit'/BUILDING/'sources/gis_feature_605.json'
MANIFEST=ROOT/'modular/manifest.json'
EXPORT=HERE/'collection_export_probe.blend'
OUT=HERE/'blender_probe.json'
EXPECTED=f'Asset_{BUILDING}'

def polygon_centroid(points):
    cross=[]
    for (x0,y0),(x1,y1) in zip(points, points[1:]+points[:1]):
        cross.append(x0*y1-x1*y0)
    area2=sum(cross)
    if abs(area2)<1e-10: raise ValueError('degenerate GIS ring')
    cx=sum((p[0]+q[0])*c for p,q,c in zip(points,points[1:]+points[:1],cross))/(3*area2)
    cy=sum((p[1]+q[1])*c for p,q,c in zip(points,points[1:]+points[:1],cross))/(3*area2)
    return [cx,cy]

def bounds(points):
    return [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]

def hausdorff(a,b):
    directed=lambda p,q:max(min(math.dist(x,y) for y in q) for x in p)
    return {'source_to_shell_m':directed(a,b),'shell_to_source_m':directed(b,a),
            'max_symmetric_m':max(directed(a,b),directed(b,a))}

def unique_ring(raw):
    pts=[(float(p[0]),float(p[1])) for p in raw]
    if len(pts)>1 and math.dist(pts[0],pts[-1])<1e-10: pts=pts[:-1]
    return pts

def project_lonlat(ring):
    lat0=40.4274
    factor=111412.84*math.cos(math.radians(lat0))
    return [( (lon+86.9137)*factor, (lat-lat0)*111040.0 ) for lon,lat in ring]

manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
entry=next(x for x in manifest['assets'] if x['id']==BUILDING)
source=json.loads(GIS.read_text(encoding='utf-8'))
raw=unique_ring(source['feature']['geometry']['rings'][0])
projected=project_lonlat(raw)
centroid=polygon_centroid(projected)
local_source=[(x-centroid[0],y-centroid[1]) for x,y in projected]
origin=entry['placement_origin_xy_m']

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections.get(EXPECTED)
assert asset is not None, f'missing collection {EXPECTED}'
objects=sorted(set(asset.all_objects),key=lambda o:o.name)
object_names=[o.name for o in objects]
mesh_objects=[o for o in objects if o.type=='MESH']
assert len(raw)==191 and len(local_source)==191, f'GIS ring count changed: {len(raw)}'
assert len(mesh_objects)>=500
shell=bpy.data.objects.get('BIND_GIS_primary_shell')
assert shell is not None and shell.type=='MESH'

depsgraph=bpy.context.evaluated_depsgraph_get()
evaluated=shell.evaluated_get(depsgraph)
mesh=evaluated.to_mesh()
verts=[evaluated.matrix_world @ v.co for v in mesh.vertices]
evaluated.to_mesh_clear()
shell_bounds=bounds([(float(p.x),float(p.y),float(p.z)) for p in verts])
zmin=shell_bounds[2][0]
base=[(float(p.x),float(p.y)) for p in verts if abs(float(p.z)-zmin)<1e-5]
top=[(float(p.x),float(p.y)) for p in verts if abs(float(p.z)-shell_bounds[2][1])<1e-5]
# The shell is an extrusion of one GIS ring, with one base and one top vertex per source point.
assert len(base)==191 and len(top)==191,(len(base),len(top))
footprint_error=hausdorff(local_source,base)
max_axis_bounds_delta=max(abs(shell_bounds[a][i]-[[min(p[0] for p in local_source),max(p[0] for p in local_source)],[min(p[1] for p in local_source),max(p[1] for p in local_source)]][a][i]) for a in (0,1) for i in (0,1))
origin_delta=[origin[i]-centroid[i] for i in range(2)]
local_centroid=[sum(p[i] for p in base)/len(base) for i in range(2)]
project_xy=project_lonlat(raw)
world_source=[(x,y) for x,y in project_xy]
world_shell=[(x+origin[0],y+origin[1]) for x,y in base]
world_error=hausdorff(world_source,world_shell)

# Evaluate the complete asset envelope, including the roof, canopy, and text details.
all_points=[]
object_z_tops=[]
for obj in objects:
    if obj.type=='MESH':
        evaluated_obj=obj.evaluated_get(depsgraph)
        evaluated_mesh=evaluated_obj.to_mesh()
        points=[evaluated_obj.matrix_world @ v.co for v in evaluated_mesh.vertices]
        evaluated_obj.to_mesh_clear()
    elif obj.bound_box:
        points=[obj.matrix_world @ __import__('mathutils').Vector(corner) for corner in obj.bound_box]
    else:
        points=[]
    all_points.extend(points)
    if points: object_z_tops.append({'name':obj.name,'max_z_m':max(float(p.z) for p in points)})
overall_bounds=bounds([(float(p.x),float(p.y),float(p.z)) for p in all_points])
object_z_tops.sort(key=lambda d:d['max_z_m'],reverse=True)

external_images=[]
for image in bpy.data.images:
    if image.source=='FILE' and image.filepath and not image.packed_file:
        external_images.append({'name':image.name,'filepath':image.filepath})
libraries=[lib.filepath for lib in bpy.data.libraries]
absolute_libraries=[p for p in libraries if bpy.path.abspath(p).startswith('\\\\') or (len(p)>2 and p[1:3]==':\\')]
nonidentity=[{'name':o.name,'location':[float(v) for v in o.location]} for o in objects if max(abs(float(v)) for v in o.location)>1e-6 and o.type!='FONT']
preview_rig_present=bpy.data.collections.get('Preview_Rig_not_for_export') is not None

actual_count=len(objects)
manifest_names=entry.get('objects',[])
manifest_missing=sorted(set(manifest_names)-set(object_names))
manifest_unlisted=sorted(set(object_names)-set(manifest_names))

# Write and reopen a collection-only library to test the actual handoff contract.
bpy.data.libraries.write(str(EXPORT),{asset},path_remap='RELATIVE_ALL',fake_user=True)
bpy.ops.wm.open_mainfile(filepath=str(EXPORT))
exported=bpy.data.collections.get(EXPECTED)
assert exported is not None, 'exported collection failed to reopen'
export_objects=sorted(set(exported.all_objects),key=lambda o:o.name)
export_count=len(export_objects)
export_camera_lights=[o.name for o in export_objects if o.type in {'CAMERA','LIGHT'}]
export_links=[lib.filepath for lib in bpy.data.libraries]
assert export_count==actual_count, (export_count,actual_count)
assert not export_camera_lights

report={
 'asset_file':ASSET.relative_to(ROOT).as_posix(),
 'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),
 'reopened_scene':'Scene',
 'expected_collection':EXPECTED,
 'collection_reopened':True,
 'collection_object_count':actual_count,
 'collection_object_names':object_names,
 'mesh_object_count':len(mesh_objects),
 'manifest_object_count':entry.get('object_count'),
 'manifest_name_count':len(manifest_names),
 'manifest_names_match':set(object_names)==set(manifest_names),
 'manifest_names_missing_from_asset':manifest_missing,
 'asset_names_missing_from_manifest':manifest_unlisted,
 'gis_feature_id':source['feature']['attributes'].get('FID'),
 'gis_ring_vertex_count':len(raw),
 'shell_vertex_count':len(verts),
 'shell_base_vertex_count':len(base),
 'shell_bounds_local_m':[[round(v,6) for v in a] for a in shell_bounds],
 'overall_asset_bounds_local_m':[[round(v,6) for v in a] for a in overall_bounds],
 'highest_asset_objects':object_z_tops[:8],
 'gis_local_bounds_m':[[round(min(p[i] for p in local_source),6),round(max(p[i] for p in local_source),6)] for i in range(2)],
 'footprint_hausdorff_m':footprint_error,
 'max_xy_bounds_delta_m':max_axis_bounds_delta,
 'gis_polygon_centroid_project_m':centroid,
 'manifest_placement_origin_xy_m':origin,
 'placement_origin_residual_m':origin_delta,
 'shell_base_vertex_mean_local_xy_m':local_centroid,
 'placed_world_footprint_hausdorff_m':world_error,
 'gis_attributes':{k:source['feature']['attributes'].get(k) for k in ['NUM_LEVELS','CountOfFLO','Extrution','Elevation','R','F01','F02','F03']},
 'external_unpacked_images':external_images,
 'linked_library_paths':libraries,
 'absolute_library_paths':absolute_libraries,
 'preview_rig_in_source_asset':preview_rig_present,
  'collection_export_probe':EXPORT.relative_to(ROOT).as_posix(),
 'export_reopened':True,
 'export_collection_object_count':export_count,
 'export_camera_or_light_objects':export_camera_lights,
 'export_linked_libraries':export_links,
 'preview_files':[
   'audit/bindley_bioscience_center/overview.png',
   'audit/bindley_bioscience_center/entry_detail.png',
   'audit/bindley_bioscience_center/plan.png'
 ]
}
OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in {'collection_object_names','manifest_names_missing_from_asset','asset_names_missing_from_manifest','collection_objects_with_nonzero_local_location_sample','highest_asset_objects'}},indent=2))
