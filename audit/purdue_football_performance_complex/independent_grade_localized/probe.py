import bpy
import hashlib
import json
import sys
import math
from pathlib import Path
from mathutils import Vector

ASSET_ID = "massing_purdue_football_performance_complex_f106c29"
COLL = "Asset_" + ASSET_ID
SCENE = "Building_" + ASSET_ID
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
mode = args[0]
out = Path(args[1])
blend = Path(bpy.data.filepath).resolve()
sha = hashlib.sha256(blend.read_bytes()).hexdigest()

def bounds(points):
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)] if points else None

result = {"mode": mode, "blend_path": str(blend), "blend_sha256": sha}
errors = []
if mode == "asset":
    coll = bpy.data.collections.get(COLL)
    scene = bpy.data.scenes.get(SCENE)
    objs = list(coll.all_objects) if coll else []
    geom = [o for o in objs if o.type in {"MESH", "CURVE", "FONT", "SURFACE", "META"}]
    points = [o.matrix_world @ Vector(c) for o in geom for c in o.bound_box]
    external = [bpy.path.abspath(i.filepath) for i in bpy.data.images if i.source == "FILE" and not i.packed_file]
    linked = [o.name for o in objs if o.library]
    result.update({"expected_collection_found": coll is not None, "expected_scene_found": scene is not None,
                   "object_count": len(objs), "geometry_object_count": len(geom),
                   "mesh_count": sum(o.type == "MESH" for o in geom),
                   "materials_used": sorted({m.name for o in geom for m in o.data.materials if m}),
                   "local_geometry_bounds_m": bounds(points), "unpacked_external_images": external,
                   "linked_objects": linked})
    if not coll: errors.append("expected asset collection is missing")
    if not scene: errors.append("expected asset scene is missing")
    if external: errors.append("unpacked external image dependencies exist")
    if linked: errors.append("unexpected linked objects in source asset")
elif mode == "master":
    needle = "Placement_" + ASSET_ID
    markers = [o for o in bpy.data.objects if o.name == needle or o.name.startswith(needle + ".")]
    instancers = [o for o in markers if o.instance_type == "COLLECTION" and o.instance_collection]
    instances = []
    for marker in instancers:
        icoll = marker.instance_collection
        objs = list(icoll.all_objects)
        geom = [o for o in objs if o.type in {"MESH", "CURVE", "FONT", "SURFACE", "META"}]
        points = [marker.matrix_world @ o.matrix_world @ Vector(c) for o in geom for c in o.bound_box]
        instances.append({"marker_name": marker.name, "marker_type": marker.type,
                          "marker_location_world_m": list(marker.matrix_world.translation),
                          "marker_rotation_world_euler": list(marker.matrix_world.to_euler()),
                          "instance_collection": icoll.name, "instance_object_count": len(objs),
                          "instance_geometry_count": len(geom), "world_bounds_m": bounds(points)})
    # Independently compare the evaluated master instance's plinth to source GIS.
    gis_path = Path(blend).parent / "audit" / "purdue_football_performance_complex" / "sources" / "purdue_gis_fpc_fid1202_2026-10-26.geojson"
    evidence_path = Path(blend).parent / "audit" / "purdue_football_performance_complex" / "build_evidence.json"
    gis = json.loads(gis_path.read_text(encoding="utf-8"))
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    feature = next(f for f in gis["features"] if int(f.get("id", f["properties"].get("OBJECTID", -1))) == 1202)
    lat0, lon0 = 40.4274, -86.9137
    origin = evidence["placement_origin_xy_m"]
    ring = feature["geometry"]["coordinates"][0]
    expected = []
    for lon, lat, *_ in ring:
        p = ((lon-lon0)*111412.84*math.cos(math.radians(lat0))-origin[0], (lat-lat0)*111040.0-origin[1])
        if not expected or math.dist(expected[-1], p) > 1e-7:
            expected.append(p)
    if len(expected) > 1 and math.dist(expected[0], expected[-1]) < 1e-7:
        expected.pop()
    gis_probe = {"source_feature_id": feature.get("id", feature["properties"].get("OBJECTID")),
                 "source_vertex_count": len(expected), "placement_origin_xy_m": origin,
                 "master_instance_plinth_found": False, "max_source_vertex_to_master_plinth_distance_m": None}
    if len(instancers) == 1:
        marker = instancers[0]
        plinth = next((o for o in marker.instance_collection.all_objects if o.name == "KFPC | structural ground plinth"), None)
        if plinth:
            model = [(marker.matrix_world @ plinth.matrix_world @ v.co).xy[:] for v in plinth.data.vertices]
            nearest = [min(math.dist(p, q) for q in model) for p in expected]
            gis_probe.update({"master_instance_plinth_found": True,
                              "plinth_vertex_count": len(model),
                              "max_source_vertex_to_master_plinth_distance_m": max(nearest) if nearest else None})
            if not nearest or max(nearest) > 0.01:
                errors.append("master instance plinth does not align with Purdue GIS FID 1202")
        else:
            errors.append("master instance's structural ground plinth is missing")
    result.update({"gis_footprint_alignment": gis_probe})
    result.update({"placement_markers_matching_id": len(markers), "collection_instancers": instances,
                   "master_scene": bpy.context.scene.name})
    if len(markers) != 1: errors.append(f"expected one Placement marker, found {len(markers)}")
    if len(instancers) != 1: errors.append(f"expected one collection instance, found {len(instancers)}")
    if instancers and instancers[0].instance_collection.name != COLL:
        errors.append("placement marker instances unexpected collection " + instancers[0].instance_collection.name)
else:
    raise ValueError("mode must be asset or master")

result["status"] = "PASS" if not errors else "FAIL"
result["errors"] = errors
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result))
