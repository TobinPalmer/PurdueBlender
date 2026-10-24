import bpy, json, os
print('SCENE', bpy.context.scene.name, len(bpy.data.objects))
print('LIBRARIES', len(bpy.data.libraries))
for lib in bpy.data.libraries:
 p=bpy.path.abspath(lib.filepath)
 print('LIB',lib.name,p,os.path.exists(p))
placements=[]
for ob in bpy.data.objects:
 if ob.name.startswith('Placement_'):
  placements.append((ob.name,tuple(round(v,5) for v in ob.matrix_world.translation),tuple(round(v,5) for v in ob.matrix_world.to_euler())))
print('PLACEMENTS',len(placements),json.dumps(placements[:8]))
print('RENDER_CAMERAS',[ob.name for ob in bpy.data.objects if ob.type=='CAMERA'])
