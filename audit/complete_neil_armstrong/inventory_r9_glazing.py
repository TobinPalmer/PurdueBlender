import bpy,json
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend'; bpy.ops.wm.open_mainfile(filepath=p); col=bpy.data.collections['Asset_neil_armstrong_hall']
rows=[]
for o in col.objects:
 if any(s in o.name.lower() for s in ['curtain','glass','clerestory','mullion']):
  if o.type=='MESH':
   pts=[o.matrix_world@v.co for v in o.data.vertices]; b=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
  else:b=None
  rows.append({'n':o.name,'b':b,'type':o.type})
print(json.dumps(rows,indent=2))
