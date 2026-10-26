"""Rebuild the Purdue Village Administration Building from official PVAB GIS footprint.

Run from repository root with Blender 4.5+:
  blender --background --python modular/buildings/build_massing_purdue_village_administration_building_3faae6c.py
"""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_purdue_village_administration_building_3faae6c"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
RAW_GIS = ROOT / "audit" / ASSET_ID / "sources" / "arcgis_fid524_raw.json"
OUTDIR = ROOT / "audit" / ASSET_ID
COLLECTION_NAME = f"Asset_{ASSET_ID}"
OBJECT_NAME = "Purdue Village Administration Building"
ESTIMATED_HEIGHT_M = 4.2  # estimated from the one-storey archival photo; not a measured height
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137


def xy_from_lonlat(lon, lat):
    x = (lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT))
    y = (lat - ORIGIN_LAT) * 111040.0
    return (x, y)


def ring_from_gis(payload):
    features = payload.get("features", [])
    if len(features) != 1:
        raise RuntimeError(f"Expected one live FID 524 feature, got {len(features)}")
    feature = features[0]
    attrs = feature.get("attributes", {})
    if attrs.get("FID") != 524 or attrs.get("BLDG_ABBR") != "PVAB":
        raise RuntimeError(f"GIS feature identity mismatch: {attrs}")
    rings = feature["geometry"]["rings"]
    ring = max(rings, key=len)
    # ArcGIS coordinates are [longitude, latitude] because outSR=4326.
    result = [xy_from_lonlat(float(lon), float(lat)) for lon, lat in ring]
    if len(result) > 1 and math.dist(result[0], result[-1]) < 1e-6:
        result.pop()
    return result


