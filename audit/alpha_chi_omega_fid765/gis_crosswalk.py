import json,math
from PIL import Image,ImageDraw
from shapely.geometry import Polygon,LineString,box
from shapely.ops import nearest_points
D='audit/alpha_chi_omega_fid765';feature=json.load(open(D+'/sources/fid765_arcgis_4326.json'))['features'][0];lat0,lon0=40.4274,-86.9137
xy=lambda lon,lat: ((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0)
gring=feature['geometry']['rings'][0];gp=[xy(lon,lat) for lon,lat in gring];g=Polygon(gp);cand=json.load(open(D+'/source_massing_footprint_xy.json'));m=Polygon(cand)
osm=json.load(open('purdue_roads.json'));nodes={e['id']:(e['lon'],e['lat']) for e in osm['elements'] if e.get('type')=='node'};roads=[]
center=g.centroid;crop=box(center.x-100,center.y-100,center.x+100,center.y+100)
for e in osm['elements']:
 if e.get('type')!='way' or 'highway' not in e.get('tags',{}):continue
 pts=[xy(*nodes[n]) for n in e.get('nodes',[]) if n in nodes]
 if len(pts)<2:continue
 line=LineString(pts)
 if line.distance(g)<100:
  seg=line.intersection(crop)
  if not seg.is_empty:roads.append((e,seg))
coords=[*gp,*cand]
for e,seg in roads:
 geoms=list(seg.geoms) if hasattr(seg,'geoms') else [seg]
 coords.extend(p for geom in geoms for p in geom.coords)
xmin=center.x-75;xmax=center.x+75;ymin=center.y-75;ymax=center.y+75
W,H=1000,900;pad=90;scale=min((W-2*pad)/(xmax-xmin),(H-2*pad)/(ymax-ymin));px=lambda p:(int(pad+(p[0]-xmin)*scale),int(H-pad-(p[1]-ymin)*scale))
im=Image.new('RGB',(W,H),'white');dr=ImageDraw.Draw(im)
for e,seg in roads:
 geoms=list(seg.geoms) if hasattr(seg,'geoms') else [seg]
 for geom in geoms:
  pts=[px(p) for p in geom.coords]
  if len(pts)>1:dr.line(pts,fill=(110,110,110),width=3)
  name=e.get('tags',{}).get('name')
  if name and len(pts)>1:dr.text(pts[len(pts)//2],name,fill=(40,40,40))
dr.polygon([px(p) for p in gp],fill=(231,140,120),outline=(160,50,40),width=4);dr.line([px(p) for p in cand+[cand[0]]],fill=(30,90,170),width=4)
p=px((center.x,center.y));dr.ellipse([p[0]-5,p[1]-5,p[0]+5,p[1]+5],fill='black')
dr.text((50,20),'Alpha Chi Omega (FID 765): local footprint / access context',fill='black');dr.text((50,45),'North is up. Gray is OpenStreetMap roads/paths from existing project snapshot.',fill=(50,50,50));dr.text((50,H-55),'Red: Purdue GIS FID 765   Blue: source massing   Black: GIS centroid',fill='black');dr.line([(W-70,95),(W-70,55)],fill='black',width=3);dr.polygon([(W-70,45),(W-78,62),(W-62,62)],fill='black');dr.text((W-80,100),'N',fill='black');im.save(D+'/fid765_footprint_overlay.png')
