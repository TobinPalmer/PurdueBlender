import bpy
from mathutils import Vector

ASSET = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend"
bpy.ops.wm.open_mainfile(filepath=ASSET)

def bounds(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return tuple(round(min(p[i] for p in pts), 2) for i in range(3)) + tuple(round(max(p[i] for p in pts), 2) for i in range(3))

print("SCENE", bpy.data.filepath, len(bpy.data.objects), len(bpy.data.materials))
for obj in sorted(bpy.data.objects, key=lambda o: o.name):
    if obj.type == "MESH":
        b = bounds(obj)
        # objects in front entry's sight corridor or visibly within entrance region
        if b[0] < 10 and b[3] > -10 and b[1] < 20 and b[4] > -10 and b[2] < 14 and b[5] > 4:
            mats = [m.name for m in obj.data.materials if m]
            print("MESH", obj.name, b, "materials=", mats[:5])

# Cast horizontal and angled rays from the official approach (+Y) toward the portal.
deps = bpy.context.evaluated_depsgraph_get()
scene = bpy.context.scene
for z in [1.5, 4.5, 8.0, 12.0]:
    origin = Vector((0, 50, z))
    direction = Vector((0, -1, 0))
    hit, loc, normal, face, ob, matrix = scene.ray_cast(deps, origin, direction, distance=100)
    print("RAY", z, hit, ob.name if ob else None, tuple(round(v,2) for v in loc) if hit else None)
