import bpy
from mathutils import Vector

print("--- INTERIOR & SUBTERRANEAN STRUCTURE DETAILS ---")

g_slab = bpy.data.objects.get("HIKS_FloorSlab_Ground_Subterranean")
b_slab = bpy.data.objects.get("HIKS_FloorSlab_Basement_Foundation")
stairs = bpy.data.objects.get("HIKS_Central_Spiral_Staircase")
rails = bpy.data.objects.get("HIKS_Atrium_Bronze_Guardrails")
tunnel = bpy.data.objects.get("HIKS_Stewart_Center_Tunnel_Connector")
cols = bpy.data.objects.get("HIKS_Subterranean_Concrete_Columns")
stacks = bpy.data.objects.get("HIKS_Subterranean_Book_Stacks_Massing")

for obj in [g_slab, b_slab, stairs, rails, tunnel, cols, stacks]:
    if not obj:
        print(f"Missing {obj}")
        continue
    verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    xs = [v.x for v in verts]
    ys = [v.y for v in verts]
    zs = [v.z for v in verts]
    print(f"\nObject: {obj.name}")
    print(f"  X bounds: [{min(xs):.3f}, {max(xs):.3f}] (size {max(xs)-min(xs):.3f} m)")
    print(f"  Y bounds: [{min(ys):.3f}, {max(ys):.3f}] (size {max(ys)-min(ys):.3f} m)")
    print(f"  Z bounds: [{min(zs):.3f}, {max(zs):.3f}] (size {max(zs)-min(zs):.3f} m)")

print("\n--- ATRIUM OPENING IN GROUND SLAB ---")
if g_slab:
    # check faces/holes in g_slab
    # let's look at face centers and areas
    f_centers = [f.calc_center_median() for f in g_slab.data.polygons]
    print(f"  Ground slab polygon count: {len(g_slab.data.polygons)}")

print("\n--- SPIRAL STAIR RADIUS AND STEPS ---")
if stairs:
    verts = [v.co for v in stairs.data.vertices]
    center_x = sum(v.x for v in verts) / len(verts)
    center_y = sum(v.y for v in verts) / len(verts)
    radii = [( (v.x - center_x)**2 + (v.y - center_y)**2 )**0.5 for v in verts]
    print(f"  Stair center XY: ({center_x:.3f}, {center_y:.3f})")
    print(f"  Radius range: [{min(radii):.3f}, {max(radii):.3f}] m")
    print(f"  Vertical travel: Z [{min(v.z for v in verts):.3f}, {max(v.z for v in verts):.3f}] m (Total {max(v.z for v in verts) - min(v.z for v in verts):.3f} m)")

