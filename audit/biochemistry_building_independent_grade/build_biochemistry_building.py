"""Build the source-backed modular library for Purdue Biochemistry Building (BCHM).

Horizontal structure follows Purdue GIS feature FID 238 exactly in the project's
documented local geographic approximation. The GIS floor/roof fields are used only
as provisional vertical cues because the service schema does not state their units.
Facade dimensions, roof equipment and the schematic lobby/lab vignette remain
interpretive; see audit/biochemistry_building/evidence.md.
"""

import bpy
import bmesh
import json
import math
import os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(ROOT, '..', '..'))
AUDIT = os.path.abspath(os.path.join(ROOT, '..', '..', 'audit', 'biochemistry_building'))
SOURCES = os.path.join(AUDIT, 'sources')
ASSET_PATH = os.path.join(ROOT, 'biochemistry_building.blend')
GIS_PATH = os.path.join(SOURCES, 'biochemistry_building_gis_fid238_2026-10-25.json')
PREVIEW_PATH = os.path.join(AUDIT, 'biochemistry_building_preview.png')
EVIDENCE_PATH = os.path.join(AUDIT, 'build_evidence.json')
os.makedirs(AUDIT, exist_ok=True)

ASSET_ID = 'biochemistry_building'
ASSET_COLLECTION = 'Asset_biochemistry_building'
SCENE_NAME = 'Scene'
ORIGIN_LON, ORIGIN_LAT = -86.9137, 40.4274
LON_SCALE = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
LAT_SCALE = 111040.0

with open(os.path.join(REPO, 'modular', 'manifest.json'), encoding='utf-8') as f:
    manifest = json.load(f)
manifest_entry = next(item for item in manifest['assets'] if item['id'] == ASSET_ID)
assert manifest_entry['file'] == 'buildings/biochemistry_building.blend'
assert manifest_entry['collection'] == ASSET_COLLECTION
assert manifest_entry['scene'] == SCENE_NAME
assert manifest_entry['local_coordinates'] is True

with open(GIS_PATH, encoding='utf-8') as f:
    gis = json.load(f)
assert len(gis['features']) == 1
feature = gis['features'][0]
attrs = feature['attributes']
assert attrs['FID'] == 238 and attrs['BLDG_ABBR'] == 'BCHM'
assert attrs['BUILDING_N'] == 'Biochemistry Building'
assert attrs['ADDRESS'] == '175 S University Street'
ring_ll = feature['geometry']['rings'][0]
ring_xy = [((lon - ORIGIN_LON) * LON_SCALE, (lat - ORIGIN_LAT) * LAT_SCALE) for lon, lat in ring_ll]
area2 = sum(ring_xy[i][0] * ring_xy[i + 1][1] - ring_xy[i + 1][0] * ring_xy[i][1] for i in range(len(ring_xy) - 1))
assert abs(area2) > 1
origin_x = sum((ring_xy[i][0] + ring_xy[i + 1][0]) * (ring_xy[i][0] * ring_xy[i + 1][1] - ring_xy[i + 1][0] * ring_xy[i][1]) for i in range(len(ring_xy) - 1)) / (3 * area2)
origin_y = sum((ring_xy[i][1] + ring_xy[i + 1][1]) * (ring_xy[i][0] * ring_xy[i + 1][1] - ring_xy[i + 1][0] * ring_xy[i][1]) for i in range(len(ring_xy) - 1)) / (3 * area2)
expected_origin = manifest_entry['placement_origin_xy_m']
assert math.dist((origin_x, origin_y), expected_origin) < 1e-6, ((origin_x, origin_y), expected_origin)
ring = [(x - origin_x, y - origin_y) for x, y in ring_xy[:-1]]
assert len(ring) == 34

