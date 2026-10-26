"""Cold-reopen check for the MRI1 massing asset; run with Blender background."""
import json, math
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'mri_modular_facility'
ASSET_ID='massing_mri_modular_facility_mri1_a93e22b'
OBJ_NAME='MRI Modular Facility (MRI1)'
COLL_NAME='Asset_'+ASSET_ID
src=json.loads((AUDIT/'sources'/'feature_918_wgs84.geojson').read_text(encoding='utf-8'))
feature=next(f for f in src['features'] if int(f['properties']['FID'])==918)
ring=feature['geometry']['coordinates'][0]
if ring[0]==ring[-1]: ring=ring[:-1]
expected=[((float(lon)+86.9137)*111412.84*math.cos(math.radians(40.4274)),
           (float(lat)-40.4274)*111040.0) for lon,lat in ring]
obj=bpy.data.objects.get(OBJ_NAME); col=bpy.data.collections.get(COLL_NAME)
if obj is None or col is None: raise RuntimeError('Saved MRI1 object/collection missing after cold reopen')
world=[obj.matrix_world@v.co for v in obj.data.vertices]
wall_edges=[]
for poly in obj.data.polygons:
    base=[(float((obj.matrix_world@obj.data.vertices[i].co).x),
           float((obj.matrix_world@obj.data.vertices[i].co).y))
          for i in poly.vertices if abs((obj.matrix_world@obj.data.vertices[i].co).z)<1e-5]
    if len(base)==2: wall_edges.append(base)
def d(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])
def edge_error(a,b):
    return min(max(d(a[0],b[0]),d(a[1],b[1])),max(d(a[0],b[1]),d(a[1],b[0])))
edges=[(expected[i],expected[(i+1)%len(expected)]) for i in range(len(expected))]
errors=[min((edge_error(e,a) for a in wall_edges),default=float('inf')) for e in edges]
lo=[min(float(p[i]) for p in world) for i in range(3)]
hi=[max(float(p[i]) for p in world) for i in range(3)]
external=[im.filepath for im in bpy.data.images if im.source=='FILE']
identity=(list(obj.location)==[0.0,0.0,0.0] and list(obj.rotation_euler)==[0.0,0.0,0.0]
          and list(obj.scale)==[1.0,1.0,1.0])
manifest=json.loads((ROOT/'modular'/'manifest.json').read_text(encoding='utf-8'))
entry=next((a for a in manifest['assets'] if a.get('id')==ASSET_ID),None)
checks={
  'saved_blend_reopened':bool(bpy.data.filepath),
  'asset_path_matches_manifest':entry is not None and entry.get('file')=='buildings/'+ASSET_ID+'.blend',
  'expected_collection_has_one_object':len(col.objects)==1 and col.objects[0]==obj,
  'expected_object_is_mesh':obj.type=='MESH',
  'identity_transform':identity,
  'no_modifiers':len(obj.modifiers)==0,
  'source_outline_has_four_corners':len(expected)==4,
  'all_four_source_edges_match':len(errors)==4 and max(errors)<0.002,
  'portable_no_file_backed_images':len(external)==0,
}
result={
 'blend_path':bpy.data.filepath,'building':'MRI Modular Facility (MRI1 / PMRI)',
 'source':'Purdue BuildingShapesZip4 FeatureServer FID 918; saved WGS84 snapshot',
 'cold_reopen_checks':checks,'pass':all(checks.values()),
 'source_wall_edge_max_error_m':max(errors),
 'matched_source_edges':sum(e<0.002 for e in errors),
 'source_bbox_xy_m':{'min':[min(p[i] for p in expected) for i in range(2)],
                      'max':[max(p[i] for p in expected) for i in range(2)]},
 'model_bounds_xyz_m':{'min':lo,'max':hi},
 'object':OBJ_NAME,'collection':COLL_NAME,'collection_object_count':len(col.objects),
 'object_type':obj.type,'mesh_vertices':len(obj.data.vertices),'mesh_faces':len(obj.data.polygons),
 'modifiers':[m.name for m in obj.modifiers],'external_file_images':external,
 'height_note':'One story supported by official GIS and contractor description; modeled 4.5 m wall/5.85 m equipment top are estimates.'
}
(AUDIT/'reopen_check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('MRI1_REOPEN_CHECK='+json.dumps(result))
if not result['pass']: raise RuntimeError('MRI1 cold-reopen validation failed')
