import bpy
obj=bpy.data.objects['House_860826641']
print('vertices')
for i,v in enumerate(obj.data.vertices): print(i,tuple(round(c,3) for c in v.co))
print('faces')
for p in obj.data.polygons: print(tuple(p.vertices),p.material_index)
