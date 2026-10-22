import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent/'deps'))
import shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
raw=json.loads((ROOT/'audit/walc_review/massing_geometry.json').read_text())
refs=json.loads((ROOT/'audit/official_building_references.json').read_text())['buildings']
m=json.loads((ROOT/'modular/manifest.json').read_text());byid={a['id']:a for a in m['assets']}
codes={'american_railway':'RAIL','brown_laboratory':'BRWN','chaney_hale':'CHAS','grissom':'GRIS','hall_of_data':'DSAI','house_1033674919':'FID888','materials_science':'MSEE','pierce_hall':'PRCE','psychological':'PSYC','wetherill':'WTHR','schleman':'SCHM'}
plan=[]
def entry(asset,code,z,new=False):
    bs=[b for b in refs if (b['fid']==888 if code=='FID888' else b['code']==code)]
    poly=unary_union([Polygon(b['rings_xy_m'][0],b['rings_xy_m'][1:]).buffer(0) for b in bs])
    triangles=shapely.constrained_delaunay_triangles(poly)
    if abs(sum(t.area for t in triangles.geoms)-poly.area)>.001:raise RuntimeError('triangle area mismatch')
    vs=[];index={};faces=[]
    def vi(x,y,zz):
        k=(float(x),float(y),float(zz))
        if k not in index:index[k]=len(vs);vs.append(k)
        return index[k]
    for t in triangles.geoms:
        cs=list(t.exterior.coords)[:-1]
        faces.append([vi(x,y,z[0]) for x,y in reversed(cs)])
        faces.append([vi(x,y,z[1]) for x,y in cs])
    for p in ([poly] if poly.geom_type=='Polygon' else poly.geoms):
        for ring in [p.exterior,*p.interiors]:
            cs=list(ring.coords)
            for (x,y),(xx,yy) in zip(cs,cs[1:]):faces.append([vi(x,y,z[0]),vi(xx,yy,z[0]),vi(xx,yy,z[1]),vi(x,y,z[1])])
    return {'id':asset['id'],'file':asset['file'],'collection':asset['collection'],'code':code,'fids':[b['fid'] for b in bs],'vertices':vs,'faces':faces,'footprint_area_m2':poly.area,'height_m':z[1]-z[0],'height_status':'retained source estimate; unverified','new':new}
for a in raw:
    code=next((code for token,code in codes.items() if token in a['id']),None)
    if code:plan.append(entry(byid[a['id']],code,a['z']))
for aid,code in [('dudley_hall','DUDL'),('lambertus_hall','LMBS')]:
    plan.append(entry({'id':aid,'file':f'buildings/{aid}.blend','collection':f'Asset_{aid}'},code,[0,16],True))
(ROOT/'audit/walc_review/massing_fix_plan.json').write_text(json.dumps(plan))
print('PLANNED',len(plan))
