import json
from PIL import Image,ImageDraw
root=r'C:/Users/Tobin/Documents/Blender/PurdueMap/'
im=Image.open(root+'audit/batch2_lawson/plan.png').convert('RGBA'); d=ImageDraw.Draw(im,'RGBA')
g=json.load(open(root+'modular/buildings/target_buildings_gis.json'))['LWSN']
# Independently fit page axes from matched corners: plan top-left (323,86) to GIS (-13.209,40.611),
# top-right (627,86) to GIS (14.791,40.547), south-west (298,986) to GIS (-15.553,-42.493).
sx=0.092105; x0=-13.209-sx*323
sy=(40.611-(-42.493))/(986-86); y0=40.611+sy*86
pts=[]
for X,Y in g['world_polygon']:
 x=X+282.5;y=Y-44.0
 pts.append(((x-x0)/sx,(y0-y)/sy))
d.line(pts+[pts[0]],fill=(240,25,20,255),width=3)
for x,y in pts[::5]:d.ellipse((x-3,y-3,x+3,y+3),fill=(240,25,20,255))
im.save(root+'audit/batch2_lawson/gis_plan_overlay_registered_r7.png')
print({'scale_x_m_per_px':sx,'scale_y_m_per_px':sy,'origin_x_m':x0,'origin_y_m':y0,'controls':[(323,86), (627,86), (298,986)]})
