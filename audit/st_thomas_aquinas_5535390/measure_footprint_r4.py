from pathlib import Path
import json
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union, polygonize
AUDIT=Path(__file__).resolve().parent
source=json.loads((AUDIT/'projected_footprint_evidence.json').read_text(encoding='utf-8'))
model=json.loads((AUDIT/'footprint_extract_r4.json').read_text(encoding='utf-8'))
gis=Polygon(source['local_outline_xy_m'])
segments=model['SOTAC_Stone_Foundation_and_Plinth']['horizontal_edges']['0.0']
model_polys=list(polygonize(unary_union([LineString(e) for e in segments])))
outline=unary_union(model_polys)
inter=outline.intersection(gis).area
res={'measurement':'2D structural foundation perimeter vs Purdue GIS FID 852 outline in the same project-local XY transform; read from saved Blender mesh horizontal base edges. GIS outline is not a surveyed wall line.',
     'GIS_feature_id':source['gis']['feature_id'],'GIS_name':source['gis']['name'],'GIS_address':source['gis']['address'],
     'GIS_source_crs':source['gis']['native_crs'],'GIS_outline_area_m2':gis.area,'model_base_outline_area_m2':outline.area,
     'intersection_area_m2':inter,'union_area_m2':outline.union(gis).area,'intersection_over_union':inter/outline.union(gis).area,
     'symmetric_difference_area_m2':outline.symmetric_difference(gis).area,'boundary_hausdorff_distance_m':outline.boundary.hausdorff_distance(gis.boundary),
     'model_bounds_local_m':list(outline.bounds),'GIS_bounds_local_m':list(gis.bounds),'model_edges':len(segments),'polygon_parts':len(model_polys)}
(AUDIT/'footprint_match_r4.json').write_text(json.dumps(res,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(res,indent=2,ensure_ascii=False))
