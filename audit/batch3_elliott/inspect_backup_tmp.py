import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch3_elliott\before_resume.blend')
c=bpy.data.collections['Asset_elliott_hall_of_music']
for o in c.all_objects:
 print(o.name,o.type,tuple(round(v,2) for v in o.dimensions),tuple(round(v,2) for v in o.location),[m.name for m in o.data.materials] if o.type=='MESH' else '')
