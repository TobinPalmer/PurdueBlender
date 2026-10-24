import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\campus_site.blend'
with bpy.data.libraries.load(p,link=False) as (src,dst): print('OBJECTS',src.objects)
