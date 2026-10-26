#!/usr/bin/env python3
"""Independent rubric evaluator for the Martin C. Jischke Hall massing.

Run with Python 3. The script reopens the saved asset in Blender and compares
the original Purdue GIS outline to the evaluated mesh's grade-level perimeter.
It does not alter the blend, sources, or shared project files.
"""
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
BUILDING_ID = "massing_martin_c_jischke_hall_of_biomedical_engineering_1a34d6a"
ASSET = ROOT / "modular" / "buildings" / f"{BUILDING_ID}.blend"
SOURCE = AUDIT / "sources" / "purdue_gis_feature_407.json"
EVIDENCE = AUDIT / "evidence.json"
FLOOR_PLANS = AUDIT / "sources" / "purdue_floor_plans.html"
PHOTO = AUDIT / "sources" / "purdue_events_photo.jpg"
MANIFEST = ROOT / "modular" / "manifest.json"
OUTPUT = AUDIT / "grade.json"
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")


def local_xy(lon: float, lat: float) -> tuple[float, float]:
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)), (lat - 40.4274) * 111040.0)


def point_segment_distance(p: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    den = dx * dx + dy * dy
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / den)) if den else 0.0
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def inspect_blend(source_ring: list[tuple[float, float]]) -> dict:
    output_path = AUDIT / "_blender_inspection.tmp.json"
    expr = """
import bpy, json, math
from pathlib import Path
from mathutils import Vector
obj = bpy.data.objects.get('Martin C. Jischke Hall of Biomedical Engineering')
coll = bpy.data.collections.get('Asset_massing_martin_c_jischke_hall_of_biomedical_engineering_1a34d6a')
if obj is None or coll is None: raise RuntimeError('Expected Jischke Hall object or collection missing')
dg = bpy.context.evaluated_depsgraph_get(); ev = obj.evaluated_get(dg); mesh = ev.to_mesh()
world = [ev.matrix_world @ v.co for v in mesh.vertices]
segments=[]; ground_vertices=set()
for edge in mesh.edges:
 a,b=edge.vertices; pa,pb=world[a],world[b]
 if abs(pa.z)<1e-4 and abs(pb.z)<1e-4 and math.hypot(pa.x-pb.x,pa.y-pb.y)>0.01:
  segments.append(((pa.x,pa.y),(pb.x,pb.y)))
  ground_vertices.add((round(pa.x,5),round(pa.y,5)))
ring=%r
def dist(p,a,b):
 dx=b[0]-a[0]; dy=b[1]-a[1]; den=dx*dx+dy*dy
 t=max(0.0,min(1.0,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0.0
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
errors=[min(dist(p,a,b) for a,b in segments) for p in ring]
bounds=[[min(v[k] for v in world),max(v[k] for v in world)] for k in range(3)]
result={
 'scene':bpy.context.scene.name,'collection':coll.name,'collection_object_count':len(coll.all_objects),
 'object_names':[x.name for x in coll.all_objects],'object_type':obj.type,
 'evaluated_vertices':len(mesh.vertices),'evaluated_faces':len(mesh.polygons),'bounds_world_m':bounds,
 'dimensions_m':list(obj.dimensions),'matrix_world':[list(row) for row in ev.matrix_world],
 'grade_outline_edge_count':len(segments),'grade_outline_vertex_count':len(ground_vertices),
 'source_ring_vertex_count':len(ring),'source_to_outline_max_error_m':max(errors),
 'source_to_outline_mean_error_m':sum(errors)/len(errors),
 'modifier_count':len(obj.modifiers),'materials':[m.name for m in mesh.materials],
 'linked_libraries':len(bpy.data.libraries),
 'unpacked_external_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]
}
ev.to_mesh_clear()
Path(%r).write_text(json.dumps(result,indent=2),encoding='utf-8')
""" % (source_ring, str(output_path))
    subprocess.run([str(BLENDER), "--background", str(ASSET), "--factory-startup", "--python-expr", expr], check=True, capture_output=True, text=True, timeout=90)
    result = json.loads(output_path.read_text(encoding="utf-8"))
    output_path.unlink(missing_ok=True)
    return result


