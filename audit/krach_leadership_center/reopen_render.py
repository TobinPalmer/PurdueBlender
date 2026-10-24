import bpy, json, hashlib
from mathutils import Vector
p=bpy.data.filepath
assert p.lower().endswith('krach_leadership_center.blend')
a=bpy.data.collections['Asset_krach_leadership_center']
# recursively collect asset members
members=set()
def walk(c):
 for o in c.objects: members.add(o)
 for ch in c.children: walk(ch)
walk(a)
required=['KRCH documented fourth-floor slab | level +14.68m','KRCH open stair | 4-floor lobby flights and etched glass balustrade']
rows=[]
for name in required:
 o=bpy.data.objects.get(name); assert o, name
 assert o in members, 'not linked under Asset collection: '+name
 pts=[o.matrix_world @ v.co for v in o.data.vertices]
 rows.append({'name':name,'bounds':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]],'materials':[m.name for m in o.data.materials if m]})
# verify expected local frame and collection instance transforms are unchanged
bpy.context.scene.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\krach_leadership_center\source_preview.png'
bpy.context.scene.render.resolution_x=1200; bpy.context.scene.render.resolution_y=800; bpy.context.scene.render.resolution_percentage=100
bpy.ops.render.render(write_still=True)
print(json.dumps({'filepath':p,'asset_collection':a.name,'asset_object_count':len(members),'checked':rows,'preview':bpy.context.scene.render.filepath},indent=2))

