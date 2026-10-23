import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend')
for sc in bpy.data.scenes:
 print('SCENE',sc.name,'render',sc.render.resolution_x,sc.render.resolution_y,'camera',sc.camera.name if sc.camera else None)
for c in bpy.data.collections:
 print('COLL',c.name,'objects',len(c.all_objects))
print('OBJS',len(bpy.data.objects),'MESHES',sum(o.type=='MESH' for o in bpy.data.objects),'CAMERAS',[(o.name,list(o.location),list(o.rotation_euler)) for o in bpy.data.objects if o.type=='CAMERA'])
print('MATS',[(m.name,tuple(round(float(x),3) for x in m.diffuse_color),m.use_nodes) for m in bpy.data.materials])
for o in bpy.data.objects:
 if o.type=='MESH' and (o.name.startswith('AssetRoot') or o.name in ['SC_Foundation_Limestone_Plinth','SC_Roof','SC_Red_Brick_Exterior','SC_Portico_3D_Text']): print('KEY',o.name,list(o.dimensions),list(o.location),[m.name for m in o.data.materials])
