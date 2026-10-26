"""Build the evidence-backed South Honors College and Residences asset.

The footprint comes from Purdue GIS feature 905 (Web Mercator). Facade and
interior details use official Purdue descriptions and public project photos;
dimensions not supplied by those sources are explicitly approximate.
Run with Blender 5.2: blender -b <asset.blend> --python <this file>.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_honors_college_and_residences_south_c663781"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
EVIDENCE = ROOT / "audit" / "honors_college_residences_south_c663781"
GIS_PATH = EVIDENCE / "sources" / "purdue_gis_fid905.json"
ASSET_COLLECTION = "Asset_" + ASSET_ID
SCENE_NAME = "Building_" + ASSET_ID
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137


def xy_from_web_mercator(x, y):
    """EPSG:3857 -> WGS84 -> project local campus meters."""
    radius = 6378137.0
    lon = math.degrees(x / radius)
    lat = math.degrees(2.0 * math.atan(math.exp(y / radius)) - math.pi / 2.0)
    east = (lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT))
    north = (lat - ORIGIN_LAT) * 111040.0
    return east, north


def material(name, color, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    mat.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat, bsdf


def add_brick_detail(mat, bsdf):
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    tex = nodes.new("ShaderNodeTexBrick")
    tex.inputs["Color1"].default_value = (0.34, 0.105, 0.066, 1)
    tex.inputs["Color2"].default_value = (0.22, 0.052, 0.038, 1)
    tex.inputs["Mortar"].default_value = (0.26, 0.24, 0.22, 1)
    tex.inputs["Scale"].default_value = 110.0
    tex.inputs["Mortar Size"].default_value = 0.025
    tex.inputs["Mortar Smooth"].default_value = 0.02
    tex.inputs["Brick Width"].default_value = 0.65
    tex.inputs["Row Height"] .default_value = 0.28
    uv = nodes.new("ShaderNodeTexCoord")
    links.new(uv.outputs["Generated"], tex.inputs["Vector"])
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.18
    bump.inputs["Distance"].default_value = 0.045
    links.new(tex.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def link_obj(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def mesh_object(name, verts, faces, mat, collection):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def cube(name, loc, scale, mat, collection, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_obj(obj, collection)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Soft architectural edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return obj


def append_box(batch, center, along, outward, width, depth, height):
    """Append an oriented box to a shared mesh batch (keeps the library lean)."""
    center, along, outward = Vector(center), Vector(along), Vector(outward)
    up = Vector((0, 0, 1))
    start = len(batch["verts"])
    for zsign in (-1, 1):
        for dsign in (-1, 1):
            for wsign in (-1, 1):
                p = center + along * (wsign * width / 2) + outward * (dsign * depth / 2) + up * (zsign * height / 2)
                batch["verts"].append(tuple(p))
    faces = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    batch["faces"].extend([tuple(start + v for v in face) for face in faces])


def append_quad(batch, points):
    start = len(batch["verts"])
    batch["verts"].extend([tuple(Vector(p)) for p in points])
    batch["faces"].append(tuple(range(start, start + 4)))


def make_window(name, center, along, outward, width, height, z, glass, metal, collection, batches):
    """Window as a framed dark-glass panel on one straight GIS facade edge."""
    center, along, outward = Vector(center), Vector(along), Vector(outward)
    center += outward * 0.075
    center.z = z
    glass_batch, frame_batch = batches["glass"], batches["metal"]
    append_box(glass_batch, center, along, outward, width, 0.06, height)
    fw = 0.055
    for side in (-1, 1):
        append_box(frame_batch, center + along * (side * (width / 2 - fw / 2)), along, outward, fw, 0.13, height + 0.10)
    for side in (-1, 1):
        append_box(frame_batch, center + Vector((0, 0, side * (height / 2 - fw / 2))), along, outward, width, 0.13, fw)
    for fraction in (-0.22, 0.22):
        append_box(frame_batch, center + along * (width * fraction), along, outward, 0.035, 0.15, height)


def build():
    with open(GIS_PATH, encoding="utf-8") as f:
        feature = json.load(f)["feature"]
    attrs = feature["attributes"]
    ring = feature["geometry"]["rings"][0]
    points = [xy_from_web_mercator(x, y) for x, y in ring[:-1]]
    # Keep campus coordinates because this manifest entry remains a massing asset.
    cx = sum(x for x, _ in points) / len(points)
    cy = sum(y for _, y in points) / len(points)
    pts = [(x, y) for x, y in points]
    min_x, max_x = min(x for x, _ in pts), max(x for x, _ in pts)
    min_y, max_y = min(y for _, y in pts), max(y for _, y in pts)
    # Segment outward normals from polygon winding.
    signed_area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2
    ccw = signed_area > 0

    scene = bpy.context.scene
    scene.name = SCENE_NAME
    collection = bpy.data.collections.get(ASSET_COLLECTION)
    if collection is None:
        collection = bpy.data.collections.new(ASSET_COLLECTION)
        scene.collection.children.link(collection)
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    brick, brick_bsdf = material("HCRS | Purdue red-brown brick", (0.31, 0.085, 0.055), 0.82)
    add_brick_detail(brick, brick_bsdf)
    concrete, _ = material("HCRS | pale limestone precast", (0.41, 0.39, 0.35), 0.62)
    slate, _ = material("HCRS | charcoal standing-seam roof", (0.018, 0.026, 0.032), 0.68, 0.05)
    glass, glass_bsdf = material("HCRS | blue gray architectural glazing", (0.075, 0.16, 0.21), 0.19, 0.22)
    glass_bsdf.inputs["Transmission Weight"].default_value = 0.12
    trim, _ = material("HCRS | dark bronze aluminum", (0.11, 0.13, 0.14), 0.28, 0.55)
    interior, _ = material("HCRS | schematic interior floor plate", (0.53, 0.48, 0.39), 0.8)
    room_wall, _ = material("HCRS | schematic interior partitions", (0.76, 0.73, 0.66), 0.88)
    entry_light, _ = material("HCRS | entry soffit and pale frame", (0.78, 0.76, 0.68), 0.45)
    window_batches = {"glass": {"verts": [], "faces": []}, "metal": {"verts": [], "faces": []}}

    # Purdue describes six above-ground stories plus basement. Story 1 is the
    # taller academic/admin podium; five upper levels are residence floors.
    z0 = 0.0
    floor_heights = [4.15] + [3.15] * 5
    floor_z = [z0]
    for h in floor_heights:
        floor_z.append(floor_z[-1] + h)
    roof_eave = floor_z[-1]
    roof_cap = roof_eave + 0.72

    # GIS polygon shell: the footprint is directly source-derived.
    verts = [(x, y, z0) for x, y in pts] + [(x, y, roof_eave) for x, y in pts]
    n = len(pts)
    faces = [tuple(range(n)), tuple(range(n, 2 * n))]
    shell = mesh_object("HCRS | Purdue GIS footprint, six-story shell", verts, faces, brick, collection)
    shell["source_feature_id"] = int(attrs["FID"])
    shell["source_layer"] = "Purdue University BuildingShapes"
    shell["story_basis"] = "Purdue official Honors building information: six stories plus basement"

    # Story bands and end pilasters; visible rhythmic horizontal articulation.
    for level, z in enumerate(floor_z[1:-1], start=1):
        for i, a in enumerate(pts):
            b = pts[(i + 1) % n]
            dx, dy = b[0] - a[0], b[1] - a[1]
            length = math.hypot(dx, dy)
            if length < 2.6:
                continue
            outward = (dy, -dx) if ccw else (-dy, dx)
            outward = Vector((outward[0], outward[1], 0)).normalized()
            center = Vector(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, z)) + outward * 0.025
            band = cube(f"HCRS | limestone story band {level:02d} edge {i:02d}", center, (length, 0.075, 0.065), concrete, collection)
            band.rotation_euler[2] = math.atan2(dy, dx)

    # Build wall planes with actual window openings rather than laying glass on
    # top of brick. Main floor windows are broad; upper residential windows repeat.
    wall_batch = {"verts": [], "faces": []}
    for i, a in enumerate(pts):
        b = pts[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        outward = (dy, -dx) if ccw else (-dy, dx)
        outward = Vector((outward[0], outward[1], 0)).normalized()
        count = max(1, int(length / 3.25)) if length >= 3.4 else 0
        along = Vector((dx / length, dy / length, 0))
        for lev in range(6):
            zlo, zhi = floor_z[lev] + 0.035, floor_z[lev+1] - 0.035
            if count == 0:
                p0 = Vector((a[0],a[1],zlo)) + outward*0.018
                p1 = Vector((b[0],b[1],zlo)) + outward*0.018
                p2 = Vector((b[0],b[1],zhi)) + outward*0.018
                p3 = Vector((a[0],a[1],zhi)) + outward*0.018
                append_quad(wall_batch, (p0,p1,p2,p3))
                continue
            cell = length / count
            win_h = min(2.15 if lev == 0 else 1.55, (zhi-zlo)*0.76)
            win_w = min(2.1 if lev == 0 else 1.45, cell*0.62)
            sill_z = (zlo + zhi - win_h) / 2
            head_z = sill_z + win_h
            for j in range(count):
                t0, t1 = j/count, (j+1)/count
                tc = (t0+t1)/2
                half = win_w/(2*length)
                tl, tr = tc-half, tc+half
                def pos(t, z):
                    return Vector((a[0]+dx*t,a[1]+dy*t,z)) + outward*0.018
                # Brick piers to either side, plus sill and head above/below glass.
                append_quad(wall_batch, (pos(t0,zlo),pos(tl,zlo),pos(tl,zhi),pos(t0,zhi)))
                append_quad(wall_batch, (pos(tr,zlo),pos(t1,zlo),pos(t1,zhi),pos(tr,zhi)))
                append_quad(wall_batch, (pos(tl,zlo),pos(tr,zlo),pos(tr,sill_z),pos(tl,sill_z)))
                append_quad(wall_batch, (pos(tl,head_z),pos(tr,head_z),pos(tr,zhi),pos(tl,zhi)))
                center = Vector((a[0]+tc*dx,a[1]+tc*dy,0))
                make_window(f"HCRS | {'academic' if lev == 0 else 'residential'} window edge{i:02d}_{j:02d}_L{lev+1}", center, along, outward, win_w, win_h, (sill_z+head_z)/2, glass, trim, collection, window_batches)

    mesh_object("HCRS | GIS perimeter brick walls with modeled openings", wall_batch["verts"], wall_batch["faces"], brick, collection)

    for window_type, mat in (("glass", glass), ("metal", trim)):
        batch = window_batches[window_type]
        mesh_object("HCRS | repeated facade " + window_type, batch["verts"], batch["faces"], mat, collection)

    # A measured-by-photo style gable at the main south arrival end. The source
    # image is complex-wide; therefore this massing cue is an inferred match.
    south_edges = []
    for i, a in enumerate(pts):
        b = pts[(i + 1) % n]
        midpoint_y = (a[1] + b[1]) * 0.5
        if abs(b[1] - a[1]) < 1.4:
            south_edges.append((midpoint_y, i, a, b))
    if south_edges:
        _, idx, a, b = min(south_edges, key=lambda item: item[0])
        length = math.dist(a, b)
        if length > 9.0:
            crest = roof_eave + 3.0
            mesh_object("HCRS | south gable end, inferred from Purdue photo", [(a[0], a[1], roof_eave), (b[0], b[1], roof_eave), ((a[0]+b[0])/2, (a[1]+b[1])/2, crest)], [(0, 1, 2)], brick, collection)
            # Pale precast framing establishes the glass-and-brick entrance bay.
            dx, dy = b[0]-a[0], b[1]-a[1]
            along = Vector((dx, dy, 0)).normalized()
            outward = Vector((0, -1 if (a[1]+b[1])/2 < cy else 1, 0))
            entry_center = Vector(((a[0]+b[0])/2, (a[1]+b[1])/2, floor_z[1] + 0.85)) + outward * 0.10
            aw = min(5.6, length * 0.42)
            ah = min(roof_eave - 1.0, 15.2)
            glazing = cube("HCRS | glazed south stair atrium", entry_center + Vector((0,0,ah/2-floor_z[1]/2)), (aw, 0.15, ah), glass, collection)
            glazing.rotation_euler[2] = math.atan2(along.y, along.x)
            # Explicit vertical mullion grid and pale stone side piers.
            for q in range(1, 5):
                pos = entry_center + Vector((0,0,ah/2-floor_z[1]/2)) + along * (aw * (q/5 - .5))
                mull = cube(f"HCRS | atrium mullion {q}", pos + outward * .12, (0.075, 0.2, ah), trim, collection)
                mull.rotation_euler[2] = math.atan2(along.y, along.x)
            for side in (-1, 1):
                pos = entry_center + Vector((0,0,ah/2-floor_z[1]/2)) + along * (side * (aw/2 + .38))
                pier = cube(f"HCRS | atrium precast pier {side}", pos + outward * .07, (0.72, 0.30, ah+0.5), entry_light, collection)
                pier.rotation_euler[2] = math.atan2(along.y, along.x)
            canopy_center = entry_center + Vector((0,0,-floor_z[1]/2 + 0.28)) + outward * 0.72
            canopy = cube("HCRS | south glazed entry canopy", canopy_center, (aw+1.5, 1.45, 0.22), concrete, collection)
            canopy.rotation_euler[2] = math.atan2(along.y, along.x)
            # Transparent opening at the ground floor marks the principal entrance.
            door_center = entry_center + Vector((0,0,-floor_z[1]/2 - 1.05)) + outward * 0.14
            door = cube("HCRS | south main entry doors", door_center, (2.25, 0.12, 2.5), glass, collection)
            door.rotation_euler[2] = math.atan2(along.y, along.x)

    # Dark roof plane/parapet and repeated roof monitor forms inferred from the
    # official exterior/aerial photographs. These are not survey dimensions.
    top_face = mesh_object("HCRS | charcoal roof cap", [(x, y, roof_cap) for x, y in pts], [tuple(range(n))], slate, collection)
    top_face["height_basis"] = "estimated: six official stories, floor-to-floor heights approximated"
    cube("HCRS | roof parapet south", ((min_x+max_x)/2, min_y, roof_eave+0.38), (max_x-min_x, 0.24, 0.76), brick, collection)

    # A separately labeled schematic residential/academic interior. No measured
    # room plan is available for South, so these objects are explicitly generic.
    floor_mesh = [(x, y, 0.0) for x, y in pts]
    for level in range(1, 7):
        z = floor_z[level] - 0.11
        verts = [(x, y, z) for x, y in pts]
        slab = mesh_object(f"SCHEMATIC INTERIOR | floor plate {level:02d} not as-built", verts, [tuple(range(n))], interior, collection)
        slab["not_as_built"] = True
        slab["basis"] = "schematic only; official sources identify academic level 1 and residential levels 2-6"
    # Generic core and partitions placed inside the footprint envelope, labeled as estimates.
    core_x = (min_x + max_x) / 2
    core_y = (min_y + max_y) / 2
    cube("SCHEMATIC INTERIOR | elevator and stair core, not as-built", (core_x, core_y, roof_eave/2), (5.0, 8.0, roof_eave-0.8), concrete, collection)
    # Basic interior subdivision planes remain inside the outer wall; no exact layout asserted.
    for level in range(1, 7):
        z = (floor_z[level] + floor_z[level-1]) / 2
        partition = cube(f"SCHEMATIC INTERIOR | pod corridor partition L{level}, not as-built", (core_x, core_y + 9.0, z), (11.0, 0.12, 2.25), room_wall, collection)
        partition["not_as_built"] = True

    # Reproducible audit view and portable lighting, kept outside the exported
    # building collection so collection linking does not import camera rig parts.
    setup = bpy.data.collections.get("HCRS_Preview_Setup") or bpy.data.collections.new("HCRS_Preview_Setup")
    if setup.name not in [c.name for c in scene.collection.children]:
        scene.collection.children.link(setup)
    for obj in list(setup.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    preview_ground, _ = material("HCRS preview | neutral campus context", (0.19, 0.22, 0.19), 0.9)
    cube("HCRS preview | ground plane", (cx, cy, -0.25), (155, 160, 0.35), preview_ground, setup)
    cam_data = bpy.data.cameras.new("HCRS audit camera")
    cam = bpy.data.objects.new("HCRS audit camera", cam_data)
    setup.objects.link(cam)
    target = Vector((cx, cy, 10.5))
    cam.location = (cx - 78, cy - 96, 54)
    direction = target - Vector(cam.location)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 132
    scene.camera = cam
    for name, loc, energy, size in (
        ("HCRS key", (cx-35,cy-65,48), 6500, 35),
        ("HCRS fill", (cx+45,cy-15,32), 3800, 28),
        ("HCRS rim", (cx+15,cy+55,40), 5000, 30),
    ):
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.shape, data.size = energy, "DISK", size
        light = bpy.data.objects.new(name, data)
        setup.objects.link(light)
        light.location = loc
        light.rotation_euler = (target - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if scene.world:
        scene.world.use_nodes = True
        background = scene.world.node_tree.nodes.get("Background")
        if background:
            background.inputs["Color"].default_value = (0.20, 0.27, 0.36, 1)
            background.inputs["Strength"].default_value = 0.35
    scene.render.resolution_x, scene.render.resolution_y = 1200, 900
    scene.render.resolution_percentage = 70
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(EVIDENCE / "hcrs_south_exterior_review.png")
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    bpy.ops.render.render(write_still=True)

    # Useful custom properties for downstream master audit.
    collection["building_id"] = ASSET_ID
    collection["source_feature_id"] = int(attrs["FID"])
    collection["source_crs"] = "EPSG:3857 (Esri WKID 102100 / latestWkid 3857), converted to local campus approximation"
    collection["footprint_method"] = "directly transformed Purdue GIS polygon ring; campus XY meters"
    collection["vertical_uncertainty"] = "floor heights estimated; GIS NUM_LEVELS=8 conflicts with official six stories plus basement"
    collection["interior_status"] = "schematic, explicitly not as-built"
    scene.unit_settings.system = "METRIC"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = 1200, 900
    scene.render.resolution_percentage = 70
    scene.render.image_settings.file_format = "PNG"
    # Leave the linked asset as the only intended deliverable collection; helper camera/light are local scene objects.
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    return {
        "building_id": ASSET_ID,
        "asset_path": str(ASSET_PATH.relative_to(ROOT)).replace("\\", "/"),
        "collection": ASSET_COLLECTION,
        "scene": SCENE_NAME,
        "gis_feature_id": attrs["FID"],
        "gis_ring_vertices": len(pts),
        "footprint_bounds_m": [[min_x,max_x],[min_y,max_y]],
        "campus_centroid_m": [cx,cy],
        "story_count_modeled": 6,
        "height_m_estimated": roof_cap,
        "uncertainty": ["GIS reports NUM_LEVELS=8; official Purdue sources describe six stories plus basement", "South-specific elevations or measured roof heights unavailable", "public exterior photograph covers the complex and South attribution of the gabled entry form is an inference", "interior is schematic and not as-built"]
    }


if __name__ == "__main__":
    print("HCRS_BUILD_RESULT=" + json.dumps(build(), sort_keys=True))
