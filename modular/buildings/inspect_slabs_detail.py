import bpy
import bmesh

for name in ["RAWL_FloorSlab_L1_Ground", "RAWL_FloorSlab_L2", "RAWL_FloorSlab_L3", "RAWL_FloorSlab_L4", "RAWL_FloorSlab_L5", "RAWL_Roof_Main_Deck"]:
    obj = bpy.data.objects.get(name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # Check bounding box of faces
    # See if there are multiple loops / holes
    print(f"\n{name}:")
    print(f"  Verts: {len(bm.verts)}, Edges: {len(bm.edges)}, Faces: {len(bm.faces)}")
    # Find boundary loops or check how the hole is cut
    # Let's count vertices on top face
    top_faces = [f for f in bm.faces if f.normal.z > 0.9]
    print(f"  Top faces: {len(top_faces)}, Area: {sum(f.calc_area() for f in top_faces):.2f} m^2")
    bm.free()
