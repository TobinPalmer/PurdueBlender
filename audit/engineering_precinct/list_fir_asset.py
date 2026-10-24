import bpy
from pathlib import Path
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\foliage_library\source\fir_sapling\fir_sapling.blend')
with bpy.data.libraries.load(str(p),link=False) as (src,dst):
 print('COLLECTIONS',src.collections)
 print('OBJECTS',src.objects)
