import bpy,json
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall'];rows=[]
for o in C.objects:
 if o.type!='MESH':continue
 ps=[o.matrix_world@Vector(v) for v in o.bound_box];mi=[min(q[i] for q in ps) for i in range(3)];ma=[max(q[i] for q in ps) for i in range(3)]
 if mi[1]<-26.1 or ma[1]>26.85 or mi[0]<-26.3 or ma[0]>13.4:
  rows.append({'n':o.name,'b':[[round(x,2) for x in mi],[round(x,2) for x in ma]],'m':[m.name for m in o.data.materials]})
print(json.dumps(rows,indent=2))
for n in ['HAAS_Photo_Limestone','Purdue_Red_Brick.001','Purdue_Red_Brick','HAAS_Photo_Red_Roof']:
 m=bpy.data.materials.get(n)
 if m:
  print('MAT',n,m.diffuse_color[:],[(x.type,[(i.name,tuple(i.default_value) if hasattr(i.default_value,'__iter__') else i.default_value) for i in x.inputs if i.name in ['Base Color','Roughness']]) for x in m.node_tree.nodes if x.type=='BSDF_PRINCIPLED'] if m.node_tree else [])
