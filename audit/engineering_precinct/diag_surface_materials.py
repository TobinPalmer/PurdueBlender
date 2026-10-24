import bpy
bpy.ops.wm.open_mainfile(filepath=r'audit/engineering_precinct/engineering_mall_foliage_library_review.blend')
for n in ['HOVD_Plaza_Paving','Preview_Fountain_Plaza_Concentric_Brick_Ring']:
 o=bpy.data.objects.get(n)
 if o:
  from mathutils import Vector
  pts=[o.matrix_world@Vector(c) for c in o.bound_box]
  print(n,tuple(round(min(p[i] for p in pts),2) for i in range(3)),tuple(round(max(p[i] for p in pts),2) for i in range(3)),[m.name for m in o.data.materials])
for n in ['Engineering_Mall_Walkway_Concrete_Textured','Engineering_Mall_Plaza_Pavers_Textured','Engineering_Mall_Mown_Grass_Textured']:
 m=bpy.data.materials.get(n)
 print('\nMATERIAL',n,'diff',tuple(round(x,3) for x in m.diffuse_color))
 for node in m.node_tree.nodes:
  if node.type in ('TEX_NOISE','TEX_BRICK','BUMP','TEX_COORD','VALTORGB'):
   print(node.name,node.type,[(i.name,tuple(round(x,4) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,4)) for i in node.inputs if i.name in ('Scale','Distance','Strength','Detail','Brick Width','Row Height')])
