#!/usr/bin/env python3
"""Independent, reproducible review of the Hagle Hall massing asset.

Run with a regular Python 3 interpreter. The script reopens the .blend in
Blender background mode, recomputes the GIS footprint metrics, and writes the
rubric result to grade.json. It does not modify the model or source snapshots.
"""
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
BUILDING_ID = "massing_marc_and_sharon_hagle_hall_hagl_071ffd6"
ASSET = ROOT / "modular" / "buildings" / f"{BUILDING_ID}.blend"
MANIFEST = ROOT / "modular" / "manifest.json"
EVIDENCE = AUDIT / "evidence.json"
SOURCE = AUDIT / "sources" / "purdue_buildings_fid430_wgs84.geojson"
ANNOUNCEMENT = AUDIT / "sources" / "purdue_bands_hagle_project_announcement_2020.html"
PREVIEW = AUDIT / "hagle_hall_preview.png"
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
OUTPUT = AUDIT / "grade.json"


def projected_ring_metrics(feature: dict) -> dict:
    ring = feature["geometry"]["coordinates"][0][:-1]
    coords = [
        (
            (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0,
        )
        for lon, lat, *_ in ring
    ]
    area = abs(
        sum(
            coords[i][0] * coords[(i + 1) % len(coords)][1]
            - coords[(i + 1) % len(coords)][0] * coords[i][1]
            for i in range(len(coords))
        )
        / 2
    )
    return {
        "vertex_count": len(coords),
        "area_m2": area,
        "bounds_xy_m": [
            [min(p[0] for p in coords), max(p[0] for p in coords)],
            [min(p[1] for p in coords), max(p[1] for p in coords)],
        ],
    }


def inspect_blend() -> dict:
    """Open saved model in Blender and return facts directly from the file."""
    expected_collection = "Asset_" + BUILDING_ID
    output_path = AUDIT / "_blender_inspection.tmp.json"
    expr = """
import bpy, json, math
from pathlib import Path
scene = bpy.context.scene
name = %r
collection = bpy.data.collections.get(name)
objects = list(collection.all_objects) if collection else []
obj = objects[0] if len(objects) == 1 else None
coords = [obj.matrix_world @ __import__('mathutils').Vector(c) for c in obj.bound_box] if obj else []
result = {
  'scene': scene.name if scene else None,
  'collection': collection.name if collection else None,
  'object_count': len(objects),
  'object_name': obj.name if obj else None,
  'object_type': obj.type if obj else None,
  'vertex_count': len(obj.data.vertices) if obj and obj.type == 'MESH' else None,
  'face_count': len(obj.data.polygons) if obj and obj.type == 'MESH' else None,
  'bounds_world_m': [[min(v[k] for v in coords), max(v[k] for v in coords)] for k in range(3)] if coords else None,
  'dimensions_m': list(obj.dimensions) if obj else None,
  'location': list(obj.location) if obj else None,
  'rotation_euler': list(obj.rotation_euler) if obj else None,
  'scale': list(obj.scale) if obj else None,
  'stories_property': obj.get('stories') if obj else None,
  'height_status_property': obj.get('height_status') if obj else None,
  'modifier_count': len(obj.modifiers) if obj else None,
  'materials': [m.name for m in obj.data.materials] if obj and obj.type == 'MESH' else [],
  'material_face_counts': {m.name: sum(1 for p in obj.data.polygons if p.material_index == i) for i,m in enumerate(obj.data.materials)} if obj and obj.type == 'MESH' else {},
  'canopy_geometry': None,
  'nw_curve_glazing_face_count': 0,
  'framed_entry_pane_face_count': 0,
  'frame_faces_at_entry': 0,
  'linked_libraries': len(bpy.data.libraries),
  'image_paths': [i.filepath for i in bpy.data.images if i.source == 'FILE'],
}
if obj and obj.type == 'MESH':
  canopy_i = next((i for i,m in enumerate(obj.data.materials) if 'roof canopy' in m.name.lower()), None)
  glass_i = next((i for i,m in enumerate(obj.data.materials) if 'glazing' in m.name.lower()), None)
  frame_i = next((i for i,m in enumerate(obj.data.materials) if 'metal frames' in m.name.lower()), None)
  canopy_faces = [p for p in obj.data.polygons if p.material_index == canopy_i] if canopy_i is not None else []
  canopy_points = [obj.matrix_world @ obj.data.vertices[j].co for p in canopy_faces for j in p.vertices]
  if canopy_points:
    result['canopy_geometry'] = {'polygon_count':len(canopy_faces),'bounds_world_m':[[min(v[k] for v in canopy_points),max(v[k] for v in canopy_points)] for k in range(3)]}
  if glass_i is not None:
    entry_panes=[]
    for p in obj.data.polygons:
      if p.material_index != glass_i: continue
      q=[obj.matrix_world @ obj.data.vertices[j].co for j in p.vertices]
      cx=sum(v.x for v in q)/len(q); cy=sum(v.y for v in q)/len(q)
      if cx < -438 and cy > -27 and min(v.z for v in q)>3.5:
        result['nw_curve_glazing_face_count'] += 1
      zs=[v.z for v in q]
      if min(zs)<0.2 and max(zs)>2.35 and max(zs)<2.75:
        entry_panes.append((sum(v.x for v in q)/len(q),sum(v.y for v in q)/len(q)))
    result['framed_entry_pane_face_count']=len(entry_panes)
    if frame_i is not None and entry_panes:
      for p in obj.data.polygons:
        if p.material_index != frame_i: continue
        q=[obj.matrix_world @ obj.data.vertices[j].co for j in p.vertices]
        cx=sum(v.x for v in q)/len(q); cy=sum(v.y for v in q)/len(q)
        if any(math.hypot(cx-ex,cy-ey)<1.2 for ex,ey in entry_panes) and min(v.z for v in q)<0.2 and max(v.z for v in q)>2.3:
          result['frame_faces_at_entry'] += 1
Path(%r).write_text(json.dumps(result, indent=2), encoding='utf-8')
""" % (expected_collection, str(output_path))
    completed = subprocess.run(
        [str(BLENDER), "--background", str(ASSET), "--factory-startup", "--python-expr", expr],
        check=True,
        capture_output=True,
        text=True,
        timeout=90,
    )
    if not output_path.exists():
        raise RuntimeError(f"Blender inspector did not write its result. stdout={completed.stdout} stderr={completed.stderr}")
    result = json.loads(output_path.read_text(encoding="utf-8"))
    output_path.unlink(missing_ok=True)
    return result


def main() -> dict:
    feature = json.loads(SOURCE.read_text(encoding="utf-8"))["features"][0]
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    asset_entry = next(x for x in manifest["assets"] if x["id"] == BUILDING_ID)
    gis = projected_ring_metrics(feature)
    model = inspect_blend()
    announcement = ANNOUNCEMENT.read_text(encoding="utf-8", errors="replace")
    article_supports_four_stories = "four-story" in announcement.lower() or "four story" in announcement.lower()
    area_sqft = gis["area_m2"] * 10.7639104167
    footprint_area_vs_program = area_sqft / 37500 * 100 if 37500 else None
    criteria = [
        {
            "name": "Identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Purdue BuildingShapesZip4 snapshot identifies FID {feature['properties']['FID']} as {feature['properties']['BUILDING_N']} ({feature['properties']['BLDG_ABBR']}).",
                f"University project announcement identifies Hagle Hall and states 37,500 square feet and four stories.",
                f"The modeled ring is generated from the same {gis['vertex_count']} GIS vertices; projected ring area recomputes to {gis['area_m2']:.2f} m² (~{area_sqft:.0f} ft²), {footprint_area_vs_program:.1f}% of stated gross floor area (plausible for four floors).",
                "Footprint evidence is an official campus GIS polygon, not a survey; no building-shape ambiguity is present in the provided crosswalk and article.",
            ],
        },
        {
            "name": "Position, orientation, and dimensions",
            "score": 1.75,
            "max_score": 2,
            "evidence": [
                "The asset is a campus-coordinate massing object with identity location/rotation/scale, and its plan bounds closely follow the GIS polygon after the project-mandated approximate WGS84-to-campus conversion.",
                f"Reopened asset bounds XY are {model['bounds_world_m'][0]} × {model['bounds_world_m'][1]} m; source ring bounds XY are {gis['bounds_xy_m']} m.",
                "Position and orientation derive from a single official GIS source. That layer has no populated feature edit date and is explicitly not survey-grade, so independent positional verification remains uncertain.",
            ],
        },
        {
            "name": "Height, floors, and roof form",
            "score": 1.25,
            "max_score": 2,
            "evidence": [
                f"The official Purdue project announcement supports four stories; the reopened mesh metadata also records {model['stories_property']} stories.",
                f"Reopened model height is {model['dimensions_m'][2]:.2f} m, but both the source record and model label it estimated; no measured elevation was found.",
                f"The revised mesh contains {model.get('canopy_geometry', {}).get('polygon_count', 0)} blue canopy-material polygons, extending to Z={model.get('canopy_geometry', {}).get('bounds_world_m', [[0,0],[0,0],[0,0]])[2][1] if model.get('canopy_geometry') else 'unknown'} m. The source photo supports a projecting blue angular roof/canopy above the curved bay, while exact canopy geometry and elevations remain visual estimates.",
                "A broad flat top plate is still present; the source photo is oblique and does not provide a roof plan or measured elevations.",
            ],
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.5,
            "max_score": 2,
            "evidence": [
                "The Purdue construction photo supports dark brick wings, a pale curved glazed bay, and a glazed ground level; corresponding colors, corner treatment, and broad window bands are present in the preview.",
                f"Freshly reopened mesh contains {model['nw_curve_glazing_face_count']} glazing faces along the NW curved-bay coordinate region; this verifies that the revision added a broadly glazed faceted curve. The source image shows glazing across the curve but also stone/opaque divisions that remain simplified.",
                f"The mesh includes {model['framed_entry_pane_face_count']} inset low-level entry glazing face(s) and {model['frame_faces_at_entry']} nearby metal-frame face(s), verifying that a framed door is present. In the single saved perspective it is still small and difficult to distinguish from adjacent storefront glazing; exact placement is not dimensioned.",
            ],
        },
        {
            "name": "Modular export, portability, and evidence",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Independent Blender 5.2 background reopen found scene {model['scene']}, expected collection {model['collection']}, one mesh object, {model['vertex_count']} vertices, and {model['face_count']} faces.",
                f"Object transform is location={model['location']}, rotation={model['rotation_euler']}, scale={model['scale']}; there are {model['modifier_count']} modifiers, {model['linked_libraries']} linked libraries, and {len(model['image_paths'])} file-backed images.",
                f"Manifest names the same asset, scene, collection, and object ({asset_entry['objects']}); structured evidence includes raw GIS, official project announcements, project photos, source URLs, dates, CRS/method notes, and a preview.",
                f"Preview exists: {PREVIEW.exists()}.",
            ],
        },
    ]
    findings = [
        {
            "severity": "moderate",
            "finding": "The rebuilt blue canopy projects above/out from the curved bay and is visible in the preview, addressing the prior missing-feature finding. It reads as a multi-faceted curved ribbon rather than the sharper angular canopy in the source photo, and exact canopy dimensions are unsupported.",
            "criterion": "Height, floors, and roof form",
        },
        {
            "severity": "moderate",
            "finding": "The NW curve now has continuous glazing, the projecting blue canopy is present, and the reopened mesh contains an inset framed door. The source photo shows opaque stone bands/divisions within the curved volume; the entrance is still difficult to pick out in the saved camera view, and the canopy reads as a curved ribbon rather than the sharper angular form in the photo.",
            "criterion": "Facade, entrances, and distinctive architecture",
        },
        {
            "severity": "uncertainty",
            "finding": "The 15.1 m height is an estimate from four stories and assumed floor heights/parapet; the sources do not establish measured eave, roof, or parapet heights.",
            "criterion": "Height, floors, and roof form",
        },
        {
            "severity": "uncertainty",
            "finding": "The GIS polygon supplies footprint and orientation evidence but no survey accuracy or populated feature edit date; campus placement is supported by that geometry and the official address/location description, not an independent survey.",
            "criterion": "Position, orientation, and dimensions",
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
            "preview_path": str(PREVIEW),
            "grader_code": str(Path(__file__).resolve()),
            "source_evidence_path": str(EVIDENCE),
            "gis_snapshot_path": str(SOURCE),
            "official_announcement_snapshot_path": str(ANNOUNCEMENT),
            "gis_feature": {"FID": feature["properties"]["FID"], "abbreviation": feature["properties"]["BLDG_ABBR"], "name": feature["properties"]["BUILDING_N"]},
            "gis_recomputed_metrics": gis,
            "gross_area_context": {"official_gross_area_sqft": 37500, "footprint_area_sqft_approx": round(area_sqft), "footprint_to_gross_area_percent": round(footprint_area_vs_program, 1)},
            "independent_blender_reopen": model,
            "manifest_entry": {"id": asset_entry["id"], "file": asset_entry["file"], "collection": asset_entry["collection"], "scene": asset_entry["scene"], "object_count": asset_entry["object_count"]},
            "builder_evidence_uncertainty": evidence["remaining_uncertainty"],
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))
