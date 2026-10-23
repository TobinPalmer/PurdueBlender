import bpy,json,math
from pathlib import Path
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/complete_potter';P=R/'modular/buildings/potter_engineering.blend';bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering']
def mat(n,col):
 m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*col,1);m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*col,1);return m
red=mat('POTR_2016_Lab205_RedOrange_Cabinets',(.42,.075,.025));black=mat('POTR_2016_Lab205_Dark_Worktop',(.025,.022,.02));grey=mat('POTR_2016_Lab205_Metal_DrawerHandles',(.3,.3,.3))
def box(n,loc,scale,ma):
 x,y,z=[v/2 for v in scale];me=bpy.data.meshes.new(n);me.from_pydata([(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)],[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.materials.append(ma);ob=bpy.data.objects.new(n,me);c.objects.link(ob);ob.location=loc;ob['evidence']='2016 study photo PDF220 room205; approximate placement from existing floorplan54 label, dimensions estimated';return ob
# Second-floor room205 label in the actual existing plan; apply recorded registration.
a=json.loads((D/'plan_registration.json').read_text())['54']['affine'];px,py=399.8,406.6;cx=a[0]*px+a[1]*py+a[4];cy=a[2]*px+a[3]*py+a[5];base=4.8768
for i in range(3):
 x=cx+(i-1)*.65;box('POTR_Historic2016_Lab205_BaseCabinet',(x,cy,base+.42),(.62,.65,.84),red)
 box('POTR_Historic2016_Lab205_Handle',(x,cy-.337,base+.68),(.24,.025,.025),grey)
box('POTR_Historic2016_Lab205_BenchTop',(cx,cy,base+.87),(2.05,.72,.06),black)
for i in range(3):box('POTR_Historic2016_Lab205_UpperCabinet',(cx+(i-1)*.65,cy+.2,base+1.9),(.62,.35,.65),red)
bpy.ops.wm.save_as_mainfile(filepath=str(P))
