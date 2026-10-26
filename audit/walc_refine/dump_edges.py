import bpy,json
asset=bpy.data.collections['Asset_walc']
rows=[]
for i in range(90):
 o=bpy.data.objects.get(f'WALC_Source906_Edge_{i}_Band2')
 if o:
  rows.append({'i':i,'loc':list(o.location),'rot':list(o.rotation_euler),'dim':list(o.dimensions),'scale':list(o.scale),'bounds':[[min((o.matrix_world@v.co)[j] for v in o.data.vertices),max((o.matrix_world@v.co)[j] for v in o.data.vertices)] for j in range(3)] if o.type=='MESH' else None})
print(json.dumps(rows))
