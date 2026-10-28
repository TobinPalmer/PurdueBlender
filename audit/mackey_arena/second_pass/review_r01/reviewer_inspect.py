import bpy, json, sys, os, collections, mathutils
out = sys.argv[sys.argv.index("--")+1]
d = {}
d["filepath"] = bpy.data.filepath
d["collections"] = [c.name for c in bpy.data.collections]
col = bpy.data.collections.get("Asset_mackey_arena")
d["asset_coll_objects"] = len(col.all_objects) if col else None
root = bpy.data.objects.get("AssetRoot_mackey_arena")
d["root"] = None if not root else {"loc": list(root.location), "rot": list(root.rotation_euler), "scale": list(root.scale), "in_coll": root.name in col.all_objects if col else None}
d["libraries"] = [l.filepath for l in bpy.data.libraries]
d["images"] = [(i.name, i.filepath, i.packed_file is not None) for i in bpy.data.images]
d["texts"] = [(t.name, t.use_module) for t in bpy.data.texts]
d["scenes"] = [s.name for s in bpy.data.scenes]
d["objects_not_in_asset_coll"] = [o.name for o in bpy.data.objects if col and o.name not in col.all_objects]
# prefix counts
pc = collections.Counter()
for o in bpy.data.objects:
    n = o.name
    parts = n.split("_")
    pc["_".join(parts[:3])] += 1
d["prefix_counts"] = dict(pc.most_common())
objs = []
for o in bpy.data.objects:
    if o.type != "MESH": continue
    bb = [o.matrix_world @ mathutils.Vector(c) for c in o.bound_box]
    lo = [min(v[i] for v in bb) for i in range(3)]; hi = [max(v[i] for v in bb) for i in range(3)]
    objs.append({"name": o.name, "lo": [round(x,2) for x in lo], "hi": [round(x,2) for x in hi], "verts": len(o.data.vertices), "polys": len(o.data.polygons), "mats": [m.name for m in o.data.materials if m], "hide_render": o.hide_render, "parent": o.parent.name if o.parent else None})
d["mesh_objects"] = objs
mats = {}
for m in bpy.data.materials:
    if not m.use_nodes or not m.node_tree: continue
    b = next((n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED"), None)
    info = {}
    if b:
        bc = b.inputs["Base Color"]
        info["base"] = list(bc.default_value)[:3]
        info["base_linked"] = bc.is_linked
        info["rough"] = b.inputs["Roughness"].default_value
        info["metal"] = b.inputs["Metallic"].default_value
        try: info["alpha"] = b.inputs["Alpha"].default_value
        except: pass
        try: info["transmission"] = b.inputs["Transmission Weight"].default_value
        except: pass
    info["nodes"] = sorted(set(n.type for n in m.node_tree.nodes))
    mats[m.name] = info
d["materials"] = mats
json.dump(d, open(out, "w"), indent=1)
print("OK")
