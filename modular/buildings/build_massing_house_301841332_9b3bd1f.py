"""Build the stable FID 762 library for current Zeta Beta Tau occupancy.

The GIS ring supports the horizontal roof projection only. Facade appearance is
guided by ZBT's national chapter-house photo (uploaded 2017) and the current
chapter website image; floor count, dimensions above grade, and hidden faces are
estimates. Run from the repository root with Blender 5.2.3:

    blender -b --python modular/buildings/build_massing_house_301841332_9b3bd1f.py
"""
from __future__ import annotations

import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "zeta_beta_tau"
SOURCE = AUDIT / "sources" / "purdue_gis_fid762_2026-10-26_wgs84.json"
ASSET_ID = "massing_house_301841332_9b3bd1f"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
SCENE_NAME = f"Building_{ASSET_ID}"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
TRANSFORM = {
    "x": "(longitude + 86.9137) * 111412.84 * cos(radians(40.4274))",
    "y": "(latitude - 40.4274) * 111040.0",
    "z": "meters above local model ground; not a surveyed elevation",
    "geographic_origin_lat_lon": [40.4274, -86.9137],
}


def xy_from_lonlat(lon: float, lat: float) -> tuple[float, float]:
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    y = (lat - 40.4274) * 111040.0
    return x, y


def polygon_area(points: list[tuple[float, float]]) -> float:
    return 0.5 * sum(
        points[i][0] * points[(i + 1) % len(points)][1]
        - points[(i + 1) % len(points)][0] * points[i][1]
        for i in range(len(points))
    )


def material(name: str, color: tuple[float, float, float, float], roughness=0.72,
             metallic=0.0) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def mesh_object(name: str, verts, faces, materials, collection,
                material_indices=None) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.clear()
    for mat in materials:
        mesh.materials.append(mat)
    mesh.validate(clean_customdata=False)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if material_indices:
        for poly, idx in zip(mesh.polygons, material_indices):
            poly.material_index = idx
    return obj


def extrusion_surface(name, ring, z_bands, materials, collection):
    """One continuous polygon shell, with side-face bands and a flat top cap."""
    n = len(ring)
    verts = [(x, y, z) for z in z_bands for x, y in ring]
    faces, indices = [], []
    # For a CCW ring, this order points side faces outward.
    for bi in range(len(z_bands) - 1):
        material_index = min(bi, len(materials) - 1)
        for i in range(n):
            j = (i + 1) % n
            faces.append((bi * n + i, bi * n + j,
                          (bi + 1) * n + j, (bi + 1) * n + i))
            indices.append(material_index)
    # The GIS ring was closed before this function; this top polygon is the
    # best available roof projection. It is not asserted to be a wall survey.
    faces.append(tuple((len(z_bands) - 1) * n + i for i in range(n)))
    indices.append(len(materials) - 1)
    return mesh_object(name, verts, faces, materials, collection, indices)


def box_mesh(name, center, tangent, normal, width, depth, z0, z1, mat, collection):
    c = Vector(center)
    t = Vector(tangent).normalized()
    no = Vector(normal).normalized()
    verts = []
    for z in (z0, z1):
        for along, out in ((-width / 2, -depth / 2),
                           (width / 2, -depth / 2),
                           (width / 2, depth / 2),
                           (-width / 2, depth / 2)):
            q = c + t * along + no * out
            verts.append((q.x, q.y, z))
    faces = [(0, 3, 2, 1), (4, 5, 6, 7),
             (0, 1, 5, 4), (1, 2, 6, 5),
             (2, 3, 7, 6), (3, 0, 4, 7)]
    return mesh_object(name, verts, faces, [mat], collection)


