import bpy
import mathutils

blend_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"

obj = bpy.data.objects.get("Mathematical Sciences Building (MATH)")
if obj:
    print(f"Object: {obj.name}")
    print(f"Location: {obj.location}")
    print(f"Rotation: {obj.rotation_euler}")
    print(f"Scale: {obj.scale}")
    print(f"Dimensions: {obj.dimensions}")
    
    verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    xs = [v.x for v in verts]
    ys = [v.y for v in verts]
    zs = [v.z for v in verts]
    print(f"X range: [{min(xs):.2f}, {max(xs):.2f}] (span: {max(xs)-min(xs):.2f})")
    print(f"Y range: [{min(ys):.2f}, {max(ys):.2f}] (span: {max(ys)-min(ys):.2f})")
    print(f"Z range: [{min(zs):.2f}, {max(zs):.2f}] (span: {max(zs)-min(zs):.2f})")
else:
    print("Object not found!")
