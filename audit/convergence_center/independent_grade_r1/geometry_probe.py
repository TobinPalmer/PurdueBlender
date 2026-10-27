import bpy,json,math,hashlib
from pathlib import Path
from collections import Counter
asset=Path(bpy.data.filepath); root=asset.parents[2]; audit=root/'audit'; outdir=audit/'convergence_center'/'independent_grade_r1'; c=bpy.data.collections.get('Asset_convergence_center'); objs=list(c.all_objects)
origin=(-1131.698568664057,-405.52500592356535); sx=111412.84*math.cos(math.radians(40.4274)); sy=111040.0
fc=json.loads((audit/'convergence_gis_feature_946.geojson').read_text(encoding='utf-8-sig'))['features'][0]
ringll=fc['geometry']['coordinates'][0]
ring=[((lon+86.9137)*sx-origin[0],(lat-40.4274)*sy-origin[1]) for lon,lat in ringll]
plate=bpy.data.objects.get('CONV_GIS_ground_plate'); verts=plate.data.vertices; zmin=min(v.co.z for v in verts); bot={i for i,v in enumerate(verts) if abs(v.co.z-zmin)<1e-5}
actual=[(verts[i].co.x,verts[i].co.y) for i in bot]
edges=[((verts[e.vertices[0]].co.x,verts[e.vertices[0]].co.y),(verts[e.vertices[1]].co.x,verts[e.vertices[1]].co.y)) for e in plate.data.edges if e.vertices[0] in bot and e.vertices[1] in bot]
def distseg(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];q=dx*dx+dy*dy;t=0 if not q else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/q));return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
errsrc=max(min(distseg(p,a,b) for a,b in edges) for p in ring[:-1]); errmod=max(min(distseg(p,a,b) for a,b in zip(ring[:-1],ring[1:])) for p in actual)
# Analyze the ground-floor lobby / interior cues by names and bounds.
lobby=[o for o in objs if any(x in o.name.casefold() for x in ('lobby','mezzanine','atrium','reception','screen_wall','lounge'))]
counts=Counter()
for o in objs:
 n=o.name.casefold()
 for k in ('window','mullion','portal','spandrel','sign','lobby','mezzanine','screen_wall','roof','plant'):
  if k in n: counts[k]+=1
# Interior/support objects occupy the ground floor and are distinct from preview collection.
matmissing=[]; external=[]
for mat in bpy.data.materials:
 if not mat.use_nodes or not mat.node_tree: matmissing.append(mat.name); continue
 for node in mat.node_tree.nodes:
  if node.type=='TEX_IMAGE':
   if not node.image: matmissing.append(mat.name+':empty image node')
   elif node.image.filepath and not node.image.packed_file:
    p=bpy.path.abspath(node.image.filepath)
    if not Path(p).exists(): external.append((mat.name,p))
report={'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'collection':c.name,'building_id':c.get('building_id'),'feature_id':c.get('source_feature_id'),'object_count':len(objs),'mesh_count':sum(o.type=='MESH' for o in objs),'ground_plate':plate.name,'source_ring_vertices':len(ring)-1,'asset_footprint_bottom_vertices':len(actual),'asset_bottom_boundary_edges':len(edges),'max_source_to_asset_boundary_deviation_m':errsrc,'max_asset_to_source_boundary_deviation_m':errmod,'lobby_object_count':len(lobby),'lobby_names':[o.name for o in lobby],'feature_object_counts':dict(counts),'missing_texture_nodes':matmissing,'unresolved_external_image_paths':external}
(outdir/'direct_geometry_probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
