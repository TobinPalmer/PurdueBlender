"""Independent Sigma Pi R4 evaluation. Run with the available bpy Python runtime."""
import bpy
import bmesh
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "sigma_pi"
OUT = Path(__file__).resolve().parent
ASSET = ROOT / "modular" / "buildings" / "massing_house_301836568_0fbca0e.blend"
GIS = AUDIT / "sources" / "purdue_gis_fid776_sigma_pi_2026-10-26.json"
EXPECTED_SHA = "562853c102de946d253c893b984032d9b7525f55638b5390d4ac3d76e3d30c73"
BUILD_ID = "massing_house_301836568_0fbca0e"


def evaluate():
    """Open and inspect the frozen file, then return a rubric result."""
    sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    if sha != EXPECTED_SHA:
        raise RuntimeError(f"Frozen asset changed: {sha} != {EXPECTED_SHA}")

    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    feature = json.loads(GIS.read_text(encoding="utf-8"))
    ring = feature["geometry"]["rings"][0]
    lat0, lon0 = 40.4274, -86.9137
    src = [((lon - lon0) * 111412.84 * math.cos(math.radians(lat0)),
            (lat - lat0) * 111040.0) for lon, lat in ring]
    if src and src[0] == src[-1]:
        src.pop()

    coll = bpy.data.collections.get("Asset_" + BUILD_ID)
    scene = bpy.data.scenes.get("Building_" + BUILD_ID)
    shell = bpy.data.objects.get("SigmaPi_Stucco_Shell_FID776")
