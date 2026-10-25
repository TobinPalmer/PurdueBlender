import bpy,collections
bpy.ops.wm.open_mainfile(filepath='modular/buildings/northwest_chiller_plant.blend')
c=bpy.data.collections['Asset_northwest_chiller_plant']
print('objects',len(c.all_objects))
print('mats')
for m in sorted({m.name for o in c.all_objects if o.type=='MESH' for m in o.data.materials if m}): print('M',m)
print('featured')
for o in c.all_objects:
 if not o.name.startswith(('NWCP_louver_blade','NWCP_acoustic_louver_bank','NWCP_roof_cooling_cell','NWCP_stringcourse')): print('O',o.name,o.type, [m.name for m in o.data.materials if m])
