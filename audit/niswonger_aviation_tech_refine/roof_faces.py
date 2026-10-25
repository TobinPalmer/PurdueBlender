import bpy,json
from mathutils import Vector
o=bpy.data.objects['NISW_Flat_Roof_Membrane']
me=o.data
info=[]
for p in me.polygons:
 vs=[o.matrix_world@me.vertices[i].co for i in p.vertices]
 if min(v.z for v in vs)>5.4:
  info.append({'n':len(vs),'xy':[[round(v.x,2),round(v.y,2)] for v in vs],'z':[round(v.z,2) for v in vs]})
print('verts',len(me.vertices),'faces',len(me.polygons),'roof top faces',len(info))
print(json.dumps(info[:100],indent=1))
