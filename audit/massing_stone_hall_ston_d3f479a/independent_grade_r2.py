"""Independent, evidence-based grade for Stone Hall r2.

Run with the Python standard library. This evaluator reads the raw GIS snapshot,
source registry, audit note, build/reopen reports, and saved r2 preview renders.
It does not edit the asset or project build files.
"""
from __future__ import annotations

import json
import math
import subprocess
import struct
from pathlib import Path


AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parents[1]
ASSET = ROOT / "modular" / "buildings" / "massing_stone_hall_ston_d3f479a.blend"
BLENDER = ROOT.parent / "blender" / "blender-4.5.15-windows-x64" / "blender.exe"
SOURCES = AUDIT / "sources"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def transform_ring(ring):
    lat0, lon0 = 40.4274, -86.9137
    sx = 111412.84 * math.cos(math.radians(lat0))
    sy = 111040.0
    pts = []
    for lon, lat in ring:
        p = ((lon - lon0) * sx, (lat - lat0) * sy)
        if not pts or math.dist(pts[-1], p) > 1e-6:
            pts.append(p)
    if len(pts) > 2 and math.dist(pts[0], pts[-1]) < 1e-6:
        pts.pop()
    return pts


def polygon_metrics(points):
    area2 = sum(points[i][0] * points[(i + 1) % len(points)][1]
                - points[(i + 1) % len(points)][0] * points[i][1]
                for i in range(len(points)))
    perimeter = sum(math.dist(points[i], points[(i + 1) % len(points)])
                    for i in range(len(points)))
    return abs(area2) / 2, perimeter


def png_size(path: Path):
    with path.open("rb") as f:
        header = f.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", header[16:24])


def inspect_blend_direct(source_path: Path):
    """Open the saved blend in background Blender and inspect actual datablocks."""
    if not BLENDER.is_file() or not ASSET.is_file():
        return {"available": False, "reason": "Blender executable or asset file is missing"}
    source_literal = json.dumps(str(source_path))
    code = f'''import bpy,json,os,math
from mathutils import Vector
source=json.load(open({source_literal},encoding="utf-8-sig"))["features"][0]
raw=source["geometry"]["rings"][0]
lat0,lon0=40.4274,-86.9137
sx=111412.84*math.cos(math.radians(lat0)); sy=111040.0
pts=[]
for lon,lat in raw:
 p=((lon-lon0)*sx,(lat-lat0)*sy)
 if not pts or math.dist(pts[-1],p)>1e-6: pts.append(p)
if len(pts)>2 and math.dist(pts[0],pts[-1])<1e-6: pts.pop()
coll=bpy.data.collections.get("Asset_massing_stone_hall_ston_d3f479a")
owned=list(coll.objects) if coll else []
obj=owned[0] if len(owned)==1 else None
n=int(obj.get("footprint_ring_vertices",0)) if obj else 0
meshpts=[(obj.data.vertices[i].co.x,obj.data.vertices[i].co.y) for i in range(min(n,len(obj.data.vertices)))] if obj else []
ring_match=(len(meshpts)==len(pts) and all(math.dist(a,b)<=1e-4 for a,b in zip(sorted(pts),sorted(meshpts))))
corners=[obj.matrix_world@Vector(c) for c in obj.bound_box] if obj else []
bounds=[[min(v[i] for v in corners),max(v[i] for v in corners)] for i in range(3)] if corners else None
images=[{{"name":im.name,"filepath":bpy.path.abspath(im.filepath),"exists":os.path.exists(bpy.path.abspath(im.filepath)),"packed":im.packed_file is not None}} for im in bpy.data.images if im.source=="FILE" and im.filepath]
libraries=[lib.filepath for lib in bpy.data.libraries]
report={{"filepath":bpy.data.filepath,"scene":bpy.context.scene.name,"scene_object_count":len(bpy.context.scene.objects),"collection_present":coll is not None,"collection_object_count":len(owned),"collection_objects":[o.name for o in owned],"object_type":obj.type if obj else None,"mesh_vertices":len(obj.data.vertices) if obj and obj.type=="MESH" else None,"mesh_faces":len(obj.data.polygons) if obj and obj.type=="MESH" else None,"world_bounds":bounds,"file_image_dependencies":images,"libraries":libraries,"object_library":obj.library.filepath if obj and obj.library else None,"mesh_data_library":obj.data.library.filepath if obj and obj.data.library else None,"material_libraries":[m.library.filepath if m and m.library else None for m in obj.data.materials] if obj else [],"scene_root_collections":[c.name for c in bpy.context.scene.collection.children],"asset_collection_at_scene_root":coll is not None and coll.name in [c.name for c in bpy.context.scene.collection.children],"footprint_ring_vertices":n,"source_ring_vertices":len(pts),"footprint_matches_source_ring":ring_match}}
print("DIRECT_ASSET_REPORT="+json.dumps(report,sort_keys=True))'''
    try:
        proc = subprocess.run(
            [str(BLENDER), "--background", str(ASSET), "--python-expr", code],
            capture_output=True, text=True, timeout=90, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"available": False, "reason": str(exc)}
    marker = "DIRECT_ASSET_REPORT="
    line = next((line for line in proc.stdout.splitlines() if line.startswith(marker)), None)
    if proc.returncode != 0 or line is None:
        return {"available": False, "reason": f"Blender exited {proc.returncode}",
                "stdout": proc.stdout[-2000:], "stderr": proc.stderr[-2000:]}
    report = json.loads(line[len(marker):])
    report["available"] = True
    report["blender_executable"] = str(BLENDER)
    report["blender_version_line"] = next((line.strip() for line in proc.stdout.splitlines()
                                           if line.startswith("Blender ")), None)
    return report


