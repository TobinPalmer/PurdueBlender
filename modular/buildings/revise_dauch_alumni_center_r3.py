"""R3 corrections for the Dauch Alumni Center detailed asset.

Run in background with the current Dauch .blend open. Preserves the GIS XY
shell and local coordinate frame; fixes shell winding and curves the roof deck.
"""
import bpy
import bmesh
import os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSET = os.path.join(ROOT, "modular", "buildings", "dauch_alumni_center.blend")
AUDIT = os.path.join(ROOT, "audit", "dauch_alumni_center")
os.makedirs(AUDIT, exist_ok=True)
COL = bpy.data.collections.get("Asset_dauch_alumni_center")
assert COL and COL.name == "Asset_dauch_alumni_center"
shell = bpy.data.objects.get("dauch_alumni_center_GIS_outline_primary_shell")
roof = bpy.data.objects.get("DAUC_roof_membrane_surface")
assert shell and roof and shell.type == roof.type == "MESH"

# Shell side faces were wound inward. Flip the 109 vertical faces only; both
# horizontal cap faces were already correctly oriented and the GIS vertices
# are left in place.
bm = bmesh.new()
bm.from_mesh(shell.data)
bm.normal_update()
side_faces = [f for f in bm.faces if abs(f.normal.z) < 0.1]
assert len(side_faces) == 109, f"Expected 109 perimeter sides; found {len(side_faces)}"
before_volume = bm.calc_volume(signed=True)
flipped_count = 0
if before_volume < 0:
    for face in side_faces:
        face.normal_flip()
        flipped_count += 1
bm.normal_update()
caps = [f for f in bm.faces if abs(f.normal.z) > 0.9]
assert sorted(round(f.normal.z) for f in caps) == [-1, 1], "Upper/lower cap normals changed unexpectedly"
signed_volume = bm.calc_volume(signed=True)
assert signed_volume > 0, f"GIS shell signed volume still not positive: {signed_volume}"
bm.to_mesh(shell.data)
bm.free()
shell.data.update()

# A neutral, restrained standing-seam membrane makes the roof read as roofing,
# rather than as brick-shaded cap geometry. Fine noise is intentionally subtle.
roofmat = bpy.data.materials.get("DAUC_r3_curved_roof_membrane") or bpy.data.materials.new("DAUC_r3_curved_roof_membrane")
roofmat.diffuse_color = (0.24, 0.27, 0.28, 1.0)
roofmat.use_nodes = True
nodes = roofmat.node_tree.nodes
links = roofmat.node_tree.links
nodes.clear()
out = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Base Color"].default_value = (0.24, 0.27, 0.28, 1.0)
bsdf.inputs["Roughness"].default_value = 0.86
noise = nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 7.0
noise.inputs["Detail"].default_value = 2.0
bump = nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.09
bump.inputs["Distance"].default_value = 0.018
links.new(noise.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

if roofmat.name not in [m.name for m in shell.data.materials if m]:
    shell.data.materials.append(roofmat)
roof_index = next(i for i,m in enumerate(shell.data.materials) if m and m.name == roofmat.name)
topfaces = [p for p in shell.data.polygons if p.normal.z > 0.9]
assert len(topfaces) == 1, f"Expected one GIS top cap; found {len(topfaces)}"
topfaces[0].material_index = roof_index

# Subdivide the roof triangulation and lift the center of the long axis to form
# a restrained barrel-like arch. The edge still meets the original roof datum;
# the 0.90 m crown and paired coping follow the photographic curved roof profile.
roof_bm = bmesh.new()
roof_bm.from_mesh(roof.data)
roof_bm.normal_update()
if len(roof_bm.verts) < 200:
    bmesh.ops.subdivide_edges(roof_bm, edges=list(roof_bm.edges), cuts=3, use_grid_fill=True)
for vert in roof_bm.verts:
    x = vert.co.x
    norm_x = max(-1.0, min(1.0, x / 30.5))
    vert.co.z = 14.405 + 0.90 * (1.0 - norm_x * norm_x)
roof_bm.normal_update()
for face in roof_bm.faces:
    if face.normal.z < 0:
        face.normal_flip()
roof_bm.normal_update()
roof_bm.to_mesh(roof.data)
roof_bm.free()
roof.data.update()
if roofmat.name not in [m.name for m in roof.data.materials if m]:
    roof.data.materials.append(roofmat)
for poly in roof.data.polygons:
    poly.material_index = next(i for i,m in enumerate(roof.data.materials) if m and m.name == roofmat.name)
    poly.use_smooth = True

def roof_rise(x):
    t = max(-1.0, min(1.0, x / 30.5))
    return 0.90 * (1.0 - t*t)

# Raise coping and rooftop equipment with the roof profile so the parapet and
# services continue to sit on the roof rather than being sunk into the crown.
shifted = []
for obj in COL.all_objects:
    if obj.name.startswith("DAUC_roof_coping_") or obj.name in {
        "DAUC_roof_mechanical_screen", "DAUC_roof_exhaust_stack_0",
        "DAUC_roof_exhaust_stack_1", "DAUC_roof_exhaust_stack_2",
        "DAUC_roof_exhaust_stack_3"
    }:
        world_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        center_x = sum(p.x for p in world_corners) / len(world_corners)
        desired_shift = roof_rise(center_x)
        previous_shift = float(obj.get("dauch_r3_roof_shift_m", 0.0))
        obj.location.z += desired_shift - previous_shift
        obj["dauch_r3_roof_shift_m"] = desired_shift
        shifted.append(obj.name)

# R2 noted faceted low-poly shrub clusters; retain their photo-based placement
# while smoothing the existing meshes.
for obj in COL.all_objects:
    if obj.name.startswith("DAUC_site_sign_") and "evergreen" in obj.name:
        if obj.type == "MESH":
            for poly in obj.data.polygons:
                poly.use_smooth = True

# Fresh local-coordinate bounds include decorative assets and the south sign.
depsgraph = bpy.context.evaluated_depsgraph_get()
world_pts = []
for obj in COL.all_objects:
    if obj.type not in {"MESH", "CURVE", "FONT", "SURFACE", "META"}:
        continue
    eval_obj = obj.evaluated_get(depsgraph)
    world_pts.extend(obj.matrix_world @ Vector(corner) for corner in eval_obj.bound_box)
assert world_pts
local_bounds = [
    [min(p[i] for p in world_pts) for i in range(3)],
    [max(p[i] for p in world_pts) for i in range(3)]
]

bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print("DAUC_R3_SAVED", {"shell_signed_volume_before_m3":before_volume, "shell_side_faces_flipped":flipped_count, "shell_signed_volume_after_m3":signed_volume, "roof_vertex_count":len(roof.data.vertices), "roof_crown_m":0.90, "roof_related_objects_shifted":len(shifted), "local_full_asset_bounds":local_bounds})
