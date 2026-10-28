import json, math, os
from PIL import Image,ImageDraw,ImageFont
ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
AUDIT=os.path.join(ROOT,"audit","circle_pines_fid761")
gis=json.load(open(os.path.join(AUDIT,"initial_inspection.json"),encoding="utf-8"))
lay=json.load(open(os.path.join(AUDIT,"schematic_layout.json"),encoding="utf-8"))
pts=gis["gis_ring_xy_local_m"]; xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
W,H=1600,1250; scale=13.; left,top=120,120
font=r"C:\Windows\Fonts\arial.ttf"; bold=r"C:\Windows\Fonts\arialbd.ttf"
def F(s,b=False): return ImageFont.truetype(bold if b else font,s)
def screen(p): return (left+(p[0]-minx)*scale,top+(maxy-p[1])*scale)
im=Image.new("RGB",(W,H),(247,248,250)); d=ImageDraw.Draw(im)
d.text((80,34),"CIRCLE PINES — SCHEMATIC 3D INTERIOR PLAN",font=F(37,True),fill=(25,39,52))
d.text((80,82),"FID 761 GIS outline retained | interior fixtures and partitions are illustrative only",font=F(20),fill=(73,87,101))
palette=[(232,224,202),(213,224,218),(232,213,193)]
for i,poly in enumerate(lay["room_floor_polygons_xy"]): d.polygon([screen(p) for p in poly],fill=palette[i%len(palette)])
for poly in lay["corridor_polygons_xy"]: d.polygon([screen(p) for p in poly],fill=(232,198,126))
for poly in lay["partition_polygons_xy"]: d.polygon([screen(p) for p in poly],fill=(115,126,127),outline=(75,85,88))
theta=math.radians(lay["frame"]["axis_angle_degrees"]); U=(math.cos(theta),math.sin(theta)); V=(-math.sin(theta),math.cos(theta))
for item in lay["furnishings"]:
    cx,cy=item["center_xy"]; du,dv=item["size_uv_m"]
    c=[(cx+U[0]*a+V[0]*b,cy+U[1]*a+V[1]*b) for a,b in [(-du/2,-dv/2),(du/2,-dv/2),(du/2,dv/2),(-du/2,dv/2)]]
    color=(111,74,46) if item["kind"]=="common_table" else (146,107,74) if item["kind"]=="chair" else (203,195,177)
    d.polygon([screen(p) for p in c],fill=color,outline=(60,50,40))
stair=lay.get("stair")
if stair:
    cu,cv=stair["center_uv"]; ox,oy=lay["frame"]["origin_xy_m"]; cx=ox+U[0]*cu+V[0]*cv; cy=oy+U[1]*cu+V[1]*cv
    for i in range(stair["steps"]):
        off=-stair["run_m"]/2+(i+.5)*stair["tread_m"]; px,py=cx+U[0]*off,cy+U[1]*off
        a=stair["width_m"]/2; p1=(px-V[0]*a,py-V[1]*a); p2=(px+V[0]*a,py+V[1]*a)
        d.line((*screen(p1),*screen(p2)),fill=(57,47,38),width=5)
outline=[screen(p) for p in pts]
d.polygon(outline,fill=None,outline=(30,49,60),width=5)
d.line((1270,155,1270,96),fill=(30,45,55),width=4); d.polygon([(1270,83),(1261,102),(1279,102)],fill=(30,45,55)); d.text((1258,58),"N",font=F(19,True),fill=(30,45,55))
d.rounded_rectangle((1040,220,1510,515),radius=14,fill=(255,255,255),outline=(200,210,217),width=2)
d.text((1070,250),"Schematic 3D inserts",font=F(21,True),fill=(32,47,59))
d.text((1070,293),"6 partition strips | clipped to footprint",font=F(18),fill=(53,67,78))
d.text((1070,325),"3 common tables + generic chairs",font=F(18),fill=(53,67,78))
d.text((1070,357),"1 bed-like furnishing block",font=F(18),fill=(53,67,78))
d.text((1070,389),"4 short steps; no destination claimed",font=F(18),fill=(53,67,78))
d.text((1070,435),"NOT an as-built plan",font=F(20,True),fill=(117,66,35))
d.text((1070,466),"No floor plan or interior image found.",font=F(17),fill=(73,87,101))
d.text((80,1110),"Room locations, circulation, stair position, furniture and all facade details remain unverified.",font=F(19,True),fill=(117,66,35))
im.save(os.path.join(AUDIT,"schematic_interior_plan_r2.png"))
print("wrote schematic_interior_plan_r2.png")
