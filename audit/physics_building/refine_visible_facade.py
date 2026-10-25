"""Add source-backed masonry, roof relief, and low basement windows."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_PATH = ROOT / "modular/buildings/physics_building_phys_3bf42f3.blend"
bpy.ops.wm.open_mainfile(filepath=str(ASSET_PATH))
asset = bpy.data.collections.get("Asset_physics_building")
if asset is None:
    raise RuntimeError("Expected Physics Building asset collection")
for ob in list(asset.all_objects):
    if ob.name.startswith("PHYS NW | basement sash"):
        bpy.data.objects.remove(ob, do_unlink=True)

def find(name):
    ob = bpy.data.objects.get(name)
    if ob is None:
        raise RuntimeError(f"Missing expected source object: {name}")
    return ob

shell = find("PHYS | GIS footprint brick envelope")
roof = find("PHYS | estimated sloped red tile roof")
window_mesh = find("PHYS | recessed dark sash glazing")
trim_mesh = find("PHYS | pale limestone window surrounds")
base_ring = [v.co.copy() for v in shell.data.vertices if abs(v.co.z) < 1e-5]
if len(base_ring) != 33:
    raise RuntimeError(f"GIS shell base ring changed: expected 33 vertices, got {len(base_ring)}")

# Keep the exact footprint. Rebuild only the roof surface as faceted slopes
# from the source outline eaves up to a long ridge, using the photo-supported
# red clay roof and the existing 52.25 ft roof datum estimate.
a, b = base_ring[0], base_ring[2]
axis = (b - a).normalized()
cross = Vector((-axis.y, axis.x, 0.0))
eaves = [v.co.copy() for v in roof.data.vertices[:33]]
ridge_points = []
for p in eaves:
    s = p.x * axis.x + p.y * axis.y
    ridge_points.append(Vector((axis.x * s, axis.y * s, 15.92)))
roof_mesh = bpy.data.meshes.new("PHYS pitched roof | source-footprint ridge surfaces")
roof_mesh.from_pydata([tuple(p) for p in eaves + ridge_points], [], [
    (i, (i + 1) % 33, 33 + (i + 1) % 33, 33 + i) for i in range(33)
])
roof_mesh.materials.append(roof.data.materials[0])
roof_mesh.update()
roof.data = roof_mesh
top = list(roof.data.vertices)[33:]
roof.data.update()
roof["roof_profile_note"] = "Shallow pitched hip/gable relief interpreted from Purdue exterior photos; eave/ridge elevations remain estimates, top GIS plan ring unchanged."

# Make the red-brown facade read as running-bond brick at campus scale. The
# mesh receives per-face facade UVs: horizontal distance along each GIS edge
# and true vertical height. The texture is portable procedural Blender data.
brick = bpy.data.materials.get("PHYSICS_BUILDING | evidence palette textured masonry")
if brick is None:
    raise RuntimeError("Textured masonry material missing")
brick.use_nodes = True
tree = brick.node_tree
bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
coords = next((n for n in tree.nodes if n.type == "TEX_COORD"), None)
if coords is None:
    coords = tree.nodes.new("ShaderNodeTexCoord")
mapping = tree.nodes.new("ShaderNodeMapping")
mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
tree.links.new(coords.outputs["UV"], mapping.inputs["Vector"])
bricktex = tree.nodes.new("ShaderNodeTexBrick")
bricktex.inputs["Color1"].default_value = (.38, .075, .042, 1)
bricktex.inputs["Color2"].default_value = (.53, .12, .068, 1)
bricktex.inputs["Mortar"].default_value = (.24, .20, .16, 1)
bricktex.inputs["Scale"].default_value = 1.0
bricktex.inputs["Mortar Size"].default_value = .012
bricktex.inputs["Mortar Smooth"].default_value = .03
bricktex.inputs["Brick Width"].default_value = .22
bricktex.inputs["Row Height"].default_value = .075
tree.links.new(mapping.outputs["Vector"], bricktex.inputs["Vector"])
tree.links.new(bricktex.outputs["Color"], bsdf.inputs["Base Color"])
bump = next((n for n in tree.nodes if n.type == "BUMP"), None) or tree.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = .16
bump.inputs["Distance"].default_value = .035
tree.links.new(bricktex.outputs["Fac"], bump.inputs["Height"])
if not bsdf.inputs["Normal"].is_linked:
    tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
brick["surface_note"] = "Procedural fired-red running-bond brick and mortar, based on Purdue facade photographs; no image dependency."

# Wrap each GIS side quad with meter-based UVs so the brick bond remains
# horizontal on differently oriented facade edges instead of stretching into
# vertical stripes. The original source vertices and footprint stay fixed.
uv = shell.data.uv_layers.get("Purdue wall brick UV") or shell.data.uv_layers.new(name="Purdue wall brick UV")
for poly in shell.data.polygons:
    ids = list(poly.vertices)
    if len(ids) == 4 and ids[0] < 33 and ids[1] < 33 and ids[2] >= 33 and ids[3] >= 33:
        p0 = shell.data.vertices[ids[0]].co
        p1 = shell.data.vertices[ids[1]].co
        edge = (Vector((p1.x - p0.x, p1.y - p0.y, 0))).length
        zbase = p0.z
        for li, vid in zip(poly.loop_indices, ids):
            point = shell.data.vertices[vid].co
            if vid in (ids[0], ids[3]):
                ucoord = 0.0
            else:
                ucoord = edge
            uv.data[li].uv = (ucoord, point.z - zbase)
    elif len(ids) >= 3:
        for li, vid in zip(poly.loop_indices, ids):
            point = shell.data.vertices[vid].co
            uv.data[li].uv = (point.x, point.y)
for polygon in shell.data.polygons:
    polygon.material_index = 0
shell.data.materials.clear()
shell.data.materials.append(brick)
shell.data.update()

# The roof remains red clay, but add a subtle tile variation and relief.
roofmat = bpy.data.materials.get("PHYSICS_BUILDING | evidence palette roof")
roofmat.use_nodes = True
rnt = roofmat.node_tree
rbsdf = next(n for n in rnt.nodes if n.type == "BSDF_PRINCIPLED")
rcoords = next((n for n in rnt.nodes if n.type == "TEX_COORD"), None) or rnt.nodes.new("ShaderNodeTexCoord")
rnoise = rnt.nodes.new("ShaderNodeTexNoise")
rnoise.inputs["Scale"].default_value = 6.0
rnoise.inputs["Detail"].default_value = 3.0
rramp = rnt.nodes.new("ShaderNodeValToRGB")
rramp.color_ramp.elements[0].position = .25
rramp.color_ramp.elements[0].color = (.22, .042, .025, 1)
rramp.color_ramp.elements[1].position = .78
rramp.color_ramp.elements[1].color = (.54, .14, .075, 1)
rnt.links.new(rcoords.outputs["Object"], rnoise.inputs["Vector"])
rnt.links.new(rnoise.outputs["Fac"], rramp.inputs["Fac"])
rnt.links.new(rramp.outputs["Color"], rbsdf.inputs["Base Color"])
rbump = rnt.nodes.new("ShaderNodeBump")
rbump.inputs["Strength"].default_value = .10
rbump.inputs["Distance"].default_value = .025
rnt.links.new(rnoise.outputs["Fac"], rbump.inputs["Height"])
if not rbsdf.inputs["Normal"].is_linked:
    rnt.links.new(rbump.outputs["Normal"], rbsdf.inputs["Normal"])

# Strengthen continuous horizontal stone courses on the three principal levels.
for ob in asset.all_objects:
    low = ob.name.lower()
    if ob.type != "MESH" or "limestone story belt" not in low:
        continue
    zmin = min(v.co.z for v in ob.data.vertices)
    zmax = max(v.co.z for v in ob.data.vertices)
    if zmax - zmin >= .19:
        continue
    mid = (zmin + zmax) * .5
    for v in ob.data.vertices:
        v.co.z = mid + (v.co.z - mid) * 1.8
    ob.data.update()
    ob["detail_note"] = "Wider limestone story course, visible in Purdue exterior reference; exact trim width estimated."

# The source facade photo shows a distinct low basement window tier below the
# regular story windows. Model 13 small sash openings only along the verified
# northwest frontage; keep the footprint and wall envelope untouched.
front_a, front_b = base_ring[0], base_ring[2]
front_t = (front_b - front_a).normalized()
front_n = Vector((-front_t.y, front_t.x, 0.0))
front_mid = (front_a + front_b) * .5 + front_t * 1.5
glass = bpy.data.materials.get("PHYSICS_BUILDING | evidence palette glazing")
stone = bpy.data.materials.get("PHYS | warm Indiana limestone")
asset_root = bpy.context.scene.collection

def add_box(name, center, dimensions, material, angle):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.rotation_euler.z = angle
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    asset.objects.link(ob)
    ob.data.materials.append(material)
    ob["source_note"] = "Small below-grade windows visible in official Purdue Physics road-side photograph; dimensions/spacing estimated."
    return ob

angle = math.atan2(front_t.y, front_t.x)
for i in range(13):
    s = -19.0 + i * (38.0 / 12.0)
    p = front_mid + front_t * s + front_n * .21
    add_box(f"PHYS NW | basement sash glazing {i+1:02d}", p + Vector((0, 0, .67)), (1.05, .08, .72), glass, angle)
    for side in (-1, 1):
        add_box(f"PHYS NW | basement sash jamb {i+1:02d} {side}", p + front_t * (side * .56) + Vector((0, 0, .67)), (.10, .12, .84), stone, angle)
    for dz in (-.42, .42):
        add_box(f"PHYS NW | basement sash sill {i+1:02d} {dz}", p + Vector((0, 0, .67 + dz)), (1.18, .12, .09), stone, angle)

# Lift existing full-size window tiers to leave room for the source-visible
# basement tier and create the three tall above-grade rows seen in photos.
def shift_quads(obj, row_offsets):
    mesh = obj.data
    for poly in mesh.polygons:
        center_z = sum(mesh.vertices[i].co.z for i in poly.vertices) / len(poly.vertices)
        if center_z < 3.1:
            delta = row_offsets[0]
        elif center_z < 7.2:
            delta = row_offsets[1]
        elif center_z < 11.3:
            delta = row_offsets[2]
        else:
            continue
        for i in poly.vertices:
            mesh.vertices[i].co.z += delta
    mesh.update()

first_row = [sum(window_mesh.data.vertices[i].co.z for i in p.vertices) / len(p.vertices)
             for p in window_mesh.data.polygons]
if first_row and min(first_row) < 2.0:
    shift_quads(window_mesh, (.48, .44, .48))
    shift_quads(trim_mesh, (.48, .44, .48))

asset["facade_revision"] = "NW road frontage gains three glazed entries, readable PHYSICS sign, small basement sash row, stronger pale story courses, procedural running-bond masonry and a shallow red-tile pitched roof; estimates remain labeled."
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH), compress=True)
print(json.dumps({"asset": str(ASSET_PATH), "basement_windows": 13, "roof_top_vertices": len(top), "roof_pitch_source": "Purdue official exterior photo; R_ft 52.25 datum is estimated"}))