def add_window_quads(edge_a, tangent, normal, along, z_center, width, height,
                     wall_offset, glass_mat, frame_mat, sill_mat, verts,
                     faces, indices):
    c = Vector((edge_a[0], edge_a[1], 0.0)) + Vector(tangent) * along + Vector(normal) * wall_offset
    t, no = Vector(tangent), Vector(normal)
    outer_w = width + 0.28
    outer_h = height + 0.28

    def quad(cx, cz, w, h, off):
        p = c + t * cx + no * off
        return [(p.x - t.x * w / 2, p.y - t.y * w / 2, cz - h / 2),
                (p.x + t.x * w / 2, p.y + t.y * w / 2, cz - h / 2),
                (p.x + t.x * w / 2, p.y + t.y * w / 2, cz + h / 2),
                (p.x - t.x * w / 2, p.y - t.y * w / 2, cz + h / 2)]

    def add_panel(cx, cz, w, h, off, mat_index):
        first = len(verts)
        verts.extend(quad(cx, cz, w, h, off))
        faces.append((first, first + 1, first + 2, first + 3))
        indices.append(mat_index)

    add_panel(0, z_center, outer_w, outer_h, 0.012, 1)  # light trim surround
    add_panel(0, z_center, width, height, 0.024, 0)     # dark glazed pane
    mullion_w = 0.075
    add_panel(0, z_center, mullion_w, height, 0.038, 2)
    add_panel(0, z_center, width, 0.075, 0.038, 2)
    add_panel(0, z_center - height * 0.20, width, 0.055, 0.038, 2)


