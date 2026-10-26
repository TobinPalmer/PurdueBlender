"""Canonical Class of 1950 modular asset packager and validator.

Run from Blender (the asset was authored by a newer Blender 5.02-series build;
this module was checked in Blender 4.5.15 without saving the source file):
  blender -b --python modular/buildings/build_class_of_1950.py
  blender -b --python modular/buildings/build_class_of_1950.py -- --package-copy work/class_of_1950_copy.blend

The authored modular .blend is the current geometry source of truth. The historical
root-level build/refine scripts build into a full scene and are not safe to rerun on
the modular master; they also do not reproduce every audited revision. This module
therefore validates and packages the saved building library byte-for-byte, without
regenerating geometry or saving over the source asset. Geometry edits should be made
in the building library and then rerun through this validation/packaging step.
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any

import bpy
from mathutils import Vector

SCRIPT = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT.parents[2]
BUILDINGS_DIR = PROJECT_ROOT / "modular" / "buildings"
ASSET_ID = "class_of_1950"
ASSET_PATH = BUILDINGS_DIR / "class_of_1950.blend"
COLLECTION_NAME = "Asset_class_of_1950"
SCENE_NAME = "Building_class_of_1950"
EVIDENCE_DIR = PROJECT_ROOT / "audit" / "class_of_1950_evidence"
MANIFEST_PATH = PROJECT_ROOT / "modular" / "manifest.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def geom_bounds(collection: bpy.types.Collection) -> list[list[float]]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points: list[Vector] = []
    for obj in collection.all_objects:
        if obj.type not in {"MESH", "CURVE", "SURFACE", "FONT", "META"}:
            continue
        evaluated = obj.evaluated_get(depsgraph)
        points.extend(evaluated.matrix_world @ Vector(c) for c in evaluated.bound_box)
    if not points:
        raise RuntimeError(f"No bounded geometry in {collection.name}")
    return [[float(min(p[i] for p in points)), float(max(p[i] for p in points))] for i in range(3)]


def _load_asset(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    bpy.ops.wm.open_mainfile(filepath=str(path))


def validate_loaded_asset(path: Path) -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))
    record = next((a for a in manifest["assets"] if a.get("id") == ASSET_ID), None)
    if record is None:
        raise RuntimeError(f"Manifest is missing {ASSET_ID}")
    if record.get("file") != "buildings/class_of_1950.blend":
        raise RuntimeError(f"Unexpected manifest asset path: {record.get('file')}")
    if record.get("collection") != COLLECTION_NAME or record.get("scene") != SCENE_NAME:
        raise RuntimeError("Manifest collection/scene no longer match the stable CL50 names")

    collection = bpy.data.collections.get(COLLECTION_NAME)
    scene = bpy.data.scenes.get(SCENE_NAME)
    if collection is None:
        raise RuntimeError(f"Missing collection {COLLECTION_NAME}")
    if scene is None:
        raise RuntimeError(f"Missing scene {SCENE_NAME}")

    objects = list(collection.all_objects)
    mesh_objects = [o for o in objects if o.type == "MESH"]
    if record.get("object_count") is not None and len(objects) != int(record["object_count"]):
        raise RuntimeError(f"Object count mismatch: manifest={record['object_count']}, saved={len(objects)}")
    required = ["CL50_Corrected_GIS_Wall_Envelope", "CL50_Corrected_GIS_Roof_Slab", "CL50_Penthouse"]
    missing = [name for name in required if bpy.data.objects.get(name) not in objects]
    if missing:
        raise RuntimeError(f"Missing expected building geometry: {missing}")

    bounds = geom_bounds(collection)
    # Independently compare the exported shell's actual bottom perimeter against
    # the raw Purdue ArcGIS geometry.  A mesh lower ring is a finer tessellation
    # than the GIS ring, so report directed nearest-vertex distances rather than
    # claiming a surveyed wall error or polygon IoU.
    gis_path = EVIDENCE_DIR / "arcgis_feature_230.json"
    gis_response = json.loads(gis_path.read_text(encoding="utf-8-sig"))
    feature = gis_response["feature"]
    attributes = feature["attributes"]
    if (attributes.get("FID"), attributes.get("BLDG_ABBR"), attributes.get("BUILDING_N")) != (
        230, "CL50", "Class of 1950 Lecture Hall"
    ):
        raise RuntimeError("The evidence GIS feature does not identify Class of 1950 (FID 230 / CL50)")
    origin_x, origin_y = record["placement_origin_xy_m"]
    ring = feature["geometry"]["rings"][0]
    radius = 6378137.0
    source_xy: list[tuple[float, float]] = []
    for merc_x, merc_y in ring:
        longitude = merc_x / radius * 180.0 / 3.141592653589793
        latitude = (2.0 * math.atan(math.exp(merc_y / radius)) - math.pi / 2.0) * 180.0 / math.pi
        campus_x = (longitude + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
        campus_y = (latitude - 40.4274) * 111040.0
        source_xy.append((campus_x - origin_x, campus_y - origin_y))
    shell = bpy.data.objects["CL50_Corrected_GIS_Wall_Envelope"]
    lower_xy = {
        (round(float((shell.matrix_world @ v.co).x), 3), round(float((shell.matrix_world @ v.co).y), 3))
        for v in shell.data.vertices
        if abs(float((shell.matrix_world @ v.co).z)) < 1e-5
    }
    if not lower_xy:
        raise RuntimeError("The GIS wall envelope has no Z=0 perimeter vertices")

    def near_distance(point: tuple[float, float], candidates: set[tuple[float, float]] | list[tuple[float, float]]) -> float:
        return min(((point[0] - other[0]) ** 2 + (point[1] - other[1]) ** 2) ** 0.5 for other in candidates)

    gis_to_shell = [near_distance(p, lower_xy) for p in source_xy]
    shell_to_gis = [near_distance(p, source_xy) for p in lower_xy]
    source_bounds = [[min(p[i] for p in source_xy), max(p[i] for p in source_xy)] for i in (0, 1)]
    shell_bounds = [[min(p[i] for p in lower_xy), max(p[i] for p in lower_xy)] for i in (0, 1)]
    footprint_check = {
        "source_feature_id": attributes["FID"],
        "source_code": attributes["BLDG_ABBR"],
        "source_crs": "EPSG:3857 (ArcGIS latestWkid=3857; layer wkid=102100)",
        "method": "Inverse Web Mercator; apply the Purdue local approximation in modular/AGENTS.md; subtract the manifest placement origin; compare GIS ring vertices with rounded-to-millimeter Z=0 envelope vertices.",
        "source_ring_vertex_count": len(source_xy),
        "model_lower_perimeter_vertex_count": len(lower_xy),
        "gis_to_model_nearest_vertex_avg_m": sum(gis_to_shell) / len(gis_to_shell),
        "gis_to_model_nearest_vertex_max_m": max(gis_to_shell),
        "model_to_gis_nearest_vertex_avg_m": sum(shell_to_gis) / len(shell_to_gis),
        "model_to_gis_nearest_vertex_max_m": max(shell_to_gis),
        "source_local_bounds_m": source_bounds,
        "model_lower_perimeter_bounds_m": shell_bounds,
        "max_axis_extent_delta_m": [max(abs(source_bounds[i][j] - shell_bounds[i][j]) for j in (0, 1)) for i in (0, 1)],
        "limitation": "Directed nearest-vertex distances document XY agreement but are not a surveyed wall error or area-overlap statistic. GIS feature has no source date; vertical field semantics remain undocumented.",
    }
    no_material = [o.name for o in mesh_objects if not o.data.materials or all(m is None for m in o.data.materials)]
    external_libraries = [
        {"path": lib.filepath, "absolute": bpy.path.abspath(lib.filepath)}
        for lib in bpy.data.libraries
    ]
    external_images = [
        {"name": im.name, "path": im.filepath, "packed": bool(im.packed_file)}
        for im in bpy.data.images
        if im.source == "FILE" and not im.packed_file
    ]
    root = bpy.data.objects.get("AssetRoot_class_of_1950")
    report = {
        "asset_id": ASSET_ID,
        "asset_path": str(path.resolve()),
        "asset_sha256": sha256(path),
        "asset_bytes": path.stat().st_size,
        "scene": SCENE_NAME,
        "collection": COLLECTION_NAME,
        "blender_version": bpy.app.version_string,
        "saved_render_engine": scene.render.engine,
        "source_file_rewrite_performed": False,
        "validation_notes": [
            "This Blender 4.5.15 run logged that the saved file was written by newer Blender binary 502.45; no source rewrite was performed.",
            "Blender logged Engine 'BLENDER_EEVEE' not available while loading; the loaded target scene reports render.engine='" + scene.render.engine + "'.",
        ],
        "object_count": len(objects),
        "mesh_object_count": len(mesh_objects),
        "evaluated_mesh_bounds_local_frame_m": bounds,
        "manifest_local_bounds_m": record.get("local_bounds_m"),
        "placement_origin_xy_m": record.get("placement_origin_xy_m"),
        "root_empty_present_at_local_origin": bool(root and all(abs(v) < 1e-6 for v in root.location)),
        "required_geometry_present": required,
        "unmaterialed_mesh_count": len(no_material),
        "unmaterialed_meshes": no_material,
        "external_libraries": external_libraries,
        "unpacked_file_images": external_images,
        "status": "PASS" if not no_material and not external_libraries and not external_images else "REVIEW",
        "source_evidence": {
            "gis_feature_id": 230,
            "gis_code": "CL50",
            "gis_name": "Class of 1950 Lecture Hall",
            "retrieved": "2026-10-25",
            "gis_crs": "EPSG:3857 (ArcGIS latestWkid=3857; layer wkid=102100)",
            "footprint_method": "Inverse Web Mercator; convert with the Purdue local approximation documented in modular/AGENTS.md; compare after subtracting the manifest placement origin.",
            "height_uncertainty": "GIS NUM_LEVELS and CountOfFLO are 3; Extrution=36 has no documented units/semantics. Model height is not claimed as surveyed.",
            "vertical_reference_fields": {
                key: attributes.get(key) for key in ("NUM_LEVELS", "CountOfFLO", "Extrution", "Elevation", "F02", "R")
            },
            "evidence_directory": str(EVIDENCE_DIR.relative_to(PROJECT_ROOT)),
            "footprint_check": footprint_check,
            "official_architecture_sources": [
                "https://archives.lib.purdue.edu/agents/corporate_entities/541",
                "https://events.purdue.edu/class_of_1950_lecture_hall",
                "https://www.roadschool.purdue.edu/maps/2024%20Class%20of%201950%20Lecture%20Hall.pdf",
            ],
        },
    }
    if report["status"] != "PASS":
        raise RuntimeError("Portability checks failed: " + json.dumps(report, indent=2))
    return report


def parse_package_output() -> Path | None:
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if not args:
        return None
    if len(args) != 2 or args[0] != "--package-copy":
        raise RuntimeError("Usage: -- --package-copy <output.blend>")
    out = Path(args[1]).expanduser()
    if not out.is_absolute():
        out = (PROJECT_ROOT / out).resolve()
    return out


def run() -> dict[str, Any]:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    package_path = parse_package_output()
    _load_asset(ASSET_PATH)
    result = validate_loaded_asset(ASSET_PATH)
    result["generated_at"] = date.today().isoformat()
    result["builder_module"] = str(SCRIPT.relative_to(PROJECT_ROOT))
    result["mode"] = "validate-existing-source"

    if package_path is not None:
        package_path.parent.mkdir(parents=True, exist_ok=True)
        if package_path.resolve() != ASSET_PATH.resolve():
            shutil.copy2(ASSET_PATH, package_path)
            result["mode"] = "validated-byte-identical-package-copy"
            result["package_copy"] = str(package_path)
            result["package_copy_sha256"] = sha256(package_path)
            if result["package_copy_sha256"] != result["asset_sha256"]:
                raise RuntimeError("Package copy hash differs from source asset")
            _load_asset(package_path)
            copied = validate_loaded_asset(package_path)
            if copied["asset_sha256"] != result["asset_sha256"]:
                raise RuntimeError("Package copy reopen verification failed")
            result["reopened_package_collection_count"] = copied["object_count"]
        else:
            result["package_copy"] = str(package_path)
            result["package_copy_skipped"] = "Source and output are the canonical asset path; no destructive rewrite performed."

    target = EVIDENCE_DIR / "package_validation.json"
    target.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"BUILD_EVIDENCE={target}")
    return result


if __name__ == "__main__":
    run()

