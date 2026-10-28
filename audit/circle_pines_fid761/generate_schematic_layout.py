"""Create an explicitly schematic 3D interior layout strictly inside FID 761."""
import json, math, os
from shapely.geometry import Polygon, LineString, box, Point
from shapely.ops import split
from shapely import affinity

ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
AUDIT=os.path.join(ROOT,"audit","circle_pines_fid761")
raw=json.load(open(os.path.join(AUDIT,"initial_inspection.json"),encoding="utf-8"))
points=raw["gis_ring_xy_local_m"]
if points[0]==points[-1]: points=points[:-1]
source_poly=Polygon(points)
if not source_poly.is_valid: source_poly=source_poly.buffer(0)
# The longest edge of the minimum rotated rectangle provides a stable plan axis.
rect=list(source_poly.minimum_rotated_rectangle.exterior.coords)
edges=[(math.hypot(rect[i+1][0]-rect[i][0],rect[i+1][1]-rect[i][1]),rect[i],rect[i+1]) for i in range(4)]
_,a,b=max(edges,key=lambda e:e[0])
theta=math.atan2(b[1]-a[1],b[0]-a[0]); co=math.cos(theta); si=math.sin(theta)
origin=source_poly.centroid
def to_uv(x,y):
    dx=x-origin.x; dy=y-origin.y
    return (co*dx+si*dy,-si*dx+co*dy)
def to_xy(u,v): return (origin.x+co*u-si*v,origin.y+si*u+co*v)
uv=[to_uv(x,y) for x,y in points]
P=Polygon(uv)
if not P.is_valid: P=P.buffer(0)
u0,v0,u1,v1=P.bounds

# Cross partitions create broad generic rooms. Lines are clipped to the source
# footprint, so no schematic interior geometry changes or extends beyond it.
cells=[P]
partition_polys=[]
partition_lines=[]
for frac in (.22,.43,.64,.82):
    u=u0+(u1-u0)*frac
    ln=LineString([(u,v0-2),(u,v1+2)])
    part=ln.intersection(P)
    lines=[]
    if part.geom_type=="LineString": lines=[part]
    elif part.geom_type=="MultiLineString": lines=list(part.geoms)
    else: lines=[g for g in getattr(part,"geoms",[]) if g.geom_type=="LineString"]
    for segment in lines:
        if segment.length<4: continue
        partition_lines.append(list(segment.coords))
        wall=segment.buffer(.075,cap_style="square").intersection(P)
        geoms=[wall] if wall.geom_type=="Polygon" else list(getattr(wall,"geoms",[]))
        for g in geoms:
            if g.geom_type=="Polygon" and g.area>0.03: partition_polys.append(list(g.exterior.coords)[:-1])
        next_cells=[]
        for cell in cells:
            try:
                res=split(cell,segment)
                next_cells.extend([g for g in res.geoms if g.area>10])
            except Exception: next_cells.append(cell)
        if next_cells: cells=next_cells

# Parallel low dividers flank the generic central circulation band, making the
# roof-open volume read as several simple spaces without asserting a real plan.
for v in (-2.8,2.8):
    cut=LineString([(u0-2,v),(u1+2,v)])
    part=cut.intersection(P)
    lines=[]
    if part.geom_type=="LineString": lines=[part]
    elif part.geom_type=="MultiLineString": lines=list(part.geoms)
    else: lines=[g for g in getattr(part,"geoms",[]) if g.geom_type=="LineString"]
    for segment in lines:
        if segment.length<5: continue
        partition_lines.append(list(segment.coords))
        wall=segment.buffer(.075,cap_style="square").intersection(P)
        geoms=[wall] if wall.geom_type=="Polygon" else list(getattr(wall,"geoms",[]))
        for g in geoms:
            if g.geom_type=="Polygon" and g.area>0.03: partition_polys.append(list(g.exterior.coords)[:-1])
        next_cells=[]
        for cell in cells:
            try:
                res=split(cell,segment)
                next_cells.extend([g for g in res.geoms if g.area>8])
            except Exception: next_cells.append(cell)
        if next_cells: cells=next_cells

