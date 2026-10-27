import json
from pathlib import Path
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[3]
probe=json.loads((Path(__file__).with_name('fresh_open_probe.json')).read_text(encoding='utf-8'))
source=json.loads((ROOT/'audit/frieda_parker_hall/sources/purdue_arcgis_fid_409.geojson').read_text(encoding='utf-8'))
feature=source['features'][0]
ORIGIN=(-499.7250061,97.475)
ring=feature['geometry']['coordinates'][0]
gis=Polygon([((lon+86.9137)*84810.60416539927-ORIGIN[0],(lat-40.4274)*111040.0-ORIGIN[1]) for lon,lat in ring])
major_names=['Frieda_EastWing_Upper_South','Frieda_EastWing_Upper_North','Frieda_WestWing_Upper']
objects={o['name']:o for o in probe['selected_structural_objects']}
missing=[n for n in major_names if n not in objects]
if missing: raise RuntimeError(f'missing major shells {missing}')
def bbox_poly(o):
 b=o['bounds_xyz']; return box(b[0][0],b[1][0],b[0][1],b[1][1])
shells={n:bbox_poly(objects[n]) for n in major_names}
shell=unary_union(list(shells.values()))
inside=shell.intersection(gis).area
union=shell.union(gis).area
allbb=probe['full_mesh_bounds_local_xyz']
model_env=[[min(shell.bounds[0],shell.bounds[2]),max(shell.bounds[0],shell.bounds[2])],[min(shell.bounds[1],shell.bounds[3]),max(shell.bounds[1],shell.bounds[3])]]
gis_env=[[gis.bounds[0],gis.bounds[2]],[gis.bounds[1],gis.bounds[3]]]
errors=[[model_env[0][0]-gis_env[0][0],model_env[0][1]-gis_env[0][1]],[model_env[1][0]-gis_env[1][0],model_env[1][1]-gis_env[1][1]]]
result={
 'asset_sha256':probe['sha256'],
 'source_provider':'Purdue University ArcGIS BuildingShapesZip4 layer 0',
 'feature_id':feature['id'],'feature_name':feature['properties']['BUILDING_N'],'address':feature['properties'].get('ADDRESS'),
 'raw_source':'audit/frieda_parker_hall/sources/purdue_arcgis_fid_409.geojson',
 'source_crs':'EPSG:4326 response; transformed into the project local frame with X=(lon+86.9137)*84810.60416539927 and Y=(lat-40.4274)*111040, then subtracting assigned origin [-499.7250061,97.475] m.',
 'gis_polygon':{'valid':gis.is_valid,'area_m2':round(gis.area,3),'bounds_local_xy_m':[[round(gis.bounds[0],3),round(gis.bounds[2],3)],[round(gis.bounds[1],3),round(gis.bounds[3],3)]],'centroid_local_xy_m':[round(gis.centroid.x,3),round(gis.centroid.y,3)],'unique_ring_vertices':len(ring)-1},
 'shell_method':'Independently fresh-opened Blender object world-space mesh bound boxes for the three remaining major upper shells; these are rectangular volumes so their XY bounds are their plan footprints. Union compared with GIS polygon using Shapely 2.2.0.',
 'upper_shells':{n:{'bounds_local_xy_m':[[round(g.bounds[0],3),round(g.bounds[2],3)],[round(g.bounds[1],3),round(g.bounds[3],3)]],'bbox_plan_area_m2':round(g.area,3),'fraction_inside_gis':round(g.intersection(gis).area/g.area,5)} for n,g in shells.items()},
 'upper_shell_union':{'area_m2':round(shell.area,3),'intersection_with_gis_m2':round(inside,3),'outside_gis_m2':round(shell.difference(gis).area,3),'iou':round(inside/union,5),'fraction_shell_area_inside_gis':round(inside/shell.area,5),'bounds_local_xy_m':[[round(shell.bounds[0],3),round(shell.bounds[2],3)],[round(shell.bounds[1],3),round(shell.bounds[3],3)]]},
 'envelope_difference_model_minus_gis_m':errors,
 'northwing_upper_object_present':any('NorthWing_Upper' in o['name'] for o in probe['selected_structural_objects']),
 'full_asset_bounds_local_xyz_m':allbb,
 'limits':['The GIS service does not publish positional accuracy/date; it may be generalized and cannot certify wall lines.','The project geographic conversion is an approximate local linear transform, not a surveyed CRS.','The shell geometry is represented with rectangular upper-shell meshes; mesh bounds are appropriate for these volumes but do not fully capture every wall/footprint detail.']}
Path(__file__).with_name('gis_comparison_r2.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['gis_polygon','upper_shell_union','envelope_difference_model_minus_gis_m','northwing_upper_object_present']},indent=2))

