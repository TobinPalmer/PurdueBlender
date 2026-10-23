import sys,json,ast
sys.path.insert(0,'audit/walc_review/deps')
from shapely import Polygon,box,constrained_delaunay_triangles
s=open('modular/buildings/build_hicks_library.py').read();pts=ast.literal_eval(s.split('GIS_POLYGON_2D = ')[1].split('\n\n')[0]);origin=next(x for x in json.load(open('modular/manifest.json'))['assets'] if x['id']=='hicks_library')['placement_origin_xy_m']
r={}
for name,z,th,hole in [('HIKS_Roof_Gravel_Ballast_Deck',2.438,.18,(83,-321.5,93.5,-314.5)),('HIKS_FloorSlab_Ground_Subterranean',-5.304,.35,(84,-320.5,92.5,-315.5))]:
 p=Polygon(pts).difference(box(*hole));tris=constrained_delaunay_triangles(p);r[name]={'z':z,'th':th,'triangles':[[[x-origin[0],y-origin[1]] for x,y in t.exterior.coords][:3] for t in tris.geoms],'rings':[[[x-origin[0],y-origin[1]] for x,y in ring.coords] for ring in [p.exterior,*p.interiors]]}
json.dump(r,open('audit/batch2_hicks/slab_plan.json','w'))
