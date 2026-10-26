"""Screening comparison of the source massing outline with official GIS polygon PAO FID 72."""
import json, math, os
from pathlib import Path
from shapely.geometry import Polygon
from shapely import hausdorff_distance

HERE=Path(__file__).parent
root=HERE.parents[1]
raw=json.loads((HERE/'gis_fid72_raw.json').read_text(encoding='utf-8'))['feature']
report=json.loads((HERE/'build_report.json').read_text(encoding='utf-8'))
ring=raw['geometry']['rings'][0]

def mercator_to_local(x,y):
    # ArcGIS layer returns WKID 102100 / latest WKID 3857 (spherical Web Mercator metres).
    lon=x/6378137.0*180.0/math.pi
    lat=(2.0*math.atan(math.exp(y/6378137.0))-math.pi/2.0)*180.0/math.pi
    # Project convention from modular/AGENTS.md: local approximate tangent plane origin.
    lx=(lon+86.9137)*111412.84*math.cos(math.radians(40.4274))
    ly=(lat-40.4274)*111040.0
    return lx,ly

gis_pts=[mercator_to_local(x,y) for x,y in ring]
asset_pts=[tuple(xy) for xy in report['source_footprint_xy_m']]
gis=Polygon(gis_pts); asset=Polygon(asset_pts)
intersection=gis.intersection(asset).area
union=gis.union(asset).area
result={
 'feature':{'BLDG_ABBR':raw['attributes'].get('BLDG_ABBR'),'FID':raw['attributes'].get('FID'),'BUILDING_N':raw['attributes'].get('BUILDING_N')},
 'source_crs':'EPSG:3857 (ArcGIS metadata WKID 102100, latestWKID 3857), metres',
 'transform':'inverse spherical Web Mercator to lon/lat; then project local formula from modular/AGENTS.md, origin lon=-86.9137 lat=40.4274',
 'model_bbox_xy_m':[[min(x for x,y in asset_pts),max(x for x,y in asset_pts)],[min(y for x,y in asset_pts),max(y for x,y in asset_pts)]],
 'gis_bbox_xy_m':[[min(x for x,y in gis_pts),max(x for x,y in gis_pts)],[min(y for x,y in gis_pts),max(y for x,y in gis_pts)]],
 'bbox_side_differences_m':{'x_min':min(x for x,y in asset_pts)-min(x for x,y in gis_pts),'x_max':max(x for x,y in asset_pts)-max(x for x,y in gis_pts),'y_min':min(y for x,y in asset_pts)-min(y for x,y in gis_pts),'y_max':max(y for x,y in asset_pts)-max(y for x,y in gis_pts)},
 'asset_outline_area_m2':asset.area,'gis_outline_area_m2_local_tangent':gis.area,
 'polygon_iou':intersection/union,'polygon_symmetric_difference_area_m2':gis.symmetric_difference(asset).area,
 'polygon_hausdorff_distance_m':hausdorff_distance(gis,asset),
 'asset_outline_centroid_xy_m':[asset.centroid.x,asset.centroid.y],
 'gis_outline_centroid_xy_m':[gis.centroid.x,gis.centroid.y],
 'centroid_offset_m':asset.centroid.distance(gis.centroid),
 'interpretation':'Screening metric only. This ArcGIS footprint is generalized campus GIS geometry, not a surveyed structural-wall line; existing mesh is a simplified massing outline. Similar bounds/overlap supports the PAO candidate identity but does not certify every wall offset, facade, roof, interior, or height.'
}
(HERE/'footprint_comparison.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
