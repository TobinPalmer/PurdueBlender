import json, math, xml.etree.ElementTree as ET
from pathlib import Path
from shapely.geometry import Polygon
root=Path('audit/massing_johnson_hall_of_nursing_jnsn_823fca7')
shared=json.load(open('audit/official_purdue_buildings_wgs84.json',encoding='utf-8-sig'))
f=next(x for x in shared['features'] if x['attributes'].get('FID')==218)
assert f['attributes']['BLDG_ABBR']=='JNSN'
feature={'attributes':f['attributes'],'geometry':f['geometry']}
(root/'sources/purdue_building_shapes_fid218_jnsn.json').write_text(json.dumps({'geometryType':shared['geometryType'],'spatialReference':shared['spatialReference'],'geometryProperties':shared['geometryProperties'],'feature':feature},indent=2),encoding='utf-8')
refs=json.load(open('audit/official_building_references.json',encoding='utf-8-sig'))
ref=next(x for x in (refs if isinstance(refs,list) else refs.get('buildings',[])) if x.get('code')=='JNSN')
(root/'sources/official_building_reference_jnsn.json').write_text(json.dumps(ref,indent=2),encoding='utf-8')
origin=(-86.9137,40.4274); cos=math.cos(math.radians(origin[1]))
transform=lambda lon,lat:((lon-origin[0])*111412.84*cos,(lat-origin[1])*111040.0)
gis=[transform(*p) for p in f['geometry']['rings'][0]]
if gis[0]==gis[-1]: gis=gis[:-1]
poly=Polygon(gis)
xml=ET.parse(root/'sources/osm_way_117146488.xml').getroot()
nodes={n.get('id'):(float(n.get('lon')),float(n.get('lat'))) for n in xml.findall('node')}
way=xml.find('way'); osm=[transform(*nodes[nd.get('ref')]) for nd in way.findall('nd')]
if osm[0]==osm[-1]: osm=osm[:-1]
osmp=Polygon(osm)
from shapely.ops import nearest_points
metrics={'gis_feature':{'FID':f['attributes']['FID'],'name':f['attributes']['BUILDING_N'],'code':f['attributes']['BLDG_ABBR'],'levels':f['attributes']['NUM_LEVELS'],'extrution_raw':f['attributes']['Extrution'],'shape_area_attr':f['attributes']['Shape__Area'],'shape_length_attr':f['attributes']['Shape__Length'],'ring_count':len(f['geometry']['rings']),'ring_vertices_including_close':len(f['geometry']['rings'][0]),'local_approx_unique_ring_vertices':len(gis),'local_approx_area_m2':poly.area,'local_approx_valid':poly.is_valid,'bounds_xy':poly.bounds},'osm':{'way_id':117146488,'tags':{x.get('k'):x.get('v') for x in way.findall('tag')},'unique_vertices':len(osm),'local_approx_area_m2':osmp.area,'bounds_xy':osmp.bounds,'boundary_hausdorff_to_gis_m':poly.boundary.hausdorff_distance(osmp.boundary),'centroid_offset_m':poly.centroid.distance(osmp.centroid)}}
(root/'sources/source_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(json.dumps(metrics,indent=2))

