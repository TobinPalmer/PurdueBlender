"""Fresh independent r2 grade of Purdue University Daniel Turf Center.

The evaluator reopens the saved massing in Blender 5.2.3, verifies the named
Purdue FID 208 footprint and native EPSG:3857 area, and assesses the attributed
2011 exterior photo, geometry, uncertainty, evidence and modular export.
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


def readj(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def local_xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def ring_area(points):
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
        "'object_location':list(o.location)}; print('DANL_R2_DIRECT='+json.dumps(s))"
    )
    cp = subprocess.run([str(BLENDER), "--background", "--python-expr", expr],
                        cwd=ROOT, capture_output=True, text=True, timeout=180)
    if cp.returncode:
        raise RuntimeError("Blender reopen failed: " + cp.stderr[-1200:])
    m = re.search(r"DANL_R2_DIRECT=(\{[^\r\n]*\})", cp.stdout)
    if not m:
        raise RuntimeError("No direct Blender snapshot returned: " + cp.stdout[-1200:])
    return json.loads(m.group(1))


def first_feature(path):
    d = readj(path)
    if "features" in d:
        return next(f for f in d["features"] if f["attributes"].get("FID") == 208)
    return d["feature"]


def evaluate():
    assert ASSET.is_file() and BLENDER.is_file()
    d = reopen()
    srcdir = HERE / "sources"
    geographic = first_feature(srcdir / "purdue_buildings_fid208_query_2026-10-26.json")
    native = first_feature(srcdir / "purdue_buildings_fid208_native3857_2026-10-26.json")
    attrs = geographic["attributes"]
    gring = geographic["geometry"]["rings"][0]
    if gring[0] == gring[-1]:
        gring = gring[:-1]
    expected = [local_xy(lon, lat) for lon, lat in gring]
    base = d["vertices_world"][:len(expected)]
    residuals = [math.dist(xy, (v[0], v[1])) for xy, v in zip(expected, base)]
    max_residual = max(residuals)
    dims = [max(p[i] for p in expected) - min(p[i] for p in expected) for i in range(2)]
    native_ring = native["geometry"]["rings"][0]
    if native_ring[0] == native_ring[-1]:
        native_ring = native_ring[:-1]
    source_area = float(attrs["Shape__Area"])
    native_area = ring_area(native_ring)
    area_delta = native_area - source_area
    bounds = d["bounds"]
    manifest = readj(ROOT / "modular" / "manifest.json")
    entry = next(e for e in manifest["assets"] if e["id"] == ID)
    mb = entry["bounds_world_m"]
    manifest_delta = [[bounds[i][j] - mb[i][j] for j in range(2)] for i in range(3)]
    max_manifest_delta = max(abs(x) for row in manifest_delta for x in row)
    build = readj(HERE / "build_result.json")
    validation = readj(HERE / "reopen_validation.json")
    register = readj(srcdir / "source_register.json")
    photo = srcdir / "daniel_center_exterior_2011_janddturf.jpg"
    overlay = srcdir / "gis_fid208_aerial_overlay.png"
    renders = [HERE / "renders" / "daniel_turf_center_top.png",
               HERE / "renders" / "daniel_turf_center_oblique.png"]
    facility_page = srcdir / "purdue_daniel_turf_center_page_2026-10-26.html"
    assert d["version"].startswith("5.2.3")
    assert d["scene"] == f"Building_{ID}" and d["collection"] == f"Asset_{ID}"
    assert d["collection_count"] == 1 and d["type"] == "MESH"
    assert attrs["FID"] == 208 and attrs["BLDG_ABBR"] == "DANL"
    assert attrs["BUILDING_N"] == "William H. Daniel Turfgrass Research & Diagnostic Court"
    assert attrs["ADDRESS"] == "1340 Cherry Lane"
    assert len(expected) == 12 and len(native_ring) == 12 and max_residual < 0.001
    assert abs(area_delta) < 0.02
    assert all(p.is_file() for p in [photo, overlay, facility_page] + renders)

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 1.9, "max_score": 2.0,
            "status": "named FID/address and 2011 photo support the target; GIS ring aligns with roof projection, not a surveyed wall line",
            "evidence": [
                f"Purdue GIS FID {attrs['FID']} / {attrs['BLDG_ABBR']} names {attrs['BUILDING_N']} at {attrs['ADDRESS']}. The Purdue HLA facility page independently identifies Daniel Turf Center at that address, and the attached 2011 J&D Turf report explicitly captions its image as the Daniel Center building exterior.",
                "This is separate from the RecWell Turf Recreation Exercise Center. The inherited screening FID 855 is the Old Purdue Exponent Building and is unrelated; the named DANL FID 208 match is used.",
                f"The GIS ring transformed to the documented campus frame is reproduced by the model's 12 lower vertices within {max_residual:.6f} m. The GIS aerial overlay aligns the ring to the long low roof projection; wall face and roof overhang offsets remain unavailable.",
                f"The apparent GIS area conflict is resolved in like-for-like native EPSG:3857 coordinates: ring shoelace area {native_area:.6f} m², Shape__Area {source_area:.6f} m², delta {area_delta:.6f} m². The ~677.061 m² local-frame area is ground-scale and is not directly comparable to Web Mercator plane area."
            ],
            "findings": ["The GIS outline is an accurate source-ring match but may track the roof projection; retain the unverified wall-line/overhang offset."]
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 1.8, "max_score": 2.0,
            "status": "plan location/orientation and source footprint reproduce closely; wall line and true dimensions remain approximate",
            "evidence": [
                f"Direct Blender reopen bounds are X {bounds[0][0]:.3f}..{bounds[0][1]:.3f} m, Y {bounds[1][0]:.3f}..{bounds[1][1]:.3f} m, and Z {bounds[2][0]:.3f}..{bounds[2][1]:.3f} m. The transformed FID 208 ring is about {dims[0]:.2f} m by {dims[1]:.2f} m.",
                "The official aerial overlay supports the building's roof-plan position and long axis; the 2011 exterior image is consistent with the long, low one-story mass. The local campus formula is approximate and neither source supplies a surveyed wall-line dimension."
            ],
            "findings": ["Treat the base ring as a roof-projection-based plan estimate; exact wall line and overhang remain unmeasured."]
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.0, "max_score": 2.0,
            "status": "one story and shallow gable are directly supported; absolute vertical dimensions remain visual estimates",
            "evidence": [
                f"Purdue GIS NUM_LEVELS={attrs['NUM_LEVELS']} supports one story. The attributed 2011 exterior photo shows a long single-story building with a shallow gable roof and the ridge aligned with the building's long axis; this supports form more directly than the prior aerial-only evidence.",
                f"The reopened mass reaches {bounds[2][1]:.2f} m. Build notes give an eave estimate of {build['gis']['visual_eave_height_estimate_m_low_confidence']:.2f} m and ridge estimate of {build['gis']['visual_ridge_height_estimate_m_low_confidence']:.2f} m based on visual scale only; no calibrated height, section or elevation exists.",
                f"GIS Extrution={attrs['Extrution']} is preserved uninterpreted; it is not used as a height because its units are undocumented. The photo supports a shallow gable but not a measured pitch or vertical scale."
            ],
            "findings": ["Keep the 3.25 m eave and 4.05 m ridge heights explicitly low-confidence estimates; no measured height source was found."]
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 0.7, "max_score": 2.0,
            "status": "photo supports metal cladding, window band and centered canopy, but the massing asset omits these facade elements",
            "evidence": [
                "The 2011 photo directly shows pale metal wall cladding, a centered entrance canopy, a horizontal row of windows, and a shallow-gabled long rectangular form.",
                "The current oblique render shows a plain neutral wall shell and shallow gable. It omits the visible windows, entrance canopy and wall cladding/rib detail; no facade composition is demonstrated in the model. Given the explicitly massing-only scope, omitting unsupported small details is understandable, but the photographed features are supported and absent.",
                "The official imagery overlay is top-down and cannot verify facade features. The expansion concept and Synthesis proposals are correctly excluded as proposed rather than as-built evidence."
            ],
            "findings": ["For a closer match to the attributable photo, add the centered canopy and simple window band and indicate the light metal-clad exterior; otherwise keep the facade criterion marked as unmodeled."]
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 1.6, "max_score": 2.0,
            "status": "asset reopens cleanly and evidence is varied; shared manifest bounds/height still reflect the earlier massing",
            "evidence": [
                f"Fresh Blender {d['version']} reopen confirms the expected scene/collection, one mesh object ({d['vertices']} vertices, {d['faces']} faces), {len(d['modifiers'])} modifiers, {len(d['unpacked_images'])} unpacked images and {d['libraries']} linked libraries. Separate validation reports a closed manifold shell and a maximum footprint vertex error of {validation['footprint_vertex_max_error_m']:.7f} m.",
                "The evidence package includes native and WGS84 GIS snapshots, GIS metadata, official HLA page, aerial imagery/overlay, a named 2011 exterior photo, source register, two renders, build record and reopen validation.",
                f"The shared manifest still reports bounds {mb}, while the reopened asset is {bounds}; maximum component difference is {max_manifest_delta:.3f} m, including its prior 3.8 m height versus current 4.05 m. Shared manifest reconciliation remains coordinator-owned."
            ],
            "findings": ["Coordinator should update shared manifest bounds/height after accepting the rebuilt asset; the model itself is self-contained and reopens successfully."]
        }
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [x for criterion in criteria for x in criterion["findings"]]
    return {
        "building_id": ID,
        "building_name": "Purdue University Daniel Turf Center / William H. Daniel Turfgrass Research & Diagnostic Court",
        "reviewer": "independent r2 evaluator; Purdue GIS FID 208 native and WGS84 snapshots, Purdue HLA page, 2011 attributed exterior photo, Esri aerial overlay, two views and Blender 5.2.3 direct reopen",
        "score": score, "max_score": 10, "passing_standard": 8,
        "criteria": criteria,
        "evidence": {
            "asset_path": str(ASSET.relative_to(ROOT)),
            "blender": d["version"], "reopened_scene": d["scene"], "reopened_collection": d["collection"],
            "direct_reopen_measurements": {k: d[k] for k in ("object", "type", "collection_count", "vertices", "faces", "bounds", "materials", "unpacked_images", "libraries", "modifiers", "object_location")},
            "source_identity": {k: attrs.get(k) for k in ("FID", "BLDG_ABBR", "BUILDING_N", "ADDRESS", "NUM_LEVELS", "Extrution", "Shape__Area")},
            "footprint": {"source_crs": "EPSG:4326 query and native EPSG:3857 geometry", "projected_bounds_xy_m": [ [min(p[i] for p in expected), max(p[i] for p in expected)] for i in range(2)], "ground_local_ring_area_m2": build["gis"]["approx_local_polygon_area_m2"], "native_3857_ring_area_m2": native_area, "native_shape_area_m2": source_area, "native_area_delta_m2": area_delta, "max_asset_ring_vertex_error_m": max_residual, "wall_line_status": "unverified; overlay is roof projection"},
            "height": {"eave_estimate_m": build["gis"]["visual_eave_height_estimate_m_low_confidence"], "ridge_estimate_m": build["gis"]["visual_ridge_height_estimate_m_low_confidence"], "extrution_raw_uninterpreted": attrs["Extrution"], "measured_height_available": False},
            "manifest_bounds_m": mb,
            "reviewed_files": [str((HERE / "README.md").relative_to(ROOT)), str((HERE / "r2_iteration_notes.md").relative_to(ROOT)), str((srcdir / "source_register.json").relative_to(ROOT)), str((srcdir / "purdue_buildings_fid208_query_2026-10-26.json").relative_to(ROOT)), str((srcdir / "purdue_buildings_fid208_native3857_2026-10-26.json").relative_to(ROOT)), str((srcdir / "daniel_center_exterior_2011_janddturf.jpg").relative_to(ROOT)), str(overlay.relative_to(ROOT)), str(facility_page.relative_to(ROOT))] + [str(p.relative_to(ROOT)) for p in renders],
            "limitations": ["GIS/orthophoto outline may follow roof projection rather than wall line.", "Eave/ridge heights are low-confidence visual estimates; Extrution=14 has undocumented units and is not used.", "2011 photo supports facade features, but current massing omits windows, canopy, and cladding detail.", "No exact facade measurements or calibrated roof pitch is available.", "Shared manifest bounds remain stale."]
        },
        "findings": findings,
        "recommendation": f"The asset scores {score}/10 and does not pass the 8/10 gate. Identity, one-story shallow-gable form, and plan location are supported by named Purdue GIS, current imagery, and the explicitly attributed 2011 exterior photo; vertical scale remains estimated and the photographed canopy/window band/cladding are absent from the massing. Shared manifest bounds and height also need reconciliation."
    }


if __name__ == "__main__":
    result = evaluate()
    (HERE / "independent_grade_r2.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
