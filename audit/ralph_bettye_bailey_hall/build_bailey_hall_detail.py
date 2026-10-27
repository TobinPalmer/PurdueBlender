import bpy
import bmesh
import json
import math
import os
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ASSET_ID = 'massing_ralph_bettye_bailey_hall_406c4db'
OBJECT_NAME = 'Ralph & Bettye Bailey Hall'
COLLECTION_NAME = 'Asset_massing_ralph_bettye_bailey_hall_406c4db'
HEIGHT_M = 7.5  # photo-scaled estimate for the lower wings; no measured elevation
ENTRY_TOWER_HEIGHT_M = 33.4 * 0.3048  # GIS field R, tentatively interpreted as feet; units undocumented
FLOOR_COUNT = 5  # official campus GIS attribute; treated as an attribute, not height evidence
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137

blend_path = bpy.data.filepath
if not blend_path or not os.path.isfile(blend_path):
    raise RuntimeError('Open the target building .blend before running this script')
obj = bpy.data.objects.get(OBJECT_NAME)
collection = bpy.data.collections.get(COLLECTION_NAME)
if obj is None or collection is None:
    raise RuntimeError('Expected building object or exported collection is missing')
if obj not in collection.objects[:]:
    raise RuntimeError('Building object is not in its expected exported collection')
if len(collection.objects) != 1:
    raise RuntimeError('Expected the original single-object massing asset; refusing to alter an unexpected collection')

snapshot_path = os.path.join(os.path.dirname(__file__), 'source_feature_411_raw.json')
with open(snapshot_path, 'r', encoding='utf-8-sig') as f:
    feature = json.load(f)
attrs = feature['attributes']
if attrs.get('FID') != 411 or attrs.get('BLDG_ABBR') != 'BALY':
    raise RuntimeError('Snapshot does not identify the official BALY feature FID 411')
source_ring = feature['geometry']['rings'][0]
if source_ring[0] == source_ring[-1]:
    source_ring = source_ring[:-1]
ring = []
for lon, lat in source_ring:
    x = (lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT))
    y = (lat - ORIGIN_LAT) * 111040.0
    ring.append(Vector((x, y)))
if len(ring) < 3:
    raise RuntimeError('Source polygon has fewer than three vertices')

