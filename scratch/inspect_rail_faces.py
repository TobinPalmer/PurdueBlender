import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/massing_american_railway_building_rail_fc0f9a2.blend')
o=bpy.data.objects['American Railway Building (RAIL)']
for p in o.data.polygons: print(list(p.vertices),tuple(round(x,2) for x in p.normal))
