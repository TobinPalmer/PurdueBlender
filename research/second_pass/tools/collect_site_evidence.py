"""Collect real GIS/aerial/tile evidence, optionally spatially cropped point data.

python collect_site_evidence.py mechanical_engineering [--crop]
Requires numpy, pyproj, shapely; --crop also requires laspy[lazrs,requests].
No model creation. Remote images/data retain original provider licensing.
"""
from pathlib import Path
import sys,json,urllib.request,urllib.parse,hashlib,datetime,copy,math
import numpy as np
from pyproj import Transformer
from shapely.geometry import Polygon
from shapely.ops import unary_union,transform
from shapely import contains_xy
D=Path(__file__).resolve().parents[1]
building=sys.argv[1];S=D/'buildings'/building/'sources';S.mkdir(parents=True,exist_ok=True)
row=next(x for x in json.loads((D/'shared/official_location_matches.json').read_text()) if x['building_id']==building)
identity_path=S/'reviewed_identity.json'
if identity_path.exists():
    # Building-specific research can resolve an alias missed by ranking's name join.
    reviewed=json.loads(identity_path.read_text(encoding='utf-8'))
    assert reviewed['building_id']==building and reviewed.get('identity_evidence_urls') and reviewed.get('review_basis')
    snapshot=D/'shared/official_purdue_buildings_wgs84_snapshot.json'
    assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==reviewed['source_snapshot_sha256']
    official={f['attributes']['FID']:f for f in json.loads(snapshot.read_text())['features']}
    assert reviewed['feature_ids']==[f['attributes']['FID'] for f in reviewed['raw_features']]
    assert all(f==official[f['attributes']['FID']] for f in reviewed['raw_features']), 'Reviewed geometry must retain exact official source features'
    row=reviewed
