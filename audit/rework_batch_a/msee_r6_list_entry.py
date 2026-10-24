import bpy,os
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/materials_science_and_electrical_engineering_msee.blend'))
col=bpy.data.collections['Asset_materials_science_and_electrical_engineering_msee']
for o in col.all_objects:
 if o.name.startswith(('R6_MSEE_entry_','R6_MSEE_fanlight_spoke_')): print(o.name)