# A lightly highlighted circulation strip follows the long axis; clip it to the
# footprint and keep it diagrammatic rather than claiming an actual route.
guide=LineString([(u0-2,0),(u1+2,0)]).buffer(1.1,cap_style="flat").intersection(P)
def polygons(g):
    if g.geom_type=="Polygon": return [g]
    return [x for x in getattr(g,"geoms",[]) if x.geom_type=="Polygon"]
corridor_polys=[list(g.exterior.coords)[:-1] for g in polygons(guide) if g.area>1]

# Place a few generic blocks only where their complete rectangles fit in a cell.
furnishings=[]
for cell in sorted(cells,key=lambda c:c.area,reverse=True):
    kind,dims=("common_table",(3.0,1.1)) if cell.area>120 else (("bed_like",(2.0,0.9)) if cell.area>32 else ("seat",(1.3,.75)) if cell.area>15 else (None,None))
    if not kind: continue
    rp=cell.representative_point(); placed=None
    for factor in (1,.85,.7,.55):
        du,dv=dims[0]*factor,dims[1]*factor
        candidate=box(rp.x-du/2,rp.y-dv/2,rp.x+du/2,rp.y+dv/2)
        if cell.covers(candidate):
            placed={"kind":kind,"center_uv":[rp.x,rp.y],"size_uv_m":[du,dv]}; break
    if placed:
        furnishings.append(placed)
        if kind=="common_table":
            for aoff in (-du/2-.36,du/2+.36):
                for boff in (-dv/2-.36,dv/2+.36):
                    cc=(rp.x+aoff,rp.y+boff); chair=box(cc[0]-.22,cc[1]-.22,cc[0]+.22,cc[1]+.22)
                    if cell.covers(chair): furnishings.append({"kind":"chair","center_uv":[cc[0],cc[1]],"size_uv_m":[.44,.44]})
    if len(furnishings)>=20: break

# Three low steps and a small top pad make one generic circulation feature;
# its location and destination are explicitly not based on a surveyed plan.
stair=None
for cell in sorted(cells,key=lambda c:c.area,reverse=True):
    min_u,min_v,max_u,max_v=cell.bounds
    candidates=[cell.representative_point()]
    candidates += [Point(u,v) for u in [min_u+1+i*2 for i in range(max(0,int((max_u-min_u-2)//2)))]
                   for v in [min_v+1+j*2 for j in range(max(0,int((max_v-min_v-2)//2)))] if cell.contains(Point(u,v))]
    placed=False
    for rp in candidates:
        footprint=box(rp.x-1.6,rp.y-.55,rp.x+1.6,rp.y+.55)
        if not cell.covers(footprint): continue
        if any(math.hypot(rp.x-f["center_uv"][0],rp.y-f["center_uv"][1])<4.2 for f in furnishings): continue
        stair={"center_uv":[rp.x,rp.y],"run_m":3.2,"width_m":1.1,"steps":4,"rise_each_m":0.09,"tread_m":0.55}
        placed=True; break
    if placed: break

def worldpoly(poly): return [list(to_xy(u,v)) for u,v in poly]
out={"status":"schematic, not an as-built interior plan","frame":{"origin_xy_m":[origin.x,origin.y],"axis_angle_degrees":math.degrees(theta)},
     "source_footprint_area_local_m2":round(P.area,3),"partition_count":len(partition_polys),
     "partition_polygons_xy":[worldpoly(p) for p in partition_polys],
     "room_floor_polygons_xy":[worldpoly(list(g.exterior.coords)[:-1]) for g in sorted(cells,key=lambda c:c.area,reverse=True)],
     "corridor_polygons_xy":[worldpoly(p) for p in corridor_polys],
     "furnishings":[{**f,"center_xy":list(to_xy(*f["center_uv"]))} for f in furnishings],
     "stair":({**stair,"center_xy":list(to_xy(*stair["center_uv"]))} if stair else None),
     "unverified_detail_note":"Room divisions, circulation, stairs and furniture are generic visual placeholders. No floor plan, interior photo, or entry location is available."}
json.dump(out,open(os.path.join(AUDIT,"schematic_layout.json"),"w",encoding="utf-8"),indent=2)
print(json.dumps({k:v for k,v in out.items() if k not in ("partition_polygons_xy","room_floor_polygons_xy","corridor_polygons_xy")},indent=2))