assert row['status']=='matched','Resolve identity/footprint before treating data as building-specific'
features=row['raw_features'];poly=unary_union([Polygon(f['geometry']['rings'][0]) for f in features]);bbox=poly.bounds
(S/'purdue_footprint.json').write_text(json.dumps({'provider':'Purdue University GIS','source_crs':'EPSG4326','snapshot_provenance':'../../../shared/location_source_provenance.json','features':features},indent=2)+'\n')
envelope={'xmin':bbox[0]-.00012,'ymin':bbox[1]-.00012,'xmax':bbox[2]+.00012,'ymax':bbox[3]+.00012,'spatialReference':{'wkid':4326}}
tile_url='https://gisdata.in.gov/server/rest/services/Indiana_Statewide_3DEP_Lidar_Dates/MapServer/4/query?'+urllib.parse.urlencode({'f':'pjson','where':'1=1','geometry':json.dumps(envelope),'geometryType':'esriGeometryEnvelope','inSR':4326,'spatialRel':'esriSpatialRelIntersects','outFields':'*','returnGeometry':'true','outSR':4326})
records=[]
def fetch(name,url):
    p=S/name
    if not p.exists():
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=45) as response:p.write_bytes(response.read())
    records.append({'file':name,'url':url,'retrieved':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    return p.read_bytes()
tiles=json.loads(fetch('lidar_delivery_tiles.json',tile_url));assert 'error' not in tiles,tiles
# Public orthographic context; export response includes actual geographic extent.
ext=[bbox[0]-.00035,bbox[1]-.00025,bbox[2]+.00035,bbox[3]+.00025]
aerial_url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?'+urllib.parse.urlencode({'f':'pjson','bbox':','.join(map(str,ext)),'bboxSR':4326,'imageSR':3857,'size':'1400,1400','format':'png32'})
export=json.loads(fetch('aerial_export.json',aerial_url))
if not export.get('href'):
    # Tiny sites can exceed World Imagery's supported export detail; widen context.
    cx=(bbox[0]+bbox[2])/2;cy=(bbox[1]+bbox[3])/2
    wide=[cx-.00125,cy-.001,cx+.00125,cy+.001]
    aerial_url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?'+urllib.parse.urlencode({'f':'pjson','bbox':','.join(map(str,wide)),'bboxSR':4326,'imageSR':3857,'size':'1200,1200','format':'png32'})
    export=json.loads(fetch('aerial_export_wide.json',aerial_url))
assert export.get('href'),export
fetch('aerial_world_imagery.png',export['href'])
summary=[]
for f in tiles.get('features',[]):
    attrs=f['attributes'];stem=attrs['Text'];date=datetime.datetime.fromtimestamp(attrs['Field4']/1000,datetime.timezone.utc).date().isoformat() if attrs.get('Field4') else None
    year=str(attrs['Project']);urls=[];metadata=None
    # Prefix observed in Indiana's public COPC listing; record failures explicitly.
    for candidate in (stem,stem.lower(),stem.upper()):
        url=f'https://giselevationingov.s3.amazonaws.com/copc/statewide/{year}/SPW/ql2/{candidate}.copc.laz'
        try:metadata=json.loads(fetch(candidate+'.copc.metadata.json',url.replace('.laz','.metadata.json')));break
        except Exception as e:urls.append({'url':url,'metadata_error':str(e)})
    info={'source_tile':stem,'acquisition_date_from_state_index':date,'source_url':url if metadata else None,'failed_candidates':urls,'point_crop_status':'Not requested'}
    if metadata is not None and '--crop' in sys.argv:
        import laspy
        from laspy.copc import Bounds
        from laspy.vlrs.vlrlist import VLRList
        with laspy.CopcReader.open(url,http_num_threads=4) as reader:
            crs=reader.header.parse_crs();forward=Transformer.from_crs(4326,crs,always_xy=True)
            corners=[forward.transform(x,y) for x in (envelope['xmin'],envelope['xmax']) for y in (envelope['ymin'],envelope['ymax'])]
            pts=reader.query(Bounds(np.min(corners,axis=0),np.max(corners,axis=0)))
            head=copy.deepcopy(reader.header);head.vlrs=VLRList([v for v in head.vlrs if v.user_id!='copc']);head.evlrs=None
            las=laspy.LasData(head);las.points=pts
            target=D/'buildings'/building/'data/lidar';target.mkdir(parents=True,exist_ok=True);dest=target/(stem+'.'+building+'_clip.laz');las.write(dest)
            px=transform(forward.transform,poly);factor=crs.axis_info[0].unit_conversion_factor
            cls=np.asarray(pts.classification);zs=np.asarray(pts.z);xs=np.asarray(pts.x);ys=np.asarray(pts.y)
            inside=contains_xy(px,xs,ys);ground=zs[(cls==2)&~inside];roof=zs[contains_xy(px.buffer(-1/factor),xs,ys)&(cls==1)]
            info.update(point_crop_status='Downloaded full-resolution spatial query; regular LAZ, COPC hierarchy removed',point_count=len(pts),points_inside_footprint=int(inside.sum()),class_counts={str(int(k)):int(v) for k,v in zip(*np.unique(cls,return_counts=True))},crs_wkt=crs.to_wkt(),crs_name=crs.name,axis_units=[{'name':a.name,'unit':a.unit_name,'factor_to_m':a.unit_conversion_factor} for a in crs.axis_info],clip_repository_path=str(dest.relative_to(D/'buildings'/building)).replace('\\','/'),clip_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),ground_class2_outside_footprint_median_native=float(np.median(ground)) if len(ground) else None,inside_eroded_footprint_class1_count=len(roof),candidate_return_heights_above_local_ground_m_p50_p90_p99=np.percentile((roof-np.median(ground))*factor,[50,90,99]).tolist() if len(roof) and len(ground) else None,limitations='Return statistics are not measured eave/ridge heights. Class1 includes non-roof objects. Compound CRS and vertical datum retained; facade/window geometry cannot be inferred from airborne cloud. No model/placement changes.')
    summary.append(info);print(json.dumps({k:v for k,v in info.items() if k not in ('crs_wkt','failed_candidates')}),flush=True)
(S/'site_download_index.json').write_text(json.dumps(records,indent=2)+'\n')
(S/'lidar_crop_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Footprint feature IDs:',row['feature_ids'],'Envelope:',envelope)
