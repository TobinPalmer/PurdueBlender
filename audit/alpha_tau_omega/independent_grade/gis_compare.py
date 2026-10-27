import json, math
from pathlib import Path
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
audit=root/'audit/alpha_tau_omega'
src=json.loads((audit/'sources/purdue_gis_fid785_2026-10-26.json').read_text(encoding='utf-8-sig'))['features'][0]
ring=src['geometry']['rings'][0]
lat0,lon0=40.4274,-86.9137
coords=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0) for lon,lat in ring]
gis=Polygon(coords)
parts=[box(-435.35,68.70,-420.15,83.70),box(-433.455,46.00,-420.105,65.10),box(-433.455,64.25,-420.105,68.65),box(-420.0,75.175,-413.80,82.825),box(-436.875,64.025,-432.625,68.475)]
model=unary_union(parts)
res={'gis_feature_id':src['attributes']['FID'],'building_name':src['attributes']['BUILDING_N'],'abbr':src['attributes']['BLDG_ABBR'],'gis_bounds_xy_m':[[gis.bounds[0],gis.bounds[2]],[gis.bounds[1],gis.bounds[3]]],'gis_area_m2':gis.area,'structural_candidate_bounds_xy_m':[[model.bounds[0],model.bounds[2]],[model.bounds[1],model.bounds[3]]],'candidate_area_m2':model.area,'intersection_area_m2':gis.intersection(model).area,'iou':gis.intersection(model).area/gis.union(model).area,'approx_local_projection':'X=(lon+86.9137)*111412.84*cos(40.4274°), Y=(lat-40.4274)*111040; local tangent approximation; not surveyed','candidate_outline_method':'Union of five manually read structural wall footprint rectangles from model/build evidence; decorative porch, steps, garden wall excluded'}
out=audit/'independent_grade'/'gis_comparison.json';out.write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
