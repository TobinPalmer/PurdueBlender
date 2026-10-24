import bpy, os
from mathutils import Vector

ROOT = r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET = ROOT + r'/modular/buildings/krannert_building.blend'
OUT = ROOT + r'/audit/batch2_krannert'
bpy.ops.wm.open_mainfile(filepath=ASSET)
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.cycles.samples = 16
s.cycles.use_denoising = True
s.render.resolution_x = 1200
s.render.resolution_y = 900
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'
s.render.film_transparent = False
s.world.use_nodes = True
bg = s.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (.80, .83, .86, 1)
bg.inputs['Strength'].default_value = .7

# Audit-only top-down views isolate just one furnished story at a time. The
# building shell, other stories, and original slab stack are hidden for render
# only; this prevents overlaid levels and keeps the source file untouched.
bpy.ops.object.light_add(type='AREA', location=(-14.5, -2.2, 25))
light = bpy.context.object
light.data.energy = 2600
light.data.shape = 'DISK'
light.data.size = 16
bpy.ops.object.camera_add(location=(-14.5, -2.2, 35))
cam = bpy.context.object
cam.rotation_euler = (Vector((-14.5, -2.2, 9.4)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 24
s.camera = cam

def z_center(o):
    try:
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        return (min(v.z for v in bb) + max(v.z for v in bb)) * .5
    except Exception:
        return o.location.z

def render_level(target_z, floor_z, story, filename):
    cam.location = (-14.5, -2.2, target_z + 20)
    cam.rotation_euler = (Vector((-14.5, -2.2, target_z)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    for o in bpy.data.objects:
        name = o.name
        keep = False
        if name.startswith(('KRAN_R1_', 'KRAN_New_', 'KRAN_R2_')):
            z = z_center(o)
            keep = (floor_z - .2) <= z <= (floor_z + 3.0)
        o.hide_render = not keep
    # Neutral audit ground so furniture footprints and clear aisles read cleanly.
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-14.5, -2.2, floor_z))
    floor = bpy.context.object
    floor.name = 'TEMP_RenderOnly_' + story + '_Floor'
    floor.dimensions = (17.0, 15.0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    floor_mat = bpy.data.materials.new('TEMP_RenderOnly_' + story + '_Floor_Mat')
    floor_mat.diffuse_color = (.30, .32, .34, 1)
    floor_mat.use_nodes = True
    floor_mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (.30, .32, .34, 1)
    floor.data.materials.append(floor_mat)
    s.render.filepath = OUT + '/' + filename
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(floor, do_unlink=True)

render_level(5.1, 3.88, 'drawingroom', 'drawingroom_plan_r2.png')
render_level(9.7, 8.52, 'parrish', 'parrish_plan_r2.png')
