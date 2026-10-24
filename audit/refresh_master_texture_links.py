"""Reload the linked building libraries, validate them, and save the campus master."""
import bpy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULAR = ROOT / "modular"
manifest = json.loads((MODULAR / "manifest.json").read_text(encoding="utf-8"))
records = [r for r in manifest["assets"] if r.get("kind") == "detailed"]
errors = []
rows = []

for record in records:
    expected = (MODULAR / record["file"]).resolve()
    collection = bpy.data.collections.get(record["collection"])
    marker = bpy.data.objects.get(f"Placement_{record['id']}")
    if collection is None:
        errors.append(f"missing linked collection {record['collection']}")
        continue
    if collection.library is None:
        errors.append(f"collection is local, expected linked library: {record['collection']}")
        continue
    actual = Path(bpy.path.abspath(collection.library.filepath)).resolve()
    if actual != expected:
        errors.append(f"wrong library for {record['id']}: {actual}")
    if marker is None or marker.instance_collection != collection:
        errors.append(f"missing or incorrect placement instance for {record['id']}")
    mats = {}
    for obj in collection.all_objects:
        for slot in obj.material_slots:
            mat = slot.material
            if mat is None:
                continue
            mats[mat.name] = mat
    textured = 0
    for mat in mats.values():
        if not mat.use_nodes or mat.node_tree is None:
            continue
        sources = {n for n in mat.node_tree.nodes if n.type in {
            "TEX_NOISE", "TEX_BRICK", "TEX_WAVE", "TEX_IMAGE", "TEX_CHECKER",
            "TEX_VORONOI", "TEX_MAGIC", "TEX_MUSGRAVE", "TEX_ENVIRONMENT",
        }}
        upstream = set()
        pending = [link.from_node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"
                   for socket in node.inputs for link in socket.links]
        while pending:
            node = pending.pop()
            if node in upstream:
                continue
            upstream.add(node)
            pending.extend(link.from_node for socket in node.inputs for link in socket.links)
        if sources & upstream:
            textured += 1
    rows.append({
        "id": record["id"],
        "library": str(actual),
        "source_exists": expected.exists(),
        "marker_matches": marker is not None and marker.instance_collection == collection,
        "object_count": len(collection.all_objects),
        "used_material_count": len(mats),
        "materials_with_connected_texture": textured,
    })

if len(rows) != len(records):
    errors.append(f"only checked {len(rows)} of {len(records)} detailed linked buildings")
if any(not row["source_exists"] for row in rows):
    errors.extend(f"missing source file: {row['id']}" for row in rows if not row["source_exists"])

result = {
    "status": "PASS" if not errors else "FAIL",
    "master": str(Path(bpy.data.filepath).resolve()),
    "master_reopened_and_saved": False,
    "detailed_buildings_linked": len(rows),
    "placement_markers": sum(o.name.startswith("Placement_") for o in bpy.context.scene.objects),
    "errors": errors,
    "buildings": rows,
}
if errors:
    raise RuntimeError("Master texture-link verification failed: " + "; ".join(errors))

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
result["master_reopened_and_saved"] = True
(ROOT / "audit" / "master_texture_link_refresh.json").write_text(
    json.dumps(result, indent=2), encoding="utf-8"
)
print(json.dumps({k: v for k, v in result.items() if k != "buildings"}))