# Create or update the local asset materials. The mesh in this library has its own material datablocks.
def material(name, color, roughness=0.82, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF') if mat.node_tree else None
    if bsdf:
        if 'Base Color' in bsdf.inputs:
            bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        if 'Roughness' in bsdf.inputs:
            bsdf.inputs['Roughness'].default_value = roughness
        if 'Metallic' in bsdf.inputs:
            bsdf.inputs['Metallic'].default_value = metallic
    if name == 'Purdue_Red_Brick' and mat.node_tree:
        nodes = mat.node_tree.nodes
        for old in list(nodes):
            if old.name in ('BALY_FacadeUV', 'BALY_BrickTexture'):
                nodes.remove(old)
        uv_node = nodes.new('ShaderNodeUVMap')
        uv_node.name = 'BALY_FacadeUV'
        uv_node.uv_map = 'FacadeUV'
        brick_node = nodes.new('ShaderNodeTexBrick')
        brick_node.name = 'BALY_BrickTexture'
        brick_node.inputs['Color1'].default_value = (0.38, 0.095, 0.055, 1.0)
        brick_node.inputs['Color2'].default_value = (0.27, 0.05, 0.03, 1.0)
        brick_node.inputs['Mortar'].default_value = (0.10, 0.085, 0.07, 1.0)
        brick_node.inputs['Scale'].default_value = 1.0
        brick_node.inputs['Mortar Size'].default_value = 0.012
        brick_node.inputs['Mortar Smooth'].default_value = 0.08
        brick_node.inputs['Brick Width'].default_value = 0.48
        brick_node.inputs['Row Height'].default_value = 0.075
        mat.node_tree.links.new(uv_node.outputs['UV'], brick_node.inputs['Vector'])
        if bsdf and 'Base Color' in bsdf.inputs:
            mat.node_tree.links.new(brick_node.outputs['Color'], bsdf.inputs['Base Color'])
    return mat

mats = [
    material('Purdue_Red_Brick', (0.34, 0.075, 0.045), 0.88),
    material('Indiana_Bedford_Limestone', (0.66, 0.60, 0.49), 0.86),
    material('Bailey_Dark_Glazing', (0.035, 0.095, 0.13), 0.22, 0.08),
    material('Bailey_Roof_Slate', (0.14, 0.16, 0.17), 0.9),
    material('Bailey_Entry_Metal', (0.055, 0.065, 0.07), 0.36, 0.35),
]
BRICK, STONE, GLASS, ROOF, METAL = range(len(mats))
INTERIOR_LOBBY = len(mats); mats.append(material('Bailey_Schematic_Lobby', (0.72, 0.68, 0.57), 0.9))
INTERIOR_REHEARSAL = len(mats); mats.append(material('Bailey_Schematic_Rehearsal', (0.55, 0.18, 0.12), 0.9))
INTERIOR_SUPPORT = len(mats); mats.append(material('Bailey_Schematic_Support', (0.74, 0.74, 0.64), 0.9))
INTERIOR_CIRCULATION = len(mats); mats.append(material('Bailey_Schematic_Circulation', (0.62, 0.60, 0.52), 0.9))
verts = []
faces = []
face_materials = []
face_uvs = []

def add_face(indices, mat_index, uv=None):
    faces.append(tuple(indices))
    face_materials.append(mat_index)
    face_uvs.append(uv)

def add_quad(points, mat_index, uv=None):
    start = len(verts)
    verts.extend(tuple(p) for p in points)
    add_face((start, start + 1, start + 2, start + 3), mat_index, uv)

def add_box(center, tangent, normal, width, depth, height, mat_index):
    center = Vector(center)
    tangent = Vector((tangent.x, tangent.y, 0.0)).normalized()
    normal = Vector((normal.x, normal.y, 0.0)).normalized()
    up = Vector((0.0, 0.0, 1.0))
    hw, hd, hh = width * 0.5, depth * 0.5, height * 0.5
    offsets = [
        (-hw, -hd, -hh), (hw, -hd, -hh), (hw, hd, -hh), (-hw, hd, -hh),
        (-hw, -hd, hh), (hw, -hd, hh), (hw, hd, hh), (-hw, hd, hh),
    ]
    base = len(verts)
    for a, b, c in offsets:
        verts.append(tuple(center + tangent * a + normal * b + up * c))
    for local_face in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        add_face(tuple(base + i for i in local_face), mat_index)

def edge_frame(a, b):
    delta = b - a
    length = delta.length
    tangent = Vector((delta.x / length, delta.y / length, 0.0))
    # The right side of a counter-clockwise ring is exterior; reverse for clockwise rings.
    normal = Vector((tangent.y, -tangent.x, 0.0)) * orientation_sign
    return length, tangent, normal

signed_area2 = sum(ring[i].x * ring[(i + 1) % len(ring)].y - ring[(i + 1) % len(ring)].x * ring[i].y for i in range(len(ring)))
orientation_sign = 1.0 if signed_area2 > 0 else -1.0
min_x, max_x = min(p.x for p in ring), max(p.x for p in ring)
min_y, max_y = min(p.y for p in ring), max(p.y for p in ring)

# GIS-derived local origin: the source polygon centroid in the project's documented
# local approximation. Localized geometry is later instanced at this proposed campus XY.
cross_sum = 0.0
centroid_x_num = 0.0
centroid_y_num = 0.0
for i, point in enumerate(ring):
    nxt = ring[(i + 1) % len(ring)]
    cross = point.x * nxt.y - nxt.x * point.y
    cross_sum += cross
    centroid_x_num += (point.x + nxt.x) * cross
    centroid_y_num += (point.y + nxt.y) * cross
placement_x = centroid_x_num / (3.0 * cross_sum)
placement_y = centroid_y_num / (3.0 * cross_sum)

# Structural shell follows the official 23-vertex (closed-ring) campus footprint.
base_z = 0.0
foundation_top = 0.72
roof_z = HEIGHT_M
for i, a2 in enumerate(ring):
    b2 = ring[(i + 1) % len(ring)]
    length, _, _ = edge_frame(a2, b2)
    a0 = Vector((a2.x, a2.y, base_z))
    b0 = Vector((b2.x, b2.y, base_z))
    a1 = Vector((a2.x, a2.y, foundation_top))
    b1 = Vector((b2.x, b2.y, foundation_top))
    a2t = Vector((a2.x, a2.y, roof_z))
    b2t = Vector((b2.x, b2.y, roof_z))
    add_quad((a0, b0, b1, a1), STONE)
    wall_height = roof_z - foundation_top
    add_quad((a1, b1, b2t, a2t), BRICK, ((0.0, 0.0), (length, 0.0), (length, wall_height), (0.0, wall_height)))

triangles = tessellate_polygon([ring])
for tri in triangles:
    indices = [int(i) for i in tri]
    # Top closure uses official plan vertices duplicated at roof height.
    for idx in indices:
        point = ring[idx]
        verts.append((point.x, point.y, roof_z))
    top_base = len(verts) - 3
    add_face((top_base, top_base + 1, top_base + 2), ROOF)
# Bottom closure uses a second triangulation to avoid relying on side winding.
for tri in triangles:
    indices = [int(i) for i in tri]
    for idx in indices:
        point = ring[idx]
        verts.append((point.x, point.y, base_z))
    bottom_base = len(verts) - 3
    add_face((bottom_base + 2, bottom_base + 1, bottom_base), ROOF)

# The current official exterior photograph shows two visible above-grade window rows.
# The GIS NUM_LEVELS=5 attribute is retained as conflicting source metadata; it is
# not used to invent five facade rows or a building height.
window_rows = [1.75, 5.0]
entry_edge = None
entry_point = None
entry_tangent = None
entry_normal = None
preferred_entry_y = (min_y + max_y) * 0.5 - 1.0
edge_data = []
for i, a in enumerate(ring):
    b = ring[(i + 1) % len(ring)]
    length, tangent, normal = edge_frame(a, b)
    edge_data.append((i, a, b, length, tangent, normal))
    if normal.x < -0.82 and length > 8.0 and min(a.y, b.y) <= preferred_entry_y <= max(a.y, b.y):
        entry_edge = i
        entry_tangent = tangent
        entry_normal = normal
        entry_point = a.lerp(b, (preferred_entry_y - a.y) / (b.y - a.y)) if abs(b.y - a.y) > 1e-6 else (a + b) * 0.5

for i, a, b, length, tangent, normal in edge_data:
    if length < 4.8:
        continue
    count = max(1, int((length - 1.8) // 3.4))
    bay_spacing = length / (count + 1)
    width = min(1.42, bay_spacing * 0.58)
    for row, zc in enumerate(window_rows):
        for bay in range(count):
            along = bay_spacing * (bay + 1)
            point = a.lerp(b, along / length)
            if i == entry_edge and row == 0 and abs(point.y - preferred_entry_y) < 2.2:
                continue
            pane_w = width * 0.78
            pane_h = 1.48
            # Glazing sits slightly proud of the wall so it reads at campus-map scale.
            glass_center = Vector((point.x, point.y, zc)) + normal * 0.065
            add_box(glass_center, tangent, normal, pane_w, 0.055, pane_h, GLASS)
            frame_center = Vector((point.x, point.y, zc)) + normal * 0.11
            frame = 0.095
            add_box(frame_center + Vector((0, 0, pane_h * 0.5)), tangent, normal, width, 0.16, frame, STONE)
            add_box(frame_center - Vector((0, 0, pane_h * 0.5)), tangent, normal, width, 0.18, frame, STONE)
            add_box(frame_center - tangent * (width * 0.5 - frame * 0.5), tangent, normal, frame, 0.16, pane_h, STONE)
            add_box(frame_center + tangent * (width * 0.5 - frame * 0.5), tangent, normal, frame, 0.16, pane_h, STONE)
            add_box(frame_center, tangent, normal, frame * 0.62, 0.17, pane_h * 0.96, METAL)

# Narrow limestone floor bands and a roof coping keep the brick elevation legible without changing the wall footprint.
for i, a, b, length, tangent, normal in edge_data:
    if length < 2.0:
        continue
    for zband in (4.0,):
        center = Vector(((a.x + b.x) * 0.5, (a.y + b.y) * 0.5, zband)) + normal * 0.025
        add_box(center, tangent, normal, length + 0.04, 0.10, 0.10, STONE)
    cap_center = Vector(((a.x + b.x) * 0.5, (a.y + b.y) * 0.5, roof_z - 0.20)) + normal * 0.08
    add_box(cap_center, tangent, normal, length + 0.18, 0.42, 0.40, STONE)

# Raised entrance tower, visible in Purdue's archival exterior photo. Its apex uses
# GIS field R=33.4 only as a tentative feet interpretation (the field units are not
# documented); the general 8 m wall/parapet remains a photo-scaled estimate.
if entry_edge is not None:
    # Let the tower project beyond the mapped wall line, as the entrance volume
    # appears to do in the archival oblique view. This projection is decorative.
    tower_center_xy = Vector((entry_point.x, entry_point.y)) - Vector((entry_normal.x, entry_normal.y)) * 1.1
    tower_height = max(HEIGHT_M, ENTRY_TOWER_HEIGHT_M)
    add_box(Vector((tower_center_xy.x, tower_center_xy.y, tower_height * 0.5)),
            entry_tangent, entry_normal, 7.2, 5.2, tower_height, BRICK)
    add_box(Vector((tower_center_xy.x, tower_center_xy.y, tower_height - 0.06)),
            entry_tangent, entry_normal, 7.34, 5.34, 0.12, STONE)
    # Tall glazed bay on the tower's street-facing side, matching the archival view.
    tower_front = Vector((tower_center_xy.x, tower_center_xy.y, 7.1)) + entry_normal * 2.65
    add_box(tower_front, entry_tangent, entry_normal, 3.8, 0.12, 5.4, GLASS)
    # Side glazing and a vertical sign panel remain schematic in size and placement.
    tower_side = Vector((tower_center_xy.x, tower_center_xy.y, 6.8)) + entry_tangent * 3.65
    add_box(tower_side, entry_normal, entry_tangent, 3.1, 0.12, 4.7, GLASS)
    tower_sign = Vector((tower_center_xy.x, tower_center_xy.y, 7.3)) + entry_normal * 2.73
    add_box(tower_sign, entry_tangent, entry_normal, 0.75, 0.10, 2.8, STONE)

# Main west-facing entrance with limestone surround, dark double glazing, and a shallow canopy.
if entry_edge is not None:
    p = Vector((entry_point.x, entry_point.y, 0.0))
    door_w, door_h = 2.25, 2.55
    door_center = p + entry_normal * 1.58 + Vector((0, 0, door_h * 0.5 + 0.05))
    add_box(door_center, entry_tangent, entry_normal, door_w, 0.08, door_h, GLASS)
    trim_center = p + entry_normal * 1.66 + Vector((0, 0, door_h * 0.5 + 0.05))
    trim = 0.24
    add_box(trim_center + Vector((0, 0, door_h * 0.5)), entry_tangent, entry_normal, door_w + 0.55, 0.24, trim, STONE)
    add_box(trim_center - entry_tangent * (door_w * 0.5 + trim * 0.5), entry_tangent, entry_normal, trim, 0.24, door_h, STONE)
    add_box(trim_center + entry_tangent * (door_w * 0.5 + trim * 0.5), entry_tangent, entry_normal, trim, 0.24, door_h, STONE)
    add_box(trim_center, entry_tangent, entry_normal, 0.10, 0.16, door_h * 0.92, METAL)
    canopy_center = p + entry_normal * 2.18 + Vector((0, 0, 3.05))
    add_box(canopy_center, entry_tangent, entry_normal, 4.2, 1.55, 0.22, STONE)
    for side in (-1, 1):
        pier_center = p + entry_normal * 2.28 + entry_tangent * (side * 1.75) + Vector((0, 0, 1.38))
        add_box(pier_center, entry_tangent, entry_normal, 0.30, 0.34, 2.76, STONE)
    plaque_center = p + entry_normal * 1.72 + Vector((0, 0, 3.65))
    add_box(plaque_center, entry_tangent, entry_normal, 3.8, 0.18, 0.55, ROOF)

# First-floor room arrangement from Purdue OEP's official BALY plan image. The plan
# has no north arrow or scale bar in the published page, so this is a labeled schematic
# inset mapped proportionally into the GIS envelope; room dimensions/orientation stay
# explicitly unverified. Names and room groupings follow the source plan itself.
def point_inside(poly, x, y):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-15) + xi):
            inside = not inside
        j = i
    return inside

room_regions = [
    ([(248,446),(377,446),(377,573),(248,573)], INTERIOR_REHEARSAL), # Lounge
    ([(484,108),(679,108),(725,155),(725,315),(680,330),(484,330)], INTERIOR_REHEARSAL), # L.R.1
    ([(482,410),(690,410),(690,573),(486,573)], INTERIOR_REHEARSAL), # L.R.2
    ([(687,420),(767,420),(767,573),(687,573)], INTERIOR_REHEARSAL), # S.R.2
    ([(767,410),(875,410),(875,573),(767,573)], INTERIOR_REHEARSAL), # S.R.1
    ([(382,331),(482,331),(482,446),(382,446)], INTERIOR_LOBBY),
    ([(249,215),(484,215),(484,330),(249,330)], INTERIOR_SUPPORT), # restrooms/custodial
    ([(759,108),(882,108),(882,339),(759,339)], INTERIOR_SUPPORT), # storage/services
    ([(687,215),(764,215),(764,319),(687,319)], INTERIOR_SUPPORT), # stairs
    ([(687,330),(759,330),(759,409),(687,409)], INTERIOR_SUPPORT), # telecom
]

# Rasterize source-backed room zones into a low-resolution first-floor plate, clipped
# to the actual GIS polygon. The image is rotated to fit its long axis to the GIS
# envelope; this establishes a visual schematic only, not georeferenced room geometry.
def inside_source_outline(x, y):
    return point_inside([(p.x,p.y) for p in ring], x, y)

cell = 0.55
x = min_x
while x + cell <= max_x:
    y = min_y
    while y + cell <= max_y:
        corners = [(x,y),(x+cell,y),(x+cell,y+cell),(x,y+cell)]
        if all(inside_source_outline(cx,cy) for cx,cy in corners):
            cx, cy = x + cell/2, y + cell/2
            local_x, local_y = cx - placement_x, cy - placement_y
            px = 569.0 + local_y * (893.0 - 245.0) / (max_y - min_y)
            py = 342.0 - local_x * (578.0 - 108.0) / (max_x - min_x)
            mat_index = INTERIOR_CIRCULATION
            for room_poly, room_mat in room_regions:
                if point_inside(room_poly, px, py):
                    mat_index = room_mat
                    break
            add_quad([(x,y,0.08),(x+cell,y,0.08),(x+cell,y+cell,0.08),(x,y+cell,0.08)], mat_index)
        y += cell
    x += cell

# Replace the original simplified extrusion while preserving its object, collection, and exported asset IDs.
old_mesh = obj.data
old_mesh_name = old_mesh.name
mesh = bpy.data.meshes.new(old_mesh_name + '_detail')
mesh.from_pydata(verts, [], faces)
mesh.materials.clear()
for mat in mats:
    mesh.materials.append(mat)
mesh.update()
for poly, mat_index in zip(mesh.polygons, face_materials):
    poly.material_index = mat_index
uv_layer = mesh.uv_layers.new(name='FacadeUV')
for poly, uv_coords in zip(mesh.polygons, face_uvs):
    if uv_coords and len(uv_coords) == len(poly.loop_indices):
        for loop_index, uv in zip(poly.loop_indices, uv_coords):
            uv_layer.data[loop_index].uv = uv
bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(mesh)
bm.free()
mesh.update()
obj.data = mesh
obj.location = (0.0, 0.0, 0.0)
obj.rotation_euler = (0.0, 0.0, 0.0)
obj.scale = (1.0, 1.0, 1.0)
if old_mesh.users == 0:
    bpy.data.meshes.remove(old_mesh)
mesh.name = old_mesh_name

# Convert all geometry from campus-world XY to local coordinates. The parent master
# collection instance should be placed at the GIS polygon centroid reported below.
for vertex in mesh.vertices:
    vertex.co.x -= placement_x
    vertex.co.y -= placement_y
mesh.update()
obj['asset_id'] = ASSET_ID
obj['gis_feature_id'] = int(attrs['FID'])
obj['proposed_master_placement_xy_m'] = [placement_x, placement_y]
obj['coordinate_frame'] = 'local geometry; placement at projected FID 411 polygon centroid'
obj['interior_status'] = 'first-floor room zones follow Purdue OEP plan; scale and north orientation are schematic/unverified'
obj['interior_source'] = 'Purdue OEP BALY first floor plan; page revision 2026-04-03'
obj['interior_schematic_assumptions'] = 'Room zones traced and proportionally fitted inside GIS outline; no plan scale or north arrow; dimensions, exact walls, and orientation unverified.'
obj['documented_first_floor_spaces'] = 'Lounge; Large Rehearsal 1; Large Rehearsal 2; Small Rehearsal 1; Small Rehearsal 2; Lobby; Reception; Restrooms; Custodial; Storage; Stairs; Telecom; Elevator; Vestibules; Sound Lock'

bpy.context.view_layer.update()
# Keep the asset portable and preserve all existing collection/scene names.
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

result = {
    'asset_id': ASSET_ID,
    'file': blend_path,
    'object': obj.name,
    'collection': collection.name,
    'source_fid': attrs['FID'],
    'source_vertices': len(ring),
    'mesh_vertices': len(mesh.vertices),
    'mesh_faces': len(mesh.polygons),
    'materials': [m.name for m in mats],
    'structural_bounds_xy_m': [[round(min_x, 3), round(max_x, 3)], [round(min_y, 3), round(max_y, 3)]],
    'proposed_master_placement_xy_m': [round(placement_x, 6), round(placement_y, 6)],
    'estimated_height_m': HEIGHT_M,
    'estimated_entry_tower_height_m': ENTRY_TOWER_HEIGHT_M,
    'floor_count_attribute': FLOOR_COUNT,
    'height_status': 'lower-wing parapet estimated at 7.5 m from Purdue exterior photos; entry tower apex estimated at 10.18 m by tentatively interpreting GIS R=33.4 as feet; field units are undocumented',
    'interior_status': 'schematic first-floor room zones mapped from official OEP plan; floor-plan scale and north orientation unavailable',
}
print('BUILD_RESULT_JSON=' + json.dumps(result))



