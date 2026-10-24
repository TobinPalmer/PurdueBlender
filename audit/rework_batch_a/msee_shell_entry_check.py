import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/materials_science_and_electrical_engineering_msee.blend')
s=bpy.data.objects['MSEE_Max_W_Brown_two_story_glazed_atrium']; screenpt=sum((s.matrix_world@v.co for v in s.data.vertices),Vector())/len(s.data.vertices)
t=Vector((.627,-.779,0)).normalized(); out=Vector((-t.y,t.x,0))
sh=bpy.data.objects['materials_science_and_electrical_engineering_msee_official_GIS_shell']
print('shell verts',len(sh.data.vertices),'polys',len(sh.data.polygons),'screen center',tuple(round(x,2) for x in screenpt),'out',tuple(round(x,2) for x in out))
for p in sh.data.polygons:
 c=sum((sh.matrix_world@sh.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
 no=sh.matrix_world.to_3x3()@p.normal; no.normalize()
 rel=c-screenpt; tang=rel.dot(t); d=rel.dot(out)
 if abs(tang)<15 and abs(c.z-4)<10:
  print('face',p.index,'n',tuple(round(x,2) for x in no),'dotOut',round(no.dot(out),2),'t',round(tang,2),'d',round(d,2),'z',round(c.z,2),'area',round(p.area,2),len(p.vertices))
print('R2 tables')
for o in bpy.data.collections['Asset_materials_science_and_electrical_engineering_msee'].all_objects:
 if o.name.startswith('R2_MSEE_atrium_collaboration_table') or o.name.startswith('R2_MSEE_atrium_seat'):
  w=o.matrix_world.translation; print(o.name,tuple(round(x,2) for x in w), 'd',round((w-screenpt).dot(out),2))
