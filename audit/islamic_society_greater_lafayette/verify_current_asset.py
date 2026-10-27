"""Fresh-process, exact-hash inspection of the current ISGL asset."""
import bpy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_islamic_societyof_greater_lafayette_0130012"
ASSET = ROOT / "modular" / "buildings" / (ASSET_ID + ".blend")
SOURCE_AUDIT = ROOT / "audit" / ASSET_ID
GIS = SOURCE_AUDIT / "sources" / "purdue_gis_FID771_SOMSA.json"
OLD_REOPEN = SOURCE_AUDIT / "independent_grade" / "r2" / "reopen_validation.json"
OUT = ROOT / "audit" / "islamic_society_greater_lafayette" / "current_asset_fresh_open.json"
EXPECTED_SCENE = "Building_" + ASSET_ID
EXPECTED_COLLECTION = "Asset_" + ASSET_ID

def lonlat_to_xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)

def main():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.context.scene
    collection = bpy.data.collections.get(EXPECTED_COLLECTION)
    objects = list(collection.objects) if collection else []
    meshes = [obj for obj in objects if obj.type == "MESH"]
    mesh = bpy.data.objects.get("Islamic Society of Greater Lafayette")
    mesh = mesh if mesh in objects and mesh.type == "MESH" else None
    gis = json.loads(GIS.read_text(encoding="utf-8"))
    feature = gis["features"][0]
    ring = feature["geometry"]["rings"][0]
    if ring[0] == ring[-1]:
        ring = ring[:-1]
    ring_xy = [lonlat_to_xy(lon, lat) for lon, lat in ring]
    shell_xy = []
    points = []
    if mesh:
        for vertex in mesh.data.vertices:
            world = mesh.matrix_world @ vertex.co
            points.append(world)
            if abs(world.z) < 1e-5:
                shell_xy.append((world.x, world.y))
    ring_errors = [min((math.hypot(x-gx, y-gy) for x, y in shell_xy), default=None)
                   for gx, gy in ring_xy]
    bounds = ([[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
              if points else None)
    file_sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    external_images = []
    for image in bpy.data.images:
        if image.source == "FILE" and not image.packed_file:
            resolved = Path(bpy.path.abspath(image.filepath)).resolve()
            external_images.append({"filepath": image.filepath, "resolved": str(resolved),
                                    "exists": resolved.exists()})
    linked_libraries = [lib.filepath for lib in bpy.data.libraries]
    materials = sorted({slot.material.name for obj in meshes for slot in obj.material_slots
                        if slot.material is not None})
    old = json.loads(OLD_REOPEN.read_text(encoding="utf-8"))
    same_probe = {
        "scene": scene.name == old.get("scene"),
        "collection": EXPECTED_COLLECTION == old.get("collection"),
        "mesh_vertex_count": len(mesh.data.vertices) == old.get("mesh_vertices") if mesh else False,
        "mesh_face_count": len(mesh.data.polygons) == old.get("mesh_faces") if mesh else False,
        "bounds_world_m": bounds == old.get("bounds_world_m"),
    }
    interior = bpy.data.objects.get("ISGL_Schematic_Interior_Open_Gathering_Space_Floor")
    interior_label = bpy.data.objects.get("ISGL_Schematic_Interior_Label")
    checks = {
        "scene_name": scene.name == EXPECTED_SCENE,
        "expected_collection_exists": collection is not None,
        "stable_structural_mesh_present": mesh is not None and len(mesh.data.vertices) == 982 and len(mesh.data.polygons) == 747,
        "stable_export_name": mesh is not None and mesh.name == "Islamic Society of Greater Lafayette",
        "schematic_interior_and_label_present": interior is not None and interior_label is not None and interior.get("accuracy_status") == "schematic; no verified floor plan",
        "gis_fid_and_abbreviation": feature["attributes"].get("FID") == 771 and feature["attributes"].get("BLDG_ABBR") == "SOMSA",
        "eleven_shell_vertices_match_within_0_00002m": len(ring_errors) == 11 and max(ring_errors, default=float("inf")) <= 0.00002,
        "no_missing_external_images": all(item["exists"] for item in external_images),
        "no_linked_libraries": not linked_libraries,
        "same_structural_probe_as_historical_r2": all(same_probe.values()),
    }
    result = {
        "fresh_open": "PASS" if all(checks.values()) else "FAIL",
        "opened_asset": str(ASSET),
        "asset_sha256": file_sha,
        "historical_r2_asset_sha256": None,
        "historical_r2_sha_verification": "not possible: the R2 result and reopen JSON record no asset SHA",
        "blender_version": bpy.app.version_string,
        "scene": scene.name,
        "collection": EXPECTED_COLLECTION,
        "object_names": [obj.name for obj in objects],
        "object_count": len(objects),
        "collection_mesh_object_count": len(meshes),
        "schematic_interior": {
            "object": interior.name if interior else None,
            "dimensions_m": [round(float(v), 4) for v in interior.dimensions] if interior else None,
            "accuracy_status": interior.get("accuracy_status") if interior else None,
            "layout_note": interior.get("layout_note") if interior else None,
            "label_object": interior_label.name if interior_label else None,
        },
        "mesh_vertices": len(mesh.data.vertices) if mesh else None,
        "mesh_faces": len(mesh.data.polygons) if mesh else None,
        "material_names": materials,
        "material_count": len(materials),
        "mesh_material_slots_without_material": [
            {"object": obj.name, "slot_index": index}
            for obj in meshes for index, slot in enumerate(obj.material_slots)
            if slot.material is None
        ],
        "bounds_world_m": bounds,
        "gis_feature": {"fid": feature["attributes"].get("FID"),
                        "abbr": feature["attributes"].get("BLDG_ABBR"),
                        "name": feature["attributes"].get("BUILDING_N"),
                        "address": feature["attributes"].get("ADDRESS"),
                        "source_ring_vertices_excluding_closure": len(ring_xy)},
        "gis_shell_vertex_nearest_error_m": {"per_vertex": ring_errors,
                                            "maximum": max(ring_errors, default=None)},
        "unpacked_external_images": external_images,
        "linked_libraries": linked_libraries,
        "historical_r2_structural_probe_comparison": same_probe,
        "checks": checks,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not all(checks.values()):
        raise RuntimeError("One or more fresh-open checks failed")

main()
