"""Build a responsive Blender master from the current active asset set."""
import bpy, json, math, time, traceback
from pathlib import Path
from mathutils import Quaternion, Vector
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "audit" / "master_open_optimization"
ASSET_LIST = OUT / "active_assets.json"
PROXY_FILE = OUT / "campus_proxy_library.blend"
MASTER_FILE = OUT / "purdue_campus_master_fast.blend"
assets = json.loads(ASSET_LIST.read_text(encoding="utf-8"))
if len(assets) != 838: raise RuntimeError(f"Unexpected active asset count: {len(assets)}")
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = "Purdue Campus | Responsive Overview"
root = scene.collection

def new_group(name):
    coll = bpy.data.collections.new(name)
    root.children.link(coll)
    return coll

detailed_group = new_group("Detailed Buildings")
massing_group = new_group("Campus Massing")
site_group = new_group("Site & Context")
name_to_record = {a["collection"]: a for a in assets}
if len(name_to_record) != len(assets): raise RuntimeError("Duplicate collection names in active asset list")
with bpy.data.libraries.load(str(PROXY_FILE), link=True) as (data_from, data_to):
    available = set(data_from.collections)
    missing = sorted(set(name_to_record) - available)
    if missing: raise RuntimeError("Proxy collections missing: " + ", ".join(missing[:10]))
    data_to.collections = sorted(name_to_record)
linked = {c.name: c for c in data_to.collections if c is not None}
if len(linked) != len(assets): raise RuntimeError(f"Linked {len(linked)} of {len(assets)} expected collections")
placed = {"detailed": 0, "massing": 0, "site": 0}
for name, record in name_to_record.items():
    source = linked[name]
    source["proxy_asset_id"] = record["id"]
    source["proxy_source_kind"] = record["kind"]
    if record["kind"] == "detailed":
        marker = bpy.data.objects.new("Placement_" + record["id"], None)
        marker.empty_display_type = "PLAIN_AXES"
        marker.empty_display_size = 8.0
        marker.instance_type = "COLLECTION"
        marker.instance_collection = source
        marker.location = (float(record["placement_origin_xy_m"][0]), float(record["placement_origin_xy_m"][1]), 0.0)
        marker["asset_id"] = record["id"]
        marker["placement_origin_xy_m"] = list(record["placement_origin_xy_m"])
        detailed_group.objects.link(marker)
        placed["detailed"] += 1
    elif record["kind"] == "massing":
        massing_group.children.link(source)
        placed["massing"] += 1
    elif record["kind"] == "site":
        site_group.children.link(source)
        placed["site"] += 1
    else:
        raise RuntimeError(f"Unknown asset kind {record['kind']} for {record['id']}")
if placed != {"detailed":110,"massing":727,"site":1}: raise RuntimeError(f"Unexpected kind counts: {placed}")
# Derive a wide overview framing from the recorded asset bounds.
lo = [min(a["bounds_world_m"][axis][0] for a in assets if a.get("bounds_world_m")) for axis in range(3)]
hi = [max(a["bounds_world_m"][axis][1] for a in assets if a.get("bounds_world_m")) for axis in range(3)]
center = Vector(((lo[0]+hi[0])/2, (lo[1]+hi[1])/2, max(0.0,(lo[2]+hi[2])/2)))
span = max(hi[0]-lo[0], hi[1]-lo[1])
# Keep the 3D view in solid material color for fast first paint.
view_q = Quaternion((1,0,0), math.radians(35)) @ Quaternion((0,0,1), math.radians(-35))
for workspace in bpy.data.workspaces:
    for screen in [workspace.screens[0]] if hasattr(workspace, "screens") and workspace.screens else []:
        for area in screen.areas:
            if area.type != "VIEW_3D": continue
            space = area.spaces.active
            space.region_3d.view_perspective = "ORTHO"
            space.region_3d.view_location = center
            space.region_3d.view_distance = span * 2.15
            space.region_3d.view_rotation = view_q
            space.shading.type = "SOLID"
            space.shading.color_type = "MATERIAL"
            space.overlay.show_floor = False
# Allow camera rendering when the site proxy contains one.
cameras = [o for o in bpy.data.objects if o.type == "CAMERA"]
if cameras: scene.camera = cameras[0]
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
# Keep the factory scene render engine because Blender 5.2 enum names are build-specific.
scene["source_asset_count"] = len(assets)
scene["proxy_library"] = PROXY_FILE.name
scene["proxy_generation"] = "merged per-asset geometry; editable source files preserved"
bpy.context.view_layer.update()
# Save a path relative to this optimization folder for portable library lookup.
for lib in bpy.data.libraries:
    lib.filepath = "//" + PROXY_FILE.name
bpy.ops.wm.save_as_mainfile(filepath=str(MASTER_FILE))
report = {
    "status":"PASS", "master_file":str(MASTER_FILE), "proxy_library":str(PROXY_FILE),
    "asset_counts":placed, "linked_collections":len(linked), "library_count":len(bpy.data.libraries),
    "scene_object_count":len(bpy.data.objects), "mesh_object_count":sum(o.type=="MESH" for o in bpy.data.objects),
    "mesh_count":len(bpy.data.meshes), "material_count":len(bpy.data.materials),
    "camera_count":len(cameras), "bounds_world_m":{"min":lo,"max":hi}, "view_center":list(center),
}
(OUT / "fast_master_build_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("FAST_MASTER_BUILD_COMPLETE " + json.dumps(report),flush=True)

