import bpy
c=bpy.data.collections['Asset_math_sciences']; region=[[16.5,18.2],[-24,-22],[4,6.5]]
for o in c.all_objects:
 if not o or o.type!='MESH' or not o.data.vertices: continue
 vs=[o.matrix_world@v.co for v in o.data.vertices]; b=[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]
 if all(b[i][0]<region[i][1] and b[i][1]>region[i][0] for i in range(3)):
  print(o.name, [[round(x,3) for x in a] for a in b], [m.name for m in o.data.materials if m])
