import bpy,json
from pathlib import Path
master=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend')
out=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\purdue_memorial_union_independent_grade\master_marker_readonly.json')
found={}
with bpy.data.libraries.load(str(master),link=True) as (src,dst):
 names=[n for n in src.objects if 'purdue_memorial_union' in n.lower() or 'memorial_union' in n.lower()]
 markers=[n for n in src.objects if n=='Placement_purdue_memorial_union']
 dst.objects=markers
objs=[o for o in dst.objects if o]
for o in objs:
 found={'name':o.name,'location':list(o.location),'rotation_euler':list(o.rotation_euler),'scale':list(o.scale),'instance_collection':o.instance_collection.name if o.instance_collection else None}
 if o.instance_collection:
  found['instance_collection_library']=o.instance_collection.library.filepath if o.instance_collection.library else None
 found['matrix_world']=[list(row) for row in o.matrix_world]
rep={'marker_objects':found,'master_named_object_blocks':names,'marker_count_named':len(markers)}
out.write_text(json.dumps(rep,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rep,indent=2))
