"""Measure approximate ME roof surfaces in the 2018 Indiana QL2 DSM."""
from __future__ import annotations
import json, math, hashlib, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
DSM = AUDIT / 'indiana_3dep_2018_dsm_in2018_30001885_12.tif'
GIS_PATH = ROOT / 'audit/official_building_references.json'
OUT = AUDIT / 'mechanical_engineering_lidar_r2.json'
refs = json.loads(GIS_PATH.read_text(encoding='utf-8'))
features = {int(f['fid']): f for f in refs['buildings'] if int(f.get('fid', -1)) in (108, 857)}

def local_xy_to_lonlat(x, y):
    # Exact inverse of the documented local approximation at the origin.
    return (-86.9137 + x / (111412.84 * math.cos(math.radians(40.4274))),
            40.4274 + y / 111040.0)

def ring_to_projected(ring, raster_crs):
    ll = [local_xy_to_lonlat(x, y) for x, y in ring]
    xs, ys = transform('EPSG:4326', raster_crs,
                       [p[0] for p in ll], [p[1] for p in ll])
    return list(zip(xs, ys)), ll

with rasterio.open(DSM) as ds:
    arr = ds.read(1)
    results = {}
    for fid, feature in features.items():
        ring = feature['rings_xy_m'][0]
        projected, lonlat = ring_to_projected(ring, ds.crs)
        poly = {'type':'Polygon','coordinates':[projected + [projected[0]]]}
        mask = geometry_mask([poly], out_shape=arr.shape, transform=ds.transform,
                             invert=True, all_touched=False)
        vals = arr[mask & np.isfinite(arr) & (arr > 0)]
        if not len(vals):
            results[str(fid)] = {'error':'No DSM cell centers in the transformed GIS footprint'}
            continue
        # summarize 2D patches by a 6x6 grid to retain spatially distinguishable roof sections
        world = feature['rings_xy_m'][0]
        xmin, xmax = min(p[0] for p in world), max(p[0] for p in world)
        ymin, ymax = min(p[1] for p in world), max(p[1] for p in world)
        cells=[]
        for iy in range(6):
            for ix in range(6):
                cx=xmin+(ix+.5)*(xmax-xmin)/6
                cy=ymin+(iy+.5)*(ymax-ymin)/6
                # local coordinate -> projected raster pixel, sample a small neighborhood
                ll=local_xy_to_lonlat(cx,cy)
                px,py=transform('EPSG:4326',ds.crs,[ll[0]],[ll[1]])
                row,col=ds.index(px[0],py[0])
                if not (0<=row<ds.height and 0<=col<ds.width): continue
                # 5x5 pixel neighborhood; guard against the approximate center being outside the feature
                r0,r1=max(0,row-2),min(ds.height,row+3)
                c0,c1=max(0,col-2),min(ds.width,col+3)
                ys,xs=np.ogrid[r0:r1,c0:c1]
                vals5=arr[r0:r1,c0:c1]
                # Apply the whole footprint mask to avoid sampling irrelevant edges; retain neighborhood stats
                m5=mask[r0:r1,c0:c1] & np.isfinite(vals5) & (vals5>0)
                vv=vals5[m5]
                if vv.size:
                    cells.append({'grid_1based':[ix+1,iy+1], 'center_world_xy_m':[round(cx,3),round(cy,3)],
                                  'surface_elevation_ftUS_median':float(np.median(vv)),
                                  'surface_elevation_ftUS_p10_p90':[float(v) for v in np.percentile(vv,[10,90])],
                                  'valid_cells':int(vv.size)})
        # One center per footprint interior cell; source height values are US survey feet.
        bins=np.arange(math.floor(float(vals.min())),math.ceil(float(vals.max()))+1,1.0)
        counts, edges=np.histogram(vals,bins=bins)
        dominant=int(np.argmax(counts))
        results[str(fid)]={
            'name':feature['name'], 'code':feature['code'], 'gis_feature_id':fid,
            'official_polygon_center_xy_m':feature['official_polygon_center_xy_m'],
            'official_polygon_bounds_xy_m':feature['aabb_xy_m'],
            'registered_polygon_bounds_in_raster_units':[float(min(x for x,y in projected)),float(min(y for x,y in projected)),float(max(x for x,y in projected)),float(max(y for x,y in projected))],
            'cell_size_ft':[abs(float(ds.transform.a)),abs(float(ds.transform.e))],
            'sampled_cells_at_cell_centers':int(len(vals)),
            'elevation_ftUS_quantiles_p10_p25_p50_p75_p90_p95_p99_max':[float(x) for x in np.percentile(vals,[10,25,50,75,90,95,99,100])],
            'dominant_1ft_elevation_bin_ftUS':[float(edges[dominant]),float(edges[dominant+1])],
            'dominant_bin_share':float(counts[dominant]/len(vals)),
            'spatial_6x6_neighborhoods':cells,
            'transformed_ring_lonlat':[[float(lon),float(lat)] for lon,lat in lonlat],
            'interpretation':'DSM returns all elevated surfaces, including roofs, trees and possible rooftop equipment; this is not a surveyed roof elevation.'}
    # Sample the bare-earth service at GIS interior points for FID 857. This
    # separates the terrain datum from the DSM surface without claiming that
    # every above-ground return belongs to roof structure.
    main=features[857]
    ring=main['rings_xy_m'][0]
    xmin,xmax=min(p[0] for p in ring),max(p[0] for p in ring)
    ymin,ymax=min(p[1] for p in ring),max(p[1] for p in ring)
    def in_poly(x,y):
        hit=False
        for i,(x1,y1) in enumerate(ring):
            x2,y2=ring[(i+1)%len(ring)]
            if (y1>y)!=(y2>y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1: hit=not hit
        return hit
    samples=[]
    for iy in range(6):
        for ix in range(6):
            cx=xmin+(ix+.5)*(xmax-xmin)/6
            cy=ymin+(iy+.5)*(ymax-ymin)/6
            if not in_poly(cx,cy): continue
            lon,lat=local_xy_to_lonlat(cx,cy)
            px,py=transform('EPSG:4326',ds.crs,[lon],[lat])
            row,col=ds.index(px[0],py[0])
            r0,r1=max(0,row-2),min(ds.height,row+3)
            c0,c1=max(0,col-2),min(ds.width,col+3)
            window=arr[r0:r1,c0:c1]
            v=window[mask[r0:r1,c0:c1] & np.isfinite(window) & (window>0)]
            if v.size:
                samples.append({'grid_1based':[ix+1,iy+1],'world_xy_m':[round(cx,3),round(cy,3)],
                                'lonlat':[lon,lat],'dsm_local_neighborhood_median_ftUS':float(np.median(v))})
    def terrain_at(s):
        geom=json.dumps({'x':s['lonlat'][0],'y':s['lonlat'][1],
                         'spatialReference':{'wkid':4326}},separators=(',',':'))
        q=urllib.parse.urlencode({'geometry':geom,'geometryType':'esriGeometryPoint',
                                  'sr':'4326','returnGeometry':'false','f':'json'})
        url='https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2016_2020_DEM/ImageServer/identify?'+q
        with urllib.request.urlopen(url,timeout=30) as response: payload=json.load(response)
        return {**s,'bare_earth_dem_ftUS':float(payload['value'])}
    with ThreadPoolExecutor(max_workers=8) as pool:
        ground_samples=list(pool.map(terrain_at,samples))
    for s in ground_samples:
        s['surface_minus_terrain_ft']=s['dsm_local_neighborhood_median_ftUS']-s['bare_earth_dem_ftUS']
    vals_agl=np.array([s['surface_minus_terrain_ft'] for s in ground_samples],dtype=float)
    results['857']['dsm_surface_vs_bare_earth_grid']={
        'method':'6x6 grid over the approximate GIS FID 857 polygon; point-in-polygon filters to interior; each DSM value is a 5x5-cell neighborhood median masked to the polygon; bare-earth value is an Indiana 2016-2020 DEM ImageServer identify query at the same grid point.',
        'samples':ground_samples,
        'surface_minus_bare_earth_ft_quantiles_p10_p25_p50_p75_p90':[float(v) for v in np.percentile(vals_agl,[10,25,50,75,90])],
        'interpretation':'Spatial height variation is indicative only. Tree canopy, rooftop equipment, GIS edge offsets, and DEM interpolation under the building can affect local values.'}
    # Dedicated low-roof check at the small GIS feature's centroid. Its center
    # falls on a uniform DSM patch and is suitable for a coarse mass-height
    # estimate when paired with the bare-earth value at the same coordinate.
    small=features[108]
    sx,sy=small['official_polygon_center_xy_m']
    slon,slat=local_xy_to_lonlat(sx,sy)
    spx,spy=transform('EPSG:4326',ds.crs,[slon],[slat])
    sr,sc=ds.index(spx[0],spy[0])
    dsm_value=float(arr[sr,sc])
    ground=terrain_at({'local_xy_m':[sx,sy],'lonlat':[slon,slat]})
    agl_ft=dsm_value-ground['bare_earth_dem_ftUS']
    results['108']['centroid_height_check']={
        'gis_centroid_world_xy_m':[sx,sy], 'gis_centroid_lonlat':[slon,slat],
        'dsm_pixel_row_col':[int(sr),int(sc)],'dsm_pixel_size_ft':[abs(float(ds.transform.a)),abs(float(ds.transform.e))],
        'dsm_surface_elevation_ftUS':dsm_value,'bare_earth_dem_elevation_ftUS':ground['bare_earth_dem_ftUS'],
        'surface_above_bare_earth_ft':agl_ft,'surface_above_bare_earth_m':agl_ft*0.304800609601219,
        'bare_earth_source':'Indiana 2016-2020 DEM ImageServer identify at same FID108 centroid; 2.5-ft original pixel resolution and stated statewide 10 cm vertical/positional accuracy standard.',
        'interpretation':'One 5-ft DSM cell centered on the small polygon indicates a ~4.20 m surface above the bare-earth DEM. The cell is uniform with its 8 immediate neighbors (values 634.72–634.91 ftUS), making a low flat roof more likely than an isolated tree return. This is an approximate height, not a surveyed wall or parapet datum.'}
    result={
      'revision':2,
      'purpose':'Source registration and roof/height assessment; no geometry change is authorized by this result alone.',
      'dsm_source':{'provider':'Indiana Geographic Information Office / Indiana Statewide Elevation Catalog','title':'Indiana 2016-2020 QL2 3DEP LiDAR, 2018 Tippecanoe DSM tile in2018_30001885_12','acquisition_date':'2018-04-20','download_url':'https://giselevationingov.s3.us-east-2.amazonaws.com/dsmoptimized/statewide/2018/SPW/5ft/in2018_30001885_12.tif','catalog':'https://registry.opendata.aws/in-elevation/','product':'5-ft raster cells; floating elevation values in US survey feet; NAD83(HARN) / Indiana West (ftUS).','license':'CC0','local_file':str(DSM.relative_to(ROOT)),'sha256':hashlib.sha256(DSM.read_bytes()).hexdigest(),'crs':ds.crs.to_wkt(),'geotransform':[float(v) for v in ds.transform[:6]],'raster_shape_px':[int(ds.height),int(ds.width)],'nodata':ds.nodata},
      'footprint_source':{'provider':'Purdue campus GIS','feature_service':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','source_snapshot':str(GIS_PATH.relative_to(ROOT)),'feature_ids':[857,108],'source_crs':'EPSG:4326 transformed to project-local approximate XY as preserved in the GIS snapshot; transformed back to EPSG:4326 with project inverse formula, then to the DSM CRS with pyproj/rasterio','campus_xy_to_lonlat':'lon=-86.9137+x/(111412.84*cos(40.4274deg)); lat=40.4274+y/111040.0','uncertainty':'Projection is the project approximate campus tangent plane, not survey control; 5-ft DSM pixels may straddle GIS roof edges.'},
      'results':results,
      'terrain_source':{'provider':'Indiana Geographic Information Office','title':'Indiana 2016-2020 hydro-flattened bare-earth DEM (DTM)','url':'https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2016_2020_DEM/ImageServer','metadata':'https://www.arcgis.com/home/item.html?id=a95c857cb47649ec87b04810214b0c1c','resolution':'2.5 ft for most Indiana counties; 10 cm vertical/positional standards per publisher; service identify queried at the FID108 centroid and a 6x6 set of FID857 interior points.'},
      'limitations':['DSM is a surface model, not bare earth. Trees, rooftop equipment, parapets, and scan artifacts may contribute high returns.','One 2018 acquisition predates the 2023-2025 Gatewood renovation; it cannot establish current interior circulation.','The FID 108 polygon overlaps the larger FID 857 polygon in plan. Raster samples within overlap cannot distinguish duplicated registration from a distinct structure without the native GIS source semantics or orthophoto comparison.','No measured elevation drawing was located in the reviewed planning PDF; height derived from DSM is approximate and should not be assigned uniformly to every wing.']}
OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:{fid:{kk:vv for kk,vv in val.items() if kk not in ('spatial_6x6_neighborhoods','transformed_ring_lonlat')} for fid,val in v.items()} if k=='results' else v for k,v in result.items() if k!='results'} | {'results':{fid:{'sampled_cells_at_cell_centers':v.get('sampled_cells_at_cell_centers'),'elevation_ftUS_quantiles_p10_p25_p50_p75_p90_p95_p99_max':v.get('elevation_ftUS_quantiles_p10_p25_p50_p75_p90_p95_p99_max'),'dominant_1ft_elevation_bin_ftUS':v.get('dominant_1ft_elevation_bin_ftUS'),'dominant_bin_share':v.get('dominant_bin_share'),'spatial_6x6_neighborhoods':v.get('spatial_6x6_neighborhoods',[]) } for fid,v in results.items()}},indent=2))
