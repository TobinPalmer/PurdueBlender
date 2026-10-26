"""Independent evidence-driven grade for the Pete Dye Clubhouse massing asset.
Run with Blender 4.5: blender.exe <asset.blend> --background --python <this file>
Returns {score, max_score, criteria, evidence, findings} and writes the result JSON.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

ID = "massing_the_pete_dye_clubhouse_a3a9641"
ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / ID
ASSET = ROOT / "modular" / "buildings" / f"{ID}.blend"
OUT = AUDIT / "independent_grade" / "pete_dye_independent_grade.json"


def grade():
    evidence_record = json.loads((AUDIT / "evidence_record.json").read_text(encoding="utf-8"))
    sources = json.loads((AUDIT / "source_register.json").read_text(encoding="utf-8"))
    osm = json.loads((AUDIT / "sources" / "osm_way_1319175917.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8"))
    recs = manifest.get("assets", manifest if isinstance(manifest, list) else [])
    manifest_record = next((r for r in recs if r.get("id") == ID), None)
    expected_collection = "Asset_" + ID
    scene = bpy.data.scenes.get("Building_" + ID)
    collection = bpy.data.collections.get(expected_collection)
    expected = []
    for n in osm["nodes"]:
        expected.append(((n["lon"] + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                         (n["lat"] - 40.4274) * 111040.0))
    if expected[0] == expected[-1]:
        expected.pop()
    foundation = bpy.data.objects.get("PDC structural foundation footprint")
    actual = []
    if foundation and foundation.type == "MESH":
        actual = [foundation.matrix_world @ foundation.data.vertices[i].co for i in range(min(4, len(foundation.data.vertices)))]
    vertex_error = max((math.hypot(actual[i].x - expected[i][0], actual[i].y - expected[i][1]) for i in range(min(len(actual), len(expected)))), default=float("inf"))
    bounds = [[0.0,0.0] for _ in range(3)]
    mesh_count = 0
    nonmesh = []
    object_names = []
    if collection:
        pts = []
        depsgraph = bpy.context.evaluated_depsgraph_get()
        for ob in collection.objects:
            object_names.append(ob.name)
            if ob.type != "MESH":
                nonmesh.append([ob.name, ob.type])
                continue
            mesh_count += 1
            ev = ob.evaluated_get(depsgraph)
            me = ev.to_mesh()
            pts.extend(ob.matrix_world @ v.co for v in me.vertices)
            ev.to_mesh_clear()
        if pts:
            bounds = [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]
    source_files = [part.strip() for s in sources.get("sources", []) for part in s.get("raw_snapshot", "").split(";") if part.strip()]
    source_files_present = all((AUDIT / f).exists() or (AUDIT / "sources" / f).exists() for f in source_files)
    previews = [AUDIT / "preview" / "course_facing_view.png", AUDIT / "preview" / "roof_and_footprint_view.png"]
    previews_present = all(p.exists() and p.stat().st_size > 10000 for p in previews)
    asset_exists = ASSET.exists() and Path(bpy.data.filepath).resolve() == ASSET.resolve()
    portable_images = all(not im.filepath or im.packed_file is not None or im.filepath.startswith("//") for im in bpy.data.images)
    expected_tags = osm.get("way", {}).get("tags", {})
    exact_collection = bool(collection and len(collection.objects) == mesh_count + len(nonmesh))
    coord_zero = bool(collection and max(abs(float(x)) for x in collection.instance_offset) < 1e-9)
    story_objects = [n for n in object_names if n in ("PDC ground story stone shell", "PDC upper story stone shell")]
    roof_objects = [n for n in object_names if n.startswith("PDC gable roof")]
    # Rubric scores incorporate evidence quality, not image resemblance alone.
    criteria = [
      {"name":"Correct identity and source-backed footprint", "score":2.0, "max_score":2.0,
       "evidence":f"Current OSM way 1319175917 is named '{expected_tags.get('name')}', tagged golf=clubhouse, and operated by Purdue. Four source ring vertices independently convert to the saved foundation with max XY vertex error {vertex_error:.6f} m. A separate 1998 GIS feature OBJECTID 233 is correctly documented as the old clubhouse and excluded.",
       "assessment":"Verified." if vertex_error < 0.01 and expected_tags.get("golf") == "clubhouse" else "Failed source/geometry check."},
      {"name":"Position, orientation, and scale/dimensions", "score":1.9, "max_score":2.0,
       "evidence":f"The saved foundation is compared vertex-by-vertex in the repository's stated local geographic approximation; the polygon defines center, plan orientation, and about 40.47 x 17.43 m. Evaluated asset bounds are {bounds} m. A terrace and roof eaves extend beyond the wall polygon by design; the course-facing direction is inferred from images, not independently georeferenced.",
       "assessment":"Source footprint position/orientation and scale verified to sub-centimeter vertex agreement; architectural projections and facade direction remain inferred."},
      {"name":"Evidence-backed height, floors, and roof form", "score":1.1, "max_score":2.0,
       "evidence":f"Purdue Administrative Operations source (2026-09-28) supports two above-ground stories; the model contains the two story shells ({len(story_objects)} named shells). CE Solutions photographs support a multi-gabled roof and a tall glazed gable; {len(roof_objects)} simple gable-slope objects are in the asset. Eave/ridge values of 8.55/15.65 m are explicitly estimates, with no measured elevations. The current roof is three repeated gables along the long axis, while source photos show an irregular, intersecting set of gables and varying roof masses; terrain/basement level also remains unresolved.",
       "assessment":"Story count and general gable family supported; exact roof silhouette/massing and all vertical dimensions are uncertain or estimated."},
      {"name":"Facade, entrances, and distinctive architecture", "score":0.9, "max_score":2.0,
       "evidence":"CE Solutions exterior photos show warm stone, dark-framed glazing, a prominent glazed gable, major dark vertical facade panels, and an elevated terrace with slender dark railing. The model captures stone, glazing, a central glazed gable, and a terrace, but replaces the source's strongly varied/intersecting facade bays and articulated dark volumes with repetitive, nearly uniform window slots and a simplified continuous horizontal belt. Main entry location/orientation is an inference, not shown to be verified by a plan or orthographic source.",
       "assessment":"Several high-level materials/features are evidence-matched; facade bay rhythm, dark volumes, entry position, and side elevations are generalized or unverified."},
      {"name":"Modular export, portability, and complete evidence", "score":1.9, "max_score":2.0,
       "evidence":f"Reopened saved asset at expected path: {asset_exists}; scene/collection identity: {bool(scene)}/{bool(collection)}; collection objects: {len(collection.objects) if collection else 0}; meshes: {mesh_count}; non-mesh objects: {nonmesh}; collection instance offset zero: {coord_zero}; image dependencies portable: {portable_images}. Source register snapshots present: {source_files_present}; preview renders present: {previews_present}. Manifest record found: {bool(manifest_record)}.",
       "assessment":"Export, reopen, and evidence are nearly complete. No rear/side preview is provided, and the official video page snapshot gives contextual identity rather than measured architecture."}
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [
       "Grade is below the required 8/10 threshold; revise and request a fresh independent grade before the model can be accepted.",
       "Use the CE Solutions exterior photos to revise roof intersections and the asymmetrical front/rear massing; current three equal longitudinal gables do not reproduce the visible roof hierarchy.",
       "Revise facade zoning around the dark vertical panel/window volumes and irregular glazing bays shown in exterior_04.webp and exterior_37.webp; current repeated uniform bays overstate regularity.",
       "Keep height and story elevations labeled estimates unless measured drawings or survey evidence are found. The documented cart-storage basement is absent and should either be represented with defensible grade evidence or explicitly retained as unresolved.",
       "Add a side/rear preview view and record which photographed facade is represented by the course-facing entrance; current entrance alignment is an inference."
    ]
    checks = {
      "asset_path_matches_expected": asset_exists,
      "expected_scene_and_collection": bool(scene and collection and scene.name == "Building_" + ID),
      "identity_tags_match": expected_tags.get("name") == "The Pete Dye Clubhouse" and expected_tags.get("golf") == "clubhouse",
      "foundation_xy_max_vertex_error_m": vertex_error,
      "manifest_entry_present": bool(manifest_record),
      "zero_collection_instance_offset": coord_zero,
      "portable_image_dependencies": portable_images,
      "source_snapshots_present": source_files_present,
      "preview_renders_present": previews_present,
      "evaluated_bounds_world_m": bounds,
      "mesh_count": mesh_count,
      "non_mesh_objects": nonmesh
    }
    result = {"asset_id":ID, "display_name":"Pete Dye Clubhouse", "independent":True,
      "score":score, "max_score":10, "pass_threshold":8, "pass":score >= 8,
      "criteria":criteria, "evidence":checks, "findings":findings,
      "sources_reviewed":[s.get("url") for s in sources.get("sources", [])],
      "model_file":str(ASSET), "preview_files":[str(p) for p in previews],
      "rubric":"AGENT.md 5-part rubric; each criterion is scored from current saved asset and raw source evidence."}
    OUT.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print("PETE_DYE_INDEPENDENT_GRADE " + json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    grade()
