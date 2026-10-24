import bpy,json
names=['KRCH flat roof cap','KRCH structural shell | GIS outline','KRCH raised foundation plinth']
for n in names:
 o=bpy.data.objects.get(n); pts=[o.matrix_world@v.co for v in o.data.vertices]; print(n,'loc',list(o.location),'dim',list(o.dimensions),'bounds',[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],'mats',[m.name for m in o.data.materials if m])
