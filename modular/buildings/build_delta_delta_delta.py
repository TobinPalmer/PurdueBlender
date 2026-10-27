"""Build a source-backed detailed library for Delta Delta Delta, FID 753.

Run with Blender 5.2 in background mode from the repository root:
  blender -b --python modular/buildings/build_delta_delta_delta.py

The GIS outline is projected into the project's local campus metre approximation,
then recentered at its polygon centroid. Geometry is stored in that local frame;
Tobin must update the master Placement_massing_house_301841333_affe21e marker
and manifest placement_origin_xy_m when integrating this library.
"""
import bpy
import json
import math
import os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSET_ID = "massing_house_301841333_affe21e"
ASSET_PATH = os.path.join(ROOT, "modular", "buildings", ASSET_ID + ".blend")
GIS_PATH = os.path.join(ROOT, "audit", "delta_delta_delta", "sources", "purdue_building_fid_753.geojson")
OUT_DIR = os.path.join(ROOT, "audit", "delta_delta_delta")
SCENE_NAME = "Building_" + ASSET_ID
COLLECTION_NAME = "Asset_" + ASSET_ID
LAT0, LON0 = 40.4274, -86.9137

# Height values are explicitly visual estimates, based on the April 2026 street
# panorama showing two occupied levels and a low roof. They are not survey data.
BASE_Z = 0.0
GROUND_FLOOR_TOP = 3.75
SECOND_FLOOR_TOP = 7.05
EAVE_Z = 7.85
RIDGE_Z = 10.05
FRONT = "south"


def project(lon, lat):
    return ((lon - LON0) * 111412.84 * math.cos(math.radians(LAT0)),
            (lat - LAT0) * 111040.0)


def polygon_centroid(points):
    twice_area = cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]):
        cross = x1 * y2 - x2 * y1
        twice_area += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    if abs(twice_area) < 1e-8:
        raise ValueError("FID 753 source ring has zero area")
    return cx / (3.0 * twice_area), cy / (3.0 * twice_area)


with open(GIS_PATH, encoding="utf-8") as f:
    feature = json.load(f)["features"][0]
if feature["properties"].get("FID") != 753 or feature["properties"].get("BUILDING_N") != "Delta Delta Delta":
    raise ValueError("Official GIS feature identity mismatch; refusing to build")
source_ring = feature["geometry"]["coordinates"][0]
campus_ring = [project(lon, lat) for lon, lat in source_ring[:-1]]
ORIGIN_XY = polygon_centroid(campus_ring)
ring = [(x - ORIGIN_XY[0], y - ORIGIN_XY[1]) for x, y in campus_ring]
if len(ring) < 8:
    raise ValueError("FID 753 footprint unexpectedly sparse")

# Remove stale scene data when this reproducible builder is rerun.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for data in list(bpy.data.collections):
    if data.users == 0:
        bpy.data.collections.remove(data)
scene = bpy.context.scene
scene.name = SCENE_NAME
asset = bpy.data.collections.new(COLLECTION_NAME)
scene.collection.children.link(asset)
presentation = bpy.data.collections.new("Presentation_Camera_Lights")
scene.collection.children.link(presentation)


def principled(name, color, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat, bsdf


brick, brick_bsdf = principled("DeltaDeltaDelta_BuffBrick", (0.72, 0.60, 0.47), 0.86)
nodes, links = brick.node_tree.nodes, brick.node_tree.links
texcoord = nodes.new("ShaderNodeTexCoord")
bricktex = nodes.new("ShaderNodeTexBrick")
bricktex.offset = 0.5
bricktex.offset_frequency = 2
bricktex.inputs["Color1"].default_value = (0.78, 0.66, 0.52, 1)
bricktex.inputs["Color2"].default_value = (0.70, 0.57, 0.43, 1)
bricktex.inputs["Mortar"].default_value = (0.88, 0.82, 0.73, 1)
bricktex.inputs["Scale"].default_value = 1.0
bricktex.inputs["Mortar Size"].default_value = 0.025
bricktex.inputs["Mortar Smooth"].default_value = 0.02
bricktex.inputs["Brick Width"].default_value = 0.55
bricktex.inputs["Row Height"].default_value = 0.18
links.new(texcoord.outputs["UV"], bricktex.inputs["Vector"])
links.new(bricktex.outputs["Color"], brick_bsdf.inputs["Base Color"])
noise = nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 30.0
bump = nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.12
bump.inputs["Distance"].default_value = 0.035
links.new(texcoord.outputs["UV"], noise.inputs["Vector"])
links.new(noise.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], brick_bsdf.inputs["Normal"])

