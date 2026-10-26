import bpy,json
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_wang_hall_wang_0dac5ab.blend'
bpy.ops.wm.open_mainfile(filepath=p)
print('FILE',bpy.data.filepath)
print('SCENES',[(x.name, list(x.collection.children.keys())) for x in bpy.data.scenes])
for c in bpy.data.collections:
 if 'wang_hall' in c.name.lower(): print('COLLECTION',c.name,[o.name for o in c.objects])
for o in bpy.data.objects:
 if 'wang' in o.name.lower(): print('OBJECT',o.name,o.type,list(o.dimensions),list(o.location),list(o.rotation_euler),list(o.scale))
