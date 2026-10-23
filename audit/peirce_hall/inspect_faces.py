import bpy
from pathlib import Path
with bpy.data.libraries.load(str(Path(r'modular/buildings/massing_pierce_hall_prce_e5f59eb.blend').resolve()),link=False) as (src,dst): dst.objects=src.objects[:]
o=bpy.data.objects['Pierce Hall (PRCE)']
m=o.data
for i,v in enumerate(m.vertices): print('V',i,tuple(round(x,2) for x in v.co))
for i,f in enumerate(m.polygons): print('F',i,'mat',f.material_index,'verts',list(f.vertices))
