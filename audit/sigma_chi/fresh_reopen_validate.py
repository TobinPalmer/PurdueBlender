"""Fresh-process Blender 5.2.3 reopen and GIS footprint validation."""
import bpy
import bmesh
import hashlib
import json
import math
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSET = os.path.join(ROOT, "modular", "buildings", "massing_sigma_chi_fid828.blend")
SOURCE = os.path.join(ROOT, "audit", "sigma_chi", "sources", "purdue_gis_fid828_raw.json")
OUT_JSON = os.path.join(ROOT, "audit", "sigma_chi", "fresh_reopen_validation.json")
OUT_RENDER = os.path.join(ROOT, "audit", "sigma_chi", "sigma_chi_fresh_reopen_render.png")
OUT_PLAN_RENDER = os.path.join(ROOT, "audit", "sigma_chi", "sigma_chi_roof_plan.png")
OUT_OBLIQUE_RENDER = os.path.join(ROOT, "audit", "sigma_chi", "sigma_chi_front_oblique.png")
COLL = "Asset_massing_sigma_chi_fid828"
SCENE = "Building_massing_sigma_chi_fid828"
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
XF = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
YF = 111040.0

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def bounds(collection):
    pts = []
    for obj in collection.objects:
        if obj.type != "MESH":
            continue
        pts.extend([obj.matrix_world @ __import__("mathutils").Vector(corner)
                    for corner in obj.bound_box])
    return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]

bpy.ops.wm.open_mainfile(filepath=ASSET)
assert SCENE in bpy.data.scenes, "expected named building scene"
scene = bpy.data.scenes[SCENE]
assert COLL in bpy.data.collections, "expected exported asset collection"
collection = bpy.data.collections[COLL]
objects = list(collection.objects)
assert len(objects) >= 250, "expected detailed facade/roof asset: %s objects" % len(objects)
assert all(o.type == "MESH" for o in objects), "non-mesh helper leaked into asset collection"
wall = bpy.data.objects.get("SigmaChi_GIS_Footprint_Walls")
assert wall and wall.name in collection.objects, "GIS footprint wall mesh missing from asset"

with open(SOURCE, "r", encoding="utf-8") as f:
    raw = json.load(f)
feature = raw["features"][0]
assert feature["attributes"]["FID"] == 828
source_ring = feature["geometry"]["rings"][0][:-1]
expected = [((lon-ORIGIN_LON)*XF, (lat-ORIGIN_LAT)*YF) for lon,lat in source_ring]
actual = [(wall.data.vertices[i].co.x, wall.data.vertices[i].co.y)
          for i in range(len(expected))]
footprint_max_error = max(math.dist(a,b) for a,b in zip(expected,actual))
assert footprint_max_error < 0.001, "footprint differs from transformed GIS ring"

nonmanifold = 0
loose_edges = 0
for obj in objects:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    nonmanifold += sum(not edge.is_manifold for edge in bm.edges)
    loose_edges += sum(edge.is_wire for edge in bm.edges)
    bm.free()
bounds_world = bounds(collection)
scene.render.filepath = OUT_RENDER
bpy.ops.render.render(write_still=True, scene=SCENE)

# A three-quarter view keeps the chapter-photo frontage and intersecting roof
# wings visible together, supplementing the direct facade and plan views.
theta = math.radians(64.6951488989826)
u = (math.cos(theta), math.sin(theta))
v = (-math.sin(theta), math.cos(theta))
edge_candidates = []
for i, a in enumerate(expected):
    b = expected[(i+1) % len(expected)]
    va, vb = a[0]*v[0]+a[1]*v[1], b[0]*v[0]+b[1]*v[1]
    length = math.dist(a,b)
    if abs(va-vb) < 0.8 and length > 18:
        edge_candidates.append((length,a,b))
_, front_a, front_b = max(edge_candidates)
front_mid = ((front_a[0]+front_b[0])/2,(front_a[1]+front_b[1])/2)
tx,ty = front_b[0]-front_a[0],front_b[1]-front_a[1]
tlen=math.hypot(tx,ty); tx,ty=tx/tlen,ty/tlen
nx,ny=ty,-tx
center_x=sum(x for x,y in expected)/len(expected)
center_y=sum(y for x,y in expected)/len(expected)
if (center_x-front_mid[0])*nx+(center_y-front_mid[1])*ny > 0:
    nx,ny=-nx,-ny
bpy.ops.object.camera_add(location=(front_mid[0]+nx*55+tx*30,
                                   front_mid[1]+ny*55+ty*30,27))
oblique_camera=bpy.context.object
oblique_camera.name="SigmaChi_AuditFrontObliqueCamera"
oblique_camera.data.type="ORTHO"
oblique_camera.data.ortho_scale=60
oblique_camera.rotation_euler=(__import__("mathutils").Vector((center_x,center_y,5.5))-
                               oblique_camera.location).to_track_quat("-Z","Y").to_euler()
scene.camera=oblique_camera
scene.render.filepath=OUT_OBLIQUE_RENDER
bpy.ops.render.render(write_still=True, scene=SCENE)

# Second render from above makes the source's L-shaped plan and roof notch
# inspectable; the temporary camera remains outside the exported asset.
center_xy = (sum(x for x,y in expected)/len(expected), sum(y for x,y in expected)/len(expected))
bpy.ops.object.camera_add(location=(center_xy[0], center_xy[1], 70.0))
plan_camera = bpy.context.object
plan_camera.name = "SigmaChi_AuditPlanCamera"
plan_camera.data.type = "ORTHO"
plan_camera.data.ortho_scale = 52
scene.camera = plan_camera
scene.render.resolution_x = 1000
scene.render.resolution_y = 850
scene.render.filepath = OUT_PLAN_RENDER
bpy.ops.render.render(write_still=True, scene=SCENE)

report = {
    "blender_version": bpy.app.version_string,
    "asset_path": os.path.relpath(ASSET, ROOT).replace(os.sep, "/"),
    "asset_sha256": sha(ASSET),
    "source_sha256": sha(SOURCE),
    "scene": SCENE,
    "collection": COLL,
    "object_count": len(objects),
    "mesh_object_count": sum(o.type == "MESH" for o in objects),
    "nonmanifold_mesh_edges": nonmanifold,
    "loose_mesh_edges": loose_edges,
    "bounds_world_m": bounds_world,
    "gis_footprint_vertex_count": len(expected),
    "gis_footprint_max_xy_error_m": footprint_max_error,
    "fresh_reopen_render": os.path.relpath(OUT_RENDER, ROOT).replace(os.sep, "/"),
    "front_oblique_render": os.path.relpath(OUT_OBLIQUE_RENDER, ROOT).replace(os.sep, "/"),
    "top_down_roof_plan_render": os.path.relpath(OUT_PLAN_RENDER, ROOT).replace(os.sep, "/"),
    "result": "PASS" if nonmanifold == 0 else "PASS_WITH_NONMANIFOLD_EDGE_FINDINGS"
}
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
    f.write("\n")
print("SIGMA_CHI_REOPEN", json.dumps(report, sort_keys=True))
