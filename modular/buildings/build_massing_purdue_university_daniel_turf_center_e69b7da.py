"""Build the massing library for Purdue's Daniel Turfgrass Center.

Source geometry comes from the named Purdue BuildingShapes feature FID 208.
The source's undocumented Extrution=14 is retained only as a raw GIS attribute,
not used for geometry. A 2011 exterior photograph documents the low elongated
metal building and shallow gable roof. Vertical scale remains an explicitly
low-confidence visual estimate because no measured elevation/height was found.
"""
from pathlib import Path
import json, math
import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ASSET_ID = "massing_purdue_university_daniel_turf_center_e69b7da"
OBJECT_NAME = "Purdue University Daniel Turf Center"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"
ROOT = Path(__file__).resolve().parents[2]
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
EVIDENCE = ROOT / "audit" / ASSET_ID
SOURCE = EVIDENCE / "sources" / "purdue_buildings_fid208_query_2026-10-26.json"

# Match the modular project's explicitly documented approximate local map transform.
LAT0, LON0 = 40.4274, -86.9137
X_METERS_PER_DEGREE = 111412.84 * math.cos(math.radians(LAT0))
Y_METERS_PER_DEGREE = 111040.0
FEET_TO_METERS = 0.3048

with SOURCE.open("r", encoding="utf-8-sig") as f:
    query = json.load(f)
feature = next(f for f in query["features"] if f["attributes"].get("FID") == 208)
attrs = feature["attributes"]
assert attrs.get("BLDG_ABBR") == "DANL"
assert attrs.get("BUILDING_N") == "William H. Daniel Turfgrass Research & Diagnostic Court"
assert attrs.get("ADDRESS") == "1340 Cherry Lane"
ring_lonlat = feature["geometry"]["rings"][0]

ring = []
for lon, lat, *_ in ring_lonlat:
    x = (lon - LON0) * X_METERS_PER_DEGREE
    y = (lat - LAT0) * Y_METERS_PER_DEGREE
    ring.append((x, y))
if ring[0] == ring[-1]:
    ring.pop()
assert len(ring) >= 4

# GIS Extrution is unitless in the retrieved metadata; do not use its raw 14 as
# a height. The exterior photo supports a shallow-gable single-story form but
# has no calibrated scale, so these are explicit low-confidence visual values.
eave_height_m = 3.25
roof_rise_m = 0.80
height_m = eave_height_m + roof_rise_m

# Create a clean, single-asset scene. The facility stays in campus-world
# coordinates because this is a simple massing library.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = SCENE_NAME
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
asset_collection = bpy.data.collections.new(COLLECTION_NAME)
scene.collection.children.link(asset_collection)

source_n = len(ring)
# The native roof-outline polygon has a centered 4.23 m x 2.35 m south bump.
# Its position matches the centered entry canopy in the attributed exterior
# photo. Treat that bump as the porch roof projection and derive the main wall
# outline by bridging its two rear corners; canopy geometry restores the exact
# source outline's outer extents below.
min_y = min(y for x, y in ring)
bump_indices = [i for i, p in enumerate(ring) if p[1] <= min_y + 0.05]
assert len(bump_indices) == 2
west_bump_i, east_bump_i = sorted(bump_indices, key=lambda i: ring[i][0])
wall_ring = [p for i, p in enumerate(ring) if i not in bump_indices]
wall_n = len(wall_ring)
yc = (min(y for x, y in wall_ring) + max(y for x, y in wall_ring)) / 2.0
# Insert boundary points where the gable ridge meets the end walls. Splitting
# these boundary edges makes the roof, walls and bottom a closed shell.
outline = []
for i, a in enumerate(wall_ring):
    b = wall_ring[(i + 1) % wall_n]
    outline.append(a)
    if (a[1] - yc) * (b[1] - yc) < 0.0:
        t = (yc - a[1]) / (b[1] - a[1])
        outline.append((a[0] + t * (b[0] - a[0]), yc))
n = len(outline)
verts = [(x, y, 0.0) for x, y in wall_ring]
outline_bottom_ids = []
for x, y in outline:
    nearest = min(range(wall_n), key=lambda i: math.hypot(wall_ring[i][0]-x, wall_ring[i][1]-y))
    if math.hypot(wall_ring[nearest][0]-x, wall_ring[nearest][1]-y) < 0.05:
        outline_bottom_ids.append(nearest)
    else:
        outline_bottom_ids.append(len(verts))
        verts.append((x, y, 0.0))