def make_material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    return mat


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if collection is None:
        raise RuntimeError(f"Expected export collection not found: {COLLECTION_NAME}")
    obj = bpy.data.objects.get(OBJECT_NAME)
    if obj is None or obj.type != "MESH" or obj.name not in collection.objects:
        raise RuntimeError(f"Expected mesh {OBJECT_NAME} in {COLLECTION_NAME}")

    payload = json.loads(RAW_GIS.read_text(encoding="utf-8"))
    ring = ring_from_gis(payload)
    n = len(ring)
    vertices = [(x, y, 0.0) for x, y in ring] + [(x, y, ESTIMATED_HEIGHT_M) for x, y in ring]
    faces = []
    material_indices = []
    signed_area = sum(ring[i][0] * ring[(i + 1) % n][1] - ring[(i + 1) % n][0] * ring[i][1] for i in range(n)) / 2.0
    clockwise = signed_area < 0
    # Side quads preserve every source boundary segment.
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, i + n, j + n, j) if clockwise else (i, j, j + n, i + n))
        material_indices.append(0)
    # Polygon caps; Blender tessellates the source plan while retaining exact ring vertices.
    faces.append(tuple(range(n)))
    faces.append(tuple(range(2 * n - 1, n - 1, -1)))
    material_indices.extend((0, 1))

    # The Purdue Archives record image shows one long public facade: a brick return,
    # pale vertically ribbed metal cladding, a glazed entrance bay, and a shallow canopy.
    # Its compass bearing is not encoded in the photograph, so align it to the longest
    # straight GIS edge, the strongest plan candidate, and record this residual uncertainty.
    facade_edge = 7
    a = ring[facade_edge]
    b = ring[(facade_edge + 1) % n]
    dx, dy = b[0] - a[0], b[1] - a[1]
    frontage_length = math.hypot(dx, dy)
    ux, uy = dx / frontage_length, dy / frontage_length
    # The official ring is clockwise; its exterior is left of each directed edge.
    if clockwise:
        nx, ny = -uy, ux
    else:
        nx, ny = uy, -ux

    def point(t, z, offset=0.0):
        return (a[0] + dx * t + nx * offset, a[1] + dy * t + ny * offset, z)

    def surface(t0, t1, z0, z1, mat_index, offset=0.035):
        idx = len(vertices)
        # Face winding is outward for the selected clockwise footprint edge.
        vertices.extend((point(t0, z0, offset), point(t0, z1, offset),
                         point(t1, z1, offset), point(t1, z0, offset)))
        faces.append((idx, idx + 1, idx + 2, idx + 3))
        material_indices.append(mat_index)

    def oriented_box(t0, t1, v0, v1, z0, z1, mat_index):
        idx = len(vertices)
        vertices.extend((point(t0,z0,v0), point(t1,z0,v0), point(t1,z1,v0), point(t0,z1,v0),
                         point(t0,z0,v1), point(t1,z0,v1), point(t1,z1,v1), point(t0,z1,v1)))
        faces.extend(((idx,idx+1,idx+2,idx+3), (idx+4,idx+7,idx+6,idx+5),
                      (idx,idx+4,idx+5,idx+1), (idx+1,idx+5,idx+6,idx+2),
                      (idx+2,idx+6,idx+7,idx+3), (idx+3,idx+7,idx+4,idx)))
        material_indices.extend((mat_index,) * 6)

    # Material slots are kept on this one mesh object so the modular asset still
    # exports as one building object in its original collection.
    mats = [
        make_material("PVAB side-wall neutral", (0.56, 0.55, 0.51)),
        make_material("PVAB flat-roof neutral", (0.34, 0.35, 0.34)),
        make_material("PVAB archive brick", (0.26, 0.105, 0.065), 0.88),
        make_material("PVAB pale vertical metal panels", (0.72, 0.72, 0.68), 0.65, 0.12),
        make_material("PVAB dark entrance glazing", (0.075, 0.12, 0.15), 0.2, 0.12),
        make_material("PVAB charcoal frames and canopy", (0.09, 0.105, 0.11), 0.45, 0.25),
        make_material("PVAB entrance metal hardware", (0.6, 0.61, 0.58), 0.35, 0.45),
    ]

    # On screen, increasing t runs from right to left for this southeast-looking
    # view. This orders the source-observed brick to the left, glazing centrally,
    # and pale ribbed metal to the right as in the Archives photograph.
    surface(0.70, 1.00, 0.0, ESTIMATED_HEIGHT_M - 0.18, 2)
    surface(0.00, 0.72, 0.0, ESTIMATED_HEIGHT_M, 3)
    glass_t0, glass_t1 = 0.34, 0.78
    surface(glass_t0, glass_t1, 0.12, 3.12, 4, offset=0.075)

    # Dark glazing mullions and perimeter frame, at modest scale from the photo.
    frame_w = 0.10 / frontage_length
    surface(glass_t0, glass_t0 + frame_w, 0.08, 3.18, 5, offset=0.10)
    surface(glass_t1 - frame_w, glass_t1, 0.08, 3.18, 5, offset=0.10)
    surface(glass_t0, glass_t1, 0.08, 0.08 + frame_w, 5, offset=0.10)
    surface(glass_t0, glass_t1, 3.08, 3.08 + frame_w, 5, offset=0.10)
    for t in [glass_t0 + (glass_t1-glass_t0)*k/7 for k in range(1,7)]:
        surface(t-frame_w/2, t+frame_w/2, 0.12, 3.12, 5, offset=0.105)

    # Double-door pair centered in the glass bay; door leaf dimensions are estimates.
    door_center = (glass_t0 + glass_t1) / 2.0
    door_width = 3.2 / frontage_length
    door_t0, door_t1 = door_center-door_width/2, door_center+door_width/2
    surface(door_t0, door_t1, 0.05, 2.20, 5, offset=0.12)
    leaf_gap = 0.055 / frontage_length
    surface(door_center-door_width/2+leaf_gap, door_center-leaf_gap/2, 0.10, 2.14, 4, offset=0.135)
    surface(door_center+leaf_gap/2, door_center+door_width/2-leaf_gap, 0.10, 2.14, 4, offset=0.135)
    handle_width = 0.035 / frontage_length
    for t in (door_center - door_width*0.12, door_center + door_width*0.12):
        surface(t-handle_width/2, t+handle_width/2, 0.95, 1.35, 6, offset=0.15)

    # Shallow dark canopy above glazing and small wall-light/sign panel shown in photo.
    oriented_box(glass_t0, glass_t1, 0.06, 1.05, 3.23, 3.43, 5)
    light_t0, light_t1 = door_center - 0.55/frontage_length, door_center + 0.55/frontage_length
    surface(light_t0, light_t1, 3.57, 3.88, 5, offset=0.08)

    # Closely spaced vertical ribs appear on the pale metal section in the archive photo.
    rib_w = 0.045 / frontage_length
    step = 0.58 / frontage_length
    rib_t = 0.00
    while rib_t < 0.34:
        surface(rib_t, min(0.34, rib_t + rib_w), 0.04, ESTIMATED_HEIGHT_M - 0.04, 3, offset=0.09)
        rib_t += step
    rib_t = 0.37
    while rib_t < 0.72:
        surface(rib_t, min(0.72, rib_t + rib_w), 3.22, ESTIMATED_HEIGHT_M - 0.04, 3, offset=0.09)
        rib_t += step

    mesh = bpy.data.meshes.new(f"{OBJECT_NAME} | FID 524 footprint shell")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    for mat in mats:
        mesh.materials.append(mat)
    for polygon, mat_index in zip(mesh.polygons, material_indices):
        polygon.material_index = mat_index

    old_mesh = obj.data
    obj.data = mesh
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)
    obj["official_gis_fid"] = 524
    obj["gis_abbreviation"] = "PVAB"
    obj["footprint_source"] = "Purdue-linked BuildingShapesZip4 ArcGIS feature FID 524; transformed from EPSG:4326 with project local approximation"
    obj["estimated_height_m"] = ESTIMATED_HEIGHT_M
    obj["height_status"] = "4.2 m estimate from one-storey photo and area cross-check; not measured"
    obj["floor_count_status"] = "one-storey appearance in Purdue Archives image; 23,360 sq ft historic GSF vs 26,709 sq ft GIS footprint is consistent, not a source-certified floor count"
    obj["facade_status"] = "front facade details based on Purdue Archives building 74 image; image compass bearing not encoded"
    obj["roof_status"] = "image supports a low horizontal parapet/flat roofline; hidden roof surface form unverified"
    obj["facade_image_source"] = "https://collections.lib.purdue.edu/campus/images/buildings/74-purdue-village-administration-building.jpeg"
    obj["facade_alignment_status"] = "aligned to longest GIS edge as a best-fit interpretation; photo viewpoint bearing unverified"
    scene = bpy.context.scene
    scene["building_id"] = ASSET_ID
    scene["gis_fid"] = 524
    scene["export_collection"] = COLLECTION_NAME
    scene["height_status"] = "4.2 m estimate; archival photo and area support low single-storey appearance, but height is unmeasured"
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))

    # Preview renders are created in memory after saving the portable building asset.
    render_collection = bpy.data.collections.new("PVAB_Preview_Only")
    scene.collection.children.link(render_collection)
    ground_mat = bpy.data.materials.new("PVAB preview ground")
    ground_mat.diffuse_color = (0.62, 0.63, 0.61, 1.0)
    ground_mat.use_nodes = True
    ground_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.62, 0.63, 0.61, 1.0)
    ground_mesh = bpy.data.meshes.new("PVAB preview ground mesh")
    ground_mesh.from_pydata([(-1100,-1000,-0.15),(-650,-1000,-0.15),(-650,-550,-0.15),(-1100,-550,-0.15)], [], [(0,1,2,3)])
    ground = bpy.data.objects.new("PVAB preview ground (not exported)", ground_mesh)
    render_collection.objects.link(ground)
    ground.data.materials.append(ground_mat)

    world = bpy.data.worlds.new("PVAB Preview World") if scene.world is None else scene.world
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.25,0.27,0.30,1.0)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.45
    light_data = bpy.data.lights.new("PVAB preview key", type="AREA")
    light_data.energy = 5500
    light_data.shape = "DISK"
    light_data.size = 100
    light = bpy.data.objects.new("PVAB preview key", light_data)
    render_collection.objects.link(light)
    light.location = (-780,-920,170)
    camera_data = bpy.data.cameras.new("PVAB preview camera")
    camera = bpy.data.objects.new("PVAB preview camera", camera_data)
    render_collection.objects.link(camera)
    scene.camera = camera
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 100
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.display.shading.light = "STUDIO"
    center = (-871.5,-797.0,1.7)
    views = [
        ("preview_oblique.png", (center[0]+nx*105, center[1]+ny*105, 34), 100),
        ("preview_facade.png", (center[0]+nx*105, center[1]+ny*105, center[2]), 82),
        ("preview_top.png", (-871.5,-797.0,210), 100),
    ]
    for filename, camera_pos, ortho_scale in views:
        camera.location = camera_pos
        camera_data.ortho_scale = ortho_scale
        direction = bpy.mathutils.Vector(center) - camera.location if hasattr(bpy, 'mathutils') else None
        # Import here to avoid any need for a system-level mathutils module.
        from mathutils import Vector
        direction = Vector(center) - camera.location
        camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(OUTDIR / filename)
        bpy.ops.render.render(write_still=True)
    print(json.dumps({"asset": str(ASSET), "collection": COLLECTION_NAME, "gis_fid": 524, "vertices": len(mesh.vertices), "faces": len(mesh.polygons), "estimated_height_m": ESTIMATED_HEIGHT_M, "previews": [str(OUTDIR / name) for name, _, _ in views]}, indent=2))


if __name__ == "__main__":
    main()