stone, _ = principled("DeltaDeltaDelta_LightLimestone", (0.72, 0.68, 0.60), 0.68)
white, _ = principled("DeltaDeltaDelta_PaintedWhite", (0.84, 0.82, 0.77), 0.58)
roof, roof_bsdf = principled("DeltaDeltaDelta_CharcoalShingle", (0.12, 0.14, 0.16), 0.88)
rn = roof.node_tree.nodes.new("ShaderNodeTexNoise")
rn.inputs["Scale"].default_value = 95
rb = roof.node_tree.nodes.new("ShaderNodeBump")
rb.inputs["Strength"].default_value = 0.22
rb.inputs["Distance"].default_value = 0.035
roof.node_tree.links.new(rn.outputs["Fac"], rb.inputs["Height"])
roof.node_tree.links.new(rb.outputs["Normal"], roof_bsdf.inputs["Normal"])
glass, _ = principled("DeltaDeltaDelta_BlueGrayGlazing", (0.12, 0.21, 0.25), 0.24, 0.18)
door_mat, _ = principled("DeltaDeltaDelta_DeepBlueDoors", (0.035, 0.10, 0.17), 0.32)
metal, _ = principled("DeltaDeltaDelta_RailingMetal", (0.68, 0.68, 0.64), 0.38, 0.72)
interior, _ = principled("DeltaDeltaDelta_WarmInterior", (0.73, 0.65, 0.50), 0.75)
wood, _ = principled("DeltaDeltaDelta_InteriorWood", (0.28, 0.14, 0.075), 0.52)


def make_mesh(name, verts, faces, material, coll=asset):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    return obj


