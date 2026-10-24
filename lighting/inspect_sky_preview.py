import bpy,json
s=bpy.context.scene
print('ROOTS',json.dumps([(c.name,len(c.objects),len(c.children),c.hide_render) for c in s.collection.children]),flush=True)
print('HOVDE_OBJECTS',json.dumps([o.name for o in bpy.data.objects if 'hovde' in o.name.lower()][:100]),flush=True)
print('HOVDE_COLLECTIONS',json.dumps([c.name for c in bpy.data.collections if 'hovde' in c.name.lower()][:100]),flush=True)
print('CAMERAS',json.dumps([o.name for o in bpy.data.objects if o.type=='CAMERA' and ('77' in o.name or 'hovde' in o.name.lower())]),flush=True)
bpy.ops.wm.quit_blender()
