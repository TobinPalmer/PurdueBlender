"""Read mesh edge topology for the single assigned building object."""
import bpy, bmesh, json
from mathutils import Vector

obj = bpy.data.objects.get("Village Bottle Shoppe")
bm = bmesh.new()
bm.from_mesh(obj.data)
bad = []
for e in bm.edges:
    if not e.is_manifold:
        bad.append({"face_count":len(e.link_faces),
                    "world_verts":[list(obj.matrix_world @ v.co) for v in e.verts]})
result = {"verts":len(bm.verts),"edges":len(bm.edges),"faces":len(bm.faces),
          "nonmanifold_edges":len(bad),"wire_edges":sum(1 for e in bm.edges if not e.link_faces),
          "boundary_edges":sum(1 for e in bm.edges if len(e.link_faces)==1),"examples":bad[:40]}
print("TOPOLOGY",json.dumps(result))
with open("audit/village_bottle_shoppe/topology_probe.json","w",encoding="utf-8") as f:
    json.dump(result,f,indent=2)
bm.free()
