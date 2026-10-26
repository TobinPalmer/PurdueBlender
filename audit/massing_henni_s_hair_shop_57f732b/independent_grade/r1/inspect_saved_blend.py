import bpy,json,math
from mathutils import Vector
blend=r'modular/buildings/massing_henni_s_hair_shop_57f732b.blend'; bpy.ops.wm.open_mainfile(filepath=blend)
scene=bpy.context.scene; objects=[]
for o in scene.objects:
  data={'name':o.name,'type':o.type,'matrix_world':[[float(x) for x in row] for row in o.matrix_world]}
  if o.type=='MESH':
    dg=bpy.context.evaluated_depsgraph_get(); oe=o.evaluated_get(dg); me=oe.to_mesh()
    pts=[oe.matrix_world@Vector(corner) for corner in oe.bound_box]
    data.update({'vertices':len(me.vertices),'faces':len(me.polygons),'evaluated_vertices':len(me.vertices),'evaluated_faces':len(me.polygons),'dimensions_local':[float(x) for x in o.dimensions],'bounds_world_m':[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)],'modifiers':[m.name for m in o.modifiers],'material_slots':[m.name if m else None for m in me.materials]})
    base=[]
    for v in me.vertices:
      p=oe.matrix_world@v.co
      if abs(p.z)<1e-5: base.append((round(p.x,6),round(p.y,6)))
    data['base_vertices_z0_unique_xy']=[list(x) for x in sorted(set(base))]
    oe.to_mesh_clear()
  if o.type=='CURVE': data['curve_text']=getattr(o.data,'body',None)
  objects.append(data)
images=[{'name':i.name,'filepath':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images]
result={'reopened_file':blend,'scene':scene.name,'scenes':[s.name for s in bpy.data.scenes],'collections':[{'name':c.name,'objects':[o.name for o in c.objects]} for c in bpy.data.collections],'objects':objects,'linked_libraries':[lib.filepath for lib in bpy.data.libraries],'images':images,'materials':[m.name for m in bpy.data.materials]}
json.dump(result,open(r'audit/massing_henni_s_hair_shop_57f732b/independent_grade/r1/direct_inspection.json','w'),indent=2)
