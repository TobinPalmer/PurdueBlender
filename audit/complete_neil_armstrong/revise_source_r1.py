"""Evidence-backed Neil Armstrong Hall source-library revision R1.

Run with Blender 5.2 in background mode from the project root. This script only
opens and saves modular/buildings/neil_armstrong_hall.blend and writes
building-specific review renders/validation under this folder. It never opens
or saves the campus master.
"""
import bpy
import json
import math
import os
from mathutils import Vector

ROOT = r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET = os.path.join(ROOT, "modular", "buildings", "neil_armstrong_hall.blend")
OUT = os.path.join(ROOT, "audit", "complete_neil_armstrong")
RENDER_DIR = os.path.join(OUT, "renders_r1")
os.makedirs(RENDER_DIR, exist_ok=True)

FEET_TO_METERS = 0.3048
ATRIUM_HEIGHT_M = 53.0 * FEET_TO_METERS
OLD_ATRIUM_HEIGHT_M = 21.5

def ensure(condition, message):
    if not condition:
        raise RuntimeError(message)

def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()

def create_review_camera(name, location, target, lens):
    data = bpy.data.cameras.new(name + "Data")
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    data.lens = lens
    data.clip_start = 0.1
    data.clip_end = 2000
    aim(obj, target)
    bpy.context.view_layer.update()
    return obj

def world_bounds(objects):
    points = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        if obj.type != 'MESH' or obj.hide_render:
            continue
        evaluated = obj.evaluated_get(depsgraph)
        points.extend(evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box)
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)] if points else None

bpy.ops.wm.open_mainfile(filepath=ASSET)
scene = bpy.context.scene
collection = bpy.data.collections.get("Asset_neil_armstrong_hall")
ensure(collection is not None, "Expected exported collection is missing")
ensure(scene.name == "Building_neil_armstrong_hall", "Unexpected source scene")
ensure(len(collection.objects) == 444, "Source object count changed before R1")
atrium_south_wall = bpy.data.objects.get("ARMS_Atrium_South_Wall")
ensure(atrium_south_wall is not None, "Atrium south wall not found")
FACTOR = ATRIUM_HEIGHT_M / atrium_south_wall.dimensions.z

# Correct the documented atrium lobby ceiling. The old builder used 21.5 m,
# while the contemporaneous project description gives 53 ft (16.1544 m).
atrium_mesh_names = [
    "ARMS_Curved_Mullion_", "ARMS_Curtain_Glass_Bay_", "ARMS_Atrium_South_Wall"
]
for obj in list(collection.objects):
    if any(obj.name.startswith(prefix) for prefix in atrium_mesh_names):
        obj.location.z *= FACTOR
        obj.scale.z *= FACTOR

# Existing ceiling components and suspended exhibit infrastructure must follow
# the lower, source-supported ceiling. Keep lateral placement and dimensions.
skylight = bpy.data.objects.get("ARMS_Atrium_Skylight_Glazing")
ensure(skylight is not None, "Atrium skylight not found")
skylight.location.z = ATRIUM_HEIGHT_M + 0.30
for obj in collection.objects:
    if obj.name.startswith("ARMS_Roof_Steel_Truss_"):
        obj.location.z = ATRIUM_HEIGHT_M - 0.5
    elif obj.name.startswith("ARMS_HighBay_Luminaire_"):
        obj.location.z = ATRIUM_HEIGHT_M - 1.2
    elif obj.name.startswith("ARMS_Light_HighBay_"):
        obj.location.z = ATRIUM_HEIGHT_M - 1.6
    elif obj.name.startswith("ARMS_Suspension_Cable_"):
        # Four illustrative cables terminate just above the module, rather than
        # extending through the newly corrected roof.
        obj.location.z = 14.92
        obj.scale.z *= 2.46 / obj.dimensions.z

# The project material record identifies Mayflower Red ACM on the high roof
# and Sea Wolf ACM on the canopy/vestibule. Give the existing roof/canopy
# objects those documented finishes rather than generic gray/stone materials.
def get_acm_material(name, color, metallic, roughness):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat

mayflower_red = get_acm_material("ARMS_Mayflower_Red_ACM", (0.34, 0.055, 0.025), 0.68, 0.3)
sea_wolf = get_acm_material("ARMS_Sea_Wolf_ACM", (0.11, 0.15, 0.16), 0.72, 0.28)
for name in ("ARMS_East_Roof_Slab", "ARMS_West_Roof_Slab"):
    obj = bpy.data.objects.get(name)
    ensure(obj is not None, f"High roof object not found: {name}")
    obj.data.materials.clear()
    obj.data.materials.append(mayflower_red)
for name in ("ARMS_Cantilever_Canopy_Deck", "ARMS_Canopy_Fascia_Trim"):
    obj = bpy.data.objects.get(name)
    ensure(obj is not None, f"Canopy object not found: {name}")
    obj.data.materials.clear()
    obj.data.materials.append(sea_wolf)

