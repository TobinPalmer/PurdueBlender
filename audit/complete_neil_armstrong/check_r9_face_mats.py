import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
for name in ['ARMS_R5_Coarse_LiDAR_wing_low','ARMS_R5_Coarse_LiDAR_wing_mid','ARMS_R5_Coarse_LiDAR_roof_high']:
 o=bpy.data.objects[name]
 m={}
 for p in o.data.polygons:
  n=p.normal
  key=o.data.materials[p.material_index].name if p.material_index<len(o.data.materials) else 'NONE'
  row=m.setdefault(key,{'faces':0,'upward_faces':0,'area':0.0,'upward_area':0.0})
  row['faces']+=1;row['area']+=p.area
  if n.z>.75:row['upward_faces']+=1;row['upward_area']+=p.area
 print(name,json.dumps(m))
