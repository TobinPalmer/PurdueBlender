import bpy
import bmesh

roof = bpy.data.objects.get("RAWL_Roof_Main_Deck")
bm = bmesh.new()
bm.from_mesh(roof.data)

print(f"Roof verts: {len(bm.verts)}, edges: {len(bm.edges)}, faces: {len(bm.faces)}")
# Check faces in atrium area
center_faces = []
for f in bm.faces:
    c = f.calc_center_median()
    if 323 < c.x < 345 and -417 < c.y < -405:
        center_faces.append(f)
print(f"Roof faces in skylight box: {len(center_faces)}")
bm.free()
