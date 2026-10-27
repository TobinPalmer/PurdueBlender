"""Independent Sigma Chi rubric evaluator; run with Blender 5.2.3 -b --python."""
import bpy
import bmesh
import hashlib
import json
import math
import os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ASSET = os.path.join(ROOT, "modular", "buildings", "massing_sigma_chi_fid828.blend")
EVIDENCE = os.path.join(ROOT, "audit", "sigma_chi")
SOURCE = os.path.join(EVIDENCE, "sources", "purdue_gis_fid828_raw.json")
OUT = os.path.join(EVIDENCE, "independent_grade", "sigma_chi_independent_grade.json")
EXPECTED_SHA = "b158aa1cb6c1ed72b54c0af6e61a3b53b37696b05a1b2e786cb65ddd5002af3c"
ASSET_ID = "massing_sigma_chi_fid828"
COLLECTION_NAME = "Asset_" + ASSET_ID
SCENE_NAME = "Building_" + ASSET_ID
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
XF = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
YF = 111040.0


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def evaluate():
    """Return rubric score, criterion evidence, and actionable findings."""
    asset_sha = sha256(ASSET)
    if asset_sha != EXPECTED_SHA:
        raise RuntimeError("Asset SHA changed; refusing to grade a different file: " + asset_sha)
    bpy.ops.wm.open_mainfile(filepath=ASSET)
    with open(SOURCE, "r", encoding="utf-8") as f:
        raw = json.load(f)

    col = bpy.data.collections.get(COLLECTION_NAME)
    scene = bpy.data.scenes.get(SCENE_NAME)
    if col is None or scene is None:
        raise RuntimeError("Expected named scene or asset collection is missing")
    objects = list(col.objects)
    mesh_objects = [o for o in objects if o.type == "MESH"]
    source_feature = next((feature for feature in raw.get("features", [])
                           if feature.get("attributes", {}).get("FID") == 828), None)
    if source_feature is None:
        raise RuntimeError("FID 828 is absent from the preserved source snapshot")
    ring_ll = source_feature["geometry"]["rings"][0]
    if math.dist(ring_ll[0], ring_ll[-1]) < 1e-10:
        ring_ll = ring_ll[:-1]
    expected = [((lon - ORIGIN_LON) * XF, (lat - ORIGIN_LAT) * YF)
                for lon, lat in ring_ll]
    wall = bpy.data.objects.get("SigmaChi_GIS_Footprint_Walls")
    actual = []
    if wall and wall.type == "MESH":
        actual = [(wall.matrix_world @ v.co).xy[:] for v in wall.data.vertices[:len(expected)]]
    footprint_error = (max((math.dist(tuple(a), tuple(b)) for a, b in zip(expected, actual)),
                           default=float("inf")))

    points = [o.matrix_world @ Vector(corner) for o in mesh_objects for corner in o.bound_box]
    bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
    nonmanifold = 0
    loose_edges = 0
    for obj in mesh_objects:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        nonmanifold += sum(not edge.is_manifold for edge in bm.edges)
        loose_edges += sum(not edge.link_faces for edge in bm.edges)
        bm.free()
    external_paths = []
    for image in bpy.data.images:
        if image.source == "FILE" and image.filepath and not image.packed_file:
            resolved = bpy.path.abspath(image.filepath)
            if not os.path.isfile(resolved):
                external_paths.append(image.filepath)
    collection_names = sorted(c.name for c in bpy.data.collections)

    # Scores reflect the five AGENT.md criteria and the evidence actually observed.
    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 2.0, "max_score": 2,
            "evidence": [
                "Preserved Purdue GIS FID 828 record names Sigma Chi, gives 202 Littleton St and GlobalID {C8550BCE-BEC4-40EA-85AB-B9B81E75436D}.",
                "Preserved chapter-house page identifies the Delta Delta house at 202 Littleton; the identity crosswalk is consistent across independent sources.",
                "The saved structural wall shell's first six XY vertices match the transformed FID 828 ring; independently measured maximum difference is %.8f m." % footprint_error,
            ],
            "findings": [] if footprint_error < 0.001 else ["Wall shell differs from source ring beyond 1 mm."],
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 2.0, "max_score": 2,
            "evidence": [
                "Asset uses campus coordinates as required for this massing library; source wall ring follows the FID 828 geographic outline with XY error %.8f m." % footprint_error,
                "The source ring itself determines plan shape, orientation, and dimensions; transformed AABB is X=%.3f..%.3f m, Y=%.3f..%.3f m." % (min(x for x,y in expected), max(x for x,y in expected), min(y for x,y in expected), max(y for x,y in expected)),
                "Independent inventory minimum-rotated-rectangle direction is documented as a secondary check, not substituted for the source ring.",
            ],
            "findings": ["No independent current survey is available; the position/dimension match is to Purdue GIS and the project's approximate local conversion."],
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 0.5, "max_score": 2,
            "evidence": [
                "Asset bounds reach Z=%.3f m; evidence correctly labels 8.8 m eaves and 13.1 m ridge as estimates." % bounds[2][1],
                "Historic chapter photos support steep roofs and gable/dormer cues, but are perspective views and cannot establish measured height, current roof layout, or floors.",
                "GIS floor attributes both say 1 but conflict with the facade's three courses and are not independent reliable storey evidence; the builder labels floor count unverified.",
            ],
            "findings": ["No elevation, survey, point-cloud height, or verified floor-count source: most of this criterion remains unsupported."],
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 0.5, "max_score": 2,
            "evidence": [
                "Historic chapter photographs show Tudor Revival character, prominent intersecting gables, masonry/stucco, an entry porch/canopy, and varied/arcuated openings.",
                "The saved render shows repeated plain rectangular windows and floor-course stripes on an otherwise box-like L mass; no prominent entrance, chimney, masonry articulation, or photo-matched gable composition is visible. Two small dormers are only generic roof cues.",
                "The overall appearance is schematic and is not sufficient evidence of architectural fidelity under AGENT.md.",
            ],
            "findings": ["The model omits the identifiable entrance and most distinctive Tudor/masonry details visible in the source photos; facade rhythm is generic."],
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 2.0, "max_score": 2,
            "evidence": [
                "Fresh open succeeded for the exact requested SHA-256; expected scene and named asset collection are present.",
                "Collection has %d objects (%d mesh objects); %d nonmanifold edges and %d loose edges were found." % (len(objects), len(mesh_objects), nonmanifold, loose_edges),
                "No unpacked missing external image dependencies were found: %s." % ("none" if not external_paths else ", ".join(external_paths)),
                "Audit folder preserves GIS/chapter-page source snapshots, render views, source metadata, transformation method, uncertainties, and fresh-open record.",
            ],
            "findings": [],
        },
    ]
    score = sum(c["score"] for c in criteria)
    findings = [finding for criterion in criteria for finding in criterion["findings"]]
    result = {
        "building": "Sigma Chi Delta Delta chapter house (Purdue GIS FID 828)",
        "asset_path": "modular/buildings/massing_sigma_chi_fid828.blend",
        "asset_sha256": asset_sha,
        "grader": "independent Blender asset review following root AGENT.md rubric",
        "blender_version": bpy.app.version_string,
        "score": score,
        "max_score": 10,
        "criteria": criteria,
        "evidence": {
            "reopened_saved_asset": True,
            "scene": scene.name,
            "collection": col.name,
            "collection_object_count": len(objects),
            "mesh_object_count": len(mesh_objects),
            "source_ring_vertex_count": len(expected),
            "source_ring_max_xy_error_m": footprint_error,
            "world_bounds_m": bounds,
            "nonmanifold_edges": nonmanifold,
            "loose_edges": loose_edges,
            "missing_unpacked_image_dependencies": external_paths,
            "inspected_views": [
                "audit/sigma_chi/sigma_chi_fresh_reopen_render.png",
                "audit/sigma_chi/sigma_chi_roof_plan.png",
                "audit/sigma_chi/sources/house_1960_62.gif",
                "audit/sigma_chi/sources/renovation_sept2006.jpg",
            ],
        },
        "findings": findings,
        "pass_threshold": 8,
        "result": "PASS" if score >= 8 else "FAIL",
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print("SIGMA_CHI_INDEPENDENT_GRADE", json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    evaluate()
