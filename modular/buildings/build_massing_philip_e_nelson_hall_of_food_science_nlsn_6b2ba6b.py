"""Build the NLSN massing asset from the Purdue BuildingShapes GIS feature.

Run with Blender 5.2.3 against the existing library asset:
  blender --background <asset.blend> --python <this file>

Geometry is campus-coordinate massing (not a local-coordinate detailed asset).
The horizontal footprint comes from the saved EPSG:4326 feature snapshot using
the approximate conversion specified in modular/AGENTS.md. Vertical dimensions
are explicitly estimated from GIS level fields and the 2022 exterior photo.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon


ASSET_ID = "massing_philip_e_nelson_hall_of_food_science_nlsn_6b2ba6b"
OBJECT_NAME = "Philip E. Nelson Hall of Food Science (NLSN)"
COLLECTION_NAME = "Asset_" + ASSET_ID
ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / ASSET_ID
SOURCE = AUDIT / "sources" / "query.json"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
PREVIEW = AUDIT / "preview.png"
METRICS = AUDIT / "build_metrics.json"

# Evidence interpretation: GIS says five levels, but the online field aliases
# are undocumented. R=46.6 is consistent with feet and about 14.2 m; use that
# as an estimated overall height, with five modeled bands, not as a survey.
ESTIMATED_HEIGHT_M = 14.2
LEVELS = 5
ENTRY_WIDTH_M = 5.2
ENTRY_HEIGHT_M = 3.2


class MeshBuilder:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.material_ids = []

    def face(self, points, material):
        start = len(self.vertices)
        self.vertices.extend(tuple(p) for p in points)
        self.faces.append(tuple(range(start, start + len(points))))
        self.material_ids.append(material)


def project(lon, lat):
    # Project convention from modular/AGENTS.md; local approximate conversion.
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def make_material(name, color, roughness=0.82):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
    return mat


def main():
    feature_collection = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
    assert len(feature_collection["features"]) == 1
    feature = feature_collection["features"][0]
    prop = feature["properties"]
    assert feature["id"] == 250 and prop["BLDG_ABBR"] == "NLSN"
    assert prop["BUILDING_N"] == "Philip E. Nelson Hall of Food Science"
    ring = feature["geometry"]["coordinates"][0]
    xy = [project(lon, lat) for lon, lat in ring[:-1]]
    assert len(xy) >= 4

    # Ensure the expected exported collection and object remain stable.
    coll = bpy.data.collections.get(COLLECTION_NAME)
    assert coll is not None, f"Missing expected collection {COLLECTION_NAME}"
    obj = bpy.data.objects.get(OBJECT_NAME)
    assert obj is not None and obj.type == "MESH"
    assert obj.name in coll.objects
    assert tuple(round(v, 6) for v in obj.location) == (0, 0, 0)
    assert tuple(round(v, 6) for v in obj.rotation_euler) == (0, 0, 0)

    # Preserve identity transforms and replace only the assigned object's mesh.
    old_mesh = obj.data
    mesh_data = MeshBuilder()
    z0, ztop = 0.0, ESTIMATED_HEIGHT_M
    for i, (x1, y1) in enumerate(xy):
        x2, y2 = xy[(i + 1) % len(xy)]
        mesh_data.face([(x1, y1, z0), (x2, y2, z0),
                        (x2, y2, ztop), (x1, y1, ztop)], 0)
    ring_vectors = [Vector((x, y, 0)) for x, y in xy]
    for tri in tessellate_polygon([ring_vectors]):
        pts = [ring_vectors[i] for i in tri]
        mesh_data.face([(p.x, p.y, ztop) for p in pts], 0)

    brick = make_material("NLSN | red-brown brick (photo-supported)", (0.38, 0.105, 0.065))
    trim = make_material("NLSN | light masonry trim (photo-supported)", (0.76, 0.68, 0.53))
    glass = make_material("NLSN | dark blue glazing (photo-supported)", (0.045, 0.11, 0.16), 0.24)
    materials = [brick, trim, glass]

    # Draw simple window fields on perimeter walls. Window count is a visual
    # massing rhythm from the dated photo; exact bay locations are unverified.
    signed_area = sum(xy[i][0] * xy[(i+1) % len(xy)][1] -
                      xy[(i+1) % len(xy)][0] * xy[i][1] for i in range(len(xy))) / 2
    ccw = signed_area > 0
    story_step = ztop / LEVELS
    for i, (x1, y1) in enumerate(xy):
        x2, y2 = xy[(i + 1) % len(xy)]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length < 4.8:
            continue
        tx, ty = dx / length, dy / length
        # Edge outward normal for the ring winding.
        nx, ny = (ty, -tx) if ccw else (-ty, tx)
        bays = max(1, int(length / 5.2))
        for bay in range(bays):
            center = (bay + 0.5) * length / bays
            # Avoid glazing across the photographed entry on the south edge.
            is_entry_edge = abs(y1 + 680.0) < 1.5 and abs(y2 + 680.0) < 1.5 and length > 35
            entry_mid = length * 0.52
            if is_entry_edge and abs(center - entry_mid) < ENTRY_WIDTH_M * 0.8:
                continue
            w = min(1.65, length / bays * 0.45)
            for level in range(LEVELS):
                zc = (level + 0.5) * story_step
                zh = min(1.15, story_step * 0.53)
                # Rectangles float slightly above the brick surface as façade
                # indication only; each remains within the estimated wall.
                base = Vector((x1 + tx * center + nx * 0.035,
                               y1 + ty * center + ny * 0.035, zc))
                corners = [base + Vector((tx * u, ty * u, z))
                           for u, z in [(-w/2, -zh/2), (w/2, -zh/2),
                                        (w/2, zh/2), (-w/2, zh/2)]]
                mesh_data.face(corners, 2)

    # Entrance porch and door on the south-facing long boundary, consistent
    # with the available Purdue Events photo. Placement within that edge is an
    # estimate; the raster photo does not provide survey coordinates.
    south_i = min(range(len(xy)), key=lambda i: (xy[i][1] + xy[(i+1) % len(xy)][1]) / 2)
    x1, y1 = xy[south_i]
    x2, y2 = xy[(south_i + 1) % len(xy)]
    dx, dy = x2-x1, y2-y1
    length = math.hypot(dx, dy)
    tx, ty = dx/length, dy/length
    nx, ny = (ty, -tx) if ccw else (-ty, tx)
    cx, cy = x1 + tx * length * 0.52, y1 + ty * length * 0.52
    # Recessed dark door panel.
    d0 = Vector((cx - tx*ENTRY_WIDTH_M/2 + nx*0.045,
                 cy - ty*ENTRY_WIDTH_M/2 + ny*0.045, 0.1))
    door = [d0, d0 + Vector((tx*ENTRY_WIDTH_M, ty*ENTRY_WIDTH_M, 0)),
            d0 + Vector((tx*ENTRY_WIDTH_M, ty*ENTRY_WIDTH_M, ENTRY_HEIGHT_M)),
            d0 + Vector((0, 0, ENTRY_HEIGHT_M))]
    mesh_data.face(door, 2)
    # Light stone lintel and simple portico columns, thin but visible in plan.
    porch_depth = 1.8
    for offset in (-ENTRY_WIDTH_M/2, ENTRY_WIDTH_M/2):
        px, py = cx + tx*offset + nx*0.35, cy + ty*offset + ny*0.35
        width = 0.28
        verts = [Vector((px, py, 0)), Vector((px+tx*width, py+ty*width, 0)),
                 Vector((px+tx*width, py+ty*width, ENTRY_HEIGHT_M)),
                 Vector((px, py, ENTRY_HEIGHT_M))]
        mesh_data.face(verts, 1)
    # Projecting flat canopy slab; photo shows a pale horizontal entrance hood.
    can_z = ENTRY_HEIGHT_M + 0.18
    a = Vector((cx-tx*ENTRY_WIDTH_M/2, cy-ty*ENTRY_WIDTH_M/2, can_z))
    b = Vector((cx+tx*ENTRY_WIDTH_M/2, cy+ty*ENTRY_WIDTH_M/2, can_z))
    c = b + Vector((nx*porch_depth, ny*porch_depth, 0))
    d = a + Vector((nx*porch_depth, ny*porch_depth, 0))
    mesh_data.face([a, b, c, d], 1)

    # Raised gabled entrance parapet/tower observed in photo; exact geometry is
    # uncertain, so keep it compact and behind the portico.
    g_base = ztop - 2.8
    g_peak = ztop + 2.2
    half = 4.3
    p1 = Vector((cx-tx*half, cy-ty*half, g_base))
    p2 = Vector((cx+tx*half, cy+ty*half, g_base))
    p3 = Vector((cx, cy, g_peak))
    mesh_data.face([p1, p2, p3], 0)
    mesh_data.face([p1+Vector((nx*0.18,ny*0.18,0)),
                    p3+Vector((nx*0.18,ny*0.18,0)),
                    p2+Vector((nx*0.18,ny*0.18,0))], 0)
    # A restrained trim line marks the stepped gable without claiming detailed
    # roof construction unsupported by source material.
    mesh_data.face([p1, p2, p2+Vector((0,0,0.18)), p1+Vector((0,0,0.18))], 1)

    new_mesh = bpy.data.meshes.new(f"{ASSET_ID}_mesh")
    new_mesh.from_pydata(mesh_data.vertices, [], mesh_data.faces)
    new_mesh.update()
    for mat in materials:
        new_mesh.materials.append(mat)
    for poly, mat_id in zip(new_mesh.polygons, mesh_data.material_ids):
        poly.material_index = mat_id
    obj.data = new_mesh
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)
    new_mesh.name = f"{ASSET_ID}_mesh"
    bpy.context.view_layer.update()

    # Reproducible dimensions and geometry summary for independent inspection.
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    bounds = [[min((eval_obj.matrix_world @ Vector(c))[i] for c in eval_obj.bound_box),
               max((eval_obj.matrix_world @ Vector(c))[i] for c in eval_obj.bound_box)]
              for i in range(3)]
    metrics = {
        "asset_id": ASSET_ID,
        "source_feature": {"provider": "Purdue ArcGIS BuildingShapesZip4", "FID": 250,
                           "BLDG_ABBR": prop["BLDG_ABBR"], "name": prop["BUILDING_N"]},
        "coordinate_transform": "X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040; approximate meters",
        "source_vertex_count_excluding_closure": len(xy),
        "source_ring_area_shoelace_m2": abs(signed_area),
        "rendered_bounds_world_m": bounds,
        "estimated_height_m": ESTIMATED_HEIGHT_M,
        "GIS_NUM_LEVELS": prop.get("NUM_LEVELS"),
        "modeled_level_bands": LEVELS,
        "uncertainty": ["GIS vertical field semantics are undocumented.",
                        "Photo shows brick walls, regular window bays and recessed entrance with pale canopy; exact bay positions and entrance coordinates are estimated.",
                        "Roof outline beyond raised entrance gable is not established by available sources."],
        "object_count": 1,
        "mesh_vertices": len(new_mesh.vertices),
        "mesh_faces": len(new_mesh.polygons),
    }

    # Temporary render rig, removed before saving the portable asset.
    scene = bpy.context.scene
    temp_objects = []
    cam_data = bpy.data.cameras.new("NLSN_preview_camera")
    cam = bpy.data.objects.new("NLSN_preview_camera", cam_data)
    scene.collection.objects.link(cam)
    temp_objects.append(cam)
    center = Vector(((bounds[0][0]+bounds[0][1])/2,
                     (bounds[1][0]+bounds[1][1])/2,
                     (bounds[2][0]+bounds[2][1])/2))
    cam.location = center + Vector((-100, -118, 89))
    direction = center - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 52
    scene.camera = cam
    for name, location, energy, size in [
        ("NLSN_preview_key", center+Vector((-50,-25,85)), 35000, 55),
        ("NLSN_preview_fill", center+Vector((40,-10,55)), 18000, 45),
    ]:
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy = energy
        ld.shape = "DISK"
        ld.size = size
        lo = bpy.data.objects.new(name, ld)
        scene.collection.objects.link(lo)
        lo.location = location
        lo.rotation_euler = (center-lo.location).to_track_quat("-Z", "Y").to_euler()
        temp_objects.append(lo)
    old_engine = scene.render.engine
    old_res = (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage)
    old_filepath = scene.render.filepath
    old_transparent = scene.render.film_transparent
    try:
        scene.render.engine = "BLENDER_WORKBENCH"
        scene.display.shading.light = "STUDIO"
        scene.display.shading.studio_light = "paint.sl"
        scene.display.shading.color_type = "MATERIAL"
        scene.display.shading.background_type = "WORLD"
        scene.display.shading.show_shadows = True
        scene.display.shading.show_cavity = True
        scene.display.shading.cavity_type = "WORLD"
        scene.render.resolution_x, scene.render.resolution_y = 1200, 900
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = "PNG"
        scene.render.film_transparent = False
        scene.render.filepath = str(PREVIEW)
        scene.world.color = (0.65, 0.65, 0.65)
        bpy.ops.render.render(write_still=True)
    finally:
        scene.camera = None
        for item in temp_objects:
            bpy.data.objects.remove(item, do_unlink=True)
        scene.render.engine = old_engine
        scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = old_res
        scene.render.filepath = old_filepath
        scene.render.film_transparent = old_transparent

    ASSET.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.mkdir(parents=True, exist_ok=True)
    METRICS.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

