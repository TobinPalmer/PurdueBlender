import bpy, json
from mathutils import Vector

path = "modular/buildings/massing_university_book_store_717bf2c.blend"
bpy.ops.wm.open_mainfile(filepath=path)
scene = bpy.context.scene
print("SCENE", scene.name, "CAM", scene.camera.name if scene.camera else None)
for name in ("Building shell | exact OpenStreetMap footprint",
             "Storefront | brick pier", "Storefront | continuous upper brick band",
             "Storefront | continuous cream parapet", "Sign | UNIVERSITY BOOK STORE",
             "Storefront | recessed glazing bay 1"):
    obj = bpy.data.objects.get(name)
    if not obj:
        print("MISSING", name)
        continue
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices] if obj.type == "MESH" else []
    bounds = [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)] if pts else []
    print(json.dumps({"name":obj.name,"type":obj.type,"location":list(obj.location),"dimensions":list(obj.dimensions),"bounds":bounds,"mats":[m.name for m in obj.data.materials] if obj.type=="MESH" else list(obj.data.materials.keys())}, default=str))
print("asset_objects", len(bpy.data.collections["Asset_massing_university_book_store_717bf2c"].objects))
shell = bpy.data.objects["Building shell | exact OpenStreetMap footprint"]
for face in shell.data.polygons:
    points = [shell.matrix_world @ shell.data.vertices[i].co for i in face.vertices]
    if min(p.y for p in points) < -16 and max(p.y for p in points) < -16.2:
        print("SOUTH_FACE", face.index, face.material_index, [(round(p.x,2), round(p.y,2), round(p.z,2)) for p in points])
