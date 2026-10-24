"""Attach R10 lidar provenance and limits to the existing Math roof objects."""
import bpy
from pathlib import Path

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = ROOT / "modular/buildings/math_sciences.blend"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset = bpy.data.collections["Asset_math_sciences"]

source = "Indiana GIO 2018 3DEP 5-ft DSM + 2.5-ft bare-earth DTM; GIS FID 227 MATH footprint"
summary = (
    "Raster DSM-minus-DTM roof/footprint height percentiles: p50 36.92m, p90 40.25m, "
    "p95 40.43m, max 40.86m above nearby terrain. This 2018 5-ft first-surface grid "
    "is not a measured architectural elevation. Footprint includes low passage/edge cells; "
    "parapets and equipment influence upper cells. It cannot resolve exact story heights, "
    "mast, parapet edges, or the full penthouse plan."
)
for name in (
    "MATH_Corrected_GIS_Roof_Slab",
    "MATH_Rooftop_Penthouse_Base",
    "MATH_Rooftop_Penthouse_Copings",
):
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"Missing expected roof object {name}")
    obj["r10_surface_source"] = source
    obj["r10_surface_height_evidence"] = summary
    obj["r10_model_vs_raster_note"] = (
        "Existing modeled bounds are retained for R10. The raster suggests a discrepancy; "
        "no published, dimensioned MATH elevation supports assigning it to the roof slab, "
        "upper occupied floor, or penthouse, so no geometry was moved."
    )
asset["r10_height_evidence_method"] = "GIS FID 227 polygon mask over Indiana GIO 2018 3DEP DSM minus corresponding DTM; 5-ft DSM cells"
asset["r10_height_evidence_note"] = summary
asset["r10_height_geometry_changed"] = False
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print("R10 source annotations saved; no geometry changed")