window_low_m, window_high_m = 2.30, 2.80
window_low_ids = list(range(len(verts), len(verts) + n))
verts.extend((x, y, window_low_m) for x, y in outline)
window_high_ids = list(range(len(verts), len(verts) + n))
verts.extend((x, y, window_high_m) for x, y in outline)
eave_ids = list(range(len(verts), len(verts) + n))
verts.extend((x, y, height_m if abs(y-yc) < 0.05 else eave_height_m) for x, y in outline)
faces = []
face_material_indices = []
# Split all wall faces at the band heights so the model remains a single
# manifold shell when the photographed south window ribbon is material-coded.
for i in range(n):
    j = (i + 1) % n
    dx, dy = outline[j][0]-outline[i][0], outline[j][1]-outline[i][1]
    long_south_facade = abs(dy) < 0.1 and (outline[i][1]+outline[j][1])/2.0 < yc-1.0 and math.hypot(dx,dy) > 10.0
    faces.append((outline_bottom_ids[i], outline_bottom_ids[j], window_low_ids[j], window_low_ids[i]))
    face_material_indices.append(0)
    faces.append((window_low_ids[i], window_low_ids[j], window_high_ids[j], window_high_ids[i]))
    face_material_indices.append(2 if long_south_facade else 0)
    faces.append((window_high_ids[i], window_high_ids[j], eave_ids[j], eave_ids[i]))
    face_material_indices.append(0)
# Bottom n-gon preserves the concave source ring with added collinear split points.
faces.append(tuple(reversed(outline_bottom_ids)))
face_material_indices.append(0)

# Split the concave GIS ring at its longitudinal centerline. The exterior
# photograph shows a shallow gable; its ridge is parallel to the long axis
# (east-west). Clip each half to the ridge and triangulate it. Original ring
# points and ridge intersections are shared so the shell stays manifold.
ridge_ids = {}
def vertex_for_xy(x, y):
    key = (round(float(x), 5), round(float(y), 5))
    # Blender's tessellator uses float32 coordinates; tolerate its rounding.
    nearest = min(range(n), key=lambda i: math.hypot(outline[i][0]-x, outline[i][1]-y))
    if math.hypot(outline[nearest][0]-x, outline[nearest][1]-y) < 0.05:
        return eave_ids[nearest]
    if key not in ridge_ids:
        ridge_ids[key] = len(verts)
        verts.append((float(x), float(y), height_m))
    return ridge_ids[key]

def clip_to_half(points, keep_lower):
    result = []
    for i, a in enumerate(points):
        b = points[(i + 1) % len(points)]
        ina = a[1] <= yc + 1e-8 if keep_lower else a[1] >= yc - 1e-8
        inb = b[1] <= yc + 1e-8 if keep_lower else b[1] >= yc - 1e-8
        if ina:
            result.append(a)
        if ina != inb:
            t = (yc - a[1]) / (b[1] - a[1])
            result.append((a[0] + t * (b[0] - a[0]), yc))
    clean = []
    for p in result:
        if not clean or math.hypot(p[0]-clean[-1][0], p[1]-clean[-1][1]) > 1e-7:
            clean.append(p)
    if len(clean) > 2 and math.hypot(clean[0][0]-clean[-1][0], clean[0][1]-clean[-1][1]) <= 1e-7:
        clean.pop()
    return clean

for lower in (True, False):
    half = clip_to_half(outline, lower)
    if len(half) >= 3:
        vectors = [Vector((x, y, 0.0)) for x, y in half]
        for tri in tessellate_polygon([vectors]):
            faces.append(tuple(vertex_for_xy(vectors[i].x, vectors[i].y) for i in tri))
            face_material_indices.append(1)

# Centered gable canopy: its rectangular footprint is the exact centered south
# roof-outline bump. Local orientation comes from the north-up aerial: parking
# sits on the south side, where the photo shows the foreground and centered door.
# Use the original ring neighbors that touch the bump: on this polygon they are
# its south-façade corners. Determine west/east by their X coordinate.
back_points = []
for i in bump_indices:
    for j in ((i-1) % source_n, (i+1) % source_n):
        if j not in bump_indices and ring[j] not in back_points:
            back_points.append(ring[j])
