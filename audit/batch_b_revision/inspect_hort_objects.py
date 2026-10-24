import bpy
p=r'modular/buildings/horticulture_building.blend'
bpy.ops.wm.open_mainfile(filepath=p)
a=bpy.data.collections['Asset_horticulture_building']
for o in a.all_objects:
 if any(x in o.name.lower() for x in ['glaz','window','curtain','vertical','facade']): print(o.name, o.type, [m.name if m else None for m in getattr(o.data,'materials',[])])