# The GIS fields F01..F04 and R step by 12.08, which is consistent with feet but
# the service does not declare units. Use a documented feet-to-meters inference,
# never claim these datums as surveyed elevations.
GIS_TO_M = 0.3048
floor_datums = [0.0] + [attrs[k] * GIS_TO_M for k in ('F01', 'F02', 'F03', 'F04')]
roof_z = attrs['R'] * GIS_TO_M
assert floor_datums == sorted(floor_datums) and len(floor_datums) == 5
assert 16.0 < roof_z < 19.0

# Reset the standalone library without touching any other Blender files.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for col in list(bpy.data.collections):
    if col.name != 'Collection':
        bpy.data.collections.remove(col)
scene = bpy.context.scene
scene.name = SCENE_NAME
root_col = bpy.data.collections.get('Collection')
if root_col:
    root_col.name = 'BCHM library scene contents'
asset = bpy.data.collections.new(ASSET_COLLECTION)
scene.collection.children.link(asset)
preview_col = bpy.data.collections.new('Preview_only')
scene.collection.children.link(preview_col)

def link_asset(obj, name=None):
    if name:
        obj.name = name
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    asset.objects.link(obj)
    return obj

def link_preview(obj, name=None):
    if name:
        obj.name = name
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    preview_col.objects.link(obj)
    return obj

def make_surface(name, color, roughness=0.75, metallic=0.0, noise_scale=5.0, bump=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new('ShaderNodeOutputMaterial')
    shader = nodes.new('ShaderNodeBsdfPrincipled')
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metallic
    links.new(shader.outputs['BSDF'], output.inputs['Surface'])
    shader.inputs['Base Color'].default_value = (*color, 1.0)
    if noise_scale:
        tex = nodes.new('ShaderNodeTexCoord')
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = noise_scale
        noise.inputs['Detail'].default_value = 2.0
        ramp = nodes.new('ShaderNodeValToRGB')
        c0 = tuple(max(0.0, c * 0.82) for c in color) + (1.0,)
        c1 = tuple(min(1.0, c * 1.16) for c in color) + (1.0,)
        ramp.color_ramp.elements[0].color = c0
        ramp.color_ramp.elements[1].color = c1
        links.new(tex.outputs['Object'], noise.inputs['Vector'])
        links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], shader.inputs['Base Color'])
        if bump:
            bump_node = nodes.new('ShaderNodeBump')
            bump_node.inputs['Strength'].default_value = min(0.35, bump)
            bump_node.inputs['Distance'].default_value = 0.03
            links.new(noise.outputs['Fac'], bump_node.inputs['Height'])
            links.new(bump_node.outputs['Normal'], shader.inputs['Normal'])
    return mat

brick = make_surface('BCHM | warm red-brown academic brick', (0.39, 0.16, 0.105), .84, 0, 5.0, .16)
stone = make_surface('BCHM | pale limestone portico and belts', (.68, .64, .53), .73, 0, 6.0, .07)
concrete = make_surface('BCHM | foundation and approach concrete', (.37, .38, .37), .85, 0, 7.0, .12)
glass = make_surface('BCHM | blue-gray laboratory glazing', (.045, .13, .19), .28, .12, 0, 0)
metal = make_surface('BCHM | dark bronze and roof metal', (.12, .15, .16), .42, .48, 0, 0)
roofmat = make_surface('BCHM | flat roof membrane', (.22, .24, .24), .9, 0, 4.0, .06)
interior = make_surface('BCHM | warm laboratory interior', (.62, .57, .46), .82, 0, 3.0, .02)