assert len(back_points) == 2
back_points = sorted(back_points, key=lambda p: p[0])
west_back = back_points[0]
east_back = back_points[-1]
west_front, east_front = ring[west_bump_i], ring[east_bump_i]
canopy_profiles = []
for t in (0.0, 1.0):
    x_left, x_right = west_front[0], east_front[0]
    y_left = west_back[1] + t * (west_front[1] - west_back[1])
    y_right = east_back[1] + t * (east_front[1] - east_back[1])
    x_mid = (x_left + x_right) / 2.0
    y_mid = (y_left + y_right) / 2.0
    # Closed pentagonal cross-section: two sloping roof faces, fascia, soffit.
    profile = [(x_left,y_left,2.72),(x_mid,y_mid,3.02),(x_right,y_right,2.72),
               (x_right,y_right,2.62),(x_left,y_left,2.62)]
    ids = list(range(len(verts), len(verts)+5))
    verts.extend(profile)
    canopy_profiles.append(ids)
front_profile, back_profile = canopy_profiles[1], canopy_profiles[0]
faces.append(tuple(front_profile)); face_material_indices.append(0)
faces.append(tuple(reversed(back_profile))); face_material_indices.append(0)
for k in range(5):
    j = (k + 1) % 5
    faces.append((back_profile[k], back_profile[j], front_profile[j], front_profile[k]))
    face_material_indices.append(1 if k in (0, 1) else 0)
mesh = bpy.data.meshes.new(f"{OBJECT_NAME} | FID 208 footprint extrusion")
mesh.from_pydata(verts, [], faces)
mesh.validate(verbose=True, clean_customdata=True)
mesh.update(calc_edges=True)
obj = bpy.data.objects.new(OBJECT_NAME, mesh)
asset_collection.objects.link(obj)

# Correct normals for a closed shell.
import bmesh
bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh)
bm.free()
mesh.update()

wall = bpy.data.materials.new("Daniel Center | pale metal siding massing")
wall.diffuse_color = (0.52, 0.49, 0.43, 1.0)
wall.use_nodes = True
wall.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.52, 0.49, 0.43, 1.0)
wall.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value = 0.85
roof = bpy.data.materials.new("Daniel Center | light metal roof massing")
roof.diffuse_color = (0.70, 0.69, 0.63, 1.0)
roof.use_nodes = True
roof.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.70, 0.69, 0.63, 1.0)
roof.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value = 0.7
glass = bpy.data.materials.new("Daniel Center | dark horizontal window band")
glass.diffuse_color = (0.12, 0.20, 0.22, 1.0)
glass.use_nodes = True
glass.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.12, 0.20, 0.22, 1.0)
glass.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value = 0.24
obj.data.materials.append(wall)
obj.data.materials.append(roof)
obj.data.materials.append(glass)
for i, p in enumerate(mesh.polygons):
    p.material_index = face_material_indices[i]

obj["asset_id"] = ASSET_ID
obj["source_feature"] = "Purdue BuildingShapesZip4 FeatureServer/0, FID 208"
obj["source_name"] = attrs["BUILDING_N"]
obj["source_abbreviation"] = attrs["BLDG_ABBR"]
obj["source_address"] = attrs["ADDRESS"]
obj["source_story_count"] = int(attrs["NUM_LEVELS"])
obj["raw_gis_extrution_uninterpreted"] = attrs["Extrution"]
obj["gis_extrution_used_for_height"] = False
obj["visual_eave_height_estimate_m_low_confidence"] = eave_height_m
obj["visual_ridge_height_estimate_m_low_confidence"] = height_m
obj["height_basis"] = "Low-confidence visual scale only; 2011 exterior photo has no calibrated dimensions. GIS Extrution=14 not interpreted."
obj["roof_basis"] = "Shallow gable supported by 2011 Daniel Center exterior photograph; ridge axis inferred from elongated footprint."
obj["footprint_basis"] = "Exact FID 208 plan projection retained as main roof plus the centered canopy over its south-side projection bump; wall overhang offset is not surveyed."
obj["photo_facade_orientation"] = "South-facing long elevation (negative Y)"
obj["photo_to_facade_mapping"] = "North-up aerial shows the parking apron on the south side; the centered 4.23 m x 2.35 m south roof-outline bump aligns with the centered canopy in the photo. The long photographed elevation maps to the GIS long axis (X)."
obj["facade_detail_method"] = "Light metal siding material; dark window band at Z 2.30-2.80 m on two long south-wall sections; closed shallow gable canopy over the exact central GIS projection bump."
obj["facade_detail_uncertainty"] = "Photo has perspective and no dimensions; face orientation is inferred from parking apron and matching centered plan bump. Band height/width and canopy vertical dimensions are visual-only estimates, not measured."
obj["position_basis"] = "Campus-world coordinates retained for massing library"

