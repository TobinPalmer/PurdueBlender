import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend'
bpy.ops.wm.open_mainfile(filepath=p)
for s in bpy.data.scenes:
 print('SCENE',s.name,'objects',len(s.objects),'camera',s.camera.name if s.camera else None,'rootchildren',[(c.name,len(c.objects),len(c.children)) for c in s.collection.children])
print('LIBS',len(bpy.data.libraries))
print('CAMERAS',[(o.name,tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.rotation_euler)) for o in bpy.data.objects if o.type=='CAMERA'])
print('SITE_MAIN',[(o.name,tuple(round(v,2) for v in o.location),o.type,o.instance_type) for o in bpy.context.scene.objects if any(k in o.name.lower() for k in ('campus_site','site','wiley','walc'))])
