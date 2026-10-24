"""Align the documented third-floor Math library/interior to the modeled F03 slab.

This changes only the standalone Math Sciences asset. The 2022 Purdue Board
plan labels the library renovation as third floor. The saved library finish was
at z=10.62 m, while the asset's estimated F03 slab top is z=6.58 m. Story
spacing remains estimated; this is an internal story-index correction, not a
surveyed elevation claim.
"""

import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = ROOT / "modular/buildings/math_sciences.blend"
OUT = ROOT / "audit/batch3_math/round8_vertical_alignment.json"
FLOOR_FINISH_TOP_M = 6.58
LIBRARY_FINISH_TOP_BEFORE_M = 10.645
DZ_M = FLOOR_FINISH_TOP_M - LIBRARY_FINISH_TOP_BEFORE_M

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
library = bpy.data.collections.get("MATH_Library_2026")
floors = bpy.data.collections.get("MATH_Floors_2026")
export = bpy.data.collections.get("Asset_math_sciences")
if library is None or floors is None or export is None:
    raise RuntimeError("Expected Math Sciences export/interior/floor collections are missing")

targets = {o.name: o for o in library.all_objects}
targets.update({o.name: o for o in export.all_objects if o.name.startswith("MATH_Lib_")})
for o in floors.all_objects:
    if o.name.startswith("MATH_2026_Third_Floor_"):
        targets[o.name] = o
if not targets:
    raise RuntimeError("No source-backed third-floor interior objects were found")

marked = [o for o in targets.values() if "r8_vertical_alignment_dz_m" in o]
if marked and len(marked) != len(targets):
    raise RuntimeError("Partial round-eight correction detected; refusing a second partial move")
if not marked:
    for obj in targets.values():
        obj.location.z += DZ_M
        obj["r8_vertical_alignment_dz_m"] = DZ_M
        obj["r8_vertical_alignment_basis"] = (
            "2022-09-28 Purdue Board of Trustees plan labels the renovation area third floor; "
            "aligned to modeled MATH_2026_Typical_Floor_03 slab top. Absolute story elevations "
            "and floor spacing remain estimates."
        )

bpy.context.view_layer.update()

# The 2022 third-floor plan shows the library zone continuing south into hall
# 311 and the elevator core. The old carpet inlay stopped at the library edge;
# add a modest, clearly tagged connector to close that documented route. The
# corridor width and edge alignment are visual estimates because the plan is not
# dimensioned for this aisle.
connector = bpy.data.objects.get("MATH_2026_Third_Floor_Core_Connector")
if connector is None:
    cx, cy, cz = -0.1, 3.10, 6.591
    sx, sy, sz = 1.25, 15.62, 0.018
    verts = [
        (cx - sx/2, cy - sy/2, cz - sz/2),
        (cx + sx/2, cy - sy/2, cz - sz/2),
        (cx + sx/2, cy + sy/2, cz - sz/2),
        (cx - sx/2, cy + sy/2, cz - sz/2),
        (cx - sx/2, cy - sy/2, cz + sz/2),
        (cx + sx/2, cy - sy/2, cz + sz/2),
        (cx + sx/2, cy + sy/2, cz + sz/2),
        (cx - sx/2, cy + sy/2, cz + sz/2),
    ]
    mesh = bpy.data.meshes.new("MATH_2026_Third_Floor_Core_Connector_Mesh")
    mesh.from_pydata(verts, [], [
        (0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
        (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
    ])
    aisle = bpy.data.materials.get("MATH_2026_Library_Aisle_Carpet")
    if aisle is None:
        raise RuntimeError("Expected source-aligned library aisle material is missing")
    mesh.materials.append(aisle)
    connector = bpy.data.objects.new("MATH_2026_Third_Floor_Core_Connector", mesh)
    library.objects.link(connector)
    connector["r8_vertical_alignment_dz_m"] = 0.0
    connector["r8_vertical_alignment_basis"] = "Created at the corrected F03 finish elevation."
    connector["source_status"] = (
        "Plan-supported connection from the third-floor library zone south through hall 311 "
        "to the elevator core, based on the 2022 Purdue Board of Trustees plan. The plan is "
        "not dimensioned for this route; 1.25 m aisle width and exact centerline are inferred."
    )
targets[connector.name] = connector

bpy.context.view_layer.update()

floor3 = bpy.data.objects.get("MATH_2026_Typical_Floor_03")
floor = bpy.data.objects.get("MATH_Lib_Floor_Terrazzo")
stair = bpy.data.objects.get("MATH_2026_Third_Floor_Stair_Treads")
elevator = bpy.data.objects.get("MATH_2026_Third_Floor_Elevator_Doors")
if any(o is None for o in (floor3, floor, stair, elevator)):
    raise RuntimeError("Expected F03 slab, library floor, stairs, or elevator doors are missing")

def world_z_bounds(obj):
    return [
        min((obj.matrix_world @ Vector(c)).z for c in obj.bound_box),
        max((obj.matrix_world @ Vector(c)).z for c in obj.bound_box),
    ]

after_bounds = {
    obj.name: [round(v, 4) for v in world_z_bounds(obj)]
    for obj in (floor3, floor, stair, elevator)
}
# Save the standalone source library only. Never load or save the campus master.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
report = {
    "date": "2026-10-24",
    "asset": "modular/buildings/math_sciences.blend",
    "edited_master": False,
    "basis": "2022-09-28 Purdue Board of Trustees third-floor library renovation plan plus modeled F03 slab",
    "source_url": "https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/Libraries%20Study%20Space%20Reno.pdf",
    "objects_aligned": len(targets),
    "object_names": sorted(targets),
    "vertical_delta_m": DZ_M,
    "library_finish_top_before_m": LIBRARY_FINISH_TOP_BEFORE_M,
    "modeled_f03_slab_top_m": FLOOR_FINISH_TOP_M,
    "core_connector": {
        "object": connector.name,
        "bounds_m": {
            "x": [-0.725, 0.525],
            "y": [-4.71, 10.91],
            "z": [6.582, 6.600],
        },
        "evidence": "2022 third-floor plan shows library area connecting south through hall 311 to the elevator core; the plan gives no corridor dimensions.",
    },
    "saved_world_z_bounds_m": after_bounds,
    "scope": "Math Library 2026 geometry, legacy MATH_Lib_* geometry, and third-floor stair/elevator geometry only.",
    "uncertainty": "The F03 absolute z value and typical floor spacing are estimated; this correction aligns the third-floor interior to the model's corresponding F03 slab, not to a surveyed elevation.",
}
OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
