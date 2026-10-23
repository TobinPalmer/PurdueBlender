import json, math, datetime, pathlib
root=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); audit=root/'audit/batch3_elliott'
feature=json.loads((audit/'building_shapes_fid_617_raw.json').read_text())['feature']; meta=json.loads((audit/'building_shapes_layer_metadata_raw.json').read_text())
near=json.loads((audit/'building_shapes_neighborhood_raw.json').read_text())
polygon=json.loads((audit/'polygon.json').read_text())
manifest=json.loads((root/'modular/manifest.json').read_text());rec=next(x for x in manifest['assets'] if x['id']=='elliott_hall_of_music')
origin=rec['placement_origin_xy_m']; source_ring=feature['geometry']['rings'][0][:-1]; assert len(source_ring)==len(polygon)==188
lat=math.radians(40.4274);lon=math.radians(-86.9137);R=6378137.0
x0=R*lon;y0=R*math.log(math.tan(math.pi/4+lat/2));k=math.cos(lat)
source_world=[((x-x0)*k,(y-y0)*k) for x,y in source_ring]
asset_world=[(x+origin[0],y+origin[1]) for x,y in polygon]
errors=[math.dist(a,b) for a,b in zip(source_world,asset_world)]
def area(poly):return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)
def perimeter(poly):return sum(math.dist(poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly)))
local_area=area(polygon);source_ground_area=feature['attributes']['Shape__Area']*k*k
local_perim=perimeter(polygon);source_ground_perim=feature['attributes']['Shape__Length']*k
out={
 'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'request_url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/617?f=pjson',
 'layer_metadata_request_url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0?f=pjson',
 'source':'Purdue BuildingShapesZip4 FeatureServer, layer 0, FID 617 (ELLT)',
 'source_crs':{'wkid':meta['extent']['spatialReference']['wkid'],'latestWkid':meta['extent']['spatialReference']['latestWkid'],'name':'WGS 84 Web Mercator Auxiliary Sphere (ArcGIS WKID 102100 / latest WKID 3857)','axis_order':'x=easting, y=northing'},
 'retrieval':'Raw layer metadata and FID 617 feature response saved beside this report; neighborhood query saved as building_shapes_neighborhood_raw.json. Retrieval date is UTC shown above.',
 'project_geographic_origin':{'latitude':40.4274,'longitude':-86.9137,'datum':'WGS 84'},
 'local_metric_conversion':'Approximate ground-plane east/north coordinates from Web Mercator: (x-x0, y-y0) multiplied by cos(latitude_origin). No rotation or best-fit was applied to the overlay.',
 'geometry_counts':{'source_ring_coordinates_including_closure':len(feature['geometry']['rings'][0]),'source_unique_vertices':len(source_ring),'asset_local_vertices':len(polygon),'neighborhood_feature_count':len(near['features'])},
 'placement_record':{'id':rec['id'],'origin_xy_m':origin,'kind':rec['kind'],'file':rec['file'],'collection':rec['collection']},
 'vertex_correspondence_method':'Compare ordered 188 unique source vertices after map-to-ground transform against ordered asset polygon.json vertices translated by the manifest origin. This is a direct placement comparison, not a freely fitted transform.',
 'vertex_residual_m':{'rms':math.sqrt(sum(e*e for e in errors)/len(errors)),'maximum':max(errors),'mean':sum(errors)/len(errors)},
 'footprint_area_m2':{'asset_polygon_local':local_area,'GIS_shape_area_ground_approx':source_ground_area,'relative_difference_percent':100*(local_area-source_ground_area)/source_ground_area},
 'perimeter_m':{'asset_polygon_local':local_perim,'GIS_shape_length_ground_approx':source_ground_perim,'relative_difference_percent':100*(local_perim-source_ground_perim)/source_ground_perim},
 'limitations':['Web Mercator-to-ground conversion uses a constant origin-latitude scale over a compact campus neighborhood.','Feature geometry verifies the horizontal footprint only; it does not verify height, façade openings, entry details, or interior geometry.','This overlay is based on Purdue GIS polygons and the current manifest/local asset coordinates; it is not a surveyed site-control measurement.']
}
(audit/'footprint_comparison_round9.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))

