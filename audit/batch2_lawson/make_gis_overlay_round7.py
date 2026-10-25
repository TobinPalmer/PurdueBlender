import json
from PIL import Image, ImageDraw

ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap/'
im=Image.open(ROOT+'audit/batch2_lawson/plan.png').convert('RGBA')
d=ImageDraw.Draw(im,'RGBA')
marker=(-282.5,44.0)
gis=json.load(open(ROOT+'modular/buildings/target_buildings_gis.json',encoding='utf8'))['LWSN']['world_polygon']
ring=[(x-marker[0],y-marker[1]) for x,y in gis]
edges=json.load(open(ROOT+'audit/batch2_lawson/r7_shell_edges_round7.json',encoding='utf8'))

# Three independently matched plan/GIS control points define this axis-aligned
# affine raster registration; pixel pick uncertainty is documented in validation.
sx,sy=.092105,.0923377778
x0=-13.209-sx*323
y0=40.611+sy*86
def px(pt): return ((pt[0]-x0)/sx,(y0-pt[1])/sy)
gis_px=[px(p) for p in ring]

for key,color in [('LWSN_Exterior_Brick',(18,75,255,255)),('LWSN_Rotunda_Curtain_Glass',(0,170,210,255))]:
    for edge in edges[key]['edges']: d.line([px(edge[0]),px(edge[1])],fill=color,width=3)

# Draw GIS on top so exact coincidences remain visible as a red/blue centerline pair.
d.line(gis_px+[gis_px[0]],fill=(228,28,34,255),width=2)

for key,detail in edges.items():
    if key=='LWSN_R7_North_GIS_Footprint_Closure': color=(255,145,0,255)
    elif key.startswith('LWSN_R7_Vestibule_'): color=(20,175,70,255)
    else: continue
    for edge in detail['edges']: d.line([px(edge[0]),px(edge[1])],fill=color,width=3)

# Control points: NW, NE, SW exterior corners selected on the PDF raster.
for (x,y),label in zip([(323,86),(627,86),(298,986)],('NW','NE','SW')):
    d.ellipse((x-5,y-5,x+5,y+5),fill=(20,20,20,255),outline=(255,255,255,255),width=1)
    d.text((x+8,y-10),label,fill=(15,15,15,255))

# Compact legend in the open upper-right page margin.
legend=[('GIS FID 59 outline',(228,28,34,255)),('Existing brick baseline',(18,75,255,255)),('Rotunda baseline',(0,170,210,255)),('R7 vestibule wall',(20,175,70,255)),('R7 north closure',(255,145,0,255))]
box=(620,38,895,149)
d.rectangle(box,fill=(255,255,255,230),outline=(45,45,45,230),width=1)
for i,(label,color) in enumerate(legend):
    yy=49+i*19
    d.line([(632,yy+6),(657,yy+6)],fill=color,width=4)
    d.text((665,yy),label,fill=(15,15,15,255))

im.save(ROOT+'audit/batch2_lawson/gis_shell_plan_overlay_round7.png')
print({'output':'audit/batch2_lawson/gis_shell_plan_overlay_round7.png','controls':[323,86,627,86,298,986],'gis_vertices':len(ring),'registration_m_per_pixel':[sx,sy]})
