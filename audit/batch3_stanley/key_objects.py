import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend')
for o in bpy.data.objects:
 if o.name in ['SC_Brick_Masonry_Exterior_Walls','SC_Portico_Classical_Pediment','SC_Portico_Molded_Arch','SC_Portico_Entablature','SC_Portico_3D_Text','SC_Main_Door_Left','SC_Main_Door_Right','SC_Main_Fanlight_Glass','SC_Portico_Porch_Slab','SC_Historic_Slate_Roof','SC_Foundation_Limestone_Plinth'] or 'Column_Shaft' in o.name:
  bb=[o.matrix_world @ Vector(c) for c in o.bound_box]
  print(o.name,'loc',tuple(round(v,2) for v in o.location),'bounds',tuple(round(min(v[i] for v in bb),2) for i in range(3)),tuple(round(max(v[i] for v in bb),2) for i in range(3)), 'mat', [m.name if m else None for m in o.data.materials] if o.type=='MESH' else '')
print('ASSET_ROOT',[(o.name,tuple(o.location),tuple(o.rotation_euler),tuple(o.scale)) for o in bpy.data.objects if o.name.startswith('AssetRoot')])
