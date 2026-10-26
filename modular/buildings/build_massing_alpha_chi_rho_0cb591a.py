"""Rebuild the Alpha Chi Rho campus massing from Purdue GIS feature 775.

The building is deliberately kept as one portable Blender mesh in campus
coordinates because the manifest classifies it as a simple massing asset.
Horizontal dimensions follow the official GIS outline; wall height, facade
openings, porch, and neutral low roof are illustrative where no current
dimensioned elevation was located.
"""

import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_alpha_chi_rho_0cb591a"
ASSET_FILE = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
GIS_FILE = ROOT / "audit" / "alpha_chi_rho" / "sources" / "purdue_gis_FID775_alpha_chi_rho_2026-10-26.json"
PREVIEW_FILE = ROOT / "audit" / "alpha_chi_rho" / "alpha_chi_rho_preview.png"
BUILD_RESULT_FILE = ROOT / "audit" / "alpha_chi_rho" / "build_result.json"
SCENE_NAME = "Building_massing_alpha_chi_rho_0cb591a"
COLLECTION_NAME = "Asset_massing_alpha_chi_rho_0cb591a"

ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
WALL_HEIGHT = 3.8
ROOF_THICKNESS = 0.35


def local_xy(lon, lat):
    """Project GIS WGS84 coordinates with the repo's documented local approximation."""
    x = (lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT))
    y = (lat - ORIGIN_LAT) * 111040.0
    return (x, y)


def material(name, color, roughness=0.75):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return m


