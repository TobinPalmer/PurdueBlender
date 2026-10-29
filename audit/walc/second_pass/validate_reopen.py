"""blender -b <asset> --python validate_reopen.py -- <out.json> <collection> <root_name> [<prefix_for_generated>]
Reopen-validation for second-pass assets: collection, parenting, libraries, external paths, bounds."""
import bpy, sys, json, hashlib, mathutils, os

argv = sys.argv[sys.argv.index("--") + 1:]
out, coll_name, root_name = argv[0], argv[1], argv[2]
gen = argv[3] if len(argv) > 3 else None
coll = bpy.data.collections.get(coll_name)
res = {"asset": bpy.data.filepath, "asset_sha256": hashlib.sha256(open(bpy.data.filepath, "rb").read()).hexdigest(),
       "blender": bpy.app.version_string, "collection_present": coll is not None}
if coll:
    objs = list(coll.all_objects)
    res["collection_object_count"] = len(objs)
    root = bpy.data.objects.get(root_name)
    res["root_present"] = root is not None
    if root:
        res["root_location"] = list(root.location)
    orphans = [o.name for o in objs if o.parent is None and o.name != root_name]
    res["objects_without_parent"] = orphans[:50]
    res["objects_without_parent_count"] = len(orphans)
    if gen:
        g = [o for o in objs if o.name.startswith(gen)]
        res["generated_objects"] = len(g)
        res["generated_not_parented_to_root"] = [o.name for o in g if o.parent is None or o.parent.name != root_name]
    lo = mathutils.Vector((1e9,) * 3); hi = -lo
    tris = 0
    dg = bpy.context.evaluated_depsgraph_get()
    for o in objs:
        if o.type != "MESH":
            continue
        for c in o.bound_box:
            v = o.matrix_world @ mathutils.Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], v[i]); hi[i] = max(hi[i], v[i])
        tris += sum(len(p.vertices) - 2 for p in o.evaluated_get(dg).data.polygons)
    res["mesh_bounds_local"] = [list(lo), list(hi)]
    res["triangles"] = tris
    res["objects_outside_collection"] = [o.name for o in bpy.data.objects if coll_name not in [c.name for c in o.users_collection]][:50]
res["libraries"] = [l.filepath for l in bpy.data.libraries]
res["images"] = [{"name": i.name, "filepath": i.filepath, "packed": i.packed_file is not None} for i in bpy.data.images if i.source == "FILE"]
res["external_absolute_paths"] = [i.filepath for i in bpy.data.images if i.source == "FILE" and i.packed_file is None and os.path.isabs(bpy.path.abspath(i.filepath)) and not i.filepath.startswith("//")]
res["scenes"] = [s.name for s in bpy.data.scenes]
res["python_autorun_texts"] = [t.name for t in bpy.data.texts if t.use_module]
res["pass"] = bool(coll) and res.get("root_present") and not res["libraries"] and not res["external_absolute_paths"] and not res["python_autorun_texts"] and (not gen or not res["generated_not_parented_to_root"])
json.dump(res, open(out, "w"), indent=1)
print("VALIDATE", res["pass"], res.get("collection_object_count"), res["asset_sha256"])
