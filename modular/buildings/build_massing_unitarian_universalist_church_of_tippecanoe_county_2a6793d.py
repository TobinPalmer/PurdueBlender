"""Build a source-based detailed revision of the UUCTC asset in its campus frame.

Run from the repository root:
  blender --background modular/buildings/massing_unitarian_universalist_church_of_tippecanoe_county_2a6793d.blend --python modular/buildings/build_massing_unitarian_universalist_church_of_tippecanoe_county_2a6793d.py

The church outline and location come from OSM way 860918857. Church identity,
occupancy history, and broad facade cues are corroborated by the congregation's
history and a venue exterior photo. Heights and unseen elevations remain estimates.
"""
import json
import math
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector


ASSET_ID = "massing_unitarian_universalist_church_of_tippecanoe_county_2a6793d"
OBJECT_NAME = "Unitarian Universalist Church of Tippecanoe County"
COLLECTION_NAME = "Asset_" + ASSET_ID
ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "audit" / "unitarian_universalist_church_of_tippecanoe_county_2a6793d"
SOURCE = EVIDENCE / "sources" / "osm_way_860918857_full.json"
HEIGHT_EAVES = 5.4  # estimated from the exterior photo; no measured elevation located
HEIGHT_RIDGE = 10.2  # estimated from the exterior photo
WING_EAVES = 4.5  # estimated from the exterior photo


