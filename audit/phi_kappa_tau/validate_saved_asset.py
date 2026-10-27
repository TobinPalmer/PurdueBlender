"""Fresh-open structural, footprint and portability checks for Phi Kappa Tau."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
import bmesh


ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_phi_kappa_tau_139b9d7"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
SOURCE_PATH = ROOT / "audit" / "phi_kappa_tau" / "fid820_arcgis_snapshot.json"
OUT_PATH = ROOT / "audit" / "phi_kappa_tau" / "fresh_reopen_validation.json"
EXPECTED_COLLECTION = f"Asset_{ASSET_ID}"
EXPECTED_SCENE = f"Building_{ASSET_ID}"

LAT0, LON0 = 40.4274, -86.9137
R = 6378137.0
LON_M = 111412.84 * math.cos(math.radians(LAT0))
LAT_M = 111040.0


def local_xy(x, y):
    lon = math.degrees(x / R)
    lat = math.degrees(2.0 * math.atan(math.exp(y / R)) - math.pi / 2.0)
    return (lon - LON0) * LON_M, (lat - LAT0) * LAT_M


def main():
    report = {
        "asset": str(ASSET_PATH.relative_to(ROOT)).replace("\\", "/"),
        "fresh_process": True,
        "saved_path_opened": str(Path(bpy.data.filepath).resolve()),
        "scene_names": sorted(scene.name for scene in bpy.data.scenes),
        "scene_ok": bpy.context.scene is not None and bpy.context.scene.name == EXPECTED_SCENE,
        "expected_scene": EXPECTED_SCENE,
        "expected_collection": EXPECTED_COLLECTION,
        "errors": [],
    }
    coll = bpy.data.collections.get(EXPECTED_COLLECTION)
    obj = bpy.data.objects.get("Phi Kappa Tau")
    report["collection_ok"] = coll is not None
    report["object_ok"] = obj is not None and obj.type == "MESH"
    report["collection_object_names"] = sorted(o.name for o in coll.objects) if coll else []
    report["object_count"] = len(coll.objects) if coll else 0
    if not report["scene_ok"]:
        report["errors"].append("Expected scene is missing or not active")
    if not coll or not obj or obj.name not in coll.objects:
        report["errors"].append("Expected mesh object/collection link is missing")
    if obj:
        report["object_type"] = obj.type
        report["object_transform"] = {
            "location": [float(v) for v in obj.location],
            "rotation_euler": [float(v) for v in obj.rotation_euler],
            "scale": [float(v) for v in obj.scale],
        }
        report["asset_metadata"] = {k: obj.get(k) for k in
            ("asset_id", "source_feature", "footprint_source_crs", "height_status", "placement_status")}
        report["material_names"] = sorted({m.name for m in obj.data.materials if m})
        report["mesh_vertices"] = len(obj.data.vertices)
        report["mesh_edges"] = len(obj.data.edges)
        report["mesh_faces"] = len(obj.data.polygons)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        report["nonmanifold_edge_count"] = sum(1 for e in bm.edges if not e.is_manifold)
        report["loose_edge_count"] = sum(1 for e in bm.edges if not e.link_faces)
        bm.free()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        ev = obj.evaluated_get(depsgraph)
        coords = [ev.matrix_world @ v.co for v in ev.to_mesh().vertices]
        ev.to_mesh_clear()
        bounds = [[min(float(p[i]) for p in coords), max(float(p[i]) for p in coords)] for i in range(3)]
        report["evaluated_bounds_world_m"] = bounds
        # The registered FID 820 ring is the wall and foundation perimeter at z=.78.
        src = json.loads(SOURCE_PATH.read_text(encoding="utf-8-sig"))
        feature = next(f for f in src["features"] if f["attributes"].get("FID") == 820)
        ring = feature["geometry"]["rings"][0]
        expected = [local_xy(float(x), float(y)) for x, y in ring]
        if math.dist(expected[0], expected[-1]) < 1e-5:
            expected.pop()
        zring = []
        for v in obj.data.vertices:
            p = obj.matrix_world @ v.co
            if abs(p.z - 0.78) < 2e-4:
                xy = (float(p.x), float(p.y))
                if not any(math.dist(xy, q) < 1e-5 for q in zring):
                    zring.append(xy)
        errors = []
        for p in expected:
            errors.append(min((math.dist(p, q) for q in zring), default=float("inf")))
        report["gis_wall_ring_xy_m"] = [[float(x), float(y)] for x, y in expected]
        report["wall_ring_vertex_count_expected"] = len(expected)
        report["wall_ring_vertex_count_found_at_z_0_78"] = len(zring)
        report["wall_ring_max_nearest_error_m"] = max(errors, default=float("inf"))
        report["wall_ring_pass_0_01m"] = (
            len(expected) == len(zring) and max(errors, default=float("inf")) <= 0.01
        )
        if not report["wall_ring_pass_0_01m"]:
            report["errors"].append("Evaluated wall ring does not match the FID 820 polygon within 0.01 m")
    image_paths = sorted({str(Path(i.filepath).as_posix()) for i in bpy.data.images
                          if i.source == "FILE" and i.filepath and not i.packed_file})
    report["unpacked_external_image_paths"] = image_paths
    report["portable_images_pass"] = len(image_paths) == 0
    if image_paths:
        report["errors"].append("Unpacked external image dependencies are present")
    report["asset_sha256"] = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
    report["asset_size_bytes"] = ASSET_PATH.stat().st_size
    report["result"] = "PASS" if not report["errors"] else "FAIL"
    OUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["errors"]:
        raise RuntimeError("Phi Kappa Tau fresh-open validation failed")


if __name__ == "__main__":
    main()
