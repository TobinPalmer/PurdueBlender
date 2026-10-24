import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/massing_american_railway_building_rail_fc0f9a2.blend')
o=bpy.data.objects['American Railway Building (RAIL)']
for i,v in enumerate(o.data.vertices): print(i,tuple(round(x,3) for x in (o.matrix_world@v.co)))
