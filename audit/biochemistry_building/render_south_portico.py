"""Render a source-relevant south-facing close view without changing the asset."""
import bpy
import math
import os
from mathutils import Vector

AUDIT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(AUDIT, '..', '..'))
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'biochemistry_building.blend')
OUTPUT = os.path.join(AUDIT, 'biochemistry_building_south_portico_preview.png')

bpy.ops.wm.open_mainfile(filepath=ASSET)
scene = bpy.context.scene
camera = scene.camera
assert camera is not None
entry = bpy.data.objects['BCHM south portico paired glass entry']
corners = [entry.matrix_world @ Vector(corner) for corner in entry.bound_box]
target = Vector((sum(p.x for p in corners) / 8, sum(p.y for p in corners) / 8, 9.0))
camera.location = (target.x, target.y - 48.0, target.z + 10.0)
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.lens = 48
scene.render.resolution_x = 1280
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.cycles.samples = 16
scene.render.filepath = OUTPUT
bpy.ops.render.render(write_still=True)
print('Rendered', OUTPUT)
