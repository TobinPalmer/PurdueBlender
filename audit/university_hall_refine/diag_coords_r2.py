import bpy,json
p='modular/buildings/university_hall.blend'
for n in ['UNIV_Mansard_Roof_Core','UNIV_Mansard_Roof_Deck','UNIV_Roof_WroughtIron_Cresting','UNIV_Dormer_Body_East_-250','UNIV_Tower_Brick_Shaft','UNIV_Belfry_Roof_Slab']:
 o=bpy.data.objects.get(n)
 if o:
  pts=[o.matrix_world @ v.co for v in o.data.vertices]
  b=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
  print(n,'loc',list(o.location),'world',list(o.matrix_world.translation),'bounds',b,'scale',list(o.scale),'parentinv',list(o.matrix_parent_inverse.translation))
