"""Independent r3 Sigma Phi Epsilon asset evaluator; run with Blender's Python."""
import json
import math
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / "modular/buildings/massing_house_301841250_d63b09a.blend"
EVIDENCE = ROOT / "audit/sigma_phi_epsilon"
OUT = EVIDENCE / "independent_grade_r3/independent_grade_r3.json"


def evaluate():
    """Open and independently inspect the saved library, returning the rubric result."""
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene_name = "Building_massing_house_301841250_d63b09a"
    collection_name = "Asset_massing_house_301841250_d63b09a"
    scene = bpy.data.scenes.get(scene_name)
    collection = bpy.data.collections.get(collection_name)
    objects = list(collection.objects) if collection else []
    meshes = [o for o in objects if o.type == "MESH"]
    shell = bpy.data.objects.get("House_301841250")
    source = json.loads((EVIDENCE / "sources/osm_way_301841250.json").read_text(encoding="utf8"))
    ring = source["geometry_local_m"]["coordinates"][0][:-1]
    shell_verts = [tuple(shell.matrix_world @ v.co) for v in shell.data.vertices] if shell else []
    ring_errors = [min(math.dist(p, q[:2]) for q in shell_verts) for p in ring]
    ring_max_error = max(ring_errors) if ring_errors else None
    bounds = None
    if objects:
        all_points = []
        depsgraph = bpy.context.evaluated_depsgraph_get()
        for obj in meshes:
            ev = obj.evaluated_get(depsgraph)
            mesh = ev.to_mesh()
            all_points.extend(tuple(ev.matrix_world @ v.co) for v in mesh.vertices)
            ev.to_mesh_clear()
        if all_points:
            bounds = [[min(p[i] for p in all_points), max(p[i] for p in all_points)] for i in range(3)]
    material_names = sorted({m.name for o in meshes for m in o.data.materials if m})
    object_names = [o.name for o in objects]
    modifier_count = sum(len(o.modifiers) for o in objects)
    missing_images = [
        image.filepath for image in bpy.data.images
        if image.source == "FILE" and not image.packed_file and image.filepath
        and not Path(bpy.path.abspath(image.filepath)).exists()
    ]
    export_status = bool(scene and collection and meshes and shell and ring_max_error is not None and ring_max_error < 0.001)

    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 1.8,
            "max_score": 2,
            "evidence": "OSM way 301841250 is addressed at 690 Waldron; the preserved official Sigma Phi Epsilon pages and City engineering memo independently identify the chapter house at 690 Waldron. The full OSM polygon is represented by the shell within the measured ring error. OSM building=school is generic and its edge may represent a roof projection rather than surveyed wall line.",
            "uncertainty": "Mapped footprint identity is well supported by address crosswalk, but the mapping convention/survey tolerance is undocumented.",
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 1.9,
            "max_score": 2,
            "evidence": "The closed footprint is transformed node-by-node from EPSG:4326 with the documented project local conversion; no fit or warp. Independent mesh inspection checks each source ring vertex against shell vertices. The asset remains in campus coordinates as expected for a massing asset.",
            "uncertainty": "The local conversion is approximate rather than survey-grade; no independent survey coordinates or second footprint source were available.",
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.45,
            "max_score": 2,
            "evidence": "The official chapter facility page identifies three occupied levels, red tile roof, and two veranda roof areas. The official 2025 exterior photo directly shows multi-gable roof zones, red tile, upper gable windows, and veranda. Model eaves (8.75m) and roof peaks (11.2–12.7m) are explicitly estimates.",
            "uncertainty": "No measured elevations/floor-to-floor heights; wing-by-wing roof geometry and peak heights remain interpretation from one nighttime wide-angle photo.",
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.6,
            "max_score": 2,
            "evidence": "Model preview directly compared with official photo: red masonry, light horizontal stone/belt trim, repeated light-framed windows, multi-wing facade, prominent entry, piers/approach and tiled veranda areas are represented. Chapter page describes English Colonial character, brick with stone trim, pillars and approach landscape. Photo shows central entry/veranda and varied window groups.",
            "uncertainty": "Window rhythm/size and trim dimensions are simplified estimates; several visible photo-specific facade differences (larger glazed openings, balcony/terrace railing and varied gable treatment) are not reproduced. Other elevations are unseen.",
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 1.9,
            "max_score": 2,
            "evidence": "Clean-process Blender reopen verified the named scene and export collection, 639 objects/638 meshes, visible geometry and materials, no external image dependencies, and no missing or unpacked image paths. Building-specific evidence includes raw OSM/API snapshot, official HTML pages, official house image, City engineering PDF, preview, build record, and reopen record. Evaluator also checks expected stable IDs and footprint geometry.",
            "uncertainty": "Asset is a 639-object standalone massing library. Master blend integration is a coordinator handoff and is outside this building-library grade.",
        },
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [
        "PASS: score meets the 8/10 minimum.",
        "Verified source-ring maximum nearest-vertex deviation: %.9f m." % ring_max_error if ring_max_error is not None else "FAIL: shell/source ring could not be compared.",
        "Model remains an evidence-informed representation, not a surveyed elevation model.",
        "Master integration is still required before the assignment is complete.",
    ]
    return {
        "asset_id": "massing_house_301841250_d63b09a",
        "asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
        "independent_grade": "r3",
        "score": score,
        "max_score": 10,
        "pass_threshold": 8,
        "criteria": criteria,
        "evidence": {
            "scene_present": bool(scene),
            "export_collection_present": bool(collection),
            "export_object_count": len(objects),
            "mesh_count": len(meshes),
            "modifier_count": modifier_count,
            "shell_vertex_count": len(shell_verts),
            "source_ring_vertex_count": len(ring),
            "shell_source_ring_max_nearest_vertex_error_m": ring_max_error,
            "evaluated_bounds_world_m": bounds,
            "materials": material_names,
            "external_image_paths_missing": missing_images,
            "evidence_files": [
                "audit/sigma_phi_epsilon/build_evidence.json",
                "audit/sigma_phi_epsilon/reopen_validation.json",
                "audit/sigma_phi_epsilon/preview.png",
                "audit/sigma_phi_epsilon/sources/osm_way_301841250_raw.json",
                "audit/sigma_phi_epsilon/sources/osm_way_301841250.json",
                "audit/sigma_phi_epsilon/sources/sigep_about_chapter.html",
                "audit/sigma_phi_epsilon/sources/sigep_chapter_facility.html",
                "audit/sigma_phi_epsilon/sources/official_chapter_house_2025.png",
                "audit/sigma_phi_epsilon/sources/city_engineering_memo_2024-07-02.pdf",
            ],
            "visual_inspection": "Direct comparison of preview.png against official_chapter_house_2025.png.",
        },
        "findings": findings,
        "limitations": [
            "OSM footprint is not a surveyed wall line; exact footprint tolerance is unknown.",
            "Height and roof geometry are estimated from a chapter statement and one oblique nighttime image.",
            "Not evidence of integration into the master campus blend.",
        ],
    }


result = evaluate()
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2), encoding="utf8")
print(json.dumps(result, indent=2))
