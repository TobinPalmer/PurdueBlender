"""Fresh-open check that R9 exports building-owned geometry only."""
import bpy, hashlib, json
from pathlib import Path

candidate = Path(bpy.data.filepath).resolve()
root = Path(__file__).resolve().parents[2]
audit = root / "audit" / "lambert_fieldhouse"
context_names = {"LAMB | Stadium sidewalk round4", "LAMB | Stadium curb round4", "LAMB | Stadium Avenue roadway round4"}
collection = bpy.data.collections.get("Asset_lambert_fieldhouse")
assert collection is not None, "Expected building export collection is missing"
objects = list(collection.all_objects)
remaining_context = sorted(o.name for o in objects if o.name in context_names)
unassigned = sorted(o.name for o in objects if o.type == "MESH" and (not o.data.materials or all(m is None for m in o.data.materials)))
hurdles = [o for o in objects if o.type == "MESH" and o.name.startswith("LAMB | R8 event hurdle")]
unassigned_hurdles = sorted(o.name for o in hurdles if not o.data.materials or all(m is None for m in o.data.materials))
track = bpy.data.objects.get("LAMB | 6-lane 200 m stadium track surface")
assert track is not None and len(track.data.vertices) % 2 == 0, "Track centerline geometry is not measurable"
n = len(track.data.vertices) // 2
centers = [(track.data.vertices[i].co + track.data.vertices[i+n].co) * .5 for i in range(n)]
perimeter = sum((centers[(i+1) % n] - centers[i]).length for i in range(n))
packed_images = sorted({im.name for im in bpy.data.images if im.source == "FILE" and im.packed_file})
external_unpacked = sorted(im.name for im in bpy.data.images if im.source == "FILE" and not im.packed_file)
linked_libraries = [lib.filepath for lib in bpy.data.libraries]
assert not remaining_context, f"Non-building context remains in export: {remaining_context}"
assert not unassigned, f"Meshes have no material: {unassigned}"
assert not unassigned_hurdles, f"Hurdles have no material: {unassigned_hurdles}"
assert abs(perimeter - 199.98895672145127) < 0.01, f"Track centerline changed: {perimeter}"
assert not linked_libraries, f"Linked libraries are not portable: {linked_libraries}"
result = {
    "fresh_open_candidate": str(candidate),
    "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
    "export_collection": collection.name,
    "collection_objects": len(objects),
    "collection_meshes": sum(o.type == "MESH" for o in objects),
    "remaining_nonbuilding_site_context_meshes": remaining_context,
    "unassigned_meshes": unassigned,
    "hurdle_mesh_count": len(hurdles),
    "unassigned_hurdle_meshes": unassigned_hurdles,
    "lane_one_centerline_perimeter_m": perimeter,
    "packed_images": packed_images,
    "unpacked_external_images": external_unpacked,
    "linked_libraries": linked_libraries,
    "status": "PASS"
}
validation_path = audit / "validation_round9.json"
validation = json.loads(validation_path.read_text(encoding="utf-8"))
validation["site_context_cleanup_fresh_open"] = result
validation["sha256"] = result["candidate_sha256"]
validation_path.write_text(json.dumps(validation, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
