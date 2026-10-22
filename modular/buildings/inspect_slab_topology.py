import bpy
import bmesh

slab = bpy.data.objects.get("RAWL_FloorSlab_L2")
bm = bmesh.new()
bm.from_mesh(slab.data)

# Let's inspect boundary edges or top faces
top_faces = [f for f in bm.faces if f.normal.z > 0.9]
print(f"Top faces count: {len(top_faces)}")
# Calculate total area of top faces
top_area = sum(f.calc_area() for f in top_faces)
print(f"Total floor slab top surface area: {top_area:.2f} m^2")

# Let's check the vertices on the top face
top_verts = set()
for f in top_faces:
    for v in f.verts:
        top_verts.add(v)

print(f"Unique vertices on top surface: {len(top_verts)}")
# Print vertex coordinates bounding the inner atrium hole
inner_verts = [v for v in top_verts if 320 < v.co.x < 350 and -420 < v.co.y < -400]
print(f"Inner verts near atrium: {len(inner_verts)}")
for v in inner_verts:
    print(f"  v: ({v.co.x:.2f}, {v.co.y:.2f}, {v.co.z:.2f})")

bm.free()
