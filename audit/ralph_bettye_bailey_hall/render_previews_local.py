"""Render exterior and schematic plan previews from a freshly saved BALY library."""
import bpy
from mathutils import Vector
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset = root / 'modular/buildings/massing_ralph_bettye_bailey_hall_406c4db.blend'
out = Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(asset))
obj = bpy.data.objects['Ralph & Bettye Bailey Hall']
scene = bpy.context.scene

def look_at(camera, target):
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()

def add_camera(name, loc, target, scale):
    data = bpy.data.cameras.new(name)
    data.type = 'ORTHO'; data.ortho_scale = scale
    camera = bpy.data.objects.new(name, data); scene.collection.objects.link(camera)
    camera.location = loc; look_at(camera, target)
    return camera

def add_area(name, loc, target, power, size):
    data = bpy.data.lights.new(name, 'AREA'); data.energy = power; data.shape = 'DISK'; data.size = size
    light = bpy.data.objects.new(name, data); scene.collection.objects.link(light)
    light.location = loc; look_at(light, target)
    return light

scene.render.engine = 'CYCLES'; scene.cycles.samples = 24
scene.render.resolution_x = 1500; scene.render.resolution_y = 1100; scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'AgX'; scene.view_settings.exposure = -0.8
world = bpy.data.worlds.new('Bailey review sky') if not bpy.data.worlds else bpy.data.worlds[0]
world.use_nodes = True; world.node_tree.nodes['Background'].inputs[0].default_value = (0.11, 0.16, 0.23, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.32; scene.world = world
add_area('Bailey review key', (-28, -35, 42), (0, 0, 4), 380, 22)
add_area('Bailey review fill', (25, -5, 24), (0, 0, 4), 160, 28)

ground_mesh = bpy.data.meshes.new('Bailey review ground mesh')
ground_mesh.from_pydata([(-70,-70,-0.12),(70,-70,-0.12),(70,70,-0.12),(-70,70,-0.12)], [], [(0,1,2,3)])
ground = bpy.data.objects.new('Bailey review ground', ground_mesh); scene.collection.objects.link(ground)
ground_mat = bpy.data.materials.new('Bailey review ground material'); ground_mat.use_nodes = True
ground_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.18, 0.21, 0.23, 1)
ground_mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.94
ground_mesh.materials.append(ground_mat)

camera = add_camera('Bailey exterior front view', (-42, -28, 27), (0, 0, 4.2), 54)
scene.camera = camera; scene.render.filepath = str(out / 'preview_exterior_front.png')
bpy.ops.render.render(write_still=True)
camera.location = (-39, 33, 27); look_at(camera, (0, 0, 4.2)); camera.data.ortho_scale = 55
scene.render.filepath = str(out / 'preview_exterior_three_quarter.png')
bpy.ops.render.render(write_still=True)

# Make a temporary plan-only mesh from the source-backed interior faces. This lives
# only in this preview process; the saved asset remains the single stable building mesh.
interior_polys = [p for p in obj.data.polygons if p.material_index >= 5]
plan_vertices, plan_faces, plan_mats = [], [], []
for poly in interior_polys:
    face = []
    for loop_index in poly.loop_indices:
        source_index = obj.data.loops[loop_index].vertex_index
        face.append(len(plan_vertices)); plan_vertices.append(tuple(obj.data.vertices[source_index].co))
    plan_faces.append(face); plan_mats.append(poly.material_index)
plan_mesh = bpy.data.meshes.new('Temporary first-floor plan preview')
plan_mesh.from_pydata(plan_vertices, [], plan_faces)
for mat in obj.data.materials:
    plan_mesh.materials.append(mat)
for poly, material_index in zip(plan_mesh.polygons, plan_mats): poly.material_index = material_index
plan_mesh.update()
plan = bpy.data.objects.new('Temporary first-floor room zones', plan_mesh); scene.collection.objects.link(plan)
obj.hide_render = True

def plan_xy(px, py):
    return ((342.0 - py) * (26.323 / 470.0), (px - 569.0) * (35.642 / 648.0))

labels = [
    ('LOUNGE', 312, 510), ('LARGE REHEARSAL 1', 580, 205),
    ('LARGE REHEARSAL 2', 570, 500), ('SMALL REHEARSAL 1', 780, 500),
    ('SMALL REHEARSAL 2', 726, 500), ('STAIR', 724, 268), ('LOBBY / RECEPTION', 430, 390),
    ('RESTROOMS', 340, 265), ('STORAGE', 820, 230),
]
for text, px, py in labels:
    x, y = plan_xy(px, py)
    curve = bpy.data.curves.new(text, 'FONT'); curve.body = text; curve.size = 0.70
    curve.align_x = 'CENTER'; curve.align_y = 'CENTER'; curve.size = 0.48
    material = bpy.data.materials.new('Bailey plan label dark'); material.use_nodes = True
    nodes = material.node_tree.nodes; nodes.clear()
    emission = nodes.new('ShaderNodeEmission'); emission.inputs['Color'].default_value = (0.015, 0.012, 0.009, 1)
    output = nodes.new('ShaderNodeOutputMaterial'); material.node_tree.links.new(emission.outputs[0], output.inputs['Surface'])
    curve.materials.append(material)
    label = bpy.data.objects.new(text, curve); scene.collection.objects.link(label); label.location = (x, y, 0.25)
    label.visible_shadow = False

title_curve = bpy.data.curves.new('Schematic caveat', 'FONT')
title_curve.body = 'SCHEMATIC PLAN • SCALE AND NORTH ORIENTATION UNVERIFIED'
title_curve.size = 0.60; title_curve.align_x = 'CENTER'; title_curve.align_y = 'CENTER'
title_mat = bpy.data.materials.new('Bailey caveat label'); title_mat.use_nodes = True
nodes = title_mat.node_tree.nodes; nodes.clear()
emission = nodes.new('ShaderNodeEmission'); emission.inputs['Color'].default_value = (0.015, 0.012, 0.009, 1)
output = nodes.new('ShaderNodeOutputMaterial'); title_mat.node_tree.links.new(emission.outputs[0], output.inputs['Surface'])
title_curve.materials.append(title_mat)
title = bpy.data.objects.new('Schematic caveat', title_curve); scene.collection.objects.link(title)
title.location = (0.0, -22.0, 0.25); title.visible_shadow = False

camera.location = (0, -2.0, 52); look_at(camera, (0, -2.0, 0)); camera.data.ortho_scale = 58
scene.render.resolution_x = 1600; scene.render.resolution_y = 1200
scene.render.filepath = str(out / 'preview_interior_schematic.png')
scene.camera = camera
bpy.ops.render.render(write_still=True)
print('Rendered previews to', out)
