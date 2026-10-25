import bpy,json
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
c=bpy.data.collections['Asset_neil_armstrong_hall']
rows=[]
for o in c.objects:
 if any(k in o.name.lower() for k in ['roof','wing','canopy','truss','penthouse','parapet']):
  vs=[o.matrix_world@v.co for v in o.data.vertices] if o.type=='MESH' else []
  b=[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)] if vs else None
  rows.append({'name':o.name,'type':o.type,'bounds':b,'verts':len(o.data.vertices) if o.type=='MESH' else None})
print(json.dumps(rows,indent=2))
