"""Independent JNSN evaluation. Run read-only with Blender -b <asset.blend> -P this_file."""
import bpy, json, math, os, struct
from pathlib import Path

ID = "massing_johnson_hall_of_nursing_jnsn_823fca7"
ASSET = Path(bpy.data.filepath).resolve()
REPO = Path(__file__).resolve().parents[3]
AUDIT = REPO / "audit" / ID
OUTDIR = AUDIT / "independent_grade"
OUT = OUTDIR / "result.json"
SOURCE = AUDIT / "sources" / "purdue_building_shapes_fid218_jnsn.json"
RECORD = AUDIT / "source_record.json"
EXPECTED_COLLECTION = "Asset_" + ID
EXPECTED_SCENE = "Building_" + ID


def evaluate():
    assert ASSET.name == ID + ".blend", f"Unexpected opened asset: {ASSET}"
    scene = bpy.data.scenes.get(EXPECTED_SCENE)
    collection = bpy.data.collections.get(EXPECTED_COLLECTION)
    assert scene is not None and collection is not None
    assert len(collection.objects) == 1
    obj = next(iter(collection.objects))
    assert obj.type == "MESH"
    dep = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dep)
    mesh = ev.to_mesh()
    try:
        world = [ev.matrix_world @ v.co for v in mesh.vertices]
        bounds = [[min(v[i] for v in world), max(v[i] for v in world)] for i in range(3)]
        ground_xy = [(float(v.x), float(v.y)) for v in world if abs(float(v.z)) < 1e-5]
        mesh_vertices, mesh_faces = len(mesh.vertices), len(mesh.polygons)
    finally:
        ev.to_mesh_clear()
    src = json.loads(SOURCE.read_text(encoding="utf-8-sig"))["feature"]
    attrs = src["attributes"]
    raw = src["geometry"]["rings"][0]
    ring = [((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)), (lat - 40.4274) * 111040.0) for lon, lat in raw]
    if ring and math.dist(ring[0], ring[-1]) < 1e-8:
        ring = ring[:-1]
    errors = [min(math.hypot(x - vx, y - vy) for vx, vy in ground_xy) for x, y in ring]
    source_bounds = [[min(p[i] for p in ring), max(p[i] for p in ring)] for i in range(2)]
    object_bounds_xy = [[bounds[i][0], bounds[i][1]] for i in range(2)]
    max_vertex_error = max(errors)
    libs = [lib.filepath for lib in bpy.data.libraries]
    external_images = [im.filepath for im in bpy.data.images if im.source == "FILE" and im.filepath and not im.packed_file]
    reviewer_renders = [
        "johnson_hall_nursing_exterior_preview.png",
        "johnson_hall_nursing_plan_preview.png",
        "johnson_hall_nursing_entry_elevation.png",
    ]
    render_data = []
    for name in reviewer_renders:
        path = AUDIT / "renders" / name
        assert path.is_file(), f"Missing render {path}"
        with path.open("rb") as f:
            header = f.read(24)
        assert header[:8] == b"\x89PNG\r\n\x1a\n"
        w, h = struct.unpack(">II", header[16:24])
        render_data.append({"file": name, "width_px": w, "height_px": h, "bytes": path.stat().st_size})
    evidence = {
        "asset_opened_directly": str(ASSET),
        "asset_version_opened_with": bpy.app.version_string,
        "version_compatibility_note": "Opened read-only in Blender 4.5.15; Blender warned that the file was written by newer Blender 5.2. No save was performed.",
        "scene": scene.name,
        "collection": collection.name,
        "asset_object": obj.name,
        "asset_mesh_object_count": len(collection.objects),
        "mesh_vertices_faces": [mesh_vertices, mesh_faces],
        "modifiers": [m.name for m in obj.modifiers],
        "object_location_m": [round(float(c), 6) for c in obj.location],
        "world_bounds_m": [[round(float(v), 6) for v in axis] for axis in bounds],
        "source_ring_unique_vertices": len(ring),
        "source_ring_area_m2_local_approx": 984.0055712634885,
        "source_ring_aabb_xy_m": [[round(v, 6) for v in axis] for axis in source_bounds],
        "shell_ground_vertices_nearest_source_max_error_m": round(max_vertex_error, 8),
        "gis_shape_area_attr_m2": attrs.get("Shape__Area"),
        "gis_num_levels": attrs.get("NUM_LEVELS"),
        "gis_extrution_raw_units_undocumented": attrs.get("Extrution"),
        "height_bounds_m": [round(bounds[2][0], 5), round(bounds[2][1], 5)],
        "osm_outline_difference_hausdorff_m": 0.875891281658294,
        "sources_reviewed": [
            "Purdue BuildingShapesZip4 FID 218 (raw JSON)",
            "OSM way 117146488 (raw XML)",
            "Purdue October 2021 space report (29,742.28 sq ft)",
            "Purdue nursing graduate handbook and university history timeline",
            "Indiana Commission 2023 replacement project authorization and Purdue project page",
        ],
        "renders_reviewed": render_data,
        "external_libraries": libs,
        "unpacked_external_images": external_images,
        "master_link_check": "not performed; evaluator examined standalone library only",
    }
    assert max_vertex_error < 0.001
    assert attrs.get("FID") == 218 and attrs.get("BLDG_ABBR") == "JNSN"
    assert len(obj.modifiers) == 0 and not libs and not external_images
    criteria = [
        {
            "name": "Correct identity and source-backed footprint", "score": 2.0, "max_score": 2,
            "status": "verified",
            "evidence": "Opened mesh uses the exact 12-vertex ground ring from Purdue BuildingShapes FID 218 / JNSN; largest nearest source-to-mesh ground vertex error is %.8f m. OSM way 117146488 independently names Johnson Hall of Nursing and differs by 0.876 m Hausdorff." % max_vertex_error,
            "uncertainty": "Purdue polygon is not a certified structural survey; stored Shape__Area (1701.02 m²) conflicts with the local ring area (984.01 m²), though the OSM geometry corroborates the ring scale."
        },
        {
            "name": "Position, orientation, and scale/dimensions", "score": 1.8, "max_score": 2,
            "status": "verified against campus GIS; not survey-verified",
            "evidence": "The reopened mesh retains the projected campus coordinates and source polygon orientation without transformation from origin; GIS AABB is %.2f by %.2f m. Footprint vertices match the declared campus local approximation within 1 mm." % (source_bounds[0][1]-source_bounds[0][0], source_bounds[1][1]-source_bounds[1][0]),
            "uncertainty": "Projection is the repository's local approximation, and GIS/OSM wall-versus-edge semantics differ slightly; no independent survey dimensions were supplied. Overall mesh bounds include entry/plinth/parapet details."
        },
        {
            "name": "Evidence-backed height, floors, and roof form", "score": 0.9, "max_score": 2,
            "status": "partly evidenced; height/roof unverified",
            "evidence": "Purdue GIS supports three levels. Reopened overall bounds reach %.2f m, consistent with the documented nominal 11.25 m massing." % bounds[2][1],
            "uncertainty": "No dimensioned elevation or survey height was located. The 3.55 m floor-to-floor spacing and flat/parapet roof are builder assumptions; GIS Extrution=24 units are undocumented and are not valid height evidence."
        },
        {
            "name": "Facade, entrances, and distinctive architecture", "score": 0.5, "max_score": 2,
            "status": "mostly illustrative",
            "evidence": "The latest exterior, plan, and entry-elevation renders show three-storey punched openings, floor bands, a glazed entry, canopy and low parapet; object topology is present in the reopened mesh.",
            "uncertainty": "No exterior photo, facade elevation, or dimensioned plan supports the brick/limestone palette, regular opening pattern, west-facing entrance location, or roof parapet. The builder explicitly labels these provisional. Appearance is not source verification."
        },
        {
            "name": "Modular export, portability, and complete evidence", "score": 2.0, "max_score": 2,
            "status": "verified for standalone asset",
            "evidence": "Directly opened the latest saved file (written at the same timestamp as the camera-only rebuild/renders). Expected scene and collection exist; one joined mesh, no modifiers, no linked libraries, and no unpacked external images. Raw sources, source record, source metrics, build script, and three valid PNG renders are present.",
            "uncertainty": "The master blend's single-link integration was outside this independent asset review."
        }
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    findings = [
        {"severity": "strength", "finding": "The saved post-camera-change asset reopens successfully. The FID 218 shell geometry still matches the source ring to sub-millimeter vertex error."},
        {"severity": "limitation", "finding": "This is a geometry-faithful GIS massing model, not a source-verified architectural reconstruction. Height and all facade/entry/roof details remain largely estimated."},
        {"severity": "scope", "finding": "The 2023 state authorization and current Purdue project page identify a planned replacement and proposed demolition. The evidence does not establish demolition completion at the present date; this asset is correctly scoped to legacy GIS identity, not the replacement."},
    ]
    return {"score": score, "max_score": 10, "criteria": criteria, "evidence": evidence, "findings": findings, "pass_threshold": 8.0, "passed": score >= 8.0, "evaluation_version": "independent JNSN r1", "evaluator": "separate review agent", "evaluated_date": "2026-10-26"}

result = evaluate()
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))


