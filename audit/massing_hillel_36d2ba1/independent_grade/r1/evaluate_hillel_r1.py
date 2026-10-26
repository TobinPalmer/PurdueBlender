"""Independent Hillel evaluation. Opens the saved asset and writes only here.

Run: blender --background --python evaluate_hillel_r1.py
"""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ASSET_ID = "massing_hillel_36d2ba1"
ASSET = ROOT / "modular" / "buildings" / (ASSET_ID + ".blend")
AUDIT = ROOT / "audit" / ASSET_ID
GRADE = AUDIT / "independent_grade" / "r1"
GIS = AUDIT / "gis_feature_803.json"
OUT_INSPECTION = GRADE / "direct_inspection.json"
OUT_RESULT = GRADE / "result.json"
RADIUS = 6378137.0

def web_mercator_to_local(x, y):
    lon = math.degrees(x / RADIUS)
    lat = math.degrees(2.0 * math.atan(math.exp(y / RADIUS)) - math.pi * 0.5)
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)

def polygon_area(points):
    return abs(sum(points[i][0] * points[(i + 1) % len(points)][1]
                   - points[(i + 1) % len(points)][0] * points[i][1]
                   for i in range(len(points))) * 0.5)

def inspect_asset():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.data.scenes.get("Building_" + ASSET_ID)
    coll = bpy.data.collections.get("Asset_" + ASSET_ID)
    objs = list(coll.objects) if coll else []
    deps = bpy.context.evaluated_depsgraph_get()
    mesh_records = []
    all_world = []
    shell_world = []
    for obj in objs:
        if obj.type != "MESH":
            continue
        ev = obj.evaluated_get(deps)
        mesh = ev.to_mesh()
        coords = [ev.matrix_world @ v.co for v in mesh.vertices]
        all_world.extend(coords)
        if obj.name == "Hillel":
            shell_world = coords
        mesh_records.append({
            "name": obj.name,
            "vertices": len(mesh.vertices),
            "faces": len(mesh.polygons),
            "modifiers": [m.name for m in obj.modifiers],
            "materials": [m.name if m else None for m in mesh.materials],
            "linked_library": obj.library.filepath if obj.library else None,
        })
        ev.to_mesh_clear()
    bounds = [[min(v[i] for v in all_world), max(v[i] for v in all_world)]
              for i in range(3)] if all_world else None
    shell_bounds = [[min(v[i] for v in shell_world), max(v[i] for v in shell_world)]
                    for i in range(3)] if shell_world else None
    data = json.loads(GIS.read_text(encoding="utf-8-sig"))
    feature = data.get("feature", data.get("features", [{}])[0])
    attrs = feature["attributes"]
    provenance = json.loads((AUDIT / "source_record.json").read_text(encoding="utf-8-sig"))
    gis_provenance = provenance["sources"][0]
    raw_rings = feature["geometry"]["rings"]
    ring_xy = [web_mercator_to_local(x, y) for x, y in raw_rings[0]]
    if len(ring_xy) > 1 and math.dist(ring_xy[0], ring_xy[-1]) < 0.01:
        ring_xy = ring_xy[:-1]
    ring_clean = []
    for p in ring_xy:
        if not ring_clean or math.dist(p, ring_clean[-1]) > 0.01:
            ring_clean.append(p)
    if len(ring_clean) > 2 and math.dist(ring_clean[0], ring_clean[-1]) <= 0.01:
        ring_clean.pop()
    base_shell = [v for v in shell_world if abs(v.z) < 0.001]
    errors = [min(math.hypot(v.x-x, v.y-y) for v in base_shell)
              for x, y in ring_clean] if base_shell else []
    area = polygon_area(ring_clean)
    unpacked_images = [img.filepath for img in bpy.data.images
                       if img.source == "FILE" and img.filepath and not img.packed_file]
    libraries = [lib.filepath for lib in bpy.data.libraries]
    renders = ["hillel_exterior_oblique.png", "hillel_roof_top.png", "hillel_roof_plan_detail.png"]
    source_docs = ["2019_tippecanoe_hillel_sketch_plan.pdf",
                   "2019_tippecanoe_variance_minutes.pdf", "purdue_hillel_contact.html"]
    return {
        "opened_saved_asset": True,
        "blender_version": bpy.app.version_string,
        "asset": str(ASSET),
        "scene": scene.name if scene else None,
        "collection": coll.name if coll else None,
        "collection_object_count": len(objs),
        "scene_object_count": len(scene.objects) if scene else None,
        "mesh_objects": mesh_records,
        "world_bounds_m": bounds,
        "world_dimensions_m": [b[1]-b[0] for b in bounds] if bounds else None,
        "structural_shell_bounds_m": shell_bounds,
        "structural_shell_dimensions_m": [b[1]-b[0] for b in shell_bounds] if shell_bounds else None,
        "gis_feature": {
            "FID": attrs.get("FID"), "BLDG_ABBR": attrs.get("BLDG_ABBR"),
            "BUILDING_N": attrs.get("BUILDING_N"), "ADDRESS": attrs.get("ADDRESS"),
            "NUM_LEVELS": attrs.get("NUM_LEVELS"), "CountOfFLO": attrs.get("CountOfFLO"),
            "Extrution": attrs.get("Extrution"), "Shape__Area_web_mercator_m2": attrs.get("Shape__Area"),
            "source_crs": gis_provenance.get("source_crs"),
            "ring_count": len(raw_rings), "ring_vertices_excluding_closure": len(ring_clean),
            "transformed_ring_area_m2": area,
            "transformed_ring_bounds_xy_m": [[min(p[0] for p in ring_clean), max(p[0] for p in ring_clean)],
                                                [min(p[1] for p in ring_clean), max(p[1] for p in ring_clean)]],
            "max_nearest_shell_ground_vertex_error_m": max(errors) if errors else None,
            "mean_nearest_shell_ground_vertex_error_m": sum(errors)/len(errors) if errors else None,
        },
        "external_libraries": libraries,
        "unpacked_external_images": unpacked_images,
        "render_engine_setting": scene.render.engine if scene else None,
        "review_runtime_note": "Blender 4.5.15 reported this .blend was written by binary version 502.44 and reported that engine BLENDER_EEVEE is unavailable. Geometry and collection data were directly inspected; render-engine compatibility was not verified.",
        "render_files": [{"path": name, "exists": (AUDIT/name).is_file(),
                           "bytes": (AUDIT/name).stat().st_size if (AUDIT/name).is_file() else 0}
                          for name in renders],
        "county_and_identity_sources": [{"path": name, "exists": (AUDIT/name).is_file(),
                                         "bytes": (AUDIT/name).stat().st_size if (AUDIT/name).is_file() else 0}
                                        for name in source_docs],
        "county_plan_overlay_images": ["audit/"+ASSET_ID+"/site_detail.png",
                                        "audit/"+ASSET_ID+"/hillel_roof_plan_detail.png"],
    }