# Preview helper objects are temporary: they are removed before the asset is saved.
preview_collection = bpy.data.collections.new("__preview_helpers__")
scene.collection.children.link(preview_collection)
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1200
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"
scene.world = bpy.data.worlds.new("Preview world")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.78, 0.82, 0.86, 1.0)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.55

cx = (min(x for x, y in ring) + max(x for x, y in ring)) / 2.0
cy = (min(y for x, y in ring) + max(y for x, y in ring)) / 2.0
span = max(max(x for x, y in ring) - min(x for x, y in ring), max(y for x, y in ring) - min(y for x, y in ring))

def link_helper(obj_helper):
    for c in list(obj_helper.users_collection):
        c.objects.unlink(obj_helper)
    preview_collection.objects.link(obj_helper)
    return obj_helper

def point_camera(cam, target):
    direction = Vector(target) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

def render_view(name, camera_location, ortho_scale):
    data = bpy.data.cameras.new(f"{name} camera")
    cam = bpy.data.objects.new(f"{name} camera", data)
    link_helper(cam)
    cam.location = camera_location
    point_camera(cam, (cx, cy, height_m * 0.25))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ortho_scale
    scene.camera = cam
    light_data = bpy.data.lights.new(f"{name} key", "AREA")
    light = bpy.data.objects.new(f"{name} key", light_data)
    link_helper(light)
    light.location = (cx - span * 0.3, cy - span * 0.4, height_m + span * 0.9)
    light_data.energy = 9000
    light_data.shape = "DISK"
    light_data.size = span * 0.7
    scene.render.filepath = str(EVIDENCE / "renders" / f"{name}.png")
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.data.objects.remove(light, do_unlink=True)
    bpy.data.cameras.remove(data)
    bpy.data.lights.remove(light_data)

render_view("daniel_turf_center_top", (cx, cy, height_m + span * 1.35), span * 1.28)
render_view("daniel_turf_center_oblique", (cx - span * 0.95, cy - span * 0.9, height_m + span * 1.0), span * 1.38)

bpy.data.collections.remove(preview_collection)
scene.camera = None
# Keep exactly one building object in the single exported collection and clear
# external paths. Save the project asset to its manifest-stable path.
for image in bpy.data.images:
    if image.source == "FILE":
        image.pack()
ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))

