import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/life_science_plant_and_soils_laboratory.blend')
c=bpy.data.collections['LSPS_Roof']
for o in c.objects:
 print(o.name,tuple(round(x,3) for x in o.location),tuple(round(x,3) for x in o.dimensions),o.type)
