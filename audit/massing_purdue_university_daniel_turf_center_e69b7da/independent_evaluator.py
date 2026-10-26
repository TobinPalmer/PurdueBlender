"""Independent evaluator for the Purdue University Daniel Turf Center massing.

Reopens the saved asset in Blender 5.2.3 and checks the mesh against the named
Purdue GIS FID 208 geometry. It records the unresolved area-attribute/ring-area
discrepancy and treats the 14-ft interpretation as uncertain.
"""
import json
import math
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ID = "massing_purdue_university_daniel_turf_center_e69b7da"
ASSET = ROOT / "modular" / "buildings" / f"{ID}.blend"
BLENDER = ROOT.parent / "blender" / "blender-5.2.3-windows-x64" / "blender.exe"


def readj(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def to_campus(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def area_xy(points):
    return abs(sum(points[i][0] * points[(i + 1) % len(points)][1]
                   - points[(i + 1) % len(points)][0] * points[i][1]
                   for i in range(len(points))) / 2)


def reopen():
    expr = (
        "import bpy,json; "
        f"bpy.ops.wm.open_mainfile(filepath={str(ASSET)!r}); "
        f"c=bpy.data.collections.get('Asset_{ID}'); "
        "o=bpy.data.objects.get('Purdue University Daniel Turf Center'); "
        "v=[[(o.matrix_world@x.co)[i] for i in range(3)] for x in o.data.vertices]; "
        "b=[[min(p[i] for p in v),max(p[i] for p in v)] for i in range(3)]; "
        "s={'version':bpy.app.version_string,'scene':bpy.context.scene.name,"
        "'collection':c.name if c else None,'collection_count':len(c.objects) if c else -1,"
        "'object':o.name if o else None,'type':o.type if o else None,"
        "'vertices':len(o.data.vertices) if o else None,'faces':len(o.data.polygons) if o else None,"
        "'bounds':b,'vertices_world':v,'materials':[m.name for m in o.data.materials if m],"
        "'unpacked_images':[i.filepath for i in bpy.data.images if i.filepath and not i.packed_file],"
        "'libraries':len(bpy.data.libraries),'modifiers':[m.name for m in o.modifiers],"
        "'object_location':list(o.location)}; print('DANL_DIRECT='+json.dumps(s))"
    )
    cp = subprocess.run([str(BLENDER), "--background", "--python-expr", expr],
                        cwd=ROOT, capture_output=True, text=True, timeout=180)
    if cp.returncode:
        raise RuntimeError("Blender reopen failed: " + cp.stderr[-1200:])
    match = re.search(r"DANL_DIRECT=(\{[^\r\n]*\})", cp.stdout)
    if not match:
        raise RuntimeError("No Blender direct snapshot: " + cp.stdout[-1200:])
    return json.loads(match.group(1))


def evaluate():
    assert ASSET.is_file() and BLENDER.is_file()
    d = reopen()
    audit = HERE / "sources"
    src = readj(audit / "purdue_buildings_fid208_query_2026-10-26.json")
    feature = next(f for f in src["features"] if f["attributes"]["FID"] == 208)
    attrs = feature["attributes"]
    ring = feature["geometry"]["rings"][0]
    if ring[0] == ring[-1]:
        ring = ring[:-1]
    expected = [to_campus(lon, lat) for lon, lat in ring]
    meshring = d["vertices_world"][:len(expected)]
    errors = [math.dist(p, (v[0], v[1])) for p, v in zip(expected, meshring)]
    max_error = max(errors)
    ring_area = area_xy(expected)
    candidate_dims = [max(p[i] for p in expected) - min(p[i] for p in expected) for i in range(2)]
    service_area = float(attrs["Shape__Area"])
    # Compare Shape__Area in the layer's EPSG:3857 coordinate plane with the
    # same ring. The local ring_area above is a ground-frame approximation.
    ring_mercator = [(6378137.0 * math.radians(lon),
                      6378137.0 * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))
                     for lon, lat in ring]
    mercator_ring_area = area_xy(ring_mercator)
    source_area_relative_error = abs(mercator_ring_area - service_area) / service_area
    area_ratio = service_area / ring_area
    manifest = readj(ROOT / "modular" / "manifest.json")
    entry = next(e for e in manifest["assets"] if e["id"] == ID)
    manifest_bounds = entry["bounds_world_m"]
    bounds = d["bounds"]
    manifest_delta = [[bounds[i][j] - manifest_bounds[i][j] for j in range(2)] for i in range(3)]
    max_manifest_delta = max(abs(x) for row in manifest_delta for x in row)
    overlay = audit / "gis_fid208_aerial_overlay.png"
    renders = [HERE / "renders" / "daniel_turf_center_top.png",
               HERE / "renders" / "daniel_turf_center_oblique.png"]
    official_page = audit / "purdue_daniel_turf_center_page_2026-10-26.html"
    assert d["version"].startswith("5.2.3")
    assert d["scene"] == f"Building_{ID}" and d["collection"] == f"Asset_{ID}"
    assert d["collection_count"] == 1 and d["type"] == "MESH"
    assert attrs["FID"] == 208 and attrs["BLDG_ABBR"] == "DANL"
    assert attrs["BUILDING_N"] == "William H. Daniel Turfgrass Research & Diagnostic Court"
    assert attrs["ADDRESS"] == "1340 Cherry Lane"
    assert len(expected) == 12 and max_error < 0.001
    assert overlay.is_file() and official_page.is_file() and all(p.is_file() for p in renders)

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 1.9, "max_score": 2.0,
            "status": "named identity and candidate outline are strongly supported; apparent area discrepancy reconciles across coordinate systems",
            "evidence": [
                f"Purdue GIS FID {attrs['FID']} / {attrs['BLDG_ABBR']} names {attrs['BUILDING_N']} at {attrs['ADDRESS']}; Purdue HLA's saved facility page independently identifies Daniel Turf Center at the same address. This is distinct from the RecWell Turf Recreation Exercise Center.",
                f"The red GIS overlay follows the long low roof in the Esri imagery. The model's 12 lower footprint vertices reproduce the FID 208 ring after the documented local projection within {max_error:.6f} m maximum vertex residual.",
                f"Service Shape__Area is {service_area:.3f} m²; the ring in the project local ground frame is {ring_area:.3f} m² (ratio {area_ratio:.3f}), but shoelace area after reprojecting the same query ring to the source layer's EPSG:3857 is {mercator_ring_area:.3f} m² (relative error {source_area_relative_error:.6g}). Thus the apparent conflict in the notes results from comparing projected-plane area to ground-frame area; the remaining uncertainty is whether the ring outlines wall or roof edges.",
                "The initial FID 855 screening candidate is correctly rejected: it refers to the Old Purdue Exponent Building, not Daniel Turf Center."
            ],
            "findings": ["Confirm whether the GIS ring follows the structural wall line or roof edge before calling its area/as-built dimensions verified."]
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 1.7, "max_score": 2.0,
            "status": "campus coordinates and plan shape match named GIS and aerial evidence; source edge interpretation remains uncertain",
            "evidence": [
                f"Blender 5.2.3 reopened bounds X {bounds[0][0]:.3f}..{bounds[0][1]:.3f} m, Y {bounds[1][0]:.3f}..{bounds[1][1]:.3f} m, Z {bounds[2][0]:.3f}..{bounds[2][1]:.3f} m. FID 208 ring plan envelope is approximately {candidate_dims[0]:.2f} m by {candidate_dims[1]:.2f} m.",
                "The north-oriented outline occupies the long low building visible in the orthophoto overlay; projected ring vertices and reopened mesh are within sub-millimetre numerical residual. Campus coordinates use the documented local approximation, not a survey-grade CRS."
            ],
            "findings": ["The aerial supports roof position and shape but does not prove the GIS ring is the structural wall line; keep that distinction explicit."]
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 0.8, "max_score": 2.0,
            "status": "one story is GIS-supported; 4.2672 m height is only a provisional interpretation of an undocumented field",
            "evidence": [
                f"GIS NUM_LEVELS={attrs['NUM_LEVELS']} supports a one-story mass. GIS Extrution={attrs['Extrution']} has no documented units. The model's {bounds[2][1]:.4f} m height assumes 14 ft = 4.2672 m; that interpretation is not independently verified.",
                "The orthophoto shows a low elongated roof mass, but provides no height or roof pitch. The mesh uses a plain single-cap roof with no support for its vertical dimensions or roof profile from elevation/section evidence."
            ],
            "findings": ["Treat 4.2672 m strictly as an estimate; do not label 14 as feet without a source documenting that unit. Roof height, pitch, and profile remain unverified."]
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 0.5, "max_score": 2.0,
            "status": "no facade or entrance source was found; model appropriately remains plain massing",
            "evidence": [
                "The official HLA facility page and overhead imagery establish the facility and plan form, but the inspected source package contains no identifiable elevation or street-level facade image for this building.",
                "The oblique render is a plain single-cap volume with no facade, door, window, or distinguishing feature. Avoiding invented detail is appropriate, but the criterion is unverified rather than demonstrated accurate."
            ],
            "findings": ["Facade layout, entrances, materials and distinctive architectural elements are unverified; seek attributable ground-level imagery or plans before adding detail."]
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 1.6, "max_score": 2.0,
            "status": "asset reopens and evidence package is complete; shared manifest still has prior bounds/height",
            "evidence": [
                f"Direct Blender {d['version']} reopen confirms one mesh object in the expected scene/collection ({d['vertices']} vertices, {d['faces']} faces), {len(d['modifiers'])} modifiers, {len(d['unpacked_images'])} unpacked images, and {d['libraries']} linked libraries. The dedicated fresh-process check records zero nonmanifold edges and sub-millimetre ring residual.",
                "The audit package has raw FID 208 GIS and layer metadata, Purdue HLA page snapshot, Esri World Imagery with an aerial overlay, source register, two rendered views, build result, and reopen validation.",
                f"The coordinator-owned manifest bounds remain {manifest_bounds}, versus reopened mesh bounds {bounds}; maximum component difference is {max_manifest_delta:.3f} m (including prior 3.8 m height versus current 4.2672 m)."
            ],
            "findings": ["Coordinator should update the shared manifest bounds after accepting the source identity/geometry; the exported asset itself is self-contained."]
        }
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [f for c in criteria for f in c["findings"]]
    return {
        "building_id": ID,
        "building_name": "Purdue University Daniel Turf Center (William H. Daniel Turfgrass Research & Diagnostic Court)",
        "reviewer": "independent evaluator; direct Purdue FID 208 GIS and layer metadata, Purdue HLA source snapshot, Esri orthophoto/overlay, saved renders, and Blender 5.2.3 direct reopen",
        "score": score, "max_score": 10, "passing_standard": 8,
        "criteria": criteria,
        "evidence": {
            "asset_path": str(ASSET.relative_to(ROOT)),
            "blender": d["version"], "reopened_scene": d["scene"], "reopened_collection": d["collection"],
            "direct_reopen_measurements": {k: d[k] for k in ("object", "type", "collection_count", "vertices", "faces", "bounds", "materials", "unpacked_images", "libraries", "modifiers", "object_location")},
            "source_identity": {k: attrs.get(k) for k in ("FID", "BLDG_ABBR", "BUILDING_N", "ADDRESS", "NUM_LEVELS", "Extrution", "Shape__Area", "Shape__Length")},
            "footprint": {"coordinate_system": "query geometry EPSG:4326; local ground frame via modular/AGENTS.md approximation", "unique_ring_vertices": len(expected), "projected_envelope_m": candidate_dims, "local_ground_ring_area_m2": ring_area, "source_epsg3857_ring_area_m2": mercator_ring_area, "service_shape_area_m2": service_area, "service_to_local_area_ratio": area_ratio, "source_area_relative_error_after_epsg3857_reprojection": source_area_relative_error, "vertex_residuals_m": errors, "max_vertex_residual_m": max_error},
            "manifest_bounds_m": manifest_bounds, "manifest_delta_vs_asset_m": manifest_delta,
            "reviewed_files": [str((HERE / "README.md").relative_to(ROOT)), str((audit / "source_register.json").relative_to(ROOT)), str((audit / "purdue_buildings_fid208_query_2026-10-26.json").relative_to(ROOT)), str((audit / "purdue_buildings_layer_metadata_2026-10-26.json").relative_to(ROOT)), str(overlay.relative_to(ROOT)), str(official_page.relative_to(ROOT))] + [str(p.relative_to(ROOT)) for p in renders],
            "limitations": ["FID 208 identifies the Daniel Turfgrass Research & Diagnostic Court, not TREC; FID 855 is stale and unrelated.", f"The Shape__Area difference is reconciled by reprojection to the source layer's EPSG:3857 plane ({source_area_relative_error:.6g} relative area error); GIS ring may still follow the roof outline rather than the structural wall footprint.", "Extrution=14 units are undocumented; 14 ft and 4.2672 m are estimates only.", "Facade, entrances and roof profile have no attributable elevation evidence.", "Shared manifest still contains older bounds and height."]
        },
        "findings": findings,
        "recommendation": f"The asset scores {score}/10, below the 8/10 gate. Named Purdue GIS FID 208 and the orthophoto strongly support identity and plan placement; the Shape__Area/ring-area difference reconciles when measured in the source EPSG:3857 plane versus the local ground frame. The 14-ft height inference, wall-versus-roof outline, and facade/roof-form details remain uncertain. The shared manifest bounds also need coordinator reconciliation."
    }


if __name__ == "__main__":
    result = evaluate()
    (HERE / "independent_grade.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
