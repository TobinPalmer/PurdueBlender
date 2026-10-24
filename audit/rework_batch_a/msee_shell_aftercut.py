import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/materials_science_and_electrical_engineering_msee.blend')
o=bpy.data.objects['materials_science_and_electrical_engineering_msee_official_GIS_shell']
for i,v in enumerate(o.data.vertices):print(i,tuple(round(x,3) for x in o.matrix_world@v.co))
for i,p in enumerate(o.data.polygons):
 c=sum((o.matrix_world@o.data.vertices[j].co for j in p.vertices),__import__('mathutils').Vector())/len(p.vertices)
 print('face',i,list(p.vertices),tuple(round(x,2) for x in c),tuple(round(x,2) for x in o.matrix_world.to_3x3()@p.normal))
