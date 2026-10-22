import bpy
for name in ['Armory_Wall_East','Armory_Wall_South_Low','Armory_Window_East_Low_-36','Armory_Roof_Seg_0']:
 o=bpy.data.objects[name];print(name,tuple(o.location),tuple(o.dimensions))
for o in bpy.data.collections['Asset_armory'].all_objects:
 if o.type=='MESH' and any(s.material and s.material.name=='Solar_Ribbon_Glass' for s in o.material_slots) and not ('Window' in o.name or 'Tower_Win' in o.name): print('OTHER',o.name,tuple(o.location),tuple(o.dimensions))
