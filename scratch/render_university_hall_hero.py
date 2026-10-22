import bpy, math, sys, time, shutil
from pathlib import Path
from mathutils import Euler, Vector

print("=== Rendering University Hall Hero with True East-Facing Sunlight & Shadows ===")

scene = bpy.context.scene

# Configure Cycles OptiX
prefs = bpy.context.preferences
cprefs = prefs.addons.get('cycles')
if cprefs:
    cprefs = cprefs.preferences
    cprefs.compute_device_type = 'OPTIX'
    cprefs.get_devices()
    for d in cprefs.devices:
        if d.type == 'OPTIX':
            d.use = True
        else:
            d.use = False

scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = 320
scene.cycles.preview_samples = 32
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'
scene.cycles.max_bounces = 8
scene.cycles.diffuse_bounces = 4
scene.cycles.glossy_bounces = 4
scene.cycles.transmission_bounces = 4
scene.cycles.transparent_max_bounces = 8

# Color Management (AgX) - Balanced outdoor daylight exposure
scene.display_settings.display_device = 'sRGB'
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = -1.25

# Resolution (High-Definition 1920x1080)
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.compression = 15

# Camera
cam = bpy.data.objects.get('Cam_52_University_Hall_East_MemorialMall_StreetView')
scene.camera = cam

# Set accurate camera transform
cam.location = Vector((-78.0000, -242.5300, 3.8000))
cam.rotation_euler = Euler((1.709, 0.0, 1.4289), 'XYZ')
cam.data.lens = 22.0

# Master Sun setup
# Sun from South-East (azimuth ~135 deg, elevation ~36 deg)
# University Hall faces East towards Memorial Mall.
# This hits the East facade at a classic 45-degree angle, casting crisp, defined shadows
# from window lintels, sills, the cupola, the entrance portico, and John Purdue's monument!
elevation_deg = 36.0
azimuth_deg = 135.0

master_sun = None
for o in bpy.data.objects:
    if o.type == 'LIGHT' and o.data.type == 'SUN':
        if o.name == 'Sun_Purdue_Daylight':
            master_sun = o
            o.hide_render = False
        else:
            o.hide_render = True

if not master_sun:
    for o in bpy.data.objects:
        if o.type == 'LIGHT' and o.data.type == 'SUN' and not o.hide_render:
            master_sun = o
            break

rot_x = math.radians(90.0 - elevation_deg)
rot_z = math.radians(azimuth_deg - 180.0)
master_sun.rotation_euler = Euler((rot_x, 0.0, rot_z), 'XYZ')

master_sun.data.energy = 3.6
master_sun.data.color = (1.0, 0.965, 0.915)  # Natural warm morning solar spectrum (~5500K)
master_sun.data.angle = math.radians(0.545)   # Physical angular diameter -> soft shadow penumbra

print(f"Master Sun: energy={master_sun.data.energy}, angle={master_sun.data.angle:.4f} rad, rot={master_sun.rotation_euler}")

# Nishita Sky in World
w = scene.world
if w and w.node_tree:
    for n in w.node_tree.nodes:
        if n.type == 'TEX_SKY':
            n.sky_type = 'MULTIPLE_SCATTERING'
            n.sun_elevation = math.radians(elevation_deg)
            n.sun_rotation = math.radians(azimuth_deg)
            n.sun_disc = True
            n.sun_size = math.radians(0.545)
            n.air_density = 1.0
            n.aerosol_density = 0.5
            n.ozone_density = 1.0
            n.altitude = 185.0
            n.ground_albedo = 0.2
        elif n.type == 'BACKGROUND':
            n.inputs['Strength'].default_value = 0.55

# Output paths
out_hero = Path("renders/university_hall/university_hall_realistic.png").resolve()
out_standard = Path("renders/university_hall/university_hall_render.png").resolve()

scene.render.filepath = str(out_hero)

print(f"Starting Cycles OptiX render to: {out_hero} ...")
t0 = time.time()
bpy.ops.render.render(write_still=True)
t1 = time.time()
print(f"Cycles OptiX render complete in {t1 - t0:.2f} seconds!")

shutil.copyfile(str(out_hero), str(out_standard))
print(f"Copied realistic render to primary {out_standard}")
