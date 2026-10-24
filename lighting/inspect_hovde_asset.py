import bpy,json
from mathutils import Vector
objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
pts=[o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
print('ASSET',json.dumps({'objects':len(bpy.context.scene.objects),'meshes':len(objs),'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],'cameras':[o.name for o in bpy.context.scene.objects if o.type=='CAMERA'],'collections':[c.name for c in bpy.data.collections]},default=str),flush=True)
bpy.ops.wm.quit_blender()
