import json
from pathlib import Path
from PIL import Image, ImageDraw

refs=json.loads(Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\official_building_references.json").read_text(encoding="utf-8"))
b=next(x for x in refs["buildings"] if x.get("code")=="SH")
pts=b["rings_xy_m"][0]
W,H=1200,900; pad=80
xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
x0,x1=min(xs),max(xs); y0,y1=min(ys),max(ys)
s=min((W-2*pad)/(x1-x0),(H-2*pad)/(y1-y0))
def xy(p): return (round(pad+(p[0]-x0)*s), round(H-pad-(p[1]-y0)*s))
im=Image.new("RGB",(W,H),(249,249,246)); d=ImageDraw.Draw(im)
d.polygon([xy(p) for p in pts],outline=(20,50,100),fill=(210,224,237),width=4)
# Current detailed shell massing footprint (world/local bounds from manifest); dotted rectangle.
for x,y in [(-1148.3,-175.45),(-1035,-175.45),(-1035,-87),(-1148.3,-87)]: pass
asset=[(-1148.3,-175.45),(-1035,-175.45),(-1035,-87),(-1148.3,-87)]
d.line([xy(p) for p in asset]+[xy(asset[0])],fill=(200,40,30),width=4)
d.text((pad,25),"Official SH polygon FID 528 (blue) and current asset envelope AABB (red)",fill=(20,20,20))
origin=(-1091.65,-131.225); centroid=tuple(b["official_polygon_center_xy_m"])
for p,label,color in [(origin,"asset local origin",(200,40,30)),(centroid,"official polygon centroid",(30,120,30))]:
    x,y=xy(p); d.ellipse((x-8,y-8,x+8,y+8),fill=color); d.text((x+12,y-8),label,fill=color)
im.save(r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\south_hall_refine\official_footprint_vs_asset.png")
print("official centroid",centroid,"current origin",origin,"rings",len(pts),"minimum rectangle",b["minimum_rotated_rectangle"])
