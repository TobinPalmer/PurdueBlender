"""Independent Beta Theta Pi review for the frozen asset revision.

Run with Blender 5.2 in background against the asset file. The rubric score
combines direct file checks with the documented side-by-side visual review of
the official chapter-house photographs and saved preview renders.
"""
import bpy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / "modular" / "buildings" / "massing_beta_theta_pi_fid826.blend"
EXPECTED_SHA256 = "1439047830952845050C68AD300C182151A7A3C6DF150C0B93A52BFBE73DD430"
OUT = Path(__file__).resolve().parent

sha = hashlib.sha256(ASSET.read_bytes()).hexdigest().upper()
if sha != EXPECTED_SHA256:
    raise RuntimeError(f"Asset changed during independent review: {sha}")

scene_name = "Building_massing_beta_theta_pi_fid826"
collection_name = "Asset_massing_beta_theta_pi_fid826"
scene = bpy.data.scenes.get(scene_name)
collection = bpy.data.collections.get(collection_name)
if scene is None or collection is None:
    raise RuntimeError("Expected standalone scene or asset collection is missing")

objects = list(collection.all_objects)
meshes = [o for o in objects if o.type == "MESH"]
materials = sorted({m.name for o in meshes for m in o.data.materials if m})
images = []
for image in bpy.data.images:
    if image.source == "FILE" and image.filepath:
        path = Path(bpy.path.abspath(image.filepath))
        if not path.exists():
            images.append({"name": image.name, "path": image.filepath, "missing": True})

mesh_bounds = []
for obj in meshes:
    for corner in obj.bound_box:
        p = obj.matrix_world @ __import__("mathutils").Vector(corner)
        mesh_bounds.append(tuple(float(v) for v in p))
bounds = [[min(p[i] for p in mesh_bounds), max(p[i] for p in mesh_bounds)] for i in range(3)]

# Scores follow AGENT.md's five equal-weight criteria. Visual findings below
# come from direct inspection of preview_west/east/north/south/aerial against
# Beta-Mu-Chapter-House-1.jpg and -11.jpg, not from mesh density.
criteria = [
    {
        "name": "Correct identity and source-backed footprint",
        "score": 2.0,
        "max_score": 2.0,
        "evidence": "Purdue GIS FID 826, the Purdue Beta Mu page, and BoilerLink all identify Beta Theta Pi at 150 Littleton Street. The shell perimeter is built from the FID 826 ring and the saved aerial overlay aligns it to the roof footprint.",
    },
    {
        "name": "Position, orientation, and scale/dimensions",
        "score": 1.6,
        "max_score": 2.0,
        "evidence": f"Campus coordinates use the documented local conversion; observed bounds are {[[round(x, 3) for x in axis] for axis in bounds]}. GIS controls plan position and dimensions. The photo set does not independently establish the photographed facade's bearing or all elevations, so facade assignment/orientation remains partly interpreted.",
    },
    {
        "name": "Evidence-backed height, floors, and roof form",
        "score": 0.55,
        "max_score": 2.0,
        "evidence": "Wall height and roof ridge are estimates. The official exterior shows a taller, articulated roof and multiple roof masses; the saved model's continuous roof reads as one broad, jagged slab from several sides, with an isolated triangular entrance gable. The two-storey wall treatment also underrepresents the photographed central bay's vertical, multi-level composition. GIS level/extrusion fields are explicitly contradictory, so they do not support the chosen height.",
    },
    {
        "name": "Facade, entrances, and distinctive architecture",
        "score": 0.75,
        "max_score": 2.0,
        "evidence": "Warm red-brown brick and pale window trim are source-consistent. However, the photographed front is distinguished by a tall pale central bay with vertically stacked/arched glazing and a more elaborate entry; the model substitutes a small triangular gable, simple door, and repeated generic sash windows. The entrance and facade rhythm therefore do not yet match the strongest reference view.",
    },
    {
        "name": "Modular export, portability, and complete evidence",
        "score": 1.85,
        "max_score": 2.0,
        "evidence": f"Expected scene/collection exist; {len(objects)} collection objects and {len(meshes)} meshes were read. Materials are {materials}; missing external file images: {images}. The audit contains raw GIS, chapter/address sources, photographs, aerial overlay, uncertainty notes, and five inspection renders. No interior plan was available; omitting a speculative interior is appropriate, but interior coverage remains absent.",
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
        "materials": materials,
        "missing_external_images": images,
        "mesh_bounds_world_m": bounds,
        "visual_references": [
            "audit/beta_theta_pi/sources/Beta-Mu-Chapter-House-1.jpg",
            "audit/beta_theta_pi/sources/Beta-Mu-Chapter-House-11.jpg",
            "audit/beta_theta_pi/preview_west.png",
            "audit/beta_theta_pi/preview_east.png",
            "audit/beta_theta_pi/preview_north.png",
            "audit/beta_theta_pi/preview_south.png",
            "audit/beta_theta_pi/preview_aerial.png",
        ],
    },
    "findings": [
        "Replace the continuous jagged roof cap with roof masses that follow the visible multi-wing roof silhouette.",
        "Reconstruct the distinctive pale central bay and its vertically stacked/arched glazing from the official exterior photo.",
        "Rework the entrance and upper facade composition; the current small triangular gable does not match the reference facade.",
        "Use additional dated/orthogonal sources before claiming roof, height, facade bearing, or hidden elevations are verified.",
        "No registered interior plan was found; the interior remains unmodeled and unverified.",
    ],
}
(OUT / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

lines = [
    "# Independent grade — Beta Theta Pi",
    "",
    f"**Score: {score:.2f}/10 — {'PASS' if score >= 8 else 'BELOW 8.0'}**",
    f"**Reviewed asset SHA-256:** `{sha}`",
    "**Review method:** Fresh-open in Blender plus direct visual comparison of all five asset previews to the official Beta Mu chapter-house gallery and source GIS/aerial evidence.",
    "",
    "| Criterion | Score | Findings |",
    "|---|---:|---|",
]
for c in criteria:
    lines.append(f"| {c['name']} | {c['score']:.2f}/{c['max_score']:.0f} | {c['evidence']} |")
lines += ["", "## Required revisions", ""]
lines += [f"- {finding}" for finding in result["findings"]]
lines += ["", "## Evidence checked", "", "The saved review views are `preview_west.png`, `preview_east.png`, `preview_north.png`, `preview_south.png`, and `preview_aerial.png`. Source comparisons used official chapter gallery images 1 and 11, FID 826 GIS snapshots, and the Esri aerial overlay.", ""]
(OUT / "grade_report.md").write_text("\n".join(lines), encoding="utf-8")
print(json.dumps({"score": score, "max_score": 10.0, "passes": score >= 8.0, "asset_sha256": sha, "criteria": criteria, "findings": result["findings"]}, indent=2))
