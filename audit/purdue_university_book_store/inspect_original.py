import bpy

path = "modular/buildings/massing_university_book_store_717bf2c.blend"
bpy.ops.wm.open_mainfile(filepath=path)
obj = bpy.data.objects["University Book Store"]
print("LOCAL_MESH_VERTS")
for vert in obj.data.vertices:
    print(vert.index, tuple(round(value, 4) for value in vert.co))
print("FACES")
for face in obj.data.polygons:
    print(face.index, list(face.vertices), face.material_index)
print("MATERIALS")
for index, material in enumerate(obj.data.materials):
    print(index, material.name)
