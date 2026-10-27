import bpy, json
from mathutils import Vector
obj=bpy.data.objects['House_301837281']
mesh=obj.data
faces=[]
for p in mesh.polygons:
    faces.append({'vertices':list(p.vertices),'normal':[round(v,6) for v in p.normal],'center':[round(v,6) for v in p.center],'material_index':p.material_index})
verts=[[round(c,6) for c in v.co] for v in mesh.vertices]
report={'scene':bpy.context.scene.name,'collection':'Asset_massing_house_301837281_58ead22','object':obj.name,'type':obj.type,'loc':list(obj.location),'rot':list(obj.rotation_euler),'scale':list(obj.scale),'dimensions':list(obj.dimensions),'material_slots':[m.name if m else None for m in obj.data.materials],'vertices':verts,'faces':faces}
with open(r'audit/phi_gamma_delta/initial_mesh.json','w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print('Saved initial mesh; verts',len(verts),'faces',len(faces),'materials',report['material_slots'])
print('WORLD_BOUNDS',[[min((obj.matrix_world@obj.bound_box[i])[axis] for i in range(8)),max((obj.matrix_world@obj.bound_box[i])[axis] for i in range(8))] for axis in range(3)])
