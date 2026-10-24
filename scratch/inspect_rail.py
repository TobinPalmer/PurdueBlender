import bpy, json
p=r'modular/buildings/massing_american_railway_building_rail_fc0f9a2.blend'
bpy.ops.wm.open_mainfile(filepath=p)
for o in bpy.data.objects:
 print(o.name, o.type, tuple(round(v,3) for v in o.location), tuple(round(v,3) for v in o.dimensions), len(o.data.materials) if o.type=='MESH' else '')
 print(' mats',[(m.name,tuple(round(v,2) for v in m.diffuse_color)) for m in o.data.materials] if o.type=='MESH' else '')
