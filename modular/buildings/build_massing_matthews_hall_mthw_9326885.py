"""Build the assigned Matthews Hall library from Purdue GIS feature 235 and official facade evidence.
Run from the repository root:
  blender --background modular/buildings/massing_matthews_hall_mthw_9326885.blend --python modular/buildings/build_massing_matthews_hall_mthw_9326885.py
The source footprint is retained in the documented campus coordinate frame because the
manifest still identifies this asset as a massing library.
"""
import json
import math
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ASSET_ID = "massing_matthews_hall_mthw_9326885"
OBJECT_NAME = "Matthews Hall (MTHW)"
COLLECTION_NAME = "Asset_" + ASSET_ID
ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "matthews_hall_mthw_9326885"
SOURCE = AUDIT / "sources" / "feature_235_wgs84.json"
# Purdue's current BEP describes a 3-story building. This is a visual proportion
# estimate, not a surveyed or measured elevation; the GIS level-count field differs.
STORIES = 3
STORY_HEIGHT = 3.8
WALL_HEIGHT = STORIES * STORY_HEIGHT
ROOF_HEIGHT = WALL_HEIGHT + 0.55


def material(name, color, roughness=0.78, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF") if mat.node_tree else None
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat


with SOURCE.open(encoding="utf-8") as handle:
    source = json.load(handle)
feature = next(f for f in source["features"] if int(f["id"]) == 235)
attrs = feature["properties"]
if attrs.get("BLDG_ABBR") != "MTHW" or attrs.get("BUILDING_N") != "Matthews Hall":
    raise RuntimeError("GIS feature 235 does not identify Matthews Hall MTHW")
ring = feature["geometry"]["coordinates"][0]
if ring[0] == ring[-1]:
    ring = ring[:-1]
if len(ring) != 14:
    raise RuntimeError(f"Expected 14 distinct GIS footprint vertices, found {len(ring)}")

# The ArcGIS query snapshot is EPSG:4326. Convert it to the project's documented
# approximate campus meters, not a surveyed CRS.
def campus_point(lonlat):
    lon, lat = map(float, lonlat)
    return Vector(((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                   (lat - 40.4274) * 111040.0, 0.0))

points = [campus_point(p) for p in ring]
area2 = sum(points[i].x * points[(i+1) % len(points)].y -
            points[(i+1) % len(points)].x * points[i].y for i in range(len(points)))
orientation_sign = 1.0 if area2 > 0 else -1.0
min_x = min(p.x for p in points)
max_x = max(p.x for p in points)
min_y = min(p.y for p in points)
max_y = max(p.y for p in points)

obj = bpy.data.objects.get(OBJECT_NAME)
collection = bpy.data.collections.get(COLLECTION_NAME)
if obj is None or obj.type != "MESH" or collection is None or obj not in collection.objects[:]:
    raise RuntimeError("Assigned asset object or exported collection is missing")
if len(collection.objects) != 1:
    raise RuntimeError("Expected exactly one object in the assigned exported collection")

prefix = "MTHW"
BRICK = 0
LIMESTONE = 1
GLASS = 2
DARK_METAL = 3
ROOF = 4
PAVING = 5
materials = [
    material(prefix + "_Red_Brick", (0.48, 0.13, 0.065), 0.91),
    material(prefix + "_Pale_Limestone", (0.70, 0.65, 0.54), 0.8),
    material(prefix + "_Window_Glass", (0.035, 0.09, 0.12), 0.24, 0.12),
    material(prefix + "_Dark_Metal", (0.075, 0.07, 0.06), 0.48, 0.25),
    material(prefix + "_Roof_Membrane", (0.17, 0.17, 0.15), 0.94),
    material(prefix + "_Entry_Steps", (0.54, 0.50, 0.43), 0.88),
]
verts, faces, face_mats = [], [], []


def face(coords, mat):
    base = len(verts)
    verts.extend(tuple(float(x) for x in p) for p in coords)
    faces.append(tuple(range(base, len(verts))))
    face_mats.append(mat)


def quad(a, b, c, d, mat):
    face((a, b, c, d), mat)


def wall_box(center, tangent, normal, width, depth, height, mat):
    """Create a closed rectangular architectural element in a wall's local frame."""
    c = Vector(center)
    t = Vector((tangent.x, tangent.y, 0.0)).normalized()
    n = Vector((normal.x, normal.y, 0.0)).normalized()
    z = Vector((0.0, 0.0, 1.0))
    hw, hd, hh = width / 2, depth / 2, height / 2
    offsets = [(-hw,-hd,-hh), (hw,-hd,-hh), (hw,hd,-hh), (-hw,hd,-hh),
               (-hw,-hd,hh), (hw,-hd,hh), (hw,hd,hh), (-hw,hd,hh)]
    base = len(verts)
    verts.extend(tuple(c + t*x + n*y + z*h) for x,y,h in offsets)
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
        faces.append(tuple(base + k for k in f))
        face_mats.append(mat)


def edge_frame(a, b):
    delta = b - a
    length = delta.length
    tangent = Vector((delta.x / length, delta.y / length, 0.0))
    outward = Vector((tangent.y, -tangent.x, 0.0)) * orientation_sign
    return length, tangent, outward


# Identify the southern frontage from the actual source outline/address. Its long
# east-west edge faces Mitch Daniels Boulevard and is the official-photo entrance.
front_index = min(range(len(points)),
                  key=lambda i: (points[i].y + points[(i+1) % len(points)].y) / 2)
front_a, front_b = points[front_index], points[(front_index+1) % len(points)]
front_len, front_tangent, front_outward = edge_frame(front_a, front_b)
front_center = (front_a + front_b) * 0.5

# Continuous source-matched structural walls. GIS overhangs are excluded from this
# footprint; belts, windows and portico are independent facade details.
for i, a in enumerate(points):
    b = points[(i+1) % len(points)]
    length, tangent, outward = edge_frame(a, b)
    if length < 0.2:
        continue
    quad((a.x,a.y,0), (b.x,b.y,0), (b.x,b.y,WALL_HEIGHT), (a.x,a.y,WALL_HEIGHT), BRICK)
    # Stone-colored base, floor belts and top cornice follow the footprint perimeter.
    for z, h in ((0.42,0.34), (STORY_HEIGHT,0.12), (2*STORY_HEIGHT,0.12),
                 (WALL_HEIGHT-0.38,0.22)):
        wall_box(((a.x+b.x)/2, (a.y+b.y)/2, z), tangent, outward,
                 length+0.04, 0.16, h, LIMESTONE)
    # Repeated window rhythm on every usable facade. The portal bay remains clear.
    if length >= 4.0:
        bays = max(1, int(length // 4.4))
        spacing = length / (bays + 1)
        win_w = min(1.48, spacing * 0.52)
        is_front = i == front_index
        for floor in range(STORIES):
            sill = 0.88 + floor * STORY_HEIGHT
            top = min(sill + 1.95, WALL_HEIGHT - 0.65)
            for bay in range(bays):
                along = spacing * (bay + 1)
                # Leave the central entrance/portico open on the primary frontage.
                if is_front and floor == 0 and abs(along - length/2) < 3.6:
                    continue
                center = a + tangent * along
                center3 = Vector((center.x, center.y, 0))
                p = center3 + outward * 0.07
                half = tangent * (win_w / 2)
                left = Vector((p.x-half.x, p.y-half.y, sill))
                right = Vector((p.x+half.x, p.y+half.y, sill))
                top_right = Vector((p.x+half.x, p.y+half.y, top))
                top_left = Vector((p.x-half.x, p.y-half.y, top))
                quad(left, right, top_right, top_left, GLASS)
                # Pale stone lintel/sill and side casing, with a dark vertical mullion.
                bar = 0.085
                zlo, zhi = sill - bar/2, top + bar/2
                hbar = tangent * (win_w/2 + bar/2)
                p0 = center3 + outward * 0.13
                quad((p0.x-hbar.x,p0.y-hbar.y,zlo), (p0.x+hbar.x,p0.y+hbar.y,zlo),
                     (p0.x+hbar.x,p0.y+hbar.y,sill+bar/2), (p0.x-hbar.x,p0.y-hbar.y,sill+bar/2), LIMESTONE)
                quad((p0.x-hbar.x,p0.y-hbar.y,top-bar/2), (p0.x+hbar.x,p0.y+hbar.y,top-bar/2),
                     (p0.x+hbar.x,p0.y+hbar.y,zhi), (p0.x-hbar.x,p0.y-hbar.y,zhi), LIMESTONE)
                for side in (-1,1):
                    cp = p0 + tangent * (side * (win_w/2 + bar/2))
                    halfbar = tangent * (bar/2)
                    quad((cp.x-halfbar.x,cp.y-halfbar.y,sill), (cp.x+halfbar.x,cp.y+halfbar.y,sill),
                         (cp.x+halfbar.x,cp.y+halfbar.y,top), (cp.x-halfbar.x,cp.y-halfbar.y,top), LIMESTONE)
                mullion_center = p0 + outward * 0.025
                mw = tangent * 0.035
                quad((mullion_center.x-mw.x,mullion_center.y-mw.y,sill),
                     (mullion_center.x+mw.x,mullion_center.y+mw.y,sill),
                     (mullion_center.x+mw.x,mullion_center.y+mw.y,top),
                     (mullion_center.x-mw.x,mullion_center.y-mw.y,top), DARK_METAL)
                # A subtle horizontal sash bar makes the double-hung rhythm legible.
                zmid = sill + (top-sill) * 0.53
                halfwin = tangent * (win_w/2)
                quad((p0.x-halfwin.x,p0.y-halfwin.y,zmid-0.035),
                     (p0.x+halfwin.x,p0.y+halfwin.y,zmid-0.035),
                     (p0.x+halfwin.x,p0.y+halfwin.y,zmid+0.035),
                     (p0.x-halfwin.x,p0.y-halfwin.y,zmid+0.035), DARK_METAL)

# Flat, low-profile roof surface with an overhanging limestone cornice and dark fascia.
for tri in tessellate_polygon([points]):
    tri_points = [points[int(i)] for i in tri]
    face([(p.x,p.y,ROOF_HEIGHT) for p in tri_points], ROOF)
for i, a in enumerate(points):
    b = points[(i+1) % len(points)]
    length, tangent, outward = edge_frame(a,b)
    offset = outward * 0.48
    quad((a.x,a.y,WALL_HEIGHT-0.16), (b.x,b.y,WALL_HEIGHT-0.16),
         (b.x+offset.x,b.y+offset.y,WALL_HEIGHT-0.16),
         (a.x+offset.x,a.y+offset.y,WALL_HEIGHT-0.16), DARK_METAL)
    quad((a.x+offset.x,a.y+offset.y,WALL_HEIGHT-0.16),
         (b.x+offset.x,b.y+offset.y,WALL_HEIGHT-0.16),
         (b.x+offset.x,b.y+offset.y,ROOF_HEIGHT),
         (a.x+offset.x,a.y+offset.y,ROOF_HEIGHT), LIMESTONE)

# South-facing classical portico and paired main doors from Purdue's exterior photo.
# Door glazing and trim sit slightly outside the structural facade plane.
door_w, door_h = 2.5, 2.95
door_center = Vector((front_center.x, front_center.y, 0.0)) + front_outward * 0.12
door_left = door_center - front_tangent * (door_w/2)
door_right = door_center + front_tangent * (door_w/2)
for lo, hi in ((door_left, (door_left+door_center)*0.5), ((door_left+door_center)*0.5, door_right)):
    quad((lo.x,lo.y,0.12), (hi.x,hi.y,0.12), (hi.x,hi.y,door_h), (lo.x,lo.y,door_h), GLASS)
# Door jambs, center meeting rail, transom, and limestone head.
for pos in (door_left, door_center, door_right):
    wall_box((pos.x+front_outward.x*0.05,pos.y+front_outward.y*0.05,door_h/2),
             front_tangent,front_outward,0.10,0.18,door_h+0.05,DARK_METAL)
wall_box((front_center.x+front_outward.x*0.12,front_center.y+front_outward.y*0.12,door_h+0.09),
         front_tangent,front_outward,door_w+0.45,0.28,0.20,LIMESTONE)
# Four square columns in a shallow portico, with bases and capitals.
portico_width, portico_depth = 8.4, 3.5
portico_center = front_center + Vector((front_outward.x,front_outward.y,0)) * (portico_depth/2+0.3)
for offset in (-3.0,-1.0,1.0,3.0):
    cxy = front_center + front_tangent*offset + Vector((front_outward.x,front_outward.y,0))*(portico_depth+0.20)
    wall_box((cxy.x,cxy.y,3.55),front_tangent,front_outward,0.42,0.50,6.5,LIMESTONE)
    wall_box((cxy.x,cxy.y,0.34),front_tangent,front_outward,0.76,0.78,0.34,LIMESTONE)
    wall_box((cxy.x,cxy.y,6.83),front_tangent,front_outward,0.75,0.78,0.34,LIMESTONE)
# Entablature slab spans columns and caps a shallow porch roof.
wall_box((portico_center.x,portico_center.y,7.12),front_tangent,front_outward,
         portico_width,portico_depth+0.55,0.62,LIMESTONE)
wall_box((portico_center.x,portico_center.y,7.47),front_tangent,front_outward,
         portico_width+0.38,portico_depth+0.86,0.16,DARK_METAL)
# Two stone approach steps, clearly separate from the GIS wall footprint.
for width, depth, z in ((7.8,0.72,0.20),(7.1,0.62,0.52)):
    c = front_center + Vector((front_outward.x,front_outward.y,0))*(portico_depth+0.55+depth/2)
    wall_box((c.x,c.y,z),front_tangent,front_outward,width,depth,0.28,PAVING)

# Replace starter mesh, keep its object/collection/scene and campus transform intact.
old_mesh = obj.data
mesh = bpy.data.meshes.new(OBJECT_NAME + "_source_based_detail")
mesh.from_pydata(verts, [], faces)
for mat in materials:
    mesh.materials.append(mat)
mesh.update()
for poly, mi in zip(mesh.polygons, face_mats):
    poly.material_index = mi
bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(mesh)
bm.free()
for vert in mesh.vertices:
    if vert.co.z < 0.0:
        vert.co.z = 0.0
mesh.update()
obj.data = mesh
obj.name = OBJECT_NAME
obj.location = (0.0,0.0,0.0)
obj.rotation_euler = (0.0,0.0,0.0)
obj.scale = (1.0,1.0,1.0)
if old_mesh.users == 0:
    bpy.data.meshes.remove(old_mesh)
mesh.name = OBJECT_NAME + "_mesh"

# Remove unused image datablocks inherited from the simple starter asset so this
# rebuilt library has no stale external texture paths.
for image in list(bpy.data.images):
    if image.source == "FILE" and image.users == 0:
        bpy.data.images.remove(image)

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("MTHW_BUILD_RESULT=" + json.dumps({
    "asset_id": ASSET_ID,
    "source_fid": attrs["FID"],
    "building_code": attrs["BLDG_ABBR"],
    "footprint_vertices": len(points),
    "mesh_vertices": len(mesh.vertices),
    "mesh_faces": len(mesh.polygons),
    "collection_object_count": len(collection.objects),
    "modeled_above_grade_stories": STORIES,
    "estimated_wall_height_m": WALL_HEIGHT,
    "estimated_roof_height_m": ROOF_HEIGHT,
    "campus_xy_bounds_m": [min_x,max_x,min_y,max_y],
    "primary_facade_orientation": "south toward Mitch Daniels Boulevard; inferred from address and official photo",
    "height_basis": "estimated from current Purdue BEP's three-story description; no measured elevation found"
}))

