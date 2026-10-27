import bpy, json, os
from mathutils import Vector
asset_id='massing_house_970455277_a3fb72a'
s=bpy.data.scenes['Building_'+asset_id]
c=bpy.data.collections['Asset_'+asset_id]
print('SCENE OBJECT COUNT',len(s.objects),'SCENE ROOT COLLECTION',s.collection.name)
print('SCENE CHILD COLLECTIONS',[x.name for x in s.collection.children])
for name in ['AOII_Garage_Slab','AOII_Level_1_Slab','AOII_Level_2_Slab','AOII_Roof_Deck','AOII_Flat_Roof_Membrane','AOII_Entry_Path']:
 o=bpy.data.objects.get(name)
 if o:
  print(name,'verts',[(round((o.matrix_world@v.co).x,4),round((o.matrix_world@v.co).y,4),round((o.matrix_world@v.co).z,4)) for v in o.data.vertices[:20]],'mats',[m.name for m in o.data.materials])
print('EXAMPLE NAMES:')
for o in list(c.all_objects)[:40]:
 print(o.name,o.type,tuple(round(x,3) for x in o.dimensions),[m.name for m in o.data.materials] if o.type=='MESH' else '')
