"""Source-guided R3 refinement of Stanley Coulter Hall; standalone asset only."""
from __future__ import annotations

import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/stanley_coulter_hall.blend"
AUDIT = ROOT / "audit/batch3_stanley"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
root = bpy.data.objects["AssetRoot_stanley_coulter_hall"]
asset_collection = bpy.data.collections["Asset_stanley_coulter_hall"]
portico_collection = bpy.data.collections["SC_Portico_and_Entrances"]


def world_vertices(obj):
    return [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]


def replace_world_mesh(obj, verts_world, faces, face_material_indices=None):
    inv = obj.matrix_world.inverted()
    mesh = bpy.data.meshes.new(obj.name + "_R3Mesh")
    mesh.from_pydata([inv @ Vector(v) for v in verts_world], [], faces)
    for material in obj.data.materials:
        mesh.materials.append(material)
    mesh.update()
    if face_material_indices:
        for poly, material_index in zip(mesh.polygons, face_material_indices):
            poly.material_index = min(material_index, max(0, len(mesh.materials) - 1))
    old = obj.data
    obj.data = mesh
    if old.users == 0:
        bpy.data.meshes.remove(old)


# Remove detached, unsupported horizontal frame scraps floating above every third-floor window.
# The frame source meshes contain separate quads at the real opening and a stray quad at z≈20.8 m.
removed_floating_faces = 0
fixed_window_frames = 0
for obj in list(asset_collection.all_objects):
    if obj.type != "MESH" or not obj.name.endswith("_BronzeFrame"):
        continue
    if not ("Level3_ThirdFloor" in obj.name or "_F3_" in obj.name):
        continue
    wverts = world_vertices(obj)
    kept_faces = []
    kept_mats = []
    for poly in obj.data.polygons:
        face = list(poly.vertices)
        if max(wverts[i].z for i in face) > 13.5:
            removed_floating_faces += 1
            continue
        kept_faces.append(face)
        kept_mats.append(poly.material_index)
    if len(kept_faces) != len(obj.data.polygons):
        used = sorted({i for face in kept_faces for i in face})
        remap = {old: new for new, old in enumerate(used)}
        verts = [wverts[i] for i in used]
        faces = [[remap[i] for i in face] for face in kept_faces]
        replace_world_mesh(obj, verts, faces, kept_mats)
        fixed_window_frames += 1


# Widen the source-facing east-facade openings into paired/grouped window units.
# The current Purdue CLA photograph supports wider grouped openings and a distinct upper band.
# Size factors are visual estimates; only the official GIS foundation is a measured plan outline.
factors = {
    "Level0_Basement": (1.28, 1.0),
    "Level1_FirstFloor": (1.42, 1.0),
    "Level2_SecondFloor": (1.52, 1.0),
    "Level3_ThirdFloor": (1.58, 0.84),
    "_F2_": (1.32, 1.0),
    "_F3_": (1.42, 0.84),
}
scaled_windows = 0
for obj in list(asset_collection.all_objects):
    if obj.type != "MESH" or not obj.name.startswith("SC_Win_East_"):
        continue
    if not obj.name.endswith(("_GlassPane", "_LimestoneTrim", "_BronzeFrame")):
        continue
    chosen = next((pair for token, pair in factors.items() if token in obj.name), None)
    if chosen is None:
        continue
    width_factor, height_factor = chosen
    # Restrict the F3/Level3 adjustment to window vertices after the unsupported z≈20.8 face is gone.
    wverts = world_vertices(obj)
    cy = sum(v.y for v in wverts) / len(wverts)
    cz = sum(v.z for v in wverts) / len(wverts)
    inv = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        q = obj.matrix_world @ vertex.co
        q.y = cy + (q.y - cy) * width_factor
        q.z = cz + (q.z - cz) * height_factor
        vertex.co = inv @ q
    obj.data.update()
    scaled_windows += 1


# Shape the stone stair cheeks to follow the stair run instead of reading as two tall solid walls.
# The short top edge sits about 0.65 m above the approximate tread line; heights remain estimated.
sloped_cheeks = []
for name in ["SC_Portico_Balustrade_North", "SC_Portico_Balustrade_South"]:
    obj = bpy.data.objects[name]
    wverts = world_vertices(obj)
    xmin = min(v.x for v in wverts)
    xmax = max(v.x for v in wverts)
    for i, point in enumerate(wverts):
        if point.z > 1.0:
            t = (point.x - xmin) / max(1e-6, xmax - xmin)
            point.z = 2.45 - t * 1.80
        wverts[i] = point
    faces = [list(poly.vertices) for poly in obj.data.polygons]
    material_indices = [poly.material_index for poly in obj.data.polygons]
    replace_world_mesh(obj, wverts, faces, material_indices)
    sloped_cheeks.append(name)


