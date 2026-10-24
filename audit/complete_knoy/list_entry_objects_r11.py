import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
for o in sorted(bpy.data.collections['Asset_knoy_hall'].objects,key=lambda x:x.name):
 if any(k in o.name.lower() for k in ['entr','plaza','landscape','stair','wall','planter','ramp','door','sidewalk','entry','canopy']):
  print(o.name, o.type, 'world', tuple(round(x,2) for x in o.matrix_world.translation), 'verts',len(o.data.vertices) if o.type=='MESH' else '')
