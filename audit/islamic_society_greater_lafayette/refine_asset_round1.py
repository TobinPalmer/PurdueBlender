"""Refine the assigned ISGL library asset without changing its GIS wall ring."""
import bpy
import hashlib
import json
import math
import shutil
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_islamic_societyof_greater_lafayette_0130012"
ASSET = ROOT / "modular" / "buildings" / (ASSET_ID + ".blend")
AUDIT = ROOT / "audit" / "islamic_society_greater_lafayette"
EXPECTED_SHA = "c84126f5b1f549db17faa7282e449fc6de171e632b6e627062ad46379247c39b"
SCENE_NAME = "Building_" + ASSET_ID
COLLECTION_NAME = "Asset_" + ASSET_ID

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def make_surface_detail(mat, kind, base_color):
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (720, 40)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (450, 40)
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.78 if kind == "brick" else 0.82
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    geo.location = (-760, 40)
    if kind == "brick":
        colors = ((0.39, 0.115, 0.071, 1), (0.30, 0.077, 0.050, 1), (0.23, 0.19, 0.16, 1))
        brick_width, row_height, mortar_size = 0.215, 0.068, 0.012
        bump_distance = 0.003
        bump_strength = 0.23
        noise_scale = 5.0
    else:
        colors = ((0.16, 0.19, 0.21, 1), (0.105, 0.13, 0.15, 1), (0.075, 0.09, 0.10, 1))
        brick_width, row_height, mortar_size = 0.34, 0.115, 0.018
        bump_distance = 0.002
        bump_strength = 0.18
        noise_scale = 9.0

    pos = nt.nodes.new("ShaderNodeSeparateXYZ")
    pos.location = (-590, 330)
    nt.links.new(geo.outputs["Position"], pos.inputs["Vector"])
    normal = nt.nodes.new("ShaderNodeSeparateXYZ")
    normal.location = (-590, -10)
    nt.links.new(geo.outputs["Normal"], normal.inputs["Vector"])
    abs_nodes = []
    for i, socket in enumerate((normal.outputs["X"], normal.outputs["Y"], normal.outputs["Z"])):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = "ABSOLUTE"
        n.location = (-390, 20 - 115 * i)
        nt.links.new(socket, n.inputs[0])
        abs_nodes.append(n)
    norm_sum = nt.nodes.new("ShaderNodeMath")
    norm_sum.operation = "ADD"
    norm_sum.location = (-190, -70)
    nt.links.new(abs_nodes[0].outputs[0], norm_sum.inputs[0])
    sum_yz = nt.nodes.new("ShaderNodeMath")
    sum_yz.operation = "ADD"
    sum_yz.location = (-20, -100)
    nt.links.new(abs_nodes[1].outputs[0], sum_yz.inputs[0])
    nt.links.new(abs_nodes[2].outputs[0], sum_yz.inputs[1])
    nt.links.new(abs_nodes[0].outputs[0], norm_sum.inputs[1])
    total_norm = nt.nodes.new("ShaderNodeMath")
    total_norm.operation = "ADD"
    total_norm.location = (130, -80)
    nt.links.new(abs_nodes[0].outputs[0], total_norm.inputs[0])
    nt.links.new(sum_yz.outputs[0], total_norm.inputs[1])

    projections = []
    for idx, components in enumerate((("Y", "Z"), ("X", "Z"), ("X", "Y"))):
        combine = nt.nodes.new("ShaderNodeCombineXYZ")
        combine.location = (-350, 380 - idx * 220)
        nt.links.new(pos.outputs[components[0]], combine.inputs["X"])
        nt.links.new(pos.outputs[components[1]], combine.inputs["Y"])
        tex = nt.nodes.new("ShaderNodeTexBrick")
        tex.location = (-90, 380 - idx * 220)
        tex.inputs["Color1"].default_value = colors[0]
        tex.inputs["Color2"].default_value = colors[1]
        tex.inputs["Mortar"].default_value = colors[2]
        tex.inputs["Scale"].default_value = 1.0
        tex.inputs["Mortar Size"].default_value = mortar_size
        tex.inputs["Mortar Smooth"].default_value = 0.05
        tex.inputs["Brick Width"].default_value = brick_width
        tex.inputs["Row Height"].default_value = row_height
        nt.links.new(combine.outputs["Vector"], tex.inputs["Vector"])
        projections.append(tex)
    sum_xy = nt.nodes.new("ShaderNodeMath")
    sum_xy.operation = "ADD"
    sum_xy.location = (120, -250)
    nt.links.new(abs_nodes[0].outputs[0], sum_xy.inputs[0])
    nt.links.new(abs_nodes[1].outputs[0], sum_xy.inputs[1])
    fac_x = nt.nodes.new("ShaderNodeMath")
    fac_x.operation = "DIVIDE"
    fac_x.location = (300, -210)
    nt.links.new(abs_nodes[0].outputs[0], fac_x.inputs[0])
    nt.links.new(sum_xy.outputs[0], fac_x.inputs[1])
    mix_xy = nt.nodes.new("ShaderNodeMixRGB")
    mix_xy.blend_type = "MIX"
    mix_xy.location = (300, 300)
    nt.links.new(fac_x.outputs[0], mix_xy.inputs[0])
    nt.links.new(projections[0].outputs["Color"], mix_xy.inputs[1])
    nt.links.new(projections[1].outputs["Color"], mix_xy.inputs[2])
    fac_z = nt.nodes.new("ShaderNodeMath")
    fac_z.operation = "DIVIDE"
    fac_z.location = (300, -330)
    nt.links.new(abs_nodes[2].outputs[0], fac_z.inputs[0])
    nt.links.new(total_norm.outputs[0], fac_z.inputs[1])
    mix_all = nt.nodes.new("ShaderNodeMixRGB")
    mix_all.blend_type = "MIX"
    mix_all.location = (460, 300)
    nt.links.new(fac_z.outputs[0], mix_all.inputs[0])
    nt.links.new(mix_xy.outputs[0], mix_all.inputs[1])
    nt.links.new(projections[2].outputs["Color"], mix_all.inputs[2])
    nt.links.new(mix_all.outputs[0], bsdf.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (215, -120)
    bump.inputs["Distance"].default_value = bump_distance
    bump.inputs["Strength"].default_value = bump_strength
    nt.links.new(projections[0].outputs["Fac"], bump.inputs["Height"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-500, -170)
    noise.inputs["Scale"].default_value = noise_scale
    noise.inputs["Detail"].default_value = 2.0
    noise.inputs["Roughness"].default_value = 0.65
    nt.links.new(geo.outputs["Position"], noise.inputs["Vector"])
    rough = nt.nodes.new("ShaderNodeMapRange")
    rough.location = (-110, -170)
    rough.inputs["From Min"].default_value = 0.0
    rough.inputs["From Max"].default_value = 1.0
    rough.inputs["To Min"].default_value = 0.7 if kind == "brick" else 0.74
    rough.inputs["To Max"].default_value = 0.88 if kind == "brick" else 0.91
    nt.links.new(noise.outputs["Fac"], rough.inputs["Value"])
    nt.links.new(rough.outputs["Result"], bsdf.inputs["Roughness"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    mat["surface_detail"] = "Procedural physical-scale brick courses and subtle relief" if kind == "brick" else "Procedural small slate-course seams and subtle relief"

def track(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()

def add_area(scene, name, loc, target, power, size, color):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = loc
    track(obj, target)
    return obj

def set_camera(scene, name, loc, target, ortho_scale):
    data = bpy.data.cameras.new(name)
    data.type = "ORTHO"
    data.ortho_scale = ortho_scale
    cam = bpy.data.objects.new(name, data)
    scene.collection.objects.link(cam)
    cam.location = loc
    track(cam, target)
    scene.camera = cam
    return cam

def main():
    before = sha(ASSET)
    if before != EXPECTED_SHA:
        raise RuntimeError(f"Asset changed since exact-hash review: {before}")
    shutil.copy2(ASSET, AUDIT / "pre_refinement_c84126f.blend")
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.data.scenes.get(SCENE_NAME)
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if not scene or not collection:
        raise RuntimeError("Stable scene or asset collection missing")
    bpy.context.window.scene = scene
    original = bpy.data.objects.get("Islamic Society of Greater Lafayette")
    if not original or original.type != "MESH":
        raise RuntimeError("Expected stable building mesh missing")
    if len(original.data.vertices) != 982 or len(original.data.polygons) != 747:
        raise RuntimeError("Starting structural mesh differs from reviewed asset")
    mesh = original.data
    old_ring = [tuple(v.co) for v in mesh.vertices[:11]]
    mats = {m.name: m for m in mesh.materials if m}
    make_surface_detail(mats["ISGL | red-brown brick"], "brick", (0.38, 0.105, 0.065))
    make_surface_detail(mats["ISGL | charcoal gray hipped roof"], "slate", (0.13, 0.16, 0.18))

    # The source has no reliable floor plan. This inset floor patch is explicitly
    # schematic and has no room partitions, furniture, or named room functions.
    world = [original.matrix_world @ v.co for v in mesh.vertices]
    cx = (min(v.x for v in world) + max(v.x for v in world)) / 2
    cy = (min(v.y for v in world) + max(v.y for v in world)) / 2
    zbase = 0.22
    floor_width, floor_depth, floor_thickness = 8.0, 6.0, 0.10
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, zbase + floor_thickness / 2))
    floor = bpy.context.object
    floor.name = "ISGL_Schematic_Interior_Open_Gathering_Space_Floor"
    floor.dimensions = (floor_width, floor_depth, floor_thickness)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    floor["accuracy_status"] = "schematic; no verified floor plan"
    floor["layout_note"] = "An open placeholder gathering area only; no room partitions or room-specific layout are asserted."
    floor["source_basis"] = "No reliable interior plan was found in the reviewed source package."
    floor_mat = bpy.data.materials.new("ISGL | schematic interior neutral floor")
    floor_mat.diffuse_color = (0.48, 0.43, 0.35, 1)
    floor_mat.use_nodes = True
    floor_bsdf = floor_mat.node_tree.nodes.get("Principled BSDF")
    floor_bsdf.inputs["Base Color"].default_value = (0.48, 0.43, 0.35, 1)
    floor_bsdf.inputs["Roughness"].default_value = 0.88
    floor.data.materials.append(floor_mat)
    for c in list(floor.users_collection):
        c.objects.unlink(floor)
    collection.objects.link(floor)

    text_curve = bpy.data.curves.new("ISGL schematic label data", "FONT")
    text_curve.body = "SCHEMATIC OPEN SPACE"
    text_curve.size = 0.48
    text_curve.extrude = 0.003
    label = bpy.data.objects.new("ISGL_Schematic_Interior_Label", text_curve)
    collection.objects.link(label)
    label.location = (cx - floor_width * 0.5 + 0.22, cy - 0.2, zbase + floor_thickness + 0.01)
    label["accuracy_status"] = "annotation only; not a verified room name"
    label_mat = bpy.data.materials.new("ISGL | schematic interior label ink")
    label_mat.diffuse_color = (0.12, 0.09, 0.06, 1)
    label_mat.use_nodes = True
    label_mat.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.12, 0.09, 0.06, 1)
    text_curve.materials.append(label_mat)

    # Roof geometry was already supported as two intersecting hip-roof volumes.
    # Existing close imagery does not support a more exact pitch/edge/opening edit.
    scene["interior_accuracy_note"] = "Schematic open gathering-area floor patch only; no verified plan, partitions, or room uses are represented."
    scene["identity_source_caveat"] = "Purdue GIS FID 771 is labeled Muslim Student Association / 1021 FIRST ST.; ISGL's current page lists 1022 1st St. No exact formal crosswalk is asserted."

    # Render previews from a controlled temporary setup.
    old_world = scene.world
    world_data = old_world or bpy.data.worlds.new("ISGL preview world")
    scene.world = world_data
    world_data.use_nodes = True
    world_data.node_tree.nodes["Background"].inputs["Color"].default_value = (0.19, 0.23, 0.28, 1)
    world_data.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"
    center = Vector((cx, cy, 3.7))
    lights = [
        add_area(scene, "ISGL temporary key", (cx + 25, cy - 30, 34), center, 6500, 26, (1.0, 0.82, 0.65)),
        add_area(scene, "ISGL temporary fill", (cx - 28, cy + 6, 22), center, 4700, 25, (0.73, 0.83, 1.0)),
    ]
    cam = set_camera(scene, "ISGL temporary exterior camera", (cx + 38, cy - 43, 35), center, 43)
    scene.render.filepath = str(AUDIT / "refined_exterior_preview.png")
    bpy.ops.render.render(write_still=True)

    # The cutaway is only for the preview. Hide roof-assigned faces in a temporary
    # render mesh while preserving the saved exterior mesh untouched.
    roof_indices = {i for i, m in enumerate(mesh.materials) if m and m.name == "ISGL | charcoal gray hipped roof"}
    kept_polys = []
    for p in mesh.polygons:
        mean_z = sum(mesh.vertices[i].co.z for i in p.vertices) / len(p.vertices)
        if p.material_index in roof_indices or (mean_z > 4.2 and abs(p.normal.z) > 0.55):
            continue
        kept_polys.append(p)
    temp_data = bpy.data.meshes.new("TEMP ISGL cutaway geometry")
    verts = [v.co.copy() for v in mesh.vertices]
    faces = [list(p.vertices) for p in kept_polys]
    temp_data.from_pydata(verts, [], faces)
    temp_data.update()
    cutaway = bpy.data.objects.new("TEMP ISGL roof-open cutaway preview", temp_data)
    cutaway.matrix_world = original.matrix_world.copy()
    scene.collection.objects.link(cutaway)
    cutaway.hide_render = True
    for material in mesh.materials:
        cutaway.data.materials.append(material)
    # Restore each surviving material index by matching source face vertex order.
    source_index = {tuple(p.vertices): p.material_index for p in kept_polys}
    for p in cutaway.data.polygons:
        p.material_index = source_index.get(tuple(p.vertices), 0)
    original.hide_render = False
    original.data = temp_data
    cam.location = (cx + 25, cy - 28, 31)
    cam.data.ortho_scale = 41
    track(cam, (cx, cy, 1.8))
    scene.render.filepath = str(AUDIT / "refined_schematic_interior_preview.png")
    bpy.ops.render.render(write_still=True)
    original.data = mesh
    bpy.data.objects.remove(cutaway, do_unlink=True)
    bpy.data.meshes.remove(temp_data)
    cam_data = cam.data
    light_data = [light.data for light in lights]
    for obj in [cam, *lights]:
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.cameras.remove(cam_data)
    for light_block in light_data:
        bpy.data.lights.remove(light_block)
    scene.world = old_world
    if world_data != old_world:
        bpy.data.worlds.remove(world_data)

    # Ensure original structure and its base ring are unchanged.
    if len(mesh.vertices) != 982 or len(mesh.polygons) != 747:
        raise RuntimeError("Structural mesh count changed")
    new_ring = [tuple(v.co) for v in mesh.vertices[:11]]
    if old_ring != new_ring:
        raise RuntimeError("GIS shell ring changed")
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    result = {
        "asset": str(ASSET), "sha256": sha(ASSET), "blender_version": bpy.app.version_string,
        "scene": scene.name, "collection": collection.name,
        "stable_mesh": original.name, "stable_mesh_vertices": len(mesh.vertices),
        "stable_mesh_faces": len(mesh.polygons), "gis_ring_unchanged": True,
        "new_objects": [floor.name, label.name],
        "interior": {"accuracy_status": floor["accuracy_status"], "dimensions_m": [floor_width, floor_depth, floor_thickness], "room_partitions": 0},
        "surface_materials_refined": ["ISGL | red-brown brick", "ISGL | charcoal gray hipped roof"],
        "roof_geometry_changed": False,
        "previews": ["refined_exterior_preview.png", "refined_schematic_interior_preview.png"],
        "identity_caveat": scene["identity_source_caveat"],
    }
    (AUDIT / "refinement_round1.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