# Add continuous steel handrails and short brackets above the stair cheeks, as seen in the
# current Purdue entrance photo. Each rail follows the tread rise; its exact dimensions are estimated.
rail_material = bpy.data.materials.get("Dark_Bronze_Framing")
if rail_material is None:
    rail_material = bpy.data.materials.new("SC_R3_Entry_Rail_Metal")
    rail_material.diffuse_color = (0.10, 0.12, 0.13, 1.0)
    rail_material.use_nodes = True
    rail_bsdf = next((n for n in rail_material.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if rail_bsdf:
        rail_bsdf.inputs["Base Color"].default_value = (0.12, 0.14, 0.15, 1.0)
        rail_bsdf.inputs["Metallic"].default_value = 0.68
        rail_bsdf.inputs["Roughness"].default_value = 0.32


def append_cylinder(verts, faces, a, b, radius, sides=12):
    a, b = Vector(a), Vector(b)
    axis = (b - a).normalized()
    ref = Vector((0, 0, 1)) if abs(axis.z) < 0.92 else Vector((0, 1, 0))
    u = axis.cross(ref).normalized()
    v = axis.cross(u).normalized()
    base = len(verts)
    for center in (a, b):
        for i in range(sides):
            angle = 2.0 * math.pi * i / sides
            p = center + radius * (math.cos(angle) * u + math.sin(angle) * v)
            verts.append(tuple(p))
    faces.append(tuple(base + i for i in range(sides - 1, -1, -1)))
    faces.append(tuple(base + sides + i for i in range(sides)))
    for i in range(sides):
        j = (i + 1) % sides
        faces.append((base + i, base + j, base + sides + j, base + sides + i))


rail_verts, rail_faces = [], []
rail_side_y = {
    "north": -2.225,
    "south": -5.670,
}
x0, x1 = 28.82, 32.19
wall_top_start, wall_top_end = 2.45, 0.65
rail_lift = 0.16


def wall_top(x):
    return wall_top_start + (x - x0) / (x1 - x0) * (wall_top_end - wall_top_start)


for side, y in rail_side_y.items():
    append_cylinder(rail_verts, rail_faces,
                    (x0, y, wall_top(x0) + rail_lift),
                    (x1, y, wall_top(x1) + rail_lift), 0.035, 16)
    for step in range(7):
        x = x0 + (x1 - x0) * step / 6.0
        z0 = wall_top(x)
        append_cylinder(rail_verts, rail_faces,
                        (x, y, z0 + 0.015),
                        (x, y, z0 + rail_lift), 0.022, 12)

mesh = bpy.data.meshes.new("SC_R3_Entry_HandrailsMesh")
mesh.from_pydata(rail_verts, [], rail_faces)
mesh.materials.append(rail_material)
mesh.update()
rail_obj = bpy.data.objects.get("SC_R3_Entry_Handrails")
if rail_obj is None:
    rail_obj = bpy.data.objects.new("SC_R3_Entry_Handrails", mesh)
    portico_collection.objects.link(rail_obj)
    rail_obj.parent = root
else:
    old = rail_obj.data
    rail_obj.data = mesh
    if old.users == 0:
        bpy.data.meshes.remove(old)


# Subtle material corrections track the source photo: warm limestone, grouped reflective glazing,
# and a slightly warmer/less featureless roof. Procedural surface noise already exists in the asset.
stone = bpy.data.materials.get("Bedford_Indiana_Limestone")
if stone and stone.use_nodes:
    mix = stone.node_tree.nodes.get("Mix")
    if mix and len(mix.inputs) > 7:
        mix.inputs[6].default_value = (0.64, 0.53, 0.40, 1.0)
        mix.inputs[7].default_value = (0.48, 0.37, 0.27, 1.0)
        mix.inputs[0].default_value = 0.62
    stone.diffuse_color = (0.57, 0.46, 0.34, 1.0)
    principled = next((n for n in stone.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if principled:
        principled.inputs["Roughness"].default_value = 0.78

glass = bpy.data.materials.get("Architectural_Glazing")
if glass and glass.use_nodes:
    principled = next((n for n in glass.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if principled:
        principled.inputs["Base Color"].default_value = (0.12, 0.20, 0.24, 1.0)
        principled.inputs["Metallic"].default_value = 0.20
        principled.inputs["Roughness"].default_value = 0.18
        if "Transmission Weight" in principled.inputs:
            principled.inputs["Transmission Weight"].default_value = 0.12
        if "Alpha" in principled.inputs:
            principled.inputs["Alpha"].default_value = 0.94
    glass.diffuse_color = (0.12, 0.20, 0.24, 1.0)

roof = bpy.data.materials.get("Historic_Slate_Roof_Procedural")
if roof and roof.use_nodes:
    mix = roof.node_tree.nodes.get("Mix")
    if mix and len(mix.inputs) > 7:
        mix.inputs[6].default_value = (0.16, 0.125, 0.10, 1.0)
        mix.inputs[7].default_value = (0.075, 0.075, 0.07, 1.0)
        mix.inputs[0].default_value = 0.58
    principled = next((n for n in roof.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if principled:
        principled.inputs["Roughness"].default_value = 0.82

# Preserve the identity frame and exactly source-matched GIS foundation; only one wall section and
# visible source-supported facade details are altered in this pass.
if list(root.location) != [0.0, 0.0, 0.0] or any(abs(v - 1.0) > 1e-6 for v in root.scale):
    raise RuntimeError("Stanley asset root changed unexpectedly")
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
digest = hashlib.sha256(ASSET.read_bytes()).hexdigest()
result = {
    "round": 3,
    "asset": str(ASSET),
    "sha256": digest,
    "asset_object_count": len(asset_collection.all_objects),
    "removed_floating_bronze_frame_faces": removed_floating_faces,
    "bronze_frame_objects_repaired": fixed_window_frames,
    "east_window_meshes_widened_or_reproportioned": scaled_windows,
    "stone_stair_cheeks_sculpted_to_stair_slope": sloped_cheeks,
    "added_entry_handrail_mesh": rail_obj.name,
    "root_transform": {"location": list(root.location), "rotation": list(root.rotation_euler), "scale": list(root.scale)},
    "limitations": ["Roof form and total height remain unverified/estimated.", "Facade window widths are qualitative visual estimates from the Purdue CLA photo.", "Interior arrangement is schematic from historical plans, not current as-built documentation."]
}
(AUDIT / "build_r3.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
