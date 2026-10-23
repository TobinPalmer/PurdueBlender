import bpy,pathlib
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/hovde_hall.blend'));c=bpy.data.collections['Asset_hovde_hall']
for o in c.all_objects:
 if o.type=='MESH' and any(s in o.name for s in ('Wall','Facade','Base_','Roof','Footprint','HOVD_Root')):
  pts=[o.matrix_world@v.co for v in o.data.vertices]; b=[min(v[i] for v in pts) for i in range(3)]+[max(v[i] for v in pts) for i in range(3)];print(o.name,tuple(round(x,2) for x in b),len(o.data.polygons))
