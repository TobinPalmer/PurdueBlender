import bpy
import bmesh

slab = bpy.data.objects.get("RAWL_FloorSlab_L2")
bm = bmesh.new()
bm.from_mesh(slab.data)

print(f"Slab L2 verts: {len(bm.verts)}, edges: {len(bm.edges)}, faces: {len(bm.faces)}")
# Check inner loops or face distribution
# Find faces near center (325 < x < 343, -415 < y < -407)
center_faces = []
for f in bm.faces:
    center = f.calc_center_median()
    if 325 < center.x < 343 and -415 < center.y < -407:
        center_faces.append(f)

print(f"Faces in atrium center region: {len(center_faces)}")

# Check if there is a hole by checking boundary edges or checking face topology
# Or check if vertices exist in that atrium region
atrium_verts = [v for v in bm.verts if 326 < v.co.x < 342 and -414 < v.co.y < -408]
print(f"Vertices in atrium center box: {len(atrium_verts)}")
bm.free()

# Let's also check if there is an documentation text or readme or markdown file
import os
for root, dirs, files in os.walk(r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings"):
    for file in files:
        if "rawl" in file.lower():
            print(f"Found file: {os.path.join(root, file)}")
