"""Fresh-open QA for the dedicated Chauncey library. Run with Blender -b."""
from pathlib import Path
import bpy, json, math, hashlib
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "audit" / "chauncey" / "fresh_open_validation.json"
GIS = json.loads((ROOT / "audit" / "chauncey" / "sources" / "purdue_fid805.geojson").read_text(encoding="utf-8"))["features"][0]
assert bpy.data.filepath.endswith("massing_chauncey_cooperative_fid805.blend"), bpy.data.filepath
asset_id = "massing_chauncey_cooperative_fid805"
coll_name = "Asset_" + asset_id
coll = bpy.data.collections.get(coll_name)
assert coll is not None
objs = list(coll.objects)
assert len(objs) >= 200, len(objs)
assert not any(o.type == "EMPTY" for o in objs)
assert any(o.name.startswith("Schematic first-floor") for o in objs)
assert any(o.name.startswith("Schematic upper-floor bed") for o in objs)
assert all(o.type == "MESH" for o in objs), {o.type for o in objs}

verts = [o.matrix_world @ Vector(corner) for o in objs for corner in o.bound_box]
bounds = [[min(v[i] for v in verts), max(v[i] for v in verts)] for i in range(3)]

# Verify the modeled structural foundation wall ring against the archived
# official polygon in the same local metric frame.
lat0, lon0 = 40.4274, -86.9137
ll = GIS["geometry"]["coordinates"][0][:-1]
world = [((lon-lon0)*111412.84*math.cos(math.radians(lat0)), (lat-lat0)*111040.0) for lon,lat in ll]
cross = [world[i][0]*world[(i+1)%len(world)][1] - world[(i+1)%len(world)][0]*world[i][1] for i in range(len(world))]
a2 = sum(cross)
cx = sum((world[i][0]+world[(i+1)%len(world)][0])*cross[i] for i in range(len(world)))/(3*a2)
cy = sum((world[i][1]+world[(i+1)%len(world)][1])*cross[i] for i in range(len(world)))/(3*a2)
base = bpy.data.objects.get("Stone foundation on official FID 805 wall ring")
assert base is not None
expected = [(x-cx,y-cy) for x,y in world]
actual = [(v.co.x,v.co.y) for v in base.data.vertices if abs(v.co.z)<1e-6]
max_ring_vertex_error_m = max(min(math.hypot(ax-ex,ay-ey) for ax,ay in actual) for ex,ey in expected)
assert len(actual) == len(expected) and max_ring_vertex_error_m < 0.001, {
    "actual_vertices":len(actual),"expected_vertices":len(expected),"max_vertex_error_m":max_ring_vertex_error_m
}

images = []
external = []
materials = set()
for obj in objs:
    for mat in obj.data.materials:
        if not mat:
            continue
        materials.add(mat.name)
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image:
                    images.append({"material": mat.name, "image": node.image.name, "path": node.image.filepath})
assert not images, images

blend = Path(bpy.data.filepath)
result = {
    "status": "PASS",
    "fresh_open": True,
    "blender_version": bpy.app.version_string,
    "blend_path": str(blend),
    "blend_sha256": hashlib.sha256(blend.read_bytes()).hexdigest(),
    "asset_collection": coll_name,
    "asset_object_count": len(objs),
    "mesh_object_count": sum(o.type == "MESH" for o in objs),
    "unique_material_count": len(materials),
    "material_names": sorted(materials),
    "external_image_dependencies": images,
    "local_collection_bounds_m": [[round(a,3),round(b,3)] for a,b in bounds],
    "official_fid805_foundation_ring_vertex_match": True,
    "foundation_ring_vertex_count": len(actual),
    "foundation_ring_max_vertex_error_m": max_ring_vertex_error_m,
    "origin_campus_xy_m": [round(cx,6),round(cy,6)],
    "schematic_interior_present": True,
    "scene_preview_camera_present": bpy.context.scene.camera is not None,
}
OUT.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
print(json.dumps(result, indent=2))
