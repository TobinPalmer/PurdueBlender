import bpy
import bmesh

print("--- DETAILED TOPOLOGY AUDIT ---")
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    # Check if closed manifold or open shell
    open_edges = [e for e in bm.edges if len(e.link_faces) == 1]
    nm_edges = [e for e in bm.edges if len(e.link_faces) > 2 or len(e.link_faces) == 0]
    is_closed = len(open_edges) == 0 and len(nm_edges) == 0
    
    dims = obj.dimensions
    area = sum(f.calc_area() for f in bm.faces)
    
    print(f"{obj.name:<42}: verts={len(bm.verts):4d}, faces={len(bm.faces):4d}, closed={str(is_closed):<5}, open_edges={len(open_edges):4d}, non_manifold={len(nm_edges):2d}, dims=({dims.x:6.2f}, {dims.y:6.2f}, {dims.z:5.2f}), area={area:8.2f}m2")
    bm.free()