# A structured build record is building-specific evidence.
coords = [(x, y, z) for x, y, z in verts]
bounds = [[min(p[i] for p in coords), max(p[i] for p in coords)] for i in range(3)]
area = abs(sum(ring[i][0] * ring[(i + 1) % source_n][1] - ring[(i + 1) % source_n][0] * ring[i][1] for i in range(source_n)) / 2.0)
record = {
    "asset_id": ASSET_ID,
    "building": OBJECT_NAME,
    "build_script": str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"),
    "asset_path": str(ASSET_PATH.relative_to(ROOT)).replace("\\", "/"),
    "source": {
        "provider": "Purdue University GIS BuildingShapesZip4 FeatureServer/0",
        "url": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0",
        "feature_id": "FID 208 / DANL",
        "retrieved": "2026-10-26",
        "source_crs": "Saved identity query is EPSG:4326; native service geometry was also captured in Web Mercator (EPSG:3857)",
        "measurement_method": "Plan coordinates transformed with the modular project's documented local degrees-to-meters approximation. Native EPSG:3857 ring shoelace area independently reconciles with Shape__Area; local ground-scale area differs because Web Mercator area includes latitude distortion.",
        "identity_evidence": "GIS feature name William H. Daniel Turfgrass Research & Diagnostic Court, abbreviation DANL, address 1340 Cherry Lane; outline overlays the long building roof in Esri World Imagery. A 2011 turf-industry visit account explicitly labels its attached exterior photo as the Daniel Center building.",
        "source_conflicts": [
            "The stale assignment_queue screening links FID 855, which the campus index identifies as the Old Purdue Exponent Building; this candidate was rejected. Named Purdue GIS FID 208 at 1340 Cherry Lane is used instead.",
            "Turf Recreation Exercise Center (TREC) is a separate RecWell facility; this model uses the outdoor-research Daniel Center's DANL/FID 208 identity and footprint.",
            "Native EPSG:3857 ring shoelace area=1170.6289 m2 matches Shape__Area=1170.6211 m2 within 0.0078 m2. The earlier apparent mismatch compared distorted Web Mercator area with a latitude-corrected local ground projection.",
            "The ring appears to follow the roof projection in aerial imagery; a surveyed wall line/overhang offset was not located, so the model records that limitation rather than treating it as a measured wall boundary.",
            "GIS Extrution=14 has undocumented units and is not used as a height. Vertical scale is a low-confidence visual estimate because no measured elevation or height source was found.",
            "The Purdue expansion flyer and Synthesis feasibility renderings describe proposed changes and were excluded as evidence of as-built form.",
            "The attributed 2011 exterior photo supports pale metal cladding, a long window band, and a centered canopy. The long facade is assigned to the south side by matching the photo's central entrance to the centered south GIS roof-outline bump and the parking apron in the north-up aerial; the photograph has no compass heading, so this orientation remains an inference."
        ],
        "uncertainty": "GIS footprint is roof-projection-like in the orthophoto; surveyed wall line and eave overhang are unavailable. Exterior photo directly supports pale metal siding, a long window band, centered entrance canopy, and shallow gable, but supplies no dimensions or compass heading. South-facing facade mapping is inferred by matching the centered photo entrance/canopy to the centered south GIS projection bump and the parking apron in the north-up aerial. Window band position and canopy Z dimensions are visual estimates; exact roof pitch and eave/ridge heights remain unmeasured, low-confidence visual estimates."
    },
    "gis": {
        "abbreviation": attrs["BLDG_ABBR"],
        "official_name": attrs["BUILDING_N"],
        "address": attrs["ADDRESS"],
        "num_levels": attrs["NUM_LEVELS"],
        "extrution_raw_uninterpreted": attrs["Extrution"],
        "visual_eave_height_estimate_m_low_confidence": eave_height_m,
        "visual_ridge_height_estimate_m_low_confidence": height_m,
        "ring_vertex_count_closed": len(ring_lonlat),
        "unique_ring_vertex_count": source_n,
        "footprint_boundary_vertex_count_after_gable_end_splits": n,
        "approx_local_polygon_area_m2": area,
        "native_epsg3857_ring_area_m2": 1170.62890625,
        "shape_area_service_m2": attrs["Shape__Area"],
        "native_area_attribute_delta_m2": 0.0078125,
        "campus_world_bounds_m": bounds,
        "transform": "X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040; Z up"
    },
    "model": {
        "kind": "simple massing",
        "objects_in_export_collection": len(asset_collection.objects),
        "vertices": len(mesh.vertices),
        "faces": len(mesh.polygons),
        "footprint": "Exact FID 208 plan extent retained in campus-world coordinates; main wall outline bridges the centered south projection bump and centered canopy restores its exact outer plan extent",
        "roof": "Shallow gable supported by a Daniel Center exterior photo; pitch and absolute vertical scale unmeasured",
        "modifiers": [],
        "external_dependencies": [],
        "preview_renders": ["renders/daniel_turf_center_top.png", "renders/daniel_turf_center_oblique.png"]
    },
    "validation": "Generated build record; clean-process reopen validation is recorded separately in reopen_validation.json."
}
with (EVIDENCE / "build_result.json").open("w", encoding="utf-8") as f:
    json.dump(record, f, indent=2)
    f.write("\n")
print(json.dumps({"asset": str(ASSET_PATH), "bounds": bounds, "vertices": len(mesh.vertices), "faces": len(mesh.polygons), "area_m2": area}, indent=2))
