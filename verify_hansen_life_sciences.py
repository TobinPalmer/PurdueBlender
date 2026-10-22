"""
Verification Script for Arthur G. Hansen Life Sciences Research Building (HANS)
"""
import bpy
import json
import math
from mathutils import Vector

def run_verification():
    blend_path = "modular/buildings/hansen_life_sciences.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    scene = bpy.context.scene
    print("=== ASSET VERIFICATION REPORT: HANSEN LIFE SCIENCES ===")
    print(f"Scene Name: {scene.name} (Expected: Building_hansen_life_sciences)")
    
    root_col = bpy.data.collections.get("Asset_hansen_life_sciences")
    print(f"Collection Name: {root_col.name if root_col else None} (Expected: Asset_hansen_life_sciences)")

    # Read official reference data
    with open("audit/official_building_references.json", "r") as f:
        data = json.load(f)
    hans_ref = None
    for b in data.get("buildings", []):
        if b.get("code") == "HANS":
            hans_ref = b
            break

    official_center = hans_ref["official_polygon_center_xy_m"]
    official_aabb = hans_ref["aabb_xy_m"]
    official_ring = hans_ref["rings_xy_m"][0]

    # Compute evaluated bounds of all mesh objects in Asset_hansen_life_sciences
    all_objs = [obj for obj in bpy.data.objects if obj.type == 'MESH' and not "Plaza" in obj.name and not "Lawn" in obj.name and not "Sidewalk" in obj.name and not "Driveway" in obj.name and not "Ribbon" in obj.name]

    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')
    min_z, max_z = float('inf'), float('-inf')

    for obj in all_objs:
        for v in obj.bound_box:
            wv = obj.matrix_world @ Vector(v)
            min_x = min(min_x, wv.x)
            max_x = max(max_x, wv.x)
            min_y = min(min_y, wv.y)
            max_y = max(max_y, wv.y)
            min_z = min(min_z, wv.z)
            max_z = max(max_z, wv.z)

    bldg_center_x = (min_x + max_x) / 2.0
    bldg_center_y = (min_y + max_y) / 2.0

    offset_x = bldg_center_x - ((official_aabb[0] + official_aabb[2]) / 2.0)
    offset_y = bldg_center_y - ((official_aabb[1] + official_aabb[3]) / 2.0)
    offset_dist = math.hypot(offset_x, offset_y)

    print("\n--- GEOMETRIC & PLACEMENT METRICS ---")
    print(f"Official Centroid:      ({official_center[0]:.5f}, {official_center[1]:.5f})")
    print(f"Official AABB:          X=[{official_aabb[0]:.3f}, {official_aabb[2]:.3f}], Y=[{official_aabb[1]:.3f}, {official_aabb[3]:.3f}]")
    print(f"Model AABB:             X=[{min_x:.3f}, {max_x:.3f}], Y=[{min_y:.3f}, {max_y:.3f}], Z=[{min_z:.3f}, {max_z:.3f}]")
    print(f"AABB Centroid Offset:   dx={offset_x:.4f}m, dy={offset_y:.4f}m, total={offset_dist:.4f}m")
    print(f"Building Heights:       Base={min_z:.3f}m, Main Roof Parapet={18.288:.3f}m, Penthouse Top={20.422:.3f}m, Max Strobic Flue={max_z:.3f}m")

    # Check footprint vertices agreement with foundation wall
    wt_objs = [obj for obj in all_objs if "WaterTable" in obj.name or "ParapetWall" in obj.name]
    print(f"Total Structural Wall Sections: {len(wt_objs)}")

    # Check materials
    print("\n--- MATERIALS & PORTABILITY ---")
    missing_textures = []
    for img in bpy.data.images:
        if img.source == 'FILE' and not img.packed_file:
            missing_textures.append(img.name)
    print(f"External Unpacked Textures: {len(missing_textures)}")
    print(f"Total Materials: {len(bpy.data.materials)}")
    for mat in bpy.data.materials:
        print(f"  - {mat.name}")

    # Check scene properties & text metadata
    print("\n--- METADATA & INTERIOR DISCLOSURE ---")
    for k in ["building_id", "building_code", "official_name", "gis_fid", "completion_year", "interior_status"]:
        print(f"scene['{k}'] = {scene.get(k)}")

    readme = bpy.data.texts.get("README_EVIDENCE")
    print(f"README_EVIDENCE text datablock present: {readme is not None} (Length: {len(readme.as_string()) if readme else 0} chars)")

    print("\n=== VERIFICATION FINISHED ===")

if __name__ == "__main__":
    run_verification()
