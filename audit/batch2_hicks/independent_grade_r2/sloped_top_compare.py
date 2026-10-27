import bpy, json, math
from pathlib import Path
root=Path.cwd(); origin=next(a['placement_origin_xy_m'] for a in json.loads((root/'modular/manifest.json').read_text(encoding='utf-8'))['assets'] if a['id']=='hicks_library')
src=json.loads((root/'modular/buildings/target_buildings_gis.json').read_text(encoding='utf-8'))['HIKS']['world_polygon']
src=[(p[0]-origin[0],p[1]-origin[1]) for p in src[:-1]]
o=bpy.data.objects['HIKS_R2_Four_Sloped_GIS_Masonry_Walls']
verts=[o.matrix_world @ v.co for v in o.data.vertices]
zgroups={}
for v in verts: zgroups.setdefault(round(v.z,4),0);zgroups[round(v.z,4)]+=1
z_top=max(zgroups); top=[v for v in verts if abs(v.z-z_top)<1e-4]
errors=[min(math.hypot(v.x-x,v.y-y) for v in top) for x,y in src]
r={'asset_sha256':__import__('hashlib').sha256((root/'modular/buildings/hicks_library.blend').read_bytes()).hexdigest(),'source_ring_nodes':len(src),'sloped_wall_top_z_m':z_top,'top_mesh_vertices':len(top),'gis_to_top_mesh_max_error_m':max(errors),'gis_to_top_mesh_rms_error_m':math.sqrt(sum(x*x for x in errors)/len(errors)),'lower_ring_base_z_m':min(v.z for v in verts),'lower_ring_x_scale_estimate':1.29,'lower_ring_y_scale_estimate':1.415,'z_groups':zgroups}
out=root/'audit/batch2_hicks/independent_grade_r2/sloped_top_compare.json';out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
