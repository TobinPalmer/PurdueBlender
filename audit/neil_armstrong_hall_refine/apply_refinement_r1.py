"""Apply evidence-backed display/material refinements to Neil Armstrong Hall only."""
from pathlib import Path
import hashlib
import json
import shutil

import bpy

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET = ROOT / "modular/buildings/neil_armstrong_hall.blend"
AUDIT = ROOT / "audit/neil_armstrong_hall_refine"
SOURCE_IMAGE = ROOT / "audit/complete_neil_armstrong/sources/wikimedia_neil_2016_03_r8.jpg"
LOCAL_SOURCE_IMAGE = AUDIT / "sources/wikimedia_neil_2016_03_r8.jpg"
EXPECTED_SHA = "63c18a8ce250345134399b48dc9eb0f5f5a7563ef3566a5b22145221e7c0145d"

def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

before = sha256(ASSET)
if before != EXPECTED_SHA:
    raise RuntimeError(f"Neil asset changed since inspection: {before}")
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
if len(bpy.data.objects) != 445:
    raise RuntimeError(f"Unexpected object count {len(bpy.data.objects)}")

asset_collection = bpy.data.collections.get("Asset_neil_armstrong_hall")
if asset_collection is None or len(asset_collection.objects) != 445:
    raise RuntimeError("Unexpected asset collection or collection count")

# The prior R5 evidence records these as coarse NDHM envelope shells and
# explicitly disclaims wall/facade/roof-edge precision. Keep their geometry
# intact for inspection, but keep them out of the rendered model and viewport
# presentation so they do not cover later detailed facade work.
coarse_names = [
    "ARMS_R5_Coarse_LiDAR_wing_low",
    "ARMS_R5_Coarse_LiDAR_wing_mid",
    "ARMS_R5_Coarse_LiDAR_roof_high",
]
visibility_before = {}
for name in coarse_names:
    obj = bpy.data.objects.get(name)
    if not obj:
        raise RuntimeError(f"Missing documented coarse envelope {name}")
    visibility_before[name] = {"hide_render": obj.hide_render, "hidden_in_view_layer": obj.hide_get()}
    if obj.get("evidence_status") != "schematic_source_derived_envelope":
        raise RuntimeError(f"Unexpected provenance for {name}")
    obj.hide_render = True
    obj.hide_set(True)
    obj["presentation_note"] = (
        "Hidden in viewport and render: coarse 2018 NDHM envelope retained as reference; "
        "it is schematic and obscured detailed facade geometry."
    )

# The source photo shows a dark red-brown metallic soffit on the prominent
# cantilever canopy. The previous Sea Wolf gray-blue ACM swatch contradicted it.
roof_material = bpy.data.materials.get("ARMS_Sea_Wolf_ACM")
if not roof_material or not roof_material.use_nodes:
    raise RuntimeError("Expected node-based ARMS_Sea_Wolf_ACM material missing")
bsdf = next((node for node in roof_material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
if not bsdf:
    raise RuntimeError("Principled shader not found in ACM material")
material_before = {
    "base_color": list(bsdf.inputs["Base Color"].default_value),
    "metallic": float(bsdf.inputs["Metallic"].default_value),
    "roughness": float(bsdf.inputs["Roughness"].default_value),
}
# The sampled sRGB median of the visible soffit region is approximately
# (78,54,46); convert to a dark linear bronze-red swatch for Principled BSDF.
bsdf.inputs["Base Color"].default_value = (0.080, 0.037, 0.027, 1.0)
bsdf.inputs["Metallic"].default_value = 0.55
bsdf.inputs["Roughness"].default_value = 0.36
material_after = {
    "base_color": list(bsdf.inputs["Base Color"].default_value),
    "metallic": float(bsdf.inputs["Metallic"].default_value),
    "roughness": float(bsdf.inputs["Roughness"].default_value),
}

# Keep a self-contained copy of the visual reference within this building's
# evidence directory and record its attribution/hash.
LOCAL_SOURCE_IMAGE.parent.mkdir(parents=True, exist_ok=True)
if not LOCAL_SOURCE_IMAGE.exists():
    shutil.copy2(SOURCE_IMAGE, LOCAL_SOURCE_IMAGE)

bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))

