import json
from pathlib import Path
from shapely.geometry import Polygon,box
from PIL import Image,ImageDraw,ImageFont
h=Path('audit/stewart_center_independent_grade')
p=json.loads((h/'purdue_gis_feature_615.json').read_text())['features'][0]['geometry']['rings'][0]
lat0,lon0=40.4274,-86.9137; mx,my=84810.60416539927,111040.; ox,oy=91.04999828338623,-253.375
ring=[((x-lon0)*mx-ox,(y-lat0)*my-oy) for x,y in p]; source=Polygon(ring)
report=json.loads((h/'building_validation.json').read_text())
W,H=1500,1080; im=Image.new('RGB',(W,H),(250,249,246)); d=ImageDraw.Draw(im)
try: f=ImageFont.truetype('arial.ttf',20); fb=ImageFont.truetype('arial.ttf',23)
except: f=fb=ImageFont.load_default()
xmin,xmax=-82,72; ymin,ymax=-57,49; pad=90
scale=min((W-2*pad)/(xmax-xmin),(H-2*pad)/(ymax-ymin))
def xy(p): return (int(pad+(p[0]-xmin)*scale),int(H-pad-(p[1]-ymin)*scale))
colors={'Loeb theater':(196,107,70),'HSSE library':(63,134,189),'Ringel Gallery':(114,164,93)}
poly=[xy(q) for q in ring]; d.polygon(poly,fill=(229,220,201),outline=(176,32,37),width=5)
for name,rec in report['interior_module_bounds'].items():
 b=rec['local_bounds_m']; r=box(b[0][0],b[1][0],b[0][1],b[1][1]); inside=source.covers(r); rec['gis_footprint_covers_module_bbox']=inside; rec['bbox_intersection_ratio']=round(r.intersection(source).area/r.area,4)
 x0,y0=xy((b[0][0],b[1][1])); x1,y1=xy((b[0][1],b[1][0])); c=colors[name]; d.rectangle((x0,y0,x1,y1),fill=(*c,180),outline=c,width=4)
 center=xy((r.centroid.x,r.centroid.y)); d.text((center[0],center[1]),name,font=f,fill=c,anchor='mm',stroke_width=2,stroke_fill=(255,255,255))
# axis grid labels
for x in range(-80,71,20):
 px=xy((x,ymin))[0]; d.line((px,pad,px,H-pad),fill=(225,225,225),width=1); d.text((px,H-pad+20),str(x),font=f,fill=(50,50,50),anchor='mm')
for y in range(-50,41,20):
 py=xy((xmin,y))[1]; d.line((pad,py,W-pad,py),fill=(225,225,225),width=1); d.text((pad-30,py),str(y),font=f,fill=(50,50,50),anchor='mm')
d.text((W/2,35),'Stewart Center: GIS structural trace and retained interior modules',font=fb,fill=(25,25,25),anchor='mm')
d.text((W/2,H-24),'Local X east / Y north, meters — module boxes are model bounds; floor plan is schematic',font=f,fill=(45,45,45),anchor='mm')
# compact legend
lx,ly=105,108
for label,c in [('Purdue GIS OBJECTID 615',(176,32,37)),*[(n,colors[n]) for n in colors]]:
 d.line((lx,ly,lx+38,ly),fill=c,width=6); d.text((lx+50,ly),label,font=f,fill=(35,35,35),anchor='lm'); ly+=32
im.save(h/'footprint_overlay.png')
(h/'building_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:{'contained':v['gis_footprint_covers_module_bbox'],'bbox_overlap':v['bbox_intersection_ratio']} for k,v in report['interior_module_bounds'].items()},indent=2))