def cube(name, loc, scale, mat, coll=asset, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    # Move out of the active scene's root collection and into the asset collection.
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Soft_masonry_edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return obj


def beam_between(name, a, b, width, depth, mat):
    mid = (Vector(a) + Vector(b)) * 0.5
    d = Vector(b) - Vector(a)
    obj = cube(name, mid, (d.length, width, depth), mat)
    obj.rotation_euler[2] = math.atan2(d.y, d.x)
    return obj


def cylinder(name, loc, radius, depth, mat, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    obj = bpy.context.object
    obj.name = name
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    asset.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def extruded_ring(name, pts, z0, z1, mat, cap=True):
    n = len(pts)
    verts = [(x, y, z0) for x, y in pts] + [(x, y, z1) for x, y in pts]
    faces = [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    if cap:
        faces.append(tuple(range(n, 2 * n)))
    return make_mesh(name, verts, faces, mat)


def wall_panel(name, a, b, u0, u1, z0, z1, material=brick):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    verts = [(a[0] + ux*u0, a[1] + uy*u0, z0),
             (a[0] + ux*u1, a[1] + uy*u1, z0),
             (a[0] + ux*u1, a[1] + uy*u1, z1),
             (a[0] + ux*u0, a[1] + uy*u0, z1)]
    obj=make_mesh(name, verts, [(0, 1, 2, 3)], material)
    uv=obj.data.uv_layers.new(name="PhysicalBrickUV")
    coords=((u0,z0),(u1,z0),(u1,z1),(u0,z1))
    for loop,co in zip(obj.data.polygons[0].loop_indices,coords):
        uv.data[loop].uv=co
    return obj


def oriented_box(name, center, width, height, depth, tangent, z_center, mat, bevel=0.0):
    x, y = center
    angle = math.atan2(tangent[1], tangent[0])
    obj = cube(name, (x, y, z_center), (width, depth, height), mat, bevel=bevel)
    obj.rotation_euler[2] = angle
    return obj


def window(name, center, tangent, zbase, width=1.55, height=2.0, arch=True):
    x, y = center
    tx, ty = tangent
    # Slightly recessed dark glass on the plane of the facade; perimeter masonry
    # is intentionally cut around openings by the wall-panel builder below.
    oriented_box(name + "_Glass", (x, y), width*0.82,
                 height*0.76, 0.045, tangent, zbase + height*0.46, glass)
    # Light stone jambs, sill, lintel/arch spring.
    frame = 0.10
    for side in (-1, 1):
        cx, cy = x + tx*side*(width/2-frame/2), y + ty*side*(width/2-frame/2)
        oriented_box(name + "_Jamb" + str(side), (cx, cy), frame, height, 0.16,
                     tangent, zbase + height/2, stone)
    oriented_box(name + "_Sill", (x, y), width+0.18, frame, 0.2, tangent,
                 zbase+0.05, stone)
    if arch:
        # A segmented half-round arch follows the observed tall first-floor arches.
        for k in range(13):
            a0 = math.pi*k/13
            a1 = math.pi*(k+1)/13
            r = width/2
            p0 = (x + tx*r*math.cos(a0), y + ty*r*math.cos(a0), zbase+height*0.72+r*math.sin(a0))
            p1 = (x + tx*r*math.cos(a1), y + ty*r*math.cos(a1), zbase+height*0.72+r*math.sin(a1))
            beam_between(name + "_ArchStone" + str(k), p0, p1, 0.10, 0.17, stone)
    else:
        oriented_box(name + "_Lintel", (x, y), width+0.18, frame, 0.2, tangent,
                     zbase+height-0.02, stone)
    # Center mullion and cross rail make windows read at campus scale.
    oriented_box(name + "_MullionV", (x, y-0.025), 0.055, height*0.80, 0.035,
                 tangent, zbase+height*0.46, white)
    oriented_box(name + "_MullionH", (x, y-0.035), width*0.76, 0.05, 0.035,
                 tangent, zbase+height*0.47, white)


# Wall shell: use GIS ring as the structural outer wall and leave true openings
# around each repeated window. Small GIS serrations are preserved; tiny edges
# get simple solid spandrel panels to avoid creating malformed windows.
ring_edges = []
for i, a in enumerate(ring):
    b = ring[(i + 1) % len(ring)]
    dx, dy = b[0]-a[0], b[1]-a[1]
    length = math.hypot(dx, dy)
    if length > 0.3:
        ring_edges.append((i, a, b, length, dx/length, dy/length))

# FID 753's southern curved edge (vertices 21-50) is the projecting entry
# pavilion visible in Street View. The panorama is near the GIS centroid looking
# north; the portico is centered near local x=-0.6 m.
front_idx = next(e for e in ring_edges if e[0] == 32)
front_mid = ((front_idx[1][0]+front_idx[2][0])/2, (front_idx[1][1]+front_idx[2][1])/2)
front_vec = (-1.0, 0.0)
normal_south = (0.0, -1.0)
front_edge_length = front_idx[3]
front_y = front_mid[1]
porch_center=(-0.6,-8.45)

# Wall opening placements along longer edges. The south-facing main facade gets
# two flanking arch windows and the entry; upper openings are rectangular.
window_records = []
for idx, a, b, length, tx, ty in ring_edges:
    # This GIS arc is the open, columned front portico. Model it separately;
    # solid panels on its short segments would seal the observed entry.
    if 21 <= idx <= 50:
        continue
    tangent = (tx, ty)
    is_front = idx == front_idx[0]
    count = max(1, int((length - 2.6) / 2.85)) if length >= 6.0 else 0
    if count == 0:
        wall_panel("DDD_Wall_%02d" % idx, a, b, 0.0, length, BASE_Z, EAVE_Z)
        continue
    spacing = length / (count + 1)
    centers = [spacing*(j+1) for j in range(count)]
    door_center = length * 0.5 if is_front else None
    if is_front:
        centers = [u for u in centers if abs(u-door_center) > 2.2]
    opening_w = 1.55 if is_front else 1.45
    openings = [(u-opening_w/2, u+opening_w/2) for u in centers]
    if is_front:
        openings.append((door_center-1.5, door_center+1.5))
    openings.sort()
    cursor=0.0
    for j,(lo,hi) in enumerate(openings):
        lo=max(cursor,lo); hi=min(length,hi)
        if lo>cursor+0.001:
            wall_panel("DDD_Wall_%02d_lower_%02d"%(idx,j),a,b,cursor,lo,BASE_Z,SECOND_FLOOR_TOP)
            wall_panel("DDD_Wall_%02d_upper_%02d"%(idx,j),a,b,cursor,lo,SECOND_FLOOR_TOP,EAVE_Z)
        if is_front and abs((lo+hi)/2-door_center)<0.25:
            # A paired entry opening; wingside wall remains continuous above.
            wall_panel("DDD_EntryHeader",a,b,lo,hi,2.85,SECOND_FLOOR_TOP)
            window_records.append(("door",idx,(lo+hi)/2,tangent,a))
        else:
            # Lower arched and upper rectangular window voids with masonry between.
            wall_panel("DDD_Spandrel_Low",a,b,lo,hi,BASE_Z,0.92)
            wall_panel("DDD_Spandrel_Mid",a,b,lo,hi,3.25,4.15)
            wall_panel("DDD_Spandrel_Upper",a,b,lo,hi,6.28,EAVE_Z)
            window_records.append(("window",idx,(lo+hi)/2,tangent,a))
        cursor=hi
    if cursor < length:
        wall_panel("DDD_Wall_%02d_end"%idx,a,b,cursor,length,BASE_Z,EAVE_Z)

# Belt courses and limestone water-table follow the outline.
extruded_ring("DDD_Foundation_Base", ring, 0.0, 0.38, stone)
for idx,a,b,length,tx,ty in ring_edges:
    # Exterior wall trim is slightly offset outwards for a clean visible course.
    nx,ny=-ty,tx  # FID 753 ring is clockwise, so the left normal is exterior.
    mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
    beam_between("DDD_Belt_%02d"%idx,(a[0]+nx*0.035,a[1]+ny*0.035,3.75),(b[0]+nx*0.035,b[1]+ny*0.035,3.75),0.10,0.12,stone)
    beam_between("DDD_Cornice_%02d"%idx,(a[0]+nx*0.04,a[1]+ny*0.04,7.82),(b[0]+nx*0.04,b[1]+ny*0.04,7.82),0.18,0.15,white)

# Windows and entry are inserted using each edge's own tangent and outward face.
for kind, idx, u, tangent, a in window_records:
    edge=next(e for e in ring_edges if e[0]==idx)
    _,ea,eb,length,tx,ty=edge
    nx,ny=-ty,tx  # FID 753 ring is clockwise, so the left normal is exterior.
    center=(ea[0]+tx*u+nx*0.09,ea[1]+ty*u+ny*0.09)
    if kind=="door":
        # Main pair of blue entry doors within a pale limestone portal.
        oriented_box("DDD_DoubleDoor",center,2.45,2.65,0.18,(tx,ty),1.70,door_mat)
        for s in (-1,1):
            c=(center[0]+tx*s*1.3,center[1]+ty*s*1.3)
            oriented_box("DDD_Entry_Jamb",c,0.22,3.0,0.28,(tx,ty),1.55,stone)
        oriented_box("DDD_Entry_Lintel",center,2.9,0.24,0.3,(tx,ty),3.08,stone)
        for s in (-1,1):
            oriented_box("DDD_Door_Leaf_%s"%s,(center[0]+tx*s*0.60,center[1]+ty*s*0.60),0.055,2.3,0.04,(tx,ty),1.7,metal)
    else:
        window("DDD_ArchedWindow_%02d_%.1f"%(idx,u),center,(tx,ty),0.95,1.42,2.05,True)
        window("DDD_UpperWindow_%02d_%.1f"%(idx,u),(center[0],center[1]),(tx,ty),4.33,1.34,1.72,False)

# Broad dark roof plate traces the official wall perimeter. Low-pitch hipped
# roof planes over the main residential block give the seen long gray shingle roof.
extruded_ring("DDD_RoofEdge",ring,EAVE_Z,EAVE_Z+0.12,roof,cap=False)
xs=[p[0] for p in ring]; ys=[p[1] for p in ring]
xmin,xmax=min(xs),max(xs); ymin,ymax=min(ys),max(ys)
roof_y0=ymin+4.3; roof_y1=ymax-4.0
roof_x0=xmin+4.2; roof_x1=xmax-4.2
ridge_y=(roof_y0+roof_y1)/2
ridge_z=RIDGE_Z
eave_z=EAVE_Z+0.16
roofverts=[(roof_x0,roof_y0,eave_z),(roof_x1,roof_y0,eave_z),(roof_x1,roof_y1,eave_z),(roof_x0,roof_y1,eave_z),
           (roof_x0+1.3,ridge_y,ridge_z),(roof_x1-1.3,ridge_y,ridge_z)]
rooffaces=[(0,1,5,4),(4,5,2,3),(0,4,3),(1,2,5)]
make_mesh("DDD_Main_HippedRoof",roofverts,rooffaces,roof)

# The photographed entrance is a formal round two-level portico with four white
# columns, a curved upper balcony, a round projecting entablature, and triangle mark.
fx,fy=front_mid
tx,ty=front_vec
nx,ny=normal_south
porch_x,porch_y=porch_center
portico_r=5.6
cyx,cyy=porch_x,porch_y
portico_r=5.6
cylinder("DDD_Portico_BalconySlab",(cyx,cyy,7.45),portico_r,0.38,stone,64)
cylinder("DDD_Portico_Crown",(cyx,cyy,8.10),portico_r+0.25,0.78,white,64)
cylinder("DDD_Portico_CrownTop",(cyx,cyy,8.54),portico_r+0.05,0.12,stone,64)
for i,xoff in enumerate((-3.9,-1.3,1.3,3.9)):
    px=porch_x+xoff
    py=porch_y-math.sqrt(max(0.0,(portico_r-0.75)**2-xoff*xoff))
    cylinder("DDD_Portico_ColumnBase_%d"%i,(px,py,0.63),0.52,0.30,stone)
    cylinder("DDD_Portico_Column_%d"%i,(px,py,4.08),0.32,6.7,white,24)
    cylinder("DDD_Portico_Capital_%d"%i,(px,py,7.42),0.50,0.30,white)

# curved balcony rail at the front half-circle, horizontal cap plus balusters.
for k in range(31):
    theta=math.pi*k/30
    px=cyx+tx*portico_r*math.cos(theta)+nx*portico_r*math.sin(theta)
    py=cyy+ty*portico_r*math.cos(theta)+ny*portico_r*math.sin(theta)
    cylinder("DDD_Baluster_%02d"%k,(px,py,8.08),0.055,0.98,white,8)
for z,name in ((7.65,"lower"),(8.49,"upper")):
    pts=[]
    for k in range(31):
        theta=math.pi*k/30
        pts.append((cyx+tx*portico_r*math.cos(theta)+nx*portico_r*math.sin(theta),
                    cyy+ty*portico_r*math.cos(theta)+ny*portico_r*math.sin(theta),z))
    for k in range(len(pts)-1):
        beam_between("DDD_BalconyRail_%s_%02d"%(name,k),pts[k],pts[k+1],0.12,0.10,white)

# Recessed two-storey glazed door bay and subtle ΔΔΔ emblem on the fascia.
entry_center=(porch_x,porch_y-3.7)
oriented_box("DDD_EntryDoubleDoor",entry_center,2.45,2.75,0.16,(1,0),1.75,door_mat)
for side in (-1,1):
    oriented_box("DDD_EntryPortalJamb_%d"%side,(entry_center[0]+side*1.34,entry_center[1]),
                 0.20,3.05,0.28,(1,0),1.60,stone)
oriented_box("DDD_EntryPortalLintel",entry_center,2.9,0.24,0.28,(1,0),3.18,stone)
for side in (-1,1):
    oriented_box("DDD_EntryDoorLeafLine_%d"%side,(entry_center[0]+side*0.60,entry_center[1]-0.08),
                 0.05,2.35,0.035,(1,0),1.76,metal)
for i in range(3):
    # Triangle motif approximated as slender white diagonals on the front fascia.
    px,py=cyx+(i-1)*0.62,cyy-portico_r-0.20
    basez=8.22
    beam_between("DDD_TriangleMark_L%d"%i,(px-tx*0.25,py-ty*0.25,basez),(px,py,basez+0.43),0.09,0.06,white)
    beam_between("DDD_TriangleMark_R%d"%i,(px,py,basez+0.43),(px+tx*0.25,py+ty*0.25,basez),0.09,0.06,white)

# Wide formal stairs down to Tower Drive; shallow rise and pale concrete cheeks.
stair_width=5.0
for i in range(10):
    z=2.58-i*0.17
    step_center=(porch_x,porch_y-(portico_r+0.65+i*0.42))
    step=cube("DDD_FrontStep_%02d"%i,(step_center[0],step_center[1],z),(stair_width,0.46,0.17),stone)
    step.rotation_euler[2]=math.atan2(ty,tx)
for s in (-1,1):
    rail_xy=(porch_x+s*(stair_width/2+0.25),porch_y-portico_r+0.1)
    for i in range(10):
        z=2.74-i*0.17
        step_center=(rail_xy[0],rail_xy[1]-(0.65+i*0.42))
        cheek=cube("DDD_StairCheek_%d_%02d"%(s,i),(step_center[0],step_center[1],z),(0.40,0.48,0.32),stone)
        cheek.rotation_euler[2]=math.atan2(ty,tx)
    # sloped metal guardrails along both sides of stairs
    beam_between("DDD_StairRail_%d"%s,(rail_xy[0],rail_xy[1]-0.55,2.85),(rail_xy[0],rail_xy[1]-4.45,1.18),0.075,0.075,metal)
    for i in range(7):
        px=rail_xy[0]; py=rail_xy[1]-0.8-i*0.52
        zz=2.74-i*0.22
        cylinder("DDD_RailPost_%d_%02d"%(s,i),(px,py,zz),0.035,0.55,metal,8)

# Visible common spaces and room partitions behind window openings, kept at
# subdued warm neutral materials. This is a schematic interior, not a floor plan.
floor_zs=(0.36,3.92,7.1)
for idx,z in enumerate(floor_zs):
    cube("DDD_InteriorFloor_%d"%idx,(0,0,z),(xmax-xmin-3.0,ymax-ymin-3.0,0.16),interior)
# Central entry hall across the middle of the house with connected open commons.
cube("DDD_InteriorHall_BackWall",(0,2.5,2.05),(17.0,0.16,3.2),interior)
cube("DDD_InteriorHall_LeftPartition",(-8.4,0.0,2.05),(0.16,8.5,3.2),interior)
cube("DDD_InteriorHall_RightPartition",(8.4,0.0,2.05),(0.16,8.5,3.2),interior)
cube("DDD_InteriorStair_LowerFlight",(0,0.2,1.9),(2.8,4.2,0.25),wood)
cube("DDD_InteriorStair_UpperFlight",(0,1.8,3.15),(2.8,4.2,0.25),wood)
for ix,x in enumerate((-5.3,-2.7,2.7,5.3)):
    cube("DDD_InteriorRoomPartition_%d"%ix,(x,6.4,5.45),(0.12,10.0,2.8),interior)
# Common-room furniture visible in the ground-floor glazing.
for ix,x in enumerate((-5.5,-2.4,2.4,5.5)):
    cube("DDD_LoungeTable_%d"%ix,(x,-4.6,0.95),(1.6,0.9,0.12),wood)
    for sx in (-0.55,0.55):
        for sy in (-0.28,0.28):
            cube("DDD_LoungeTableLeg_%d_%s_%s"%(ix,sx,sy),(x+sx,-4.6+sy,0.64),(0.09,0.09,0.55),wood)

# Add roof fascia and evenly spaced dormer-like roof vents where they sit clear
# of the portico; references do not establish operable dormers, so these are low
# profile roof ventilators rather than an asserted dormer count.
for i in range(7):
    px=xmin+6.0+i*((xmax-xmin-12.0)/6.0)
    cube("DDD_RoofVent_%02d"%i,(px,ridge_y-3.2,8.70),(0.5,0.34,0.28),roof,bevel=0.05)

# Place the original GIS coordinates in a named root empty for auditability; the
# collection geometry itself remains in the local frame and exports through it.
root=bpy.data.objects.new("AssetRoot_"+ASSET_ID,None)
asset.objects.link(root)
root.empty_display_type="PLAIN_AXES"
root.empty_display_size=0.8
root["source_fid"]=753
root["source_address"]=feature["properties"].get("ADDRESS","")
root["placement_origin_xy_m"]=ORIGIN_XY
root["local_coordinates"]=True

# A neutral studio camera renders the detailed library for review.
target=Vector((0,0,4.0))
cam_data=bpy.data.cameras.new("DDD_ReviewCamera")
cam=bpy.data.objects.new("DDD_ReviewCamera",cam_data)
presentation.objects.link(cam)
cam.location=(target.x+nx*88,target.y+ny*88,target.z+8.0)
direction=target-Vector(cam.location)
cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
cam_data.lens=54
scene.camera=cam
light_data=bpy.data.lights.new("DDD_KeyArea","AREA")
light=bpy.data.objects.new("DDD_KeyArea",light_data)
presentation.objects.link(light)
light.location=(target.x-nx*30-tx*18,target.y-ny*30-ty*18,26)
light.data.energy=14000
light.data.shape="DISK"
light.data.size=24
light.rotation_euler=(Vector((0,0,4))-Vector(light.location)).to_track_quat("-Z","Y").to_euler()
fill_data=bpy.data.lights.new("DDD_FillArea","AREA")
fill=bpy.data.objects.new("DDD_FillArea",fill_data)
presentation.objects.link(fill)
fill.location=(30,18,24)
fill.data.energy=8500
fill.data.size=18
fill.rotation_euler=(Vector((0,0,4))-Vector(fill.location)).to_track_quat("-Z","Y").to_euler()
scene.world.use_nodes=True
world_bg=next(n for n in scene.world.node_tree.nodes if n.type=="BACKGROUND")
world_bg.inputs["Color"].default_value=(0.50,0.56,0.64,1.0)
world_bg.inputs["Strength"].default_value=0.8
engine_ids=[item.identifier for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
scene.render.engine=next((value for value in engine_ids if "EEVEE" in value), engine_ids[0])
scene.render.resolution_x=1500
scene.render.resolution_y=950
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.filepath=os.path.join(OUT_DIR,"delta_delta_delta_front.png")
scene.view_settings.view_transform="AgX"
scene.render.film_transparent=False

# Pack and save only this source asset. Presentation camera/lights are outside
# the exported collection and will not be linked into the campus master.
bpy.ops.wm.save_as_mainfile(filepath=ASSET_PATH)
bpy.ops.render.render(write_still=True)
print("DELTA_DELTA_DELTA_BUILD_COMPLETE", json.dumps({
    "asset": ASSET_PATH,
    "collection": COLLECTION_NAME,
    "scene": SCENE_NAME,
    "object_count": len(asset.objects),
    "gis_vertex_count": len(ring),
    "campus_origin_xy_m": ORIGIN_XY,
    "local_bounds_xy_m": [min(xs), max(xs), min(ys), max(ys)],
    "estimated_height_m": RIDGE_Z,
    "front_edge_index": front_idx[0],
    "front_edge_length_m": front_edge_length,
    "front_edge_mid_local_m": front_mid,
}))