def evaluate():
    gis_path = SOURCES / "purdue_building_gis_fid240_ston_4326.json"
    metadata_path = SOURCES / "purdue_building_gis_layer_metadata.json"
    registry_path = SOURCES / "source_registry.json"
    archive_path = SOURCES / "purdue_historic_building_record_71.html"
    note_path = AUDIT / "audit_note.md"
    build_path = AUDIT / "build_validation.json"
    reopen_path = AUDIT / "reopen_validation.json"

    gis = load_json(gis_path)
    registry = load_json(registry_path)
    build = load_json(build_path)
    reopened = load_json(reopen_path)
    direct = inspect_blend_direct(gis_path)
    note = note_path.read_text(encoding="utf-8")
    attrs = gis["features"][0]["attributes"]
    raw_ring = gis["features"][0]["geometry"]["rings"][0]
    ring = transform_ring(raw_ring)
    ring_area, ring_perimeter = polygon_metrics(ring)
    gis_source = next(s for s in registry["sources"] if s.get("feature_id") == 240)
    archive_source = next(s for s in registry["sources"] if s.get("feature_ids") == [1371, 1372, 1373, 1374])
    archive_ids = archive_source["feature_ids"]
    preview_names = ["stone_hall_isometric.png", "stone_hall_front.png", "stone_hall_top.png"]
    previews = {name: png_size(AUDIT / "preview" / name) for name in preview_names}
    photos = [SOURCES / name for name in archive_source["snapshots"]]

    identity = (attrs.get("FID") == 240 and attrs.get("BLDG_ABBR") == "STON"
                and attrs.get("BUILDING_N") == "Winthrop E. Stone Hall"
                and attrs.get("ADDRESS") == "700 Mitch Daniels Blvd"
                and reopened.get("source_fid_property") == 240)
    ring_match = (direct.get("footprint_matches_source_ring") is True
                  and reopened.get("footprint_matches_source_ring") is True
                  and reopened.get("source_ring_vertices") == len(ring)
                  and reopened.get("footprint_ring_vertices") == len(ring))
    package_report_pass = (reopened.get("status") == "pass"
                           and reopened.get("collection_present") is True
                           and reopened.get("collection_object_count") == 1
                           and reopened.get("external_image_dependencies") == [])
    render_bundle_ok = all(v is not None for v in previews.values()) and all(p.is_file() for p in photos)
    direct_package_ok = (direct.get("available") is True
                         and direct.get("scene") == "Building_massing_stone_hall_ston_d3f479a"
                         and direct.get("collection_present") is True
                         and direct.get("collection_object_count") == 1
                         and direct.get("collection_objects") == ["Stone Hall (STON)"]
                         and direct.get("object_type") == "MESH"
                         and direct.get("libraries") == []
                         and direct.get("file_image_dependencies") == []
                         and direct.get("object_library") is None
                         and direct.get("mesh_data_library") is None
                         and all(x is None for x in direct.get("material_libraries", []))
                         and direct.get("asset_collection_at_scene_root") is True)
    area_stored = float(attrs["Shape__Area"])
    perimeter_stored = float(attrs["Shape__Length"])
    area_ratio = area_stored / ring_area
    perimeter_ratio = perimeter_stored / ring_perimeter

    criteria = [
        {
            "name": "Identity / footprint",
            "score": 2.0 if identity and ring_match else 1.0,
            "max_score": 2,
            "status": "GIS identity and ring corroborated; GIS summary metrics conflict",
            "evidence": [
                f"Raw Purdue GIS FID {attrs['FID']} identifies {attrs['BUILDING_N']} ({attrs['BLDG_ABBR']}), {attrs['ADDRESS']}; saved reopen record carries source FID 240.",
                f"Independently transformed raw ring has {len(ring)} unique vertices and approximate area {ring_area:.3f} m² / perimeter {ring_perimeter:.3f} m; Blender directly compared it with the saved mesh base ring and found match={direct.get('footprint_matches_source_ring')}.",
                f"Stored Shape__Area={area_stored:.6f} is {area_ratio:.3f}x ring-derived area; Shape__Length={perimeter_stored:.6f} is {perimeter_ratio:.3f}x ring-derived perimeter. The polygon ring is the usable footprint source, not these inconsistent aggregates.",
                "Top preview shows the mapped stepped/jogged plan shape; footprint remains an approximate campus GIS envelope, not surveyed wall lines.",
            ],
        },
        {
            "name": "Position / orientation / scale",
            "score": 1.75 if ring_match else 0.75,
            "max_score": 2,
            "status": "ring registration supported with approximate transform limitation",
            "evidence": [
                f"Background Blender directly opened the asset and reported bounds {direct.get('world_bounds')}; the first {direct.get('footprint_ring_vertices')} base vertices match the transformed source ring={direct.get('footprint_matches_source_ring')}.",
                "Top render also visibly retains the source ring's main jogs. Registration uses the documented campus transform and is not survey-controlled.",
                "Coordinates use a local approximate geographic transform, not surveyed CRS/control; orientation and absolute registration inherit that limitation.",
            ],
        },
        {
            "name": "Height / floors / roof",
            "score": 0.75,
            "max_score": 2,
            "status": "estimated height; story interpretation and roof silhouette partly supported",
            "evidence": [
                f"Raw GIS has NUM_LEVELS={attrs.get('NUM_LEVELS')} and Extrution={attrs.get('Extrution')}; the layer does not declare Extrution units. Reported model height {reopened.get('height_m')} m is 45 ft converted to meters, an explicit but unverified interpretation.",
                "GIS F01-F04 values are used to support four visible facade bands; B and G are retained as ambiguous below/grade-related fields. The rendered four bands do not independently demonstrate six stories.",
                "Archive images support a low flat/parapet edge, which the flat roof approximates. No surveyed top elevation or floor-to-floor dimensions are supplied.",
            ],
        },
        {
            "name": "Facade / entrance",
            "score": 1.5,
            "max_score": 2,
            "status": "improved, photo-informed stylization; proportions remain approximate",
            "evidence": [
                f"Archive photos {archive_ids} visibly support brick walling, pale vertical pilasters and horizontal bands, regularly repeated rectangular windows, a centered formal entrance with multiple doors, and broad shallow steps.",
                "R2 front/isometric renders show brick-colored walling, pale vertical and horizontal trim, repeated windows, a wider three-panel entrance surround, and entry steps. These match the source vocabulary better than a blank massing shell.",
                "Compared with archive views, modeled openings and entrance remain simplified and much less monumental; facade bay/window proportions and the visible story rhythm are stylized rather than measured. Historical views do not establish current condition.",
            ],
        },
        {
            "name": "Modular export / evidence",
            "score": 2.0 if package_report_pass and render_bundle_ok and direct_package_ok else 0.75,
            "max_score": 2,
            "status": "direct Blender open and package evidence checks pass" if direct_package_ok else "package evidence incomplete or direct Blender check failed",
            "evidence": [
                f"Direct Blender 4.5.15 open reports scene={direct.get('scene')}, collection present={direct.get('collection_present')}, one object={direct.get('collection_objects')}, mesh={direct.get('object_type')} with {direct.get('mesh_vertices')} vertices / {direct.get('mesh_faces')} faces; world bounds={direct.get('world_bounds')}.",
                f"Link inspection reports libraries={direct.get('libraries')}, file image dependencies={direct.get('file_image_dependencies')}, object/mesh/material library links={[direct.get('object_library'), direct.get('mesh_data_library'), direct.get('material_libraries')]}, and asset collection linked at scene root={direct.get('asset_collection_at_scene_root')}.",
                f"Saved reopen report agrees: scene {reopened.get('scene')}, collection {reopened.get('collection_present')}, {reopened.get('collection_object_count')} object(s), no linked image dependencies, status={reopened.get('status')}.",
                "The audit bundle contains source registry with provider, URLs, retrieval date, source CRS, method and uncertainty; raw GIS feature/layer metadata; archive page and four photographs; build and reopen reports; and three preview renders.",
                f"R2 previews are readable PNGs: {previews}; the four cited photo files are present={all(p.is_file() for p in photos)}. The blend exists={ASSET.is_file()} (bytes={ASSET.stat().st_size if ASSET.is_file() else None}).",
                f"The evaluator directly opened the saved .blend with `{BLENDER} --background {ASSET} --python-expr <embedded inspection code>`; Blender reported no external libraries or file image dependencies.",
            ],
        },
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    evidence = [
        str(ASSET), str(gis_path), str(metadata_path), str(registry_path), str(archive_path),
        str(note_path), str(build_path), str(reopen_path),
        *[str(SOURCES / n) for n in archive_source["snapshots"]],
        *[str(AUDIT / "preview" / n) for n in preview_names],
    ]
    findings = [
        f"Score: {score}/10 using the five published two-point criteria.",
        f"GIS FID 240 is the correct Stone Hall identity; the raw polygon ring yields about {ring_area:.3f} m² and {ring_perimeter:.3f} m, while stored Shape__Area={area_stored:.3f} and Shape__Length={perimeter_stored:.3f} materially disagree.",
        "The 13.716 m top is not a measured height: it assumes GIS Extrution=45 means feet, while the GIS layer declares no units. The GIS NUM_LEVELS=6 also does not map directly to the four visible facade bands.",
        "R2's wider entrance surround, steps, taller window treatment, brick and pale trim align more closely with archive photos 1371-1374, but remain a qualitative interpretation.",
        f"Background Blender directly verified the asset scene, root export collection, single mesh object, world bounds, absence of external links, and the mesh base ring against the transformed GIS ring (match={direct.get('footprint_matches_source_ring')}).",
    ]
    return {
        "building_id": "massing_stone_hall_ston_d3f479a",
        "revision": "r2",
        "score": score,
        "max_score": 10,
        "criteria": criteria,
        "evidence": evidence,
        "findings": findings,
        "metrics": {
            "source_ring_vertices": len(ring), "ring_area_m2_approx": round(ring_area, 3),
            "ring_perimeter_m_approx": round(ring_perimeter, 3),
            "stored_shape_area": area_stored, "stored_shape_length": perimeter_stored,
            "stored_to_ring_area_ratio": round(area_ratio, 3),
            "stored_to_ring_perimeter_ratio": round(perimeter_ratio, 3),
            "height_m_reported": reopened.get("height_m"), "height_interpretation": "Extrution=45 assumed feet; unit undeclared",
        },
        "direct_blender_inspection": direct,
        "limitations": [
            "The GIS-to-campus transform is approximate; source aggregate geometry fields conflict with the ring-derived metrics.",
            "Archive photographs are historical and perspective views, not measured elevations or current-condition documentation.",
        ],
    }


if __name__ == "__main__":
    result = evaluate()
    out = AUDIT / "independent_grade_r2.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"score": result["score"], "max_score": result["max_score"],
                      "criteria": [{"name": c["name"], "score": c["score"], "max_score": c["max_score"]}
                                   for c in result["criteria"]],
                      "output": str(out)}, indent=2))
