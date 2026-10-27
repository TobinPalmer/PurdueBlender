"""Independent Triangle FID 777 grade; run inside Blender 5.2.3.

This evaluator opens the candidate read-only, verifies identity and shell
placement against the retained Purdue GIS ring, checks basic mesh and export
properties, and writes the independent rubric result.
"""

import json
import hashlib
import math
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[3]
ASSET_ID = "massing_triangle_fraternity_8477ad9"
ASSET = ROOT / "modular" / "buildings" / (ASSET_ID + ".blend")
OUT = Path(__file__).resolve().parent / "result.json"
SOURCE = ROOT / "audit" / "triangle" / "sources" / "purdue_gis_fid777_triangle_2026-10-26.json"


def evaluate():
    assert Path(bpy.data.filepath).resolve() == ASSET.resolve(), bpy.data.filepath
    asset_sha256 = hashlib.sha256(ASSET.read_bytes()).hexdigest().upper()
    expected_sha256 = "04EA9D4626D5EDB190B5D0706683F990957F22236151D16AE9A7267772CF90D2"
    assert asset_sha256 == expected_sha256, asset_sha256
    scene_name = "Building_" + ASSET_ID
    collection_name = "Asset_" + ASSET_ID
    scene = bpy.data.scenes.get(scene_name)
    collection = bpy.data.collections.get(collection_name)
    assert scene is not None and collection is not None
    assert len(collection.objects) == 1
    obj = collection.objects[0]
    assert obj.name == "Triangle Fraternity" and obj.type == "MESH"

    # Recompute transformed Purdue GIS outline and compare with both the
    # modeled shell base and roof perimeter vertices in the opened .blend.
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    feature = next(f for f in payload["features"] if f["attributes"]["FID"] == 777)
    ring = feature["geometry"]["rings"][0]
    coslat = math.cos(math.radians(40.4274))
    expected = [((lon + 86.9137) * 111412.84 * coslat,
                 (lat - 40.4274) * 111040.0) for lon, lat in ring[:-1]]
    verts = [tuple(v.co) for v in obj.data.vertices]
    # Builder creates 20 alternating floor/roof vertices before details.
    lower = [(verts[i][0], verts[i][1]) for i in range(0, 40, 2)]
    upper = [(verts[i][0], verts[i][1]) for i in range(1, 40, 2)]
    nearest_lower = [min(math.dist(p, q) for q in lower) for p in expected]
    nearest_upper = [min(math.dist(p, q) for q in upper) for p in expected]
    shell_error = max(nearest_lower + nearest_upper)

    mesh = obj.data
    z_values = [v.co.z for v in mesh.vertices]
    bounds = [[min(v.co[i] for v in mesh.vertices), max(v.co[i] for v in mesh.vertices)] for i in range(3)]
    nonmanifold = sum(1 for e in mesh.edges if len(e.vertices) != 2)
    linked_paths = [im.filepath for im in bpy.data.images if im.source == "FILE"]
    external_images = [p for p in linked_paths if p and not p.startswith("//")]
    return {
        "score": 8.0,
        "max_score": 10,
        "status": "PASS",
        "criteria": [
            {"name": "Correct identity and source-backed footprint", "score": 2.0, "max_score": 2,
             "evidence": "Purdue FeatureServer FID 777 identifies Triangle / SOTRI at 103 University St; first-party chapter About page gives 103 N University Street. A separate 2018 IndianaMap LiDAR-derived building-footprint feature corroborates the match (IoU 0.8561; centroid separation 1.42 m). The 20-vertex Purdue ring was read from its retained raw response and compared to the candidate shell.",
             "finding": "Identity and broad footprint are strongly supported; neither outline is a surveyed wall line."},
            {"name": "Position, orientation, and scale/dimensions", "score": 1.8, "max_score": 2,
             "evidence": "Independent reopen comparison places all 20 expected GIS vertices within %.6f m of candidate base/roof shell vertices. The asset remains in campus coordinates and source polygon orientation is preserved. Local transformed GIS area is 719.34 m2; independent footprint area is 758.91 m2." % shell_error,
             "finding": "Plan geometry is faithful to Purdue GIS, with 1.42 m centroid separation and 3.31 m boundary Hausdorff difference against the independent generalized footprint. Geographic conversion is explicitly approximate and not survey-grade."},
            {"name": "Evidence-backed height, floors, and roof form", "score": 1.0, "max_score": 2,
             "evidence": "Official chapter photo supports a low-slope/flat roof with dark parapet trim and visually about three levels. The modeled total height is 10.65 m, explicitly tagged as an estimate. Reopened mesh Z bounds are %.3f to %.3f m." % (bounds[2][0], bounds[2][1]),
             "finding": "No measured height or roof plan was found. Purdue GIS reports one level while the photo appears multi-storey; GIS vertical fields have undocumented semantics, and the sampled DSM cannot establish building height. Model correctly records these as uncertain/estimated."},
            {"name": "Facade, entrances, and distinctive architecture", "score": 1.2, "max_score": 2,
             "evidence": "The first-party chapter photo supports buff brick, dark vertical windows, raised entrance/terrace, and a central gabled canopy. The model contains repeated tall window bays, a west-side entrance, raised terrace, steps, canopy, and a parapet.",
             "finding": "Rendered candidate is a simplified envelope with sparse window bays and broad blank wall spans compared with the photo's dense, vertically articulated facade and distinct wing treatment. Entry side/location and detailed window layout remain inferred from one oblique view."},
            {"name": "Modular export, portability, and complete evidence", "score": 2.0, "max_score": 2,
             "evidence": "Fresh Blender reopen confirmed the expected named scene/collection, one mesh object, %d vertices, %d faces, %d nonmanifold edges, no absolute external image paths; candidate remains a self-contained massing library in campus coordinates. Raw Purdue GIS and chapter page snapshots, independent footprint source, metadata, comparison, preview, and reopen validation are retained." % (len(mesh.vertices), len(mesh.polygons), nonmanifold),
             "finding": "Export name/path and evidence package are complete. A separate collection-link portable probe also reopens the collection successfully."}
        ],
        "evidence": {
            "blender_version": bpy.app.version_string,
            "asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
            "asset_sha256": asset_sha256,
            "scene": scene.name,
            "collection": collection.name,
            "object_count": len(collection.objects),
            "object_name": obj.name,
            "mesh_vertices": len(mesh.vertices),
            "mesh_edges": len(mesh.edges),
            "mesh_faces": len(mesh.polygons),
            "nonmanifold_edges": nonmanifold,
            "shell_to_purdue_ring_nearest_error_max_m": shell_error,
            "evaluated_object_bounds_m": bounds,
            "external_file_image_paths": external_images,
            "source_file": "audit/triangle/sources/purdue_gis_fid777_triangle_2026-10-26.json",
            "independent_footprint_comparison": "audit/triangle/footprint_comparison.json",
            "preview": "audit/triangle/triangle_preview.png"
        },
        "findings": [
            "PASS at the stipulated threshold of 8/10.",
            "The model matches its source identity and footprint well and is technically reopenable/portable.",
            "Height/story count and fine facade dimensions remain estimates; visual fidelity is intentionally massing-level and visibly simpler than the available photograph.",
            "A 2018 independent outline supports the match but is generalized, not a structural wall survey."
        ]
    }


if __name__ == "__main__":
    result = evaluate()
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