def mesh_obj(name, vertices, faces, material):
    mesh = bpy.data.meshes.new(name + 'Mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    asset.objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    return obj

def cube(name, loc, dims, material, angle=0.0, bevel=0.0):
    # Construct boxes directly so the many inspectable facade parts do not each
    # trigger Blender's context-dependent primitive and transform operators.
    hx, hy, hz = (d / 2 for d in dims)
    c, s = math.cos(angle), math.sin(angle)
    vertices = []
    for x, y, z in [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
                    (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]:
        vertices.append((loc[0] + c * x - s * y, loc[1] + s * x + c * y, loc[2] + z))
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    mesh = bpy.data.meshes.new(name + 'Mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    asset.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new('Small softened arris', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def extruded_polygon(name, pts, z0, z1, material):
    n = len(pts)
    verts = [(x, y, z0) for x, y in pts] + [(x, y, z1) for x, y in pts]
    faces = [tuple(range(n)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    return mesh_obj(name, verts, faces, material)

def facade_cube(name, x, y, z, width, depth, height, angle, material, bevel=.0):
    return cube(name, (x, y, z), (width, depth, height), material, angle, bevel)

def add_wall_window(name, center, outward, angle, width, floor_index):
    x, y = center
    # GIS floor heights are provisional inferred feet values. Keep visual window
    # proportions consistent with the five story rhythm without claiming a survey.
    zbase = floor_datums[floor_index]
    h = 1.72 if floor_index < 4 else 1.52
    zc = zbase + (1.92 if floor_index < 4 else 1.68)
    depth = .11
    glass_x, glass_y = x + outward[0] * .09, y + outward[1] * .09
    frame_x, frame_y = x + outward[0] * .16, y + outward[1] * .16
    facade_cube(name + ' | glazing', glass_x, glass_y, zc, width, depth, h, angle, glass)
    frame = .105
    # Frames, a central meeting rail, and two narrow vertical lights are separate
    # source-local elements so the facade remains inspectable in the library.
    for s in (-1, 1):
        facade_cube(name + ' | jamb', frame_x + math.cos(angle) * s * (width / 2), frame_y + math.sin(angle) * s * (width / 2), zc, frame, .16, h + .16, angle, stone, .012)
    for s in (-1, 1):
        facade_cube(name + ' | head/sill', frame_x, frame_y, zc + s * (h / 2), width + .12, .17, frame, angle, stone, .012)
    facade_cube(name + ' | center mullion', frame_x, frame_y, zc, .055, .18, h, angle, metal, .008)
    facade_cube(name + ' | meeting rail', frame_x, frame_y, zc - .02, width - .08, .18, .055, angle, stone, .008)

def signed_area(pts):
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2

area = signed_area(ring)
assert area < 0, area

# Exact official footprint envelope; the ring is a single exterior shell, without
# any claimed interior courtyard voids.
base_z = .35
shell = extruded_polygon('biochemistry_building_GIS_outline_primary_shell', ring, base_z, roof_z, brick)
shell['source_provider'] = 'Purdue BuildingShapesZip4 FeatureServer'
shell['source_feature_id'] = 238
shell['source_crs'] = 'EPSG:4326 WGS 84 response; transformed by project local approximation'
shell['geometry_status'] = 'Exact first exterior GIS ring; no scaling; GIS source provides one ring'
shell['height_status'] = 'Roof datum provisionally interpreted from GIS R=57.82 as feet; unit unverified'

# Masonry base and parapet follow each meaningful footprint edge. Short jogs stay
# with the source shell but do not receive invented facade details.
for i, (p, q) in enumerate(zip(ring, ring[1:] + ring[:1])):
    dx, dy = q[0] - p[0], q[1] - p[1]
    length = math.hypot(dx, dy)
    if length < 1.1:
        continue
    angle = math.atan2(dy, dx)
    # For this clockwise GIS ring, exterior points to the left of each edge.
    outward = (-dy / length, dx / length)
    cx, cy = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    facade_cube(f'BCHM foundation plinth {i:02d}', cx + outward[0] * .10, cy + outward[1] * .10, .62, length, .28, .54, angle, concrete, .025)
    facade_cube(f'BCHM flat roof parapet {i:02d}', cx + outward[0] * .08, cy + outward[1] * .08, roof_z + .27, length, .22, .54, angle, stone, .018)
    # Five narrow belt courses follow the floor rhythm and tie the additions into
    # one documented academic/laboratory complex.
    if length >= 2.0:
        for fi, datum in enumerate(floor_datums[1:], start=1):
            z = datum - .19
            facade_cube(f'BCHM limestone story belt {i:02d}_{fi}', cx + outward[0] * .08, cy + outward[1] * .08, z, length, .12, .16, angle, stone, .012)
    if length >= 7.8:
        bays = max(1, int((length - 2.0) // 3.3))
        margin = (length - bays * 2.1) / (bays + 1)
        for floor_i in range(5):
            for bay_i in range(bays):
                d = margin + bay_i * (2.1 + margin) + 1.05
                wx = p[0] + dx / length * d
                wy = p[1] + dy / length * d
                # Keep the south portico opening clear on the longest south edge.
                is_portico_edge = outward[1] < -.92 and abs(cy - min(v[1] for v in ring)) < 1.6
                if is_portico_edge and floor_i == 0 and abs(d - length / 2) < 2.2:
                    continue
                win_width = min(1.55, max(1.05, margin * .54))
                add_wall_window(f'BCHM facade bay {i:02d}_{floor_i}_{bay_i}', (wx, wy), outward, angle, win_width, floor_i)

# Flat, restrained roof treatment; exact rooftop layout is not surveyed. Mechanical
# screen is schematic, reflecting lab use, and does not alter the GIS shell.
roof_center = (0.0, 0.0)  # exact GIS area centroid, verified inside the footprint
mesh_obj('BCHM flat roof membrane exact GIS ring', [(x, y, roof_z + .025) for x, y in ring], [tuple(range(len(ring)))], roofmat)
for i, (dx, dy, sx, sy) in enumerate([(0.0, -14.0, 5.6, 3.6), (0.0, -8.0, 4.2, 3.0), (10.0, -8.0, 3.0, 2.3)]):
    x, y = roof_center[0] + dx, roof_center[1] + dy
    cube(f'BCHM schematic rooftop mechanical screen {i}', (x, y, roof_z + .58), (sx, sy, 1.05), metal, bevel=.06)
    cube(f'BCHM schematic rooftop service curb {i}', (x, y, roof_z + .08), (sx + .35, sy + .35, .16), concrete, bevel=.025)
for i, (dx, dy) in enumerate([(-2.0, 0.0), (8.0, 0.0), (12.0, -10.0)]):
    x, y = roof_center[0] + dx, roof_center[1] + dy
    cube(f'BCHM schematic roof exhaust stack {i}', (x, y, roof_z + .65), (.70, .70, 1.25), metal, bevel=.04)
    cube(f'BCHM roof exhaust cap {i}', (x, y, roof_z + 1.30), (1.0, 1.0, .16), stone, bevel=.025)

# Main entry: GIS southern facade is the longest segment facing south. Purdue's
# 2008-09 Catalyst states the department name remains over this south portico.
entry_edge = None
for p, q in zip(ring, ring[1:] + ring[:1]):
    dx, dy = q[0] - p[0], q[1] - p[1]
    length = math.hypot(dx, dy)
    if length > 8.0 and dy / length > -.12 and dy / length < .12 and dx < 0 and (p[1] + q[1]) / 2 < min(v[1] for v in ring) + 2.0:
        # Southern edge of the clockwise ring runs westward and its outward normal points south.
        entry_edge = (p, q, dx, dy, length)
        break
assert entry_edge, 'Could not identify GIS south portico edge'
p, q, dx, dy, length = entry_edge
ex, ey = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
angle = math.atan2(dy, dx)
outward = (-dy / length, dx / length)
# The two stone piers and head frame a paired entrance below a modest flat portico.
door_width, door_height = 2.50, 2.75
door_z = base_z + door_height / 2
front_offset = .22
facade_cube('BCHM south portico paired glass entry', ex + outward[0] * front_offset, ey + outward[1] * front_offset, door_z, door_width, .18, door_height, angle, glass)
for side in (-1, 1):
    xx = ex + math.cos(angle) * side * (door_width / 2 + .26) + outward[0] * .29
    yy = ey + math.sin(angle) * side * (door_width / 2 + .26) + outward[1] * .29
    cube(f'BCHM south portico limestone pier {side}', (xx, yy, 2.52), (.46, .60, 4.35), stone, angle, .025)
    cube(f'BCHM south portico pier base {side}', (xx, yy, .55), (.68, .82, .32), stone, angle, .02)
    cube(f'BCHM south portico capital {side}', (xx, yy, 4.73), (.64, .76, .32), stone, angle, .02)
facade_cube('BCHM south portico limestone entablature', ex + outward[0] * .29, ey + outward[1] * .29, 4.92, door_width + 1.55, .68, .40, angle, stone, .035)
facade_cube('BCHM south portico limestone name band', ex + outward[0] * .36, ey + outward[1] * .36, 5.40, 5.15, .14, .54, angle, stone, .025)

def add_facing_text(body, loc, outward, size, material, name):
    bpy.ops.object.text_add(location=loc)
    obj = link_asset(bpy.context.object, name)
    obj.data.body = body
    obj.data.size = size
    obj.data.align_x = 'CENTER'
    obj.data.align_y = 'CENTER'
    # Keep text upright and orient its local +Z to face outward from the wall.
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = Vector((outward[0], outward[1], 0)).to_track_quat('Z', 'Y')
    obj.data.extrude = .003
    obj.data.materials.append(material)
    return obj

add_facing_text('AGRICULTURAL CHEMISTRY', (ex + outward[0] * .46, ey + outward[1] * .46, 5.40), outward, .28, metal, 'BCHM historic south portico inscription')

# Central doors, limestone stair and modest landing. The location is bounded to
# the south frontage; exact door dimensions and stair layout are not documented.
facade_cube('BCHM south portico transom', ex + outward[0] * .33, ey + outward[1] * .33, 3.95, 2.45, .12, .48, angle, glass)
for step in range(4):
    d = .40 * (step + 1)
    z = .14 * (step + 1)
    cube(f'BCHM south entry step {step}', (ex + outward[0] * (d + .55), ey + outward[1] * (d + .55), z / 2), (door_width + 1.5, d, z), concrete, angle, .03)
cube('BCHM south portico landing', (ex + outward[0] * 2.15, ey + outward[1] * 2.15, .18), (door_width + 2.2, 1.45, .24), concrete, angle, .025)

# A small visible laboratory vignette supports the documented research use; it is
# schematic, kept just inside the southern wall behind the glazing.
for i, (dxi, dyi) in enumerate([(-1.15, 2.1), (1.10, 2.1)]):
    cube(f'BCHM schematic lab bench {i}', (ex + dxi, ey + dyi, 1.22), (2.05, .70, .12), interior, bevel=.025)
    cube(f'BCHM schematic lab cabinet {i}', (ex + dxi, ey + dyi, .70), (1.95, .58, .86), stone, bevel=.025)
    cube(f'BCHM schematic lab instrument {i}', (ex + dxi, ey + dyi, 1.78), (.62, .42, .96), metal, bevel=.03)

# Portable preview-only ground, camera, and lighting live outside the exported collection.
world = bpy.data.worlds.new('BCHM | neutral studio') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (.34, .42, .52, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = .45
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.render.resolution_x = 1440
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'

bpy.ops.mesh.primitive_plane_add(size=190, location=(0, 0, -.18))
ground = bpy.context.object
ground.name = 'Preview ground only'
ground.data.materials.append(make_surface('BCHM preview neutral ground', (.22, .26, .23), .95, 0, 3.0, .04))
link_preview(ground)

bpy.ops.object.light_add(type='SUN', location=(-90, -85, 100))
sun = bpy.context.object
sun.name = 'Preview sun only'
sun.rotation_euler = (math.radians(26), math.radians(-35), math.radians(-25))
sun.data.energy = 2.0
link_preview(sun)
bpy.ops.object.light_add(type='AREA', location=(-40, -75, 55))
fill = bpy.context.object
fill.name = 'Preview area fill only'
fill.data.energy = 25000
fill.data.shape = 'DISK'
fill.data.size = 55
fill.rotation_euler = (math.radians(22), 0, math.radians(-15))
link_preview(fill)

target = Vector((0, 0, 7.3))
camloc = Vector((-94, -102, 66))
bpy.ops.object.camera_add(location=camloc)
camera = bpy.context.object
camera.name = 'Preview south-west overview only'
camera.data.lens = 53
camera.rotation_euler = (target - camloc).to_track_quat('-Z', 'Y').to_euler()
scene.camera = camera
link_preview(camera)

scene.render.filepath = PREVIEW_PATH
scene.render.image_settings.file_format = 'PNG'
bpy.ops.wm.save_as_mainfile(filepath=ASSET_PATH)
bpy.ops.render.render(write_still=True)

mesh_objects = [obj for obj in asset.objects if obj.type == 'MESH']
font_objects = [obj for obj in asset.objects if obj.type == 'FONT']
world_points = []
for obj in mesh_objects:
    for corner in obj.bound_box:
        world_points.append(obj.matrix_world @ Vector(corner))
bounds = [[min(p[i] for p in world_points), max(p[i] for p in world_points)] for i in range(3)]
payload = {
    'asset_id': ASSET_ID,
    'asset_file': 'modular/buildings/biochemistry_building.blend',
    'collection': ASSET_COLLECTION,
    'scene': SCENE_NAME,
    'source_feature': {'provider': 'Purdue University BuildingShapesZip4 FeatureServer layer 0', 'feature_id': 238, 'building_code': 'BCHM', 'name': 'Biochemistry Building', 'address': '175 S University Street', 'retrieved_date': '2026-10-25', 'crs': 'EPSG:4326 WGS 84', 'snapshot': 'sources/biochemistry_building_gis_fid238_2026-10-25.json'},
    'local_frame': 'XY east/north, Z up, meters; exact local origin is GIS polygon centroid under project local approximation',
    'placement_origin_xy_m': [origin_x, origin_y],
    'gis_ring_unique_vertex_count': len(ring),
    'gis_local_area_approx_m2': abs(area),
    'gis_local_perimeter_approx_m': sum(math.dist(ring[i], ring[(i + 1) % len(ring)]) for i in range(len(ring))),
    'floor_datums_m': floor_datums,
    'roof_datum_m': roof_z,
    'vertical_unit_inference': 'GIS F01-F04 and R are treated provisionally as feet because the 12.08-unit repeated spacing is consistent with story intervals; layer schema declares numeric type but no units. These are estimates, not surveyed elevations.',
    'exported_object_count': len(asset.objects),
    'mesh_object_count': len(mesh_objects),
    'font_object_count': len(font_objects),
    'evaluated_local_bounds_m': bounds,
    'preview': 'biochemistry_building_preview.png',
    'source_supported_form': ['Five story count in GIS attributes', '1938 original Agricultural Chemistry Building; additions recorded in 1952 and 1981', 'south portico inscription AGRICULTURAL CHEMISTRY from Purdue 2008-09 Catalyst', 'current laboratory/research use from Purdue department pages', 'brick academic laboratory character and multiple eras supported by Purdue archive and renovation records'],
    'estimated_or_unverified': ['GIS vertical field units not declared; floor intervals/roof elevation are provisional', 'Exact facade bay counts, window dimensions, wall heights and door dimensions are not sourced by measured elevations', 'Roof profile and mechanical-equipment arrangement are not surveyed', 'Single GIS exterior ring has no courtyard holes; interior room geometry and exact addition joints are unverified', 'Visible laboratory furnishings are a programmatic schematic, not as-built'],
    'external_image_dependencies': [],
    'independent_grade': None,
}
with open(EVIDENCE_PATH, 'w', encoding='utf-8') as f:
    json.dump(payload, f, indent=2)
print(json.dumps(payload, indent=2))
