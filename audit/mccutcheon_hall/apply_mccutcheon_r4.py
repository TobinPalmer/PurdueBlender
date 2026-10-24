import bpy
import json
from pathlib import Path

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET = ROOT / "modular/buildings/mccutcheon_hall.blend"
LIDAR = json.loads((ROOT / "audit/mccutcheon_hall/mccutcheon_r4_lidar_height.json").read_text(encoding="utf-8"))
bpy.ops.wm.open_mainfile(filepath=str(ASSET))

collection = bpy.data.collections["Asset_mccutcheon_hall"]
root = bpy.data.objects["AssetRoot_mccutcheon_hall"]
removed_names = []
for suffix in (
    "Penthouse_Brick", "Penthouse_Coping", "Penthouse_Roof_Slab",
    "PH_Louver_N", "PH_Louver_S", "PH_Louver_W", "PH_Louver_E", "PH_Door",
):
    for tower in ("North", "South"):
        name = f"MCUT_{tower}_{suffix}"
        obj = bpy.data.objects.get(name)
        if obj is not None:
            bpy.data.objects.remove(obj, do_unlink=True)
            removed_names.append(name)

assert len(removed_names) == 16, removed_names
assert len(collection.all_objects) == 219, len(collection.all_objects)

root["r4_documented_north_tower_occupied_floors"] = 8
root["r4_documented_south_tower_occupied_floors"] = 8
root["r4_floor_count_source_urls"] = json.dumps([
    "https://www.in.gov/dA/a0641c5d3d/November_2014_CHE_Agenda.pdf?language_id=1",
    "https://www.in.gov/che/files/Sept_2015_Commission_Meeting_Agenda.pdf",
    "https://www.bcclt.com/case-studies/mccutcheon-hall-university-residences-bathroom-renovation-phase-iv/",
])
root["r4_lidar_roof_p95_height_above_ground_m"] = float(LIDAR["estimated_height_above_nearby_ground_m"]["95"])
root["r4_lidar_roof_p999_height_above_ground_m"] = float(LIDAR["estimated_height_above_nearby_ground_m"]["99.9"])
root["r4_lidar_max_candidate_height_above_ground_m"] = float(
    LIDAR["class1_candidate_max_z_m"] - LIDAR["ground_class2_z_median_m"]
)
root["r4_roof_change_status"] = (
    "Removed unsupported tall brick tower rooftop penthouse assemblies. 2017-2018 USGS 3DEP class-1 return estimate "
    "has p95 25.93m, p99.9 26.09m, and max 26.16m above nearby class-2 ground; LAS metadata states vertical accuracy N/A "
    "and this tile contains no class-6 building returns. Roof profile and equipment dimensions remain unverified."
)

scene = bpy.data.scenes["Building_mccutcheon_hall"]
scene["r4_change_summary"] = "Removed 16 unsupported tall penthouse objects from both tower roofs; retained eight-storey tower shells, roof decks, parapets, and copings."
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps({"saved_asset": str(ASSET), "removed_objects": removed_names, "collection_objects_after": len(collection.all_objects), "root_properties": {k: str(root[k]) for k in root.keys()}}, indent=2))
