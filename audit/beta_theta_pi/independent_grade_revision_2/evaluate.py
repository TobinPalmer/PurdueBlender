"""Exact-SHA independent reevaluation of the revised Beta Theta Pi asset.

Run this script in Blender against the named .blend. Visual assessment compares
the east/west and other saved views with official chapter photographs and GIS.
"""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / "modular" / "buildings" / "massing_beta_theta_pi_fid826.blend"
EXPECTED_SHA256 = "4E45D55F49DB9796F8C3780CD29AB83B3D27B4C3E1ABA6FD6140AFE3CD2455B1"
OUT = Path(__file__).resolve().parent

sha = hashlib.sha256(ASSET.read_bytes()).hexdigest().upper()
if sha != EXPECTED_SHA256:
    raise RuntimeError(f"Asset SHA mismatch: expected {EXPECTED_SHA256}, got {sha}")

scene = bpy.data.scenes.get("Building_massing_beta_theta_pi_fid826")
collection = bpy.data.collections.get("Asset_massing_beta_theta_pi_fid826")
if scene is None or collection is None:
    raise RuntimeError("Expected scene or exported collection is missing")
objects = list(collection.all_objects)
meshes = [o for o in objects if o.type == "MESH"]
materials = sorted({m.name for o in meshes for m in o.data.materials if m})
external_images = []
for img in bpy.data.images:
    if img.source == "FILE" and img.filepath:
        p = Path(bpy.path.abspath(img.filepath))
        if not p.exists():
            external_images.append({"name": img.name, "path": img.filepath})
points = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
bounds = [[float(min(p[i] for p in points)), float(max(p[i] for p in points))] for i in range(3)]
roof_names = [o.name for o in objects if "roof" in o.name.lower()]
central_bay = [o.name for o in objects if "Pale_bay" in o.name]
arched_features = [o.name for o in objects if "arched" in o.name.lower() or "Entry_arch" in o.name]

