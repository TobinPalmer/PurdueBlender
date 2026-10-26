"""Independent rubric evaluator for Provenance Apartments 005.

Reopens the saved library with Blender 5.2.3 and compares the shell ring to
Purdue's FID 506 GIS candidate. The GIS source layer is explicitly
"BLDG Building Pre-planning"; this evaluation does not promote that candidate
to a verified as-built footprint.
"""
import json
import math
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ID = "massing_provenance_apartments_005_960f6b0"
ASSET = ROOT / "modular" / "buildings" / f"{ID}.blend"
BLENDER = ROOT.parent / "blender" / "blender-5.2.3-windows-x64" / "blender.exe"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def wgs84_to_campus(x, y):
    """Inverse Web Mercator then use the documented campus approximation."""
    lon = math.degrees(x / 6378137.0)
    lat = math.degrees(2 * math.atan(math.exp(y / 6378137.0)) - math.pi / 2)
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def reopen_asset():
    expr = (
        "import bpy,json; "
        f"bpy.ops.wm.open_mainfile(filepath={str(ASSET)!r}); "
        f"c=bpy.data.collections.get('Asset_{ID}'); "
        "o=bpy.data.objects.get('Provenance Apartments.005'); "
        "v=[[(o.matrix_world@x.co)[i] for i in range(3)] for x in o.data.vertices]; "
        "b=[[min(x[i] for x in v),max(x[i] for x in v)] for i in range(3)]; "
        "s={'version':bpy.app.version_string,'scene':bpy.context.scene.name,"
        "'collection':c.name if c else None,'collection_count':len(c.objects) if c else -1,"
        "'object':o.name if o else None,'type':o.type if o else None,"
        "'vertices':len(o.data.vertices) if o else None,'faces':len(o.data.polygons) if o else None,"
        "'bounds':b,'base_vertices':v[:32],"
        "'materials':[m.name for m in o.data.materials if m],"
        "'unpacked_images':[i.filepath for i in bpy.data.images if i.filepath and not i.packed_file],"
        "'libraries':len(bpy.data.libraries),'modifiers':[m.name for m in o.modifiers]}; "
        "print('PROVENANCE_REOPEN='+json.dumps(s))"
    )
    cp = subprocess.run([str(BLENDER), "--background", "--python-expr", expr],
                        cwd=ROOT, capture_output=True, text=True, timeout=180)
    if cp.returncode:
        raise RuntimeError("Blender reopen failed: " + cp.stderr[-1500:])
    m = re.search(r"PROVENANCE_REOPEN=(\{[^\r\n]*\})", cp.stdout)
    if not m:
        raise RuntimeError("Blender did not return a reopen snapshot: " + cp.stdout[-1500:])
    return json.loads(m.group(1))


