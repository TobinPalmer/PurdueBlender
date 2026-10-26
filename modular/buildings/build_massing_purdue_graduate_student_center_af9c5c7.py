"""Build a source-backed PGSC facade/interior asset in the project local frame.

The PGSC is the brick office/student-center frontage within the Northwestern
Avenue Parking Garage, not the entire parking garage.  The GIS source defines
the PGSC portion; this asset deliberately models that low-volume component and
does not recreate the garage's upper parking decks.
"""
import bpy
import bmesh
import json
import math
from pathlib import Path
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
MODULAR = ROOT / "modular"
EVIDENCE = ROOT / "audit" / "purdue_graduate_student_center"
SOURCE = EVIDENCE / "sources" / "purdue_gis_pgsc_fid526_2026-10-26.geojson"
ASSET_ID = "massing_purdue_graduate_student_center_af9c5c7"
COLLECTION_NAME = "Asset_" + ASSET_ID
SCENE_NAME = "Building_" + ASSET_ID
ASSET_PATH = MODULAR / "buildings" / (ASSET_ID + ".blend")

GEO_ORIGIN_LAT = 40.4274
GEO_ORIGIN_LON = -86.9137
LON_METERS_AT_ORIGIN = 111412.84 * math.cos(math.radians(GEO_ORIGIN_LAT))
LAT_METERS = 111040.0
WALL_HEIGHT = 3.65  # GIS Extrution=12 is retained as an ambiguous source value; 12 ft is plausible, not proven.
CANOPY_HEIGHT = 3.25