# Remove the unsupported Apollo service stage and engine from the visible
# reconstruction. The source describes a full-scale Apollo I command-unit
# replica, not a complete command/service spacecraft. Keep the source object
# names for manifest compatibility and mark the withdrawn meshes explicitly.
for name in ("ARMS_Apollo_Service_Module", "ARMS_Apollo_Engine_Nozzle"):
    obj = bpy.data.objects.get(name)
    ensure(obj is not None, f"Expected exhibit object missing: {name}")
    obj.hide_render = True
    obj.hide_viewport = True
    obj["evidence_status"] = "withdrawn from visible model; source supports Apollo I command-unit replica only"

# Replace the generic cylindrical command-module mesh with a restrained
# truncated-cone silhouette. Profile dimensions are illustrative, not claimed
# to be surveyed. Keep the stable object name/material for modular compatibility.
module = bpy.data.objects.get("ARMS_Apollo_Command_Module")
ensure(module is not None, "Apollo command-unit object not found")
mesh = module.data
mesh.clear_geometry()
segments = 32
profile = [(-1.5, 1.92), (-0.8, 1.77), (0.55, 1.28), (1.26, 0.62), (1.48, 0.53)]
verts = []
for z, radius in profile:
    for i in range(segments):
        a = math.tau * i / segments
        verts.append((radius * math.cos(a), radius * math.sin(a), z))
faces = []
faces.append(tuple(range(segments - 1, -1, -1)))
for ring in range(len(profile) - 1):
    a0 = ring * segments
    b0 = (ring + 1) * segments
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((a0 + i, a0 + j, b0 + j, b0 + i))
faces.append(tuple((len(profile) - 1) * segments + i for i in range(segments)))
mesh.from_pydata(verts, [], faces)
mesh.update()
module.location.z = 11.95
module.scale = (1.0, 1.0, 1.0)
module["evidence_status"] = "Apollo I command-unit replica silhouette; dimensions are illustrative, not surveyed"

# Place the heat shield under the capsule and reduce the docking collar to a
# modest neck. Its presence is illustrative; no dimension is claimed.
shield = bpy.data.objects.get("ARMS_Apollo_HeatShield")
ensure(shield is not None, "Apollo heat shield object not found")
shield.location.z = 10.40
collar = bpy.data.objects.get("ARMS_Apollo_Docking_Probe")
if collar:
    collar.location.z = 13.52
    collar.dimensions = (0.68, 0.68, 0.22)
    collar["evidence_status"] = "illustrative top collar; exact replica detailing unverified"

# The 19.2 m transom row was above the verified 53 ft atrium ceiling; hide it
# but preserve the manifest-listed objects and record why it is withdrawn.
for obj in collection.objects:
    if obj.name.startswith("ARMS_Curved_Transom_") and obj.name.endswith("_19"):
        obj.hide_render = True
        obj.hide_viewport = True
        obj["evidence_status"] = "withdrawn; model level exceeded sourced 53 ft atrium ceiling"

bpy.ops.wm.save_as_mainfile(filepath=ASSET)

# Reopen the saved source before validation and rendering.
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene = bpy.context.scene
collection = bpy.data.collections.get("Asset_neil_armstrong_hall")
ensure(collection is not None and len(collection.objects) == 444, "Reopened library/collection validation failed")
ensure(scene.name == "Building_neil_armstrong_hall", "Reopened source scene name changed")
ensure(abs(bpy.data.objects["ARMS_Atrium_South_Wall"].dimensions.z - ATRIUM_HEIGHT_M) < 0.01,
       "Atrium wall height differs from sourced 53 ft")
ensure(bpy.data.objects["ARMS_Apollo_Service_Module"].hide_render, "Unsupported service module remains visible")
ensure(bpy.data.objects["ARMS_Apollo_Engine_Nozzle"].hide_render, "Unsupported engine remains visible")
ensure(len([o for o in collection.objects if o.type == 'CAMERA']) == 0, "Temporary review camera persisted")
ensure(not any(o.name.startswith("NeilReview") for o in bpy.data.objects), "Temporary review object persisted")
reopened_bounds = world_bounds(collection.objects)

# Temporary, explicitly review-only lights/cameras make repeatable views; they
# are removed before the script exits and are never saved into the source asset.
world = scene.world or bpy.data.worlds.new("NeilReviewWorld")
scene.world = world
world.use_nodes = True
background = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
background.inputs['Color'].default_value = (0.28, 0.32, 0.38, 1.0)
background.inputs['Strength'].default_value = 0.65
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.render.use_compositing = False
scene.render.use_sequencer = False
scene.view_settings.view_transform = 'AgX'

