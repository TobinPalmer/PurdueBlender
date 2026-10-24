import bpy
from pathlib import Path
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\campus_site.blend')
with bpy.data.libraries.load(str(p),link=False) as (src,dst):
 print('MATS',src.materials)
