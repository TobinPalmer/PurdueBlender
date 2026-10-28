"""Render the south long facade without modifying the saved library."""
import bpy, os
from mathutils import Vector
folder=os.path.dirname(os.path.abspath(__file__))
obj=bpy.data.objects.get('Riverside Covenannt Church')
if obj is None: raise RuntimeError('Riverside mesh missing')
pts=[obj.matrix_world@v.co for v in obj.data.vertices]
lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
center=(lo+hi)/2
# Project axes show the south facade from the parking/entry side; use a near-level view.
center.z=4.1
camdata=bpy.data.cameras.new('RiversideFrontCamera'); cam=bpy.data.objects.new('RiversideFrontCamera',camdata); bpy.context.scene.collection.objects.link(cam)
cam.location=center+Vector((0,-55,5.5)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.type='ORTHO'; camdata.ortho_scale=40; bpy.context.scene.camera=cam
for n,offset,energy,size in [('RiversideFrontKey',(0,-24,27),4500,22),('RiversideFrontFill',(12,-10,11),1800,18)]:
 ld=bpy.data.lights.new(n,'AREA'); ld.energy=energy; ld.shape='DISK'; ld.size=size
 ob=bpy.data.objects.new(n,ld); bpy.context.scene.collection.objects.link(ob); ob.location=center+Vector(offset); ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene
try: scene.render.engine='BLENDER_EEVEE_NEXT'
except TypeError: scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1440; scene.render.resolution_y=850; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(folder,'preview_south_facade.png')
scene.view_settings.view_transform='AgX'; scene.view_settings.exposure=0
scene.render.film_transparent=False
bpy.ops.render.render(write_still=True)
print('RIVERSIDE_FRONT_PREVIEW='+scene.render.filepath)