def make_material(name, color, roughness=0.75, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    principled = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    principled.inputs["Base Color"].default_value = (*color, 1.0)
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Metallic"].default_value = metallic
    return mat


def make_brick_material():
    mat = make_material("PGSC | warm red-brown modular brick", (0.33, 0.105, 0.067), 0.88)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    texcoord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
    brick = nodes.new("ShaderNodeTexBrick")
    brick.inputs["Color1"].default_value = (0.40, 0.12, 0.075, 1.0)
    brick.inputs["Color2"].default_value = (0.26, 0.065, 0.043, 1.0)
    brick.inputs["Mortar"].default_value = (0.68, 0.60, 0.50, 1.0)
    brick.inputs["Scale"].default_value = 2.5
    brick.inputs["Mortar Size"].default_value = 0.035
    brick.inputs["Mortar Smooth"].default_value = 0.015
    brick.inputs["Brick Width"].default_value = 0.52
    brick.inputs["Row Height"].default_value = 0.25
    # Object-space X/Z provides true horizontal courses on upright wall objects;
    # using X/Y here makes the thin wall depth look like vertical stripes.
    separate = nodes.new("ShaderNodeSeparateXYZ")
    combine = nodes.new("ShaderNodeCombineXYZ")
    links.new(texcoord.outputs["Object"], separate.inputs["Vector"])
    links.new(separate.outputs["X"], combine.inputs["X"])
    links.new(separate.outputs["Z"], combine.inputs["Y"])
    links.new(combine.outputs["Vector"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], brick.inputs["Vector"])
    links.new(brick.outputs["Color"], principled.inputs["Base Color"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.14
    bump.inputs["Distance"].default_value = 0.025
    links.new(brick.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    return mat


def cube(name, loc, dims, mat, collection, angle=0.0, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    obj.rotation_euler[2] = angle
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Soft dressed edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.affect = "EDGES"
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def local_xy(lon, lat, anchor):
    x = (lon - GEO_ORIGIN_LON) * LON_METERS_AT_ORIGIN
    y = (lat - GEO_ORIGIN_LAT) * LAT_METERS
    return (x - anchor[0], y - anchor[1])


def signed_area(points):
    return 0.5 * sum(points[i][0] * points[(i + 1) % len(points)][1]
                      - points[(i + 1) % len(points)][0] * points[i][1]
                      for i in range(len(points)))


def outward_normal(a, b, area):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if area > 0:  # CCW boundary: exterior lies to the right.
        return (dy / length, -dx / length)
    return (-dy / length, dx / length)


def facade_box(name, a, b, start, end, z0, z1, depth, offset, mat, collection, area, bevel=0.0):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    angle = math.atan2(dy, dx)
    n = outward_normal(a, b, area)
    t = (start + end) * 0.5
    loc = (a[0] + dx * t + n[0] * offset,
           a[1] + dy * t + n[1] * offset,
           (z0 + z1) * 0.5)
    return cube(name, loc, (length * (end - start), depth, z1 - z0), mat, collection, angle, bevel)


def build_shell(points, wall_mat, roof_mat, collection, wall_height):
    n = len(points)
    verts = [(x, y, z) for z in (0.0, wall_height) for x, y in points]
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    mesh = bpy.data.meshes.new("PGSC surveyed wall footprint shell")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(wall_mat)
    mesh.materials.append(roof_mat)
    for poly in mesh.polygons:
        poly.material_index = 1 if poly.index == 1 else 0
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new("PGSC source-footprint brick volume (garage office portion)", mesh)
    collection.objects.link(obj)
    return obj


def orient_text(obj, tangent, normal):
    xaxis = Vector((tangent[0], tangent[1], 0.0)).normalized()
    zaxis = Vector((normal[0], normal[1], 0.0)).normalized()
    yaxis = Vector((0.0, 0.0, 1.0))
    if xaxis.cross(yaxis).dot(zaxis) < 0.0:
        xaxis.negate()
    basis = Matrix((xaxis, yaxis, zaxis)).transposed()
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = basis.to_quaternion()


def setup_scene(scene):
    scene.unit_settings.system = "METRIC"
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    engines = [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    scene.render.engine = next((e for e in engines if "BLENDER_EEVEE_NEXT" == e), engines[0])
    scene.view_settings.view_transform = "AgX"
    scene.render.film_transparent = False
    world = bpy.data.worlds.new("PGSC neutral daylight")
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.36, 0.44, 0.56, 1.0)
    bg.inputs["Strength"].default_value = 0.48
    scene.world = world


def main():
    with SOURCE.open("r", encoding="utf-8") as f:
        fc = json.load(f)
    features = fc.get("features", [])
    feature = next(f for f in features if int(f.get("id", -1)) == 526)
    ring_ll = feature["geometry"]["coordinates"][0]
    world_points = [((lon - GEO_ORIGIN_LON) * LON_METERS_AT_ORIGIN,
                     (lat - GEO_ORIGIN_LAT) * LAT_METERS) for lon, lat in ring_ll[:-1]]
    bounds = [[min(p[i] for p in world_points), max(p[i] for p in world_points)] for i in range(2)]
    anchor = ((bounds[0][0] + bounds[0][1]) * 0.5,
              (bounds[1][0] + bounds[1][1]) * 0.5)
    points = [local_xy(lon, lat, anchor) for lon, lat in ring_ll[:-1]]
    area = signed_area(points)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    scene["asset_id"] = ASSET_ID
    scene["coordinate_frame"] = "local; Placement marker supplies campus XY"
    scene["placement_origin_xy_m"] = list(anchor)
    setup_scene(scene)

    root = scene.collection
    asset = bpy.data.collections.new(COLLECTION_NAME)
    asset["asset_id"] = ASSET_ID
    asset["coordinate_frame"] = "local; Placement marker supplies campus XY"
    asset["placement_origin_xy_m"] = list(anchor)
    root.children.link(asset)

    brick = make_brick_material()
    concrete = make_material("PGSC | precast garage concrete", (0.56, 0.55, 0.51), 0.82)
    trim = make_material("PGSC | charcoal anodized aluminum", (0.09, 0.12, 0.13), 0.3, 0.55)
    glass = make_material("PGSC | smoked storefront glazing", (0.032, 0.085, 0.105), 0.16, 0.18)
    door_glass = make_material("PGSC | entry glass", (0.055, 0.14, 0.17), 0.12, 0.12)
    sign_mat = make_material("PGSC | cream white dimensional lettering", (0.9, 0.86, 0.72), 0.32, 0.1)
    interior_floor = make_material("PGSC | warm interior terrazzo", (0.40, 0.36, 0.30), 0.74)
    interior_wall = make_material("PGSC | interior painted gypsum", (0.73, 0.70, 0.63), 0.8)
    furniture = make_material("PGSC | dark walnut furniture", (0.20, 0.095, 0.047), 0.68)
    seat = make_material("PGSC | lounge upholstery", (0.20, 0.25, 0.25), 0.9)

    shell = build_shell(points, brick, concrete, asset, WALL_HEIGHT)
    shell["source_footprint_feature"] = "Purdue GIS BuildingShapesZip4 FeatureServer/0, FID 526"
    shell["vertical_status"] = "estimated: 3.65m; GIS Extrution=12 has undocumented units"
    # Existing records identify the PGSC frontage as an office/student-center portion of the garage.
    # Its visible southwest-facing street edge is the GIS boundary chain 2-5.
    front_indices = [2, 3, 4, 5]
    # Interior ground plane and facade-specific features stay inside this one GIS-derived shell.
    floor_mesh = bpy.data.meshes.new("PGSC interior floor outline")
    floor_mesh.from_pydata([(x, y, 0.12) for x, y in points], [], [tuple(range(len(points)))])
    floor_mesh.materials.append(interior_floor)
    floor = bpy.data.objects.new("PGSC interior floor | schematic", floor_mesh)
    asset.objects.link(floor)

    # Front canopy broken at GIS corners, matching the long brick-and-glass entry edge in 2025 photos.
    for idx in front_indices:
        a, b = points[idx], points[(idx + 1) % len(points)]
        seglen = math.dist(a, b)
        if seglen < 1.0:
            continue
        n = outward_normal(a, b, area)
        angle = math.atan2(b[1] - a[1], b[0] - a[0])
        mid = ((a[0] + b[0]) * 0.5 + n[0] * 0.95,
               (a[1] + b[1]) * 0.5 + n[1] * 0.95,
               CANOPY_HEIGHT)
        cube(f"PGSC suspended storefront canopy {idx}", mid,
             (seglen + 0.08, 1.9, 0.22), trim, asset, angle, 0.025)
        edge = (mid[0] + n[0] * 0.92, mid[1] + n[1] * 0.92, CANOPY_HEIGHT - 0.13)
        cube(f"PGSC canopy fascia {idx}", edge, (seglen, 0.12, 0.24), concrete, asset, angle, 0.015)
        # Brick piers at entrances and canopy joints.
        for t in (0.04, 0.50, 0.96):
            px = a[0] + (b[0] - a[0]) * t + n[0] * 0.11
            py = a[1] + (b[1] - a[1]) * t + n[1] * 0.11
            cube(f"PGSC brick pilaster {idx}-{t:.2f}", (px, py, WALL_HEIGHT * 0.5),
                 (0.42, 0.22, WALL_HEIGHT), brick, asset, angle, 0.018)

    # Storefront and entrance elements along the principal west/southwest-facing front.
    for idx in (2, 4, 5):
        a, b = points[idx], points[(idx + 1) % len(points)]
        seglen = math.dist(a, b)
        if seglen < 4.0:
            continue
        n = outward_normal(a, b, area)
        angle = math.atan2(b[1] - a[1], b[0] - a[0])
        if idx == 2:
            # Large lobby glazing with a paired entry at the interior end.
            facade_box("PGSC west lobby fixed storefront glazing", a, b, 0.14, 0.51,
                       0.62, 2.55, 0.065, 0.10, glass, asset, area)
            facade_box("PGSC paired glazed entry doors", a, b, 0.53, 0.75,
                       0.12, 2.45, 0.095, 0.13, door_glass, asset, area)
            # Aluminum perimeter, central stile, and door pulls.
            for t in (0.13, 0.52, 0.64, 0.76):
                x = a[0] + (b[0] - a[0]) * t + n[0] * 0.17
                y = a[1] + (b[1] - a[1]) * t + n[1] * 0.17
                cube(f"PGSC storefront mullion {t:.2f}", (x, y, 1.58),
                     (0.065, 0.055, 1.95), trim, asset, angle)
            facade_box("PGSC transom band", a, b, 0.13, 0.76, 2.53, 2.62,
                       0.06, 0.18, trim, asset, area)
        else:
            # Recessed dark window bays in brick piers, proportions read from official exterior photo.
            for j, t in enumerate((0.22, 0.68)):
                half = min(1.0 / seglen, 0.16)
                facade_box(f"PGSC lounge window {idx}-{j}", a, b, max(0.08, t-half),
                           min(0.92, t+half), 1.05, 2.15, 0.055, 0.10, glass, asset, area)
                for edge_t in (max(0.08, t-half), min(0.92, t+half)):
                    x = a[0] + (b[0]-a[0])*edge_t + n[0]*0.15
                    y = a[1] + (b[1]-a[1])*edge_t + n[1]*0.15
                    cube(f"PGSC dark window jamb {idx}-{j}-{edge_t:.2f}", (x,y,1.60),
                         (0.045,0.07,1.15),trim,asset,angle)

    # Dimensional sign on the best-supported long front face; wording and location are explicit in Purdue imagery.
    a, b = points[2], points[3]
    dx, dy = b[0]-a[0], b[1]-a[1]
    n = outward_normal(a, b, area)
    tangent = (dx, dy)
    center = ((a[0]+b[0])*0.5 + n[0]*0.20,
              (a[1]+b[1])*0.5 + n[1]*0.20, 3.47)
    curve = bpy.data.curves.new("PGSC raised entrance identification", "FONT")
    curve.body = "PURDUE GRADUATE STUDENT CENTER"
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = 0.28
    curve.extrude = 0.012
    text = bpy.data.objects.new("PGSC sign | exact name from Purdue official photo", curve)
    asset.objects.link(text)
    text.location = center
    orient_text(text, tangent, n)
    text.data.materials.append(sign_mat)

    # Schematic, source-described interior furnishing; not presented as a measured floor plan.
    # Divide the local envelope into lounge / multi-purpose / kitchen / small rooms with low-contrast partitions.
    xmin, xmax = min(p[0] for p in points), max(p[0] for p in points)
    ymin, ymax = min(p[1] for p in points), max(p[1] for p in points)
    zpart = 2.75
    cx, cy = (xmin+xmax)*0.5, (ymin+ymax)*0.5
    cube("PGSC schematic multipurpose-room partition", (cx+4.0, cy-1.0, zpart*0.5),
         (0.12, 10.0, zpart), interior_wall, asset)
    cube("PGSC schematic lounge kitchen partition", (cx-4.0, cy+1.0, zpart*0.5),
         (8.0, 0.12, zpart), interior_wall, asset)
    cube("PGSC multipurpose meeting table", (cx+4.3, cy+3.0, 0.9), (5.2, 1.35, 0.12), furniture, asset, 0.0, 0.025)
    for i in range(6):
        x = cx + 2.4 + (i % 3) * 1.75
        y = cy + 1.9 + (i // 3) * 2.2
        cube(f"PGSC multipurpose chair {i+1}", (x, y, 0.45), (0.48, 0.48, 0.08), seat, asset)
        cube(f"PGSC chair back {i+1}", (x, y+0.24, 0.76), (0.45, 0.08, 0.52), seat, asset)
    cube("PGSC lounge sofa", (cx-4.0, cy-3.1, 0.55), (3.4, 0.85, 0.65), seat, asset, 0.0, 0.08)
    cube("PGSC lounge coffee table", (cx-4.0, cy-1.6, 0.47), (1.6, 0.8, 0.10), furniture, asset)
    cube("PGSC kitchen island", (cx-5.3, cy+4.4, 0.95), (3.0, 0.75, 0.9), concrete, asset, 0.0, 0.03)
    cube("PGSC kitchenette counter", (cx-6.8, cy+5.4, 1.0), (0.7, 3.2, 0.9), furniture, asset)
    cube("PGSC study desk", (cx+5.4, cy-4.4, 0.78), (2.4, 0.9, 0.10), furniture, asset)
    cube("PGSC lobby information desk", (cx-1.0, cy-7.0, 0.62), (2.8, 0.7, 0.75), furniture, asset, 0.0, 0.03)

    # Camera and lights live outside the exported building collection.
    cam_data = bpy.data.cameras.new("PGSC preview camera")
    cam = bpy.data.objects.new("PGSC preview camera", cam_data)
    root.objects.link(cam)
    # Street-height camera approximates the 501 Northwestern Ave Street View.
    cam.location = (-25.0, -25.0, 5.4)
    target = Vector((0.0, 0.0, 2.1))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_data.lens = 47
    scene.camera = cam
    for name, loc, power, size in (
        ("PGSC warm key", (-16,-14,25), 2400, 18),
        ("PGSC facade fill", (18,-4,15), 1300, 14),
    ):
        ld = bpy.data.lights.new(name, "AREA")
        lo = bpy.data.objects.new(name, ld)
        root.objects.link(lo)
        lo.location = loc
        ld.energy = power
        ld.shape = "DISK"
        ld.size = size
        lo.rotation_euler = (Vector((0,0,1.5)) - lo.location).to_track_quat("-Z", "Y").to_euler()

    # Keep all source file references relative/portable; procedural materials need no image paths.
    bpy.context.view_layer.update()
    asset_objects = list(asset.all_objects)
    geom = [o for o in asset_objects if o.type in {"MESH", "CURVE", "FONT"}]
    world_bounds = [[min((o.matrix_world @ Vector(c))[i] for o in geom for c in o.bound_box),
                     max((o.matrix_world @ Vector(c))[i] for o in geom for c in o.bound_box)] for i in range(3)]
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    scene.render.filepath = str(EVIDENCE / "preview_three_quarter.png")
    bpy.ops.render.render(write_still=True)
    # Second evidence view isolates the source-described room program. Room dimensions and
    # partitions are schematic because no measured floor plan was found.
    exterior_prefixes = (
        "PGSC source-footprint", "PGSC suspended", "PGSC canopy fascia", "PGSC brick pilaster",
        "PGSC west lobby", "PGSC paired", "PGSC storefront", "PGSC transom", "PGSC lounge window",
        "PGSC dark window", "PGSC sign",
    )
    hidden = []
    for obj in asset.objects:
        if obj.name.startswith(exterior_prefixes):
            hidden.append((obj, obj.hide_render))
            obj.hide_render = True
    old_location = cam.location.copy()
    old_rotation = cam.rotation_euler.copy()
    old_lens = cam_data.lens
    cam.location = (0.0, -6.0, 65.0)
    cam.rotation_euler = (Vector((0.0, 0.0, 0.0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_data.lens = 50
    scene.render.filepath = str(EVIDENCE / "preview_interior_schematic.png")
    bpy.ops.render.render(write_still=True)
    for obj, prior in hidden:
        obj.hide_render = prior
    cam.location = old_location
    cam.rotation_euler = old_rotation
    cam_data.lens = old_lens
    report = {
        "asset_id": ASSET_ID,
        "asset_path": str(ASSET_PATH.relative_to(ROOT)).replace("\\", "/"),
        "collection": COLLECTION_NAME,
        "scene": SCENE_NAME,
        "geometry_object_count": len(geom),
        "material_count": len([m for m in bpy.data.materials if m.users]),
        "placement_origin_xy_m": list(anchor),
        "source_bounds_world_m": [[bounds[0][0], bounds[0][1]], [bounds[1][0], bounds[1][1]], [0.0, WALL_HEIGHT]],
        "local_bounds_m": world_bounds,
        "story_height_status": "3.65m modeled from the GIS Extrution=12 as plausible feet; height is estimated, not surveyed",
        "interior_status": "schematic furnishings/partitions from official room descriptions; not a measured plan",
        "export_note": "Models the PGSC low office/student-center portion only; the Northwestern Avenue Parking Garage upper decks are a separate building asset.",
        "external_image_paths": sorted(set(p.filepath for img in bpy.data.images for p in [img] if img.source == "FILE")),
    }
    (EVIDENCE / "build_metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("PGSC_BUILD_REPORT=" + json.dumps(report))


if __name__ == "__main__":
    main()

