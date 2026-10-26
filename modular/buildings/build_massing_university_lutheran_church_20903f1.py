"""Build a detailed, portable University Lutheran Church library asset.

Footprint coordinates come from OSM way 301932784 and use the project's local
campus conversion. Exterior appearance follows official ULu imagery; floor plans
and height beyond the documented room uses are schematic estimates.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_university_lutheran_church_20903f1"
COLLECTION_NAME = "Asset_" + ASSET_ID
SCENE_NAME = "Building_" + ASSET_ID
ASSET_PATH = ROOT / "modular" / "buildings" / (ASSET_ID + ".blend")
EVIDENCE_DIR = ROOT / "audit" / "university_lutheran_church"
OSM_PATH = EVIDENCE_DIR / "sources" / "osm_way_301932784.json"
ROAD_PATH = EVIDENCE_DIR / "sources" / "osm_northwestern_avenue_way_932656636.json"

LAT0, LON0 = 40.4274, -86.9137
WALL_BOTTOM = -2.6
FLOOR_TOPS = [-2.6, 0.0, 3.8, 7.45, 11.05]
ROOF_Z = 12.75
PARAPET_Z = 13.45


def campus_xy(lat, lon):
    return ((lon - LON0) * 111412.84 * math.cos(math.radians(LAT0)),
            (lat - LAT0) * 111040.0)


def make_material(name, color, roughness=0.7):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return mat, bsdf, nodes, links


def brick_material():
    mat, bsdf, nodes, links = make_material("ULu | mixed red-brown brick", (0.34, 0.12, 0.075), 0.86)
    tex = nodes.new("ShaderNodeTexBrick")
    tex.inputs["Color1"].default_value = (0.43, 0.18, 0.12, 1)
    tex.inputs["Color2"].default_value = (0.25, 0.09, 0.055, 1)
    tex.inputs["Mortar"].default_value = (0.55, 0.50, 0.43, 1)
    tex.inputs["Scale"].default_value = 1.0
    tex.inputs["Brick Width"].default_value = 0.42
    tex.inputs["Row Height"].default_value = 0.21
    tex.inputs["Mortar Size"].default_value = 0.014
    tex.inputs["Mortar Smooth"].default_value = 0.006
    uv = nodes.new("ShaderNodeTexCoord")
    links.new(uv.outputs["UV"], tex.inputs["Vector"])
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 95.0
    noise.inputs["Detail"].default_value = 2.0
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.025
    links.new(uv.outputs["UV"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


BRICK = brick_material()
STONE, _, _, _ = make_material("ULu | pale limestone bands", (0.68, 0.63, 0.53), 0.75)
ROOF, roof_bsdf, roof_nodes, roof_links = make_material("ULu | charcoal standing-seam roof", (0.07, 0.085, 0.09), 0.48)
roof_bsdf.inputs["Metallic"].default_value = 0.35
GLASS, glass_bsdf, _, _ = make_material("ULu | dark blue-gray insulated glazing", (0.035, 0.075, 0.10), 0.18)
glass_bsdf.inputs["Metallic"].default_value = 0.27
FRAME, _, _, _ = make_material("ULu | charcoal aluminum frames", (0.055, 0.065, 0.065), 0.48)
INTERIOR, _, _, _ = make_material("ULu | warm interior wall paint", (0.78, 0.74, 0.64), 0.82)
FLOOR, _, _, _ = make_material("ULu | interior concrete and carpet", (0.38, 0.34, 0.29), 0.92)
WOOD, _, _, _ = make_material("ULu | oak furniture", (0.31, 0.16, 0.075), 0.68)
SIGN, sign_bsdf, _, _ = make_material("ULu | warm white signage", (0.91, 0.89, 0.78), 0.42)
SIGN_EMISSION = sign_bsdf.inputs.get("Emission Color")
if SIGN_EMISSION:
    SIGN_EMISSION.default_value = (0.48, 0.43, 0.30, 1)


def link_obj(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    asset_collection.objects.link(obj)
    return obj


def add_mesh(name, verts, faces, material, uvs=None, smooth=False):
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    asset_collection.objects.link(obj)
    if uvs:
        layer = mesh.uv_layers.new(name="Physical-scale UV")
        for poly, uvcoords in zip(mesh.polygons, uvs):
            for loop_index, uv in zip(poly.loop_indices, uvcoords):
                layer.data[loop_index].uv = uv
    if smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    return obj


def tri_indices(points):
    return tessellate_polygon([[Vector((p[0], p[1], 0.0)) for p in points]])


def add_polygon_plate(name, points, z0, z1, material, roof_material=None):
    verts, faces, uvs = [], [], []
    n = len(points)
    verts.extend([(x,y,z0) for x,y in points])
    verts.extend([(x,y,z1) for x,y in points])
    # Shared perimeter vertices produce a closed shell rather than disconnected wall panels.
    for i, a in enumerate(points):
        b = points[(i + 1) % n]
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        faces.append((i, (i+1)%n, (i+1)%n+n, i+n))
        uvs.append([(0, 0), (length, 0), (length, z1 - z0), (0, z1 - z0)])
    # Both horizontal caps are triangulated so the concave GIS ring never self-fills.
    coords = tri_indices(points)
    for tri in coords:
        idx = [int(v) for v in tri]
        faces.append(tuple(i+n for i in idx))
        uvs.append([(points[i][0], points[i][1]) for i in idx])
    for tri in coords:
        idx = [int(v) for v in tri]
        faces.append(tuple(reversed(idx)))
        uvs.append([(points[i][0], points[i][1]) for i in reversed(idx)])
    obj = add_mesh(name, verts, faces, material, uvs)
    if roof_material:
        obj.data.materials.append(roof_material)
        for p in obj.data.polygons:
            if n <= p.index < n + len(coords):
                p.material_index = 1
    return obj


def basis_for_edge(a, b, center):
    tangent = Vector((b[0] - a[0], b[1] - a[1], 0)).normalized()
    normal = Vector((tangent.y, -tangent.x, 0))
    midpoint = Vector(((a[0] + b[0]) * .5, (a[1] + b[1]) * .5, 0))
    inward = Vector((center[0] - midpoint.x, center[1] - midpoint.y, 0))
    if normal.dot(inward) > 0:
        normal.negate()
    return tangent, normal


def create_box(name, center, dims, tangent=None, normal=None, material=BRICK, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    if tangent is not None and normal is not None:
        up = Vector((0, 0, 1))
        rot = Matrix((tangent, normal, up)).transposed().to_4x4()
        obj.rotation_euler = rot.to_euler()
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_obj(obj)
    obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new("small softened edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return obj


def point_on_side(a, tangent, normal, distance, out, z):
    return Vector((a[0], a[1], z)) + tangent * distance + normal * out


def add_window(name, a, tangent, normal, edge_length, ucenter, zcenter, width, height):
    center = point_on_side(a, tangent, normal, ucenter, 0.11, zcenter)
    # Glazing, metal perimeter, and mullions are offset in front of the brick shell.
    create_box(name + " dark glass", center, (width, 0.075, height), tangent, normal, GLASS, 0.018)
    bar = 0.085
    for v in (-width / 2, width / 2):
        c = point_on_side(a, tangent, normal, ucenter + v, 0.17, zcenter)
        create_box(name + " jamb", c, (bar, 0.13, height + 0.10), tangent, normal, FRAME, 0.01)
    for zoff in (-height / 2, height / 2):
        c = point_on_side(a, tangent, normal, ucenter, 0.17, zcenter + zoff)
        create_box(name + " head or sill", c, (width + 0.1, 0.13, bar), tangent, normal, STONE, 0.01)
    mullions = 3 if width > 2.8 else 1
    for i in range(1, mullions + 1):
        c = point_on_side(a, tangent, normal, ucenter - width / 2 + width * i / (mullions + 1), 0.18, zcenter)
        create_box(name + " vertical mullion", c, (0.055, 0.15, height - 0.06), tangent, normal, FRAME)
    c = point_on_side(a, tangent, normal, ucenter, 0.18, zcenter)
    create_box(name + " transom", c, (width - 0.06, 0.15, 0.055), tangent, normal, FRAME)


def add_text(name, body, pos, tangent, normal, size, material, extrude=0.012):
    cu = bpy.data.curves.new(name + " lettering", "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.bevel_depth = 0.004
    obj = bpy.data.objects.new(name, cu)
    asset_collection.objects.link(obj)
    # Text local X follows the facade, local Y stays vertical and local Z points outward.
    up = Vector((0, 0, 1))
    obj.rotation_euler = Matrix((tangent, up, normal)).transposed().to_4x4().to_euler()
    obj.location = pos
    obj.data.materials.append(material)
    return obj


def add_partition(name, p0, p1, z0, z1, thickness=0.14, material=INTERIOR):
    a, b = Vector(p0), Vector(p1)
    direction = (b - a).normalized()
    side = Vector((-direction.y, direction.x, 0))
    return create_box(name, (a + b) * .5 + Vector((0, 0, (z0 + z1) * .5)),
                      ((b - a).length, thickness, z1 - z0), direction, side, material, 0.015)


def point_inside(poly, x, y):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def furnish_box_local(name, anchor, tangent, inward, u, v, z, dims, mat):
    p = Vector((anchor[0], anchor[1], z)) + tangent * u + inward * v
    return create_box(name, p, dims, tangent, inward, mat, 0.035)


def main():
    if not OSM_PATH.exists():
        raise FileNotFoundError(OSM_PATH)
    data = json.loads(OSM_PATH.read_text(encoding="utf-8"))
    way = next(e for e in data["elements"] if e["type"] == "way" and e["id"] == 301932784)
    nodes = {e["id"]: e for e in data["elements"] if e["type"] == "node"}
    ring = [campus_xy(nodes[i]["lat"], nodes[i]["lon"]) for i in way["nodes"][:-1]]
    ring = [(float(x), float(y)) for x, y in ring]
    center = (sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring))

    # Identify the road-facing frontage from the nearby OSM Northwestern Avenue way.
    # This avoids selecting the longest side when it faces away from the street.
    rd = json.loads(ROAD_PATH.read_text(encoding="utf-8"))
    road_way = next(e for e in rd["elements"] if e["type"] == "way" and e["id"] == 932656636)
    road_nodes = {e["id"]: e for e in rd["elements"] if e["type"] == "node"}
    road_pts = [campus_xy(road_nodes[i]["lat"], road_nodes[i]["lon"]) for i in road_way["nodes"]]
    road_segments = [(Vector((a[0],a[1],0)), Vector((b[0],b[1],0))) for a,b in zip(road_pts,road_pts[1:])]
    front_faces = []
    road_edge_stats = []
    for i,a in enumerate(ring):
        b=ring[(i+1)%len(ring)]
        tangent,normal=basis_for_edge(a,b,center)
        mid=Vector(((a[0]+b[0])*0.5,(a[1]+b[1])*0.5,0))
        choices=[]
        for ra,rb in road_segments:
            roadvec=(rb-ra).normalized()
            segment=rb-ra
            t=max(0.0,min(1.0,(mid-ra).dot(segment)/(segment.length_squared or 1.0)))
            nearest=ra+segment*t
            toward=(nearest-mid)
            choices.append((toward.length,abs(tangent.dot(roadvec)),normal.dot(toward.normalized()) if toward.length else -1.0))
        distance,alignment,facing=min(choices,key=lambda x:x[0])
        road_edge_stats.append({"index":i,"distance_m":distance,"parallel_alignment":alignment,"faces_road":facing})
        if alignment >= 0.90 and facing >= 0.45:
            front_faces.append(i)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.collections, bpy.data.meshes, bpy.data.cameras, bpy.data.lights, bpy.data.curves):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)
    global asset_collection
    asset_collection = bpy.data.collections.new(COLLECTION_NAME)
    bpy.context.scene.collection.children.link(asset_collection)
    scene = bpy.context.scene
    scene.name = SCENE_NAME

    add_polygon_plate("ULu | brick building envelope and sloped roof", ring, WALL_BOTTOM, ROOF_Z, BRICK, ROOF)
    # Exposed roof field and high-low parapet profile follow the photo's broken roofline.
    roof_coords = tri_indices(ring)
    roof_verts, roof_faces = [], []
    for tri in roof_coords:
        ids = []
        for index in tri:
            p = ring[int(index)]
            ids.append(len(roof_verts))
            # Very shallow drainage fall (estimated) toward the rear.
            roof_verts.append((p[0], p[1], ROOF_Z + 0.16 * ((p[1] - center[1]) / 30.0)))
        roof_faces.append(tuple(ids))
    roof_obj = add_mesh("ULu | low-slope standing-seam roof", roof_verts, roof_faces, ROOF)
    solid = roof_obj.modifiers.new("roof thickness", "SOLIDIFY")
    solid.thickness = 0.12

    # Foundation/ground-level plinth and interior floor slabs.
    for z, label in [(-2.55, "basement"), (0.0, "ground"), (3.8, "second"), (7.45, "third")]:
        add_polygon_plate("ULu | " + label + " floor slab", ring, z - 0.12, z, FLOOR)

    # Stepped parapet caps: photo confirms low-pitched roof and uneven roof edge.
    for i, a in enumerate(ring):
        b = ring[(i + 1) % len(ring)]
        length = math.dist(a, b)
        if length < 1.7:
            continue
        tangent, normal = basis_for_edge(a, b, center)
        ztop = PARAPET_Z + (0.42 if i in (14, 15) else (0.18 if i in (0, 3, 8, 11) else 0.0))
        create_box("ULu | roof parapet segment", ((a[0]+b[0])/2, (a[1]+b[1])/2, (ROOF_Z+ztop)/2),
                   (length+0.08, 0.28, ztop-ROOF_Z), tangent, normal, BRICK, 0.025)
        create_box("ULu | metal coping", ((a[0]+b[0])/2, (a[1]+b[1])/2, ztop+0.035),
                   (length+0.16, 0.38, 0.07), tangent, normal, ROOF, 0.02)

    # Facade bands, brick recess modules, windows, and storefronts on each GIS edge.
    # Group contiguous, collinear road-facing ring segments into full window bays.
    # The ULu outline has three broad street-facing wall runs: edge 3, edges 5–6,
    # and edge 8. The other aligned edges are short returns.
    if not front_faces:
        front_faces = [max(range(len(ring)), key=lambda i: math.dist(ring[i], ring[(i+1)%len(ring)]))]
    front_bay_groups=[]
    for i in sorted(front_faces):
        a=ring[i]; b=ring[(i+1)%len(ring)]
        t,norm=basis_for_edge(a,b,center)
        length=math.dist(a,b)
        if front_bay_groups:
            g=front_bay_groups[-1]
            prev_t, _=basis_for_edge(ring[g['last']],ring[(g['last']+1)%len(ring)],center)
            contiguous=(i==g['last']+1 and abs(t.dot(prev_t))>=0.995)
            if contiguous:
                g['last']=i; g['length']+=length; g['b']=b
                continue
        front_bay_groups.append({'first':i,'last':i,'a':a,'b':b,'length':length})
    front_bay_groups=[g for g in front_bay_groups if g['length']>=6.0]
    if not front_bay_groups:
        i=max(front_faces,key=lambda k:math.dist(ring[k],ring[(k+1)%len(ring)]))
        front_bay_groups=[{'first':i,'last':i,'a':ring[i],'b':ring[(i+1)%len(ring)],'length':math.dist(ring[i],ring[(i+1)%len(ring)])}]
    frontage_weight=sum(g['length'] for g in front_bay_groups)
    frontage_center=Vector((0,0,0))
    for g in front_bay_groups:
        frontage_center += Vector(((g['a'][0]+g['b'][0])*0.5,(g['a'][1]+g['b'][1])*0.5,0))*g['length']
    frontage_center /= frontage_weight
    sign_group=min(front_bay_groups,key=lambda g:(Vector(((g['a'][0]+g['b'][0])*0.5,(g['a'][1]+g['b'][1])*0.5,0))-frontage_center).length)
    front_index=sign_group['first']
    front_a,front_b=sign_group['a'],sign_group['b']
    front_length=sign_group['length']
    front_t,front_n=basis_for_edge(front_a,front_b,center)
    for i, a in enumerate(ring):
        b = ring[(i+1) % len(ring)]
        length = math.dist(a, b)
        if length < 2.1:
            continue
        tangent, normal = basis_for_edge(a, b, center)
        # Pale masonry courses divide the three above-ground levels as seen in source imagery.
        for z in (3.72, 7.38, 10.98):
            if i in range(sign_group['first'],sign_group['last']+1) and abs(z - 7.38) < 0.01:
                # Keep the sign spandrel free of a course, as in the church's own photo.
                continue
            create_box("ULu | continuous pale limestone course", ((a[0]+b[0])/2, (a[1]+b[1])/2, z),
                       (length+0.10, 0.17, 0.18), tangent, normal, STONE, 0.018)
        if i in front_faces:
            # Main street windows are placed once per complete facade run below.
            continue
        count = max(1, min(3, int(length // 5.0)))
        bay_step = length / count
        for level, (low, high) in enumerate(((0.0, 3.8), (3.8, 7.45), (7.45, 11.05))):
            # Ground floor has tall storefront glass; upper levels have horizontal ribbon windows.
            w = min(bay_step * (0.68 if i == front_index else 0.50), 5.2 if i == front_index else 2.6)
            h = min((high-low)*0.62 if level == 0 else (high-low)*0.52, 2.45 if level == 0 else 1.95)
            zc = low + (high-low)*0.51 if level == 0 else low + (high-low)*0.52
            for bay in range(count):
                u = (bay + 0.5) * bay_step
                if w < 0.9:
                    continue
                add_window("ULu | facade window %02d-%02d" % (i, bay), a, tangent, normal, length, u, zc, w, h)
                # Thin projecting aluminum awning above the cafe floor.
                if level == 0:
                    awn = point_on_side(a, tangent, normal, u, 0.52, high-0.32)
                    create_box("ULu | shallow glass-and-metal entrance canopy", awn,
                               (w+0.25, 0.72, 0.10), tangent, normal, ROOF, 0.035)

    # The official street photograph shows three large bays across each floor,
    # rather than a row of narrow separate windows. One continuous window is
    # centered in each of the three dominant GIS wall runs.
    for bay_no,g in enumerate(front_bay_groups):
        a,b=g['a'],g['b']; length=g['length']
        tangent,normal=basis_for_edge(a,b,center)
        for level,(low,high) in enumerate(((0.0,3.8),(3.8,7.45),(7.45,11.05))):
            width=min(length*0.78,6.0)
            height=2.45 if level==0 else 1.95
            zc=low+(high-low)*0.51 if level==0 else low+(high-low)*0.52
            add_window("ULu | main street bay %02d floor %02d"%(bay_no+1,level+1),a,tangent,normal,length,length*0.5,zc,width,height)
            if level==0:
                awn=point_on_side(a,tangent,normal,length*0.5,0.52,high-0.32)
                create_box("ULu | broad storefront canopy",awn,(width+0.28,0.72,0.10),tangent,normal,ROOF,0.035)

    # Public identity sign and a slim Fuel coffee sign on the confirmed street facade.
    fmid = Vector(((front_a[0]+front_b[0])/2, (front_a[1]+front_b[1])/2, 0))
    sign_pos = fmid + front_n*0.29 + Vector((0, 0, 7.12)) - front_t*2.45
    # Reference imagery shows raised pale letters directly on the brick spandrel.
    add_text("ULu | UNIVERSITY sign lettering", "UNIVERSITY", sign_pos + front_t*0.95 + Vector((0,0,0.48)), front_t, front_n, 0.50, SIGN)
    add_text("ULu | LUTHERAN sign lettering", "LUTHERAN", sign_pos + Vector((0,0,-0.30)), front_t, front_n, 1.18, SIGN)
    fuel_pos = fmid + front_n*0.30 + front_t*(front_length*0.34) + Vector((0,0,2.05))
    fuel_back = create_box("ULu | Fuel vertical sign", fuel_pos, (0.62,0.16,1.85), front_t, front_n, SIGN,0.03)
    add_text("ULu | Fuel lettering", "fuel", fuel_pos + front_n*0.12 + front_t*(-0.24) + Vector((0,0,-0.18)), front_t, front_n, 0.34, FRAME)

    # Sconces at the entry and a modest recessed entry canopy.
    for u in (0.25,front_length-0.25):
        p = point_on_side(front_a, front_t, front_n, u, 0.24, 1.9)
        create_box("ULu | exterior wall sconce", p, (0.22,0.18,0.52), front_t, front_n, FRAME, 0.04)
    canopy_center = point_on_side(front_a, front_t, front_n, front_length*0.5, 0.63, 3.42)
    create_box("ULu | broad cafe entry canopy", canopy_center, (min(7.2,front_length),1.0,0.16), front_t, front_n, ROOF,0.05)

    # Schematic but source-informed interior: offices/cafe at grade, retained offices
    # upstairs, sanctuary on level three, and fellowship/activity hall in the basement.
    inward = -front_n
    int_anchor = (center[0], center[1])
    room_end = 8.5
    # Low interior partitions preserve open circulation between the cafe and offices.
    add_partition("ULu | ground floor cafe-office partition", 
                  (int_anchor[0]+front_t.x*(-1.8)+inward.x*2.0, int_anchor[1]+front_t.y*(-1.8)+inward.y*2.0, 0),
                  (int_anchor[0]+front_t.x*(-1.8)+inward.x*room_end, int_anchor[1]+front_t.y*(-1.8)+inward.y*room_end, 0),
                  0.15, 3.3)
    # Cafe bar / service counter and small tables.
    furnish_box_local("ULu | Fuel coffee service counter", int_anchor, front_t, inward, 4.6, 2.8, 1.15, (4.2,0.75,1.0), WOOD)
    for u,v in ((-6,3.1),(-2.5,3.1),(1.0,3.1),(-6,6.1),(-2.5,6.1),(1,6.1)):
        if point_inside(ring, int_anchor[0]+front_t.x*u+inward.x*v, int_anchor[1]+front_t.y*u+inward.y*v):
            furnish_box_local("ULu | cafe table", int_anchor, front_t, inward, u, v, 0.86, (1.0,0.8,0.09), WOOD)
            for dx in (-0.7,0.7):
                furnish_box_local("ULu | cafe chair", int_anchor, front_t, inward, u+dx, v+0.85, 0.45, (0.45,0.45,0.85), FRAME)
    # Office furniture on the second level, arranged in modular desk groups.
    for u in (-8,-4,0,4,8):
        for v in (1.5,4.0,6.5):
            x=int_anchor[0]+front_t.x*u+inward.x*v; y=int_anchor[1]+front_t.y*u+inward.y*v
            if point_inside(ring,x,y):
                furnish_box_local("ULu | second floor office desk", int_anchor, front_t, inward, u, v, 4.55, (1.5,0.75,0.08), WOOD)
                furnish_box_local("ULu | office chair", int_anchor, front_t, inward, u, v+0.72, 4.88, (0.52,0.5,0.8), FRAME)

    # Third floor sanctuary: nave seating oriented toward an altar along the rear wall.
    sanctuary_z = 7.47
    for row, v in enumerate((1.5,3.0,4.5,6.0,7.5)):
        for u in (-8,-4,0,4,8):
            x=int_anchor[0]+front_t.x*u+inward.x*v; y=int_anchor[1]+front_t.y*u+inward.y*v
            if point_inside(ring,x,y):
                furnish_box_local("ULu | sanctuary pew", int_anchor, front_t, inward, u, v, sanctuary_z+0.46, (3.2,0.52,0.82), WOOD)
    altar_u, altar_v = 0.0, 10.0
    ax=int_anchor[0]+front_t.x*altar_u+inward.x*altar_v; ay=int_anchor[1]+front_t.y*altar_u+inward.y*altar_v
    if point_inside(ring,ax,ay):
        furnish_box_local("ULu | sanctuary altar", int_anchor, front_t, inward, altar_u, altar_v, sanctuary_z+0.62, (2.8,0.95,1.0), WOOD)
        furnish_box_local("ULu | pulpit", int_anchor, front_t, inward, altar_u+2.1, altar_v, sanctuary_z+0.65, (0.8,0.75,1.0), WOOD)
    # Basement fellowship/gym tables and court markings.
    for u in (-7,-2,3,8):
        x=int_anchor[0]+front_t.x*u+inward.x*4.0; y=int_anchor[1]+front_t.y*u+inward.y*4.0
        if point_inside(ring,x,y):
            furnish_box_local("ULu | basement fellowship table", int_anchor, front_t, inward, u, 4.0, -1.55, (2.1,0.9,0.09), WOOD)
    add_partition("ULu | sanctuary side room partition", 
                  (int_anchor[0]+front_t.x*6.5+inward.x*8.0, int_anchor[1]+front_t.y*6.5+inward.y*8.0,0),
                  (int_anchor[0]+front_t.x*6.5+inward.x*12.0, int_anchor[1]+front_t.y*6.5+inward.y*12.0,0),
                  7.6,10.6)

    # Give all Blender text/mesh objects useful identity metadata.
    for obj in asset_collection.objects:
        obj["building_id"] = ASSET_ID
        obj["identity"] = "University Lutheran Church, 460 Northwestern Avenue, West Lafayette, Indiana"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.world.color = (0.18,0.20,0.25)
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.render.resolution_percentage = 100
    # Camera for a three-quarter view of the primary street facade.
    lookat = Vector((center[0], center[1], 5.0))
    camera_data = bpy.data.cameras.new("ULu presentation camera")
    camera = bpy.data.objects.new("ULu presentation camera", camera_data)
    scene.collection.objects.link(camera)
    # Move the camera to the road side of the whole outline while retaining the
    # street-facing elevation in view.
    all_front_normals=[]
    for i in front_faces:
        ta,na=basis_for_edge(ring[i],ring[(i+1)%len(ring)],center)
        all_front_normals.append((na,math.dist(ring[i],ring[(i+1)%len(ring)])))
    road_n=Vector((0,0,0))
    for na,w in all_front_normals: road_n += na*w
    if road_n.length: road_n.normalize()
    else: road_n=front_n.copy()
    camera.location = (center[0]+road_n.x*62+front_t.x*11,
                       center[1]+road_n.y*62+front_t.y*11, 25)
    camera.rotation_euler = (lookat-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.data.lens = 45
    scene.camera = camera
    for name, loc, energy, size in (("large warm key",(center[0]+5,center[1]-15,28),5200,20),
                                    ("cool fill",(center[0]-20,center[1]+5,20),2300,16),
                                    ("roof rim",(center[0]+14,center[1]+20,24),3500,12)):
        ld=bpy.data.lights.new(name,"AREA"); lo=bpy.data.objects.new(name,ld); scene.collection.objects.link(lo)
        lo.location=loc; ld.energy=energy; ld.shape="DISK"; ld.size=size
        lo.rotation_euler=(lookat-lo.location).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath = str(EVIDENCE_DIR / "preview_three_quarter.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    bpy.ops.render.render(write_still=True)

    frontage_render_center=Vector((frontage_center.x,frontage_center.y,5.6))
    facade_camera_data=bpy.data.cameras.new("ULu street elevation camera")
    facade_camera=bpy.data.objects.new("ULu street elevation camera",facade_camera_data)
    scene.collection.objects.link(facade_camera)
    facade_camera.location=(frontage_render_center.x+road_n.x*42, frontage_render_center.y+road_n.y*42, 17)
    facade_camera.rotation_euler=(Vector((frontage_render_center.x,frontage_render_center.y,6.0))-facade_camera.location).to_track_quat("-Z","Y").to_euler()
    facade_camera.data.lens=38
    scene.camera=facade_camera
    scene.render.resolution_x=1400; scene.render.resolution_y=950
    scene.render.filepath=str(EVIDENCE_DIR / "preview_street_elevation.png")
    bpy.ops.render.render(write_still=True)

    # A separate top orthographic preview for footprint comparison.
    top = bpy.data.cameras.new("ULu top footprint camera")
    top_obj = bpy.data.objects.new("ULu top footprint camera", top)
    scene.collection.objects.link(top_obj)
    top_obj.location=(center[0],center[1],72)
    top_obj.rotation_euler=(0,0,0)
    top_obj.rotation_euler=(0,0,0)
    top_obj.rotation_euler[0]=0
    top_obj.rotation_euler[1]=0
    top_obj.rotation_euler[2]=0
    # Camera local -Z must point down: rotate 180 degrees about X.
    top_obj.rotation_euler=(0,0,0)
    top.type="ORTHO"; top.ortho_scale=47
    scene.camera=top_obj
    scene.render.resolution_x=1000; scene.render.resolution_y=1000
    scene.render.filepath=str(EVIDENCE_DIR / "preview_top.png")
    bpy.ops.render.render(write_still=True)

    print(json.dumps({"asset":str(ASSET_PATH),"scene":scene.name,"collection":asset_collection.name,
                      "objects":len(asset_collection.objects),"ring_points":len(ring),
                      "front_edge_index":front_index,"front_edge_length_m":math.dist(front_a,front_b),
                      "street_front_edges":front_faces,"street_window_bay_groups":[[g['first']+j for j in range(g['last']-g['first']+1)] for g in front_bay_groups],"sign_group_edges":[sign_group['first']+j for j in range(sign_group['last']-sign_group['first']+1)],"road_edge_stats":road_edge_stats,
                      "bounds_xy_m":[[min(x for x,y in ring),max(x for x,y in ring)],[min(y for x,y in ring),max(y for x,y in ring)]],
                      "z_bounds_m":[WALL_BOTTOM,PARAPET_Z+0.42]},indent=2))


if __name__ == "__main__":
    main()
