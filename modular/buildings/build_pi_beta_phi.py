"""Build the Pi Beta Phi (FID 774) Purdue chapter house as a detailed library.

The GIS ring supplies the XY shell. Stories, roof, and interior are visual
reconstruction estimates because no measured elevations or floor plans were
located. Run with Blender 5.2:
  blender -b --python modular/buildings/build_pi_beta_phi.py
"""
import bpy
import json
import math
import os
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSET_ID = "massing_house_301838781_891384f"
ASSET_PATH = os.path.join(ROOT, "modular", "buildings", ASSET_ID + ".blend")
SOURCE = os.path.join(ROOT, "audit", "pi_beta_phi", "sources", "purdue_arcgis_fids_774_841_wgs84.json")
AUDIT = os.path.join(ROOT, "audit", "pi_beta_phi")
ORIGIN = (-429.57778493112545, -311.88038117902056)
bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name, color, roughness=0.8, metallic=0.0, brick=False):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if brick:
        tex = nodes.new("ShaderNodeTexBrick")
        tex.inputs["Color1"].default_value = (0.32, 0.073, 0.038, 1)
        tex.inputs["Color2"].default_value = (0.48, 0.13, 0.066, 1)
        tex.inputs["Mortar"].default_value = (0.24, 0.22, 0.19, 1)
        tex.inputs["Scale"].default_value = 1.0
        tex.inputs["Mortar Size"].default_value = 0.015
        tex.inputs["Mortar Smooth"].default_value = 0.01
        coord = nodes.new("ShaderNodeTexCoord")
        links.new(coord.outputs["UV"], tex.inputs["Vector"])
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.18
        bump.inputs["Distance"].default_value = 0.035
        links.new(tex.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


BRICK = material("PiPhi warm red brick", (0.38, 0.1, 0.052), brick=True)
LIMESTONE = material("PiPhi painted white trim", (0.83, 0.81, 0.75), 0.58)
ROOF = material("PiPhi charcoal roof membrane", (0.105, 0.12, 0.14), 0.68)
GLASS = material("PiPhi blue gray glazing", (0.055, 0.13, 0.17), 0.23, 0.12)
WOOD = material("PiPhi dark walnut", (0.19, 0.085, 0.039), 0.52)
FLOOR = material("PiPhi interior oak flooring", (0.36, 0.21, 0.11), 0.65)
CARPET = material("PiPhi blue gray carpet", (0.20, 0.26, 0.31), 0.96)
METAL = material("PiPhi dark iron", (0.07, 0.075, 0.08), 0.36, 0.62)
GREEN = material("PiPhi planting green", (0.08, 0.22, 0.07), 0.95)


def mesh_obj(name, verts, faces, mat, collection, smooth=False):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    collection.objects.link(ob)
    if smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    return ob


def cube(name, loc, scale, mat, collection, bevel=0.0, rot=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = scale
    ob.rotation_euler[2] = rot
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    collection.objects.link(ob)
    ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new("Soft masonry edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        ob.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return ob


def cylinder(name, loc, radius, depth, mat, collection, vertices=20, rot=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    ob = bpy.context.object
    ob.name = name
    if rot:
        ob.rotation_euler = rot
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    collection.objects.link(ob)
    ob.data.materials.append(mat)
    if vertices > 12:
        for p in ob.data.polygons:
            if len(p.vertices) == 4:
                p.use_smooth = True
    return ob


def uv_sphere(name, loc, scale, mat, collection):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    collection.objects.link(ob)
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def make_text(name, body, loc, size, mat, collection, rotation=(math.pi / 2, 0, 0)):
    cu = bpy.data.curves.new(name + "Curve", "FONT")
    cu.body = body
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.size = size
    cu.extrude = 0.004
    ob = bpy.data.objects.new(name, cu)
    collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rotation
    cu.materials.append(mat)
    return ob


def build_shell(collection, ring):
    pts = [(p[0] - ORIGIN[0], p[1] - ORIGIN[1]) for p in ring]
    if pts[0] == pts[-1]:
        pts.pop()
    n = len(pts)
    wall_h = 7.25
    verts = [(x, y, z) for z in (0.0, wall_h) for x, y in pts]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    # Blender accepts a concave n-gon and triangulates it for evaluation.
    faces.append(tuple(range(n, 2*n)))
    shell = mesh_obj("PiPhi_FID774_structural_shell", verts, faces, BRICK, collection)
    uv = shell.data.uv_layers.new(name="FacadeBrickCourses")
    for poly in shell.data.polygons:
        if poly.index < n:
            i = poly.index
            a, b = pts[i], pts[(i+1)%n]
            length = math.hypot(b[0]-a[0], b[1]-a[1])
            coords = ((0,0),(length,0),(length,wall_h),(0,wall_h))
            for loop_index, co in zip(poly.loop_indices, coords):
                uv.data[loop_index].uv = co
        else:
            for loop_index in poly.loop_indices:
                uv.data[loop_index].uv = (0,0)
    shell["GIS_FID"] = 774
    shell["footprint_source"] = "Purdue BuildingShapesZip4 FeatureServer/0, FID 774"
    shell["footprint_accuracy"] = "GIS ring reproduced in local coordinates; source polygon is not a survey"
    return pts, wall_h, shell


def add_roof_and_trim(collection, pts, wall_h):
    # The current street view shows a white continuous top cornice/parapet.
    # The screened flat roof behind it is a conservative reconstruction.
    n = len(pts)
    z0, z1 = wall_h, wall_h + 0.72
    verts = [(x, y, z) for z in (z0, z1) for x, y in pts]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    mesh_obj("PiPhi_white_perimeter_cornice", verts, faces, LIMESTONE, collection)
    # Recessed-looking top surface follows the source footprint and remains
    # intentionally flat until roof plans can support a more exact silhouette.
    topverts = [(x, y, z1 + 0.05) for x, y in pts]
    roof_faces = [tuple(range(len(pts)))]
    mesh_obj("PiPhi_flat_roof_surface_estimated", topverts, roof_faces, ROOF, collection)


def add_window(collection, center, tangent, normal, z, width=1.28, height=1.65, label="window"):
    # Window plane with painted limestone reveal, projecting frame and mullions.
    t = Vector((tangent[0], tangent[1], 0)).normalized()
    n = Vector((normal[0], normal[1], 0)).normalized()
    c = Vector((center[0], center[1], z))
    def point(u, v, depth=0.0):
        q = c + t * u + Vector((0, 0, v)) + n * depth
        return tuple(q)
    pane_verts = [point(-width/2, -height/2, 0.045), point(width/2, -height/2, 0.045), point(width/2, height/2, 0.045), point(-width/2, height/2, 0.045)]
    mesh_obj(label + "_glazing", pane_verts, [(0, 1, 2, 3)], GLASS, collection)
    frame = 0.09
    for u in (-width/2-frame/2, width/2+frame/2):
        cube(label + "_jamb", point(u, 0, 0.10), (frame, 0.13, height+0.18), LIMESTONE, collection, 0.02, math.atan2(t.y, t.x))
    for v in (-height/2-frame/2, height/2+frame/2):
        cube(label + "_sill_lintel", point(0, v, 0.10), (width+0.18, 0.13, frame), LIMESTONE, collection, 0.018, math.atan2(t.y, t.x))
    cube(label + "_mullion", point(0, 0, 0.12), (0.055, 0.075, height), LIMESTONE, collection, 0.01, math.atan2(t.y, t.x))
    cube(label + "_midrail", point(0, 0, 0.12), (width, 0.06, 0.05), LIMESTONE, collection, 0.01, math.atan2(t.y, t.x))


def add_facade_windows(collection, pts, wall_h):
    # Avoid very short GIS jogs. Windows are spaced along actual source walls.
    n = len(pts)
    signed_area = sum(pts[i][0]*pts[(i+1)%n][1]-pts[(i+1)%n][0]*pts[i][1] for i in range(n)) * 0.5
    for i, a in enumerate(pts):
        b = pts[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length < 2.25:
            continue
        t = (dx / length, dy / length)
        # For CCW rings interior is left; for CW rings interior is right.
        normal = (dy / length, -dx / length) if signed_area > 0 else (-dy / length, dx / length)
        count = max(1, int(length // 3.7))
        # Rows match two occupied stories and a smaller high attic-level band.
        rows = [(1.55, 1.68), (4.55, 1.68)]
        for row_idx, (z, h) in enumerate(rows):
            for k in range(count):
                d = length * (k + 0.5) / count
                c = (a[0] + t[0]*d + normal[0]*0.03, a[1] + t[1]*d + normal[1]*0.03)
                add_window(collection, c, t, normal, z, width=min(1.38, length/count*0.55), height=h, label=f"PiPhi_facade_{i}_{row_idx}_{k}")
        # Compact upper openings sit below the white roof band.
        for k in range(max(1, count - 1)):
            d = length * (k + 1) / (count + 1)
            c = (a[0] + t[0]*d + normal[0]*0.04, a[1] + t[1]*d + normal[1]*0.04)
            add_window(collection, c, t, normal, 6.58, width=min(0.95, length/count*0.38), height=0.82, label=f"PiPhi_attic_{i}_{k}")


def add_main_entry(collection):
    # Southern State Street elevation from March 2026 Google Street View:
    # red brick, pale projecting classical portico, central door, symmetric
    # window rhythm and a raised walk/steps.
    # GIS FID 774 places the main entrance projection near x=-430/y=-331.
    x0 = -431.5 - ORIGIN[0]
    yfront = -332.9 - ORIGIN[1]
    width = 8.5
    cube("PiPhi_entry_portico_entablature", (x0, yfront + 0.20, 6.95), (width, 1.0, 0.42), LIMESTONE, collection, 0.08)
    cube("PiPhi_entry_portico_architrave", (x0, yfront + 0.20, 6.62), (width+0.32, 1.22, 0.16), LIMESTONE, collection, 0.035)
    # Four clean classical columns with fluted shafts, bases and capitals.
    for j, dx in enumerate((-3.55, -1.18, 1.18, 3.55)):
        x, y = x0 + dx, yfront + 0.27
        cylinder(f"PiPhi_portico_column_{j}_shaft", (x, y, 3.38), 0.23, 6.35, LIMESTONE, collection, 24)
        cylinder(f"PiPhi_portico_column_{j}_base", (x, y, 0.20), 0.37, 0.28, LIMESTONE, collection, 24)
        cylinder(f"PiPhi_portico_column_{j}_capital", (x, y, 6.60), 0.38, 0.30, LIMESTONE, collection, 24)
        for flute in range(8):
            ang = flute * math.tau / 8
            cylinder(f"PiPhi_column_flute_{j}_{flute}", (x+math.cos(ang)*0.225, y+math.sin(ang)*0.225, 3.36), 0.018, 5.8, LIMESTONE, collection, 8)
    # Centered double entry doors with a transom and sidelights.
    door_y = yfront + 0.07
    cube("PiPhi_main_door_pair", (x0, door_y, 1.48), (2.45, 0.18, 2.95), WOOD, collection, 0.04)
    cube("PiPhi_door_transom", (x0, door_y - 0.01, 3.12), (2.55, 0.12, 0.42), GLASS, collection, 0.025)
    for dx in (-1.53, 1.53):
        cube("PiPhi_entry_sidelight", (x0+dx, door_y - 0.03, 1.70), (0.36, 0.11, 2.42), GLASS, collection, 0.02)
        cube("PiPhi_entry_sidelight_trim", (x0+dx, door_y - 0.10, 1.70), (0.47, 0.10, 2.55), LIMESTONE, collection, 0.02)
    make_text("PiPhi_house_letters", "Π Β Φ", (x0, yfront-0.34, 6.98), 0.55, LIMESTONE, collection)
    make_text("PiPhi_address", "1012", (x0, yfront-0.35, 3.64), 0.28, LIMESTONE, collection)
    # Curved second-storey balcony rail above the entry; low-key, as in the
    # published chapter-house illustration. Its exact radius is unverified.
    radius = 3.7
    arc = []
    for k in range(17):
        theta = math.pi + math.pi*k/16
        arc.append((x0 + radius*math.cos(theta), yfront - 0.52 - 0.55*math.sin(theta), 6.0))
    for k in range(len(arc)-1):
        a, b = arc[k], arc[k+1]
        mid = ((a[0]+b[0])/2, (a[1]+b[1])/2, 6.20)
        dx, dy = b[0]-a[0], b[1]-a[1]
        length = math.hypot(dx,dy)
        cube("PiPhi_balcony_rail_segment", mid, (length+0.04, 0.10, 0.22), LIMESTONE, collection, 0.018, math.atan2(dy,dx))
    for k, p in enumerate(arc[::2]):
        cylinder(f"PiPhi_baluster_{k}", (p[0],p[1],5.88), 0.045, 0.42, LIMESTONE, collection, 10)
    # Entry stair and landing.
    cube("PiPhi_entry_landing", (x0, yfront-0.68, 0.16), (9.3, 2.15, 0.30), LIMESTONE, collection, 0.06)
    for i in range(6):
        y = yfront - 1.85 - i*0.43
        z = max(0.075, 0.21-i*0.025)
        cube(f"PiPhi_entry_step_{i+1}", (x0, y, z), (9.2+i*0.25, 0.56, 0.16), LIMESTONE, collection, 0.025)


def add_roof_detail(collection, pts):
    # Screened flat roof mechanical units and roof lights are modest estimates.
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
    cube("PiPhi_roof_hatch", (cx+3.2, cy+2.4, 7.8), (1.25, 1.1, 0.38), LIMESTONE, collection, 0.04)
    for j in range(3):
        cube(f"PiPhi_roof_vent_{j}", (cx-4+j*2.2, cy+1.4, 7.68), (0.9, 0.7, 0.42), METAL, collection, 0.05)


def add_interior(collection, pts):
    # No floor plans were located. This arrangement is explicitly conceptual;
    # documented room types guide the objects but not the exact room positions.
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
    for level, z in enumerate((0.20, 3.18, 6.16)):
        # The floor plates follow a generous main rectangle. The GIS-derived
        # perimeter shell remains authoritative; floor plan is only a visual cutaway aid.
        cube(f"PiPhi_interior_floor_{level+1}", (cx,cy,z), (20.5,27.5,0.16), FLOOR if level==0 else CARPET, collection)
    for level, z in enumerate((0.0,2.98,5.96)):
        # Hallway partitions/doors, intentionally sparse to avoid claiming a
        # precise room plan. The interior can be read from a cutaway view.
        cube(f"PiPhi_hall_partition_{level}_west", (cx-6.4,cy,z+1.35), (0.14,10.0,2.7), LIMESTONE, collection)
        cube(f"PiPhi_hall_partition_{level}_east", (cx+6.5,cy,z+1.35), (0.14,10.0,2.7), LIMESTONE, collection)
        for side in (-1,1):
            for room in range(2):
                yy = cy - 7.6 + room*8.2
                cube(f"PiPhi_room_partition_{level}_{side}_{room}", (cx+side*3.1,yy,z+1.32), (6.3,0.12,2.64), LIMESTONE, collection)
                # Doors held open so the rooms remain visible in an interior view.
                cube(f"PiPhi_room_door_{level}_{side}_{room}", (cx+side*3.1,yy-0.05,z+1.0), (0.88,0.10,2.05), WOOD, collection, 0.025)
    # First-floor chapter-house dining / library / lounge furniture cues.
    z=0.42
    for i in range(3):
        yy=cy-2.8+i*2.25
        cube(f"PiPhi_dining_table_{i}",(cx-3.7,yy,z+0.42),(2.8,1.05,0.10),WOOD,collection,0.035)
        for dx in (-1.0,1.0):
            for dy in (-0.58,0.58):
                cube(f"PiPhi_dining_chair_{i}_{dx}_{dy}",(cx-3.7+dx,yy+dy,z+0.23),(0.44,0.42,0.78),WOOD,collection,0.035)
    # Study room desks and bookcases, prompted by the chapter-house campaign.
    for i in range(3):
        yy=cy+4.1+i*1.65
        cube(f"PiPhi_study_desk_{i}",(cx+3.6,yy,z+0.42),(2.0,0.78,0.08),WOOD,collection,0.03)
        for k in range(3):
            cube(f"PiPhi_library_shelf_{i}_{k}",(cx+7.3,yy-0.65+k*0.35,z+0.85),(0.75,0.10,0.12),WOOD,collection,0.015)
    cube("PiPhi_kitchen_island",(cx+4.0,cy-6.1,z+0.53),(4.8,1.05,1.0),LIMESTONE,collection,0.06)
    for i in range(4):
        cube(f"PiPhi_kitchen_cabinet_{i}",(cx+6.6+i*0.82,cy-7.9,z+1.0),(0.74,0.55,1.8),WOOD,collection,0.04)
    cube("PiPhi_lounge_rug",(cx-7.1,cy-8.0,z+0.095),(5.8,4.0,0.04),CARPET,collection,0.02)
    for i in range(3):
        cube(f"PiPhi_lounge_seating_{i}",(cx-7.4+i*1.8,cy-7.0,z+0.46),(1.5,0.72,0.75),WOOD,collection,0.09)
    cube("PiPhi_lounge_coffee_table",(cx-7.0,cy-8.5,z+0.38),(2.2,1.05,0.22),WOOD,collection,0.05)
    # Upper residential floors use small, consistent beds as a concept, not a
    # claim about exact room count or furniture positions.
    for floor_no, z0 in ((2,3.35),(3,6.33)):
        for side in (-1,1):
            for j in range(3):
                x=cx+side*(8.2+j*0.12)
                y=cy-7.8+j*6.7
                cube(f"PiPhi_bed_{floor_no}_{side}_{j}",(x,y,z0+0.20),(1.0,2.0,0.30),LIMESTONE,collection,0.06)
                cube(f"PiPhi_headboard_{floor_no}_{side}_{j}",(x,y-0.85,z0+0.62),(1.05,0.10,0.62),WOOD,collection,0.035)


def add_lighting_camera(scene, center):
    # Product-style cameras and lights are omitted from the exported asset. The
    # render script below generates views with a separate temporary scene setup.
    pass


def main():
    with open(SOURCE, encoding="utf-8-sig") as f:
        src = json.load(f)
    feature = next(f for f in src["features"] if f["attributes"]["FID"] == 774)
    # outSR=4326 gives explicit WGS84 longitude/latitude coordinates.
    ring_ll = feature["geometry"]["rings"][0]
    ring_xy = []
    for lon, lat in ring_ll:
        x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
        y = (lat - 40.4274) * 111040.0
        ring_xy.append((x,y))
    # Rebuild the individual asset file from scratch while preserving the scene,
    # asset collection, object name, ID, and expected library path.
    scene = bpy.context.scene
    scene.name = "Building_" + ASSET_ID
    asset = bpy.data.collections.new("Asset_" + ASSET_ID)
    scene.collection.children.link(asset)
    asset["building_name"] = "Pi Beta Phi"
    asset["GIS_FID"] = 774
    asset["coordinate_frame"] = "Local geometry relative to official FID 774 polygon centroid; master Placement marker supplies campus XY"
    local_ring, wall_h, shell = build_shell(asset, ring_xy)
    add_roof_and_trim(asset, local_ring, wall_h)
    add_facade_windows(asset, local_ring, wall_h)
    add_main_entry(asset)
    add_roof_detail(asset, local_ring)
    add_interior(asset, local_ring)
    # Preserve the historic object name for source-object crosswalk tooling.
    shell.name = "House_301838781"
    # Pack no external images are used; every surface is procedural/material-based.
    scene.render.engine = "BLENDER_EEVEE"
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    # A neutral dark blue-gray world makes brick and limestone read clearly.
    world = bpy.data.worlds.new("PiPhi render world")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.22,0.28,0.36,1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45
    # Model evidence properties for the root integration step.
    asset["placement_origin_xy_m"] = list(ORIGIN)
    bpy.context.view_layer.update()
    all_points = [ob.matrix_world @ vert.co for ob in asset.objects if ob.type == "MESH" for vert in ob.data.vertices]
    asset["local_bounds_xyz_m"] = [[min(p[i] for p in all_points), max(p[i] for p in all_points)] for i in range(3)]
    asset["local_footprint_bounds_xy_m"] = [
        [min(x for x,y in local_ring), max(x for x,y in local_ring)],
        [min(y for x,y in local_ring), max(y for x,y in local_ring)],
    ]
    os.makedirs(os.path.dirname(ASSET_PATH), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=ASSET_PATH)
    print(json.dumps({"saved":ASSET_PATH,"scene":scene.name,"collection":asset.name,"objects":len(asset.objects),"origin_xy_m":ORIGIN,"footprint_vertices":len(local_ring),"wall_height_estimate_m":wall_h},indent=2))


if __name__ == "__main__":
    main()