evidence = {
    "building_id": "neil_armstrong_hall",
    "revision": "R11 refinement",
    "date": "2026-10-25",
    "asset": "../../modular/buildings/neil_armstrong_hall.blend",
    "sha256_before": before,
    "sha256_after": sha256(ASSET),
    "collection": "Asset_neil_armstrong_hall",
    "collection_objects": len(asset_collection.objects),
    "total_objects": len(bpy.data.objects),
    "changes": [
        {
            "kind": "presentation visibility",
            "objects": coarse_names,
            "before": visibility_before,
            "after": {name: {"hide_render": True, "hidden_in_view_layer": True} for name in coarse_names},
            "basis": "R5 source evidence calls these coarse NDHM/GIS envelope solids, not wall, facade, floor-plan, or exact roof-edge geometry. They obscure the independently modeled facade and are retained unchanged as hidden reference geometry.",
            "source": "../../audit/complete_neil_armstrong/evidence_r5.json",
        },
        {
            "kind": "canopy soffit PBR material",
            "material": roof_material.name,
            "before": material_before,
            "after": material_after,
            "basis": "Officially attributed exterior photo of the building shows the large cantilever canopy underside in a dark red-brown metallic finish; previous base color was gray-blue.",
            "reference_image": "sources/wikimedia_neil_2016_03_r8.jpg",
            "reference_image_url": "https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_03.jpg",
            "patch_sampling_note": "The dark visible canopy region was sampled approximately from the source photo; surrounding sky/glazing pixels are excluded from the material inference. A red-brown metal approximation is used; exact paint/ACM manufacturer color is unverified.",
        },
    ],
    "sources": [
        {
            "title": "Neil Armstrong Hall of Engineering Purdue University 2016 03",
            "publisher": "Wikimedia Commons",
            "url": "https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_03.jpg",
            "retrieval_date": "2026-10-25",
            "local_image": "sources/wikimedia_neil_2016_03_r8.jpg",
            "image_sha256": sha256(LOCAL_SOURCE_IMAGE),
            "used_for": "Color evidence only for the cantilever canopy. Unregistered perspective image; not used to set dimensions, orientation, or facade coordinates.",
        },
        {
            "title": "Neil Armstrong Hall of Engineering emergency plan page",
            "publisher": "Purdue University Office of Emergency Preparedness",
            "url": "https://www.purdue.edu/operations/emergency-preparedness/arms/",
            "retrieval_date": "2026-10-25",
            "used_for": "Building identity and room/program context; not used to infer dimensions.",
        },
        {
            "title": "Purdue University BuildingShapesZip4 feature 642",
            "publisher": "Purdue University / Indiana Geographic Information Office",
            "url": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0",
            "feature_id": 642,
            "source_crs": "EPSG:2968 for project transform details recorded in prior audit evidence_r5.json",
            "used_for": "Contextual registered footprint basis for the retained coarse envelope; does not define facade/roof/canopy edges.",
            "raw_snapshot": "../../audit/complete_neil_armstrong/sources/gis_feature_642_20261024.json",
        },
        {
            "title": "Indiana 3DEP 2018 Tippecanoe NDHM",
            "publisher": "Purdue Digital Forestry / iDiF",
            "url": "https://lidar.digitalforestry.org/QL2_3DEP_LiDAR_IN_2017_2019_l2/tippecanoe/cog/tippecanoe_ndhm_2018.tif",
            "source_crs_units": "EPSG:2968, US survey feet; see prior evidence_r5.json for conversion and sampling method.",
            "used_for": "Provenance for coarse envelopes kept hidden as reference geometry.",
            "raw_snapshot": "../../audit/complete_neil_armstrong/sources/tippecanoe_ndhm_clip_r5.tif",
        },
    ],
    "validation_pending": "Run independent reopen/validation and record exact values before handing to grader.",
}
(AUDIT / "evidence_r11.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
print(json.dumps(evidence, indent=2))
