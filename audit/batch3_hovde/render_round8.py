import bpy
from mathutils import Vector
from pathlib import Path

P = Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
bpy.ops.wm.open_mainfile(filepath=str(P / 'modular/buildings/hovde_hall.blend'))
s = bpy.context.scene
c = bpy.data.collections['Asset_hovde_hall']
s.render.engine = 'BLENDER_EEVEE'
s.eevee.taa_render_samples = 96
s.render.resolution_x, s.render.resolution_y = 1600, 1000
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'
s.view_settings.view_transform = 'AgX'
s.view_settings.look = 'AgX - Medium High Contrast'
s.view_settings.exposure = .55
root = bpy.data.objects['HOVD_Root']
side = (root.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()
along = (root.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()

def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()

def camera(name, loc, target, scale):
    data = bpy.data.cameras.new(name)
    obj = bpy.data.objects.new(name, data)
    s.collection.objects.link(obj)
    obj.location = loc
    aim(obj, target)
    data.type = 'ORTHO'
    data.ortho_scale = scale
    return obj

def area(name, loc, target, power, size):
    data = bpy.data.lights.new(name, 'AREA')
    obj = bpy.data.objects.new(name, data)
    s.collection.objects.link(obj)
    obj.location = loc
    data.energy = power
    data.shape = 'DISK'
    data.size = size
    aim(obj, target)
    return obj

port = bpy.data.objects['HOVD_Portico_Entablature'].matrix_world.translation.copy()
for args in [('R8_Key', port + side*42 + along*14 + Vector((0,0,42)), port, 2600, 45),
             ('R8_Fill', port - side*28 - along*16 + Vector((0,0,28)), port, 2100, 48)]:
    area(*args)
cam = camera('R8_Exterior', port+side*77+along*9+Vector((0,0,26)), port+Vector((0,0,1)), 96)
s.camera = cam
s.render.filepath = str(P / 'audit/batch3_hovde/exterior_round8.png')
bpy.ops.render.render(write_still=True)

# Low approach detail: align camera with the east facade normal so the columns frame the door bays.
target = port + Vector((0,0,-2.6))
cam.location = target + side*43 + Vector((0,0,6.5))
aim(cam, target)
cam.data.ortho_scale = 32
s.render.filepath = str(P / 'audit/batch3_hovde/portico_detail_round8.png')
bpy.ops.render.render(write_still=True)

# Interpretive room cutaways: show the modeled floor, actual three retained walls, and furniture together.
# The floor plans are not verified by historical room plans; camera-facing walls/ceiling are temporarily hidden.
roomsets = [
    ('Pres', 'HOVD_Pres_Floor', 'presidential_office_cutaway_round8.png'),
    ('Board', 'HOVD_Board_Floor', 'trustees_boardroom_cutaway_round8.png')
]
for tag, floorname, outname in roomsets:
    for obj in s.objects:
        if obj.type not in {'CAMERA','LIGHT'}:
            obj.hide_render = True
    # Reveal all components in the selected room; retain three perimeter walls and floor.
    for obj in s.objects:
        n = obj.name
        if n.startswith(f'HOVD_{tag}_') or (tag == 'Board' and n.startswith('HOVD_Chair_')):
            obj.hide_render = False
        if n.endswith('_Ceiling') or 'Room_Wall_Front' in n or 'Room_Wall_E' in n:
            obj.hide_render = True
    # Remove the front door leaf/header from the isolated three-quarter cutaway; the entry opening is visible.
    for n in (f'HOVD_{tag}_Room_Door_Leaf', f'HOVD_{tag}_Room_Door_Header'):
        if n in bpy.data.objects:
            bpy.data.objects[n].hide_render = True
    for obj in s.objects:
        if obj.type == 'LIGHT':
            obj.hide_render = True
    focus = bpy.data.objects[floorname].matrix_world.translation.copy() + Vector((0,0,1.25))
    cam.location = focus + side*13 - along*18 + Vector((0,0,12))
    aim(cam, focus)
    cam.data.ortho_scale = 14.5
    bpy.context.view_layer.update()
    local_fill = area(f'R8_{tag}_RoomFill', focus + Vector((0,0,10)), focus, 850, 9)
    label_curve = bpy.data.curves.new(f'R8_{tag}_InterpretiveLabel', type='FONT')
    label_curve.body = 'INTERPRETIVE LAYOUT  |  ROOM PLAN NOT SOURCE-VERIFIED'
    label_curve.size = .22
    label_curve.extrude = 0
    label = bpy.data.objects.new(f'R8_{tag}_InterpretiveLabel', label_curve)
    s.collection.objects.link(label)
    label.location = cam.matrix_world @ Vector((-6.7, -4.2, -14))
    label.rotation_euler = cam.rotation_euler
    ink = bpy.data.materials.new(f'R8_{tag}_LabelInk')
    ink.diffuse_color = (.03,.03,.03,1)
    ink.use_nodes = True
    ink.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (.03,.03,.03,1)
    ink.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value = (.03,.03,.03,1)
    ink.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value = .7
    label.data.materials.append(ink)
    s.camera = cam
    s.view_settings.exposure = -.25
    s.render.filepath = str(P / 'audit/batch3_hovde' / outname)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(label, do_unlink=True)
    bpy.data.curves.remove(label_curve)
    bpy.data.materials.remove(ink)
    local_light_data = local_fill.data
    bpy.data.objects.remove(local_fill, do_unlink=True)
    if local_light_data.users == 0:
        bpy.data.lights.remove(local_light_data)
print('Round 8 exterior and labeled interpretive 3/4 cutaways rendered from reopened saved asset.')