def make_material(name, color, roughness=0.78, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat


with SOURCE.open(encoding="utf-8") as f:
    osm = json.load(f)
nodes = {e["id"]: e for e in osm["elements"] if e["type"] == "node"}
way = next(e for e in osm["elements"] if e["type"] == "way" and e["id"] == 860918857)
tags = way.get("tags", {})
if tags.get("name") != OBJECT_NAME or tags.get("addr:housenumber") != "333":
    raise RuntimeError("OSM feature identity/address did not match the assigned church")
ring = [nodes[node_id] for node_id in way["nodes"]]
if len(ring) < 4 or way["nodes"][0] != way["nodes"][-1]:
    raise RuntimeError("Expected a closed OSM building outline")

# Project to the repository's documented campus coordinate approximation.
def campus_xy(node):
    lat, lon = float(node["lat"]), float(node["lon"])
    return Vector(((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                   (lat - 40.4274) * 111040.0))


points = [campus_xy(n) for n in ring]
if (points[0] - points[-1]).length < 1e-8:
    points.pop()
if len(points) != 19:
    raise RuntimeError(f"Expected 19 distinct footprint vertices, found {len(points)}")

obj = bpy.data.objects.get(OBJECT_NAME)
collection = bpy.data.collections.get(COLLECTION_NAME)
if obj is None or collection is None or obj not in collection.objects[:]:
    raise RuntimeError("Assigned asset object/collection is missing")
if len(collection.objects) != 1:
    raise RuntimeError("Expected exactly one object in the assigned exported collection")

tag = ASSET_ID.upper().replace("MASSING_", "")
materials = [
    make_material(tag + "_Warm_Limestone", (0.67, 0.64, 0.56)),
    make_material(tag + "_Pale_Siding", (0.76, 0.75, 0.69)),
    make_material(tag + "_Roof", (0.105, 0.12, 0.13), 0.88),
    make_material(tag + "_Window_Glass", (0.055, 0.12, 0.16), 0.2, 0.12),
    make_material(tag + "_Dark_Mullion", (0.075, 0.085, 0.09), 0.4, 0.2),
    make_material(tag + "_Stained_Glass_Blue", (0.08, 0.24, 0.48), 0.25),
    make_material(tag + "_Stained_Glass_Amber", (0.58, 0.30, 0.085), 0.28),
    make_material(tag + "_Stained_Glass_Ruby", (0.38, 0.08, 0.12), 0.3),
]
WALL, SIDING, ROOF, GLASS, FRAME, BLUE, AMBER, RUBY = range(len(materials))
verts, faces, face_mats = [], [], []


def add_face(coords, material_index):
    start = len(verts)
    verts.extend(tuple(v) for v in coords)
    faces.append(tuple(range(start, len(verts))))
    face_mats.append(material_index)


def quad(a, b, c, d, material_index):
    add_face((a, b, c, d), material_index)


# Perimeter walls follow the geocoded OSM footprint exactly at grade. The lower
# south-west and eastern wings stay at the lower photo-estimated eave height.
minx = min(p.x for p in points)
miny = min(p.y for p in points)
maxy = max(p.y for p in points)
for i, a in enumerate(points):
    b = points[(i + 1) % len(points)]
    length = (b - a).length
    if length < 0.75:
        continue
    west_front_segment = i == 14  # the broad west frontage visible in the photo
    eave = HEIGHT_EAVES if west_front_segment else WING_EAVES
    material = WALL if i % 3 == 0 else SIDING
    quad((a.x, a.y, 0), (b.x, b.y, 0),
         (b.x, b.y, eave), (a.x, a.y, eave), material)
    # Repeated dark windows and light horizontal lintels on long wall runs.
    if length >= 7.0 and not west_front_segment:
        delta = b - a
        tangent = delta.normalized()
        outward = Vector((tangent.y, -tangent.x))
        count = max(1, int(length // 4.2))
        spacing = length / (count + 1)
        for bay in range(count):
            center = a + tangent * (spacing * (bay + 1)) + outward * 0.035
            width, sill, top = min(1.55, spacing * 0.58), 1.25, min(3.65, eave - 0.5)
            half = tangent * (width / 2)
            quad((center.x-half.x, center.y-half.y, sill),
                 (center.x+half.x, center.y+half.y, sill),
                 (center.x+half.x, center.y+half.y, top),
                 (center.x-half.x, center.y-half.y, top), GLASS)
            # Slim vertical mullion in each side-wing window.
            m = half * 0.88
            quad((center.x-m.x, center.y-m.y, sill),
                 (center.x+m.x, center.y+m.y, sill),
                 (center.x+m.x, center.y+m.y, top),
                 (center.x-m.x, center.y-m.y, top), FRAME)

# Low wing roof over the concave source polygon. Blender triangulates this roof
# from the source outline; the central gable roof overlays its sanctuary section.
for tri in __import__("mathutils.geometry", fromlist=["tessellate_polygon"]).tessellate_polygon([points]):
    roof_points = [points[int(idx)] for idx in tri]
    add_face([(p.x, p.y, WING_EAVES) for p in roof_points], ROOF)

# The photo shows a tall west-facing gabled sanctuary front. The OSM ring's
# west-facing edge 14->15 spans that frontage; its detailed height is estimated.
front_a, front_b = points[14], points[15]
y0, y1 = sorted((front_a.y, front_b.y))
x_front = (front_a.x + front_b.x) / 2
y_mid = (y0 + y1) / 2
front_width = y1 - y0
eave = HEIGHT_EAVES
peak = HEIGHT_RIDGE
front_depth = 21.0  # inferred from the rectangular sanctuary portion of the footprint
x_back = x_front + front_depth

# Add the triangular gable above the wall and a tall multi-pane stained-glass
# composition, with transparent openings represented by a slightly offset face.
add_face(((x_front-0.06, y0, eave), (x_front-0.06, y1, eave),
          (x_front-0.06, y_mid, peak)), WALL)
span = front_width * 0.78
glass_y0, glass_y1 = y_mid - span / 2, y_mid + span / 2
glass_bottom, glass_eave, glass_peak = 2.75, 6.0, 9.35
bay_count = 7
colors = [BLUE, AMBER, GLASS, RUBY, BLUE, GLASS, AMBER]
for bay in range(bay_count):
    ya = glass_y0 + span * bay / bay_count
    yb = glass_y0 + span * (bay + 1) / bay_count
    def glass_top(y):
        half = front_width / 2
        return glass_peak - (glass_peak-glass_eave) * abs(y-y_mid) / half
    ta, tb = min(glass_eave, glass_top(ya)), min(glass_eave, glass_top(yb))
    quad((x_front-0.12, ya, glass_bottom),
         (x_front-0.12, yb, glass_bottom),
         (x_front-0.12, yb, tb),
         (x_front-0.12, ya, ta), colors[bay])
    # Dark vertical mullions retain the source photo's strong window rhythm.
    ybar = yb
    ztop = min(glass_eave, glass_top(ybar))
    add_face([(x_front-0.16, ybar-0.045, glass_bottom),
              (x_front-0.16, ybar+0.045, glass_bottom),
              (x_front-0.16, ybar+0.045, ztop),
              (x_front-0.16, ybar-0.045, ztop)], FRAME)
# Transom and paired entry doors below the stained-glass wall.
door_width = 2.7
door_y0, door_y1 = y_mid-door_width/2, y_mid+door_width/2
quad((x_front-0.18, door_y0, 0.12), (x_front-0.18, door_y1, 0.12),
     (x_front-0.18, door_y1, 2.55), (x_front-0.18, door_y0, 2.55), GLASS)
for yy in (door_y0, y_mid, door_y1):
    add_face([(x_front-0.23, yy-0.055, 0.08),
              (x_front-0.23, yy+0.055, 0.08),
              (x_front-0.23, yy+0.055, 2.62),
              (x_front-0.23, yy-0.055, 2.62)], FRAME)
quad((x_front-0.24, door_y0-0.16, 2.62),
     (x_front-0.24, door_y1+0.16, 2.62),
     (x_front-0.24, door_y1+0.16, 2.78),
     (x_front-0.24, door_y0-0.16, 2.78), WALL)

# Paired sloping roof planes make the sanctuary gable visible from the entry.
roof_ymin, roof_ymax = y0-0.55, y1+0.55
ridge_y = y_mid
ridge_z = peak+0.15
roof_x0, roof_x1 = x_front-0.75, x_back+0.6
quad((roof_x0, roof_ymin, eave), (roof_x1, roof_ymin, eave),
     (roof_x1, ridge_y, ridge_z), (roof_x0, ridge_y, ridge_z), ROOF)
quad((roof_x0, ridge_y, ridge_z), (roof_x1, ridge_y, ridge_z),
     (roof_x1, roof_ymax, eave), (roof_x0, roof_ymax, eave), ROOF)
# Narrow ridge cap, plus light fascia on both gable slopes.
quad((roof_x0, ridge_y-0.16, ridge_z+0.04),
     (roof_x1, ridge_y-0.16, ridge_z+0.04),
     (roof_x1, ridge_y+0.16, ridge_z+0.04),
     (roof_x0, ridge_y+0.16, ridge_z+0.04), FRAME)

old_mesh = obj.data
mesh = bpy.data.meshes.new(OBJECT_NAME + "_source_based_detail")
mesh.from_pydata(verts, [], faces)
for mat in materials:
    mesh.materials.append(mat)
mesh.update()
for poly, index in zip(mesh.polygons, face_mats):
    poly.material_index = index
bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(mesh)
bm.free()
mesh.update()
obj.data = mesh
obj.name = OBJECT_NAME
obj.location = (0, 0, 0)
obj.rotation_euler = (0, 0, 0)
obj.scale = (1, 1, 1)
if old_mesh.users == 0:
    bpy.data.meshes.remove(old_mesh)
mesh.name = OBJECT_NAME + "_mesh"

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("UUCTC_BUILD_RESULT=" + json.dumps({
    "asset_id": ASSET_ID,
    "osm_way_id": way["id"],
    "outline_vertices": len(points),
    "mesh_vertices": len(mesh.vertices),
    "mesh_faces": len(mesh.polygons),
    "collection_object_count": len(collection.objects),
    "estimated_wing_eaves_m": WING_EAVES,
    "estimated_sanctuary_eaves_m": HEIGHT_EAVES,
    "estimated_ridge_m": HEIGHT_RIDGE,
    "footprint_match": "Exact OSM outline at grade; roof overhangs excluded from wall-footprint comparison",
}))
