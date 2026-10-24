import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\foliage_library\engineering_foliage_library.blend'
with bpy.data.libraries.load(p,link=False) as (src,dst): print(src.materials)
