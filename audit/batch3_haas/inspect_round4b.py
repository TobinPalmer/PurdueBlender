import bpy
from mathutils import Vector
c=bpy.data.collections['Asset_felix_haas_hall']
for o in c.objects:
 if o.name.startswith('HAAS_Estimated_Side_') or o.name.startswith('HAAS_Estimated_Long_') or 'Cupola' in o.name:
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)]
  print(o.name,[[round(v,2) for v in mn],[round(v,2) for v in mx]])
for m in ['Purdue_Red_Brick.001','Purdue_Red_Brick','HAAS_Photo_Limestone','HAAS_GooglePhotos_RedClayTiles_estimated']:
 x=bpy.data.materials.get(m);print('MAT',m,tuple(x.diffuse_color) if x else None)
 if x:
  for n in x.node_tree.nodes:
   if n.type=='TEX_BRICK':print('BRICK',dict((k,tuple(n.inputs[k].default_value) if hasattr(n.inputs[k].default_value,'__len__') else n.inputs[k].default_value) for k in ['Color1','Color2','Mortar','Scale','Mortar Size','Brick Width','Row Height']))
   if n.type=='BSDF_PRINCIPLED':print('BSDF',tuple(n.inputs['Base Color'].default_value),n.inputs['Roughness'].default_value)
