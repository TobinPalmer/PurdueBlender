import json, math, os
from PIL import Image, ImageDraw, ImageFont

ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
AUDIT=os.path.join(ROOT,"audit","circle_pines_fid761")
data=json.load(open(os.path.join(AUDIT,"initial_inspection.json"),encoding="utf-8"))
pts=data["gis_ring_xy_local_m"][:-1]
xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
minx,maxx=min(xs),max(xs); miny,maxy=min(ys),max(ys)
W,H=1600,1250; scale=13.0; left,top=120,120
font_path=r"C:\Windows\Fonts\arial.ttf"
bold_path=r"C:\Windows\Fonts\arialbd.ttf"
def font(size,bold=False): return ImageFont.truetype(bold_path if bold else font_path,size)
def xy(p): return (left+(p[0]-minx)*scale, top+(maxy-p[1])*scale)
poly=[xy(p) for p in pts]
im=Image.new("RGB",(W,H),(247,248,250)); d=ImageDraw.Draw(im)
d.text((80,35),"CIRCLE PINES — PLAN EVIDENCE",font=font(38,True),fill=(25,39,52))
d.text((80,82),"FID 761 | Purdue GIS EPSG:3857 polygon projected to approximate campus-local meters",font=font(20),fill=(73,87,101))
d.polygon(poly,fill=(220,233,240),outline=(28,91,124),width=5)
# Dashed model footprint on the exact same polygon demonstrates direct vertex use.
for a,b in zip(poly,poly[1:]+poly[:1]):
    dx=b[0]-a[0]; dy=b[1]-a[1]; length=math.hypot(dx,dy); n=max(1,int(length/15))
    for i in range(n):
        if i%2==0:
            t0=i/n; t1=min((i+0.65)/n,1)
            d.line((a[0]+dx*t0,a[1]+dy*t0,a[0]+dx*t1,a[1]+dy*t1),fill=(211,107,49),width=4)
# North arrow
d.line((1250,155,1250,95),fill=(30,45,55),width=4); d.polygon([(1250,83),(1241,101),(1259,101)],fill=(30,45,55)); d.text((1238,58),"N",font=font(19,True),fill=(30,45,55))
d.rounded_rectangle((1040,225,1510,470),radius=14,fill=(255,255,255),outline=(200,210,217),width=2)
d.line((1070,275,1145,275),fill=(28,91,124),width=6); d.text((1160,261),"Purdue GIS footprint",font=font(21),fill=(32,47,59))
d.line((1070,320,1145,320),fill=(211,107,49),width=5); d.text((1160,306),"Modeled wall base",font=font(21),fill=(32,47,59))
d.text((1070,365),"The lines coincide: model uses all 44 unique",font=font(18),fill=(53,67,78))
d.text((1070,392),"source vertices; no rotation or scaling applied.",font=font(18),fill=(53,67,78))
d.text((1070,430),"Approx. bounds: 49.86 × 64.39 m",font=font(19,True),fill=(32,47,59))
d.text((80,1110),"Footprint agreement only. It does not verify height, roof, facade or interior layout.",font=font(22,True),fill=(117,66,35))
im.save(os.path.join(AUDIT,"footprint_overlay.png"))

# A separate roof-off interpretation illustrates empty floor volume and possible
# partitions without presenting a measured or sourced interior plan.
im=Image.new("RGB",(W,H),(247,248,250)); d=ImageDraw.Draw(im)
d.text((80,35),"CIRCLE PINES — SCHEMATIC OPEN-ROOF PLAN",font=font(38,True),fill=(25,39,52))
d.text((80,82),"Interior arrangement is undocumented; lines below are illustrative only",font=font(20),fill=(73,87,101))
d.polygon(poly,fill=(239,237,228),outline=(52,65,72),width=5)
mask=Image.new("L",(W,H),0); ImageDraw.Draw(mask).polygon(poly,fill=255)
parts=Image.new("RGBA",(W,H),(0,0,0,0)); pd=ImageDraw.Draw(parts)
# Generic partition guides are clipped to the GIS footprint, explicitly not a floor plan.
px0,py0=xy((minx,miny)); px1,py1=xy((maxx,maxy))
for frac in [.25,.48,.72]:
    x=left+(maxx-minx)*frac*scale
    pd.line((x,top,x,top+(maxy-miny)*scale),fill=(129,139,140,255),width=5)
for frac in [.30,.62]:
    y=top+(maxy-miny)*frac*scale
    pd.line((left,y,left+(maxx-minx)*scale,y),fill=(129,139,140,255),width=5)
im=Image.composite(Image.alpha_composite(im.convert("RGBA"),parts),im.convert("RGBA"),mask).convert("RGB")
d=ImageDraw.Draw(im)
d.rounded_rectangle((1040,225,1510,490),radius=14,fill=(255,255,255),outline=(200,210,217),width=2)
d.text((1070,260),"GIS-derived wall perimeter",font=font(20,True),fill=(32,47,59))
d.line((1070,315,1140,315),fill=(129,139,140),width=5); d.text((1160,300),"Illustrative partition",font=font(19),fill=(53,67,78))
d.text((1070,365),"No floor plan or interior photo",font=font(19),fill=(53,67,78))
d.text((1070,393),"was available for this building.",font=font(19),fill=(53,67,78))
d.text((1070,445),"Not an as-built representation",font=font(19,True),fill=(117,66,35))
d.text((80,1110),"Interior lines are a diagrammatic example; rooms, circulation and openings remain unverified.",font=font(21,True),fill=(117,66,35))
im.save(os.path.join(AUDIT,"schematic_interior_plan.png"))
print("wrote footprint_overlay.png and schematic_interior_plan.png")
