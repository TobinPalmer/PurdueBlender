import bpy
import json
import hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
BLEND = ROOT / "modular/buildings/potter_engineering.blend"
OUT = ROOT / "audit/potter_engineering_refine/current_validation.json"

bpy.ops.wm.open_mainfile(filepath=str(BLEND))
collection = bpy.data.collections["Asset_potter_engineering"]
root = bpy.data.objects["AssetRoot_potter_engineering"]
shell = collection.objects["POTR_Official_864_Structural_Envelope"]
roof = collection.objects["POTR_Official_864_Roof"]
core = collection.objects["POTR_4S04_Enclosure_Walls_183sf_Estimate"]
landing = collection.all_objects["POTR_2016_StairCore3_Penthouse_Landing_4S04_Estimate"]

def local_bounds(obj):
    pts = [obj.matrix_local @ Vector(corner) for corner in obj.bound_box]
    return [[round(min(p[i] for p in pts), 5), round(max(p[i] for p in pts), 5)] for i in range(3)]

def ray_hit(obj, xyz, direction):
    return bool(obj.ray_cast(Vector(xyz), Vector(direction))[0])

images_missing = [im.filepath for im in bpy.data.images if im.source == "FILE" and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]
mesh_objects = [o for o in collection.all_objects if o.type == "MESH"]
all_points = [(o.matrix_world @ Vector(corner)) for o in mesh_objects for corner in o.bound_box]
overall_bounds = [[round(min(p[i] for p in all_points), 5), round(max(p[i] for p in all_points), 5)] for i in range(3)]

entry_center_clear = not ray_hit(core, (8.8, 35.2, 14.4), (1, 0, 0))
entry_control_hits_wall = ray_hit(core, (8.8, 36.2, 14.4), (1, 0, 0))
roof_open_center_clear = not ray_hit(roof, (10.5, 35.2, 20), (0, 0, -1))
roof_control_west_hits = ray_hit(roof, (8.5, 35.2, 20), (0, 0, -1))
roof_control_east_hits = ray_hit(roof, (12.3, 35.2, 20), (0, 0, -1))

# A conservative 0.8 m square person-footprint proxy checks the upper stair-to-door turn.
# Its endpoint centres and turn corner are judged against the modeled landing footprint;
# crossing the 4S04 west wall is allowed only through the ray-verified 1.2 m door gap.
landing_xy = local_bounds(landing)[:2]
path_centres = [(9.262, 35.725), (9.262, 35.2), (9.45, 35.2)]
proxy_half = 0.4
proxy_fits_landing = all(
    all(landing_xy[axis][0] <= p[axis] - proxy_half and p[axis] + proxy_half <= landing_xy[axis][1] for axis in (0, 1))
    for p in path_centres
)
door_interval_y = [34.6, 35.8]
proxy_fits_door = door_interval_y[0] <= 35.2 - proxy_half and 35.2 + proxy_half <= door_interval_y[1]

result = {
    "reopened_saved_asset": True,
    "asset_path": str(BLEND),
    "asset_root_location": [round(v, 6) for v in root.location],
    "export_collection": collection.name,
    "object_count": len(collection.all_objects),
    "expected_object_count": 500,
    "object_count_match": len(collection.all_objects) == 500,
    "overall_mesh_local_bounds_m": overall_bounds,
    "asset_sha256": hashlib.sha256(BLEND.read_bytes()).hexdigest().upper(),
    "structural_shell_local_bounds_m": local_bounds(shell),
    "roof_local_bounds_m": local_bounds(roof),
    "landing_local_bounds_m": local_bounds(landing),
    "room401_walls_local_bounds_m": local_bounds(core),
    "missing_external_images": images_missing,
    "s03_roof_aperture_rays": {
        "center_opening_clear": roof_open_center_clear,
        "west_control_hits_roof": roof_control_west_hits,
        "east_control_hits_roof": roof_control_east_hits,
        "opening_is_estimated": True,
        "source_supports_stair_location_but_not_aperture_dimensions": True,
    },
    "four_s04_door_rays": {
        "centerline_clear": entry_center_clear,
        "side_control_hits_wall": entry_control_hits_wall,
        "clear_width_m_estimate": 1.2,
    },
    "upper_route_proxy": {
        "footprint_side_m": 0.8,
        "centerline_points_xy_m": path_centres,
        "all_proxy_footprints_fit_modeled_landing": proxy_fits_landing,
        "proxy_fits_estimated_door_clear_width": proxy_fits_door,
        "is_code_or_accessibility_certification": False,
    },
}
OUT.write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
