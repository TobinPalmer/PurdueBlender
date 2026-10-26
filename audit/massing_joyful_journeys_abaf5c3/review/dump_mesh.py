import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/massing_joyful_journeys_abaf5c3.blend')
o=bpy.data.objects['Joyful Journeys']; me=o.data
print('verts');
for i,v in enumerate(me.vertices): print(i,tuple(round(a,4) for a in v.co))
print('faces')
for p in me.polygons: print(tuple(p.vertices))
