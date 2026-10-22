import bpy
from mathutils import Vector

slab = bpy.data.objects.get("RAWL_FloorSlab_L2")
# Test a point right under the center of the skylight: (334.0, -411.0, 5.486)
# Skylight center is approx (334.0, -411.0)
target_pt = Vector((334.0, -411.0, 10.0))
ray_dir = Vector((0.0, 0.0, -1.0))

success, loc, normal, face_idx = slab.ray_cast(target_pt, ray_dir)
print(f"Ray cast from (334, -411, 10) down through FloorSlab_L2: hit={success}, loc={loc}, face_idx={face_idx}")

# Also check other slabs
for slab_name in ["RAWL_FloorSlab_L1_Ground", "RAWL_FloorSlab_L2", "RAWL_FloorSlab_L3", "RAWL_FloorSlab_L4", "RAWL_FloorSlab_L5", "RAWL_Roof_Main_Deck"]:
    s = bpy.data.objects.get(slab_name)
    succ, l, n, idx = s.ray_cast(target_pt, ray_dir)
    print(f"  {slab_name}: hit={succ}, hit_z={l.z if succ else None}")
