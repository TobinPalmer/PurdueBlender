import bpy, json
from pathlib import Path
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
out={}
for n in ['SC_Win_East_Level3_ThirdFloor_0_BronzeFrame','SC_Win_East_Level2_SecondFloor_0_BronzeFrame','SC_Historic_Slate_Roof','SC_Classical_Entablature_Cornice']:
 o=bpy.data.objects.get(n)
 if not o:continue
 vs=[list(o.matrix_world@v.co) for v in o.data.vertices] if o.type=='MESH' else []
 out[n]={'type':o.type,'vertex_count':len(vs),'verts':[list(map(lambda x:round(x,3),v)) for v in vs[:500]],'faces':[list(poly.vertices) for poly in o.data.polygons] if o.type=='MESH' else [],'face_count':len(o.data.polygons) if o.type=='MESH' else None}
Path(r'audit/batch3_stanley/frame_mesh_r3.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print({k:(v['vertex_count'],v['face_count']) for k,v in out.items()})
