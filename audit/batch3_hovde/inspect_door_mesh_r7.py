import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend')
for n in ['HOVD_Door_Frame_1','HOVD_Door_Frame_2','HOVD_Door_Frame_3','HOVD_Door_Bronze_1','HOVD_Wall_East']:
 o=bpy.data.objects[n]; print(n,o.type,len(o.data.vertices) if o.type=='MESH' else None,len(o.data.polygons) if o.type=='MESH' else None,o.data.name)
 if o.type=='MESH':
  print(' verts sample',[(tuple(round(v.co[j],3) for j in range(3))) for v in o.data.vertices[:12]])
