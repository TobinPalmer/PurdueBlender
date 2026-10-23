import bpy,pathlib,json
p=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');bpy.ops.wm.open_mainfile(filepath=str(p/'modular/buildings/hovde_hall.blend'))
c=bpy.data.collections['Asset_hovde_hall']
for o in c.all_objects:
 if o.type=='MESH' and ('Footprint' in o.name or 'Bridge' in o.name or 'Walkway' in o.name or 'ELLT' in o.name or 'Entrance' in o.name or 'Stair' in o.name or 'Hovde' in o.name):
  coords=[o.matrix_world@v.co for v in o.data.vertices] if o.data.vertices else []
  bounds=([min(v[i] for v in coords) for i in range(3)]+[max(v[i] for v in coords) for i in range(3)]) if coords else []
  print(o.name,'dim',tuple(round(v,2) for v in o.dimensions),'loc',tuple(round(v,2) for v in o.location),'bounds',tuple(round(v,2) for v in bounds),'faces',len(o.data.polygons))
