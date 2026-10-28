import bpy, sys, json, math, os, hashlib, mathutils
argv = sys.argv[sys.argv.index("--")+1:]
outdir, camsf = argv[0], argv[1]
cams = json.load(open(camsf))
os.makedirs(outdir, exist_ok=True)
scn = bpy.context.scene
for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try:
        scn.render.engine = eng; break
    except TypeError: pass
scn.render.resolution_percentage = 100
scn.view_settings.view_transform = "Standard"; scn.view_settings.look = "None"; scn.view_settings.exposure = 0
world = bpy.data.worlds.new("RvWorld"); world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs[0].default_value = (0.70, 0.76, 0.85, 1); bg.inputs[1].default_value = 0.45
scn.world = world
sd = bpy.data.lights.new("RvSun", "SUN"); sd.energy = 2.6; sd.angle = math.radians(2)
sun = bpy.data.objects.new("RvSun", sd); scn.collection.objects.link(sun)
bpy.ops.mesh.primitive_plane_add(size=1200, location=(0, 0, -0.02))
gp = bpy.context.active_object
gm = bpy.data.materials.new("RvGround"); gm.use_nodes = True
b = next(n for n in gm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
b.inputs["Base Color"].default_value = (0.36, 0.37, 0.35, 1); b.inputs["Roughness"].default_value = 0.9
gp.data.materials.append(gm)
cd = bpy.data.cameras.new("RvCam"); cam = bpy.data.objects.new("RvCam", cd)
scn.collection.objects.link(cam); scn.camera = cam; cd.clip_end = 3000; cd.sensor_fit = "AUTO"
log = []
for c in cams:
    cam.location = c["loc"]
    d = mathutils.Vector(c["look"]) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    if c.get("ortho"):
        cd.type = "ORTHO"; cd.ortho_scale = c["ortho"]
    else:
        cd.type = "PERSP"; cd.lens = c.get("lens", 35)
    sun.rotation_euler = tuple(math.radians(v) for v in c.get("sun", [50, 0, 35]))
    scn.render.resolution_x, scn.render.resolution_y = c.get("res", [1600, 1000])
    fp = os.path.join(outdir, c["name"] + ".png"); scn.render.filepath = fp
    bpy.ops.render.render(write_still=True)
    log.append(c)
sha = hashlib.sha256(open(bpy.data.filepath, "rb").read()).hexdigest()
json.dump({"asset": bpy.data.filepath, "asset_sha256": sha, "engine": scn.render.engine, "view_transform": "Standard",
           "world": [0.7, 0.76, 0.85, 0.45], "sun_energy": 2.6, "saved": False, "cameras": log},
          open(os.path.join(outdir, "reviewer_render_settings.json"), "w"), indent=1)
print("RENDERED", len(log), sha)
