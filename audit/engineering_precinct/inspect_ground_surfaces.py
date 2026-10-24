import bpy
p=r'audit/engineering_precinct/engineering_mall_foliage_library_review.blend'
bpy.ops.wm.open_mainfile(filepath=p)
for o in bpy.data.objects:
 if any(k in o.name.lower() for k in ('way','grass','plaza','strip','drive','walk')):
  mats=[m.name if m else 'NONE' for m in (o.data.materials if hasattr(o.data,'materials') else [])]
  if o.type=='MESH':
   print(o.name, o.type, mats, 'slots',len(o.material_slots),'faces',len(o.data.polygons))
