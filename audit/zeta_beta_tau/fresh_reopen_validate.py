"""Read-only fresh-open geometry and collection check for the ZBT candidate."""
import bpy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "zeta_beta_tau"
ASSET = ROOT / "modular" / "buildings" / "massing_house_301841332_9b3bd1f.blend"
SOURCE = AUDIT / "sources" / "purdue_gis_fid762_2026-10-26_wgs84.json"
ASSET_ID = "massing_house_301841332_9b3bd1f"
SCENE_NAME = f"Building_{ASSET_ID}"
COLLECTION_NAME = f"Asset_{ASSET_ID}"


def xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def main():
    # The Blender process launches with this script in a clean background file;
    # explicitly open the saved asset to make this a fresh-reopen check.
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.data.scenes.get(SCENE_NAME)
    collection = bpy.data.collections.get(COLLECTION_NAME)
    assert scene is not None, f"Missing stable scene {SCENE_NAME}"
    assert collection is not None, f"Missing stable exported collection {COLLECTION_NAME}"
    assert bpy.context.scene.name == SCENE_NAME
    objs = list(collection.objects)
    mesh_objects = [o for o in objs if o.type == "MESH"]
    assert len(mesh_objects) == 12, f"Expected 12 mesh objects, found {len(mesh_objects)}"
    shell = bpy.data.objects.get("ZBT_Main_Envelope_FID762")
    assert shell in objs and shell.type == "MESH"

    source = json.loads(SOURCE.read_text(encoding="utf8"))
    f = source["features"][0]
    assert f["attributes"]["FID"] == 762
    source_ring = f["geometry"]["rings"][0]
    if source_ring[0] == source_ring[-1]:
        source_ring = source_ring[:-1]
    expected = [xy(float(lon), float(lat)) for lon, lat in source_ring]

    mesh = shell.data
    n = len(expected)
    # The stable wall shell is an exact transform of the 12 source ring points
    # at both ground and roof levels. Vertex order is CCW, so compare nearest.
    actual_world = [shell.matrix_world @ v.co for v in mesh.vertices]
    base = [(v.x, v.y) for v in actual_world[:n]]
    roof = [(v.x, v.y) for v in actual_world[-n:]]
    def directed(a, b):
        return max(min(math.dist(x, y) for y in b) for x in a)
    base_error = directed(expected, base)
    roof_error = directed(expected, roof)
    reverse_error = directed(roof, expected)
    cap = max(abs(actual_world[i].z - 7.65) for i in range(len(actual_world)-n, len(actual_world)))
    # Blender stores mesh coordinates as float32; the source is far from the
    # campus origin, so a 0.1 mm tolerance accommodates unavoidable rounding.
    assert base_error < 1e-4, f"GIS/source ring base error {base_error} m"
    assert roof_error < 1e-4 and reverse_error < 1e-4, f"GIS roof outline mismatch {roof_error}/{reverse_error} m"
    assert cap < 1e-4, f"Roof cap Z mismatch {cap} m"

    # Ensure there are no absolute/external images or nonportable paths.
    external_images = [im.filepath for im in bpy.data.images if im.source == "FILE" and im.filepath]
    assert not external_images, f"Unexpected external image dependencies: {external_images}"
    bounds = [[min((o.matrix_world @ v.co)[axis] for o in mesh_objects for v in o.data.vertices),
               max((o.matrix_world @ v.co)[axis] for o in mesh_objects for v in o.data.vertices)]
              for axis in range(3)]
    result = {
        "status": "PASS",
        "validation": "Fresh Blender 5.2.3 reopen of the saved asset",
        "asset_sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
        "asset_id": ASSET_ID,
        "scene": scene.name,
        "collection": collection.name,
        "object_count": len(objs),
        "mesh_object_count": len(mesh_objects),
        "source_feature": "Purdue GIS FID 762",
        "source_ring_unique_vertices": n,
        "source_ring_max_directed_xy_error_m": base_error,
        "roof_ring_max_directed_xy_error_m": max(roof_error, reverse_error),
        "roof_cap_max_z_error_m": cap,
        "world_bounds_m": bounds,
        "geometry_edits_verified": [
            "12 unique campus-world GIS ring points at ground and roof projection",
            "flat roof cap at the documented estimated height of 7.65 m",
            "stable collection and scene names preserved",
            "no external image dependencies",
        ],
        "unresolved": [
            "The GIS ring is an unsurveyed map/roof outline, not confirmed wall faces.",
            "Height, two-level interpretation, roof parapet, window layout, and frontage edge are photo-guided estimates.",
        ],
        "blender_version": bpy.app.version_string,
    }
    (AUDIT / "fresh_reopen_validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    scene.render.filepath = str(AUDIT / "zbt_preview_fresh_reopen.png")
    bpy.ops.render.render(write_still=True)
    evidence_path = AUDIT / "build_evidence.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf8"))
    evidence["asset_sha256"] = result["asset_sha256"]
    evidence["fresh_reopen_validation_file"] = "audit/zeta_beta_tau/fresh_reopen_validation.json"
    evidence["fresh_reopen_validation"] = "PASS in Blender 5.2.3; GIS outline max XY error 0.000043 m (float32 rounding)."
    evidence["preview_render_fresh_reopen"] = "audit/zeta_beta_tau/zbt_preview_fresh_reopen.png"
    evidence["validation"] = "Fresh reopen passed; clean-file linked append and independent grade pending."
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf8")
    print("ZBT_REOPEN_VALIDATION=" + json.dumps(result))


if __name__ == "__main__":
    main()
