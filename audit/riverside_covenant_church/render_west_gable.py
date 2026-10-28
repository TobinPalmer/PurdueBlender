"""Render the west stained-glass entry gable for direct reference review."""
import bpy, os
from mathutils import Vector
folder=os.path.dirname(os.path.abspath(__file__))
obj=bpy.data.objects.get('Riverside Covenannt Church')
if obj is None: raise RuntimeError('Riverside church mesh missing')
pts=[obj.matrix_world@v.co for v in obj.data.vertices]
lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts))); hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
center=(lo+hi)/2; center.z=4.55
camdata=bpy.data.cameras.new('RiversideWestGableCamera'); cam=bpy.data.objects.new('RiversideWestGableCamera',camdata); bpy.context.scene.collection.objects.link(cam)
cam.location=center+Vector((-42,-5,8)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); camdata.type='ORTHO'; camdata.ortho_scale=21; bpy.context.scene.camera=cam
for n,off,power,size in [('GableKey',(-18,-7,25),1800,18),('GableFill',(-8,18,15),900,14)]:
 ld=bpy.data.lights.new('Riverside_'+n,'AREA'); ld.energy=power; ld.shape='DISK'; ld.size=size
 ob=bpy.data.objects.new('Riverside_'+n,ld); bpy.context.scene.collection.objects.link(ob); ob.location=center+Vector(off); ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene
try: scene.render.engine='BLENDER_EEVEE_NEXT'
except TypeError: scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1280; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(folder,'preview_west_gable.png')
scene.view_settings.view_transform='AgX'; scene.view_settings.exposure=-.35
bpy.ops.render.render(write_still=True)
print('RIVERSIDE_WEST_GABLE_PREVIEW='+scene.render.filepath)
