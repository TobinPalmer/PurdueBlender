from pathlib import Path
import json, math, urllib.parse, urllib.request
from io import BytesIO
from PIL import Image, ImageDraw
AUDIT=Path(__file__).resolve().parent
BASE='https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0'
IMG='https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer'
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'PurdueMap building accuracy audit/1.0'})
 with urllib.request.urlopen(req,timeout=90) as r:return r.read()
meta=json.loads(fetch(BASE+'?f=json'))
(AUDIT/'purdue_campus_building_layer_metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
query=BASE+'/query?'+urllib.parse.urlencode({'where':'OBJECTID = 315','outFields':'*','outSR':'4326','returnGeometry':'true','f':'json'})
raw=fetch(query); (AUDIT/'purdue_crec_feature_315.json').write_bytes(raw)
data=json.loads(raw); feat=data['features'][0]; geom=feat['geometry']; rings=geom['rings']
lat0=40.4274; lon0=-86.9137
ring_ll=rings[0]
# Project-local conversion defined by this project, EPSG:4326 to local meter approximation.
xy=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0) for lon,lat in ring_ll]
ring_xy=[(x,y) for x,y in xy]
area=abs(sum(ring_xy[i][0]*ring_xy[(i+1)%len(ring_xy)][1]-ring_xy[(i+1)%len(ring_xy)][0]*ring_xy[i][1] for i in range(len(ring_xy)-1)))/2
bounds=[[min(x for x,y in xy),max(x for x,y in xy)],[min(y for x,y in xy),max(y for x,y in xy)]]
# Current imagery extent in Web Mercator; pad 35 m for immediate site context.
def webmerc(lon,lat):
 x=lon*20037508.342789244/180
 lat=max(-85.05112878,min(85.05112878,lat)); y=math.log(math.tan((90+lat)*math.pi/360))/(math.pi/180)*20037508.342789244/180
 return x,y
merc=[webmerc(lon,lat) for lon,lat in ring_ll]; pad=45
bbox=[min(x for x,y in merc)-pad,min(y for x,y in merc)-pad,max(x for x,y in merc)+pad,max(y for x,y in merc)+pad]
w,h=2048,2048
url=IMG+'/exportImage?'+urllib.parse.urlencode({'bbox':','.join(f'{v:.3f}' for v in bbox),'bboxSR':'3857','imageSR':'3857','size':f'{w},{h}','format':'jpg','f':'image','interpolation':'RSP_BilinearInterpolation'})
img=Image.open(BytesIO(fetch(url))).convert('RGB'); img.save(AUDIT/'indiana_current_orthophoto.jpg',quality=94)
draw=ImageDraw.Draw(img); pts=[((x-bbox[0])/(bbox[2]-bbox[0])*w,(bbox[3]-y)/(bbox[3]-bbox[1])*h) for x,y in merc]
draw.line(pts+[pts[0]],fill=(255,40,40),width=5)
img.save(AUDIT/'indiana_current_orthophoto_gis_overlay.jpg',quality=94)
(AUDIT/'orthophoto_request.json').write_text(json.dumps({'url':url,'service':IMG,'provider':'Indiana Geographic Information Office','retrieval_date':'2026-10-24','source_date':'Current imagery service; returned scene date not yet identified','crs':'EPSG:3857','bbox':bbox,'size_px':[w,h],'feature_id':315},indent=2)+'\n',encoding='utf-8')
# Download source page image from Architect Magazine, retain only as view reference (not packed texture).
photo_url='https://cdnassets.hw.net/ab/fc/8cbabafd4274b1d523c2a35cb18f/eastentry-hero.jpg'
try:
 b=fetch(photo_url); (AUDIT/'architect_east_entry_reference.jpg').write_bytes(b)
except Exception as e: print('Architect image fetch warning:',repr(e))
try:
 api='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({'action':'query','titles':'File:France A Córdova Recreational Sports Center Purdue University 2016 01.jpg','prop':'imageinfo','iiprop':'url|extmetadata','format':'json'})
 d=json.loads(fetch(api)); page=next(iter(d['query']['pages'].values())); ii=page['imageinfo'][0]
 (AUDIT/'wikimedia_photo_metadata.json').write_text(json.dumps({'api_url':api,'retrieval_date':'2026-10-24','page':page},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 b=fetch(ii['url']); (AUDIT/'wikimedia_exterior_reference.jpg').write_bytes(b)
 print('Wikimedia image',ii['url'],len(b))
except Exception as e: print('Wikimedia fetch warning:',repr(e))
props=feat['attributes']
summary={'provider':'Purdue University Libraries GIS / Purdue Campus MapServer, layer 0','service_url':BASE,'query_url':query,'retrieval_date':'2026-10-24','source_crs':data['spatialReference'],'feature_id':props['OBJECTID'],'abbr':props.get('ABBR'),'name':props.get('Name'),'address':props.get('ADDRESS'),'reported_area_m2':props.get('Shape.STArea()'),'reported_perimeter_m':props.get('Shape.STLength()'),'ring_count':len(rings),'ring_vertex_count':sum(len(r) for r in rings),'project_local_bounds_m':bounds,'project_local_polygon_area_m2_approx':area,'conversion':'x=(lon+86.9137)*111412.84*cos(radians(40.4274)); y=(lat-40.4274)*111040.0','crs_note':'Source geometry was returned in EPSG:4326; project coordinates are approximate local tangent-plane conversion, not survey coordinates.','official_history_url':'https://collections.lib.purdue.edu/campus/buildings/168?s=481','official_facility_facts_url':'https://purdue.edu/recwell/visit/facility/fact-sheet.php','architect_url':'https://moodynolan.com/projects/france-a-cordova-recreational-sports-center/','external_photo_reference_url':photo_url,'imagery_service':IMG,'orthophoto':'indiana_current_orthophoto.jpg','orthophoto_overlay':'indiana_current_orthophoto_gis_overlay.jpg','limitations':['The Purdue GIS polygon supports one combined plan footprint; it does not describe internal courtyard voids or roof form.','Current imagery service metadata/scene dates need identification; roof plan only, no wall height.','Legacy GIS record building square footage and official RecWell fact sheet size differ due facility definitions and project inclusion; report both without conflating.','Architectural image is an illustrative source-photo reference only; it is not used as an image texture.']}
(AUDIT/'source_record.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'name':props['Name'],'area_m2':props['Shape.STArea()'],'perimeter_m':props['Shape.STLength()'],'xy_bounds':bounds,'approx_area_local':area,'rings':len(rings),'vertices':sum(len(r) for r in rings),'orthophoto_bytes':(AUDIT/'indiana_current_orthophoto.jpg').stat().st_size,'architect_photo_bytes':(AUDIT/'architect_east_entry_reference.jpg').stat().st_size if (AUDIT/'architect_east_entry_reference.jpg').exists() else None},ensure_ascii=False,indent=2))
