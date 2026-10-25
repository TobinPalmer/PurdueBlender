import bpy,json
from mathutils import Vector
o=bpy.data.objects['ARMS_Cantilever_Canopy_Deck']
res=[]
for p in o.data.polygons:
    vs=[o.matrix_world@o.data.vertices[i].co for i in p.vertices]
    c=sum(vs,Vector((0,0,0)))/len(vs)
    if 18<=c.z<=22 and -63<=c.x<=-48 and 14<=c.y<=24:
        res.append({'poly':p.index,'center':[round(c.x,3),round(c.y,3),round(c.z,3)],'normal':[round(x,3) for x in (o.matrix_world.to_3x3()@p.normal)],'mat':p.material_index,'verts':[list(round(q,3) for q in v) for v in vs]})
print(json.dumps(res,indent=2))
