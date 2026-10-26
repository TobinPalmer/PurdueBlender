"""Read-only match between Grissom's saved shell and Purdue FID 236."""
import json, math
import bpy

obj = bpy.data.objects.get("Grissom Hall")
if obj is None:
    obj = bpy.data.objects["Grissom Hall | source footprint shell"]
mesh = obj.data
shell = []
for v in mesh.vertices:
    if abs(v.co.z) < 1e-4:
        xy = (float(v.co.x), float(v.co.y))
        if not any(math.dist(xy, q) < 1e-5 for q in shell):
            shell.append(xy)

with open("audit/massing_grissom_hall_01fd0e0/sources/official_feature_236.json", encoding="utf-8") as f:
    feature = json.load(f)["features"][0]
attrs = feature["attributes"]
assert attrs["FID"] == 236 and attrs["BLDG_ABBR"] == "GRIS"
ring = feature["geometry"]["rings"][0]
source = []
for lon, lat in ring:
    xy = ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
          (lat - 40.4274) * 111040.0)
    if not any(math.dist(xy, q) < 1e-5 for q in source):
        source.append(xy)

def directed_distances(a, b):
    return [min(math.dist(p, q) for q in b) for p in a]

d1 = directed_distances(shell, source)
d2 = directed_distances(source, shell)
result = {
    "building": attrs["BUILDING_N"], "source_feature_id": attrs["FID"],
    "shell_vertex_count": len(shell), "source_vertex_count": len(source),
    "shell_to_source_vertex_max_m": max(d1),
    "shell_to_source_vertex_mean_m": sum(d1)/len(d1),
    "source_to_shell_vertex_max_m": max(d2),
    "source_to_shell_vertex_mean_m": sum(d2)/len(d2),
    "shell_bounds_local_m": [[min(p[i] for p in shell), max(p[i] for p in shell)] for i in (0,1)],
    "source_bounds_local_m": [[min(p[i] for p in source), max(p[i] for p in source)] for i in (0,1)],
    "gis_vertical_attributes_raw": {k: attrs.get(k) for k in (
        "NUM_LEVELS", "CountOfFLO", "Elevation", "Extrution", "F01", "F02", "F03", "F04", "F05", "R")},
}
print("GRISSOM_OFFICIAL_GIS_MATCH", json.dumps(result, indent=2))
