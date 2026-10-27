import bpy,json
p=r'modular/buildings/massing_house_1089876362_14ecd2c.blend'
bpy.ops.wm.open_mainfile(filepath=p)
o=bpy.data.objects['House_1089876362']
print(json.dumps({'vertices':[[round(c,4) for c in v.co] for v in o.data.vertices], 'faces':[{'verts':list(poly.vertices),'mat':poly.material_index,'normal':[round(c,3) for c in poly.normal]} for poly in o.data.polygons]},indent=2))
