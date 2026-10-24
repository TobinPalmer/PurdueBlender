import bpy
from pathlib import Path
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
for x in ['tree_small_02','shrub_02','shrub_04','fern_02','grass_medium_01']:
 p=root/'modular'/'site'/'foliage_library'/'source'/x/(x+'.blend')
 with bpy.data.libraries.load(str(p),link=False) as (src,dst):
  names=[n for n in src.collections if ('LOD' in n or n==x)]
  dst.collections=names
 print('\nASSET',x)
 for c in dst.collections:
  print('COLL',c.name,'objects',len(c.all_objects))
  for ob in c.all_objects:
   if ob.type=='MESH':
    tris=sum(len(poly.vertices)-2 for poly in ob.data.polygons)
    if tris>10000 or ob.name in (x+'_LOD1',x+'_LOD2',x+'_LOD3'):
     print('  ',ob.name, tris,'dims',tuple(round(v,2) for v in ob.dimensions))
