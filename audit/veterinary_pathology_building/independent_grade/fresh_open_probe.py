import bpy, json, hashlib, math, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ASSET = os.path.join(ROOT, "modular", "buildings", "massing_veterinary_pathology_building_48b5a5b.blend")
EVIDENCE = os.path.join(ROOT, "audit", "veterinary_pathology_building", "evidence.json")
GEOJSON = os.path.join(ROOT, "audit", "veterinary_pathology_building", "purdue_campus_building_vpth_raw.geojson")
OUT = os.path.join(ROOT, "audit", "veterinary_pathology_building", "independent_grade", "fresh_open_probe.json")

scene = bpy.data.scenes.get("Building_massing_veterinary_pathology_building_48b5a5b")
collection = bpy.data.collections.get("Asset_massing_veterinary_pathology_building_48b5a5b")
assert scene is not None and collection is not None
objects = list(collection.objects)
assert len(objects) == 1
obj = objects[0]
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = obj.evaluated_get(depsgraph)
world_verts = [evaluated.matrix_world @ v.co for v in evaluated.data.vertices]
bounds = [[min(float(v[i]) for v in world_verts), max(float(v[i]) for v in world_verts)] for i in range(3)]

feature = json.load(open(GEOJSON, encoding="utf-8"))["features"][0]
ring = feature["geometry"]["coordinates"][0]
lat0, lon0 = 40.4274, -86.9137
coslat = math.cos(math.radians(lat0))
gis = [((lon-lon0)*111412.84*coslat, (lat-lat0)*111040.0) for lon,lat in ring]
gis_bounds = [[min(p[i] for p in gis), max(p[i] for p in gis)] for i in range(2)]
bottom = [(float(v.co.x), float(v.co.y)) for v in evaluated.data.vertices if abs(float(v.co.z)) < 1e-5]
hausdorff_gis_to_mesh = max(min(math.hypot(x-u,y-v) for u,v in bottom) for x,y in gis) if bottom else None
hausdorff_mesh_to_gis = max(min(math.hypot(x-u,y-v) for u,v in gis) for x,y in bottom) if bottom else None

mat_stats=[]
for idx,mat in enumerate(evaluated.data.materials):
    used=sum(1 for poly in evaluated.data.polygons if poly.material_index==idx)
    node_types=[]
    if mat and mat.use_nodes and mat.node_tree:
        node_types=[n.type for n in mat.node_tree.nodes]
    mat_stats.append({"slot":idx,"name":mat.name if mat else None,"polygons_using_slot":used,"node_types":node_types})
images=[]
for image in bpy.data.images:
    if image.source == "FILE":
        images.append({"name":image.name,"path":bpy.path.abspath(image.filepath)})
libraries=[bpy.path.abspath(lib.filepath) for lib in bpy.data.libraries if lib.filepath]
report={
 "readback_fresh_process":True,
 "asset_sha256":hashlib.sha256(open(ASSET,"rb").read()).hexdigest(),
 "scene":scene.name,
 "collection":collection.name,
 "collection_object_count":len(objects),
 "object_name":obj.name,
 "stable_asset_id":obj.get("stable_asset_id"),
 "object_type":obj.type,
 "world_bounds_m":bounds,
 "gis_polygon_bounds_xy_m":gis_bounds,
 "gis_to_mesh_bottom_vertex_hausdorff_m":hausdorff_gis_to_mesh,
 "mesh_bottom_vertex_to_gis_ring_hausdorff_m":hausdorff_mesh_to_gis,
 "vertex_count":len(evaluated.data.vertices),
 "polygon_count":len(evaluated.data.polygons),
 "material_slot_count":len(evaluated.data.materials),
 "materials":mat_stats,
 "file_image_dependencies":images,
 "external_libraries":libraries,
 "scene_object_types":{t:sum(1 for o in scene.objects if o.type==t) for t in sorted(set(o.type for o in scene.objects))},
 "GIS_properties":feature["properties"],
}
os.makedirs(os.path.dirname(OUT),exist_ok=True)
json.dump(report,open(OUT,"w",encoding="utf-8"),indent=2)
print(json.dumps(report,indent=2))