sun_data = bpy.data.lights.new("NeilReviewSunData", 'SUN')
sun_data.energy = 2.0
sun = bpy.data.objects.new("NeilReviewSun", sun_data)
scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(25), math.radians(-20), math.radians(-28))

old_camera = scene.camera
exterior = create_review_camera("NeilReviewExterior", (-1.5, 100.0, 20.0), (-1.5, -8.0, 8.0), 50.0)
exterior.data.type = 'ORTHO'
exterior.data.ortho_scale = 200.0
exterior.rotation_euler = (math.radians(-84.0), 0.0, 0.0)
bpy.context.view_layer.update()
scene.camera = exterior
scene.render.filepath = os.path.join(RENDER_DIR, "exterior_r1.png")
bpy.ops.render.render(write_still=True)

# Elevated exterior view documents the roof colors/footprint in relation to the
# central glazed atrium; it is a presentation view, not a survey camera.
roof_camera = create_review_camera("NeilReviewRoofOblique", (-1.5, 80.0, 90.0), (-1.5, -12.0, 8.0), 50.0)
roof_camera.data.type = 'ORTHO'
roof_camera.data.ortho_scale = 200.0
bpy.context.view_layer.update()
scene.camera = roof_camera
scene.render.filepath = os.path.join(RENDER_DIR, "exterior_roof_oblique_r1.png")
bpy.ops.render.render(write_still=True)

interior = create_review_camera("NeilReviewAtriumCutaway", (0.0, 28.0, 9.0), (-1.5, -12.0, 11.0), 50.0)
bpy.context.view_layer.update()
glass_panels = [o for o in collection.objects if o.name.startswith("ARMS_Curtain_Glass_Bay_")]
front_mullions = [o for o in collection.objects if o.name.startswith(("ARMS_Curved_Mullion_", "ARMS_Curved_Transom_"))]
roof_glass = bpy.data.objects.get("ARMS_Atrium_Skylight_Glazing")
front_walls = [bpy.data.objects.get(n) for n in ("ARMS_East_Wall_North", "ARMS_West_Wall_North")]
front_walls = [o for o in front_walls if o]
cutaway_roofs = [o for o in collection.objects if o.name in {
    "ARMS_East_Roof_Slab", "ARMS_West_Roof_Slab", "ARMS_East_Roof_Penthouse",
    "ARMS_East_Penthouse_Louvers", "ARMS_West_Roof_Penthouse", "ARMS_West_Penthouse_Louvers"
}]
cutaway_objects = glass_panels + front_mullions + front_walls + cutaway_roofs + ([roof_glass] if roof_glass else [])
for obj in cutaway_objects:
    obj.hide_render = True
scene.camera = interior
scene.render.filepath = os.path.join(RENDER_DIR, "atrium_interior_r1.png")
bpy.ops.render.render(write_still=True)
for obj in cutaway_objects:
    obj.hide_render = False

validation = {
    "building_id": "neil_armstrong_hall",
    "asset_path": "modular/buildings/neil_armstrong_hall.blend",
    "scene": scene.name,
    "collection": collection.name,
    "object_count": len(collection.objects),
    "asset_root_location": list(bpy.data.objects["AssetRoot_neil_armstrong_hall"].location),
    "asset_local_bounds_m": reopened_bounds,
    "atrium_ceiling_height_m": ATRIUM_HEIGHT_M,
    "atrium_ceiling_height_ft": 53.0,
    "atrium_south_wall_dimensions_m": list(bpy.data.objects["ARMS_Atrium_South_Wall"].dimensions),
    "visible_service_module": not bpy.data.objects["ARMS_Apollo_Service_Module"].hide_render,
    "visible_engine_nozzle": not bpy.data.objects["ARMS_Apollo_Engine_Nozzle"].hide_render,
    "command_unit_bounds_m": list(bpy.data.objects["ARMS_Apollo_Command_Module"].dimensions),
    "roof_material": bpy.data.objects["ARMS_East_Roof_Slab"].data.materials[0].name,
    "canopy_material": bpy.data.objects["ARMS_Cantilever_Canopy_Deck"].data.materials[0].name,
    "saved_then_reopened": True,
    "temporary_review_objects_saved": False,
    "renders": ["renders_r1/exterior_r1.png", "renders_r1/exterior_roof_oblique_r1.png", "renders_r1/atrium_interior_r1.png"],
}
with open(os.path.join(OUT, "validation_r1.json"), "w", encoding="utf-8") as f:
    json.dump(validation, f, indent=2)

bpy.data.objects.remove(exterior, do_unlink=True)
bpy.data.objects.remove(roof_camera, do_unlink=True)
bpy.data.objects.remove(interior, do_unlink=True)
bpy.data.objects.remove(sun, do_unlink=True)
print(json.dumps(validation, indent=2))
