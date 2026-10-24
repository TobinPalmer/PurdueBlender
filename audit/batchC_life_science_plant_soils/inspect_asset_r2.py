import bpy, json

path = r"modular/buildings/life_science_plant_and_soils_laboratory.blend"
bpy.ops.wm.open_mainfile(filepath=path)
root = bpy.data.collections.get("Asset_life_science_plant_and_soils_laboratory")
def walk(c):
    for o in c.objects:
        yield o
    for child in c.children:
        yield from walk(child)
objs = list(walk(root)) if root else []
data = {
    "file": bpy.data.filepath,
    "collections": [(c.name, len(c.objects), [x.name for x in c.children]) for c in bpy.data.collections],
    "objects": [(o.name, o.type, tuple(round(float(v), 3) for v in o.dimensions), tuple(round(float(v), 3) for v in o.location), [m.name for m in o.data.materials] if o.type == "MESH" else []) for o in objs],
    "texts": [t.name for t in bpy.data.texts],
    "materials": []
}
for mat in bpy.data.materials:
    d = {"name": mat.name, "use_nodes": mat.use_nodes, "nodes": []}
    if mat.use_nodes:
        for n in mat.node_tree.nodes:
            item = {"type": n.type, "name": n.name}
            for inp in n.inputs:
                if inp.name in ("Base Color", "Roughness", "Metallic", "IOR", "Normal"):
                    try: item[inp.name] = tuple(inp.default_value) if hasattr(inp.default_value, "__len__") else inp.default_value
                    except: pass
            d["nodes"].append(item)
    data["materials"].append(d)
print(json.dumps(data, indent=2, default=str))
