"""Build Our Saviour Lutheran Church (West Lafayette) from a matched OSM way.

Run in Blender 5.2.3 against the assigned library:
  blender --background <asset.blend> --python <this file>

The footprint comes from OSM way 860901797, whose name, address, place-of-
worship tag, and website match the congregation's official page. Coordinates
are transformed to approximate campus meters per modular/AGENTS.md. Roof and
height are illustrative estimates based on the church's exterior photographs.
"""
from __future__ import annotations

import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon


ASSET_ID = "massing_our_saviour_lutheran_church_118afa2"
OBJECT_NAME = "Our Saviour Lutheran Church"
COLLECTION_NAME = "Asset_" + ASSET_ID
ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / ASSET_ID
SOURCE = AUDIT / "sources" / "osm_way_860901797_full.xml"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
PREVIEW = AUDIT / "preview.png"
METRICS = AUDIT / "build_metrics.json"

# All vertical dimensions are estimates from undimensioned exterior photos.
WALL_HEIGHT_M = 4.8
ROOF_EAVE_M = 4.8
RIDGE_HEIGHT_M = 14.2
SWEPT_GABLE_HEIGHT_M = 16.0
CROSS_TOP_M = 18.1


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

    def box_on_plane(self, center, tangent, normal, width, height, z_center, material, depth=0.06):
        # Thin rectangular panel placed on a vertical facade plane.
        c = Vector((center[0], center[1], z_center))
        t = Vector((tangent[0], tangent[1], 0)) * width / 2
        n = Vector((normal[0], normal[1], 0)) * depth / 2
        z = Vector((0, 0, height / 2))
        pts = [c-t-z-n, c+t-z-n, c+t+z-n, c-t+z-n,
               c-t-z+n, c+t-z+n, c+t+z+n, c-t+z+n]
        for f in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]:
            self.face([pts[i] for i in f], material)


