import bpy, math
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath=r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\south_hall.blend")
scene = bpy.context.scene
coll = bpy.data.collections.get("Asset_south_hall")
objs = [o for o in coll.all_objects if o.type == "MESH"]
pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
mn = Vector(tuple(min(p[i] for p in pts) for i in range(3)))
mx = Vector(tuple(max(p[i] for p in pts) for i in range(3)))
target = (mn + mx) * 0.5
cam_data = bpy.data.cameras.new("SouthHall_ReviewCamera")
cam = bpy.data.objects.new("SouthHall_ReviewCamera", cam_data)
scene.collection.objects.link(cam)
cam.location = target + Vector((145, -190, 108))
cam.rotation_euler = (target-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.lens = 48
scene.camera = cam
sun_data = bpy.data.lights.new("SouthHall_ReviewSun", "SUN")
sun = bpy.data.objects.new("SouthHall_ReviewSun", sun_data); scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(26), math.radians(-18), math.radians(-28)); sun.data.energy=3.0
scene.render.engine="CYCLES"; scene.cycles.samples=24
scene.render.resolution_x=1300; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.world.color=(0.12,0.12,0.12)
scene.render.image_settings.file_format="PNG"
scene.render.filepath=r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\south_hall_refine\baseline_oblique.png"
bpy.ops.render.render(write_still=True)
print("BASELINE_BOUNDS",list(mn),list(mx),"TARGET",list(target))
