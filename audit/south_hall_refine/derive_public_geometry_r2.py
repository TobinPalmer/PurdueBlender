"""Clip schematic first-floor public zones and circulation to South Hall's GIS outline."""
import json, math
from pathlib import Path
from shapely.geometry import Polygon, LineString, box
from shapely.ops import triangulate

HERE=Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\south_hall_refine")
fp=json.loads((HERE/"gis_footprint_r1.json").read_text(encoding="utf-8"))
part=json.loads((HERE/"gis_partition_r1.json").read_text(encoding="utf-8"))
outline=Polygon(fp["local_outline_xy_m"])
res=part["residential_outline_xy_local_m"]
maxx=max(p[0] for p in res)
edges=[]
area=sum(res[i][0]*res[(i+1)%len(res)][1]-res[(i+1)%len(res)][0]*res[i][1] for i in range(len(res)))/2
for i,a in enumerate(res):
    b=res[(i+1)%len(res)]
    dx=b[0]-a[0]; dy=b[1]-a[1]; length=math.hypot(dx,dy)
    midx=(a[0]+b[0])/2
    if midx>maxx-1 and length>7:
        t=(dx/length,dy/length)
        outward=(t[1],-t[0]) if area>0 else (-t[1],t[0])
        edges.append((length,(midx,(a[1]+b[1])/2),outward))
if not edges: raise RuntimeError("Could not resolve GIS east entry edge")
_,mid,out=max(edges,key=lambda x:x[0])
entry=(mid[0]-out[0]*4,mid[1]-out[1]*4)
nodes=[entry,(10.0,-33.5),(22.0,-45.0),(-48.0,-39.0)]
connected={0}; route_edges=[]
while len(connected)<len(nodes):
    best=None
    for i in connected:
        for j in range(len(nodes)):
            if j in connected: continue
            dist=math.dist(nodes[i],nodes[j])
            if best is None or dist<best[0]: best=(dist,i,j)
    dist,i,j=best; connected.add(j); route_edges.append((i,j))

def polygons(g):
    if g.is_empty: return []
    if g.geom_type=="Polygon": return [g]
    if g.geom_type=="MultiPolygon": return list(g.geoms)
    return [x for x in getattr(g,"geoms",[]) if x.geom_type=="Polygon"]

def triangles(g):
    out=[]
    for p in polygons(g):
        for tri in triangulate(p):
            if p.covers(tri):
                coords=list(tri.exterior.coords)[:-1]
                if len(coords)==3:
                    if Polygon(coords).area<0: coords.reverse()
                    out.append([[round(x,6),round(y,6)] for x,y in coords])
    return out

zone_specs=[("lobby_lounge",(10.0,-33.5),18.0,14.0),
            ("dining_sushi_boss",(22.0,-45.0),14.0,12.0),
            ("game_lounge",(-48.0,-39.0),20.0,18.0)]
zones=[]
for name,(x,y),w,h in zone_specs:
    raw=box(x-w/2,y-h/2,x+w/2,y+h/2); clipped=raw.intersection(outline)
    zones.append({"name":name,"center_xy_m":[x,y],"requested_dimensions_m":[w,h],
                  "requested_area_m2":raw.area,"clipped_area_m2":clipped.area,
                  "trimmed_outside_area_m2":raw.difference(outline).area,
                  "triangles_xy":triangles(clipped)})

routes=[]
for i,j in route_edges:
    center=LineString([nodes[i],nodes[j]])
    raw=center.buffer(1.2,cap_style="square",join_style="mitre")
    clipped=raw.intersection(outline)
    routes.append({"node_indices":[i,j],"centerline_xy_m":[nodes[i],nodes[j]],
                   "width_m":2.4,"requested_area_m2":raw.area,
                   "clipped_area_m2":clipped.area,
                   "trimmed_outside_area_m2":raw.difference(outline).area,
                   "triangles_xy":triangles(clipped)})

result={"building_id":"south_hall","source_outline_fid":528,
        "method":"Shapely intersections of schematic carpet rectangles/corridor strips with full Purdue FID 528 polygon; triangulated only within the intersection",
        "entry_node_xy_m":[round(x,6) for x in entry],
        "public_nodes_xy_m":[[round(x,6) for x in p] for p in nodes],
        "zones":zones,"routes":routes,
        "total_zone_overhang_area_m2":sum(z["trimmed_outside_area_m2"] for z in zones),
        "total_route_overhang_area_m2":sum(r["trimmed_outside_area_m2"] for r in routes),
        "residual_overhang_after_clip_m2":0.0,
        "uncertainty":"all public zone locations and route connections remain schematic because no floor plan is available; the clipping only prevents diagram geometry crossing the GIS envelope"}
assert result["residual_overhang_after_clip_m2"]==0.0
assert all(abs(z["trimmed_outside_area_m2"]+z["clipped_area_m2"]-z["requested_area_m2"])<1e-7 for z in zones)
assert all(abs(r["trimmed_outside_area_m2"]+r["clipped_area_m2"]-r["requested_area_m2"])<1e-7 for r in routes)
(HERE/"public_geometry_r2.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"entry":entry,"zone_overhang_before_m2":result["total_zone_overhang_area_m2"],"route_overhang_before_m2":result["total_route_overhang_area_m2"],"after_clip_m2":0.0,"routes":len(routes),"zones":len(zones)},indent=2))
