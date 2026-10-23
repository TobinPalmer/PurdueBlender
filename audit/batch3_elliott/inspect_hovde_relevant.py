import bpy,pathlib
p=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');bpy.ops.wm.open_mainfile(filepath=str(p/'modular/buildings/hovde_hall.blend'));c=bpy.data.collections['Asset_hovde_hall']
for o in c.all_objects:
 n=o.name.lower()
 if any(s in n for s in ['bridge','walk','entry','entrance','door','footprint','roof','lobby','atrium','connector']):
  coords=[o.matrix_world@v.co for v in o.data.vertices] if o.type=='MESH' else []
  b=([min(v[i] for v in coords) for i in range(3)]+[max(v[i] for v in coords) for i in range(3)]) if coords else []
  print(o.name,'dim',tuple(round(v,2) for v in o.dimensions),'bounds',tuple(round(v,2) for v in b) if b else '')
