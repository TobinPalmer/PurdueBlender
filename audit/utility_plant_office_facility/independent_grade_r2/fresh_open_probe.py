"""Independent fresh-open probe for the UPOF Blender asset."""
import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / "modular/buildings/massing_utility_plant_office_facility_e219ef5.blend"
AUDIT = ROOT / "audit/utility_plant_office_facility"
OUTDIR = AUDIT / "independent_grade_r2"
ASSET_COLLECTION = "Asset_massing_utility_plant_office_facility_e219ef5"
SCENE_NAME = "Building_massing_utility_plant_office_facility_e219ef5"
GIS_ID = "massing_utility_plant_office_facility_e219ef5"
ANCHOR = (105.20840981346892, -1052.103607498187)


def main():
    scene = bpy.context.scene
    col = bpy.data.collections.get(ASSET_COLLECTION)
    shell = bpy.data.objects.get("UPOF_Office_Shell_Footprint_Verified_Extrusion_Estimated")
    assert scene and scene.name == SCENE_NAME
    assert col and shell and shell.type == "MESH"
    world_vertices = [shell.matrix_world @ v.co for v in shell.data.vertices]
    ring = [(v.x, v.y) for v in world_vertices if abs(v.z) < 1e-6]
    src = json.loads((AUDIT / "sources/arcgis_fid296_feature.json").read_text(encoding="utf-8"))
    source_ring = src["features"][0]["geometry"]["rings"][0][:-1]
    expected = [(round((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)), 3) - ANCHOR[0],
                 round((lat - 40.4274) * 111040.0, 3) - ANCHOR[1])
                for lon, lat in source_ring]
    errors = [min(math.hypot(x - u, y - v) for u, v in expected) for x, y in ring]
    area = abs(sum(ring[i][0] * ring[(i + 1) % len(ring)][1]
                   - ring[(i + 1) % len(ring)][0] * ring[i][1]
                   for i in range(len(ring)))/2)
    xbounds = [min(p[0] for p in ring), max(p[0] for p in ring)]
    ybounds = [min(p[1] for p in ring), max(p[1] for p in ring)]
    edges = [math.dist(ring[i], ring[(i + 1) % len(ring)]) for i in range(len(ring))]
    i = max(range(len(edges)), key=edges.__getitem__)
    a, b = ring[i], ring[(i + 1) % len(ring)]
    orientation = abs(math.degrees(math.atan2(b[0] - a[0], b[1] - a[1])))

    asset_objects = list(col.all_objects)
    mesh_z = [float((obj.matrix_world @ Vector(corner)).z)
              for obj in asset_objects if obj.type == "MESH" for corner in obj.bound_box]
    external_images = [img.filepath for img in bpy.data.images
                       if img.source == "FILE" and img.filepath and not img.packed_file
                       and not Path(bpy.path.abspath(img.filepath)).exists()]
    seam_objects = [obj for obj in asset_objects if obj.name.startswith("Roof_Standing_Seam_")]
    seam_dims = []
    for obj in seam_objects[:5]:
        coords = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        dims = [max(c[i] for c in coords) - min(c[i] for c in coords) for i in range(3)]
        seam_dims.append({"name": obj.name, "dims_m": dims})
    roof_equipment = [obj.name for obj in asset_objects
                      if obj.name.startswith(("Roof_HVAC_", "Roof_Service_Hatch"))]
    interior = {child.name: len(child.all_objects) for child in col.children}
    mats = sorted({m.name for obj in asset_objects for m in obj.data.materials if m})
    image_dependencies = [img.name for img in bpy.data.images if img.source == "FILE"]

    # Render the opened file's saved camera to ensure the saved asset renders as represented.
    preview = OUTDIR / "fresh_open_oblique.png"
    scene.render.filepath = str(preview)
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)

    probe = {
        "fresh_open": True,
        "blender_version": bpy.app.version_string,
        "scene": scene.name,
        "export_collection": col.name,
        "asset_sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
        "expected_sha256": "3d80ce9c7eb6c21ce21308da292e4bc7409acd7dc20875bd5a7c8e81fb0c7b28",
        "objects_in_asset": len(asset_objects),
        "mesh_objects": sum(obj.type == "MESH" for obj in asset_objects),
        "shell_vertex_count": len(shell.data.vertices),
        "shell_footprint_vertices": len(ring),
        "local_footprint_bounds_m": {"x": xbounds, "y": ybounds},
        "local_footprint_dimensions_m": {"x": xbounds[1]-xbounds[0], "y": ybounds[1]-ybounds[0]},
        "local_footprint_area_m2": area,
        "max_vertex_error_against_raw_gis_ring_m": max(errors),
        "long_axis_rotation_from_north_deg": orientation,
        "shell_z_bounds_m": [min(v.z for v in world_vertices), max(v.z for v in world_vertices)],
        "all_asset_mesh_z_bounds_m": [min(mesh_z), max(mesh_z)],
        "roof_seam_object_count": len(seam_objects),
        "roof_seam_examples": seam_dims,
        "unsupported_large_roof_equipment_names": roof_equipment,
        "interior_child_collection_object_counts": interior,
        "external_unpacked_images_missing": external_images,
        "all_image_files": image_dependencies,
        "unique_materials": mats,
        "procedural_materials_no_image_files": not image_dependencies,
        "placement_origin_xy_m": ANCHOR,
        "fresh_open_render": preview.relative_to(ROOT).as_posix(),
        "passed": scene.name == SCENE_NAME and col.name == ASSET_COLLECTION
                   and len(ring) == 10 and max(errors) < 0.002
                   and not external_images and not roof_equipment,
    }
    (OUTDIR / "fresh_open_probe.json").write_text(json.dumps(probe, indent=2), encoding="utf-8")
    print("UPOF_GRADE_PROBE", json.dumps(probe, sort_keys=True))


if __name__ == "__main__":
    main()