def campus_xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def parse_osm_way(path):
    root = ET.parse(path).getroot()
    nodes = {n.attrib["id"]: (float(n.attrib["lon"]), float(n.attrib["lat"]))
             for n in root.findall("node")}
    way = next((w for w in root.findall("way") if w.attrib.get("id") == "860901797"), None)
    assert way is not None, "Expected OSM way 860901797 not found"
    tags = {t.attrib["k"]: t.attrib["v"] for t in way.findall("tag")}
    assert tags.get("name") == "Our Saviour Lutheran Church"
    assert tags.get("addr:housenumber") == "300"
    assert tags.get("addr:street") == "Fowler Avenue"
    assert tags.get("amenity") == "place_of_worship"
    assert tags.get("website") == "https://osluth.org/"
    coords = [nodes[n.attrib["ref"]] for n in way.findall("nd")]
    assert len(coords) >= 5 and coords[0] == coords[-1]
    return tags, way.attrib, [campus_xy(lon, lat) for lon, lat in coords[:-1]]


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
    tags, osm_meta, xy = parse_osm_way(SOURCE)
    coll = bpy.data.collections.get(COLLECTION_NAME)
    obj = bpy.data.objects.get(OBJECT_NAME)
    assert coll is not None and obj is not None and obj.type == "MESH"
    assert obj.name in coll.objects
    assert tuple(round(v, 6) for v in obj.location) == (0, 0, 0)
    assert tuple(round(v, 6) for v in obj.rotation_euler) == (0, 0, 0)

    xs, ys = [p[0] for p in xy], [p[1] for p in xy]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    xmid = (x0 + x1) / 2.0
    # OSM footprint is an L-shaped church plan. The asymmetric ridge and raised
    # north-facing entry gable approximate the distinctive sail-like roof in
    # the church's own exterior photos; no construction drawing is available.
    ridge_x = xmid + 1.6
    y_front, y_rear = y1 + 0.15, y0 + 0.55

    old_mesh = obj.data
    geom = MeshBuilder()
    # Exact OSM perimeter walls and a triangulated wall cap.
    for i, (ax, ay) in enumerate(xy):
        bx, by = xy[(i + 1) % len(xy)]
        geom.face([(ax, ay, 0), (bx, by, 0),
                   (bx, by, WALL_HEIGHT_M), (ax, ay, WALL_HEIGHT_M)], 0)
    poly = [Vector((x, y, 0)) for x, y in xy]
    for tri in tessellate_polygon([poly]):
        geom.face([(poly[i].x, poly[i].y, WALL_HEIGHT_M) for i in tri], 0)

    brick = make_material("OSLC | warm buff brick (official photo)", (0.58, 0.43, 0.30))
    roof = make_material("OSLC | charcoal shingle roof (photo estimate)", (0.105, 0.12, 0.13))
    teal = make_material("OSLC | teal vertical gable cladding (official photo)", (0.035, 0.24, 0.25))
    glass_blue = make_material("OSLC | blue stained glass (photo estimate)", (0.045, 0.22, 0.42), 0.28)
    glass_amber = make_material("OSLC | amber stained glass (photo estimate)", (0.65, 0.35, 0.05), 0.3)
    trim = make_material("OSLC | light window/cross trim", (0.84, 0.83, 0.75))
    door_mat = make_material("OSLC | dark entry glazing", (0.07, 0.12, 0.14), 0.25)
    mats = [brick, roof, teal, glass_blue, glass_amber, trim, door_mat]

    # Two steep gabled roof planes meet on an offset ridge. This keeps the
    # church's tall, sanctuary-scale roof silhouette; exact pitch is estimated.
    z_eave, z_ridge = ROOF_EAVE_M, RIDGE_HEIGHT_M
    geom.face([(x0 + 3.5, y_rear, z_eave), (ridge_x, y_rear, z_ridge),
               (ridge_x, y_front, z_ridge), (x0 + 3.5, y_front, z_eave)], 1)
    geom.face([(ridge_x, y_rear, z_ridge), (x1, y_rear, z_eave),
               (x1, y_front, z_eave), (ridge_x, y_front, z_ridge)], 1)

    # A lower gabled roof over the westward shoulder/entry, visible in the
    # official photos. The eave boundary follows the church footprint notch.
    wing_x0, wing_x1 = x0 + 0.1, x0 + 6.2
    wing_y0, wing_y1 = y0 + 5.5, y0 + 16.0
    wing_ridge_x = (wing_x0 + wing_x1) / 2
    wing_z = 10.6
    geom.face([(wing_x0, wing_y0, 4.3), (wing_ridge_x, wing_y0, wing_z),
               (wing_ridge_x, wing_y1, wing_z), (wing_x0, wing_y1, 4.3)], 1)
    geom.face([(wing_ridge_x, wing_y0, wing_z), (wing_x1, wing_y0, 4.3),
               (wing_x1, wing_y1, 4.3), (wing_ridge_x, wing_y1, wing_z)], 1)

    # North-facing gable: teal cladding follows the swept asymmetric profile
    # seen in the church photos and surrounds the triangular stained-glass
    # field. The exact curve and peak offset are visual estimates.
    peak = (ridge_x + 1.0, y_front + 0.08, SWEPT_GABLE_HEIGHT_M)
    left_base = (x0 + 3.5, y_front + 0.08, WALL_HEIGHT_M)
    right_base = (x1, y_front + 0.08, WALL_HEIGHT_M)
    profile = [
        left_base,
        (x0 + 5.8, y_front + 0.08, 7.5),
        (x0 + 9.2, y_front + 0.08, 11.2),
        (ridge_x - 2.0, y_front + 0.08, 14.3),
        peak,
        (ridge_x + 3.4, y_front + 0.08, 14.6),
        (ridge_x + 6.6, y_front + 0.08, 11.8),
        (x1 - 2.0, y_front + 0.08, 8.1),
        right_base,
    ]
    profile_vecs=[Vector(p) for p in profile]
    for tri in tessellate_polygon([profile_vecs]):
        geom.face([profile_vecs[i] for i in tri], 2)
    # Main triangular window inset within the gable.
    glass_left = (ridge_x - 4.0, y_front + 0.18, 5.35)
    glass_right = (ridge_x + 4.6, y_front + 0.18, 5.35)
    glass_peak = (ridge_x + 0.7, y_front + 0.18, 12.2)
    # Two stained-glass fields and a restrained pale mullion network.
    split_x = ridge_x + 0.5
    geom.face([glass_left, glass_peak, (split_x, y_front + 0.18, 5.35)], 4)
    geom.face([glass_peak, glass_right, (split_x, y_front + 0.18, 5.35)], 3)
    # Narrow framing follows the triangular glazing without oversized bars.
    for xa in [ridge_x - 2.3, ridge_x + 2.2]:
        ztop = 12.2 - max(0.0, abs(xa - (ridge_x + 0.7))) * (6.85 / 8.6)
        geom.face([(xa - 0.035, y_front + 0.22, 5.35),
                   (xa + 0.035, y_front + 0.22, 5.35),
                   (xa + 0.035, y_front + 0.22, ztop),
                   (xa - 0.035, y_front + 0.22, ztop)], 5)
    geom.face([(ridge_x - 3.9, y_front + 0.22, 8.4),
               (ridge_x + 4.45, y_front + 0.22, 8.4),
               (ridge_x + 4.45, y_front + 0.22, 8.5),
               (ridge_x - 3.9, y_front + 0.22, 8.5)], 5)

    # Main entrance and adjacent glazing, placed on the photographed north
    # facade; exact door offset is estimated from perspective photos.
    facade_y = y_front + 0.17
    entry_center_x = x0 + 5.2
    geom.face([(entry_center_x - 1.5, facade_y, 0.15),
               (entry_center_x + 1.5, facade_y, 0.15),
               (entry_center_x + 1.5, facade_y, 3.0),
               (entry_center_x - 1.5, facade_y, 3.0)], 6)
    # Side windows on south/east elevation, broad massing openings only.
    side_edges = []
    for i, (ax, ay) in enumerate(xy):
        bx, by = xy[(i + 1) % len(xy)]
        if abs(ax-bx) < 0.15 and max(ay, by) - min(ay, by) > 12:
            side_edges.append((ax, min(ay,by), max(ay,by), 1 if ax > xmid else -1))
    for ex, low, high, side in side_edges:
        tangent = (0, 1)
        normal = (side, 0)
        count = max(1, int((high-low) / 6.0))
        for j in range(count):
            cy = low + (j + 0.5) * (high-low) / count
            geom.box_on_plane((ex, cy), tangent, normal, 1.25, 1.45, 2.5, 3, depth=0.08)

    # Roof cross shown in the church's own north/east-facing photograph.
    cross_y = y_front + 0.44
    cross_x = peak[0]
    stem_w, arm_w = 0.26, 1.05
    geom.face([(cross_x-stem_w/2,cross_y,16.05),(cross_x+stem_w/2,cross_y,16.05),
               (cross_x+stem_w/2,cross_y,CROSS_TOP_M),(cross_x-stem_w/2,cross_y,CROSS_TOP_M)], 5)
    geom.face([(cross_x-arm_w/2,cross_y,17.15),(cross_x+arm_w/2,cross_y,17.15),
               (cross_x+arm_w/2,cross_y,17.4),(cross_x-arm_w/2,cross_y,17.4)], 5)

    new_mesh = bpy.data.meshes.new(f"{ASSET_ID}_mesh")
    new_mesh.from_pydata(geom.vertices, [], geom.faces)
    new_mesh.update()
    for mat in mats:
        new_mesh.materials.append(mat)
    for poly, mat_id in zip(new_mesh.polygons, geom.material_ids):
        poly.material_index = mat_id
    bm = bmesh.new()
    bm.from_mesh(new_mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(new_mesh)
    bm.free()
    obj.data = new_mesh
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)
    new_mesh.name = f"{ASSET_ID}_mesh"
    bpy.context.view_layer.update()

    depsgraph = bpy.context.evaluated_depsgraph_get()
    eobj = obj.evaluated_get(depsgraph)
    bounds = [[min((eobj.matrix_world @ Vector(c))[i] for c in eobj.bound_box),
               max((eobj.matrix_world @ Vector(c))[i] for c in eobj.bound_box)]
              for i in range(3)]
    plan_area = abs(sum(xy[i][0] * xy[(i+1)%len(xy)][1] -
                        xy[(i+1)%len(xy)][0] * xy[i][1] for i in range(len(xy))) / 2)
    metrics = {
        "asset_id": ASSET_ID,
        "identity": {"OSM_way": 860901797, "name": tags["name"],
                     "address": f'{tags["addr:housenumber"]} {tags["addr:street"]}, {tags["addr:city"]}, {tags["addr:state"]}',
                     "amenity": tags["amenity"], "website": tags["website"],
                     "source_timestamp": osm_meta.get("timestamp")},
        "footprint": {"source_coordinate_system": "WGS 84 EPSG:4326", "unique_vertices": len(xy),
                      "transformed_bounds_xy_m": [[min(p[i] for p in xy), max(p[i] for p in xy)] for i in range(2)],
                      "approximate_local_area_m2": plan_area,
                      "transform": "X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040"},
        "evaluated_bounds_world_m": bounds,
        "vertical_estimates_m": {"wall_eave": WALL_HEIGHT_M, "main_ridge": RIDGE_HEIGHT_M,
                                  "raised_gable": SWEPT_GABLE_HEIGHT_M, "cross_top": CROSS_TOP_M},
        "mesh": {"vertices": len(new_mesh.vertices), "faces": len(new_mesh.polygons),
                 "materials": [m.name for m in new_mesh.materials], "object_count_in_export_collection": 1},
        "uncertainty": ["No dimensioned elevations or measured height source found; all roof/wall heights and pitch are estimates from unscaled perspective images.",
                        "OSM is a community-maintained footprint source; name/address/website tags match the official church page and footprint is contained at the official map pin.",
                        "The GIS queue's FID 823 maps to Fairway, 1320 David Ross Rd, and is not this church."],
    }

    scene = bpy.context.scene
    temp_objects = []
    cam_data = bpy.data.cameras.new("OSLC_preview_camera")
    cam = bpy.data.objects.new("OSLC_preview_camera", cam_data)
    scene.collection.objects.link(cam)
    temp_objects.append(cam)
    center = Vector(((bounds[0][0]+bounds[0][1])/2,
                     (bounds[1][0]+bounds[1][1])/2,
                     (bounds[2][0]+bounds[2][1])/2))
    cam.location = center + Vector((-25, 57, 17))
    cam.rotation_euler = (center-cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 50
    scene.camera = cam
    old_engine = scene.render.engine
    old_res = (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage)
    old_filepath = scene.render.filepath
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
        scene.render.filepath = str(PREVIEW)
        scene.world.color = (0.72, 0.72, 0.72)
        bpy.ops.render.render(write_still=True)
    finally:
        scene.camera = None
        for temp in temp_objects:
            bpy.data.objects.remove(temp, do_unlink=True)
        scene.render.engine = old_engine
        scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = old_res
        scene.render.filepath = old_filepath

    AUDIT.mkdir(parents=True, exist_ok=True)
    METRICS.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
