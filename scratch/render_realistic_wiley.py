import bpy, math, sys, time
from pathlib import Path
from mathutils import Euler, Vector

print("=== Setting up Realistic Lighting & Shadows for Wiley Hall ===")

scene = bpy.context.scene

# 1. Configure GPU Devices for Cycles OptiX
prefs = bpy.context.preferences
cprefs = prefs.addons.get('cycles')
if cprefs:
    cprefs = cprefs.preferences
    cprefs.compute_device_type = 'OPTIX'
    cprefs.get_devices()
    for d in cprefs.devices:
        if d.type == 'OPTIX':
            d.use = True
            print(f"Enabled OptiX device: {d.name}")
        else:
            d.use = False

scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = 128
scene.cycles.preview_samples = 32
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'
scene.cycles.max_bounces = 8
scene.cycles.diffuse_bounces = 4
scene.cycles.glossy_bounces = 4
scene.cycles.transmission_bounces = 4
scene.cycles.transparent_max_bounces = 8

# Color Management (AgX)
scene.display_settings.display_device = 'sRGB'
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = -0.65

# Resolution (1920x1080)
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.compression = 15

# 2. Camera Setup
cam = bpy.data.objects.get('Cam_07_Wiley_Hall_StreetView')
if not cam:
    print("ERROR: Camera Cam_07_Wiley_Hall_StreetView not found!")
    sys.exit(1)

scene.camera = cam
# Improve architectural framing: lens 35mm (instead of ultra-wide 28mm) brings the building closer
# and showcases the brick texture, windows, and tree shadows with great composition
cam.data.lens = 36.0
# Slightly elevate and adjust Z to frame the ground, trees, and roof beautifully
cam.location = Vector((-599.2, 85.0, 7.5))
cam.rotation_euler = Euler((math.radians(88.0), 0.0, 0.0), 'XYZ')
print(f"Using Camera: {cam.name} at {cam.location}, lens={cam.data.lens}mm")

# 3. Sunlight & World Setup
# Only keep master sun active
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

# Directional Sunlight:
# Elevation 34 deg, Azimuth 215 deg (South-Southwest)
# Shines onto the south facade and inside the courtyard at a warm, dynamic angle
elevation_deg = 34.0
azimuth_deg = 215.0

rot_x = math.radians(90.0 - elevation_deg)
rot_z = math.radians(azimuth_deg - 180.0)
master_sun.rotation_euler = Euler((rot_x, 0.0, rot_z), 'XYZ')

master_sun.data.energy = 4.2
master_sun.data.color = (1.0, 0.965, 0.915)  # Natural warm solar tint (~5500K)
master_sun.data.angle = math.radians(0.54)   # Physical angular diameter -> soft shadow penumbra

print(f"Master Sun configured: energy={master_sun.data.energy}, angle={master_sun.data.angle:.4f} rad, rot={master_sun.rotation_euler}")

# Configure Nishita Sky in World
w = scene.world
if w and w.node_tree:
    for n in w.node_tree.nodes:
        if n.type == 'TEX_SKY':
            n.sky_type = 'MULTIPLE_SCATTERING'
            n.sun_elevation = math.radians(elevation_deg)
            n.sun_rotation = math.radians(azimuth_deg)
            n.sun_disc = True
            n.sun_size = math.radians(0.54)
            n.air_density = 1.0
            n.aerosol_density = 0.4
            n.ozone_density = 1.0
            n.altitude = 185.0
            n.ground_albedo = 0.2
            print("Configured Nishita Sky texture.")
        elif n.type == 'BACKGROUND':
            n.inputs['Strength'].default_value = 0.75  # Balanced ambient fill

# 4. Render output path
out_path = Path("renders/wiley_hall/wiley_hall_realistic.png").resolve()
scene.render.filepath = str(out_path)

print(f"Starting Cycles OptiX render to: {out_path} ...")
t0 = time.time()
bpy.ops.render.render(write_still=True)
t1 = time.time()
print(f"Cycles OptiX render complete in {t1 - t0:.2f} seconds!")
