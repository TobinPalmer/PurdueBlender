import bpy

for sname in ["RAWL_FloorSlab_L2", "RAWL_FloorSlab_L3", "RAWL_FloorSlab_L4", "RAWL_FloorSlab_L5"]:
    obj = bpy.data.objects.get(sname)
    print(f"{sname}: verts={len(obj.data.vertices)}, faces={len(obj.data.polygons)}")
