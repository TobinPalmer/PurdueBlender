import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/life_science_plant_and_soils_laboratory.blend')
for o in bpy.data.collections['Asset_life_science_plant_and_soils_laboratory'].all_objects:
 if any(k in o.name.lower() for k in ['stack','vent','chimney','exhaust','shaft','mechanical']): print(o.name,tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.dimensions),[c.name for c in o.users_collection])
