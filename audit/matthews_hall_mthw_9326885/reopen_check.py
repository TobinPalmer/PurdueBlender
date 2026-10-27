"""Reopen-time checks for the assigned Matthews Hall library."""
import json, math
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'matthews_hall_mthw_9326885'
raw=json.loads((AUDIT/'sources'/'feature_235_wgs84.json').read_text(encoding='utf-8'))
feature=raw['features'][0]
ring=feature['geometry']['coordinates'][0]
if ring[0]==ring[-1]: ring=ring[:-1]
expected=[]
for lon,lat in ring:
    expected.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0))
obj=bpy.data.objects['Matthews Hall (MTHW)']
collection=bpy.data.collections['Asset_massing_matthews_hall_mthw_9326885']
world=[]; base=[]
for v in obj.data.vertices:
    p=obj.matrix_world @ v.co
    world.append(tuple(float(x) for x in p))
    if abs(p.z)<1e-5:
        xy=(round(p.x,4),round(p.y,4))
        if xy not in base: base.append(xy)
eq=[(round(x,4),round(y,4)) for x,y in expected]
def directed(a,b):
    return max(min(math.hypot(x-u,y-v) for u,v in b) for x,y in a) if a and b else None
haus=max(directed(eq,base) or 0.0,directed(base,eq) or 0.0)
segments=[]
for poly in obj.data.polygons:
    pts=[obj.matrix_world @ obj.data.vertices[i].co for i in poly.vertices]
    z0=[p for p in pts if abs(p.z)<1e-5]
    if len(z0)==2:
        segments.append(sorted([(round(z0[0].x,4),round(z0[0].y,4)),(round(z0[1].x,4),round(z0[1].y,4))]))
expected_segments=[sorted([eq[i],eq[(i+1)%len(eq)]]) for i in range(len(eq))]
def edge_distance(a,b):
    return min(max(math.dist(a[0],b[0]),math.dist(a[1],b[1])),
               max(math.dist(a[0],b[1]),math.dist(a[1],b[0])))
seg_errors=[]
matched_segments=[]
for expected_edge in expected_segments:
    best=min(segments,key=lambda actual_edge:edge_distance(expected_edge,actual_edge),default=None)
    error=edge_distance(expected_edge,best) if best else float('inf')
    seg_errors.append(error)
    if best is not None and error < 0.002:
        matched_segments.append(best)
seg_ok=len(matched_segments)==len(expected_segments)
wall_vertices=[]
for segment in matched_segments:
    for point in segment:
        if point not in wall_vertices:
            wall_vertices.append(point)
edge_haus=max(seg_errors) if seg_errors else float('inf')
wall_vertex_haus=max(directed(eq,wall_vertices) or 0.0,directed(wall_vertices,eq) or 0.0)
lo=[min(p[i] for p in world) for i in range(3)]; hi=[max(p[i] for p in world) for i in range(3)]
result={
 'saved_asset_reopened': bool(bpy.data.filepath),
 'asset_path':bpy.data.filepath,
 'asset_id':'massing_matthews_hall_mthw_9326885',
 'object_name':obj.name,
 'object_type':obj.type,
 'export_collection':collection.name,
 'collection_object_count':len(collection.objects),
 'mesh_vertices':len(obj.data.vertices),
 'mesh_faces':len(obj.data.polygons),
 'mesh_materials':[m.name for m in obj.data.materials],
 'modifiers':[m.name for m in obj.modifiers],
 'world_bounds_m':{'min':lo,'max':hi},
 'source_ring_vertices':len(eq),
 'all_mesh_vertices_at_grade_including_portico_and_door':len(base),
 'source_wall_edges_match':seg_ok,
 'source_wall_edge_symmetric_hausdorff_m':edge_haus,
 'unique_source_wall_vertices_at_grade':len(wall_vertices),
 'source_wall_vertex_symmetric_hausdorff_m':wall_vertex_haus,
 'external_image_count':len([im for im in bpy.data.images if im.source=='FILE']),
 'placement_transform':'identity; campus coordinates',
}
(AUDIT/'reopen_check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('MTHW_REOPEN_CHECK='+json.dumps(result))

