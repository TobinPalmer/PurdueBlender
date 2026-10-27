"""Independent read-only audit of Alpha Sigma Phi's source Blender asset."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / "modular/buildings/massing_house_301841603_654031c.blend"
GIS = ROOT / "audit/alpha_sigma_phi/sources/arcgis_fid763_feature.json"
OUT = Path(__file__).resolve().parent / "result.json"

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene_name = "Building_massing_house_301841603_654031c"
collection_name = "Asset_massing_house_301841603_654031c"
root_name = "House_301841603"
scene = bpy.data.scenes.get(scene_name)
asset = bpy.data.collections.get(collection_name)
shell = bpy.data.objects.get(root_name)
assert scene is not None and asset is not None and shell is not None

src = json.loads(GIS.read_text(encoding="utf-8"))["features"][0]
ring = src["geometry"]["rings"][0][:-1]
src_xy = [((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
           (lat - 40.4274) * 111040.0) for lon, lat in ring]
model_xy = sorted({(round((shell.matrix_world @ v.co).x, 6),
                    round((shell.matrix_world @ v.co).y, 6))
                   for v in shell.data.vertices})
errors = [min(math.hypot(x - mx, y - my) for mx, my in model_xy) for x, y in src_xy]
area = abs(sum(src_xy[i][0] * src_xy[(i + 1) % len(src_xy)][1] -
               src_xy[(i + 1) % len(src_xy)][0] * src_xy[i][1]
               for i in range(len(src_xy))) / 2)

objects = list(asset.all_objects)
mesh_objects = [o for o in objects if o.type == "MESH"]
world_points = [o.matrix_world @ v.co for o in mesh_objects for v in o.data.vertices]
bounds = [[min(getattr(v, axis) for v in world_points),
           max(getattr(v, axis) for v in world_points)] for axis in ("x", "y", "z")]
materials = sorted({m.name for o in mesh_objects for m in o.data.materials if m})
material_types = {}
for name in materials:
    mat = bpy.data.materials.get(name)
    material_types[name] = [n.type for n in mat.node_tree.nodes] if mat and mat.use_nodes else []

result = {
    "asset": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
    "scene": scene.name,
    "collection": asset.name,
    "root_object": shell.name,
    "fid": src["attributes"]["FID"],
    "address": src["attributes"]["ADDRESS"],
    "footprint_vertex_count": len(ring),
    "model_unique_footprint_vertices": len(model_xy),
    "max_vertex_error_m": round(max(errors), 6),
    "projected_footprint_area_m2": round(area, 3),
    "world_bounds_m": [[round(a, 3), round(b, 3)] for a, b in bounds],
    "asset_object_count": len(objects),
    "mesh_object_count": len(mesh_objects),
    "materials": materials,
    "material_nodes": material_types,
    "validation": {
        "stable_identity": scene.get("building_id") == "massing_house_301841603_654031c",
        "gis_footprint_match": len(ring) == len(model_xy) and max(errors) < 0.001,
        "source_height_conflict": {
            "extrution_attribute": src["attributes"].get("Extrution"),
            "num_levels": src["attributes"].get("NUM_LEVELS"),
            "count_of_floors": src["attributes"].get("CountOfFLO"),
            "unit_documented": False,
        },
        "public_floor_plan_available": False,
        "direct_target_facade_reference_available": False,
        "builder_fresh_open_record": "audit/alpha_sigma_phi/fresh_open_validation.json",
    },
    "review_evidence": {
        "exterior_preview": "audit/alpha_sigma_phi/previews/alpha_sigma_phi_exterior.png",
        "interior_cutaway_preview": "audit/alpha_sigma_phi/previews/alpha_sigma_phi_interior_cutaway.png",
        "GIS_overlay": "audit/alpha_sigma_phi/sources/esri_world_imagery_fid763_footprint_overlay.png",
        "chapter_address_and_history": "https://img1.wsimg.com/blobby/go/f462eca5-24f6-4531-81f7-6819824ee6a1/CHAPTER%20HISTORY%20-%20ALPHAs.pdf",
        "Purdue_archived_fraternity_row_photo_index": "https://collections.lib.purdue.edu/pupindex/search.php?fq=PublicationYear%3A%221968%22+AND+subjectStr%3A%22Fraternities%22&q=Fraternities&qtype=SubjectHeading&submit=submit",
        "current_Google_Street_View_pano": "https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=40.43505,-86.92572",
    },
}

def evaluate():
    """Return an evidence-based 0–10 grade using the repository's 5 criteria."""
    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 2.0, "max_score": 2.0,
            "evidence": "Purdue GIS FID 763 identifies Alpha Sigma Phi at 951 David Ross Rd; independent vertex comparison finds 8/8 GIS vertices represented, with max error 0.000062 m. The aerial overlay shows the ring following the L-shaped roof.",
            "finding": "Pass. Building identity and plan footprint are directly supported.",
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 2.0, "max_score": 2.0,
            "evidence": "Reopened asset has expected stable scene, collection, root, zero root translation, and campus-coordinate bounds matching the GIS ring. The two principal wings are aligned with the source polygon.",
            "finding": "Pass for plan position/orientation/footprint scale. The building height is scored separately because source height metadata is contradictory.",
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 0.5, "max_score": 2.0,
            "evidence": "Aerial evidence supports the L-shaped roof plan but not the roof profile. The modeled 10.363 m height comes from interpreting GIS `Extrution=34` as feet; unit is undocumented. GIS also lists NUM_LEVELS=1 and CountOfFLO=1, while the model has three window levels.",
            "finding": "Major unresolved contradiction. The flat roof is plausible from the aerial but not evidenced as the actual roof form; height and story count remain estimates.",
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 0.75, "max_score": 2.0,
            "evidence": "The model has brick, repeated windows, and a basic entrance canopy. The chapter history confirms the current address and 1966 move-in, but available Street View is partly obscured and is not a decisive elevation of the house; exact brick color, fenestration, and entry location are not verified.",
            "finding": "Only generic residential character is supported. Current render shows a simple dark-brick box, evenly repeated windows, and an indistinct entry; distinctive facade features are missing or unverified.",
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 2.0, "max_score": 2.0,
            "evidence": "The expected .blend path reopens with the expected scene, collection, and root. 851 mesh objects are contained in the building asset. All nine assigned materials are node-based; brick uses a procedural shader, with no external image dependency observed. Source snapshots, provenance, fresh-open record, and exterior/interior previews are present.",
            "finding": "Pass for source asset packaging and evidence completeness. Interior remains clearly labeled schematic; no public floor plan was found.",
        },
    ]
    score = round(sum(item["score"] for item in criteria), 2)
    return {
        **result,
        "score": score,
        "max_score": 10,
        "passes_8_threshold": score >= 8,
        "criteria": criteria,
        "evidence": [
            "Independent Blender 5.2.3 fresh-open inspection in this evaluator.",
            "Purdue ArcGIS FID 763 source snapshot and official campus footprint.",
            "Esri World Imagery footprint overlay saved with the builder's evidence.",
            "Chapter-hosted history PDF confirms Alpha Pi address/history.",
            "Google Street View pano and Purdue archive photo index were inspected; neither supplied a clear, target-facing contemporary elevation in the saved evidence.",
            "Exterior and interior cutaway renders inspected directly.",
        ],
        "findings": [
            "Excellent source-backed footprint; keep it unchanged.",
            "Resolve floor-count/height conflict with a direct target-facing elevation, measured imagery, or reliable Purdue plan. Do not infer GIS Extrution units without evidence.",
            "Rework roof silhouette and window/entrance placement only when supported by a target-specific reference; current facade is generic and too weakly verified.",
            "Improve the interior cutaway presentation: brighter, near-vertical camera, legible rooms/furnishings, and less shadow obstruction. Any room plan remains illustrative until a real plan is found.",
            "The interior and several facade choices are estimates; they should not be described as verified architectural facts.",
        ],
    }

graded = evaluate()
OUT.write_text(json.dumps(graded, indent=2), encoding="utf-8")
print(json.dumps({"score": graded["score"], "max_score": graded["max_score"],
                  "criteria": graded["criteria"], "evidence": graded["evidence"],
                  "findings": graded["findings"]}, indent=2))
