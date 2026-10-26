import bpy, os, math
from mathutils import Vector
files=[('bell_tower',r'modular/buildings/bell_tower.blend'),('felix_haas',r'modular/buildings/felix_haas_hall.blend'),('psychological_sciences',r'modular/buildings/psychological_sciences.blend')]
os.makedirs('audit/material_review',exist_ok=True)
for label,p in files:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p)); sc=bpy.context.scene
 if not sc.camera:
  pts=[]
  for o in bpy.data.objects:
   if o.type=='MESH': pts.extend([o.matrix_world @ Vector(c) for c in o.bound_box])
  if pts:
   lo=Vector((min(v.x for v in pts),min(v.y for v in pts),min(v.z for v in pts))); hi=Vector((max(v.x for v in pts),max(v.y for v in pts),max(v.z for v in pts)))
   center=(lo+hi)/2; span=max(hi-lo); camd=bpy.data.cameras.new('ReviewCamera'); cam=bpy.data.objects.new('ReviewCamera',camd); sc.collection.objects.link(cam)
   cam.location=center+Vector((span*1.3,-span*1.8,span*1.25)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); camd.type='ORTHO'; camd.ortho_scale=span*1.7; sc.camera=cam
 sc.render.resolution_x=960; sc.render.resolution_y=720; sc.render.resolution_percentage=100
 if sc.render.engine=='CYCLES': sc.cycles.samples=20
 sc.render.filepath=os.path.abspath(f'audit/material_review/{label}_review.png')
 bpy.ops.render.render(write_still=True)
 print('rendered',label)
