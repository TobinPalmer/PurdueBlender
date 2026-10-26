from __future__ import annotations
import json
import math
import sys
from pathlib import Path
import numpy as np
import laspy
from pyproj import Transformer, CRS

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'audit' / 'massing_turf_recreation_exercise_center_9622f45'
SOURCES = AUDIT / 'sources'
LAS = SOURCES / 'indiana_2018_lidar_trec_tile_29951885_12.copc.laz'
GIS = SOURCES / 'purdue_gis_trec_oid312_2026-10-26.geojson'
OSM = SOURCES / 'osm_trec_way_283275002_2026-10-26.json'
FT_TO_M = 0.3048006096012192
CRS = CRS.from_epsg(2968)
TRANSFORM = Transformer.from_crs('EPSG:4326', CRS, always_xy=True)

def ring_gis():
    d=json.loads(GIS.read_text(encoding='utf-8-sig'))
    ll=d['features'][0]['geometry']['coordinates'][0][:-1]
    return np.array([TRANSFORM.transform(lon,lat) for lon,lat in ll])

def ring_osm():
    d=json.loads(OSM.read_text(encoding='utf-8-sig'))
    nodes={e['id']:e for e in d['elements'] if e['type']=='node'}
    way=next(e for e in d['elements'] if e['type']=='way')
    return np.array([TRANSFORM.transform(nodes[n]['lon'],nodes[n]['lat']) for n in way['nodes']])

def inside(x,y,p):
    # Vectorized ray casting; edges included in each segment's crossing rule.
    result=np.zeros(x.shape,dtype=bool)
    j=len(p)-1
    for i in range(len(p)):
        xi,yi=p[i]; xj,yj=p[j]
        hit=((yi>y)!=(yj>y)) & (x < (xj-xi)*(y-yi)/(yj-yi+1e-30)+xi)
        result ^= hit
        j=i
    return result

def stats(arr):
    a=np.asarray(arr)
    if not len(a): return {'count':0}
    return {'count':int(len(a)),'min_ft':float(np.min(a)),'p05_ft':float(np.percentile(a,5)),'median_ft':float(np.median(a)),'p95_ft':float(np.percentile(a,95)),'max_ft':float(np.max(a))}

gis,osm=ring_gis(),ring_osm()
all_xy=np.vstack([gis,osm]); minx,miny=np.min(all_xy,axis=0); maxx,maxy=np.max(all_xy,axis=0)
# 60 ft around both compared footprints for nearby ground classification.
buff=60
bounds=(minx-buff,miny-buff,maxx+buff,maxy+buff)
roof_gis=[]; roof_osm=[]; ground=[]
roof_profile_x=[]; roof_profile_z=[]
counts={'class6_in_gis':0,'class6_in_osm':0,'class2_in_ground_window':0}
class_hist_gis={}; class_hist_osm={}
with laspy.open(LAS) as f:
    header={'point_count':int(f.header.point_count),'point_format':str(f.header.point_format),'scales':list(map(float,f.header.scales)),'offsets':list(map(float,f.header.offsets)),'crs':str(f.header.parse_crs())}
    for chunk in f.chunk_iterator(1_000_000):
        x=np.asarray(chunk.x); y=np.asarray(chunk.y); z=np.asarray(chunk.z); c=np.asarray(chunk.classification)
        b=(x>=bounds[0])&(x<=bounds[2])&(y>=bounds[1])&(y<=bounds[3])
        if not np.any(b): continue
        x,y,z,c=x[b],y[b],z[b],c[b]
        is_gis=inside(x,y,gis); is_osm=inside(x,y,osm)
        bld=c==6; gr=c==2
        for code in np.unique(c[is_gis]): class_hist_gis[int(code)]=class_hist_gis.get(int(code),0)+int(np.sum(is_gis&(c==code)))
        for code in np.unique(c[is_osm]): class_hist_osm[int(code)]=class_hist_osm.get(int(code),0)+int(np.sum(is_osm&(c==code)))
        mg=bld&is_gis; mo=bld&is_osm
        # Some vendor point clouds leave roof returns unclassified. Exclude
        # only class 2 ground points when deriving the roof-height envelope.
        roof_gis.extend(z[is_gis & (c!=2)].tolist()); roof_osm.extend(z[is_osm & (c!=2)].tolist())
        roof_profile_x.extend(x[is_osm & (c!=2)].tolist())
        roof_profile_z.extend(z[is_osm & (c!=2)].tolist())
        counts['class6_in_gis']+=int(np.sum(mg)); counts['class6_in_osm']+=int(np.sum(mo))
        mgnd=gr&~is_osm
        ground.extend(z[mgnd].tolist()); counts['class2_in_ground_window']+=int(np.sum(mgnd))

out={'source':'2018 Indiana QL2 LAS 1.4, Tippecanoe Co tile in2018_29951885_12.copc.laz','source_tile':'EPSG:2968 NAD83(HARN) Indiana West US survey feet; vertical NAVD88 Geoid12B US survey feet','bounds_ft':list(bounds),'purdue_gis_perimeter_xy_ft':{'vertices':len(gis),'bbox':[float(gis[:,0].min()),float(gis[:,1].min()),float(gis[:,0].max()),float(gis[:,1].max())]},'osm_perimeter_xy_ft':{'vertices':len(osm),'bbox':[float(osm[:,0].min()),float(osm[:,1].min()),float(osm[:,0].max()),float(osm[:,1].max())]},'header':header,'counts':counts,'class_histogram_inside_perimeter':{'purdue_gis_ring':class_hist_gis,'osm_ring':class_hist_osm},'roof_non_ground_return_elevation_ft':{'purdue_gis_ring':stats(roof_gis),'osm_ring':stats(roof_osm)},'nearby_ground_class2_elevation_ft':stats(ground)}
# Convert roof and nearby ground quantiles to approximate height above surrounding ground.
ground_med=out['nearby_ground_class2_elevation_ft'].get('median_ft')
profile=[]
px=np.asarray(roof_profile_x); pz=np.asarray(roof_profile_z)
if len(px):
    edges=np.linspace(float(osm[:,0].min()),float(osm[:,0].max()),13)
    for i in range(len(edges)-1):
        sel=(px>=edges[i])&((px<edges[i+1]) if i<len(edges)-2 else (px<=edges[i+1]))
        if np.sum(sel):
            qs=np.percentile(pz[sel],[5,50,95])
            profile.append({'x_bin_ft':[float(edges[i]),float(edges[i+1])],'point_count':int(np.sum(sel)),'p05_height_above_ground_m':round((qs[0]-ground_med)*FT_TO_M,3),'median_height_above_ground_m':round((qs[1]-ground_med)*FT_TO_M,3),'p95_height_above_ground_m':round((qs[2]-ground_med)*FT_TO_M,3)})
out['osm_roof_cross_section_bins_east_to_west']=profile
for key in ['purdue_gis_ring','osm_ring']:
    r=out['roof_non_ground_return_elevation_ft'][key]
    if ground_med is not None and r.get('count'):
        r['height_above_nearby_ground_m']={q:round((r[q+'_ft']-ground_med)*FT_TO_M,3) for q in ['median','p95','max']}
    # Across-width elevation profile in five equal bands, using class-6 roof points.
# Write result to assigned audit folder.
(AUDIT/'lidar_height_analysis.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
