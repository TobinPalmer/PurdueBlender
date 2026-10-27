from pathlib import Path
import json, math

root = Path(__file__).resolve().parents[3]
audit = root / "audit" / "veterinary_medicine_isolation_facility"
probe = json.loads((audit / "independent_grade" / "fresh_open_probe.json").read_text(encoding="utf-8"))
evidence = json.loads((audit / "evidence.json").read_text(encoding="utf-8"))
feature = json.loads((audit / "purdue_gis_VMIF_feature.json").read_text(encoding="utf-8"))
assert probe["fresh_open"]
assert probe["scene"] == evidence["scene"]
assert probe["collection"] == evidence["collection"]
assert probe["sha256"] == evidence["blend_sha256"]
assert probe["gis_footprint_max_vertex_xy_error_m"] < 0.00001
assert probe["anchor_error_m"] < 0.001

ring = feature["geometry"]["rings"][0][:-1]
lat0, lon0 = 40.4274, -86.9137
mxlon = 111412.84 * math.cos(math.radians(lat0))
mlat = 111040.0
points = [((lon-lon0)*mxlon, (lat-lat0)*mlat) for lon, lat in ring]
twice_area = sum(points[i][0]*points[(i+1)%len(points)][1] - points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))
coordinate_area = abs(twice_area) / 2
reported_area = float(feature["attributes"]["Shape__Area"])
area_delta = reported_area - coordinate_area
area_pct = 100.0 * area_delta / coordinate_area

criteria = [
    {
        "criterion": "Correct identity and source-backed footprint",
        "score": 2.0,
        "max_score": 2.0,
        "evidence": [
            "Purdue BuildingShapesZip4 FID 78 identifies Veterinary Medicine Isolation Facility (VMIF), at 402 S University Street.",
            f"The 12 perimeter vertices of the modeled wall shell match the projected source polygon; maximum XY error is {probe['gis_footprint_max_vertex_xy_error_m']:.9f} m.",
            "The Purdue Archives source separately supports VMIF identity and the eight-stall animal-care program."
        ],
        "limits": [
            f"GIS Shape__Area reports {reported_area:.3f} m² while the captured ring coordinates produce {coordinate_area:.3f} m² under the documented local projection ({area_delta:.3f} m² / {area_pct:.1f}% difference). The model follows the polygon ring and does not reconcile this provider conflict."
        ]
    },
    {
        "criterion": "Position, orientation, and scale/dimensions",
        "score": 1.75,
        "max_score": 2.0,
        "evidence": [
            f"The saved scene anchor matches the source polygon centroid within {probe['anchor_error_m']:.9f} m.",
            "The wall outline preserves the official GIS ring shape and rotation without rescaling."
        ],
        "limits": [
            "The master placement marker and nearby campus context were not part of this isolated-asset review.",
            "Plinth and fascia extend beyond the source wall perimeter, so the overall mesh bounds are slightly larger than the GIS envelope."
        ]
    },
    {
        "criterion": "Evidence-backed height, floors, and roof form",
        "score": 1.25,
        "max_score": 2.0,
        "evidence": [
            "Purdue GIS reports one level, matching the single-storey shell.",
            f"Fresh-open local geometry reaches {probe['local_bounds_m'][2][1]:.2f} m above its origin."
        ],
        "limits": [
            "The 3.66 m eave height interprets GIS Extrution=12 as feet although field units are undocumented.",
            "No captured source verifies the flat/low-slope roof form, roof elevation, parapet profile, or HVAC arrangement."
        ]
    },
    {
        "criterion": "Facade, entrances, and distinctive architecture",
        "score": 0.75,
        "max_score": 2.0,
        "evidence": [
            "The outline is distinctive and follows the cross-shaped GIS perimeter; the interior cutaway includes a schematic corridor, eight stalls and support/mechanical rooms consistent with the Archives program description."
        ],
        "limits": [
            "The exterior has no modeled windows or entrance doors; the builder explicitly left openings out because target-specific facade evidence was not found.",
            "Wall, roof and trim materials are visual assumptions. The model reads as a generic blank service building in its exterior preview."
        ]
    },
    {
        "criterion": "Modular export, portability, and complete evidence",
        "score": 2.0,
        "max_score": 2.0,
        "evidence": [
            f"Blender {probe['blender_version']} reopened the saved source scene and expected exported collection successfully.",
            f"The collection contains {probe['collection_object_count']} local mesh objects with {probe['vertex_count']} vertices and {probe['polygon_count']} faces.",
            "Every mesh has a material assigned; there are no external image dependencies or linked libraries.",
            "Structured provenance, builder notes, two preview renders and a fresh-open probe are present."
        ],
        "limits": []
    }
]
score = round(sum(c["score"] for c in criteria), 2)
result = {
    "building": "Veterinary Medicine Isolation Facility (VMIF)",
    "asset": probe["sha256"],
    "score": score,
    "max_score": 10,
    "passing_threshold": 8,
    "pass": score >= 8,
    "criteria": criteria,
    "evidence": {
        "fresh_open_probe": "fresh_open_probe.json",
        "fresh_open_probe_script": "fresh_open_probe.py",
        "evaluator": "evaluator.py",
        "source_evidence": "../evidence.json",
        "GIS_feature_snapshot": "../purdue_gis_VMIF_feature.json",
        "exterior_preview": "../vmif_preview.png",
        "cutaway_preview": "../vmif_cutaway.png",
        "GIS_coordinate_area_m2": round(coordinate_area, 3),
        "GIS_reported_shape_area_m2": reported_area,
        "GIS_area_difference_percent": round(area_pct, 1)
    },
    "findings": [
        {
            "severity": "major source conflict",
            "finding": f"The GIS Shape__Area value ({reported_area:.3f} m²) conflicts with the area derived from the returned polygon coordinates ({coordinate_area:.3f} m²). The model exactly follows the vertices, but the source discrepancy remains unresolved."
        },
        {
            "severity": "major visual incompleteness",
            "finding": "The exterior shell has no doors or windows and no target-specific facade evidence; the current exterior therefore appears as a generic blank volume. Obtain reliable target-specific facade imagery or plans before adding these details."
        },
        {
            "severity": "uncertainty",
            "finding": "The roof form and height are estimates. The 12-unit extrusion is interpreted as feet without documented units. The interior program is evidence-informed, while its spatial layout is illustrative."
        },
        {
            "severity": "integration not reviewed",
            "finding": "This grade covers the standalone asset only; the master placement and overlap with neighboring models were not inspected."
        }
    ]
}
out = audit / "independent_grade" / "result.json"
out.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"score": score, "pass": result["pass"], "area_from_coordinates_m2": round(coordinate_area, 3), "reported_area_m2": reported_area, "result": str(out)}, indent=2))
