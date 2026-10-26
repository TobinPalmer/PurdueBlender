import bpy,os
from mathutils import Vector
files=[('bell_tower',r'modular/buildings/bell_tower.blend','Bell_Dark_Metal_Roof'),('felix_haas',r'modular/buildings/felix_haas_hall.blend','HAAS_Slate_Roof'),('psychological_sciences',r'modular/buildings/psychological_sciences.blend','PSYC | dark membrane roof')]
os.makedirs('audit/material_review',exist_ok=True)
for label,p,mname in files:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p)); sc=bpy.context.scene
 roofobjs=[o for o in bpy.data.objects if o.type=='MESH' and any(m and m.name==mname for m in o.data.materials)]
 roofpts=[o.matrix_world@Vector(c) for o in roofobjs for c in o.bound_box]
 allobjs=[o for o in bpy.data.objects if o.type=='MESH' and max(o.dimensions)<100]
 allpts=[o.matrix_world@Vector(c) for o in allobjs for c in o.bound_box]
 def bounds(pts):
  lo=Vector((min(v.x for v in pts),min(v.y for v in pts),min(v.z for v in pts))); hi=Vector((max(v.x for v in pts),max(v.y for v in pts),max(v.z for v in pts))); return (lo+hi)*0.5,hi-lo
 def camera(center,scale,direction):
  d=bpy.data.cameras.new('Review'); o=bpy.data.objects.new('Review',d); sc.collection.objects.link(o); o.location=center+direction*scale*1.5; o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler(); d.type='ORTHO';d.ortho_scale=scale;sc.camera=o
 sc.render.resolution_x=960;sc.render.resolution_y=720;sc.render.resolution_percentage=100
 if sc.render.engine=='CYCLES':sc.cycles.samples=24
 center,size=bounds(allpts); camera(center,max(size.x,size.y,size.z)*1.9,Vector((1,-1,0.75)))
 sc.render.filepath=os.path.abspath(f'audit/material_review/{label}_overview_texture.png');bpy.ops.render.render(write_still=True)
 center,size=bounds(roofpts); camera(center,max(size.x,size.y)*1.18,Vector((0.45,-0.65,1.25)))
 sc.render.filepath=os.path.abspath(f'audit/material_review/{label}_roof_close_texture.png');bpy.ops.render.render(write_still=True)
 print('rendered',label,'roof objects',len(roofobjs))
