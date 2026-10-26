import bpy,json
from mathutils import Vector
p=r'modular/buildings/massing_hi_vine_dbdf0c5.blend'; bpy.ops.wm.open_mainfile(filepath=p)
scene=bpy.context.scene
objs=[]
for o in scene.objects:
 if o.type=='MESH':
  bb=[o.matrix_world@Vector(v) for v in o.bound_box]
  geom=[[min(v[i] for v in bb),max(v[i] for v in bb)] for i in range(3)]
  bottom=[]
  if o.data.polygons:
   poly=min(o.data.polygons,key=lambda f:sum((o.matrix_world@o.data.vertices[i].co).z for i in f.vertices)/len(f.vertices))
   bottom=[[float((o.matrix_world@o.data.vertices[i].co).x),float((o.matrix_world@o.data.vertices[i].co).y)] for i in poly.vertices]
  objs.append({'name':o.name,'type':o.type,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'bounds_world_m':geom,'modifiers':[m.name for m in o.modifiers],'materials':[m.name if m else None for m in o.data.materials],'bottom_ring_xy':bottom,'custom_properties':{k:o[k] for k in o.keys()}})
result={'asset':p,'scene':scene.name,'scenes':[s.name for s in bpy.data.scenes],'collections':[c.name for c in bpy.data.collections],'scene_collection_children':[c.name for c in scene.collection.children],'objects':[{'name':o.name,'type':o.type} for o in scene.objects],'mesh_objects':objs,'linked_libraries':[l.filepath for l in bpy.data.libraries],'image_paths':[i.filepath for i in bpy.data.images if i.filepath and not i.packed_file]}
json.dump(result,open(r'audit/massing_hi_vine_dbdf0c5/review/reopen_asset_facts_r1.json','w'),indent=2)

