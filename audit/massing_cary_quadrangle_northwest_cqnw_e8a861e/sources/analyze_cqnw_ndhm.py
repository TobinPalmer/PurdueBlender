"""Reproducibly sample the 2018 NDHM inside the CQNW GIS footprint."""
import json, math
from pathlib import Path
import numpy as np
import pyproj
import tifffile
from shapely.geometry import Point, Polygon

HERE=Path(__file__).resolve().parent
GEOJSON=HERE/'purdue_building_shapes_fid647_2026-10-26.geojson'
RASTER=HERE/'in2018_29951885_12_ndhm.tif'
OUT=HERE/'../cqnw_ndhm_analysis.json'

def main():
    feature=json.loads(GEOJSON.read_text(encoding='utf-8'))['features'][0]
    ring=feature['geometry']['coordinates'][0]
    transformer=pyproj.Transformer.from_crs(4326,2968,always_xy=True)
    footprint=Polygon([transformer.transform(lon,lat) for lon,lat in ring])
    raster=np.squeeze(tifffile.imread(RASTER))
    values=[]
    for row in range(raster.shape[0]):
        y=1890000-(row+0.5)*5
        for col in range(raster.shape[1]):
            x=2995000+(col+0.5)*5
            if footprint.contains(Point(x,y)):
                value=float(raster[row,col])
                if math.isfinite(value) and 0<=value<200:
                    values.append(value)
    p10,median,p90=np.percentile(values,[10,50,90])
    result={'provider':'Purdue Geospatial Data Science Lab / Indiana Digital Forestry','source_url':'https://giselevationingov.s3.us-east-2.amazonaws.com/ndhmoptimized/statewide/2018/SPW/5ft/in2018_29951885_12_ndhm.tif','source_epoch':'2018 LiDAR collection','crs':'EPSG:2968 NAD83(HARN) / Indiana West (ftUS)','resolution_ft':5,'sample_count':len(values),'percentiles_ft':{'p10':float(p10),'median':float(median),'p90':float(p90)},'percentiles_m':{'p10':float(p10*1200/3937),'median':float(median*1200/3937),'p90':float(p90*1200/3937)},'measurement_method':'Transform FID 647 WGS84 polygon to EPSG:2968 and sample raster pixel centers strictly inside. Tile origin 2,995,000 ftUS, 1,890,000 ftUS, pixel size 5 ft.','uncertainty':'Normalized surface height is not a surveyed wall/eave/ridge height; canopy and edge mixed pixels remain possible.'}
    OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
