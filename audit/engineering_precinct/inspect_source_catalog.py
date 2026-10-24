import bpy
from pathlib import Path
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
for rel in ['foliage_library/source/tree_small_02/tree_small_02.blend','foliage_library/source/shrub_02/shrub_02.blend','foliage_library/source/shrub_04/shrub_04.blend','foliage_library/source/fern_02/fern_02.blend','foliage_library/source/grass_medium_01/grass_medium_01.blend']:
 p=root/'modular'/'site'/rel
 print('\nFILE',p)
 with bpy.data.libraries.load(str(p),link=False) as (src,dst):
  print('collections', [x for x in src.collections if ('geometry' in x or '_LOD2' in x or x in ('fern_02',))][:15])
  names=[n for n in src.objects if ('trunk' in n or '_LOD1' in n and 'leaves' in n or '_LOD2' in n)]
  print('obj candidates',names[:30])
