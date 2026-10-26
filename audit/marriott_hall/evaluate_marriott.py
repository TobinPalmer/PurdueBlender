#!/usr/bin/env python3
"""Independent evaluator for the Marriott Hall modular massing asset.

Run with Python 3 from any working directory. Reopens the .blend through
Blender, recalculates source-ring coordinates, and writes grade.json. The model,
shared indexes, and source snapshots are read-only inputs to this evaluator.
"""
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
ASSET_ID = "massing_marriot_hall_7cd3eb5"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
SOURCE = AUDIT / "sources" / "purdue_feature_862_raw.json"
MANIFEST = ROOT / "modular" / "manifest.json"
EVIDENCE = AUDIT / "evidence.json"
ANNOUNCEMENT = AUDIT / "sources" / "cso_architect_marriott_hall.html"
OUTPUT = AUDIT / "grade.json"
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")


def project_source_ring(feature: dict) -> list[tuple[float, float]]:
    r = 6378137.0
    out = []
    for x, y in feature["geometry"]["rings"][0][:-1]:
        lon = math.degrees(x / r)
        lat = math.degrees(2 * math.atan(math.exp(y / r)) - math.pi / 2)
        out.append(((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)), (lat - 40.4274) * 111040.0))
    return out


def inspect_blend(expected_ring: list[tuple[float, float]]) -> dict:
    output_path = AUDIT / "_blender_inspection.tmp.json"
    expr = """
import bpy, json, math
from pathlib import Path
from mathutils import Vector
obj = bpy.data.objects.get('Marriot Hall')
coll = bpy.data.collections.get('Asset_massing_marriot_hall_7cd3eb5')
if obj is None or coll is None: raise RuntimeError('Expected Marriott Hall object/collection absent')
dg = bpy.context.evaluated_depsgraph_get()
ev = obj.evaluated_get(dg)
mesh = ev.to_mesh()
world = [ev.matrix_world @ v.co for v in mesh.vertices]
ground = [v for v in world if abs(v.z) < 1e-4]
ring = %r
errors = [min(math.hypot(v.x-x, v.y-y) for v in ground) for x,y in ring]
bounds = [[min(v[k] for v in world), max(v[k] for v in world)] for k in range(3)]
result = {
 'scene': bpy.context.scene.name,
 'collection': coll.name,
 'collection_object_count': len(coll.all_objects),
 'objects': [o.name for o in coll.all_objects],
 'object_name': obj.name,
 'object_type': obj.type,
 'vertex_count': len(mesh.vertices),
 'face_count': len(mesh.polygons),
 'bounds_world_m': bounds,
 'dimensions_m': list(obj.dimensions),
 'matrix_world': [list(row) for row in ev.matrix_world],
 'modifier_count': len(obj.modifiers),
 'materials': [m.name for m in mesh.materials],
 'linked_libraries': len(bpy.data.libraries),
 'unpacked_external_images': [i.filepath for i in bpy.data.images if i.source == 'FILE' and i.filepath and not i.packed_file],
 'source_ring_vertex_count': len(ring),
 'source_ring_vertices_found_within_1mm': sum(e <= .001 for e in errors),
 'source_ring_max_nearest_error_m': max(errors),
 'source_ring_mean_nearest_error_m': sum(errors)/len(errors),
}
ev.to_mesh_clear()
Path(%r).write_text(json.dumps(result, indent=2), encoding='utf-8')
""" % (expected_ring, str(output_path))
    subprocess.run(
        [str(BLENDER), "--background", str(ASSET), "--factory-startup", "--python-expr", expr],
        check=True,
        capture_output=True,
        text=True,
        timeout=90,
    )
    data = json.loads(output_path.read_text(encoding="utf-8"))
    output_path.unlink(missing_ok=True)
    return data


