"""GIS footprint residuals, plan overlay and imagery overlay for Acacia FID 791."""
import json, math, os
from shapely.geometry import Polygon, LineString, Point
from PIL import Image, ImageDraw, ImageFont

HERE=os.path.abspath(os.path.dirname(__file__))
src=os.path.join(HERE,'sources')
gis=json.load(open(os.path.join(src,'purdue_gis_fid791_2026-10-26_wgs84.json'),encoding='utf8'))['features'][0]
state=json.load(open(os.path.join(src,'purdue_gis_fid791_2026-10-26_stateplane_2968.json'),encoding='utf8'))['features'][0]
shell=json.load(open(os.path.join(HERE,'shell_outline.json'),encoding='utf8'))
lat0,lon0=40.4274,-86.9137
def local(lon,lat): return ((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0)
ring=[local(lon,lat) for lon,lat in gis['geometry']['rings'][0][:-1]]
gp=Polygon(ring); sp=Polygon(shell); inter=gp.intersection(sp); union=gp.union(sp)
attr=gis['attributes']; state_poly=Polygon(state['geometry']['rings'][0]); usft=.304800609601219
sb=state_poly.area*usft*usft; sl=state_poly.length*usft
gb=gp.bounds; mb=sp.bounds
line1=LineString(gp.exterior.coords); line2=LineString(sp.exterior.coords)
res=[line1.distance(Point(p)) for p in list(sp.exterior.coords)[:-1]]+[line2.distance(Point(p)) for p in list(gp.exterior.coords)[:-1]]
cent=(gp.centroid.x-sp.centroid.x,gp.centroid.y-sp.centroid.y)
out={
 'source_feature_id':791,
 'coordinate_transform':'WGS84 to project-local approximate meters: X=(lon+86.9137)*111412.84*cos(40.4274 degrees); Y=(lat-40.4274)*111040',
 'crs_stateplane':'EPSG:2968 NAD83(HARN) / Indiana West, US survey feet; converted at 0.304800609601219 m/ft',
 'measurements':{
  'gis_wgs84_ring_area_m2':gp.area,'shell_area_m2':sp.area,'shell_minus_ring_area_m2':sp.area-gp.area,
  'shell_area_residual_percent_of_gis':100*(sp.area-gp.area)/gp.area,
  'gis_bbox_x_width_m':gb[2]-gb[0],'shell_bbox_x_width_m':mb[2]-mb[0],
  'shell_minus_gis_x_width_m':(mb[2]-mb[0])-(gb[2]-gb[0]),
  'gis_bbox_y_length_m':gb[3]-gb[1],'shell_bbox_y_length_m':mb[3]-mb[1],
  'shell_minus_gis_y_length_m':(mb[3]-mb[1])-(gb[3]-gb[1]),
  'south_extension_beyond_shell_m':mb[1]-gb[1],
  'intersection_over_union':inter.area/union.area,'symmetric_difference_area_m2':gp.symmetric_difference(sp).area,
  'centroid_delta_gis_minus_shell_xy_m':list(cent),'centroid_delta_distance_m':math.hypot(*cent),
  'bidirectional_vertex_to_boundary_rms_m':math.sqrt(sum(x*x for x in res)/len(res)),
  'bidirectional_vertex_to_boundary_max_m':max(res),'hausdorff_boundary_m':gp.hausdorff_distance(sp),
  'shape_area_attribute':attr['Shape__Area'],'shape_length_attribute':attr['Shape__Length'],
  'stateplane_ring_area_m2_after_unit_conversion':sb,'stateplane_ring_perimeter_m_after_unit_conversion':sl},
 'final_shell_transform_applied_m':[0,0,0],
 'source_field_resolution':'The encoded WGS84 ring area is 461.877 m2; the EPSG:2968 ring converts to 462.103 m2, a +0.226 m2 (+0.049%) residual, so the two geometries agree. The shell is 459.065 m2, -2.812 m2 (-0.609%) from the WGS84 ring. GIS bounds are 19.513 x 31.648 m; shell bounds are 19.439 x 28.493 m. The GIS ring extends 3.148 m farther south, consistent with its small entry/porch projection; shell-to-ring IoU is 0.933, centroid offset 0.660 m, and Hausdorff residual 3.211 m. ArcGIS Shape__Area=798.445 and Shape__Length=138.597 differ from the encoded rings by +336.568 m2 and +33.220 m and are treated as stale/legacy summary attributes. The modeled structural shell remains in its original campus coordinates without a transform.',
 'porch_bearing':'West-facing long elevation, inferred by matching the official porch/elevation plan to the north-up aerial and its west-side approach path. The official facade image itself is not geotagged.'
}
out['measurements']['stateplane_area_m2_minus_wgs84_ring_m2']=sb-gp.area
out['measurements']['stateplane_area_residual_percent']=100*(sb-gp.area)/gp.area
out['measurements']['shape_area_attribute_minus_wgs84_ring_m2']=attr['Shape__Area']-gp.area
out['measurements']['shape_length_attribute_minus_ring_perimeter_m']=attr['Shape__Length']-gp.length
with open(os.path.join(HERE,'gis_comparison.json'),'w',encoding='utf8') as f: json.dump(out,f,indent=2)

W,H=1600,1120; pad=85
xmin=min(gb[0],mb[0])-2; xmax=max(gb[2],mb[2])+2; ymin=min(gb[1],mb[1])-2; ymax=max(gb[3],mb[3])+2
scale=min((W-2*pad)/(xmax-xmin),(H-2*pad)/(ymax-ymin))
def planpx(p):return (pad+(p[0]-xmin)*scale,H-pad-(p[1]-ymin)*scale)
im=Image.new('RGB',(W,H),(249,249,247)); d=ImageDraw.Draw(im,'RGBA')
try: font=ImageFont.truetype('arial.ttf',22); small=ImageFont.truetype('arial.ttf',17)
except: font=small=ImageFont.load_default()
d.polygon([planpx(p) for p in ring],fill=(244,159,48,70),outline=(214,110,12,255),width=4)
d.polygon([planpx(p) for p in shell],fill=(19,146,189,42),outline=(0,99,145,255),width=4)
d.text((45,25),'ACACIA / FID 791 — structural shell and Purdue GIS ring',font=font,fill=(25,35,45,255))
d.line((50,75,105,75),fill=(214,110,12,255),width=5); d.text((115,62),'GIS ring',font=small,fill=(25,35,45,255))
d.line((230,75,285,75),fill=(0,99,145,255),width=5); d.text((295,62),'Structural wall shell',font=small,fill=(25,35,45,255))
mx,my=planpx(((xmin+xmax)/2,ymax-1.6)); d.line((mx,my,mx,my-65),fill=(20,30,40,255),width=4); d.polygon([(mx,my-78),(mx-9,my-58),(mx+9,my-58)],fill=(20,30,40,255)); d.text((mx-9,my-109),'N',font=font,fill=(20,30,40,255))
caption=f"GIS ring {gp.area:.2f} m2 | shell {sp.area:.2f} m2 | IoU {inter.area/union.area:.3f} | centroid {math.hypot(*cent):.2f} m | Hausdorff {gp.hausdorff_distance(sp):.2f} m"
d.rectangle((30,H-67,W-30,H-24),fill=(255,255,255,240)); d.text((45,H-61),caption,font=small,fill=(20,35,45,255))
im.save(os.path.join(HERE,'gis_topdown_overlay.png'))

# Overlay local-coordinate shell and FID ring on the north-up Esri imagery mosaic.
meta=json.load(open(os.path.join(src,'esri_world_imagery_acacia_metadata.json'),encoding='utf8'))
z=meta['zoom']; n=2**z; cx,cy=meta['center_tile_xy']; tx0,ty0=cx-1,cy-1
def tilepx(lon,lat):
 px=(lon+180)/360*n*256; py=(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n*256
 return (px-tx0*256,py-ty0*256)
def geog(x,y):return (lon0+x/(111412.84*math.cos(math.radians(lat0))),lat0+y/111040.0)
aerial=Image.open(os.path.join(src,'esri_world_imagery_acacia_z20_mosaic.jpg')).convert('RGB'); ad=ImageDraw.Draw(aerial,'RGBA')
ad.polygon([tilepx(lon,lat) for lon,lat in gis['geometry']['rings'][0]],fill=(244,145,22,25),outline=(255,128,0,255),width=3)
ad.polygon([tilepx(*geog(x,y)) for x,y in shell],fill=(0,150,230,20),outline=(0,220,255,255),width=3)
ad.rectangle((6,6,760,64),fill=(0,0,0,175)); ad.text((16,12),'NORTH-UP / ESRI WORLD IMAGERY Z20 | orange: GIS | cyan: wall shell',font=small,fill=(255,255,255,255))
ad.line((737,29,737,53),fill=(255,255,255,255),width=3); ad.polygon([(737,15),(729,31),(745,31)],fill=(255,255,255,255)); ad.text((731,0),'N',font=small,fill=(255,255,255,255))
aerial.save(os.path.join(HERE,'aerial_gis_orientation_overlay.png'))
print(json.dumps({'comparison':out,'plan_overlay':'audit/acacia/gis_topdown_overlay.png','aerial_overlay':'audit/acacia/aerial_gis_orientation_overlay.png'}))
