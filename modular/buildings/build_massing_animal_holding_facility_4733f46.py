"""Build the Animal Holding Facility from official Purdue and Indiana footprint records.

The footprint remains in the project's campus coordinate frame. Vertical dimensions
are diagrammatic: the GIS reports one level, but its extrusion field has no unit
definition. Run with Blender 4.5 from the repository root.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/massing_animal_holding_facility_4733f46.blend"
SOURCE = ROOT / "audit/animal_holding_facility/sources/purdue_gis_fid266_2026-10-25.json"
OUT = ROOT / "audit/animal_holding_facility"
COLLECTION = "Asset_massing_animal_holding_facility_4733f46"
SCENE = "Building_massing_animal_holding_facility_4733f46"

feature = json.loads(SOURCE.read_text(encoding="utf-8"))["features"][0]
ring = feature["geometry"]["rings"][0]
points = []
for lon, lat in ring[:-1]:
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    y = (lat - 40.4274) * 111040.0
    points.append((x, y))
assert len(points) == 16 and ring[0] == ring[-1], (len(points), ring[0], ring[-1])

# GIS confirms one occupied level. A conservative 4.8 m envelope is a modeling
# estimate only; the service's Extrution=12 has no documented vertical units.
WALL_H = 4.4
ROOF_H = 0.4
WALL_THICKNESS = 0.28

scene = bpy.context.scene
scene.name = SCENE
col = bpy.data.collections.get(COLLECTION)
if col is None:
    col = bpy.data.collections.new(COLLECTION)
    scene.collection.children.link(col)
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

def material(name, color, roughness=0.82):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    if shader:
        shader.inputs["Base Color"].default_value = (*color, 1.0)
        shader.inputs["Roughness"].default_value = roughness
    return mat

wall_mat = material("AHF | neutral masonry (diagrammatic)", (0.60, 0.60, 0.56))
roof_mat = material("AHF | low roof (form unverified)", (0.28, 0.30, 0.29))
trim_mat = material("AHF | perimeter trim", (0.42, 0.43, 0.40))

verts, faces, face_materials = [], [], []

def add_box(center, axes, sizes, material_index):
    cx, cy, cz = center
    ax, ay = axes
    sx, sy, sz = (s / 2 for s in sizes)
    base = len(verts)
    for dz in (-sz, sz):
        for dy in (-sy, sy):
            for dx in (-sx, sx):
                verts.append((cx + ax[0] * dx + ay[0] * dy,
                              cy + ax[1] * dx + ay[1] * dy, cz + dz))
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    for q in quads:
        faces.append(tuple(base + i for i in q))
        face_materials.append(material_index)

for i, p0 in enumerate(points):
    p1 = points[(i + 1) % len(points)]
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    tangent = (dx / length, dy / length)
    normal = (-tangent[1], tangent[0])
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    add_box((mid[0], mid[1], WALL_H / 2), (tangent, normal),
            (length + 0.04, WALL_THICKNESS, WALL_H), 0)
    add_box((mid[0], mid[1], WALL_H + ROOF_H / 2), (tangent, normal),
            (length + 0.04, 0.36, ROOF_H), 2)

# Fill the roof as a triangulated polygon, keeping the exact GIS outline.
poly = [[Vector((x, y, 0.0)) for x, y in points]]
triangles = tessellate_polygon(poly)
roof_base = len(verts)
verts.extend((x, y, WALL_H + ROOF_H) for x, y in points)
verts.extend((x, y, WALL_H) for x, y in points)
n = len(points)
for tri in triangles:
    ids = tuple(roof_base + i for i in tri)
    faces.append(ids)
    face_materials.append(1)
    faces.append(tuple(roof_base + n + i for i in reversed(tri)))
    face_materials.append(1)

mesh = bpy.data.meshes.new("Animal Holding Facility | GIS-derived envelope")
mesh.from_pydata(verts, [], faces)
mesh.materials.clear()
for mat in (wall_mat, roof_mat, trim_mat):
    mesh.materials.append(mat)
mesh.update()
obj = bpy.data.objects.new("Animal Holding Facility", mesh)
col.objects.link(obj)
for poly_face, material_index in zip(mesh.polygons, face_materials):
    poly_face.material_index = material_index

# Set up an audit preview camera and lighting; these remain outside the asset collection.
center_x = sum(p[0] for p in points) / len(points)
center_y = sum(p[1] for p in points) / len(points)
camera_data = bpy.data.cameras.new("AHF Preview Camera")
camera = bpy.data.objects.new("AHF Preview Camera", camera_data)
scene.collection.objects.link(camera)
camera.location = (center_x - 62, center_y - 74, 56)
target = Vector((center_x, center_y, WALL_H / 2))
camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.type = "ORTHO"
camera_data.ortho_scale = 112
scene.camera = camera
light_data = bpy.data.lights.new("AHF Preview Sun", "SUN")
light = bpy.data.objects.new("AHF Preview Sun", light_data)
scene.collection.objects.link(light)
light.rotation_euler = (math.radians(28), math.radians(-22), math.radians(-32))
light_data.energy = 2.0
scene.render.engine = "CYCLES"
scene.cycles.samples = 24
scene.render.resolution_x = 1200
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(OUT / "animal_holding_facility_preview.png")
scene.world.color = (0.16, 0.17, 0.18)

OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
bpy.ops.render.render(write_still=True)

evidence = {
    "building_id": "massing_animal_holding_facility_4733f46",
    "asset": "modular/buildings/massing_animal_holding_facility_4733f46.blend",
    "collection": COLLECTION,
    "source_feature_id": 266,
    "geometry_source": "audit/animal_holding_facility/sources/purdue_gis_fid266_2026-10-25.json",
    "method": "Project the official Purdue GIS exterior ring using the project-prescribed approximate local conversion; preserve campus coordinates and original manifest identity.",
    "footprint_vertices": len(points),
    "vertical_model": {"levels": 1, "wall_height_m": WALL_H, "roof_cap_m": ROOF_H,
                       "status": "diagrammatic estimate; GIS Extrution=12 has undocumented units"},
    "facade": "Neutral unfenestrated envelope; current facade and entrances unverified because no dated exterior imagery or elevations were found.",
    "roof": "Low flat diagrammatic cap; roof form unverified.",
    "preview": "audit/animal_holding_facility/animal_holding_facility_preview.png"
}
(OUT / "build_evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
