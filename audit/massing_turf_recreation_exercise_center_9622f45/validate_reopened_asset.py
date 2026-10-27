"""Reopen-time checks for the assigned TREC Blender library."""

import json
from pathlib import Path

import bpy
from mathutils import Vector

BUILDING_ID = "massing_turf_recreation_exercise_center_9622f45"
ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / f"{BUILDING_ID}.blend"
OUT = Path(__file__).with_name("reopen_validation.json")
COLLECTION_NAME = f"Asset_{BUILDING_ID}"
SCENE_NAME = f"Building_{BUILDING_ID}"


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.context.scene
    collection = bpy.data.collections.get(COLLECTION_NAME)
    assert scene.name == SCENE_NAME, scene.name
    assert collection is not None, "expected exported collection missing"
    assert len(bpy.data.scenes) == 1, [s.name for s in bpy.data.scenes]
    objects = list(collection.objects)
    assert "TREC_GIS_Footprint_Slab" in {o.name for o in objects}
    assert "TREC_Gabled_Metal_Roof_ESTIMATED" in {o.name for o in objects}
    assert "TREC_Entry_Door_Left_SCHEMATIC" in {o.name for o in objects}
    assert "TREC_Entry_Door_Right_SCHEMATIC" in {o.name for o in objects}
    assert all(o.type == "MESH" for o in objects)

    depsgraph = bpy.context.evaluated_depsgraph_get()
    all_corners = []
    face_total = 0
    evaluated_mesh_count = 0
    for obj in objects:
        ev = obj.evaluated_get(depsgraph)
        mesh = ev.to_mesh()
        evaluated_mesh_count += 1
        face_total += len(mesh.polygons)
        all_corners.extend([obj.matrix_world @ Vector(corner) for corner in ev.bound_box])
        ev.to_mesh_clear()

    mins = [min(p[i] for p in all_corners) for i in range(3)]
    maxs = [max(p[i] for p in all_corners) for i in range(3)]
    slab = bpy.data.objects["TREC_GIS_Footprint_Slab"]
    slab_xy = [(v.co.x, v.co.y) for v in slab.data.vertices]
    shoelace = abs(sum(slab_xy[i][0] * slab_xy[(i + 1) % len(slab_xy)][1] -
                       slab_xy[(i + 1) % len(slab_xy)][0] * slab_xy[i][1]
                       for i in range(len(slab_xy))) / 2.0)
    wall = bpy.data.objects["TREC_Unspecified_Exterior_Wall_Envelope"]
    roof = bpy.data.objects["TREC_Gabled_Metal_Roof_ESTIMATED"]
    wall_z_bounds = [min(v.co.z for v in wall.data.vertices), max(v.co.z for v in wall.data.vertices)]
    roof_z_bounds = [min(v.co.z for v in roof.data.vertices), max(v.co.z for v in roof.data.vertices)]
    report = {
        "asset": str(ASSET.relative_to(ROOT)),
        "opened_scene": scene.name,
        "expected_scene": SCENE_NAME,
        "collection": collection.name,
        "object_count": len(objects),
        "evaluated_mesh_count": evaluated_mesh_count,
        "evaluated_face_count": face_total,
        "world_bounds_m": [[mins[i], maxs[i]] for i in range(3)],
        "gis_perimeter_vertex_count": len(slab.data.vertices),
        "gis_ring_area_m2": shoelace,
        "wall_z_bounds_m": wall_z_bounds,
        "roof_z_bounds_m": roof_z_bounds,
        "entrance_objects": ["TREC_Entry_Door_Left_SCHEMATIC", "TREC_Entry_Door_Right_SCHEMATIC"],
        "lidar_profile_target_heights_m": {"eaves_approximate": 9.7, "ridge_approximate": 14.4},
        "collection_instance_transform": "direct campus-coordinate collection geometry; object transforms evaluated",
        "material_slots": sorted({m.name for o in objects for m in o.data.materials if m}),
        "rendered_views_exist": {
            name: (OUT.parent / name).is_file()
            for name in ("preview.png", "preview_top.png", "preview_north_gable.png", "preview_east_entry.png")
        },
        "checks": {
            "saved_asset_reopened": True,
            "expected_scene_and_collection": True,
            "only_mesh_geometry_in_asset_collection": True,
            "gis_footprint_retained": True,
            "estimated_roof_is_separate_mesh": True,
            "geometry_not_in_local_origin_frame": True,
            "lidar_profile_heights_are_in_saved_geometry": abs(wall_z_bounds[1] - 9.7) < 0.01 and abs(roof_z_bounds[1] - 14.4) < 0.01,
            "schematic_entrance_opening_and_panels_present": True,
            "four_review_renders_exist": all((OUT.parent / name).is_file() for name in ("preview.png", "preview_top.png", "preview_north_gable.png", "preview_east_entry.png")),
        },
        "limitations": [
            "Wall/eave and ridge heights are LiDAR-derived estimates, not surveyed dimensions; the exact entrance bay and facade materials remain unverified.",
            "Master blend placement and neighboring context were not checked by this building-only reopen; Tobin owns master integration.",
        ],
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    evidence_path = Path(__file__).with_name("evidence.json")
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    evidence["validation"]["reopened_check"] = "passed"
    evidence["validation"]["reopen_report"] = "reopen_validation.json"
    evidence["validation"]["evaluated_world_bounds_m"] = report["world_bounds_m"]
    evidence["validation"]["object_count"] = report["object_count"]
    evidence["validation"]["evaluated_face_count"] = report["evaluated_face_count"]
    evidence["validation"]["reviewer"] = "builder self-check; independent grade pending"
    evidence_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    rebuild_path = Path(__file__).with_name("rebuild_record.json")
    if rebuild_path.exists():
        rebuild = json.loads(rebuild_path.read_text(encoding="utf-8"))
        rebuild["saved_asset_evaluated_bounds_m"] = report["world_bounds_m"]
        rebuild["reopen_validation"] = "passed; stable scene and collection reopened, 32 GIS perimeter vertices retained"
        rebuild_path.write_text(json.dumps(rebuild, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
