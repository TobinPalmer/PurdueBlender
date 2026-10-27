import bpy,json
from mathutils import Vector
asset='modular/buildings/massing_house_301841329_bed5cb6.blend'
bpy.ops.wm.open_mainfile(filepath=asset)
c=bpy.data.collections['Asset_massing_house_301841329_bed5cb6']
o=bpy.data.objects['House_301841329']
verts=[list(o.matrix_world@v.co) for v in o.data.vertices]
faces=[list(p.vertices) for p in o.data.polygons]
print(json.dumps({'collection':c.name,'objects':[x.name for x in c.all_objects],'object_type':o.type,'vertices':len(verts),'faces':len(faces),'bounds':[[min(p[i] for p in verts),max(p[i] for p in verts)] for i in range(3)],'verts':verts,'faces':faces,'mat_names':[m.name for m in o.data.materials]},indent=2))
