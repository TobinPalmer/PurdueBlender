import bpy
col=bpy.data.collections['Asset_armory']
for o in col.all_objects:
 if o.type=='MESH' and (not len(o.material_slots) or any(s.material is None for s in o.material_slots)):print('UNASSIGNED',o.name,tuple(o.location),len(o.material_slots))
