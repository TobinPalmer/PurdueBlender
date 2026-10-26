import bpy,json
from pathlib import Path
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
out={}
for n in ['SC_Portico_Balustrade_North','SC_Portico_Balustrade_South','SC_Portico_Pedestal_North','SC_Portico_Pedestal_South','SC_Portico_Rectangular_Stone_Portal_Surround','SC_Portico_Porch_Slab']:
 o=bpy.data.objects.get(n)
 if not o:continue
 out[n]={'verts':[[round(c,3) for c in (o.matrix_world@v.co)] for v in o.data.vertices],'faces':[list(poly.vertices) for poly in o.data.polygons]}
Path(r'audit/batch3_stanley/portico_mesh_r3.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print({n:len(v['verts']) for n,v in out.items()})
