"""Rebuild Riverside Covenant Church from the Indiana 2018 LiDAR footprint and a dated exterior reference.

The source library is a campus-coordinate massing asset. This script preserves its
asset/collection names and writes only to the already-open assigned .blend file.
Architectural heights and the photo-derived entrance composition remain estimates.
"""
import bpy
import bmesh
import json
import math
import os
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "audit" / "riverside_covenant_church"
ASSET_ID = "massing_riverside_covenannt_church_3a60684"
COLLECTION_NAME = "Asset_" + ASSET_ID
OBJECT_NAME = "Riverside Covenannt Church"
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137

with (EVIDENCE / "indiana_building_footprint_feature_409445.json").open(encoding="utf-8") as f:
    gis = json.load(f)
feature = gis["features"][0]
raw_ring = feature["geometry"]["rings"][0][:-1]
obj = bpy.data.objects.get(OBJECT_NAME)
collection = bpy.data.collections.get(COLLECTION_NAME)
if not bpy.data.filepath or obj is None or collection is None or obj not in collection.objects[:] or len(collection.objects) != 1:
    raise RuntimeError("Assigned Riverside asset/collection mismatch")
world = obj.matrix_world.copy()
inverse = world.inverted_safe()

def project(lon, lat):
    return Vector(((lon + 86.9137) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
                   (lat - ORIGIN_LAT) * 111040.0, 0.0))

ring = [project(lon, lat) for lon, lat in raw_ring]
if len(ring) != 4:
    raise RuntimeError(f"Expected independent GIS quadrilateral; got {len(ring)} vertices")
center = sum(ring, Vector((0, 0, 0))) / len(ring)
# Use the longest polygon edge as the hall's long axis. Orient it eastward so its
# perpendicular is northward and the photographed entrance remains on the south side.
edges=[ring[(i+1)%len(ring)]-ring[i] for i in range(len(ring))]
axis=max(edges,key=lambda e:e.length).normalized()
if axis.x<0: axis.negate()
cross=Vector((-axis.y,axis.x,0.0))
length=max(e.length for e in edges)
width=min(e.length for e in edges)