# AGENT.md rubric: five equally weighted categories; claims remain conservative
# where the photos do not establish surveyed elevations or facade bearing.
criteria = [
    {
        "name": "Correct identity and source-backed footprint",
        "score": 2.0,
        "max_score": 2.0,
        "evidence": "Purdue BuildingShapesZip4 FID 826 and both Purdue/official chapter address records identify Beta Theta Pi at 150 Littleton Street. The wall shell follows the official GIS polygon; the saved GIS/aerial overlay supports the property match.",
    },
    {
        "name": "Position, orientation, and scale/dimensions",
        "score": 1.7,
        "max_score": 2.0,
        "evidence": f"The project geographic transform and full GIS polygon are used without box rescaling. Evaluated asset bounds in Blender are {[[round(v,3) for v in axis] for axis in bounds]}. Aerial overlay supports plan placement, but the photo facade has no surveyed compass bearing and the roof/facade alignment to individual GIS edges is interpretive.",
    },
    {
        "name": "Evidence-backed height, floors, and roof form",
        "score": 0.8,
        "max_score": 2.0,
        "evidence": f"Three facade levels now match the official front photographs, and the housing directory reports four floors plus a basement; above-grade count remains an interpretation. Roof bands and the tower are now differentiated, but the east/west/aerial views still show oversized intersecting facets, abrupt roof seams, and exposed triangular wall-top areas. The roof silhouette/pitch does not yet read like the photo's discrete slate gables. The GIS height fields remain contradictory/unusable.",
    },
    {
        "name": "Facade, entrances, and distinctive architecture",
        "score": 1.35,
        "max_score": 2.0,
        "evidence": f"The revision adds the tall pale bay with three arched glazed levels, a separate central brick gable, and an arched stone entry with plaque, all recognizable in chapter photos 1, 11, 14, 15 and 16. Brick tone and pale stone/window trim are source-consistent. Several west/east windows still appear partly occluded by or set into roof planes, while secondary elevations use a repeated generic sash layout; exact facade bearing and openings remain unregistered to GIS.",
    },
    {
        "name": "Modular export, portability, and complete evidence",
        "score": 1.8,
        "max_score": 2.0,
        "evidence": f"Fresh-open check is this independent Blender 5.2.3 process: expected scene and collection loaded; {len(objects)} collection objects/{len(meshes)} meshes, five materials ({materials}), and no missing external image paths ({external_images}). The evidence record includes raw GIS, layer metadata, official chapter gallery and address sources, aerial overlay, source-derived decisions and uncertainties. No public interior plan is available, so the interior is correctly omitted but remains unmodeled.",
    },
]
score = round(sum(c["score"] for c in criteria), 2)
result = {
    "building": "Beta Theta Pi (Beta Mu Chapter)",
    "asset_path": "modular/buildings/massing_beta_theta_pi_fid826.blend",
    "asset_sha256": sha,
    "score": score,
    "max_score": 10.0,
    "passes": score >= 8.0,
    "criteria": criteria,
    "evidence": {
        "scene": scene.name,
        "collection": collection.name,
        "object_count": len(objects),
        "mesh_count": len(meshes),
        "bounds_world_m": bounds,
        "materials": materials,
        "missing_external_images": external_images,
        "roof_objects": roof_names,
        "central_bay_objects": central_bay,
        "arched_feature_objects": arched_features,
        "visual_references": [
            "audit/beta_theta_pi/preview_west.png",
            "audit/beta_theta_pi/preview_east.png",
            "audit/beta_theta_pi/preview_north.png",
            "audit/beta_theta_pi/preview_south.png",
            "audit/beta_theta_pi/preview_aerial.png",
            "audit/beta_theta_pi/sources/Beta-Mu-Chapter-House-1.jpg",
            "audit/beta_theta_pi/sources/Beta-Mu-Chapter-House-11.jpg",
            "audit/beta_theta_pi/sources/Beta-Mu-Chapter-House-14.jpg",
            "audit/beta_theta_pi/sources/Beta-Mu-Chapter-House-15.jpg",
            "audit/beta_theta_pi/sources/Beta-Mu-Chapter-House-16.jpg",
            "audit/beta_theta_pi/sources/gis_overlay_esri_aerial.jpg",
        ],
    },
    "findings": [
        "Rebuild the roof panels so they follow each concave GIS cross-section instead of spanning between only the global minimum and maximum X intersections; the current rendered roof still has bridged/overlapping facets and exposed wall-top triangles.",
        "Align upper-floor windows and the pale bay/portal to the roof eaves so they remain visible and do not intersect or disappear behind the roof surfaces.",
        "Retain the improved three-level central bay, central gable, and entry, while using additional source views to resolve roof bearings and hidden elevations.",
        "No reliable floor plan was found; interior remains unmodeled rather than invented.",
    ],
}
(OUT / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
lines = [
    "# Independent grade revision 2 — Beta Theta Pi",
    "",
    f"**Score: {score:.2f}/10 — {'PASS' if score >= 8.0 else 'BELOW 8.0'}**",
    f"**Reviewed asset SHA-256:** `{sha}`",
    "**Review:** Blender 5.2.3 fresh-open; east/west/north/south/aerial renders; official Beta Mu chapter photos 1, 11, 14, 15, 16; FID 826 GIS/aerial overlay.",
    "",
    "| Criterion | Score | Evidence and findings |",
    "|---|---:|---|",
]
for c in criteria:
    lines.append(f"| {c['name']} | {c['score']:.2f}/{c['max_score']:.0f} | {c['evidence']} |")
lines += ["", "## Required revisions", ""]
lines += [f"- {finding}" for finding in result["findings"]]
lines += ["", "## Detailed file inspection", "", f"- Scene: `{scene.name}`; exported collection: `{collection.name}`.", f"- Objects/meshes: {len(objects)}/{len(meshes)}; materials: {', '.join(materials)}.", f"- Missing external image dependencies: {len(external_images)}.", f"- Roof-named objects inspected: {', '.join(roof_names)}.", "- The identity and footprint are well supported. The score remains below threshold because roof geometry and roof-to-facade intersections are visibly inaccurate in the saved views.", ""]
(OUT / "grade_report.md").write_text("\n".join(lines), encoding="utf-8")
print(json.dumps({"score": score, "max_score": 10.0, "passes": score >= 8.0, "asset_sha256": sha, "criteria": criteria, "findings": result["findings"]}, indent=2))
