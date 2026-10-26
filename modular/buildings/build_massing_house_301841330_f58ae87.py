"""Build the Sigma Nu Beta Zeta chapter house (Purdue GIS FID 758).

Inputs and source metadata live under audit/sigma_nu/sources/. Geometry is in
project campus coordinates (meters, X east, Y north, Z up). Re-run with Blender:
    blender -b --python modular/buildings/build_massing_house_301841330_f58ae87.py
"""
from __future__ import annotations
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "sigma_nu"
SOURCE = AUDIT / "sources" / "purdue_gis_fid_758.json"
ASSET = ROOT / "modular" / "buildings" / "massing_house_301841330_f58ae87.blend"
PREVIEW = AUDIT / "sigma_nu_preview.png"
BUILDING_ID = "massing_house_301841330_f58ae87"
COLLECTION_NAME = "Asset_" + BUILDING_ID
SCENE_NAME = "Building_" + BUILDING_ID

with SOURCE.open("r", encoding="utf-8-sig") as stream:
    feature = json.load(stream)
attrs = feature["attributes"]
assert attrs["FID"] == 758 and attrs["BLDG_ABBR"] == "SOSN"
ring = feature["geometry"]["rings"][0]
if ring[0] == ring[-1]:
    ring = ring[:-1]
lat0, lon0 = 40.4274, -86.9137
x_scale = 111412.84 * math.cos(math.radians(lat0))
vertices_xy = [((lon - lon0) * x_scale, (lat - lat0) * 111040.0) for lon, lat in ring]
# Keep ring CCW in the project XY plane, making boundary normals predictable.
def signed_area(points):
    return sum(points[i][0] * points[(i+1) % len(points)][1] - points[(i+1) % len(points)][0] * points[i][1] for i in range(len(points))) / 2
if signed_area(vertices_xy) < 0:
    vertices_xy.reverse()

# Reset this dedicated library only.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for collection in list(bpy.data.collections):
    if collection.name != "Collection":
        bpy.data.collections.remove(collection)
scene = bpy.context.scene
scene.name = SCENE_NAME
asset_collection = bpy.data.collections.get(COLLECTION_NAME) or bpy.data.collections.new(COLLECTION_NAME)
if asset_collection.name not in scene.collection.children:
    scene.collection.children.link(asset_collection)
review_collection = bpy.data.collections.get("Review_Only_Sigma_Nu") or bpy.data.collections.new("Review_Only_Sigma_Nu")
if review_collection.name not in scene.collection.children:
    scene.collection.children.link(review_collection)

# Materials use simple Principled BSDF colors and do not depend on external files.
def material(name, color, roughness=0.78, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat
brick = material("Warm red-brown brick (photo-supported)", (0.38, 0.105, 0.075))
base_masonry = material("Light lower-story masonry (photo-supported)", (0.67, 0.63, 0.54))
stone = material("Pale stone/concrete trim (photo-supported)", (0.72, 0.68, 0.58))
glass = material("Dark window glass (generalized)", (0.045, 0.075, 0.09), 0.26, 0.12)
roof_mat = material("Dark asphalt roof (roof material reported; form estimated)", (0.12, 0.14, 0.16))
door_mat = material("Recessed entry", (0.09, 0.055, 0.04))

# Main GIS outline is the footprint baseline. GIS does not identify it as a
# surveyed wall line; the polygon is retained unwarped as the best available shell.
wall_h = 7.2  # estimated; GIS NUM_LEVELS/Extrution semantics are not a height datum
base_h = 2.8  # estimated story break; photo shows contrasting lower masonry and upper brick
roof_h = 0.25 # neutral low cap; roof form and dimensions remain unverified
n = len(vertices_xy)
verts = [(x, y, z) for z in (0.0, base_h, wall_h) for x, y in vertices_xy]
faces = [tuple(range(n-1, -1, -1)), tuple(range(2*n, 3*n))]
faces += [(i, (i+1)%n, (i+1)%n+n, i+n) for i in range(n)]
faces += [(i+n, (i+1)%n+n, (i+1)%n+2*n, i+2*n) for i in range(n)]
mesh = bpy.data.meshes.new("Sigma Nu FID 758 GIS footprint shell")
mesh.from_pydata(verts, [], faces)
mesh.materials.append(base_masonry)
mesh.materials.append(brick)
mesh.materials.append(roof_mat)
mesh.polygons[0].material_index = 0
mesh.polygons[1].material_index = 2
for face in mesh.polygons[2:2+n]: face.material_index = 0
for face in mesh.polygons[2+n:]: face.material_index = 1
body = bpy.data.objects.new("House_301841330", mesh)
asset_collection.objects.link(body)

# Deterministic bounds and face helpers.
center_x = sum(x for x, _ in vertices_xy) / n
center_y = sum(y for _, y in vertices_xy) / n
front_candidates = []
for i in range(n):
    edge = Vector(vertices_xy[(i+1)%n]) - Vector(vertices_xy[i])
    normal = Vector((edge.y, -edge.x)).normalized()  # outward for this CCW ring
    if normal.y > 0.7:
        front_candidates.append((edge.length, i))
# Choose the longest GIS edge that faces north/northwest toward Tower Drive.
# The road alignment is contextual evidence, not a surveyed facade bearing.
fallback_edges = [((Vector(vertices_xy[(i+1)%n]) - Vector(vertices_xy[i])).length, i) for i in range(n)]
long_edge = max(front_candidates or fallback_edges)[1]
p0 = Vector(vertices_xy[long_edge]); p1 = Vector(vertices_xy[(long_edge+1)%n])
tangent = (p1-p0).normalized()
# CCW polygon's outward normal is to the right of the edge.
outward = Vector((tangent.y, -tangent.x))
facade_center = (p0+p1)/2
facade_length = (p1-p0).length

def add_box(name, center, dimensions, tangent2=tangent, normal2=outward, mat=stone):
    c = Vector((center[0], center[1], center[2]))
    t = Vector((tangent2.x, tangent2.y, 0)).normalized()
    up = Vector((0,0,1))
    normal = Vector((normal2.x, normal2.y,0)).normalized()
    # local axes: width along facade, depth toward facade normal, height up
    w,d,h = dimensions
    local = [(-w/2,-d/2,-h/2),(w/2,-d/2,-h/2),(w/2,d/2,-h/2),(-w/2,d/2,-h/2),
             (-w/2,-d/2,h/2),(w/2,-d/2,h/2),(w/2,d/2,h/2),(-w/2,d/2,h/2)]
    vs = [tuple(c + t*a + normal*b + up*cc) for a,b,cc in local]
    fs = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me = bpy.data.meshes.new(name + " mesh"); me.from_pydata(vs, [], fs); me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); asset_collection.objects.link(ob); return ob

