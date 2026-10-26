"""Independent Blender probe for the ABE grade; read-only against the model."""
from pathlib import Path
import json, math
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSET = ROOT / "modular/buildings/agricultural_and_biological_engineering_abe.blend"
EVIDENCE = ROOT / "audit/abe/evidence"
GIS = EVIDENCE / "purdue_abe_gis_feature_406.json"
MANIFEST = ROOT / "modular/manifest.json"
OUT = HERE / "blender_probe.json"
ID = "agricultural_and_biological_engineering_abe"
COLLECTION = "Asset_" + ID

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
root = bpy.data.collections.get(COLLECTION)
assert root is not None
assert bpy.data.scenes.get("Scene") is not None
objs = list(root.all_objects)
shell = next(o for o in objs if o.type == "MESH" and o.get("source_geometry") == "Purdue GIS feature 406 outer ring")
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
entry = next(x for x in manifest["assets"] if x["id"] == ID)
gis = json.loads(GIS.read_text(encoding="utf-8"))
ring = max(gis["feature"]["geometry"]["rings"], key=len)
scale_x = 111412.84 * math.cos(math.radians(40.4274))
scale_y = 111040.0
origin = entry["placement_origin_xy_m"]
src = [((lon + 86.9137) * scale_x, (lat - 40.4274) * scale_y) for lon, lat in ring[:-1]]
expected_local = [(x-origin[0], y-origin[1]) for x,y in src]
depsgraph = bpy.context.evaluated_depsgraph_get()
mesh = shell.evaluated_get(depsgraph).to_mesh()
actual = [(shell.matrix_world @ v.co).to_tuple() for v in mesh.vertices]
shell.evaluated_get(depsgraph).to_mesh_clear()

def bounds(points):
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
def area_centroid(points):
    area2 = 0.0; cx = cy = 0.0
    for a,b in zip(points, points[1:]+points[:1]):
        cross = a[0]*b[1]-b[0]*a[1]
        area2 += cross; cx += (a[0]+b[0])*cross; cy += (a[1]+b[1])*cross
    return [cx/(3*area2), cy/(3*area2)]
def point_segment_distance(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    den=dx*dx+dy*dy
    t=0.0 if den==0 else max(0.0,min(1.0,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
    return math.hypot(p[0]-(a[0]+t*dx),p[1]-(a[1]+t*dy))
def directed_hausdorff(points, polygon):
    return max(min(point_segment_distance(p,a,b) for a,b in zip(polygon,polygon[1:]+polygon[:1])) for p in points)

actual2=[(p[0],p[1]) for p in actual]
source_world=[(x,y) for x,y in src]
source_local=[(x,y) for x,y in expected_local]
actual_centroid=area_centroid(actual2)
source_world_centroid=area_centroid(source_world)
source_local_centroid=area_centroid(source_local)
imgs=[]
for im in bpy.data.images:
    if im.source == "FILE" and im.filepath and not im.packed_file:
        imgs.append(im.filepath)
external_libs=[lib.filepath for lib in bpy.data.libraries if lib.filepath]
result={
  "asset_path": str(ASSET.relative_to(ROOT)), "scene": bpy.context.scene.name,
  "collection": root.name, "building_id": root.get("building_id"),
  "source_feature_id": root.get("source_feature_id"),
  "collection_object_count": len(objs), "mesh_object_count": sum(o.type=="MESH" for o in objs),
  "shell_name": shell.name, "shell_bounds_asset_coordinates_m": bounds(actual),
  "source_bounds_project_coordinates_m": [[min(p[i] for p in src),max(p[i] for p in src)] for i in range(2)],
  "source_ring_vertex_count": len(src), "shell_vertex_count": len(actual),
  "shell_to_source_directed_hausdorff_m": directed_hausdorff(actual2, source_world),
  "source_to_shell_directed_hausdorff_m": directed_hausdorff(source_world, actual2),
  "source_centroid_project_xy_m": source_world_centroid,
  "source_centroid_expected_local_xy_m": source_local_centroid,
  "shell_centroid_asset_xy_m": actual_centroid,
  "shell_centroid_error_if_local_m": math.dist(actual_centroid,source_local_centroid),
  "shell_centroid_error_if_project_coordinates_m": math.dist(actual_centroid,source_world_centroid),
  "manifest_placement_origin_xy_m": origin,
  "unpacked_file_images": imgs, "linked_library_paths": external_libs,
  "collection_metadata": {k:(list(root.get(k)) if k=="placement_origin_xy_m" else root.get(k)) for k in ["footprint_status","vertical_status","facade_status","placement_origin_xy_m","model_units"]},
  "manifest_entry_object_count": entry.get("object_count"),
  "manifest_collection_matches": entry.get("collection")==COLLECTION,
}
OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result))
