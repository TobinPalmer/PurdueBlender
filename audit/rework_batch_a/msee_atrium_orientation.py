import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/materials_science_and_electrical_engineering_msee.blend')
c=bpy.data.collections['Asset_materials_science_and_electrical_engineering_msee']
for n in ['MSEE_Max_W_Brown_two_story_glazed_atrium','materials_science_and_electrical_engineering_msee_official_GIS_shell','MSEE_atrium_roof_monitor']:
 o=bpy.data.objects.get(n); print(n,'loc',tuple(round(v,3) for v in o.location),'dim',tuple(round(v,3) for v in o.dimensions),'rot',tuple(round(v,3) for v in o.rotation_euler),'scale',tuple(round(v,3) for v in o.scale))
