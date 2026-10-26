from pathlib import Path
import json, math
import numpy as np
import tifffile
from pyproj import Transformer
from shapely.geometry import Polygon, Point
ROOT=Path('.')
src=ROOT/'audit/massing_campus_edge_343e3d8/sources'
raw=json.loads((src/'openstreetmap_way_886359911_full.json').read_text(encoding='utf-8'))
by_id={e['id']:e for e in raw['elements'] if e['type']=='node'}
way=next(e for e in raw['elements'] if e['type']=='way')
coords_wgs=[(by_id[n]['lon'],by_id[n]['lat']) for n in way['nodes']]
transform=Transformer.from_crs('EPSG:4326','EPSG:2968',always_xy=True)
coords_ft=[transform.transform(lon,lat) for lon,lat in coords_wgs]
poly=Polygon(coords_ft)
p=src/'indiana_2018_tippecanoe_ndhm_in2018_30001880_12.tif'
with tifffile.TiffFile(p) as tf:
    a=tf.pages[0].asarray()
OX,OY,PIX=3000000.0,1885000.0,5.0
rows=[]; vals=[]
# Inspect cell centers strictly inside OSM polygon, excluding likely tree/nodata extremes.
for r in range(a.shape[0]):
    y=OY-(r+0.5)*PIX
    # bounding box early-outs
    if y < poly.bounds[1]-PIX or y > poly.bounds[3]+PIX: continue
    for c in range(a.shape[1]):
        x=OX+(c+0.5)*PIX
        if x < poly.bounds[0]-PIX or x > poly.bounds[2]+PIX: continue
        if poly.contains(Point(x,y)):
            v=float(a[r,c])
            if math.isfinite(v): vals.append(v); rows.append((r,c,v))
arr=np.asarray(vals)
ft_to_m=1200/3937
filtered=arr[(arr>=10)&(arr<=160)]
ind=json.loads((src/'indiana_2016_2020_building_footprints_point_query_2026-10-25.json').read_text(encoding='utf-8-sig'))
ind_poly=Polygon([transform.transform(lon,lat) for lon,lat in ind['features'][0]['geometry']['coordinates'][0]])
summary={
 'building_id':'massing_campus_edge_343e3d8',
 'source':'Indiana 2018 3DEP normalized digital height model',
 'tile':'in2018_30001880_12_ndhm.tif',
 'source_crs':'EPSG:2968 NAD83(HARN) / Indiana West (US survey feet)',
 'tile_geotransform':{'upper_left_x_ftUS':OX,'upper_left_y_ftUS':OY,'pixel_size_ftUS':PIX,'width_px':a.shape[1],'height_px':a.shape[0]},
 'footprint':'OpenStreetMap way 886359911, projected from EPSG:4326 to EPSG:2968 with pyproj',
 'pixel_sampling':'Sample pixel centers inside OSM way polygon; no interpolation.',
 'raw_inside_sample_count':len(arr),
 'raw_inside_ft_quantiles':{str(q):float(np.percentile(arr,q)) for q in [5,25,50,75,90,95,99]},
 'filtered_roof_values_ft_10_to_160':{'n':int(filtered.size),'quantiles':{str(q):float(np.percentile(filtered,q)) for q in [5,25,50,75,90,95,99]},'median_m':float(np.median(filtered)*ft_to_m),'p90_m':float(np.percentile(filtered,90)*ft_to_m)},
 'candidate_roof_height_estimate_m':float(np.percentile(filtered,75)*ft_to_m),
 'interpretation':'NDHM cells estimate height above ground; robust interior roof-surface statistics support approximate building height but are not a surveyed roof datum/eave. The tile contains outliers, excluded from the representative roof sample by the stated 10–160 ft range.',
 'limitations':['5-ft raster cells mix roof edges and surroundings.','Tree/outlier cells inside the plan polygon can inflate upper quantiles.','NDHM height surface does not establish floor count, eave height, or architectural stepbacks.','Collection year 2018; current photo evidence is later.'],
 'indiana_footprint_comparison':{'objectid':ind['features'][0]['properties']['objectid'],'source_year':ind['features'][0]['properties']['lidaryear'],'osm_area_m2_local':float(Polygon([( (lon+86.9137)*111412.84*math.cos(math.radians(40.4274)), (lat-40.4274)*111040 ) for lon,lat in coords_wgs]).area),'indiana_area_ft2_stateplane':float(ind_poly.area),'indiana_area_m2_stateplane':float(ind_poly.area*(1200/3937)**2)}
}
out=ROOT/'audit/massing_campus_edge_343e3d8/campus_edge_ndhm_analysis.json'
out.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
