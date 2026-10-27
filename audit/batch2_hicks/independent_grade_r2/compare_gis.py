import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector
root=Path.cwd(); asset=root/'modular/buildings/hicks_library.blend'; exp='3fc4a157b3ee6ce863edcb74155c1463706f75e7b7fb9170e2849b25cde48cf0'
sha=hashlib.sha256(asset.read_bytes()).hexdigest()
manifest=json.loads((root/'modular/manifest.json').read_text(encoding='utf-8'))
rec=next(a for a in manifest['assets'] if a['id']=='hicks_library')
gis=json.loads((root/'modular/buildings/target_buildings_gis.json').read_text(encoding='utf-8'))['HIKS']['world_polygon']
origin=rec['placement_origin_xy_m']
source=[(p[0]-origin[0],p[1]-origin[1]) for p in gis]
obj=bpy.data.objects.get('HIKS_Exterior_Masonry_Walls')
if obj is None: raise RuntimeError('Main exterior masonry shell mesh missing')
verts=[obj.matrix_world @ v.co for v in obj.data.vertices]
unique_source=source[:-1] if math.dist(source[0],source[-1])<1e-6 else source
nearest=[]
for p in unique_source:
 d=min(math.hypot(v.x-p[0],v.y-p[1]) for v in verts)
 nearest.append(d)
bounds=lambda ps:[[min(p[i] for p in ps),max(p[i] for p in ps)] for i in range(3)]
pts=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
# Compare outer structural edge bounds against exact GIS bounds.
gis_bounds=[[min(p[i] for p in source),max(p[i] for p in source)] for i in range(2)]
mesh_bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(2)]
result={'asset_sha256':sha,'expected_sha256':exp,'sha_match':sha==exp,'source_provider':'Purdue University Campus GIS BuildingShapesZip4','feature_id':197,'source_ring_vertices':len(unique_source),'source_ring_xy_local_m':unique_source,'shell_object':'HIKS_Exterior_Masonry_Walls','shell_object_vertex_count':len(verts),'shell_object_face_count':len(obj.data.polygons),'gis_bounds_local_xy_m':gis_bounds,'shell_bounds_local_xy_m':mesh_bounds,'max_bbox_axis_error_m':max(abs(gis_bounds[i][j]-mesh_bounds[i][j]) for i in range(2) for j in range(2)),'source_point_nearest_mesh_vertex_errors_m':nearest,'max_gis_vertex_error_m':max(nearest),'rms_gis_vertex_error_m':math.sqrt(sum(d*d for d in nearest)/len(nearest)),'asset_origin_xy_m':origin}
out=root/'audit/batch2_hicks/independent_grade_r2/compare_gis.json';out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k not in ['source_ring_xy_local_m','source_point_nearest_mesh_vertex_errors_m']},indent=2))
