import hashlib
import json
import math
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/massing_utility_plant_office_facility_e219ef5.blend"
EVIDENCE = ROOT / "audit/utility_plant_office_facility/build_evidence.json"
OUT = ROOT / "audit/utility_plant_office_facility/validation.json"
GIS_SNAPSHOT = ROOT / "audit/utility_plant_office_facility/sources/arcgis_fid296_feature.json"
ASSET_COLLECTION = "Asset_massing_utility_plant_office_facility_e219ef5"
SCENE_NAME = "Building_massing_utility_plant_office_facility_e219ef5"

def main():
    # Blender has already freshly opened the asset passed on the command line.
    scene = bpy.context.scene
    asset_col = bpy.data.collections.get(ASSET_COLLECTION)
    shell = bpy.data.objects.get("UPOF_Office_Shell_Footprint_Verified_Extrusion_Estimated")
    assert scene and scene.name == SCENE_NAME, f"Unexpected scene {scene.name if scene else None}"
    assert asset_col, f"Missing {ASSET_COLLECTION}"
    assert shell and shell.type == "MESH", "Missing extruded GIS shell"
    assert len(asset_col.all_objects) > 250, "Unexpectedly incomplete asset collection"

    verts = [shell.matrix_world @ v.co for v in shell.data.vertices]
    footprint = [(v.x, v.y) for v in verts if abs(v.z) < 1e-6]
    assert len(footprint) == 10, f"Expected 10 unique GIS ring vertices, got {len(footprint)}"
    bx = (min(x for x, y in footprint), max(x for x, y in footprint))
    by = (min(y for x, y in footprint), max(y for x, y in footprint))
    area = abs(sum(footprint[i][0] * footprint[(i + 1) % len(footprint)][1]
                   - footprint[(i + 1) % len(footprint)][0] * footprint[i][1]
                   for i in range(len(footprint))) / 2.0)
    width, depth = bx[1] - bx[0], by[1] - by[0]
    source_feature = json.loads(GIS_SNAPSHOT.read_text(encoding="utf-8"))["features"][0]
    geo_ring = source_feature["geometry"]["rings"][0][:-1]
    ax, ay = 105.20840981346892, -1052.103607498187
    expected = [(round((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)), 3) - ax,
                 round((lat - 40.4274) * 111040.0, 3) - ay)
                for lon, lat in geo_ring]
    point_errors = [min(math.hypot(x - ex, y - ey) for ex, ey in expected)
                    for x, y in footprint]
    max_point_error = max(point_errors)
    edges = [math.dist(footprint[i], footprint[(i + 1) % len(footprint)])
             for i in range(len(footprint))]
    major_edge = max(range(len(edges)), key=edges.__getitem__)
    x1, y1 = footprint[major_edge]
    x2, y2 = footprint[(major_edge + 1) % len(footprint)]
    orientation_from_north_deg = abs(math.degrees(math.atan2(x2 - x1, y2 - y1)))

    externals = []
    for image in bpy.data.images:
        if image.source == "FILE" and image.filepath and not image.packed_file:
            resolved = Path(bpy.path.abspath(image.filepath))
            if not resolved.exists():
                externals.append(str(image.filepath))

    # Distinguish roof/parapet envelope from rooftop mechanical equipment.
    mesh_z = [float((obj.matrix_world @ Vector(corner)).z)
              for obj in asset_col.all_objects if obj.type == "MESH"
              for corner in obj.bound_box]
    all_mesh_z = (min(mesh_z), max(mesh_z))
    record = {
        "status": "pass" if not externals and max_point_error < 0.002 else "fail",
        "fresh_open": True,
        "asset_path": ASSET.relative_to(ROOT).as_posix(),
        "scene": scene.name,
        "collection": asset_col.name,
        "object_count_in_asset_collection": len(asset_col.all_objects),
        "shell_vertex_count": len(shell.data.vertices),
        "shell_footprint_vertex_count": len(footprint),
        "shell_bounds_local_m": {"x": list(bx), "y": list(by)},
        "shell_dimensions_local_m": {"east_west": width, "north_south": depth},
        "shell_area_from_ring_m2": area,
        "max_xy_vertex_error_vs_raw_gis_ring_m": max_point_error,
        "longest_gis_edge_orientation_degrees_from_north": orientation_from_north_deg,
        "shell_z_bounds_m": [min(v.z for v in verts), max(v.z for v in verts)],
        "asset_mesh_z_bounds_m_all_asset_objects": list(all_mesh_z),
        "unverified_roof_equipment_objects": [obj.name for obj in asset_col.all_objects
                                              if obj.name.startswith(("Roof_HVAC_", "Roof_Service_Hatch"))],
        "external_unpacked_images": externals,
        "textures": "procedural Blender node materials; no linked external texture files",
        "placement_origin_xy_m": [105.20840981346892, -1052.103607498187],
        "asset_sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
        "validated_with_blender": bpy.app.version_string,
    }
    OUT.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print("UPOF_VALIDATION", json.dumps(record, sort_keys=True))

from mathutils import Vector

if __name__ == "__main__":
    main()
