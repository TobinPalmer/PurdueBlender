import json
from PIL import Image,ImageDraw
p='audit/batch2_lawson/plan.png'; im=Image.open(p).convert('RGBA'); draw=ImageDraw.Draw(im,'RGBA')
g=json.load(open('modular/buildings/target_buildings_gis.json'))['LWSN']; marker=(-282.5,44.0)
pts=[]
for x,y in g['world_polygon']:
 lx=x-marker[0];ly=y-marker[1]
 # existing plan registration used by the first-floor detail trace
 px=327+(lx+15.55)/.0944;py=88+(42.27-ly)/.0944;pts.append((px,py))
draw.line(pts,fill=(235,20,30,255),width=3)
for x,y in pts[::5]:draw.ellipse((x-3,y-3,x+3,y+3),fill=(235,20,30,255))
im.save('audit/batch2_lawson/gis_plan_overlay_current_r7.png')
