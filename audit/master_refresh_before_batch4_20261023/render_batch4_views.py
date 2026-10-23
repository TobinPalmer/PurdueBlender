import bpy, json
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[2]
MOD = ROOT / 'modular'
manifest = json.loads((MOD / 'manifest.json').read_text(encoding='utf-8'))
by_id = {a['id']: a for a in manifest['assets']}
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = 'WORLD'
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'Medium High Contrast'
scene.render.resolution_x = 1400
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
cam_data = bpy.data.cameras.new('Batch4MasterReviewCamera')
cam = bpy.data.objects.new('Batch4MasterReviewCamera', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.type = 'ORTHO'
outdir = ROOT / 'audit' / 'master_refresh_before_batch4_20261023' / 'assembled_views'
outdir.mkdir(parents=True, exist_ok=True)
ids = ['rawls_hall','niswonger_aviation_tech','knoy_hall','class_of_1950','potter_engineering']
for bid in ids:
    rec = by_id[bid]
    bounds = rec.get('bounds_world_m')
    if not bounds:
        marker = bpy.data.objects[f"Placement_{bid}"]
        local = rec['local_bounds_m']
        bounds = [[local[i][0] + (marker.location[i] if i < 2 else 0.0), local[i][1] + (marker.location[i] if i < 2 else 0.0)] for i in range(3)]
    lo = [b[0] for b in bounds]
    hi = [b[1] for b in bounds]
    target = Vector(((lo[0]+hi[0])/2, (lo[1]+hi[1])/2, (lo[2]+hi[2])/2))
    offset = Vector((110.0, -130.0, 115.0))
    cam.location = target + offset
    cam.rotation_euler = (target-cam.location).to_track_quat('-Z','Y').to_euler()
    cam_data.ortho_scale = max(95.0, min(230.0, max(hi[0]-lo[0], hi[1]-lo[1])*2.25))
    scene.render.filepath = str(outdir / f'{bid}_assembled.png')
    bpy.ops.render.render(write_still=True)
    print('RENDERED', bid, scene.render.filepath)