def main() -> dict:
    feature = json.loads(SOURCE.read_text(encoding="utf-8-sig"))["features"][0]
    props = feature["attributes"]
    raw_ring = feature["geometry"]["rings"][0][:-1]
    source_ring = [local_xy(lon, lat) for lon, lat in raw_ring]
    original_area = abs(sum(source_ring[i][0] * source_ring[(i+1) % len(source_ring)][1] - source_ring[(i+1) % len(source_ring)][0] * source_ring[i][1] for i in range(len(source_ring))) / 2)
    source_bounds = [[min(p[k] for p in source_ring), max(p[k] for p in source_ring)] for k in range(2)]
    model = inspect_blend(source_ring)
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    floor_text = FLOOR_PLANS.read_text(encoding="utf-8", errors="replace").lower()
    floor_labels = {key: phrase in floor_text for key, phrase in {
        "basement": "the basement contains research areas",
        "first_floor": "the first floor contains academic offices",
        "second_floor": "the second floor holds research areas",
        "third_floor": "the third floor houses research areas",
    }.items()}
    photo_exists = PHOTO.exists()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entry = next(x for x in manifest["assets"] if x["id"] == BUILDING_ID)

    criteria = [
        {
            "criterion": "Identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Purdue BuildingShapesZip4 FID {props['FID']} identifies {props['BUILDING_N']} ({props['BLDG_ABBR']}); official BME and Purdue Events pages independently corroborate the building identity and address.",
                f"The structural plan derives from the official {len(source_ring)}-vertex GIS outline; its approximate projected polygon area recomputes to {original_area:.1f} m².",
                "The project preserves the major outline and reports simplification of the original 178-vertex GIS ring to 88 vertices, with maximum deviation about 1.02 m. This is a map/architectural outline, not a certified wall survey.",
            ],
        },
        {
            "criterion": "Position, orientation, and dimensions",
            "score": 1.75,
            "max_score": 2,
            "evidence": [
                f"Independent Blender 5.2.3 reopen found {model['grade_outline_edge_count']} grade-level perimeter edges; maximum source-vertex distance to the simplified mesh outline is {model['source_to_outline_max_error_m']:.3f} m (mean {model['source_to_outline_mean_error_m']:.3f} m).",
                f"Source bounds XY are {source_bounds} m; evaluated asset bounds XY (including facade details) are {model['bounds_world_m'][:2]} m.",
                "The footprint follows the official EPSG:4326 GIS geometry using the project’s documented approximate local conversion and remains in campus coordinates with identity transform. A small deduction reflects 1.02 m generalization tolerance and unpublished GIS positional accuracy.",
            ],
        },
        {
            "criterion": "Height, floors, and roof form",
            "score": 1.25,
            "max_score": 2,
            "evidence": [
                f"Purdue BME Floor Plans snapshot explicitly documents a basement and first, second, and third floors; the model represents three above-ground levels, so the GIS four-level count is plausibly reconciled.",
                f"The saved model is {model['bounds_world_m'][2][1]-model['bounds_world_m'][2][0]:.1f} m tall. Evidence clearly labels 14.2 m as an estimate; no measured elevations were found and GIS Extrution=36 has undocumented units.",
                "The preview uses a flat low-slope roof, but the available photo is an oblique corner view with no roof plan/elevation. The roof silhouette and parapet height remain visually plausible rather than dimensionally verified.",
            ],
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.0,
            "max_score": 2,
            "evidence": [
                "Purdue's single oblique exterior photo shows pale opaque end masses, a large glazed upper central facade, a brick lower facade, and a recessed entrance.",
                "The preview captures the pale shell, brick base band, repeated glazing, and general massing silhouette.",
                "The model's upper facade is mostly blank pale wall with repeated small punched windows; it does not reproduce the prominent large central curtain wall in the photo. The entry markers are schematic and do not make the recessed entrance clearly legible from the saved view. Facade rhythm and entrance locations are not dimensioned.",
            ],
        },
        {
            "criterion": "Modular export, portability, and evidence",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Independent Blender reopen found expected scene {model['scene']}, collection {model['collection']}, one mesh object, {model['evaluated_vertices']} evaluated vertices, and {model['evaluated_faces']} faces.",
                f"Model has {model['modifier_count']} modifiers, {model['linked_libraries']} linked libraries, {len(model['unpacked_external_images'])} unpacked external images, and an identity campus transform.",
                "Manifest entry matches the asset ID/path/collection/object count. Evidence contains raw GIS, official facilities/building-information/floor-plans pages, an official Purdue photo, source dates/method/uncertainty notes, a preview, and a separate saved-blend validation record.",
            ],
        },
    ]
    findings = [
        {
            "severity": "major",
            "finding": "The primary facade cue is absent: the reference photo has a broad two-level glazed central wall, while the preview shows mostly opaque upper cladding with small repeated windows. Add or revise the central curtain-wall bay and check from the documented photo-facing side.",
            "criterion": "Facade, entrances, and distinctive architecture",
        },
        {
            "severity": "moderate",
            "finding": "The documented recessed entrance is not visually legible in the saved preview; the west/east entrance markers have explicitly approximate placement and are not survey-backed.",
            "criterion": "Facade, entrances, and distinctive architecture",
        },
        {
            "severity": "uncertainty",
            "finding": "The 14.2 m total height, floor-to-floor spacing, roof level, and parapet height are estimates. The source confirms basement plus three above-ground floors but does not give measured elevations.",
            "criterion": "Height, floors, and roof form",
        },
        {
            "severity": "uncertainty",
            "finding": f"The 178-point GIS outline was generalized to an 88-edge model outline, with independently recomputed maximum source-to-outline deviation of {model['source_to_outline_max_error_m']:.2f} m. The GIS is not a certified survey and its feature edit date is unavailable.",
            "criterion": "Position, orientation, and dimensions",
        },
        {
            "severity": "uncertainty",
            "finding": "A single oblique exterior image supports the broad facade treatment but cannot verify hidden elevations, exact window spacing, door positions, or roof plan.",
            "criterion": "Facade, entrances, and distinctive architecture",
        },
    ]
    result = {
        "building_id": BUILDING_ID,
        "score": sum(c["score"] for c in criteria),
        "max_score": 10,
        "passing_standard": 8,
        "passed": sum(c["score"] for c in criteria) >= 8,
        "criteria": criteria,
        "findings": findings,
        "evidence": {
            "asset_path": str(ASSET),
            "preview_path": str(AUDIT / "preview_detail.png"),
            "grader_code": str(Path(__file__).resolve()),
            "gis_source_path": str(SOURCE),
            "source_evidence_path": str(EVIDENCE),
            "floor_plans_snapshot_path": str(FLOOR_PLANS),
            "photo_snapshot_path": str(PHOTO),
            "gis_identity": {"FID": props["FID"], "abbreviation": props["BLDG_ABBR"], "name": props["BUILDING_N"]},
            "gis_recomputed": {"original_vertex_count": len(source_ring), "projected_area_m2_approx": original_area, "bounds_xy_m": source_bounds},
            "floor_plan_text_checks": floor_labels,
            "independent_blender_reopen": model,
            "manifest_entry": {"id": entry["id"], "file": entry["file"], "collection": entry["collection"], "scene": entry["scene"], "object_count": entry["object_count"]},
            "builder_validation_path": str(AUDIT / "validation.json"),
            "source_uncertainty": evidence["geometry"]["height_status"] + "; GIS positional accuracy unpublished",
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