# The front elevation is photo-supported at a broad level: brick, pale
# horizontal trim, recessed centered entry, and multiple rectangular openings.
# Beta Zeta's Spring 2022 newsletter names rooms on floors one through three;
# the vertical story division is therefore represented, but exact elevations
# and whether all three floors are above grade remain unverified.
front_l = min(facade_length - 2.0, 24.0)
front_start = facade_center - tangent * (front_l/2)
# Pale stringcourses and lintel bands.
middle_story = (base_h + wall_h) / 2
for z in (base_h+0.05, middle_story, wall_h-0.08):
    add_box("Front facade pale horizontal band", (facade_center.x, facade_center.y, z), (front_l, 0.15, 0.16), mat=stone)
# Central recessed doorway plus low canopy and two pale piers.
entry_w = min(2.8, front_l*0.15)
entry_center = facade_center
add_box("Recessed central entrance", (entry_center.x, entry_center.y + outward.y*0.14, 1.40), (entry_w, 0.12, 2.8), mat=door_mat)
for side in (-1,1):
    loc = entry_center + tangent * (side*(entry_w/2 + 0.28)) + outward*0.22
    add_box("Pale entrance pier", (loc.x,loc.y,1.6), (0.48,0.42,3.2), mat=stone)
canopy_center = entry_center + outward*0.45
add_box("Entrance canopy", (canopy_center.x,canopy_center.y,3.0), (entry_w+1.25,1.0,0.26), mat=stone)
# Multiple front openings and at least three occupied floors are source-backed;
# counts, spacing, window dimensions, and exact story heights remain estimates.
for z in (base_h + (middle_story-base_h)/2, (middle_story+wall_h)/2):
    for side in (-1,1):
        along = side * (entry_w/2 + 3.8)
        loc = facade_center + tangent*along + outward*0.10
        add_box("Pale window surround", (loc.x,loc.y,z), (2.25,0.15,1.55), mat=stone)
        loc2 = facade_center + tangent*along + outward*0.20
        add_box("Dark rectangular window", (loc2.x,loc2.y,z), (1.92,0.12,1.25), mat=glass)

# Photo 2 on the same 2019 newsletter shows a projecting upper-level bay window
# on a side elevation. Its exact orientation and dimensions are not recoverable
# from the un-georeferenced photograph, so place a restrained bay on the side
# adjoining the north-facing entrance facade and keep its profile within the GIS
# outline. It is represented as a recessed bay mass, since the polygon is the
# only plan evidence and cannot establish the projection depth.
side_i = (long_edge + 1) % n
side_a = Vector(vertices_xy[side_i]); side_b = Vector(vertices_xy[(side_i+1)%n])
side_t = (side_b-side_a).normalized(); side_n = Vector((side_t.y,-side_t.x))
side_mid = (side_a+side_b)/2
bay_c = side_mid - side_n*0.30
add_box("Pale side bay surround", (bay_c.x,bay_c.y,5.3), (3.0,0.60,2.2), tangent2=side_t, normal2=side_n, mat=stone)
bay_g = side_mid - side_n*0.06
add_box("Side bay glazing", (bay_g.x,bay_g.y,5.3), (2.45,0.08,1.72), tangent2=side_t, normal2=side_n, mat=glass)