# Estimates are kept explicit: the exterior photograph supports the low horizontal
# roof and central glazed A-frame, but supplies no surveyed elevations.
eaves, main_ridge, apex = 4.5, 5.7, 11.5
overhang = 0.55
tag = ASSET_ID
def material(name, color, roughness=0.78, metallic=0.0):
    m = bpy.data.materials.get(tag + "_" + name) or bpy.data.materials.new(tag + "_" + name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return m

brick = material("Brick", (0.105, 0.022, 0.009))
trim = material("Stone_Trim", (0.84, 0.80, 0.69))
glass = material("Glazing", (0.035, 0.10, 0.14), 0.23, 0.03)
roof = material("Slate_Roof", (0.018, 0.022, 0.026), 0.85)
wood = material("Entry_Wood", (0.19, 0.075, 0.04), 0.52)
vertices, faces, material_ids = [], [], []
def add_face(points, mi):
    start = len(vertices)
    vertices.extend(tuple(inverse @ p) for p in points)
    faces.append(tuple(range(start, start + len(points))))
    material_ids.append(mi)

def add_box(c, tangent, normal, box_width, depth, height, mi):
    c = Vector(c); t = Vector((tangent.x, tangent.y, 0)).normalized()
    n = Vector((normal.x, normal.y, 0)).normalized(); z = Vector((0,0,1))
    hw, hd, hh = box_width/2, depth/2, height/2
    offsets = [(-hw,-hd,-hh),(hw,-hd,-hh),(hw,hd,-hh),(-hw,hd,-hh),
               (-hw,-hd,hh),(hw,-hd,hh),(hw,hd,hh),(-hw,hd,hh)]
    start = len(vertices)
    vertices.extend(tuple(inverse @ (c+t*a+n*b+z*h)) for a,b,h in offsets)
    for face in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
        faces.append(tuple(start+i for i in face)); material_ids.append(mi)

def add_beam(p0, p1, tangent, thickness, depth, mi):
    p0, p1 = Vector(p0), Vector(p1)
    direction = (p1-p0).normalized()
    front = Vector((tangent.x, tangent.y, 0)).normalized()
    side = direction.cross(front).normalized()
    if side.z < 0: side.negate()
    points = [p0-side*thickness/2-front*depth/2, p0+side*thickness/2-front*depth/2,
              p0+side*thickness/2+front*depth/2, p0-side*thickness/2+front*depth/2,
              p1-side*thickness/2-front*depth/2, p1+side*thickness/2-front*depth/2,
              p1+side*thickness/2+front*depth/2, p1-side*thickness/2+front*depth/2]
    start=len(vertices); vertices.extend(tuple(inverse @ p) for p in points)
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
        faces.append(tuple(start+i for i in f)); material_ids.append(mi)

# Structural shell follows the independent state GIS perimeter (feature 409445).
for i, a0 in enumerate(ring):
    b0 = ring[(i+1)%len(ring)]
    add_face((a0,b0,Vector((b0.x,b0.y,eaves)),Vector((a0.x,a0.y,eaves))),0)

# Shallow roof across the main hall, matching the low horizontal eaves in the 2016 view.
half_l, half_w = length/2+overhang, width/2+overhang
end0, end1 = center-axis*half_l, center+axis*half_l
s0,s1=end0-cross*half_w,end1-cross*half_w
n0,n1=end0+cross*half_w,end1+cross*half_w
ra=Vector((end0.x,end0.y,main_ridge)); rb=Vector((end1.x,end1.y,main_ridge))
for pts in ((s0+Vector((0,0,eaves)),ra,rb,s1+Vector((0,0,eaves))),
            (ra,n0+Vector((0,0,eaves)),n1+Vector((0,0,eaves)),rb)):
    add_face(pts,3)

# Front is the south long facade. The photo shows a centered A-frame stained-glass
# entrance, masonry piers, and a continuous shallow canopy/roof edge.
front = center-cross*(width/2)
front_y = front.y - 0.06
front_normal = -cross
half_frame=4.7
left=Vector((center.x-axis.x*half_frame,front_y,4.85))
right=Vector((center.x+axis.x*half_frame,front_y,4.85))
peak=Vector((center.x,front_y,apex))
# Dark glazed triangular field, ivory A-frame surround, and a simple mullion grid.
add_face((left,right,peak),2)
add_beam(left,peak,front_normal,0.28,0.34,1)
add_beam(peak,right,front_normal,0.28,0.34,1)
add_beam(left,right,front_normal,0.22,0.34,1)
for fraction in (-0.68,-0.36,0.0,0.36,0.68):
    x=center.x+axis.x*half_frame*fraction
    height=4.85+(apex-4.85)*(1-abs(fraction))
    add_beam((x,front_y-0.03,4.95),(x,front_y-0.03,height),front_normal,0.075,0.16,1)
for z in (6.4,7.9,9.4):
    half=half_frame*(apex-z)/(apex-4.85)
    add_beam((center.x-axis.x*half,front_y-0.04,z),(center.x+axis.x*half,front_y-0.04,z),front_normal,0.065,0.16,1)

# Door bank beneath the glazed peak: four glazed paired entry bays from the reference.
door_y=front_y-0.12
door_width=2.15
for i in range(4):
    x=center.x+axis.x*((i-1.5)*2.35)
    add_box((x,door_y,1.62),axis,front_normal,door_width,0.10,3.18,4)
    # Narrow glazing lights and visible vertical meeting stile.
    add_box((x,door_y-0.075,2.0),axis,front_normal,1.48,0.035,1.85,2)
    add_box((x,door_y-0.10,1.62),axis,front_normal,0.07,0.10,3.18,1)
    for dx in (-door_width/2,door_width/2):
        add_box(Vector((x,door_y-0.09,1.62))+axis*dx,axis,front_normal,0.09,0.11,3.10,1)

# Side windows remain schematic: the old unverified row is replaced with modest
# openings consistent with the horizontal brick hall, but not claimed measured.
for side_sign in (-1.0,1.0):
    outward=cross*side_sign
    wall=center+outward*(width/2)
    for fraction in (-0.31,0.0,0.31):
        p=wall+axis*(length*fraction)
        add_box(Vector((p.x,p.y,2.4))+outward*0.08,axis,outward,2.0,0.08,1.5,2)
        add_box(Vector((p.x,p.y,2.4))+outward*0.14,axis,outward,2.18,0.10,0.10,1)
        for dx in (-1.04,1.04):
            add_box(Vector((p.x,p.y,2.4))+outward*0.14+axis*dx,axis,outward,0.10,0.10,1.68,1)

old_mesh=obj.data
old_mesh_name=old_mesh.name
mesh=bpy.data.meshes.new(old_mesh_name+"_gis_a_frame_revision")
mesh.from_pydata(vertices,[],faces)
for m in (brick,trim,glass,roof,wood): mesh.materials.append(m)
mesh.update()
for poly,mi in zip(mesh.polygons,material_ids): poly.material_index=mi
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update()
obj.data=mesh
if old_mesh.users==0: bpy.data.meshes.remove(old_mesh)
mesh.name=old_mesh_name
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
world_vertices=[world@v.co for v in mesh.vertices]
result={"asset_id":ASSET_ID,"collection_objects":len(collection.objects),"footprint_source":"Indiana Building Footprints 2016-2020; objectid 409445; lidar year 2018","source_ring_vertices":len(ring),"mesh_vertices":len(mesh.vertices),"mesh_faces":len(mesh.polygons),"bounds_world_m":[[round(min(v[i] for v in world_vertices),6),round(max(v[i] for v in world_vertices),6)] for i in range(3)],"estimated_eaves_m":eaves,"estimated_main_roof_ridge_m":main_ridge,"estimated_glazed_apex_m":apex,"footprint_preserved_from_independent_gis":True}
print("BUILD_RESULT_JSON="+json.dumps(result))
