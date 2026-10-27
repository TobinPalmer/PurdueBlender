"""Evidence-based site-sign and planting refinement for Dauch Alumni Center.

Run with Blender on the existing modular asset:
  blender --background modular/buildings/dauch_alumni_center.blend --python modular/buildings/build_dauch_alumni_center_refinements.py
This script changes only the Dauch asset and writes its dedicated audit previews.
"""
import bpy
import math
import os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSET = os.path.join(ROOT, "modular", "buildings", "dauch_alumni_center.blend")
OUT = os.path.join(ROOT, "audit", "dauch_alumni_center")
os.makedirs(OUT, exist_ok=True)
COL = bpy.data.collections.get("Asset_dauch_alumni_center")
assert COL is not None, "Expected export collection is missing"

def material(name, color, roughness=0.72, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

limestone = material("DAUC_refinement_honed_limestone", (0.66, 0.62, 0.53), 0.84)
dark_letter = material("DAUC_refinement_bronze_letters", (0.16, 0.13, 0.085), 0.42, 0.55)
soil = material("DAUC_refinement_mulch", (0.12, 0.075, 0.038), 0.98)
leaf = bpy.data.materials.get("R2_DAUC_site_plant") or material("DAUC_refinement_evergreen", (0.075, 0.22, 0.11), 0.92)

def cube(name, loc, dims, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Soft dressed-stone edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    COL.objects.link(obj)
    return obj

def shrub(name, loc, scale):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(leaf)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    COL.objects.link(obj)
    return obj

# Official exterior photographs show a freestanding stone identification sign
# in the landscaped approach, with the building name and Purdue University.
# Existing model had only a small, wall-mounted identity inscription.
sign_x, sign_y = 13.7, -24.6
cube("DAUC_site_sign_base", (sign_x, sign_y, 0.19), (2.82, 0.38, 0.30), limestone, 0.045)
cube("DAUC_site_sign_stone_panel", (sign_x, sign_y, 0.92), (2.52, 0.26, 1.18), limestone, 0.055)

def front_text(name, body, loc, size, mat):
    curve = bpy.data.curves.new(name + "_curve", "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.0025
    curve.bevel_depth = 0.0005
    obj = bpy.data.objects.new(name, curve)
    COL.objects.link(obj)
    obj.location = loc
    # Text's local +Z normal points toward the viewer at the south (-Y) face.
    obj.rotation_euler[0] = math.radians(90)
    obj.data.materials.append(mat)
    return obj

front_text("DAUC_site_sign_title", "DAUCH ALUMNI CENTER", (sign_x, sign_y - 0.134, 1.10), 0.174, dark_letter)
front_text("DAUC_site_sign_subtitle", "PURDUE UNIVERSITY", (sign_x, sign_y - 0.135, 0.77), 0.125, dark_letter)

# Low landscaped bed and fuller clustered evergreen masses echo the official
# entrance photograph, while staying separate from the structural footprint.
cube("DAUC_site_sign_mulch_bed", (sign_x, sign_y, 0.08), (3.9, 1.05, 0.10), soil, 0.04)
for side, cx in (("west", sign_x - 1.42), ("east", sign_x + 1.42)):
    for i, (dx, dy, sx, sy, sz) in enumerate(((-0.28, 0.00, 0.42, 0.33, 0.40), (0.12, -0.05, 0.48, 0.37, 0.48), (0.42, 0.08, 0.39, 0.31, 0.36))):
        shrub(f"DAUC_site_sign_{side}_evergreen_{i+1}", (cx + dx, sign_y + dy, 0.17 + sz * 0.72), (sx, sy, sz))

# Save source before rendering. Render a dedicated, building-only 3/4 view.
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
scene = bpy.context.scene
old_camera = scene.camera
old_engine = scene.render.engine
old_res = (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage)
old_transparent = scene.render.film_transparent
cam_data = bpy.data.cameras.new("DAUC_audit_camera_data")
cam = bpy.data.objects.new("DAUC_audit_camera", cam_data)
scene.collection.objects.link(cam)
cam.location = (55.0, -74.0, 36.0)
target = Vector((0.0, -1.0, 7.0))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
cam_data.type = "ORTHO"
cam_data.ortho_scale = 86.0
scene.camera = cam
lights = []
for name, loc, power, size in (("DAUC_audit_key", (8, -34, 45), 5200, 28), ("DAUC_audit_fill", (-32, -6, 24), 2500, 24)):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    light = bpy.data.objects.new(name, data)
    scene.collection.objects.link(light)
    light.location = loc
    light.rotation_euler = (Vector((0, -5, 5)) - light.location).to_track_quat("-Z", "Y").to_euler()
    lights.append(light)
scene.render.engine = "CYCLES"
scene.cycles.samples = 24
scene.render.resolution_x = 1280
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.filepath = os.path.join(OUT, "dauch_alumni_center_refinement_overview.png")
bpy.ops.render.render(write_still=True)

# Focused sign detail view.
cam.location = (sign_x + 4.8, sign_y - 9.5, 5.0)
cam.rotation_euler = (Vector((sign_x, sign_y, 1.1)) - cam.location).to_track_quat("-Z", "Y").to_euler()
cam_data.ortho_scale = 9.0
scene.render.resolution_x = 1100
scene.render.resolution_y = 760
scene.render.filepath = os.path.join(OUT, "dauch_alumni_center_refinement_sign_detail.png")
bpy.ops.render.render(write_still=True)

# Discard temporary render-only camera/lights so the exported asset remains a
# clean geometry library. Reopen validation is performed by the calling process.
scene.camera = old_camera
scene.render.engine = old_engine
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = old_res
scene.render.film_transparent = old_transparent
for obj in [cam, *lights]:
    bpy.data.objects.remove(obj, do_unlink=True)
bpy.data.cameras.remove(cam_data)
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print("DAUCH_REFINEMENT_DONE", len(COL.all_objects), ASSET)
