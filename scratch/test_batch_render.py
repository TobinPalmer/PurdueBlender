import bpy, os, json, time
from pathlib import Path
from mathutils import Vector

ROOT = Path('.').resolve()
RENDERS_DIR = ROOT / 'renders'
RENDERS_DIR.mkdir(parents=True, exist_ok=True)

s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE'
s.view_settings.exposure = -0.65
s.eevee.shadow_resolution_scale = 0.25
if hasattr(s.eevee, 'light_threshold'):
    s.eevee.light_threshold = 0.1
opts = {i.identifier for i in s.eevee.bl_rna.properties['shadow_pool_size'].enum_items}
if '512' in opts:
    s.eevee.shadow_pool_size = '512'

s.render.resolution_x = 1600
s.render.resolution_y = 1000
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'
s.eevee.taa_render_samples = 64

# Test with 2 buildings
test_jobs = [
    ('hovde_hall', 'Cam_77_Hovde_South_Hero'),
    ('armory', 'Cam_87_Armory_UniversitySt_Hero')
]

for b_id, cam_name in test_jobs:
    b_dir = RENDERS_DIR / b_id
    b_dir.mkdir(parents=True, exist_ok=True)
    out_file = b_dir / f"{b_id}_campus_hero.png"
    
    cam = bpy.data.objects.get(cam_name)
    if not cam:
        print(f"Camera {cam_name} not found!")
        continue
        
    s.camera = cam
    s.render.filepath = str(out_file)
    print(f"Rendering {b_id} using {cam_name} -> {out_file}...")
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    dt = time.time() - t0
    print(f"Done in {dt:.2f}s! File size: {out_file.stat().st_size} bytes")

print("Test render complete!")
