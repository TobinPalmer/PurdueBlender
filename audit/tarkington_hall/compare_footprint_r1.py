import json,math
from pathlib import Path
from shapely.geometry import Polygon,MultiPoint
from shapely.ops import unary_union
from PIL import Image, ImageDraw, ImageFont
root=Path.cwd(); out=root/'audit'/'tarkington_hall'
feat=json.load(open(out/'gis_feature_662.json',encoding='utf-8'))['feature']
origin=(-591.6124877929688,348.0)
lon0=-86.9137; lat0=40.4274
xscale=111412.84*math.cos(math.radians(lat0)); yscale=111040.0
rings=feat['geometry']['rings']
source_rings=[]
for ring in rings:
 source_rings.append([((lon-lon0)*xscale-origin[0],(lat-lat0)*yscale-origin[1]) for lon,lat in ring])
gis=Polygon(source_rings[0],source_rings[1:])
vert_data=json.load(open(out/'shell_vertices_r1.json',encoding='utf-8'))
parts=[]
for rec in vert_data['objects']:
 p=MultiPoint(rec['vertices_xy']).convex_hull
 if p.geom_type=='Polygon' and p.area>0:parts.append((rec['name'],p))
model=unary_union([p for _,p in parts])
intersection=gis.intersection(model).area
union=gis.union(model).area
iou=intersection/union if union else 0
bd=gis.boundary.hausdorff_distance(model.boundary)
# symmetric sampled boundary residual using vertices plus 10 cm densification
# Hausdorff values are also recorded; nearest-boundary residuals need denser samples.
def samples(line,step=.25):
 pts=[]
 for ls in (line.geoms if hasattr(line,'geoms') else [line]):
  length=ls.length;n=max(1,int(math.ceil(length/step)))
  pts.extend([ls.interpolate(i/n,normalized=True) for i in range(n+1)])
 return pts
sg=samples(gis.boundary); mg=samples(model.boundary)
s_to_m=[p.distance(model.boundary) for p in sg];m_to_s=[p.distance(gis.boundary) for p in mg]
metrics={'building':'Tarkington Hall','feature_id':feat['attributes']['FID'],'building_code':feat['attributes']['BLDG_ABBR'],'model_asset':'modular/buildings/tarkington_hall.blend','model_shell_objects':[n for n,_ in parts],'source_crs':'EPSG:4326','project_conversion':'X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040.0','model_local_origin_world_m':list(origin),'measurement_method':'Source GIS outline transformed into project-local meters; model structural-shell object vertices transformed through saved object matrices; each selected shell object convex-hulled in XY and unioned. Decoration, windows, paths, and landscaping excluded by the existing master audit shell selection.','source_polygon_area_m2':gis.area,'model_shell_union_area_m2':model.area,'intersection_area_m2':intersection,'union_area_m2':union,'polygon_iou':iou,'symmetric_sampled_boundary_mean_m':(sum(s_to_m)+sum(m_to_s))/(len(s_to_m)+len(m_to_s)),'symmetric_sampled_boundary_p95_m':sorted(s_to_m+m_to_s)[int(.95*(len(s_to_m)+len(m_to_s))-1)],'symmetric_boundary_hausdorff_m':bd,'source_centroid_local_xy_m':[gis.centroid.x,gis.centroid.y],'model_centroid_local_xy_m':[model.centroid.x,model.centroid.y],'centroid_delta_m':[model.centroid.x-gis.centroid.x,model.centroid.y-gis.centroid.y],'source_bounds_local_m':[[gis.bounds[0],gis.bounds[2]],[gis.bounds[1],gis.bounds[3]]],'model_bounds_local_m':[[model.bounds[0],model.bounds[2]],[model.bounds[1],model.bounds[3]]],'limitations':['The Purdue map polygon is not documented as surveyed wall faces.','The convex hull of each selected structural shell object can bridge local setbacks and openings.','The model shell selection follows the existing audit list, which is named and repeatable but not a surveyed wall classification.','The project coordinate transform is a local approximation, not a projected survey CRS.']}
json.dump(metrics,open(out/'footprint_comparison_r1.json','w',encoding='utf-8'),indent=2)
# Draw an auditable top-down overlay without an additional plotting dependency.
W,H=1400,1100
all_bounds=gis.union(model).bounds
minx,miny,maxx,maxy=all_bounds
pad=max((maxx-minx)*.06,2.0); minx-=pad;maxx+=pad;miny-=pad;maxy+=pad
scale=min((W-140)/(maxx-minx),(H-180)/(maxy-miny))
def pix(pt): return (int(70+(pt[0]-minx)*scale),int(H-90-(pt[1]-miny)*scale))
img=Image.new('RGB',(W,H),(248,249,251));d=ImageDraw.Draw(img,'RGBA')
# light grid every 10 m
for x in range(math.floor(minx/10)*10,math.ceil(maxx/10)*10+1,10):
 px=pix((x,miny))[0];d.line((px,45,px,H-70),fill=(120,130,140,35),width=1)
for y in range(math.floor(miny/10)*10,math.ceil(maxy/10)*10+1,10):
 py=pix((minx,y))[1];d.line((60,py,W-50,py),fill=(120,130,140,35),width=1)
def draw_poly(poly,fill,outline,width):
 pts=[pix(q) for q in list(poly.exterior.coords)]
 d.polygon(pts,fill=fill)
 d.line(pts,fill=outline,width=width,joint='curve')
 for ring in poly.interiors:
  pts2=[pix(q) for q in list(ring.coords)]; d.polygon(pts2,fill=(248,249,251,255));d.line(pts2,fill=outline,width=width)
# red source fill, blue model outline
draw_poly(gis,(229,73,73,55),(178,45,61,255),4)
for poly in model.geoms if hasattr(model,'geoms') else [model]:
 pts=[pix(q) for q in list(poly.exterior.coords)];d.line(pts,fill=(23,110,171,255),width=4,joint='curve')
# labels and title
try: font=ImageFont.truetype('arial.ttf',26);small=ImageFont.truetype('arial.ttf',19)
except: font=small=ImageFont.load_default()
d.text((70,22),'Tarkington Hall GIS Footprint vs Structural Shell',font=font,fill=(25,35,45,255))
d.text((70,58),f'IoU {iou:.3f}   |   mean symmetric boundary residual {metrics["symmetric_sampled_boundary_mean_m"]:.2f} m   |   FID 662',font=small,fill=(45,55,65,255))
y0=H-55;d.line((70,y0,W-70,y0),fill=(178,45,61,255),width=5);d.text((85,y0-14),'Purdue GIS',font=small,fill=(45,55,65,255));d.line((240,y0,W-70,y0),fill=(23,110,171,255),width=5);d.text((255,y0-14),'Model shell union',font=small,fill=(45,55,65,255))
img.save(out/'footprint_overlay_r1.png')
print(json.dumps({k:metrics[k] for k in ['source_polygon_area_m2','model_shell_union_area_m2','polygon_iou','symmetric_sampled_boundary_mean_m','symmetric_sampled_boundary_p95_m','symmetric_boundary_hausdorff_m','centroid_delta_m','source_bounds_local_m','model_bounds_local_m']},indent=2))
