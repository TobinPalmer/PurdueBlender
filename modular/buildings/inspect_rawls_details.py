import bpy

print("=== TEXT BLOCKS ===")
for t in bpy.data.texts:
    print(f"Text block: {t.name}")
    print("----- START -----")
    print(t.as_string()[:1000])
    print("----- END -----")

print("\n=== ATRIUM & SLAB GEOMETRY ===")
for slab_name in ["RAWL_FloorSlab_L1_Ground", "RAWL_FloorSlab_L2", "RAWL_FloorSlab_L3", "RAWL_FloorSlab_L4", "RAWL_FloorSlab_L5"]:
    slab = bpy.data.objects.get(slab_name)
    if slab:
        # Check bounding box of the slab
        coords = [slab.matrix_world @ v.co for v in slab.data.vertices]
        xs = [c.x for c in coords]
        ys = [c.y for c in coords]
        zs = [c.z for c in coords]
        print(f"{slab_name}: verts={len(slab.data.vertices)}, faces={len(slab.data.polygons)}, X=[{min(xs):.2f}, {max(xs):.2f}], Y=[{min(ys):.2f}, {max(ys):.2f}], Z=[{min(zs):.2f}, {max(zs):.2f}]")

cols = bpy.data.objects.get("RAWL_Atrium_Structural_Columns")
if cols:
    coords = [cols.matrix_world @ v.co for v in cols.data.vertices]
    xs = [c.x for c in coords]
    ys = [c.y for c in coords]
    zs = [c.z for c in coords]
    print(f"RAWL_Atrium_Structural_Columns: X=[{min(xs):.2f}, {max(xs):.2f}], Y=[{min(ys):.2f}, {max(ys):.2f}], Z=[{min(zs):.2f}, {max(zs):.2f}]")

print("\n=== EXTERNAL IMAGES / PATHS ===")
for img in bpy.data.images:
    print(f"Image: {img.name}, filepath: {img.filepath}, packed: {img.packed_file is not None}")

print("\n=== CAMERAS IN BLEND ===")
for cam in [o for o in bpy.data.objects if o.type == 'CAMERA']:
    print(f"Camera: {cam.name}, loc: {cam.location}, rot: {cam.rotation_euler}")

print("\n=== MATERIALS USAGE ===")
for mat in bpy.data.materials:
    users = [o.name for o in bpy.data.objects if mat.name in [m.name for m in o.data.materials] if o.type == 'MESH']
    print(f"Material {mat.name}: used by {len(users)} objects")
