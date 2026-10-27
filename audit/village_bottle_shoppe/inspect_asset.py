import bpy,json,collections
obj=bpy.data.objects.get('Village Bottle Shoppe')
print('MATLIST',json.dumps([m.name if m else None for m in obj.data.materials]))
C=collections.Counter(p.material_index for p in obj.data.polygons)
print('INDICES',dict(C))
for p in obj.data.polygons:
 c=obj.matrix_world@p.center
 if c.z>4.1: print('UPPER',round(c.x,2),round(c.y,2),round(c.z,2),p.material_index,obj.data.materials[p.material_index].name if p.material_index<len(obj.data.materials) else 'invalid',list(p.normal))
