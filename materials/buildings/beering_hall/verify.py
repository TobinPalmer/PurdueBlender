import bpy,json,os
from mathutils import Vector
p=os.path.abspath('modular/buildings/beering_hall.blend');b=os.path.abspath('materials/buildings/beering_hall/before.blend')
def sig():
 c=bpy.data.collections['Asset_beering_hall'];return {o.name:{'matrix':[list(x) for x in o.matrix_world],'verts':len(o.data.vertices) if o.type=='MESH' else None,'polys':len(o.data.polygons) if o.type=='MESH' else None} for o in c.all_objects}
bpy.ops.wm.open_mainfile(filepath=b);before=sig();bpy.ops.wm.open_mainfile(filepath=p);after=sig()
r={'exported_collection':'Asset_beering_hall','objects_before':len(before),'objects_after':len(after),'geometry_and_transforms_unchanged':all(after.get(k)==v for k,v in before.items()),'file_images':[{'name':i.name,'packed':bool(i.packed_file),'path':i.filepath} for i in bpy.data.images if i.source=='FILE'],'materials':len(bpy.data.materials)}
assert all(after.get(k)==v for k,v in before.items())
assert all(i['packed'] for i in r['file_images'])
open('materials/buildings/beering_hall/verification.json','w').write(json.dumps(r,indent=2));print(json.dumps(r))

