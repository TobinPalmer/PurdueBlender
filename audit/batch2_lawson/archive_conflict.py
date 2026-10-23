import bpy
C=bpy.data.collections['Asset_lawson_hall'];R=bpy.data.collections.new('LWSN_Previous_Interior_Reference');bpy.context.scene.collection.children.link(R);R.hide_render=True;R.hide_viewport=True
for n in ['LWSN_Interior_Public_Core','LWSN_Interior_Glass_Partitions']:
 o=bpy.data.objects.get(n)
 if o:
  for c in list(o.users_collection):c.objects.unlink(o)
  R.objects.link(o)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
