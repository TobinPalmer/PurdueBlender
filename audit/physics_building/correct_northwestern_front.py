"""Correct the Physics Building's Northwestern Avenue entry frontage."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[2]
ASSET_PATH = ROOT / "modular/buildings/physics_building_phys_3bf42f3.blend"
bpy.ops.wm.open_mainfile(filepath=str(ASSET_PATH))
asset = bpy.data.collections.get("Asset_physics_building")
if asset is None:
    raise RuntimeError("Expected asset collection is missing")

# The 34-point clockwise GIS outline has a straight northwest-facing frontage
# across source vertices 0–2. Purdue's photos show the principal three-door
# entrance centered on this long face. The prior camera-selected portal landed
# on a recessed courtyard edge, so remove only that incorrectly placed revision.
discard = (
    "PHYS NW |",
    "PHYS | full-height double entry glazing",
    "PHYS | massive carved stone portal jamb",
    "PHYS | carved arch spring course",
    "PHYS | carved arched portal voussoir ring",
    "PHYS | broad limestone entry step",
    "PHYS | PHYSICS carved lintel plaque",
    "PHYS | building name engraving",
    "PHYS | arched upper-window limestone surround",
    "PHYS | tall upper arch window glazing",
    "PHYS | fanlight mullion",
    "PHYS | entry lamp base",
    "PHYS | entry lamp bronze post",
    "PHYS | entry lamp lantern",
    "PHYS | prominent central physics name",
    "PHYSICS_BUILDING | schematic vestibule visible through entry",
    "PHYSICS_BUILDING | schematic entry walk",
    "PHYSICS_BUILDING | schematic entry planter",
    "PHYSICS_BUILDING | low planter planting",
)
for obj in list(asset.all_objects):
    if any(obj.name.startswith(prefix) if prefix.endswith(" |") else (obj.name == prefix or obj.name.startswith(prefix + ".")) for prefix in discard):
        bpy.data.objects.remove(obj, do_unlink=True)

shell = bpy.data.objects.get("PHYS | GIS footprint brick envelope")
if shell is None or shell.type != "MESH":
    raise RuntimeError("GIS footprint shell is missing")
base = [v.co.copy() for v in shell.data.vertices if abs(v.co.z) < 1e-5]
if len(base) != 33:
    raise RuntimeError(f"Expected 33 non-repeated GIS base vertices, found {len(base)}")
a, b = base[0], base[2]
tangent = (b - a).normalized()
# The outline is clockwise, so its exterior is the left-hand normal.
normal = Vector((-tangent.y, tangent.x, 0.0))
angle = math.atan2(tangent.y, tangent.x)
center = (a + b) * 0.5 + tangent * 1.5

stone = bpy.data.materials.get("PHYS | warm Indiana limestone")
glass = bpy.data.materials.get("PHYSICS_BUILDING | evidence palette glazing")
metal = bpy.data.materials.get("PHYSICS_BUILDING | graphite metal details")
wood = bpy.data.materials.get("PHYS | dark bronze metal")
if not all((stone, glass, metal, wood)):
    raise RuntimeError("Expected portable Physics materials are missing")

def box(name, loc, dims, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.rotation_euler.z = angle
    for old in list(ob.users_collection):
        old.objects.unlink(ob)
    asset.objects.link(ob)
    if mat:
        ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new("Entry stone eased edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    ob["evidence_note"] = "Northwestern Avenue entry composition observed in Purdue Physics exterior photographs; dimensions estimated."
    return ob

def point(s=0.0, outward=0.22, z=0.0):
    return center + tangent * s + normal * outward + Vector((0, 0, z))

# Three separate glazed door bays beneath the long PHYSICS name panel, matching
# the official road-side facade photograph. Each bay has a stone surround,
# transom, and shallow projecting limestone hood.
for i, s in enumerate((-3.5, 0.0, 3.5), 1):
    box(f"PHYS NW | entrance {i} dark glazed doors", point(s, .18, 1.36), (2.05, .09, 2.65), glass, .012)
    for side in (-1, 1):
        box(f"PHYS NW | entrance {i} limestone jamb {side}", point(s + side * 1.16, .30, 1.48), (.24, .42, 2.98), stone, .025)
    box(f"PHYS NW | entrance {i} limestone head", point(s, .30, 2.98), (2.56, .42, .24), stone, .025)
    box(f"PHYS NW | entrance {i} glazed transom", point(s, .17, 3.28), (2.05, .08, .32), glass, .01)
    box(f"PHYS NW | entrance {i} stone hood", point(s, .53, 3.52), (3.10, .90, .26), stone, .035)
    box(f"PHYS NW | entrance {i} door stile", point(s, .25, 1.37), (.075, .12, 2.48), metal, .008)

# A continuous carved sign bay and engraved identity above the three door hoods.
box("PHYS NW | limestone PHYSICS sign panel", point(0, .34, 4.12), (14.6, .34, .78), stone, .035)
curve = bpy.data.curves.new("PHYS NW | PHYSICS sign lettering", "FONT")
curve.body = "PHYSICS"
curve.align_x = "CENTER"
curve.size = .57
curve.extrude = .004
label = bpy.data.objects.new("PHYS NW | PHYSICS sign lettering", curve)
asset.objects.link(label)
rot = Matrix((-tangent, Vector((0, 0, 1)), normal)).transposed()
label.rotation_euler = rot.to_euler()
label.location = point(0, .53, 3.91)
label.data.materials.append(metal)
label["evidence_note"] = "Permanent building-name panel visible in Purdue Physics exterior photos."

# A broad, low three-riser stone approach ties the entry group to grade.
for j in range(3):
    box(f"PHYS NW | broad entry stair {j+1}", point(0, .92 + j * .42, .10 + j * .12), (15.4, 1.05, .18), stone, .018)

# Warm glazed vestibule cue is expressly schematic; Purdue's public evacuation
# plan identifies the main entrance, but does not disclose an as-built interior.
interior = bpy.data.materials.new("PHYS NW | schematic vestibule glow")
interior.diffuse_color = (.55, .28, .09, 1)
interior.use_nodes = True
bsdf = next(n for n in interior.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
bsdf.inputs["Base Color"].default_value = (.55, .28, .09, 1)
if "Emission Color" in bsdf.inputs:
    bsdf.inputs["Emission Color"].default_value = (.36, .12, .025, 1)
    bsdf.inputs["Emission Strength"].default_value = .16
box("PHYS NW | schematic warm vestibule visible through doors", point(0, -.08, 1.35), (8.9, .06, 2.3), interior, .0)

asset["northwest_entry_revision"] = "Principal three-door PHYSICS entrance repositioned to the exposed Northwestern Avenue facade (GIS outline vertices 0–2); photo-supported composition, dimensions interpretive."
asset["northwest_entry_revision_source"] = "Purdue Events Physics Building 2022 photo; Purdue Physics campus resources exterior image; official evacuation plan identifies Northwestern Avenue/main entrance."
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH), compress=True)
print(json.dumps({"asset": str(ASSET_PATH), "front_center_local_m": list(center), "front_tangent_xy": [tangent.x, tangent.y], "front_normal_xy": [normal.x, normal.y], "doors": 3}))
