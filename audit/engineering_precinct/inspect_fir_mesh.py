import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\foliage_library\source\fir_sapling\fir_sapling.blend'
with bpy.data.libraries.load(p,link=False) as (src,dst): dst.objects=list(src.objects)
for o in dst.objects: print(o.name,len(o.data.polygons),len(o.data.vertices),tuple(round(x,3) for x in o.dimensions))
