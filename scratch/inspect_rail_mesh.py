import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/massing_american_railway_building_rail_fc0f9a2.blend')
o=bpy.data.objects['American Railway Building (RAIL)']; m=o.data
print('mesh',len(m.vertices),len(m.polygons),'matidx',[(x.name,sum(1 for p in m.polygons if p.material_index==i)) for i,x in enumerate(m.materials)])
print('bbox',[(min((o.matrix_world@v.co)[i] for v in m.vertices),max((o.matrix_world@v.co)[i] for v in m.vertices)) for i in range(3)])
print('loc',o.location,'scale',o.scale)
for p in m.polygons[:10]: print(p.index,p.material_index,tuple(round(x,2) for x in p.normal),tuple(round(x,2) for x in p.center))
