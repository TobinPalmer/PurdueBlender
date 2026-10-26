import bpy,json
from pathlib import Path
p=Path('modular/buildings/massing_northwestern_parking_garage_979f1a2.blend').resolve()
bpy.ops.wm.open_mainfile(filepath=str(p))
col=bpy.data.collections.get('Asset_massing_northwestern_parking_garage_979f1a2')
objs=list(col.all_objects) if col else []
out=[]
for o in objs:
 if o.type=='MESH':
  deps=bpy.context.evaluated_depsgraph_get(); ev=o.evaluated_get(deps); me=ev.to_mesh()
  coords=[o.matrix_world @ v.co for v in me.vertices]
  bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)] if coords else []
  out.append({'name':o.name,'vertices':len(me.vertices),'edges':len(me.edges),'faces':len(me.polygons),'materials':[m.name if m else None for m in o.data.materials],'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'world_bounds':bounds,'lib':str(o.library.filepath) if o.library else None})
  ev.to_mesh_clear()
print(json.dumps({'file':str(p),'scene':bpy.context.scene.name,'collections':len(bpy.data.collections),'objects':out},indent=2))
