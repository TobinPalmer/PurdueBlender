import bpy
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
o=bpy.data.objects['SC_Portico_Entablature'];material=bpy.data.materials['Bedford_Indiana_Limestone']
boxes=[((28.15,-6.12,7.10),(30.35,-1.82,7.65))]
verts=[];faces=[];inv=o.matrix_world.inverted()
for (x0,y0,z0),(x1,y1,z1) in boxes:
 coords=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
 verts.extend([tuple(inv@Vector(v)) for v in coords]);n=len(verts)-8
 faces.extend([tuple(n+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
me=bpy.data.meshes.new('SC_Portico_Entablature_FixedLocalMesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update();old=o.data;o.data=me
if old.users==0:bpy.data.meshes.remove(old)
t=bpy.data.objects['SC_Portico_3D_Text'];t.scale.x=0.78
bpy.context.view_layer.update()
pts=[o.matrix_world@Vector(c) for c in o.bound_box]
print('ENT_BOUNDS',[tuple(min(v[i] for v in pts) for i in range(3)),tuple(max(v[i] for v in pts) for i in range(3))],'text scale',list(t.scale))
bpy.ops.wm.save_as_mainfile(filepath=p)
