import bpy
from pathlib import Path
for a in ('grass_ground','asphalt_01'):
 p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\foliage_library\source')/a/f'{a}.blend'
 with bpy.data.libraries.load(str(p),link=False) as (src,dst): print(a,src.materials,src.objects)
