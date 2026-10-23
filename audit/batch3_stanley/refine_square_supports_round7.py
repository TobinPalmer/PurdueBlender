import bpy
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'; bpy.ops.wm.open_mainfile(filepath=p)
mat=bpy.data.materials.get('Bedford_Indiana_Limestone')
if mat and mat.use_nodes:
 bs=mat.node_tree.nodes.get('Principled BSDF')
 if bs: bs.inputs['Base Color'].default_value=(0.65,0.55,0.42,1); bs.inputs['Roughness'].default_value=0.76
 mat.diffuse_color=(0.65,0.55,0.42,1)
def box_rebuild(o, center, dims):
 cx,cy,cz=center;dx,dy,dz=[v/2 for v in dims]
 xyz=[(cx-dx,cy-dy,cz-dz),(cx+dx,cy-dy,cz-dz),(cx+dx,cy+dy,cz-dz),(cx-dx,cy+dy,cz-dz),(cx-dx,cy-dy,cz+dz),(cx+dx,cy-dy,cz+dz),(cx+dx,cy+dy,cz+dz),(cx-dx,cy+dy,cz+dz)]
 faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 inv=o.matrix_world.inverted(); verts=[inv@Vector(v) for v in xyz]
 mesh=bpy.data.meshes.new(o.name+'_SquareRebuild');mesh.from_pydata(verts,[],faces);mesh.materials.append(mat);mesh.update();old=o.data;o.data=mesh
 if old.users==0:bpy.data.meshes.remove(old)
for idx in (0,3):
 for part, height, width in [('Plinth',0.52,0.48),('Shaft',4.5,0.34),('Capital',0.28,0.48)]:
  o=bpy.data.objects[f'SC_Portico_Column_{part}_{idx}']
  pts=[o.matrix_world@Vector(c) for c in o.bound_box]; lo=[min(p[i] for p in pts) for i in range(3)]; hi=[max(p[i] for p in pts) for i in range(3)]
  cx=(lo[0]+hi[0])/2; cy=(lo[1]+hi[1])/2; cz=(lo[2]+hi[2])/2
  # front-face square supports: broad enough to read in the photo but not classical round columns
  box_rebuild(o,(cx,cy,cz),(width,width,height))
scene=bpy.context.scene
scene['Entry architecture edit']='Round classical shafts replaced with modest square limestone supports and reduced limestone/walk widths; current exterior photo indicates a rectangular entry surround. Support dimensions estimated.'
bpy.ops.wm.save_as_mainfile(filepath=p); print('updated square supports')
