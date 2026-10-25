import bpy
import json

ASSET = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend"
bpy.ops.wm.open_mainfile(filepath=ASSET)
for name in ["ARMS_Sea_Wolf_ACM", "ARMS_Mayflower_Red_ACM", "ARMS_R6_Mayflower_Red_ACM", "ARMS_R9_Light_Roof_Surface", "ARMS_Purdue_Red_Brick", "ARMS_Solar_Curtain_Glass"]:
    mat = bpy.data.materials.get(name)
    if not mat:
        continue
    node = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if mat.use_nodes else None
    vals = {}
    if node:
        for input_name in ["Base Color", "Metallic", "Roughness", "Alpha"]:
            socket = node.inputs.get(input_name)
            if socket:
                vals[input_name] = list(socket.default_value) if hasattr(socket.default_value, "__len__") else socket.default_value
    print("MAT", json.dumps({"name": name, "use_nodes": mat.use_nodes, "values": vals}))
for name in ["ARMS_Cantilever_Canopy_Deck", "ARMS_Canopy_Fascia_Trim", "ARMS_East_Roof_Slab", "ARMS_West_Roof_Slab"]:
    obj = bpy.data.objects.get(name)
    if obj:
        print("OBJ", name, [m.name for m in obj.data.materials], "polygons", len(obj.data.polygons))