def add_sign(edge_a, tangent, normal, along, z_center, collection, sign_mat):
    t = Vector(tangent).normalized()
    no = Vector(normal).normalized()
    p = Vector((edge_a[0], edge_a[1], 0.0)) + t * along + no * 0.07
    text = bpy.data.curves.new("ZBT_Frontage_Sign_Type", type="FONT")
    text.body = "ZBT"
    text.align_x = "CENTER"
    text.align_y = "CENTER"
    text.size = 1.6
    text.extrude = 0.018
    obj = bpy.data.objects.new("ZBT_Frontage_Sign", text)
    collection.objects.link(obj)
    # Local text X follows the wall; local Y is vertical; local Z faces out.
    orient = Matrix(((t.x, 0.0, no.x),
                     (t.y, 0.0, no.y),
                     (0.0, 1.0, 0.0)))
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = orient.to_quaternion()
    obj.location = (p.x, p.y, z_center)
    obj.data.materials.append(sign_mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj.select_set(False)
    return bpy.data.objects.get("ZBT_Frontage_Sign")


def add_oriented_mesh_box(name, center, tangent, normal, width, depth, z0,
                          z1, mat, collection):
    return box_mesh(name, center, tangent, normal, width, depth, z0, z1,
                    mat, collection)


def configure_preview(scene, center, front_normal, front_tangent, materials):
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "AgX"
    scene.render.filepath = str(AUDIT / "zbt_preview.png")

    world = bpy.data.worlds.new("ZBT_Preview_World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.48, 0.55, 0.63, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.55
    scene.world = world

    plane_mesh = bpy.data.meshes.new("ZBT_Preview_Ground_Mesh")
    plane_mesh.from_pydata([(-80, -80, -0.12), (80, -80, -0.12),
                            (80, 80, -0.12), (-80, 80, -0.12)], [], [(0, 1, 2, 3)])
    plane_mesh.materials.append(materials["ground"])
    plane = bpy.data.objects.new("ZBT_Preview_Ground", plane_mesh)
    scene.collection.objects.link(plane)

    t = Vector(front_tangent).normalized()
    no = Vector(front_normal).normalized()
    target = Vector((center[0], center[1], 4.0))
    cam_data = bpy.data.cameras.new("ZBT_Preview_Camera")
    camera = bpy.data.objects.new("ZBT_Preview_Camera", cam_data)
    scene.collection.objects.link(camera)
    camera.location = target + no * 95.0 + t * 16.0 + Vector((0, 0, 41))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 80.0
    scene.camera = camera

    light_data = bpy.data.lights.new("ZBT_Preview_Area", type="AREA")
    light = bpy.data.objects.new("ZBT_Preview_Area", light_data)
    scene.collection.objects.link(light)
    light.location = target + Vector((30, -20, 55))
    light.data.energy = 18000
    light.data.shape = "DISK"
    light.data.size = 55
    light.rotation_euler = (target - light.location).to_track_quat("-Z", "Y").to_euler()


def main():
    AUDIT.mkdir(parents=True, exist_ok=True)
    src = json.loads(SOURCE.read_text(encoding="utf8"))
    if not src.get("features") or len(src["features"]) != 1:
        raise RuntimeError("Expected exactly one saved Purdue GIS feature")
    feature = src["features"][0]
    attrs = feature["attributes"]
    if attrs.get("FID") != 762 or attrs.get("ADDRESS", "").strip() != "900 David Ross Rd":
        raise RuntimeError(f"Unexpected source crosswalk: FID={attrs.get('FID')} address={attrs.get('ADDRESS')}")

    source_ring = feature["geometry"]["rings"][0]
    if len(source_ring) > 1 and source_ring[0] == source_ring[-1]:
        source_ring = source_ring[:-1]
    ring = [xy_from_lonlat(float(lon), float(lat)) for lon, lat in source_ring]
    if polygon_area(ring) < 0:
        ring.reverse()
    area = abs(polygon_area(ring))
    bounds = [[min(p[i] for p in ring), max(p[i] for p in ring)] for i in range(2)]
    center = ((bounds[0][0] + bounds[0][1]) / 2,
              (bounds[1][0] + bounds[1][1]) / 2)

    # Start with a clean file while preserving the stable scene/collection names.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.data.scenes.new(SCENE_NAME)
    bpy.context.window.scene = scene
    collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(collection)

    mats = {
        "foundation": material("ZBT_Warm_Stone_Base", (0.39, 0.34, 0.29, 1)),
        "wall": material("ZBT_Light_Warm_Facade", (0.70, 0.65, 0.57, 1)),
        "belt": material("ZBT_Floor_Band", (0.82, 0.77, 0.68, 1)),
        "parapet": material("ZBT_Parapet_Face", (0.58, 0.58, 0.55, 1)),
        "roof": material("ZBT_Light_Flat_Roof", (0.70, 0.72, 0.69, 1)),
        "glass": material("ZBT_Blue_Grey_Glazing", (0.085, 0.14, 0.18, 1), roughness=0.22, metallic=0.1),
        "frame": material("ZBT_Light_Window_Frames", (0.82, 0.79, 0.72, 1), roughness=0.42),
        "mullion": material("ZBT_Window_Mullions", (0.50, 0.50, 0.47, 1), roughness=0.42),
        "sign": material("ZBT_Sign_Letters", (0.16, 0.19, 0.20, 1), roughness=0.45),
        "wood": material("ZBT_Deck_Dark_Wood", (0.20, 0.15, 0.11, 1), roughness=0.86),
        "ground": material("ZBT_Preview_Ground_Material", (0.32, 0.38, 0.31, 1)),
    }

    # Two visible facade levels and a shallow parapet are photo-guided estimates.
    z0, zbase, zmid, zband, zeaves, zroof = 0.0, 0.42, 3.55, 3.72, 7.05, 7.65
    levels = [z0, zbase, zmid, zband, zeaves, zroof]
    bands = [mats["foundation"], mats["wall"], mats["belt"], mats["wall"], mats["parapet"]]
    # The final cap material is the light roof membrane.
    shell_mats = bands + [mats["roof"]]
    extrusion_surface("ZBT_Main_Envelope_FID762", ring, levels, shell_mats, collection)

    # Photo-facing elevations are not georeferenced to a surveyed wall. The
    # southeast-facing longest wall is selected from the aerial/context shape;
    # only its broad window rhythm and deck are photo-supported.
    edges = []
    for i, a in enumerate(ring):
        b = ring[(i + 1) % len(ring)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length < 1.0:
            continue
        tangent = Vector((dx / length, dy / length, 0))
        normal = Vector((tangent.y, -tangent.x, 0))
        edges.append((length, a, b, tangent, normal, i))
    front = max(edges, key=lambda e: e[0])
    front_len, front_a, front_b, front_t, front_n, front_index = front

    # Repeated large rectangular windows reflect both available chapter photos;
    # bays on unpictured elevations are schematic and noted in the evidence.
    window_verts, window_faces, window_indices = [], [], []
    for length, a, b, tangent, normal, edge_index in edges:
        if length < 8.0:
            continue
        usable = max(0, length - 3.2)
        count = max(1, int(usable // 5.0))
        spacing = usable / count if count else 0
        width = min(2.05, max(1.15, spacing * 0.55))
        for floor_z in (1.92, 5.08):
            for wi in range(count):
                along = 1.6 + spacing * (wi + 0.5)
                add_window_quads(a, tangent, normal, along, floor_z,
                                 width, 1.45, 0.02, mats["glass"], mats["frame"],
                                 mats["mullion"], window_verts, window_faces,
                                 window_indices)
    mesh_object("ZBT_Facade_Window_Bays", window_verts, window_faces,
                [mats["glass"], mats["frame"], mats["mullion"]], collection,
                window_indices)

    front_mid = (front_a[0] + (front_b[0] - front_a[0]) * 0.5,
                 front_a[1] + (front_b[1] - front_a[1]) * 0.5)
    add_sign(front_a, front_t, front_n, front_len * 0.5, 3.55,
             collection, mats["sign"])

    # The national/current chapter photos show a long timber-railed frontage deck.
    deck_width = min(34.0, front_len * 0.80)
    deck_center = Vector((front_mid[0], front_mid[1], 0.0)) + front_n * 1.0
    add_oriented_mesh_box("ZBT_Front_Deck", deck_center, front_t, front_n,
                          deck_width, 2.05, 0.55, 0.82, mats["wood"], collection)
    rail_z0, rail_z1 = 0.84, 1.83
    # Three dark horizontal rails along the outside edge.
    for ri, z in enumerate((1.05, 1.38, 1.73)):
        add_oriented_mesh_box(f"ZBT_Deck_Rail_{ri+1}",
                              deck_center + front_n * 1.00,
                              front_t, front_n, deck_width, 0.10,
                              z, z + 0.10, mats["wood"], collection)
    post_verts, post_faces = [], []
    # Posts every ~2.5 m are combined in a single mesh object.
    post_count = max(2, int(deck_width / 2.5) + 1)
    for i in range(post_count):
        along = -deck_width / 2 + deck_width * i / (post_count - 1)
        c = deck_center + front_t * along + front_n * 1.0
        base_idx = len(post_verts)
        for z in (0.82, 1.85):
            for u, v in ((-0.06, -0.06), (0.06, -0.06),
                          (0.06, 0.06), (-0.06, 0.06)):
                p = c + front_t * u + front_n * v
                post_verts.append((p.x, p.y, z))
        post_faces.extend([(base_idx+a, base_idx+b, base_idx+c, base_idx+d)
                           for a,b,c,d in ((0,3,2,1),(4,5,6,7),(0,1,5,4),
                                           (1,2,6,5),(2,3,7,6),(3,0,4,7))])
    mesh_object("ZBT_Deck_Railing_Posts", post_verts, post_faces,
                [mats["wood"]], collection)

    # Simple centered stair treads; their exact position and dimensions are not
    # visible in the chapter photographs, so they remain schematic.
    stair_center = deck_center + front_n * 1.3
    for i in range(4):
        width = 3.0 - i * 0.12
        ztop = 0.52 - i * 0.13
        c = stair_center + front_n * (i * 0.34)
        add_oriented_mesh_box(f"ZBT_Front_Stair_Tread_{i+1}", c,
                              front_t, front_n, width, 0.45,
                              max(0.02, ztop - 0.13), ztop, mats["wood"], collection)

    # Keep preview ground/camera/lights outside the exported asset collection.
    configure_preview(scene, center, front_n, front_t, mats)
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.resolution_percentage = 100
    scene.camera.data.dof.use_dof = False
    scene.render.filepath = str(AUDIT / "zbt_preview.png")

    # Only the building's collection is exported to linked campus files.
    bpy.context.window.scene = scene
    scene.render.filepath = str(AUDIT / "zbt_preview.png")
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))

    mesh_objects = [o for o in collection.objects if o.type == "MESH"]
    record = {
        "building": "Zeta Beta Tau — Alpha Alpha, Purdue University",
        "asset_id": ASSET_ID,
        "asset_path": "modular/buildings/" + ASSET_PATH.name,
        "collection": COLLECTION_NAME,
        "scene": SCENE_NAME,
        "source": {
            "provider": "Purdue University GIS",
            "feature_id": 762,
            "feature_name": attrs.get("BUILDING_N"),
            "address": attrs.get("ADDRESS"),
            "source_crs": "EPSG:4326 (ArcGIS outSR=4326)",
            "source_url": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D762&outFields=*&returnGeometry=true&outSR=4326&f=pjson",
            "snapshot": "audit/zeta_beta_tau/sources/purdue_gis_fid762_2026-10-26_wgs84.json",
            "retrieved": "2026-10-26",
            "source_geometry_date": "not populated by service",
            "identity_note": "FID 762 is at the current official ZBT address; the GIS name is the historic/conflicting Phi Kappa Theta label. See crosswalk_resolution.md.",
        },
        "transform": TRANSFORM,
        "footprint": {
            "ring_vertex_count_closed": len(source_ring) + 1,
            "ring_vertex_count_unique": len(ring),
            "area_m2_from_transformed_ring": round(area, 3),
            "bounds_world_m": [[round(v, 3) for v in row] for row in bounds],
            "maximum_bbox_dimensions_m": [round(bounds[0][1]-bounds[0][0], 3), round(bounds[1][1]-bounds[1][0], 3)],
            "comparison": "The main envelope and flat roof projection use the transformed GIS ring. GIS footprint is a map/roof outline, not a surveyed wall-face survey.",
            "Shape__Area_attribute": attrs.get("Shape__Area"),
            "area_attribute_units": "undocumented; conflicts with transformed ring area and not used for geometry",
        },
        "geometry_edits": [
            "Replaced the generic 4-corner 16 m extrusion with a source-ring 12-corner envelope and flat roof.",
            "Added two photo-guided facade levels, repeated glazing, and a shallow flat-roof parapet.",
            "Added the long front deck, railings, schematic entry stair, and ZBT frontage sign from chapter-photo cues.",
            "Preserved the stable asset path, ID, collection, scene, and campus-world XY frame.",
        ],
        "dimensions": {
            "ground_z_m": 0.0,
            "roof_top_z_m": zroof,
            "height_status": "estimated from two visible facade levels and person/window proportions in chapter photos; not measured",
            "story_count": 2,
            "story_count_status": "photo-guided estimate; GIS NUM_LEVELS=1 is retained as conflicting legacy metadata",
            "roof_form": "flat/low-slope roof with shallow parapet; visually supported by current official chapter photo and aerial imagery; exact pitch/elevation unknown",
            "orientation_status": "FID 762 roof ring orientation verified in campus transform; frontage edge inferred from the longest face and aerial context, not a georeferenced facade photo",
            "frontage_edge_index_in_transformed_ccw_ring": front_index,
            "frontage_edge_length_m": round(front_len, 3),
            "frontage_outward_normal_xy": [round(front_n.x, 6), round(front_n.y, 6)],
        },
        "facade_evidence": [
            {"url": "https://zbt.org/undergraduates/chapter-locator/alpha-alpha-purdue-university/", "provider": "Zeta Beta Tau International", "source_date": "photo upload path 2017/10; capture date unknown", "supports": "Alpha Alpha chapter house identity, ZBT/900 David Ross signage, broad light facade, broad horizontal timber-railed deck."},
            {"url": "https://zbtpurdue.com/", "provider": "Zeta Beta Tau at Purdue", "source_date": "homepage accessed 2026-10-26; image path 2024/08; image capture date unknown", "supports": "Current ZBT identity and current photo cues: broad light facade, large regular glazing, shallow flat roof edge, long deck/railing."},
            {"url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export", "provider": "Esri World Imagery mosaic", "source_date": "mosaic capture date not supplied; accessed 2026-10-26", "source_crs": "EPSG:3857 request; 1000x750; bbox -9676616.3,4929120,-9676316.3,4929345 m", "supports": "Aerial roof context and broad source-ring alignment; see audit/zeta_beta_tau/fid762_aerial_overlay.png."},
        ],
        "uncertainty": [
            "The GIS polygon and `Shape__Area` field disagree; the field's units are undocumented, and the transformed polygon area was used for horizontal geometry.",
            "Purdue GIS retains Phi Kappa Theta (`SOFKH`) at the same address; current ZBT sources support present occupancy, but transition date and any temporary shared occupancy are unknown.",
            "The facade photographs are not georeferenced elevations; the frontage edge and window spacing are estimated, and unpictured sides are schematic.",
            "The GIS's Extrution=36 has undocumented units and NUM_LEVELS=1; neither is used as a measured height or story count.",
            "No interior plan, measured wall line, roof survey, or surveyed vertical datum was found; interior layout is not modeled.",
        ],
        "blender_version": bpy.app.version_string,
        "mesh_object_count_in_export_collection": len(mesh_objects),
        "preview_render": "audit/zeta_beta_tau/zbt_preview.png",
        "asset_sha256": hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest(),
        "validation": "Build candidate; fresh reopen and independent grade pending.",
    }
    (AUDIT / "build_evidence.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf8")
    print("ZBT_BUILD_RECORD=" + json.dumps(record))


if __name__ == "__main__":
    main()
