import bpy
from mathutils import Vector

target_pt = Vector((334.0, -411.0, 50.0))
ray_dir = Vector((0.0, 0.0, -1.0))

print("Raycasting downwards from (334, -411, 50):")
for slab_name in ["RAWL_Roof_Main_Deck", "RAWL_FloorSlab_L5", "RAWL_FloorSlab_L4", "RAWL_FloorSlab_L3", "RAWL_FloorSlab_L2", "RAWL_FloorSlab_L1_Ground"]:
    s = bpy.data.objects.get(slab_name)
    succ, l, n, idx = s.ray_cast(target_pt, ray_dir)
    print(f"  {slab_name}: hit={succ}, hit_z={l.z if succ else None}")
