import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=Path.cwd()
feature=json.loads((root/'audit/veterinary_medicine_isolation_facility/purdue_gis_VMIF_feature.json').read_text(encoding='utf-8'))
evidence=json.loads((root/'audit/veterinary_medicine_isolation_facility/evidence.json').read_text(encoding='utf-8'))
ring=feature['geometry']['rings'][0][:-1]
lat0,lon0=40.4274,-86.9137
sx=111412.84*math.cos(math.radians(lat0)); sy=111040.0
pts=[Vector(((lon-lon0)*sx,(lat-lat0)*sy,0)) for lon,lat in ring]
# Source polygon shoelace area/centroid in project tangent plane.
twice=0.0; cx=0.0; cy=0.0
for i,a in enumerate(pts):
 b=pts[(i+1)%len(pts)]; cross=a.x*b.y-b.x*a.y
 twice+=cross; cx+=(a.x+b.x)*cross; cy+=(a.y+b.y)*cross
signed_area=twice/2
centroid=Vector((cx/(6*signed_area),cy/(6*signed_area)))
anchor=Vector(evidence['anchor_campus_xy_m'])
local=[Vector((p.x-anchor.x,p.y-anchor.y,0)) for p in pts]
col=bpy.data.collections.get('Asset_massing_veterinary_medicine_isolation_facility_66d1305')
shell=next((o for o in col.all_objects if o.name=='GIS footprint exterior wall shell with west service opening'),None)
sv=[shell.matrix_world @ v.co for v in shell.data.vertices] if shell else []
err=[min((p-v).length for v in sv) for p in local]
shell_bounds=[[min(v[i] for v in sv),max(v[i] for v in sv)] for i in (0,1)]
expected_bounds=[[min(p[i] for p in local),max(p[i] for p in local)] for i in (0,1)]
shape_area=float(feature['attributes']['Shape__Area'])
result={
 'source_fid':feature['attributes']['FID'],'source_name':feature['attributes']['BUILDING_N'],'ring_vertex_count':len(ring),
 'ring_area_projected_m2':abs(signed_area),'shape_area_attribute_m2':shape_area,'area_difference_m2':shape_area-abs(signed_area),'area_difference_percent_of_ring':100*(shape_area-abs(signed_area))/abs(signed_area),
 'polygon_centroid_projected_xy_m':[centroid.x,centroid.y],'asset_anchor_xy_m':list(anchor),'anchor_centroid_error_m':(centroid-anchor).length,
 'ring_vertex_max_distance_to_shell_mesh_m':max(err),'ring_vertex_distances_m':err,
 'source_ring_bounds_local_xy_m':expected_bounds,'shell_bounds_local_xy_m':shell_bounds,
 'dimensions_local_xy_m':[expected_bounds[0][1]-expected_bounds[0][0],expected_bounds[1][1]-expected_bounds[1][0]],
 'method':'Projected official GIS ring using the documented local tangent approximation, subtracted the saved area-centroid anchor, then compared each source corner to the fresh-open saved exterior wall shell vertex set.'
}
out=root/'audit/veterinary_medicine_isolation_facility/independent_grade_r2/gis_comparison.json'
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
