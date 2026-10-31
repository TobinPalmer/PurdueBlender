from pathlib import Path
import json, xml.etree.ElementTree as ET
from pyproj import Transformer
from shapely.geometry import Polygon,LineString
from shapely.ops import nearest_points
root=Path(__file__).resolve().parents[3]; audit=root/'audit/massing_telecommunications_building_tel_8dfaccf'; g=json.loads((audit/'sources/purdue_gis_fid199_tel.json').read_text(encoding='utf-8-sig'))['features'][0]
conv=lambda p:((p[0]+86.9137)*111412.84*__import__('math').cos(__import__('math').radians(40.4274)),(p[1]-40.4274)*111040.0)
pr=[conv(p) for p in g['geometry']['rings'][0]]
rt=ET.parse(audit/'sources/osm_way_159752232.xml').getroot(); nodes={x.attrib['id']:(float(x.attrib['lon']),float(x.attrib['lat'])) for x in rt.findall('node')}; way=rt.find('way'); refs=[n.attrib['ref'] for n in way.findall('nd')]; op=[conv(nodes[r]) for r in refs]
pp=Polygon(pr); po=Polygon(op)
entry=[n for n in rt.findall('node') if any(t.attrib.get('k')=='entrance' and t.attrib.get('v')=='main' for t in n.findall('tag'))]
entry_xy=conv((float(entry[0].attrib['lon']),float(entry[0].attrib['lat']))) if entry else None
b=pp.bounds; ob=po.bounds
res={'purdue_fid':g['attributes']['FID'],'purdue_name':g['attributes']['BUILDING_N'],'code':g['attributes']['BLDG_ABBR'],'address':g['attributes']['ADDRESS'],'gis_ring_coordinate_count':len(pr),'ring_area_local_m2':pp.area,'ring_perimeter_local_m':pp.length,'ring_bounds_local_m':b,'osm_way':int(way.attrib['id']),'osm_tags':{t.attrib['k']:t.attrib['v'] for t in way.findall('tag')},'osm_ring_coordinate_count':len(op),'osm_area_local_m2':po.area,'osm_bounds_local_m':ob,'outline_hausdorff_distance_m':pp.boundary.hausdorff_distance(po.boundary),'centroid_distance_m':pp.centroid.distance(po.centroid),'main_entrance_node':int(entry[0].attrib['id']) if entry else None,'main_entrance_world_xy_m':entry_xy,'main_entrance_distance_to_purdue_outline_m':pp.boundary.distance(__import__('shapely').geometry.Point(entry_xy)) if entry_xy else None,'resolution':'Purdue BuildingShapes FID 199 has the exact TEL code, official name and 191 N University address. Independent OSM way 159752232 has the same named building and address number 191, with mapped entrance=main node. Compare outlines numerically to confirm plan match; OSM remains crowd-sourced corroboration.'}
(audit/'sources'/'crosswalk_metrics.json').write_text(json.dumps(res,indent=2),encoding='utf-8'); print(json.dumps(res,indent=2))
