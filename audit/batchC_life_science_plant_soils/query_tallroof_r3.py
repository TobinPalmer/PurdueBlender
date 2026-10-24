import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/life_science_plant_and_soils_laboratory.blend')
for o in bpy.data.collections['Asset_life_science_plant_and_soils_laboratory'].all_objects:
 if o.type=='MESH' and max(o.dimensions)>2 and o.location.z>9: print(o.name,tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.dimensions))
