"""Create transparent upper-floor and patio rings from the identified OSM footprint."""
import json, math
from pathlib import Path
from shapely.geometry import Polygon, box, mapping
from shapely.ops import unary_union

OUT=Path(__file__).parent
d=json.loads((OUT/'osm_buildings_near_faith_west.json').read_text(encoding='utf-8'))
feature=next(e for e in d['elements'] if e.get('tags',{}).get('name')=='Faith West Community Center')
coords=[((p['lon']+86.9137)*111412.84*math.cos(math.radians(40.4274)),(p['lat']-40.4274)*111040.0) for p in feature['geometry']]
footprint=Polygon(coords).buffer(0)
# The KJG exterior and Titan aerial show the residence wings behind and along one side of the
# lower community-center podium. Clip the OSM outline to two image-supported zones, then union
# them so the output can preserve disconnected components rather than bridging them.
upper=unary_union([footprint.intersection(box(-690,2170,-635,2226)), footprint.intersection(box(-657,2140,-635,2208))]).buffer(0)
low_roof=footprint.difference(upper).buffer(0)
patio=footprint.intersection(box(-671,2137,-634,2150)).buffer(0)
def rings(g):
    parts=[g] if g.geom_type=='Polygon' else list(g.geoms)
    return [[list(p) for p in part.exterior.coords[:-1]] for part in parts if part.geom_type=='Polygon' and part.area>1.0]
low_parts=[low_roof] if low_roof.geom_type=='Polygon' else list(low_roof.geoms)
hvac_sites=[[part.representative_point().x,part.representative_point().y] for part in low_parts if part.geom_type=='Polygon' and part.area>70]
data={"building_id":"massing_faith_west_community_center_84aa829","provider":"OSM way 743763888 transformed with project local approximation","whole_footprint_polygons":rings(footprint),"upper_footprint_polygons":rings(upper),"upper_area_m2":upper.area,"upper_component_count":len(rings(upper)),"low_roof_polygons":rings(low_roof),"low_roof_area_m2":low_roof.area,"hvac_representative_points_world_m":hvac_sites,"patio_polygons":rings(patio),"patio_area_m2":patio.area,"projection":"X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040.0"}
(OUT/'faith_west_geometry.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in data.items() if 'polygons' not in k},indent=2))
