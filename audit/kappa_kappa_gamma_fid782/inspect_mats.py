import bpy,collections
ob=bpy.data.objects['House_301840871']; c=collections.Counter(p.material_index for p in ob.data.polygons);print([(i,m.name,c[i]) for i,m in enumerate(ob.data.materials)])
for p in ob.data.polygons:
 if p.center.z>9.5 and p.material_index>=6:
  print('top-face',p.material_index,ob.data.materials[p.material_index].name,tuple(round(x,2) for x in p.center), 'base',tuple(round(x,3) for x in next(n for n in ob.data.materials[p.material_index].node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value[:3]));
