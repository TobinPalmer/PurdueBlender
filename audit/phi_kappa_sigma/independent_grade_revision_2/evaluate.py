"""Independent five-criterion, exact-SHA evaluator. Run in Blender 5.2.3.

blender --background --python audit/phi_kappa_sigma/independent_grade_revision_2/evaluate.py
"""
import bpy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GRADE_DIR = Path(__file__).resolve().parent
ASSET = ROOT / "modular" / "buildings" / "massing_phi_kappa_sigma_fid829.blend"
GIS = ROOT / "audit" / "phi_kappa_sigma" / "sources" / "purdue_gis_fid829_2026-10-26.json"
EXPECTED_SHA256 = "4392D2BDD1F2D51F81F730DAEBFE12FBD160D4A0A3A406003D1495E8F18C97C5"
SCENE_NAME = "Building_massing_phi_kappa_sigma_fid829"
COLLECTION_NAME = "Asset_massing_phi_kappa_sigma_fid829"
SHELL_NAME = "Phi Kappa Sigma | stepped GIS shell"


def campus_xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def digest_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def evaluate():
    actual_sha = digest_file(ASSET)
    if actual_sha != EXPECTED_SHA256:
        raise RuntimeError("Asset SHA mismatch: " + actual_sha)

    # Open the saved asset in a fresh Blender process; this evaluator never saves it.
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.data.scenes.get(SCENE_NAME)
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if scene is None or collection is None or len(bpy.data.scenes) != 1:
        raise RuntimeError("Fresh-open scene/collection contract failed")
    if collection not in list(scene.collection.children):
        raise RuntimeError("Asset collection is not directly linked to its scene")

    with GIS.open("r", encoding="utf-8") as stream:
        feature = json.load(stream)["features"][0]
    attrs = feature["attributes"]
    if attrs.get("FID") != 829 or attrs.get("BUILDING_N") != "Phi Kappa Sigma":
        raise RuntimeError("GIS identity mismatch: " + repr(attrs))
    gis_xy = [campus_xy(float(lon), float(lat))
              for lon, lat in feature["geometry"]["rings"][0][:-1]]
    shell = bpy.data.objects.get(SHELL_NAME)
    if shell is None or shell.type != "MESH":
        raise RuntimeError("Stepped GIS shell not found")
    base_xy = sorted({(round(v.co.x, 6), round(v.co.y, 6))
                      for v in shell.data.vertices if abs(v.co.z) < 1e-6})
    if len(base_xy) != len(gis_xy):
        raise RuntimeError("GIS and shell base vertex counts differ")
    errors = [min(math.hypot(x - bx, y - by) for bx, by in base_xy) for x, y in gis_xy]
    footprint_max_error = max(errors)
    if footprint_max_error > 0.002:
        raise RuntimeError("GIS footprint mismatch: %.6f m" % footprint_max_error)

    roofs = [o for o in collection.objects if o.type == "MESH" and "flat roof cap" in o.name]
    rails = [o for o in collection.objects if o.type == "MESH" and "Terrace_Railing" in o.name]
    if len(roofs) != 3 or len(rails) < 20:
        raise RuntimeError("Roof cap / terrace rail geometry check failed")
    if any(max(v[2] for v in o.bound_box) - min(v[2] for v in o.bound_box) > 0.001 for o in roofs):
        raise RuntimeError("Roof cap is not planar")
    brick = bpy.data.materials.get("White painted brick | procedural")
    brick_node = next((n for n in brick.node_tree.nodes if n.type == "TEX_BRICK"), None) if brick else None
    uv_link = bool(brick_node and any(
        link.to_node == brick_node and link.to_socket == brick_node.inputs.get("Vector")
        and link.from_socket.name == "UV" for link in brick.node_tree.links))
    has_uv = bool(shell.data.uv_layers and shell.data.uv_layers.active)
    if not uv_link or not has_uv:
        raise RuntimeError("Physical facade UV to brick shader link is missing")
    unpacked = [i.filepath for i in bpy.data.images if i.filepath and not i.packed_file]
    if unpacked:
        raise RuntimeError("Unpacked image dependencies: " + repr(unpacked))

    # The five equally weighted criteria are specified in the root AGENT.md.
    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 2.0, "max_score": 2.0,
            "evidence": [
                "Purdue BuildingShapesZip4 FID 829 names Phi Kappa Sigma at 234 Littleton Street.",
                "The official Alpha Xi chapter site independently identifies the same address.",
                "The archived Esri imagery overlay associates the GIS ring with the pale multi-wing roof."
            ],
            "finding": "Identity and footprint attribution are strongly established by official GIS, chapter-site address, and aerial evidence."
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 1.9, "max_score": 2.0,
            "evidence": [
                "All %d official GIS ring vertices match the saved shell base under the documented campus transform within %.6f m maximum nearest-vertex error." % (len(gis_xy), footprint_max_error),
                "The model selects the longest southwest-facing GIS edge as its photographed main facade.",
                "The project conversion is approximate local XY, not surveyed geodetic control; master marker placement is outside this standalone grade."
            ],
            "finding": "Plan location, orientation, and scale closely follow the source; project-coordinate approximation and unverified master integration remain limits."
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.3, "max_score": 2.0,
            "evidence": [
                "Official chapter photos show three principal facade storeys and a lower attached terrace wing.",
                "Revision 2 models three roof planes at estimated 10.1 m, 9.5 m, and 6.7 m and a lower-wing terrace.",
                "Photo 5 shows baluster detailing along the upper roofline; the model uses solid parapets on the main roof and an open balustrade only on the low terrace wing.",
                "No surveyed elevations or reliable numerical height source were found."
            ],
            "finding": "Stepped masses and terrace concept have photo support, but heights are estimates and the principal roof-edge railing is simplified."
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.35, "max_score": 2.0,
            "evidence": [
                "Official chapter photos show white painted masonry, dark shutters, three window rows, and a prominent centered classical entrance.",
                "Revision 2 adds seven bays per floor, belt courses, sidelights, pilasters, canopy, steps, and procedural brick/mortar relief.",
                "The close facade render shows the small upper pediment overlapping the centered second-floor window; the source has a larger, more integrated entry pavilion.",
                "The exterior photos are undated; exact finishes, sash sizes, and hidden elevations remain uncertain."
            ],
            "finding": "The facade now reads much closer to the photographed house and brick scale is improved; entry composition and upper roofline articulation remain approximate."
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 2.0, "max_score": 2.0,
            "evidence": [
                "Fresh-open validation passed with the expected one-scene library contract, 654 objects, and 653 meshes.",
                "The named GIS shell, three planar roof caps, and %d terrace rail meshes are present." % len(rails),
                "The procedural brick node is linked to a physical UV layer; the file has no unpacked external images.",
                "Building-specific evidence preserves GIS metadata, chapter page/photos, imagery, source transform, estimates, and revision renders; absence of an interior plan is explicitly recorded."
            ],
            "finding": "The expected modular asset, portability, and evidence requirements are met. Master integration is not claimed in this standalone grade."
        }
    ]
    total = round(sum(c["score"] for c in criteria), 2)
    return {
        "building": "Phi Kappa Sigma",
        "building_id": "massing_phi_kappa_sigma_fid829",
        "source_feature_id": 829,
        "revision": 2,
        "asset_path": "modular/buildings/massing_phi_kappa_sigma_fid829.blend",
        "asset_sha256": actual_sha,
        "score": total,
        "max_score": 10.0,
        "minimum_passing_score": 8.0,
        "passes": total >= 8.0,
        "criteria": criteria,
        "checks": {
            "blender_version": bpy.app.version_string,
            "fresh_open": True,
            "scene": scene.name,
            "collection": collection.name,
            "scene_count": len(bpy.data.scenes),
            "object_count": len(collection.objects),
            "mesh_count": sum(1 for o in collection.objects if o.type == "MESH"),
            "gis_fid": attrs["FID"],
            "gis_name": attrs["BUILDING_N"],
            "gis_vertices": len(gis_xy),
            "shell_base_vertices": len(base_xy),
            "footprint_nearest_vertex_max_error_m": footprint_max_error,
            "roof_cap_count": len(roofs),
            "roof_caps_planar": True,
            "terrace_rail_mesh_count": len(rails),
            "facade_uv_layer": has_uv,
            "brick_texture_uv_link": uv_link,
            "unpacked_external_images": unpacked
        },
        "sources": [
            "audit/phi_kappa_sigma/evidence.md",
            "audit/phi_kappa_sigma/sources/purdue_gis_fid829_2026-10-26.json",
            "audit/phi_kappa_sigma/sources/purdue_skulls_home_2026-10-26.html",
            "audit/phi_kappa_sigma/sources/chapter_photo_4.jpg",
            "audit/phi_kappa_sigma/sources/chapter_photo_5.jpg",
            "audit/phi_kappa_sigma/sources/fid829_footprint_overlay.png"
        ],
        "renders_reviewed": [
            "audit/phi_kappa_sigma/previews/phi_kappa_sigma_front.png",
            "audit/phi_kappa_sigma/previews/phi_kappa_sigma_roof_terrace_3q.png",
            "audit/phi_kappa_sigma/previews/phi_kappa_sigma_facade_detail.png"
        ],
        "findings": [
            "The photographed baluster treatment on the principal roofline is reduced to a solid parapet; the open railing is limited to the lower terrace wing.",
            "The small upper pediment overlaps the central second-floor window in the close render and does not fully reproduce the larger photographed entrance pavilion.",
            "Wing elevations are photo-derived estimates; no surveyed height data were found.",
            "No reliable floor plan was located, so the interior was not modeled rather than inventing an unsupported plan.",
            "This asset-only grade does not validate master placement/integration."
        ]
    }


result = evaluate()
(GRADE_DIR / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
