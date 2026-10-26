"""Render registered GIS/model plan overlay from the reopened asset validation record."""
import json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE=Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\south_hall_refine")
src=json.loads((HERE/"gis_footprint_r1.json").read_text(encoding="utf-8"))
val=json.loads((HERE/"validation_r1.json").read_text(encoding="utf-8"))
g=[tuple(p) for p in src["local_outline_xy_m"][:-1]]
m=[tuple(p) for p in val["footprint_registered_overlay"]["model_boundary_xy_local_m"]]
W,H=1600,1120; im=Image.new("RGB",(W,H),(250,250,248)); d=ImageDraw.Draw(im)
font=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",22)
small=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",16)
left,top,right,bottom=140,110,1460,960
mnx=min(x for x,y in g); mxx=max(x for x,y in g); mny=min(y for x,y in g); mxy=max(y for x,y in g)
scale=min((right-left)/(mxx-mnx),(bottom-top)/(mxy-mny))
cx=(mnx+mxx)/2; cy=(mny+mxy)/2
def pt(p): return (round(W/2+(p[0]-cx)*scale),round(H/2-(p[1]-cy)*scale))
gp=[pt(p) for p in g]; mp=[pt(p) for p in m]
d.polygon(gp,fill=(218,231,243),outline=(25,61,105),width=6)
# Dashed red model perimeter makes its exact overlap with the blue GIS edge visible.
for i,a in enumerate(mp):
    b=mp[(i+1)%len(mp)]; dx=b[0]-a[0]; dy=b[1]-a[1]; length=math.hypot(dx,dy)
    if length==0: continue
    ux,uy=dx/length,dy/length; pos=0.0
    while pos<length:
        end=min(pos+10,length)
        d.line([(a[0]+ux*pos,a[1]+uy*pos),(a[0]+ux*end,a[1]+uy*end)],fill=(202,53,45),width=3)
        pos+=18
origin=pt((0,0)); d.ellipse((origin[0]-8,origin[1]-8,origin[0]+8,origin[1]+8),fill=(24,144,66),outline=(255,255,255),width=2)
d.text((origin[0]+13,origin[1]-26),"asset local origin",font=small,fill=(24,110,51))
d.text((55,28),"South Hall — Purdue GIS outline and reopened Blender footprint",font=font,fill=(22,34,46))
d.text((55,64),"Solid blue: Purdue ArcGIS FID 528  |  dashed red: asset base mesh  |  aligned in project-local metres",font=small,fill=(40,52,65))
# North arrow in map panel.
ax,ay=1510,190; d.line((ax,ay+62,ax,ay),fill=(30,42,53),width=4); d.polygon([(ax,ay-4),(ax-10,ay+18),(ax+10,ay+18)],fill=(30,42,53)); d.text((ax-10,ay-36),"N",font=font,fill=(30,42,53))
# 20 m scale bar.
bar=20*scale; bx,by=left,1015; d.line((bx,by,bx+bar,by),fill=(30,42,53),width=5); d.line((bx,by-9,bx,by+9),fill=(30,42,53),width=3); d.line((bx+bar,by-9,bx+bar,by+9),fill=(30,42,53),width=3); d.text((bx,by+12),"20 m",font=small,fill=(30,42,53))
metrics=val["footprint_registered_overlay"]
d.text((430,1010),f"GIS area {metrics['simplified_area_m2']:.2f} m²  |  mesh plan area {metrics['model_mesh_plan_area_m2']:.2f} m²  |  max vertex mismatch {metrics['max_model_vertex_to_source_vertex_m']:.5f} m",font=small,fill=(40,52,65))
d.text((430,1040),"Same GIS polygon drives the mesh; agreement verifies the build transform, not survey accuracy.",font=small,fill=(90,70,40))
out=HERE/"official_footprint_vs_asset_r1.png"; im.save(out); print(out)
