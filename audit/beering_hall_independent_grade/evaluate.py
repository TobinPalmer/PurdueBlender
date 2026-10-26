"""Independent Beering Hall evaluator. Run from the PurdueBlender project root."""
from __future__ import annotations
import json, math, subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
GRADE = PROJECT / "audit/beering_hall_independent_grade"
ASSET = PROJECT / "modular/buildings/beering_hall.blend"
BLENDER = PROJECT.parent / "blender/blender-4.5.15-windows-x64/blender.exe"


def bounds(points):
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(2)]


def evaluate(run_blender: bool = True):
    if run_blender:
        if not BLENDER.exists():
            raise FileNotFoundError(f"Blender executable not found: {BLENDER}")
        for script, logname in [("blender_probe.py", "blender_probe.log"),
                                ("reopen_export_probe.py", "export_probe.log")]:
            proc = subprocess.run([str(BLENDER), "-b", "--python", str(GRADE / script),
                                   "--python-exit-code", "1"], cwd=PROJECT,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  text=True, timeout=180)
            (GRADE / logname).write_text(proc.stdout, encoding="utf-8")
            if proc.returncode:
                raise RuntimeError(f"{script} failed; see {GRADE / logname}")
    src = json.loads((GRADE / "source_gis_feature_251.json").read_text(encoding="utf-8"))
    record = json.loads((GRADE / "source_record.json").read_text(encoding="utf-8"))
    model = json.loads((GRADE / "blender_probe.json").read_text(encoding="utf-8"))
    exported = json.loads((GRADE / "export_probe_result.json").read_text(encoding="utf-8"))
    manifest = json.loads((PROJECT / "modular/manifest.json").read_text(encoding="utf-8"))
    entry = next(a for a in manifest["assets"] if a["id"] == "beering_hall")
    feature = src["features"][0]
    attrs = feature["properties"]
    assert feature["id"] == 251 and attrs["BLDG_ABBR"] == "BRNG"
    assert attrs["BUILDING_N"].startswith("Steven C. Beering Hall")
    assert entry["collection"] == model["collection"] == exported["collection"] == "Asset_beering_hall"
    assert model["object_count"] == entry["object_count"] == exported["object_count"]

    ring = feature["geometry"]["coordinates"][0]
    origin = entry["placement_origin_xy_m"]
    def project_local(point):
        return ((point[0] + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)) - origin[0],
                (point[1] - 40.4274) * 111040.0 - origin[1])
    gis = [project_local(p) for p in ring]
    gis_bounds = bounds(gis)
    walls = [model["structural_objects"][n]["bottom_vertices_xy"] for n in
             ("BRNG_Classroom_Wing_Masonry", "BRNG_Office_Tower_Masonry")]
    shell_points = [tuple(p) for poly in walls for p in poly]
    shell_bounds = bounds(shell_points)
    gis_size = [b[1]-b[0] for b in gis_bounds]
    shell_size = [b[1]-b[0] for b in shell_bounds]
    size_delta = [abs(a-b) for a,b in zip(gis_size,shell_size)]
    bbox_center_error = math.dist([(b[0]+b[1])/2 for b in gis_bounds],
                                  [(b[0]+b[1])/2 for b in shell_bounds])
    height = model["evaluated_bounds_local_m"][2][1] - model["evaluated_bounds_local_m"][2][0]
    gis_roof_ft = attrs.get("R")
    conditional_roof_m = gis_roof_ft * 0.3048 if isinstance(gis_roof_ft,(int,float)) else None

    criteria = [
      {"criterion":"Correct identity and source-backed footprint","score":1.4,"max_score":2,
       "evidence":[f"Official Purdue GIS feature {feature['id']} matches BRNG, full building name and address {attrs['ADDRESS']}.",
                   f"The 51-coordinate GIS ring converts to {gis_size[0]:.2f} x {gis_size[1]:.2f} m in project axes; the two primary wall meshes span {shell_size[0]:.2f} x {shell_size[1]:.2f} m.",
                   f"Bounding-size deltas are {size_delta[0]:.2f} m and {size_delta[1]:.2f} m; their centers differ by {bbox_center_error:.2f} m.",
                   "The source GIS footprint includes a detailed curved southern frontage; the model uses large rectilinear wall masses plus a separate rotunda drum, so envelope match does not prove full perimeter agreement."],
       "findings":["Identity and overall envelope are strongly supported; detailed boundary registration has not been demonstrated against all GIS vertices."]},
      {"criterion":"Position, orientation, and scale/dimensions","score":1.6,"max_score":2,
       "evidence":[f"Manifest local-placement origin is {origin} m; Blender scene bounds are local and the library scene is {model['scene']}.",
                   f"The main structural envelope's bbox-center offset from GIS is {bbox_center_error:.2f} m; the bbox dimensions differ by at most {max(size_delta):.2f} m.",
                   "Primary wing meshes follow the GIS's cardinal N/S and E/W orientation."],
       "findings":["No exact wall-by-wall perimeter or master placement-marker reopen was supplied, so this score is based on local asset geometry and manifest origin."]},
      {"criterion":"Evidence-backed height, floors, and roof form","score":1.1,"max_score":2,
       "evidence":[f"Purdue GIS reports NUM_LEVELS={attrs['NUM_LEVELS']} and floor-level fields F02–F07; model evaluated height is {height:.2f} m.",
                   f"GIS R={gis_roof_ft} and Extrution={attrs['Extrution']} have no documented unit/measurement definition in the retrieved service metadata. If R is feet it implies {conditional_roof_m:.2f} m, close to the model, but this is a conditional inference rather than verified height.",
                   "The Purdue College of Education exterior photo shows a white circular rooftop room/rotunda; the model uses a green copper-tier dome and places a tall drum on a separate lower-volume wing."],
       "findings":["Nine-level count and roof datum are not independently resolved; the model's rotunda height, location and green dome finish conflict with the official photo."]},
      {"criterion":"Facade, entrances, and distinctive architecture","score":1.2,"max_score":2,
       "evidence":["The model uses dark red brick, limestone base/details, repeated windows and a circular rooftop feature; Purdue's photo confirms brick, variable window bays and a white circular upper room.",
                   "The current model view shows highly uniform small windows and continuous white floor bands; Purdue's photo shows varied larger vertical glazing and a white ring with vertical openings.",
                   "The model includes a west entrance door and limestone pediment, but the reviewed exterior view/source image do not verify the entrance dimensions or side."],
       "findings":["Some architectural cues are present, but the signature rooftop form/material and facade rhythm are only partially supported; entrance evidence is thin."]},
      {"criterion":"Modular export, portability, and complete evidence","score":1.45,"max_score":2,
       "evidence":[f"Actual asset reopened in Blender {model['blender_version']}; {model['object_count']} collection objects, expected scene/collection and manifest object count match.",
                   f"Collection-only export reopened with {exported['object_count']} objects; it contains no cameras/lights, unpacked image paths, or linked libraries.",
                   "The model uses procedural materials and has no external image dependencies.",
                   "This legacy building has no dedicated build script or building-specific source/evidence folder; this review had to assemble the source record and direct provenance itself."],
       "findings":["The library contract and portability pass; reproducible builder logic and original source provenance are absent from the repository."]},
    ]
    score=round(sum(c["score"] for c in criteria),2)
    result={"building_id":"beering_hall","score":score,"max_score":10,"pass_threshold":8,
            "passed":score>=8,"criteria":criteria,
            "evidence":{"gis_feature_id":feature["id"],"gis_attributes":{k:attrs[k] for k in
              ["BLDG_ABBR","BUILDING_N","ADDRESS","NUM_LEVELS","CountOfFLO","Extrution","R"]},
              "gis_local_bounds_m":gis_bounds,"wall_shell_local_bounds_m":shell_bounds,
              "bbox_size_delta_m":size_delta,"bbox_center_error_m":bbox_center_error,
              "model_evaluated_bounds_local_m":model["evaluated_bounds_local_m"],
              "asset_sha256":model["sha256"],"asset_path":"modular/buildings/beering_hall.blend",
              "preview_path":"audit/texture_batch_1/beering_hall.png",
              "official_photo_path":"audit/beering_hall_independent_grade/source_beering_education_purdue.jpeg",
              "source_record_path":"audit/beering_hall_independent_grade/source_record.json",
              "blender_probe_path":"audit/beering_hall_independent_grade/blender_probe.json",
              "export_probe_path":"audit/beering_hall_independent_grade/export_probe_result.json"},
            "findings":["Overall identity and horizontal envelope are credible, but the source perimeter's curved southern edge is represented by an approximate combination of rectangular walls and a detached circular drum.",
                        "Height inferred from GIS R=95.1 is conditional because the GIS field units are undocumented; story count is not reconciled with the nine-level attribute.",
                        "The official Purdue photo places a white ring-like rotunda atop the principal brick tower. The model instead has a green tiered dome and a tall drum on its lower southern wing.",
                        "The model's main facade is more repetitive than the source photo, and no building-specific builder/source-evidence package exists.",
                        "Blender emitted a compatibility warning because the file was saved with a newer Blender build (5.02.45) and reopened in 4.5.15; checks succeeded, but the newer file should be preserved to avoid loss on save."]}
    (GRADE/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result

if __name__ == "__main__":
    print(json.dumps(evaluate(),indent=2,ensure_ascii=False))