def evaluate():
    assert ASSET.is_file() and BLENDER.is_file()
    d = reopen_asset()
    reg = read_json(HERE / "source_register.json")
    build = read_json(HERE / "build_evidence.json")
    validation = read_json(HERE / "reopen_validation.json")
    gis = read_json(HERE / "sources" / "official_purdue_fid506.json")["feature"]
    attrs = gis["attributes"]
    ring = gis["geometry"]["rings"][0]
    if ring[0] == ring[-1]:
        ring = ring[:-1]
    expected = [wgs84_to_campus(x, y) for x, y in ring]
    base = d["base_vertices"][:len(expected)]
    residuals = [math.dist(p, (v[0], v[1])) for p, v in zip(expected, base)]
    max_residual = max(residuals)
    dims = [max(p[i] for p in expected) - min(p[i] for p in expected) for i in range(2)]
    manifest = read_json(ROOT / "modular" / "manifest.json")
    entry = next(x for x in manifest["assets"] if x["id"] == ID)
    mb = entry["bounds_world_m"]
    bounds = d["bounds"]
    manifest_delta = [[bounds[i][j] - mb[i][j] for j in range(2)] for i in range(3)]
    views = [HERE / "preview_southwest.png", HERE / "preview_top.png"]
    photos = [HERE / "sources" / n for n in ("studio_m_photo_1.jpg", "studio_m_photo_2.jpg", "studio_m_photo_poi26.jpg")]
    assert d["version"].startswith("5.2.3")
    assert d["scene"] == f"Building_{ID}" and d["collection"] == f"Asset_{ID}"
    assert d["collection_count"] == 1 and d["type"] == "MESH"
    assert attrs["FID"] == 506 and attrs["BUILDING_N"] == "Building F"
    assert attrs["Layer"] == "BLDG Building Pre-planning"
    assert len(residuals) == 32 and max_residual < 0.001
    assert all(p.is_file() for p in views + photos)

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 1.0, "max_score": 2.0,
            "status": "FID 506 is an explicit Building F candidate, but the feature is pre-planning and the as-built identity/wall line is unverified",
            "evidence": [
                f"Purdue Campus Map FeatureServer layer 0 FID {attrs['FID']} is named {attrs['BUILDING_N']} (BLDG_ABBR {attrs['BLDG_ABBR']}; Building_F field {attrs['Building_F']}). Its layer attribute is {attrs['Layer']!r}, BUILDING_1 is {attrs['BUILDING_1']!r}, while ADDRESS is blank, NUM_LEVELS is {attrs['NUM_LEVELS']}, and BUILT/OCCUPIED are null.",
                f"The 32-vertex model base ring matches this FID 506 polygon after inverse Web Mercator and the repository's campus projection to {max_residual:.6f} m maximum vertex residual. This verifies reproduction of the candidate geometry, not that the pre-planning polygon is the as-built Building F wall line.",
                "The Purdue Residences page confirms Provenance as the apartment community, and Studio M's project page confirms the development and seven three-story buildings, but neither source cross-identifies this GIS polygon as the completed individual Building F."
            ],
            "findings": ["Treat FID 506 as a candidate only; a current as-built campus footprint or identifiable Building F address/elevation is needed to verify the selected individual building and wall registration."]
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 1.5, "max_score": 2.0,
            "status": "campus coordinates and dimensions match the direct GIS candidate; physical as-built registration remains uncertain",
            "evidence": [
                f"Direct Blender reopen bounds are X {bounds[0][0]:.3f}..{bounds[0][1]:.3f} m, Y {bounds[1][0]:.3f}..{bounds[1][1]:.3f} m, and Z {bounds[2][0]:.3f}..{bounds[2][1]:.3f} m. The transformed FID 506 candidate envelope is {dims[0]:.2f} m by {dims[1]:.2f} m.",
                "The single mesh retains campus-world coordinates and identity transform, and its shell ring reproduces the candidate polygon at sub-millimetre numerical error. The uncertainty is upstream in whether the pre-planning polygon represents the as-built footprint, rather than in the Blender transformation."
            ],
            "findings": ["Validate the candidate position/orientation/dimensions against current orthophoto or as-built survey before treating them as verified for the completed building."]
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.2, "max_score": 2.0,
            "status": "three-story character and repeated gables are supported at project level; building-specific dimensions are estimates",
            "evidence": [
                "Studio M's project description states that the Provenance development has seven three-story apartment buildings; project photographs show repeated gabled roofs. This supports the general storey count and roof vocabulary but does not assign an elevation or exact gable sequence to FID 506.",
                f"The model uses estimated {build['dimensions']['wall_height_m']:.1f} m wall/eave and {build['dimensions']['ridge_height_m']:.1f} m ridge heights. The Purdue FID 506 record itself has NUM_LEVELS=0 and Extrution=0, so it provides no height measurement."
            ],
            "findings": ["Keep wall and ridge heights and the five-segment roof layout labeled as estimates; no Building F section, survey, or individually attributable roof image is present."]
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 0.8, "max_score": 2.0,
            "status": "project material palette and repeated gables are recognizable; individual facade composition is generalized",
            "evidence": [
                "Studio M images show a three-story apartment facade with brick, dark framed windows, balconies, dark vertical accent bays/panels, and repeated gabled roof masses. The secondary project material description supports brick and dark panel/cherry finishes, though those finishes are not assigned to individual FID 506 elevations.",
                "The southwest render conveys a long three-story brick block with repeated roof breaks and windows, but the facade is highly schematic: no balconies, entrances, canopy/door details, or clear dark accent panels are visible; window placement and gable-to-facade correspondence are not attributable to this individual building. The top preview is useful for plan inspection but does not add facade evidence."
            ],
            "findings": ["The model's facades lack prominent visible elements in the official project photographs, especially balconies, framed glazing, dark accent bays, and identifiable entries. Building-specific reference imagery is needed before assigning exact arrangement."]
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 1.6, "max_score": 2.0,
            "status": "saved library and evidence reopen cleanly; shared manifest bounds still describe the superseded proxy",
            "evidence": [
                f"Blender {d['version']} reopened scene {d['scene']} and collection {d['collection']} with one mesh ({d['vertices']} vertices, {d['faces']} faces), no modifiers, {len(d['unpacked_images'])} unpacked image dependencies, and {d['libraries']} linked Blender libraries.",
                "The audit folder includes the raw official FID 506 feature and layer metadata, source register, project/residences snapshots, three project photographs, two previews, build evidence, and a separate-process reopen validation.",
                f"The shared manifest still declares bounds {mb}; reopened geometry bounds are {bounds}. This mismatch is up to {max(abs(x) for row in manifest_delta for x in row):.2f} m and shows that the coordinator-owned manifest was not reconciled with the rebuilt candidate asset. The asset itself and dedicated evidence are portable."
            ],
            "findings": ["Coordinator should reconcile the shared manifest bounds with the rebuilt asset after independent source identity/footprint review."]
        }
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [f for c in criteria for f in c["findings"]]
    return {
        "building_id": ID,
        "building_name": "Provenance Apartments 005 (FID 506 Building F candidate)",
        "reviewer": "independent evaluator; direct FID 506 GIS snapshot/layer metadata, first-party project/residences pages, three Studio M photographs, two renders, and Blender 5.2.3 direct reopen",
        "score": score, "max_score": 10, "passing_standard": 8,
        "criteria": criteria,
        "evidence": {
            "asset_path": str(ASSET.relative_to(ROOT)),
            "blender": d["version"], "reopened_scene": d["scene"], "reopened_collection": d["collection"],
            "direct_reopen_measurements": {k: d[k] for k in ("object", "type", "collection_count", "vertices", "faces", "bounds", "materials", "unpacked_images", "libraries", "modifiers")},
            "source_identity": {k: attrs.get(k) for k in ("FID", "BUILDING_N", "Layer", "BLDG_ABBR", "BUILDING_1", "ADDRESS", "NUM_LEVELS", "BUILT", "OCCUPIED", "Building_F")},
            "candidate_footprint": {"source_crs": "EPSG:3857 confirmed by FeatureServer metadata", "source_ring_vertex_count": len(ring), "projected_candidate_envelope_m": dims, "per_vertex_residuals_m": residuals, "max_vertex_residual_m": max_residual, "as_built_status": "unverified; source layer says BLDG Building Pre-planning"},
            "manifest_bounds_m": mb, "manifest_delta_vs_mesh_bounds_m": manifest_delta,
            "reviewed_files": [str((HERE / "source_register.json").relative_to(ROOT)), str((HERE / "build_evidence.json").relative_to(ROOT)), str((HERE / "reopen_validation.json").relative_to(ROOT))] + [str(p.relative_to(ROOT)) for p in views + photos],
            "limitations": ["FID 506 candidate identity and as-built wall footprint are not confirmed by current survey or individual-building imagery.", "GIS record has zero levels, zero extrusion, and blank address; heights are estimates.", "Studio M photographs establish development-wide architectural vocabulary but do not identify the FID 506 block.", "Shared manifest bounds remain from the earlier, much wider massing proxy."]
        },
        "findings": findings,
        "recommendation": f"The asset scores {score}/10 and does not pass the 8/10 gate. The saved mesh faithfully reproduces the FID 506 pre-planning polygon, but the individual as-built identity/footprint is unverified, building-specific height/facade evidence is absent, and the shared manifest bounds still need reconciliation."
    }


if __name__ == "__main__":
    result = evaluate()
    (HERE / "independent_grade.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