class MeshBuilder:
    def __init__(self):
        self.verts = []
        self.faces = []
        self.material_ids = []

    def face(self, points, material_id):
        self.faces.append(tuple(self.vertex(p) for p in points))
        self.material_ids.append(material_id)

    def vertex(self, point):
        self.verts.append(tuple(point))
        return len(self.verts) - 1

    def box(self, center, axes, size, material_id):
        """Add a closed box; axes are normalized local x/y/z basis vectors."""
        c = Vector(center)
        ax, ay, az = (Vector(a) for a in axes)
        sx, sy, sz = (v / 2 for v in size)
        corners = [
            c + ax * (sx * x) + ay * (sy * y) + az * (sz * z)
            for x, y, z in (
                (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
                (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
            )
        ]
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                  (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            self.face([corners[i] for i in f], material_id)


def ring_area(points):
    return 0.5 * sum(
        points[i][0] * points[i + 1][1] - points[i + 1][0] * points[i][1]
        for i in range(len(points) - 1)
    )


def main():
    feature = json.loads(GIS_FILE.read_text(encoding="utf-8"))["features"][0]
    assert feature["attributes"]["FID"] == 775
    assert feature["attributes"]["BUILDING_N"] == "Alpha Chi Rho"
    ring = feature["geometry"]["rings"][0]
    footprint = [local_xy(lon, lat) for lon, lat in ring[:-1]]
    n = len(footprint)
    signed_area = ring_area(footprint + [footprint[0]])
    ccw = signed_area > 0

    # Start from a clean scene so the exported library contains only this asset
    # and a separate render rig. Its one-object collection remains manifest-safe.
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)
    for scene in list(bpy.data.scenes):
        if scene != bpy.context.scene:
            bpy.data.scenes.remove(scene)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    asset = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(asset)
    rig = bpy.data.collections.new("Render_Setup")
    scene.collection.children.link(rig)

    mats = [
        material("Warm white horizontal siding", (0.83, 0.80, 0.72)),
        material("Stone foundation", (0.43, 0.43, 0.40)),
        material("Dark gray roof membrane (illustrative)", (0.16, 0.19, 0.20)),
        material("Muted blue gray glazing", (0.18, 0.29, 0.34), 0.25),
        material("White window and porch trim", (0.91, 0.89, 0.83)),
        material("Wood entry door", (0.28, 0.19, 0.14)),
        material("Siding seam shadow", (0.66, 0.65, 0.59)),
    ]
    mb = MeshBuilder()

    # Official GIS building perimeter, extruded into a one-level shell. The
    # source level count supports one level, while its extrusion field's units
    # are undocumented; the 3.8 m shell height is therefore only an estimate.
    bottom = [(x, y, 0.0) for x, y in footprint]
    eaves = [(x, y, WALL_HEIGHT) for x, y in footprint]
    roof_top = [(x, y, WALL_HEIGHT + ROOF_THICKNESS) for x, y in footprint]
    for i in range(n):
        j = (i + 1) % n
        mb.face([bottom[i], bottom[j], eaves[j], eaves[i]], 0)
        mb.face([eaves[i], eaves[j], roof_top[j], roof_top[i]], 2)
    mb.face(list(reversed(bottom)), 1)
    mb.face(roof_top, 2)

    # Horizontal siding courses wrap the outside wall faces. Their shallow
    # relief is based on the 1978 chapter-house photograph in Purdue's Debris.
    outward_sign = 1.0 if ccw else -1.0
    for i in range(n):
        p = footprint[i]
        q = footprint[(i + 1) % n]
        dx, dy = q[0] - p[0], q[1] - p[1]
        length = math.hypot(dx, dy)
        if length < 1.5:
            continue
        tangent = (dx / length, dy / length, 0.0)
        normal = (outward_sign * dy / length, -outward_sign * dx / length, 0.0)
        mb.box(((p[0] + q[0]) / 2 + normal[0] * 0.045,
                (p[1] + q[1]) / 2 + normal[1] * 0.045,
                0.19), (tangent, normal, (0.0, 0.0, 1.0)),
               (length, 0.09, 0.38), 1)
        for z in [0.64 + k * 0.28 for k in range(int((WALL_HEIGHT - 0.7) / 0.28))]:
            mb.box(((p[0] + q[0]) / 2 + normal[0] * 0.025,
                    (p[1] + q[1]) / 2 + normal[1] * 0.025,
                    z), (tangent, normal, (0.0, 0.0, 1.0)),
                   (length, 0.025, 0.018), 6)

    # Facade rhythm is illustrative: evenly spaced paired windows, with no
    # claims about exact openings, room layouts, or current facade details.
    west_fronts = []
    for i in range(n):
        p, q = footprint[i], footprint[(i + 1) % n]
        dx, dy = q[0] - p[0], q[1] - p[1]
        length = math.hypot(dx, dy)
        nx, ny = outward_sign * dy / length, -outward_sign * dx / length
        if nx < -0.85 and length >= 5.4:
            west_fronts.append((length, i))
    entry_edge_index = max(west_fronts)[1] if west_fronts else None
    for i in range(n):
        p, q = footprint[i], footprint[(i + 1) % n]
        dx, dy = q[0] - p[0], q[1] - p[1]
        length = math.hypot(dx, dy)
        if length < 5.4:
            continue
        tangent = (dx / length, dy / length, 0.0)
        normal = (outward_sign * dy / length, -outward_sign * dx / length, 0.0)
        count = max(1, int((length - 1.2) // 3.2))
        centers = [length * (j + 1) / (count + 1) for j in range(count)]
        # The westward-facing street side receives a simple entry porch.
        street_front = i == entry_edge_index
        door_center = centers[len(centers) // 2] if street_front else None
        for center in centers:
            if street_front and center == door_center:
                continue
            c = (p[0] + tangent[0] * center + normal[0] * 0.055,
                 p[1] + tangent[1] * center + normal[1] * 0.055,
                 1.85)
            axes = (tangent, normal, (0.0, 0.0, 1.0))
            # Painted trim surround, inset glazing, and simple muntins.
            mb.box(c, axes, (1.42, 0.07, 1.62), 4)
            mb.box((c[0] + normal[0] * 0.045,
                    c[1] + normal[1] * 0.045, c[2]), axes,
                   (1.12, 0.035, 1.32), 3)
            mb.box((c[0] + normal[0] * 0.075,
                    c[1] + normal[1] * 0.075, c[2]), axes,
                   (0.055, 0.025, 1.25), 4)
            mb.box((c[0] + normal[0] * 0.075,
                    c[1] + normal[1] * 0.075, c[2]), axes,
                   (1.05, 0.025, 0.055), 4)
        if street_front:
            center = door_center
            c = (p[0] + tangent[0] * center + normal[0] * 0.08,
                 p[1] + tangent[1] * center + normal[1] * 0.08, 1.12)
            axes = (tangent, normal, (0.0, 0.0, 1.0))
            mb.box((c[0] - normal[0] * 0.035,
                    c[1] - normal[1] * 0.035, 1.125), axes,
                   (1.38, 0.08, 2.25), 4)
            mb.box(c, axes, (1.10, 0.05, 2.08), 5)
            # Shallow entrance canopy, modeled as a simple porch hood.
            porch_center = (c[0] + normal[0] * 0.75,
                            c[1] + normal[1] * 0.75, 2.48)
            mb.box(porch_center, axes, (2.5, 1.45, 0.15), 2)
            for offset in (-0.95, 0.95):
                col = (c[0] + tangent[0] * offset + normal[0] * 1.35,
                       c[1] + tangent[1] * offset + normal[1] * 1.35, 1.23)
                mb.box(col, axes, (0.12, 0.12, 2.45), 4)

    mesh = bpy.data.meshes.new("Alpha Chi Rho GIS shell and illustrative facade")
    mesh.from_pydata(mb.verts, [], mb.faces)
    mesh.update()
    obj = bpy.data.objects.new("Alpha Chi Rho", mesh)
    asset.objects.link(obj)
    for m in mats:
        mesh.materials.append(m)
    for poly, material_id in zip(mesh.polygons, mb.material_ids):
        poly.material_index = material_id
    # Correct the shell's orientation and keep each face smoothness explicit.
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    for poly in mesh.polygons:
        poly.use_smooth = False

    # Render rig is outside the exported asset collection.
    center_x = sum(p[0] for p in footprint) / n
    center_y = sum(p[1] for p in footprint) / n
    bpy.ops.object.select_all(action="DESELECT")
    camera_data = bpy.data.cameras.new("AXP massing preview camera")
    camera = bpy.data.objects.new("AXP massing preview camera", camera_data)
    rig.objects.link(camera)
    camera.location = (center_x - 46.0, center_y - 48.0, 37.0)
    target = Vector((center_x, center_y, 4.2))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 48.0
    scene.camera = camera

    light_data = bpy.data.lights.new("Large soft key", type="AREA")
    light_data.energy = 8200
    light_data.shape = "DISK"
    light_data.size = 32
    light = bpy.data.objects.new("Large soft key", light_data)
    rig.objects.link(light)
    light.location = (center_x - 18, center_y - 24, 38)
    light.rotation_euler = (Vector((center_x, center_y, 3.0)) - light.location).to_track_quat("-Z", "Y").to_euler()

    scene.render.engine = "CYCLES"
    scene.cycles.samples = 20
    scene.render.resolution_x = 1250
    scene.render.resolution_y = 1050
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.52, 0.56, 0.62)
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.52, 0.56, 0.62, 1.0)
        background.inputs["Strength"].default_value = 0.8
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.8
    scene.render.filepath = str(PREVIEW_FILE)

    os.makedirs(PREVIEW_FILE.parent, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_FILE))
    bpy.ops.render.render(write_still=True)

    bounds = [[min(v[i] for v in obj.bound_box), max(v[i] for v in obj.bound_box)] for i in range(3)]
    result = {
        "asset": str(ASSET_FILE),
        "collection": COLLECTION_NAME,
        "scene": SCENE_NAME,
        "object_count": len(asset.objects),
        "mesh_vertices": len(mesh.vertices),
        "mesh_polygons": len(mesh.polygons),
        "gis_vertex_count": n,
        "gis_xy_area_m2_approx": abs(signed_area),
        "bounds_m": bounds,
        "estimated_wall_height_m": WALL_HEIGHT,
        "estimated_total_height_m": WALL_HEIGHT + ROOF_THICKNESS,
        "preview": str(PREVIEW_FILE),
    }
    BUILD_RESULT_FILE.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
