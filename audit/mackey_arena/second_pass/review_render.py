"""Standard second-pass review render set (headless).

blender -b <asset.blend> --python review_render.py -- <outdir> <prefix> [extra_json]
Renders elevations N/E/S/W (orthographic), obliques NE/SE/SW/NW (perspective 35 mm),
top (orthographic) and optional close-ups from extra_json: [{"name":..,"loc":[..],"look":[..],"lens":..}].
Builds its own temporary camera/light/world; nothing is saved to the asset.
"""
import bpy, sys, json, math, os, hashlib, mathutils

argv = sys.argv[sys.argv.index("--") + 1:]
outdir, prefix = argv[0], argv[1]
extra = json.loads(open(argv[2]).read()) if len(argv) > 2 and os.path.exists(argv[2]) else []
os.makedirs(outdir, exist_ok=True)
scn = bpy.context.scene

lo = mathutils.Vector((1e9,) * 3); hi = -lo
for o in scn.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    for c in o.bound_box:
        v = o.matrix_world @ mathutils.Vector(c)
        for i in range(3):
            lo[i] = min(lo[i], v[i]); hi[i] = max(hi[i], v[i])
# below-grade parts (e.g. a sunken arena bowl) must not move the ground plane / framing:
# the asset's local z = 0 is grade.
lo.z = max(lo.z, 0.0)
ctr = (lo + hi) / 2
size = hi - lo
R = max(size.x, size.y)

for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try:
        scn.render.engine = eng
        break
    except TypeError:
        pass
scn.render.resolution_x, scn.render.resolution_y = 1600, 1000
scn.render.resolution_percentage = 100
scn.render.film_transparent = False
try:
    scn.view_settings.view_transform = "Standard"
    scn.view_settings.look = "None"
except Exception:
    pass
scn.view_settings.exposure = 0.0

world = bpy.data.worlds.new("ReviewWorld")
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs[0].default_value = (0.70, 0.76, 0.85, 1)
bg.inputs[1].default_value = 0.45
scn.world = world

sun_d = bpy.data.lights.new("ReviewSun", "SUN")
sun_d.energy = 2.6
sun_d.angle = math.radians(2.0)
sun = bpy.data.objects.new("ReviewSun", sun_d)
scn.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), 0, math.radians(35))  # light from SSW-ish, high

# ground plane
bpy.ops.mesh.primitive_plane_add(size=R * 4, location=(ctr.x, ctr.y, lo.z - 0.02))
gp = bpy.context.active_object
gm = bpy.data.materials.new("ReviewGround")
gm.use_nodes = True
bs = next(n for n in gm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
bs.inputs["Base Color"].default_value = (0.36, 0.37, 0.35, 1)
bs.inputs["Roughness"].default_value = 0.9
gp.data.materials.append(gm)

cam_d = bpy.data.cameras.new("ReviewCam")
cam = bpy.data.objects.new("ReviewCam", cam_d)
scn.collection.objects.link(cam)
scn.camera = cam
cam_d.clip_end = R * 20


def look_at(obj, target):
    d = mathutils.Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


log = []


def shot(name, loc, target, ortho=None, lens=35, sun_rot=None):
    cam.location = loc
    look_at(cam, target)
    if ortho:
        cam_d.type = "ORTHO"; cam_d.ortho_scale = ortho
    else:
        cam_d.type = "PERSP"; cam_d.lens = lens
    if sun_rot:
        sun.rotation_euler = sun_rot
    fp = os.path.join(outdir, f"{prefix}_{name}.png")
    scn.render.filepath = fp
    bpy.ops.render.render(write_still=True)
    log.append({"name": name, "file": os.path.basename(fp), "camera_loc": list(loc), "target": list(target),
                "type": "ortho" if ortho else "persp", "ortho_scale": ortho, "lens": None if ortho else lens})


D = R * 2.2
zt = lo.z + size.z * 0.4
aspect = 1.6
STD = os.environ.get("RR_ONLY_EXTRA") != "1"
if STD:
    for nm, (dx, dy), srot in [("elev_N", (0, 1), (math.radians(55), 0, math.radians(160))),
                               ("elev_E", (1, 0), (math.radians(55), 0, math.radians(70))),
                               ("elev_S", (0, -1), (math.radians(55), 0, math.radians(-20))),
                               ("elev_W", (-1, 0), (math.radians(55), 0, math.radians(-110)))]:
        width = size.x if dy else size.y
        sc = max(width * 1.08, size.z * aspect * 1.25)
        shot(nm, (ctr.x + dx * D, ctr.y + dy * D, zt), (ctr.x, ctr.y, zt), ortho=sc, sun_rot=srot)
    for nm, ang, srot in [("obl_NE", 45, 160), ("obl_SE", -45, 20), ("obl_SW", -135, -60), ("obl_NW", 135, -160)]:
        a = math.radians(ang)
        dist = R * 0.95
        shot(nm, (ctr.x + math.cos(a) * dist, ctr.y + math.sin(a) * dist, lo.z + R * 0.38),
             (ctr.x, ctr.y, lo.z + size.z * 0.3), lens=30, sun_rot=(math.radians(50), 0, math.radians(srot)))
    shot("top", (ctr.x, ctr.y, hi.z + R), (ctr.x, ctr.y, lo.z), ortho=max(size.x, size.y * 1.6) * 1.06,
         sun_rot=(math.radians(35), 0, math.radians(35)))
for e in extra:
    shot(e["name"], e["loc"], e["look"], lens=e.get("lens", 35), ortho=e.get("ortho"),
         sun_rot=tuple(math.radians(v) for v in e["sun"]) if "sun" in e else None)

asset = bpy.data.filepath
sha = hashlib.sha256(open(asset, "rb").read()).hexdigest()
json.dump({"asset": asset, "asset_sha256": sha, "engine": scn.render.engine, "resolution": [1600, 1000],
           "view_transform": scn.view_settings.view_transform, "world_color": [0.70, 0.76, 0.85], "world_strength": 0.45, "sun_energy": 2.6,
           "bounds": [list(lo), list(hi)], "shots": log},
          open(os.path.join(outdir, f"{prefix}_render_settings.json"), "w"), indent=1)
print("RENDERED", len(log), sha)
