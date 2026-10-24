import bpy,json
s=bpy.context.scene
for o in s.objects:
 if o.type=='CAMERA': print('CAMINFO',json.dumps({'object':o.name,'object_library':o.library.filepath if o.library else None,'data':o.data.name,'data_library':o.data.library.filepath if o.data.library else None,'clip_end':o.data.clip_end,'active':o is s.camera}))
