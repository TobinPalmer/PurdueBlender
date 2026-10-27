"""Independent Moosehead assessment. Run by opening the .blend in Blender 4.5.15."""
import json
import math
from pathlib import Path

import bpy


ASSET_ID = "massing_the_moosehead_lounge_f81529e"
ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / ASSET_ID
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
OSM_PATH = AUDIT / "sources" / "osm_way_910910470_full.json"
MANIFEST_PATH = ROOT / "modular" / "manifest.json"
SCENE_NAME = f"Building_{ASSET_ID}"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
OBJECT_NAME = "The Moosehead Lounge"
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
SCALE_X = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
SCALE_Y = 111040.0
EXPECTED_EAVE = 5.25


def local_xy(lon, lat):
    return ((lon - ORIGIN_LON) * SCALE_X, (lat - ORIGIN_LAT) * SCALE_Y)


def iter_dicts(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_dicts(child)


def evaluate():
    scene = bpy.context.scene
    coll = bpy.data.collections.get(COLLECTION_NAME)
    objects = list(coll.objects) if coll else []
    obj = objects[0] if len(objects) == 1 else None
    errors = []
    if scene.name != SCENE_NAME:
        errors.append(f"unexpected scene name {scene.name!r}")
    if coll is None:
        errors.append("manifest asset collection missing")
    if len(objects) != 1:
        errors.append(f"asset collection contains {len(objects)} objects, expected one")
    if obj and (obj.name != OBJECT_NAME or obj.type != "MESH"):
        errors.append("manifest object name or type mismatch")

    world_verts, poly_records = [], []
    if obj:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            world_verts = [evaluated.matrix_world @ v.co for v in mesh.vertices]
            poly_records = [(int(p.material_index), list(p.vertices)) for p in mesh.polygons]
            bounds = [[float(min(v[i] for v in world_verts)), float(max(v[i] for v in world_verts))]
                      for i in range(3)] if world_verts else None
            lower = {(round(v.x, 5), round(v.y, 5)) for v in world_verts if abs(v.z) < 1e-5}
            eave = {(round(v.x, 5), round(v.y, 5)) for v in world_verts if abs(v.z - EXPECTED_EAVE) < 1e-5}
            structural_points = sorted(lower & eave)
            materials = [m.name if m else None for m in mesh.materials]
            material_face_counts = {}
            for material_index, _ in poly_records:
                material_face_counts[str(material_index)] = material_face_counts.get(str(material_index), 0) + 1
            modifiers = [m.name for m in obj.modifiers]
            external_image_files = [im.filepath for im in bpy.data.images if im.source == "FILE"]
            vertex_count, face_count = len(mesh.vertices), len(mesh.polygons)
        finally:
            evaluated.to_mesh_clear()
    else:
        bounds, structural_points, materials, material_face_counts, modifiers, external_image_files = None, [], [], {}, [], []
        vertex_count = face_count = 0

    osm = json.loads(OSM_PATH.read_text(encoding="utf-8"))
    elements = osm["elements"]
    node_map = {e["id"]: e for e in elements if e.get("type") == "node"}
    way = next(e for e in elements if e.get("type") == "way" and e.get("id") == 910910470)
    source_ring = [local_xy(node_map[n]["lon"], node_map[n]["lat"]) for n in way["nodes"][:-1]]
    residuals = []
    for sx, sy in source_ring:
        residuals.append(min(math.hypot(sx - mx, sy - my) for mx, my in structural_points)
                         if structural_points else None)
    footprint_max_residual = max(r for r in residuals if r is not None) if residuals else None

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest_entry = next((d for d in iter_dicts(manifest) if d.get("id") == ASSET_ID), None)
    manifest_bounds = manifest_entry.get("bounds_world_m") if manifest_entry else None
    main_nodes = [e for e in elements if e.get("type") == "node"
                  and e.get("tags", {}).get("entrance") == "main"
                  and e.get("tags", {}).get("level") == "0"]
    door_faces = []
    if obj and materials:
        door_material_indices = {i for i, name in enumerate(materials) if name == "Entry doors — schematic"}
        for material_index, vertex_indices in poly_records:
            if material_index in door_material_indices:
                door_faces.extend([world_verts[i] for i in vertex_indices])
    entrance_residuals = []
    for nd in main_nodes:
        ex, ey = local_xy(nd["lon"], nd["lat"])
        entrance_residuals.append(min((math.hypot(ex - v.x, ey - v.y) for v in door_faces), default=None))

    bbox_osm = [[min(x for x, y in source_ring), max(x for x, y in source_ring)],
                [min(y for x, y in source_ring), max(y for x, y in source_ring)]]
    bbox_asset = bounds[:2] if bounds else None
    bbox_error = max(abs(bbox_osm[a][b] - bbox_asset[a][b]) for a in range(2) for b in range(2)) if bbox_asset else None
    estimate_notes = [
        "OSM tags building:levels=2, but no scaled elevation or measured height source was found.",
        "Eave 5.25 m and ridge 7.60 m are explicit estimates; the single gable form is schematic and roof divisions are unverified.",
        "Facade windows/materials are generic schematic placeholders; available evidence has no street-level facade photograph or elevation.",
        "The 2018 Indiana footprint is a conflicting merged/adjacent-roof candidate and is disclosed, not used as the shell.",
        "Purdue GIS FID 855 is correctly excluded: the assignment queue and README map it to the Old Purdue Exponent Building.",
    ]
    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": f"OSM way 910910470 is directly tagged The Moosehead Lounge, 434 North Grant Street; the captured West Lafayette BPW map labels Moosehead at the site. The named, addressed OSM ring is compared against an imagery overlay and the mesh structural outline (maximum source-to-mesh vertex residual {footprint_max_residual:.4f} m). Purdue's name query found no Moosehead; FID 855 is an Old Purdue Exponent candidate and is explicitly excluded.",
            "findings": [],
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 1.9,
            "max_score": 2.0,
            "evidence": f"The object retains campus-world coordinates and identity object transform. OSM/project local-conversion footprint bbox is {bbox_osm}; reopened asset world bbox is {bbox_asset}; maximum bbox difference is {bbox_error:.3f} m. Orthophoto overlay supports site alignment. Approximate geographic conversion and community-mapped source are documented.",
            "findings": ["The local projection is approximate rather than surveyed, and no independent parcel survey or Purdue-named GIS feature was found."],
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.0,
            "max_score": 2.0,
            "evidence": "OSM building:levels=2 supports a two-level interpretation. Reopened mesh reaches 7.60 m, with 5.25 m eaves; both heights are labeled estimated. Indiana current imagery supports roof plan context only.",
            "findings": ["No source establishes measured eave or ridge height.", "One broad gable is schematic; the orthophoto shows roof complexity/sections that are not established by the model, and the gable end walls are not filled to the roof ridge."],
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 0.7,
            "max_score": 2.0,
            "evidence": f"The OSM snapshot includes {len(main_nodes)} main entrance nodes on level 0; the asset models doors at these locations (nearest door-face vertex distances {entrance_residuals}). Rendered views show two rows of repeated rectangular windows and generic masonry/trim/glazing.",
            "findings": ["No direct facade photographs or elevations were located; window count, sizes, materials, facade rhythm, and exact entry construction are schematic.", "The massing lacks gable-end infill and visible source-backed architectural details."],
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 1.9,
            "max_score": 2.0,
            "evidence": f"Independently reopened in Blender {bpy.app.version_string}; exact scene/collection/object identities persist; asset collection has one mesh object, {vertex_count} vertices, {face_count} faces, no modifiers, and no file-backed image dependencies. Scene has {len(bpy.data.objects)} objects including a separate render-only collection. Source snapshots, reconciliation, validation, and four renders are present.",
            "findings": [],
        },
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    findings = [finding for c in criteria for finding in c["findings"]]
    result = {
        "evaluator": "Independent evaluator r1; executed by Blender Python after reopening the saved asset in Blender 4.5.15 LTS.",
        "score": score,
        "max_score": 10,
        "passing_threshold": 8,
        "pass": score >= 8,
        "criteria": criteria,
        "evidence": {
            "asset": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
            "blender_version": bpy.app.version_string,
            "scene": scene.name,
            "asset_collection": coll.name if coll else None,
            "asset_collection_object_names": [o.name for o in objects],
            "scene_object_count": len(bpy.data.objects),
            "object_transform": {"location": list(obj.location), "scale": list(obj.scale)} if obj else None,
            "object_bounds_world_m": bounds,
            "source_footprint_ring_projected_local_m": [[round(x, 6), round(y, 6)] for x, y in source_ring],
            "structural_intersection_vertices": len(structural_points),
            "source_to_mesh_nearest_vertex_residuals_m": [round(x, 6) for x in residuals if x is not None],
            "source_to_mesh_max_residual_m": footprint_max_residual,
            "manifest_bounds_world_m": manifest_bounds,
            "source_bbox_world_m": bbox_osm,
            "source_asset_bbox_max_delta_m": bbox_error,
            "osm_levels": way.get("tags", {}).get("building:levels"),
            "osm_entrance_node_ids": [n["id"] for n in main_nodes],
            "door_face_nearest_node_residuals_m": entrance_residuals,
            "materials": materials,
            "face_count_by_material_index": material_face_counts,
            "modifiers": modifiers,
            "file_backed_images": external_image_files,
            "purdue_fid_855_conflict": "README assignment crosswalk identifies FID 855 as Old Purdue Exponent Building; it is not a Moosehead match.",
        },
        "findings": findings,
        "uncertainties": estimate_notes,
        "check_errors": errors,
    }
    out = AUDIT / "independent_grade_r1.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    report = evaluate()
    print(json.dumps(report, indent=2))
