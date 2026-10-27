"""Reopen the Moosehead asset in Blender and record export-level checks."""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_the_moosehead_lounge_f81529e"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
OUT = ROOT / "audit" / ASSET_ID / "reopen_validation.json"
SCENE_NAME = f"Building_{ASSET_ID}"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
EXPECTED_OBJECT = "The Moosehead Lounge"


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.context.scene
    coll = bpy.data.collections.get(COLLECTION_NAME)
    checks = {}
    checks["scene_name"] = scene.name == SCENE_NAME
    checks["asset_collection_present"] = coll is not None
    objects = list(coll.objects) if coll else []
    checks["exactly_one_export_object"] = len(objects) == 1
    checks["object_name_and_type"] = len(objects) == 1 and objects[0].name == EXPECTED_OBJECT and objects[0].type == "MESH"
    checks["export_collection_is_linked_to_scene"] = bool(coll and coll.name in {c.name for c in scene.collection.children_recursive})

    object_report = None
    if len(objects) == 1 and objects[0].type == "MESH":
        obj = objects[0]
        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            world_verts = [evaluated.matrix_world @ v.co for v in mesh.vertices]
            bounds = [[min(v[i] for v in world_verts), max(v[i] for v in world_verts)] for i in range(3)]
            base_vertices = [v for v in world_verts if abs(v.z) <= 1e-5]
            # The OSM structural outline is represented by coincident XY vertices
            # at Z=0 and the modeled eave. Windows/doors can project slightly
            # past that wall outline and should not be treated as footprint.
            bottom_xy = {(round(v.x, 5), round(v.y, 5)) for v in world_verts if abs(v.z) <= 1e-5}
            eave_xy = {(round(v.x, 5), round(v.y, 5)) for v in world_verts if abs(v.z - 5.25) <= 1e-5}
            structural_xy = bottom_xy & eave_xy
            structural_bounds = [
                [min(p[i] for p in structural_xy), max(p[i] for p in structural_xy)]
                for i in range(2)
            ] if structural_xy else None
            structural_expected = [
                [294.6150767505242, 322.0258640165149],
                [145.68447999984983, 158.78719999990608],
            ]
            max_detail_overhang = max(
                abs(bounds[0][0] - structural_expected[0][0]),
                abs(bounds[0][1] - structural_expected[0][1]),
                abs(bounds[1][0] - structural_expected[1][0]),
                abs(bounds[1][1] - structural_expected[1][1]),
            )
            top_z = max(v.z for v in world_verts)
            object_report = {
                "name": obj.name,
                "type": obj.type,
                "origin": [float(x) for x in obj.location],
                "scale": [float(x) for x in obj.scale],
                "evaluated_bounds_world_m": [[float(v) for v in axis] for axis in bounds],
                "structural_outline_bounds_world_m": structural_bounds,
                "max_decorative_projection_beyond_outline_m": float(max_detail_overhang),
                "evaluated_vertices": len(mesh.vertices),
                "evaluated_faces": len(mesh.polygons),
                "modifiers": [m.name for m in obj.modifiers],
                "base_z_vertex_count": len(base_vertices),
                "evaluated_top_z_m": float(top_z),
                "materials": [m.name for m in mesh.materials],
            }
            checks["no_modifiers"] = len(obj.modifiers) == 0
            checks["nonzero_mesh_and_faces"] = len(mesh.vertices) > 0 and len(mesh.polygons) > 0
            checks["z_datum_zero"] = bounds[2][0] >= -1e-6 and bounds[2][0] <= 1e-6
            checks["structural_outline_matches_osm_and_manifest"] = (
                structural_bounds is not None
                and abs(structural_bounds[0][0] - structural_expected[0][0]) < 0.01
                and abs(structural_bounds[0][1] - structural_expected[0][1]) < 0.01
                and abs(structural_bounds[1][0] - structural_expected[1][0]) < 0.01
                and abs(structural_bounds[1][1] - structural_expected[1][1]) < 0.01
                and abs(bounds[2][1] - 7.6) < 0.01
            )
            checks["decorative_detail_overhang_below_0_1m"] = max_detail_overhang < 0.1
        finally:
            evaluated.to_mesh_clear()

    external_images = []
    for image in bpy.data.images:
        if image.source == "FILE" and image.filepath and not image.packed_file:
            external_images.append(bpy.path.abspath(image.filepath))
    checks["no_unpacked_external_images"] = len(external_images) == 0
    checks["stable_scene_identity"] = scene.get("building_id") == ASSET_ID
    checks["identity_excludes_fid_855"] = "Old Purdue Exponent Building" in scene.get("excluded_candidate", "")
    checks["estimated_height_disclosed"] = scene.get("height_status", "").startswith("Estimated")
    checks["footprint_conflict_disclosed"] = "409924" in scene.get("footprint_status", "") and "38.01%" in scene.get("footprint_status", "")
    checks["r2_geometry_edits_recorded"] = scene.get("geometry_iteration", "").startswith("r2:")
    if len(objects) == 1 and objects[0].type == "MESH":
        obj = objects[0]
        try:
            roof_sections = json.loads(obj.get("roof_sections_json", "[]"))
        except Exception:
            roof_sections = []
        checks["two_orthophoto_interpreted_roof_zones"] = len(roof_sections) == 2
        checks["gable_end_faces_recorded"] = obj.get("gable_end_faces") == 2
        checks["unsupported_facade_details_omitted"] = "No windows" in obj.get("facade_detail_status", "")

    report = {
        "building_id": ASSET_ID,
        "asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
        "blender_version": bpy.app.version_string,
        "opened_file": bpy.data.filepath,
        "scene_name": scene.name,
        "asset_collection": COLLECTION_NAME,
        "scene_collection_objects": len(scene.objects),
        "collection_objects": [o.name for o in objects],
        "object": object_report,
        "external_unpacked_images": external_images,
        "scene_identity": scene.get("identity_source"),
        "excluded_candidate": scene.get("excluded_candidate"),
        "footprint_status": scene.get("footprint_status"),
        "height_status": scene.get("height_status"),
        "roof_status": scene.get("roof_status"),
        "geometry_iteration": scene.get("geometry_iteration"),
        "roof_sections": roof_sections if len(objects) == 1 and objects[0].type == "MESH" else [],
        "facade_detail_status": objects[0].get("facade_detail_status") if objects else None,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
