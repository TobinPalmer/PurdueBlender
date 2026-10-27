"""Reopen-time validation for the Philip E. Nelson Hall modular asset."""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ASSET_ID = "massing_philip_e_nelson_hall_of_food_science_nlsn_6b2ba6b"
ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / ASSET_ID
OBJECT_NAME = "Philip E. Nelson Hall of Food Science (NLSN)"
COLLECTION_NAME = "Asset_" + ASSET_ID
EXPECTED_MESH_NAME = ASSET_ID + "_mesh"

def check(name, passed, evidence, finding=None):
    return {"name": name, "passed": bool(passed), "evidence": evidence,
            "finding": finding if finding else (None if passed else "Check failed")}

def main():
    checks = []
    coll = bpy.data.collections.get(COLLECTION_NAME)
    obj = bpy.data.objects.get(OBJECT_NAME)
    checks.append(check("expected_collection", coll is not None,
                        {"expected": COLLECTION_NAME, "present": coll.name if coll else None}))
    checks.append(check("expected_object", obj is not None and obj.type == "MESH",
                        {"expected": OBJECT_NAME, "type": obj.type if obj else None,
                         "present": obj.name if obj else None}))

    meshes = [o for o in (coll.objects if coll else []) if o.type == "MESH"]
    checks.append(check("single_object_export", len(meshes) == 1 and meshes[0] == obj,
                        {"mesh_objects": [o.name for o in meshes], "count": len(meshes)}))
    if obj:
        checks.append(check("identity_transform", tuple(obj.location) == (0.0, 0.0, 0.0)
                            and tuple(obj.rotation_euler) == (0.0, 0.0, 0.0)
                            and tuple(obj.scale) == (1.0, 1.0, 1.0),
                            {"location": list(obj.location), "rotation": list(obj.rotation_euler),
                             "scale": list(obj.scale), "parent": obj.parent.name if obj.parent else None}))
        checks.append(check("manifest_object_name_and_mesh", obj.data.name == EXPECTED_MESH_NAME,
                            {"mesh": obj.data.name, "vertices": len(obj.data.vertices),
                             "faces": len(obj.data.polygons), "modifiers": [m.name for m in obj.modifiers]}))
        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated = obj.evaluated_get(depsgraph)
        bounds = [[min((evaluated.matrix_world @ Vector(c))[i] for c in evaluated.bound_box),
                   max((evaluated.matrix_world @ Vector(c))[i] for c in evaluated.bound_box)]
                  for i in range(3)]
        checks.append(check("evaluated_bounds", bounds[0][0] < -179 and bounds[0][1] > -125
                            and bounds[1][0] < -681 and bounds[1][1] > -615
                            and abs(bounds[2][0]) < 0.01 and bounds[2][1] > 16.0,
                            {"bounds_world_m": bounds,
                             "note": "Outer bounds include the estimated entrance canopy and raised gable."}))
        texture_images = [im.name for im in bpy.data.images if im.source == "FILE"]
        linked_libraries = [lib.filepath for lib in bpy.data.libraries]
        checks.append(check("portable_materials", not texture_images and not linked_libraries,
                            {"file_images": texture_images, "linked_libraries": linked_libraries,
                             "materials": [m.name for m in obj.data.materials]}))
        active_mesh_count = len([o for o in bpy.data.objects if o.type == "MESH"])
        checks.append(check("no_unrelated_mesh_objects", active_mesh_count == 1,
                            {"mesh_object_count_in_file": active_mesh_count}))
    else:
        bounds = None

    output = {
        "asset_id": ASSET_ID,
        "asset_path": bpy.data.filepath,
        "blender_version": bpy.app.version_string,
        "reopened_saved_asset": True,
        "score": sum(1 for c in checks if c["passed"]),
        "max_score": len(checks),
        "checks": checks,
        "findings": [c["finding"] for c in checks if c["finding"]],
        "geometry_bounds_world_m": bounds,
        "criteria_note": "This is an asset/portability validation, not an independent architectural fidelity grade."
    }
    (AUDIT / "reopen_validation.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
