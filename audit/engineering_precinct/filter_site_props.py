import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\campus_site.blend'
with bpy.data.libraries.load(p,link=False) as (src,dst):
 print([n for n in src.objects if any(k in n.lower() for k in ('bench','bollard','nozzle','lamp'))][:100])