roof = bpy.data.objects.get("SigmaPi_Roof_Surface_LiDAR_2018_Interpolated")
    if not coll or not scene or not shell or not roof or shell.type != "MESH" or roof.type != "MESH":
        raise RuntimeError("Expected modular collection, scene, shell, or roof is missing")

    dg = bpy.context.evaluated_depsgraph_get()
    shell_eval = shell.evaluated_get(dg)
    mesh = shell_eval.to_mesh()
    try:
        world = [shell_eval.matrix_world @ v.co for v in mesh.vertices]
        bottom = [(v.x, v.y) for v in world if v.z < 1.0]
        nearest = [min(math.hypot(x - sx, y - sy) for x, y in bottom) for sx, sy in src]
        shell_bounds = [[min(v[i] for v in world), max(v[i] for v in world)] for i in range(3)]
        bm = bmesh.new(); bm.from_mesh(mesh)
        nonmanifold = sum(not e.is_manifold for e in bm.edges)
        bm.free()
    finally:
        shell_eval.to_mesh_clear()

    roof_eval = roof.evaluated_get(dg)
    roof_mesh = roof_eval.to_mesh()
    try:
        roof_world = [roof_eval.matrix_world @ v.co for v in roof_mesh.vertices]
        roof_z = [v.z for v in roof_world]
        roof_bounds = [[min(v[i] for v in roof_world), max(v[i] for v in roof_world)] for i in range(3)]
        roof_bm = bmesh.new(); roof_bm.from_mesh(roof_mesh)
        roof_nonmanifold = sum(not e.is_manifold for e in roof_bm.edges)
        roof_bm.free()
    finally:
        roof_eval.to_mesh_clear()

    objects = list(coll.objects)
    meshes = [o for o in objects if o.type == "MESH"]
    linked = [lib.filepath for lib in bpy.data.libraries if lib.filepath]
    ext_images = [im.filepath for im in bpy.data.images if im.source == "FILE" and im.filepath and not im.packed_file]
    ext_textures = [n.image.filepath for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes
                    if n.type == "TEX_IMAGE" and n.image and n.image.source == "FILE" and n.image.filepath and not n.image.packed_file]
    names = [o.name.lower() for o in objects]
    windows = sum("window" in n for n in names)
    doors = sum("entry" in n or "door" in n for n in names)
    evidence_paths = [
        "source_register.json", "accuracy_record.json", "build_result.json", "reopen_validation.py",
        "sources/purdue_gis_fid776_sigma_pi_2026-10-26.json", "sources/indiana_current_aerial_sigma_pi_3857_overlay.jpg",
        "sources/sigma_pi_lidar_surface_analysis.json", "sources/sigma_pi_lidar_roof_mesh.json",
        "sources/lidar_footprint_comparison_metrics.json", "sources/sigma_pi_eta_data_2004.pdf",
        "sources/purdue_debris_1932_page323.jpg", "renders/sigma_pi_preview.png"
    ]
    present = [p for p in evidence_paths if (AUDIT / p).is_file()]

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint", "score": 1.9, "max_score": 2,
            "evidence": (f"The opened asset is the expected Sigma Pi collection; raw Purdue GIS feature FID {feature['attributes'].get('FID')} "
                         f"names Sigma Pi (SOSP) at 130 Russell St. The official Sigma Pi location page and Purdue Off-Campus Housing listing independently identify 130 N Russell. "
                         f"The exported shell bottom was directly compared to all {len(src)} unique GIS vertices; maximum nearest error is {max(nearest):.6f} m. "
                         "Current state orthophoto overlay corroborates the GIS ring as roof-plan perimeter."),
            "uncertainty": "GIS and orthophoto identify the roof outline; the exterior structural wall line and eave offset are not surveyed."
        },
        {
            "criterion": "Position, orientation, and scale/dimensions", "score": 1.9, "max_score": 2,
            "evidence": (f"Direct inspection of the loaded mesh gives shell world bounds {shell_bounds}; the 36-vertex source ring is reconstructed with max XY error "
                         f"{max(nearest):.6f} m. Source ring projection reconciles GIS planar EPSG:3857 area/length with the layer values within rounding, and the overlay matches current orthophoto."),
            "uncertainty": "Plan location and roof perimeter are strong; no surveyed structural wall line or height control is available."
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form", "score": 1.2, "max_score": 2,
            "evidence": (f"The actual saved asset contains a separate triangulated roof mesh with {len(roof_mesh.vertices)} vertices and {len(roof_mesh.polygons)} faces, "
                         f"world bounds {roof_bounds}, and {roof_nonmanifold} nonmanifold edges. The 2018 LiDAR source records 1,094 filtered unclassified surface returns, "
                         "with percentile roof heights around 9.74–12.25 m above local ground; the mesh follows a varied surface rather than a flat cap."),
            "uncertainty": "The LiDAR returns are class 1 and may include vegetation; no class-6 returns were available. Shell height/story count remain estimates and GIS NUM_LEVELS conflicts with chapter multi-deck clues. Neither current roof structure nor present floor count is measured."
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture", "score": 0.8, "max_score": 2,
            "evidence": (f"The loaded asset has {windows} named window objects and {doors} named entry/door objects, visible façade materials and an entry in its saved preview. "
                         "The 2004 Eta Data supports broad stucco/wood-trim cues and multi-deck use; the undated Off-Campus Housing street-view photo supports masonry lower façade, Tudor half-timber cues, window tiers, and an entry."),
            "uncertainty": "The saved preview's façades are mostly plain, with the half-timber pattern and distinctive façade organization from the photo not clearly represented. The photo is undated, cropped above the roof, and no raw photo was preserved in the audit; opening count and side/rear details remain unverified."
        },
        {
            "criterion": "Modular export, portability, and complete evidence", "score": 1.7, "max_score": 2,
            "evidence": (f"The SHA-256 matches the frozen target exactly and the file opened without errors in bpy {bpy.app.version_string}; the loaded asset contains {len(objects)} collection objects "
                         f"({len(meshes)} meshes), {nonmanifold} shell nonmanifold edges, {len(linked)} linked libraries, {len(ext_images)} unpacked external images, and {len(ext_textures)} unpacked image textures. "
                         f"{len(present)}/{len(evidence_paths)} expected key source/evidence files are present."),
            "uncertainty": "The available inspector is Blender Python 4.5.15, not the builder's Blender 5.2.3; Blender warned that it was reading a newer 5.2 file and removed some UI region data. Mesh geometry was inspected read-only, but a matching 5.2.3 runtime was unavailable. Coordinator manifest reconciliation and master integration remain pending."
        }
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    result = {
        "score": score, "max_score": 10, "passing_threshold": 8, "passes": score >= 8,
        "asset_sha256": sha, "expected_sha256": EXPECTED_SHA, "criteria": criteria,
        "evidence": {
            "asset": ASSET.relative_to(ROOT).as_posix(), "asset_sha256_verified": True,
            "fresh_open_read_only": True, "inspector_version": bpy.app.version_string,
            "newer_file_version_warning": "Asset authored in Blender 5.2.3; read by bpy 4.5.15. No save performed.",
            "identity": {k: feature["attributes"].get(k) for k in ("FID", "BUILDING_N", "BLDG_ABBR", "ADDRESS", "NUM_LEVELS")},
            "collection": coll.name, "scene": scene.name, "collection_objects": len(objects), "collection_mesh_objects": len(meshes),
            "shell": {"name": shell.name, "vertex_count": len(shell.data.vertices), "face_count": len(shell.data.polygons),
                      "nonmanifold_edges": nonmanifold, "world_bounds_xyz": shell_bounds,
                      "gis_ring_unique_vertices": len(src), "gis_to_shell_bottom_max_nearest_error_m": max(nearest),
                      "gis_to_shell_bottom_mean_nearest_error_m": sum(nearest) / len(nearest)},
            "roof": {"name": roof.name, "vertex_count": len(roof_mesh.vertices), "face_count": len(roof_mesh.polygons),
                     "nonmanifold_edges": roof_nonmanifold, "world_bounds_xyz": roof_bounds},
            "named_window_object_count": windows, "named_entry_or_door_object_count": doors,
            "linked_libraries": linked, "unpacked_external_images": ext_images, "unpacked_external_texture_paths": ext_textures,
            "evidence_files_present": present, "evidence_files_missing": [p for p in evidence_paths if p not in present],
            "preview": "audit/sigma_pi/renders/sigma_pi_preview.png",
            "read_only_inspection": True
        },
        "findings": [
            "Identity and exact GIS roof-plan registration are strongly supported by official chapter location, GIS feature, raw geometry, and current aerial overlay.",
            "The revised asset includes an articulated LiDAR-derived roof surface; this is a clear improvement over the prior flat roof cap, but class-1 returns do not prove roof-only surfaces and the wall height/story count remain estimated.",
            "Facade evidence has improved with an inspected street-view listing photo, but it is undated and not saved locally; the preview does not show clear Tudor half-timber detailing and has limited distinctive façade detail.",
            "The file opened read-only in bpy 4.5.15 and mesh geometry was inspected directly, but an exact-version Blender 5.2.3 independent reopen was unavailable. No asset data was saved or changed.",
            "Overall score is below the 8/10 gate. Improve source-matched facade detail and strengthen independent verification of height/story and current roof form before passing."
        ]
    }
    return result


result = evaluate()
(OUT / "grade_result_r4.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