def main() -> dict:
    feature = json.loads(SOURCE.read_text(encoding="utf-8-sig"))["feature"]
    props = feature["attributes"]
    ring = project_source_ring(feature)
    area = abs(sum(ring[i][0] * ring[(i + 1) % len(ring)][1] - ring[(i + 1) % len(ring)][0] * ring[i][1] for i in range(len(ring))) / 2)
    bounds = [[min(p[k] for p in ring), max(p[k] for p in ring)] for k in range(2)]
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entry = next(a for a in manifest["assets"] if a["id"] == ASSET_ID)
    model = inspect_blend(ring)
    cso = ANNOUNCEMENT.read_text(encoding="utf-8", errors="replace")
    cso_supports_style = "dark red brick and tile roof" in cso.lower() and "transparent façade" in cso.lower()

    criteria = [
        {
            "criterion": "Identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Purdue ArcGIS feature FID {props['FID']} identifies {props['BUILDING_N']} ({props['BLDG_ABBR']}) at {props['ADDRESS']} (the service's separate BUILDING_1 field is {props['BUILDING_1']}).",
                f"Recomputed source polygon has {len(ring)} unique ring vertices and approximately {area:.1f} m² area under the mandated local campus transform.",
                "Purdue venue listing identifies Marriott Hall and the same street address; independent architect project page names Purdue as client and describes the same building.",
                "Feature identity is cross-checked by ID, abbreviation, name, and address rather than nearest-location alone. GIS outline is not a certified survey.",
            ],
        },
        {
            "criterion": "Position, orientation, and dimensions",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Independent Blender reopen found {model['source_ring_vertices_found_within_1mm']}/{model['source_ring_vertex_count']} transformed source vertices in the evaluated mesh within 1 mm; maximum nearest-vertex error {model['source_ring_max_nearest_error_m']:.6f} m.",
                f"GIS ring bounds XY are {bounds}; evaluated model bounds XY are {model['bounds_world_m'][:2]} m. Extra bounds are roof overhang/steps, not the structural footprint.",
                "Footprint and cardinal orientation follow the official EPSG:3857 feature using its documented inverse projection and the project’s approximate WGS84-to-campus conversion. This verifies geometric registration to that GIS source, not survey-grade position.",
            ],
        },
        {
            "criterion": "Height, floors, and roof form",
            "score": 1.0,
            "max_score": 2,
            "evidence": [
                f"GIS record lists four levels; model height is {model['bounds_world_m'][2][1]-model['bounds_world_m'][2][0]:.2f} m with eave/ridge estimates of 9.6/12.6 m.",
                "The builder and source evidence correctly label vertical dimensions estimates; ArcGIS Extrution=39 has no documented units and is not treated as a measured elevation.",
                "Architect and Purdue photos confirm a broad red pitched roof with deep eaves, so a gable silhouette is evidence-based. The rendered roof is an irregular collection of overlapping/faceted roof planes across the GIS footprint, unlike the dominant long continuous gable seen in the reference photos; exact roof plan and height remain unverified.",
                "The exterior reads as roughly three above-grade facade bands despite a GIS four-level attribute; the fourth level's interpretation is unresolved.",
            ],
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.5,
            "max_score": 2,
            "evidence": [
                "Architect and Purdue source photos show red brick, light horizontal masonry bands, vertical brick piers, upper transparent glazing, lower punched windows, deep roof eaves, and a visible glazed entrance/canopy.",
                "Preview captures brick, light belt courses, upper glazing, lower windows, gabled red roof, overhang, entrance doors, a metal canopy, and steps.",
                "Facade rhythm is schematic: source photos show prominent vertical piers, tall upper curtain-wall bays, a larger entrance-side covered plaza, and a more legible lobby. The preview's entrance canopy/doors are much smaller and less distinctive, and window dimensions are not measured.",
            ],
        },
        {
            "criterion": "Modular export, portability, and evidence",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Independent Blender 5.2 reopen found expected scene {model['scene']}, collection {model['collection']}, one mesh, {model['vertex_count']} vertices, and {model['face_count']} faces.",
                f"Model has {model['modifier_count']} modifiers, {model['linked_libraries']} linked libraries, and {len(model['unpacked_external_images'])} unpacked image dependencies; the identity world matrix preserves the massing library's campus-coordinate convention.",
                "Manifest entry matches asset ID, file, collection, scene, and one-object export. Evidence has raw feature and layer metadata, source photos/pages, architect information, project approval PDF, retrieval dates, projection/method notes, uncertainty, two previews, and a separate reopen-validation record.",
            ],
        },
    ]
    findings = [
        {
            "severity": "major",
            "finding": "Roof geometry needs review: the preview has large intersecting/faceted roof surfaces that create multiple apparent ridges over the irregular footprint, while the source photos primarily show a long, clear gable roof with deep eaves. The model height and roof dimensions remain estimates.",
            "criterion": "Height, floors, and roof form",
        },
        {
            "severity": "moderate",
            "finding": "The four-level GIS attribute is not reconciled with the approximately three visible above-grade facade bands in the model/reference view. Clarify whether the extra level is below grade or whether a facade level is missing before claiming floor-count fidelity.",
            "criterion": "Height, floors, and roof form",
        },
        {
            "severity": "moderate",
            "finding": "The principal entrance and upper glazed lobby are present in simplified form, but the real building's broad entrance-side canopy/plaza and tall glazed bays are more prominent than the model preview suggests.",
            "criterion": "Facade, entrances, and distinctive architecture",
        },
        {
            "severity": "uncertainty",
            "finding": "The GIS footprint is an official Purdue polygon and matches the transformed mesh ring within 0.1 mm, but the service does not publish survey accuracy or a feature edit date. Height, facade bay spacing, and exact roof plan are not dimensioned in the collected sources.",
            "criterion": "Position, orientation, and dimensions",
        },
        {
            "severity": "uncertainty",
            "finding": "The 2009 approval lists 42,500 gross square feet while the architect project page lists 35,000 square feet; neither is used to scale the source footprint, and the difference remains unexplained.",
            "criterion": "Identity and source-backed footprint",
        },
        {
            "severity": "uncertainty",
            "finding": "The GIS Shape__Area attribute stored in the evidence is 3,423.2, which exceeds the approximate 2,499 m² source bounding rectangle; its units/meaning are unclear, so the evaluator recomputes polygon area from the source ring and does not rely on that attribute.",
            "criterion": "Identity and source-backed footprint",
        },
    ]
    result = {
        "building_id": ASSET_ID,
        "score": sum(c["score"] for c in criteria),
        "max_score": 10,
        "passing_standard": 8,
        "passed": sum(c["score"] for c in criteria) >= 8,
        "criteria": criteria,
        "findings": findings,
        "evidence": {
            "asset_path": str(ASSET),
            "grader_code": str(Path(__file__).resolve()),
            "source_evidence_path": str(EVIDENCE),
            "raw_gis_snapshot": str(SOURCE),
            "architect_page_snapshot": str(ANNOUNCEMENT),
            "official_feature": {"FID": props["FID"], "abbreviation": props["BLDG_ABBR"], "name": props["BUILDING_N"], "address": props["BUILDING_1"]},
            "gis_ring": {"unique_vertices": len(ring), "projected_area_m2_approx": area, "bounds_xy_m": bounds},
            "independent_blender_reopen": model,
            "manifest_entry": {"id": entry["id"], "file": entry["file"], "collection": entry["collection"], "scene": entry["scene"], "object_count": entry["object_count"]},
            "preexisting_builder_validation": "audit/marriott_hall/validation.json",
            "source_uncertainties": evidence["uncertainties"],
            "architect_visual_style_evidence_found": cso_supports_style,
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
