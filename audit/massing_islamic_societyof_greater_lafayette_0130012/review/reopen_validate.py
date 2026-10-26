"""Fresh-process direct reopen validation for the ISGL Blender asset."""
import bpy
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET_ID = "massing_islamic_societyof_greater_lafayette_0130012"
ASSET = ROOT / "modular" / "buildings" / (ASSET_ID + ".blend")
AUDIT = ROOT / "audit" / ASSET_ID
GIS = AUDIT / "sources" / "purdue_gis_FID771_SOMSA.json"
OUT = AUDIT / "review" / "reopen_validation.json"
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
    meshes = [o for o in objects if o.type == "MESH"]
    mesh = meshes[0] if len(meshes) == 1 else None
    linked_images = [im.filepath for im in bpy.data.images
                     if im.source == "FILE" and not im.packed_file]
    linked_libraries = [lib.filepath for lib in bpy.data.libraries]
    gis_data = json.loads(GIS.read_text(encoding="utf-8"))
    feature = gis_data["features"][0]
    ring_ll = feature["geometry"]["rings"][0]
    if ring_ll[0] == ring_ll[-1]:
        ring_ll = ring_ll[:-1]
    ring_xy = [lonlat_to_xy(lon, lat) for lon, lat in ring_ll]
    base_xy = []
    if mesh:
        for v in mesh.data.vertices:
            co = mesh.matrix_world @ v.co
            if abs(co.z) < 1e-5:
                base_xy.append((co.x, co.y))
    nearest = [min((math.hypot(x-gx, y-gy) for x,y in base_xy), default=None)
               for gx,gy in ring_xy]
    bounds = None
    if mesh:
        coords = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
        bounds = [[min(c[i] for c in coords), max(c[i] for c in coords)] for i in range(3)]
    expected_renders = [
        "isgl_exterior_approach.png", "isgl_front_elevation.png", "isgl_roof_plan.png"
    ]
    renders = {name: {"exists": (AUDIT / "renders" / name).is_file(),
                      "bytes": ((AUDIT / "renders" / name).stat().st_size
                                if (AUDIT / "renders" / name).is_file() else 0)}
               for name in expected_renders}
    checks = {
        "asset_file_exists": ASSET.is_file(),
        "scene_name": scene.name == EXPECTED_SCENE,
        "expected_collection_exists": collection is not None,
        "exactly_one_collection_object": len(objects) == 1,
        "exactly_one_mesh": len(meshes) == 1,
        "one_object_expected_name": len(objects) == 1 and objects[0].name == "Islamic Society of Greater Lafayette",
        "no_modifiers": mesh is not None and len(mesh.modifiers) == 0,
        "no_external_images": len(linked_images) == 0,
        "no_linked_libraries": len(linked_libraries) == 0,
        "gis_identity_fid_771_somsa": feature["attributes"].get("FID") == 771 and feature["attributes"].get("BLDG_ABBR") == "SOMSA",
        "gis_shell_vertices_within_0_00002m": len(nearest) == 11 and max(nearest, default=float("inf")) <= 0.00002,
        "all_three_renders_present": all(v["exists"] and v["bytes"] > 10000 for v in renders.values()),
    }
    result = {
        "validation": "passed" if all(checks.values()) else "failed",
        "opened_asset": str(ASSET),
        "blender_version": bpy.app.version_string,
        "scene": scene.name,
        "collection": EXPECTED_COLLECTION,
        "object_names": [o.name for o in objects],
        "object_count": len(objects),
        "mesh_vertices": len(mesh.data.vertices) if mesh else None,
        "mesh_faces": len(mesh.data.polygons) if mesh else None,
        "bounds_world_m": bounds,
        "gis_feature": {"fid": feature["attributes"].get("FID"),
                        "bldg_abbr": feature["attributes"].get("BLDG_ABBR"),
                        "ring_vertices_excluding_closure": len(ring_xy)},
        "gis_shell_vertex_nearest_error_m": {
            "per_vertex": nearest,
            "maximum": max(nearest, default=None),
        },
        "unpacked_external_images": linked_images,
        "linked_libraries": linked_libraries,
        "render_files": renders,
        "checks": checks,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not all(checks.values()):
        raise RuntimeError("One or more direct reopen validation checks failed")

main()
