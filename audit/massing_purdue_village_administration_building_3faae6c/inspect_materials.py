import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/massing_purdue_village_administration_building_3faae6c.blend')
o=bpy.data.objects['Purdue Village Administration Building']; m=o.data
for i,p in enumerate(m.polygons):
 c=p.center; print(i,p.material_index,m.materials[p.material_index].name,'n',tuple(round(q,3) for q in p.normal),'c',tuple(round(q,2) for q in c),'verts',len(p.vertices))
