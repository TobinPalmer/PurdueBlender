import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/life_science_plant_and_soils_laboratory.blend')
for o in bpy.data.objects:
 if any(k in o.name.lower() for k in ['floor plate','lab bench','lab vessel','interior']): print(o.name,tuple(round(x,2) for x in o.location),tuple(round(x,2) for x in o.dimensions),[c.name for c in o.users_collection])
