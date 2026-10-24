import bpy, math
from mathutils import Vector
scene=bpy.context.scene
keep={bpy.data.objects['KRCH | four-story visible switchback stair and etched glass guard']}
keep.update(o for o in bpy.data.objects if o.name.startswith('KRCH | schematic level slab'))
keep.update(o for o in bpy.data.objects if o.name.startswith('KRCH | continuous stair handrails'))
old=[(o,o.hide_render) for o in bpy.data.objects]
for o in bpy.data.objects: o.hide_render=o not in keep
# render only the architectural stair/floor cuts with transparent background.
scene.render.film_transparent=True
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1200; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
scene.world.color=(0.28,0.28,0.28)
data=bpy.data.cameras.new('TEMP stair diagnostic camera'); cam=bpy.data.objects.new('TEMP stair diagnostic camera',data); scene.collection.objects.link(cam)
cam.location=(-19.45,-30.0,8.0); target=Vector((-19.45,-9.3,7.6)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=40; scene.camera=cam
lights=[]
for name,loc,power,size,targetpos in [('TEMP diagnostic key',(-20,-9,17),7000,10,(-19,-9,5)),('TEMP diagnostic fill',(-30,-8,8),5000,10,(-19,-9,8))]:
 d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.size=size; o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc; o.rotation_euler=(Vector(targetpos)-o.location).to_track_quat('-Z','Y').to_euler(); lights.append(o)
scene.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\krach_leadership_center\lobby_stair_preview.png'; bpy.ops.render.render(write_still=True)




