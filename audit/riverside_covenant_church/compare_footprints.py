import json, math
from pathlib import Path
p=Path(__file__).parent
proj=lambda lon,lat: ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0)
raw=json.loads((p/'source_osm_way_860918859_raw.json').read_text(encoding='utf-8-sig'))
osm=[proj(n['lon'],n['lat']) for n in raw['nodes'][:-1]]
feature=json.loads((p/'indiana_building_footprint_feature_409445.json').read_text(encoding='utf-8-sig'))['features'][0]
gis=[proj(lon,lat) for lon,lat in feature['geometry']['rings'][0][:-1]]
def area(poly):
 return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)
def signed_area(poly):
 return sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2
# Align ring start/order by choosing the minimum summed vertex distance over rotations and reversed ordering.
def align(a,b):
 opts=[]
 for rev in (False,True):
  q=list(reversed(b)) if rev else list(b)
  for k in range(len(q)):
   r=q[k:]+q[:k]
   errs=[math.dist(x,y) for x,y in zip(a,r)]
   opts.append((max(errs),sum(errs),r,errs,rev,k))
 return min(opts,key=lambda x:(x[0],x[1]))
mx,total,aligned,errs,rev,k=align(osm,gis)
area_o,area_g=area(osm),area(gis)
# Convex polygon clipping for the overlap ratio.
def clip(subject, clipper):
 out=list(subject); orient=1 if signed_area(clipper)>=0 else -1
 for i,a in enumerate(clipper):
  b=clipper[(i+1)%len(clipper)]
  inp=out; out=[]
  if not inp: break
  def side(q): return orient*((b[0]-a[0])*(q[1]-a[1])-(b[1]-a[1])*(q[0]-a[0]))
  for j,e in enumerate(inp):
   s=inp[j-1]; se,ss=side(e),side(s)
   if (se>=-1e-9)!=(ss>=-1e-9):
    dx=e[0]-s[0]; dy=e[1]-s[1]; ex=b[0]-a[0]; ey=b[1]-a[1]
    den=dx*ey-dy*ex
    if abs(den)>1e-15:
     t=((a[0]-s[0])*ey-(a[1]-s[1])*ex)/den
     out.append((s[0]+t*dx,s[1]+t*dy))
   if se>=-1e-9: out.append(e)
 return out
inter=area(clip(osm,gis)); union=area_o+area_g-inter
cx_o=sum(x for x,y in osm)/len(osm); cy_o=sum(y for x,y in osm)/len(osm)
cx_g=sum(x for x,y in gis)/len(gis); cy_g=sum(y for x,y in gis)/len(gis)
result={
 'building':'Riverside Covenant Church','retrieval_date':'2026-10-26',
 'official_source':{'provider':'Indiana Geographic Information Office / IndianaMap','dataset':'Indiana Building Footprints 2016-2020','feature_id':feature['attributes']['objectid'],'county':feature['attributes'].get('county'),'lidar_year':feature['attributes'].get('lidaryear'),'url':'https://gisdata.in.gov/server/rest/services/Hosted/Building_Footprints/FeatureServer/0','service_layer_crs':'EPSG:3857','query_output_crs':'EPSG:4326'},
 'comparison_source':{'provider':'OpenStreetMap via Overpass API','feature_id':'way/860918859','snapshot_timestamp':'2026-10-22T03:48:50Z','url':'https://www.openstreetmap.org/way/860918859'},
 'projection':{'name':'Purdue project approximate local XY conversion','x':'(longitude + 86.9137) * 111412.84 * cos(radians(40.4274))','y':'(latitude - 40.4274) * 111040.0','units':'meters','limitation':'not a surveyed CRS'},
 'method':'Transform independent Indiana footprint and OSM rings to project-local XY; recompute areas in meters; select cyclic/reversed vertex alignment with least maximum vertex distance; compute convex-polygon intersection-over-union.',
 'official_footprint_area_m2':round(area_g,3),'osm_footprint_area_m2':round(area_o,3),'area_ratio_official_to_osm':round(area_g/area_o,4),
 'centroid_offset_m':round(math.dist((cx_o,cy_o),(cx_g,cy_g)),3),'max_aligned_vertex_offset_m':round(mx,3),'mean_aligned_vertex_offset_m':round(sum(errs)/len(errs),3),
 'footprint_iou':round(inter/union,4),'best_alignment':{'reversed':rev,'rotation':k},
 'osm_ring_projected_m':[[round(x,3),round(y,3)] for x,y in osm],
 'indiana_ring_projected_m':[[round(x,3),round(y,3)] for x,y in gis],
 'uncertainty':'Indiana 2016-2020 footprints are independent of the original OSM import and identify the local structure by polygon overlap. They are not a legal survey; the source attribution states LIDAR year 2018. Boundary differences may reflect mapping tolerance or roof/structure treatment.'}
(p/'footprint_comparison_indiana_2018_vs_osm.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ('official_footprint_area_m2','osm_footprint_area_m2','centroid_offset_m','max_aligned_vertex_offset_m','footprint_iou')},indent=2))