# Roof plate forms a low, dark parapet cap. Building height and roof profile remain
# estimates because no measured elevations were found.
roof_verts = [(x,y,wall_h+roof_h) for x,y in vertices_xy]
roof_mesh = bpy.data.meshes.new("Estimated flat roof plan")
roof_mesh.from_pydata(roof_verts, [], [tuple(range(n))]); roof_mesh.materials.append(roof_mat)
roof_obj = bpy.data.objects.new("Estimated low roof silhouette", roof_mesh); asset_collection.objects.link(roof_obj)
# A narrow roof fascia makes the estimated cap readable without changing its plan.
for i in range(n):
    a=Vector(vertices_xy[i]); b=Vector(vertices_xy[(i+1)%n]); edge=(b-a).length
    mid=(a+b)/2
    direction=(b-a).normalized(); norm=Vector((direction.y,-direction.x))
    add_box("Roof fascia", (mid.x,mid.y,wall_h+roof_h/2), (edge,0.08,roof_h), tangent2=direction, normal2=norm, mat=roof_mat)

# Use one camera to show the front and footprint. This render is a review aid.
scene.render.engine = "CYCLES"
scene.cycles.samples = 16
scene.render.resolution_x = 1200; scene.render.resolution_y = 900; scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(PREVIEW)
scene.world.color = (0.14,0.14,0.14)
# Camera comes from the selected facade's outward direction.
target = Vector((center_x,center_y,4.4))
cam_pos = Vector((facade_center.x,facade_center.y,0)) + Vector((outward.x,outward.y,0))*58 + Vector((0,0,23))
bpy.ops.object.camera_add(location=cam_pos)
cam=bpy.context.object; cam.name="Review camera"
cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler(); cam.data.type="ORTHO"; cam.data.ortho_scale=44
scene.camera=cam
# key light
bpy.ops.object.light_add(type="AREA", location=(center_x+18,center_y+25,35))
light=bpy.context.object; light.name="Review key light"; light.data.energy=4200; light.data.shape="DISK"; light.data.size=24
light.rotation_euler=(target-light.location).to_track_quat("-Z","Y").to_euler()
# Move all objects into the dedicated library collection, preserving the scene.
for ob in list(scene.objects):
    if ob is cam or ob is light:
        for c in list(ob.users_collection): c.objects.unlink(ob)
        review_collection.objects.link(ob)
    elif ob.name not in asset_collection.objects:
        for c in list(ob.users_collection): c.objects.unlink(ob)
        asset_collection.objects.link(ob)
# Hide review camera/lights from the exported collection? Leave them in scene but
# disabled in viewport/render collection for the consumer.
for ob in (cam, light):
    ob.hide_render = True; ob.hide_viewport = True
# Collection contains geometry plus hidden review objects; render before hiding.
for ob in (cam, light): ob.hide_render = False; ob.hide_viewport = False
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
bpy.ops.render.render(write_still=True)
# Preserve camera and light but hide them on asset open.
for ob in (cam, light): ob.hide_render=True; ob.hide_viewport=True
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
# Record source-ring exactness in a lightweight machine-readable validation file.
base_xy = [(float(v.co.x), float(v.co.y)) for v in body.data.vertices if abs(v.co.z) < 1e-6]
ring_error = max(min(math.dist(point, actual) for actual in base_xy) for point in vertices_xy)
ring_error = max(ring_error, max(min(math.dist(point, source) for source in vertices_xy) for point in base_xy))
with (AUDIT / "build_validation.json").open("w", encoding="utf-8") as stream:
    json.dump({"building_id":BUILDING_ID,"source_fid":758,"source_polygon_vertices":n,
               "base_ring_max_vertex_error_m":ring_error,"transform":"project local approximate geographic conversion; EPSG:4326 input",
               "bounds_xy_m":[[min(x for x,y in vertices_xy),max(x for x,y in vertices_xy)],
                               [min(y for x,y in vertices_xy),max(y for x,y in vertices_xy)]],
               "estimated_wall_height_m":wall_h,"estimated_roof_height_m":wall_h+roof_h,"estimated_lower_masonry_height_m":base_h,
               "source_supported_minimum_occupied_floors":3,
               "estimated_story_division_z_m":[base_h,(base_h+wall_h)/2],
               "front_orientation":"longest north/northwest-facing GIS edge selected toward Tower Drive; photo is not georeferenced",
               "facade_source":"Beta Zeta Fall 2019 newsletter page 3 plus Spring 2022 newsletter p. 1 and p. 6 exterior/context images; contrasting lower/upper masonry, entrance, openings and side bay broadly generalized. Spring 2022 text supports at least three occupied floors.",
               "unresolved":"Absolute wall/roof height, story elevations, whether each occupied floor is above grade, roof form and dimensions, unseen elevations, wall-vs-roof GIS boundary, and precise facade bearing."},stream,indent=2)
print("SIGMA_NU_BUILD", json.dumps({"fid":758,"vertices":n,"facade_edge_m":facade_length,"wall_height_estimate_m":wall_h,"roof_height_estimate_m":wall_h+roof_h,"asset":str(ASSET)}))
