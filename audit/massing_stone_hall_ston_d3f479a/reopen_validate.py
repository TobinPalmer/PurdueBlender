"""Run with Blender background after build to verify the saved Stone Hall asset."""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy


BUILDING_ID = "massing_stone_hall_ston_d3f479a"
ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / f"{BUILDING_ID}.blend"
AUDIT = ROOT / "audit" / BUILDING_ID
SOURCE = AUDIT / "sources" / "purdue_building_gis_fid240_ston_4326.json"
OUTPUT = AUDIT / "reopen_validation.json"
COLLECTION = f"Asset_{BUILDING_ID}"
SCENE = f"Building_{BUILDING_ID}"


def transform_ring(ring):
    lat0, lon0 = 40.4274, -86.9137
    sx = 111412.84 * math.cos(math.radians(lat0))
    sy = 111040.0
    out = []
    for lon, lat in ring:
        p = ((lon - lon0) * sx, (lat - lat0) * sy)
        if not out or math.dist(out[-1], p) > 1e-6:
            out.append(p)
    if len(out) > 2 and math.dist(out[0], out[-1]) < 1e-6:
        out.pop()
    return out


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.context.scene
    coll = bpy.data.collections.get(COLLECTION)
    owned = list(coll.objects) if coll else []
    meshes = [o for o in owned if o.type == "MESH"]
    obj = meshes[0] if len(meshes) == 1 else None
    issues = []
    if scene.name != SCENE:
        issues.append(f"scene mismatch: {scene.name!r} != {SCENE!r}")
    if coll is None:
        issues.append("expected exported collection is missing")
    if len(owned) != 1 or obj is None:
        issues.append(f"expected one mesh object in collection; found {len(owned)} owned objects / {len(meshes)} meshes")
    elif obj.name != "Stone Hall (STON)":
        issues.append(f"object name mismatch: {obj.name}")

    report = {"building_id": BUILDING_ID, "asset": str(ASSET.relative_to(ROOT)).replace("\\", "/"), "scene": scene.name,
              "collection_present": coll is not None, "collection_object_count": len(owned), "object_names": [o.name for o in owned],
              "render_engine": scene.render.engine, "external_image_dependencies": [], "issues": issues}
    if obj:
        n = int(obj.get("footprint_ring_vertices", 0))
        with SOURCE.open("r", encoding="utf-8-sig") as f:
            feature = json.load(f)["features"][0]
        source_points = transform_ring(feature["geometry"]["rings"][0])
        mesh_points = [(obj.data.vertices[i].co.x, obj.data.vertices[i].co.y) for i in range(min(n, len(obj.data.vertices)))]
        source_sorted = sorted(source_points)
        mesh_sorted = sorted(mesh_points)
        mismatch = (len(source_sorted) != len(mesh_sorted) or
                    (len(source_sorted) == len(mesh_sorted) and any(math.dist(a, b) > 1e-4 for a, b in zip(source_sorted, mesh_sorted))))
        if n != len(source_points) or mismatch:
            issues.append(f"base footprint-ring coordinates do not exactly match source after transform (mesh={n}, source={len(source_points)})")
        world_corners = [obj.matrix_world @ __import__("mathutils").Vector(p) for p in obj.bound_box]
        bounds = [[min(v[i] for v in world_corners), max(v[i] for v in world_corners)] for i in range(3)]
        linked_images = sorted({im.filepath for im in bpy.data.images if im.source == "FILE" and im.filepath})
        report.update({"object": obj.name, "type": obj.type, "building_id_property": obj.get("building_id"), "source_fid_property": obj.get("source_fid"),
                       "bounds_world_m": [[round(v, 3) for v in pair] for pair in bounds], "mesh_vertices": len(obj.data.vertices),
                       "mesh_faces": len(obj.data.polygons), "footprint_ring_vertices": n, "source_ring_vertices": len(source_points),
                       "footprint_matches_source_ring": not mismatch, "height_status": obj.get("height_status"), "height_m": obj.get("height_m"),
                       "external_image_dependencies": linked_images})
        if linked_images:
            issues.append(f"external image dependencies found: {linked_images}")
    report["issues"] = issues
    report["status"] = "pass" if not issues else "fail"
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
