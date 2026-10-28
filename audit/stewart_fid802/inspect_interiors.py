import bpy,json
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_house_1089875810_8c9b95d.blend'
bpy.ops.wm.open_mainfile(filepath=p)
o=bpy.data.objects.get('House_1089875810_schematic_partitions_furniture')
print('obj',o.name,'faces',len(o.data.polygons),'hide_render',o.hide_render,'zrange',min(v.co.z for v in o.data.vertices),max(v.co.z for v in o.data.vertices))
for story,z in [('basement',-2.45),('ground',.12),('second',3.02),('third',5.92)]:
 lo=z-.25;hi=z+2.95
 sel=[p for p in o.data.polygons if lo<=sum(o.data.vertices[i].co.z for i in p.vertices)/len(p.vertices)<=hi]
 print(story,len(sel),min((sum(o.data.vertices[i].co.z for i in p.vertices)/len(p.vertices) for p in sel),default=None),max((sum(o.data.vertices[i].co.z for i in p.vertices)/len(p.vertices) for p in sel),default=None))
