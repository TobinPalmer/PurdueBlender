import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modular/buildings/rawls_hall.blend'));g=bpy.data.objects['RAWL_SE_Diagonal_CurtainWall_Glass'];w=bpy.data.objects['RAWL_Masonry_Exterior_Walls'];p0=w.matrix_world@w.data.vertices[19].co;p1=w.matrix_world@w.data.vertices[20].co;axis=(p1-p0).normalized();rows=[]
for p in g.data.polygons:
 pts=[g.matrix_world@g.data.vertices[i].co for i in p.vertices];u=[(q-p0).dot(axis) for q in pts];z=[q.z for q in pts];rows.append({'face':p.index,'u':[round(min(u),4),round(max(u),4)],'z':[round(min(z),4),round(max(z),4)],'center_u':round(sum(u)/4,3),'center_z':round(sum(z)/4,3)})
print('pane_count',len(rows),'u_len', (p1-p0).length);print(json.dumps(rows,indent=2))
