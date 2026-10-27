import bpy,json
p='modular/buildings/massing_purdue_village_administration_building_3faae6c.blend';bpy.ops.wm.open_mainfile(filepath=p)
o=bpy.data.objects['Purdue Village Administration Building']
print(json.dumps({'loc':list(o.location),'dimensions':list(o.dimensions),'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'bounds':[[min((o.matrix_world@v.co)[i] for v in o.data.vertices),max((o.matrix_world@v.co)[i] for v in o.data.vertices)] for i in range(3)],'faces':[{'n':list(p.normal),'center':list(p.center),'verts':len(p.vertices)} for p in o.data.polygons], 'materials':[m.name for m in o.data.materials]},indent=2))