def evaluate(inspect):
    gis = inspect["gis_feature"]
    images_ok = not inspect["unpacked_external_images"] and not inspect["external_libraries"]
    renders_ok = len(inspect["render_files"]) == 3 and all(
        r["exists"] and r["bytes"] > 10000 for r in inspect["render_files"])
    shell_ok = (gis["FID"] == 803 and gis["BLDG_ABBR"] == "SOHIL"
                and gis["BUILDING_N"] == "Hillel Foundation"
                and gis["ring_vertices_excluding_closure"] == 12
                and (gis["max_nearest_shell_ground_vertex_error_m"] or 1) < 0.001)
    criterion = [
        {"criterion": "Correct identity and source-backed footprint", "score": 2.0 if shell_ok else 0.5,
         "max_score": 2,
         "assessment": "Purdue GIS FID 803 / SOHIL explicitly names Hillel Foundation at 912 W State Street. The county 2019 hearing identifies the Hillel Jewish Center at that address, and the current Hillel site records the renamed address. The converted 12-vertex feature shell is closely supported by the aerial-underlay roof and the county's approximate 6,500 sq ft existing-building area.",
         "uncertainty": "The county record also documents a proposed 845 sq ft addition, but does not establish completion. The official GIS feature has no source date/survey status; its footprint may represent the pre-addition building."},
        {"criterion": "Position, orientation, and scale/dimensions", "score": 1.8 if shell_ok else 0.7,
         "max_score": 2,
         "assessment": "The shell is placed in the documented campus-world frame and directly follows the converted GIS polygon. Its 610.95 m2 plan area is close to the hearing's approximate 6,500 sq ft (603.87 m2); county plan/aerial supports corner-site context and the current roof outline. The west-facing front is corroborated by the minutes.",
         "uncertainty": "Coordinate conversion is approximate and the county plan is a 2019 subdivision sketch, not a surveyed building footprint; its annotated aerial is not used for independent metric registration. Exact structural wall dimensions remain unverified."},
        {"criterion": "Evidence-backed height, floors, and roof form", "score": 1.0,
         "max_score": 2,
         "assessment": "GIS lists NUM_LEVELS=1 / CountOfFLO=1 and Extrution=12, and the model represents a low one-level massing. The county aerial confirms a roof plane exists.",
         "uncertainty": "No measured elevation or source establishes whether Extrution=12 means feet or the actual eave height. At 3.6576 m the model uses a plausible but unverified 12 ft extrusion. The aerial/plan cannot establish roof pitch or exact roof silhouette, so the flat/low-slope cap is a neutral schematic."},
        {"criterion": "Facade, entrances, and distinctive architecture", "score": 0.6,
         "max_score": 2,
         "assessment": "The model includes schematic wall, windows, glazing, trim, and a west-facing entry; its front direction is supported by the county hearing statement that the building faces Waldron Street.",
         "uncertainty": "Available primary evidence does not show an exterior elevation or sufficiently clear facade image. Window count, spacing, materials, entry size/position, roof finish, and architectural character are illustrative and cannot be verified from the aerial/site plan."},
        {"criterion": "Modular export, portability, and complete evidence", "score": 1.5 if (inspect["scene"] == "Building_"+ASSET_ID and inspect["collection"] == "Asset_"+ASSET_ID and inspect["collection_object_count"] == 5 and images_ok and renders_ok) else 1.0,
         "max_score": 2,
         "assessment": "Direct reopen confirms the expected scene and collection with five mesh objects, no modifiers, no external libraries, and no unpacked file images. Raw GIS, county plan/minutes, official Hillel identity snapshot, detailed provenance/uncertainty, and preview renders are present.",
         "uncertainty": "The saved asset reports Blender 5.2.0 LTS; this review runtime was Blender 4.5.15 and warned about the forward file version and unavailable BLENDER_EEVEE engine. Mesh and collection data were inspectable, but render-engine compatibility was not verified."},
    ]
    score = round(sum(c["score"] for c in criterion), 1)
    findings = [
        {"severity": "major", "finding": "The GIS extrusion is the only height clue, with no documented units or measured roof/eave level; roof pitch is not established by the top-down evidence.",
         "action": "Keep 3.6576 m explicitly provisional and seek a dimensioned elevation/as-built drawing or a reliable oblique source before claiming vertical accuracy."},
        {"severity": "major", "finding": "Facade and entry details are schematic, with no elevation/photo evidence for windows, material, count, spacing, or exact entrance geometry.",
         "action": "Retain the current conservative schematic, or refine only after acquiring photo/elevation evidence; do not present the illustrative facade as verified."},
        {"severity": "moderate", "finding": "A 2019 county hearing proposed an 845 sq ft addition, but no completion record is in the source set. The modeled footprint appears to follow the pre-addition feature and is close to the county's existing-area estimate.",
         "action": "Document the pre-addition interpretation and seek a later parcel/as-built footprint if the model is intended to show the current building."},
        {"severity": "minor", "finding": "This independent reopen used Blender 4.5.15 against a file saved by Blender 5.2.0; the file opened for mesh inspection but emitted a forward-version warning and its BLENDER_EEVEE engine identifier was unavailable.",
         "action": "Verify opening and rendering in the intended Blender 5.2 environment; do not save the file from the older reviewer runtime."},
    ]
    return {"building_id": ASSET_ID, "review_revision": "r1", "score": score,
            "max_score": 10, "passing_threshold": 8, "passed": score >= 8,
            "criteria": criterion,
            "evidence": {
                "asset": "modular/buildings/"+ASSET_ID+".blend",
                "direct_reopen_measurements": "audit/"+ASSET_ID+"/independent_grade/r1/direct_inspection.json",
                "builder_reopen_validation": "audit/"+ASSET_ID+"/reopen_validation.json",
                "source_record": "audit/"+ASSET_ID+"/source_record.json",
                "GIS_feature": "audit/"+ASSET_ID+"/gis_feature_803.json",
                "county_sketch_plan": "audit/"+ASSET_ID+"/2019_tippecanoe_hillel_sketch_plan.pdf",
                "county_variance_minutes": "audit/"+ASSET_ID+"/2019_tippecanoe_variance_minutes.pdf",
                "official_contact_snapshot": "audit/"+ASSET_ID+"/purdue_hillel_contact.html",
                "visual_review": ["audit/"+ASSET_ID+"/hillel_exterior_oblique.png", "audit/"+ASSET_ID+"/hillel_roof_top.png",
                                  "audit/"+ASSET_ID+"/hillel_roof_plan_detail.png", "audit/"+ASSET_ID+"/site_detail.png"],
                "direct_measurements": inspect},
            "findings": findings}

GRADE.mkdir(parents=True, exist_ok=True)
inspection = inspect_asset()
OUT_INSPECTION.write_text(json.dumps(inspection, indent=2) + "\n", encoding="utf-8")
result = evaluate(inspection)
OUT_RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
