import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/rawls_hall.blend');bpy.context.view_layer.update()
for o in bpy.data.objects:
 if o.type=='MESH' and ('South' in o.name or 'North_Windows' in o.name or 'Glass' in o.name or 'Mullions' in o.name):
  p=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box]
  b=[[round(min(v[i] for v in p),3),round(max(v[i] for v in p),3)] for i in range(3)]
  print(o.name,'bounds',b,'parent',o.parent.name if o.parent else None,'inv',tuple(round(o.matrix_parent_inverse[i][3],3) for i in range(3)),'mats',[m.name if m else None for m in o.data.materials], 'quads',len(o.data.polygons))
for m in bpy.data.materials:
 if 'Glass' in m.name or 'Curtain' in m.name:
  print('MAT',m.name,'method',m.surface_render_method,'diff',list(m.diffuse_color))
