"""Refine the Lambert Fieldhouse R8 library candidate without editing shared files.

The script improves material scale/relief, corrects the review renders, and
removes the GIS-outline stone-band object that reads as disconnected context.
All source-supported massing/footprint/track meshes stay at their current transforms.
"""
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "lambert_fieldhouse"
SOURCE = AUDIT / "lambert_fieldhouse_r8_candidate.blend"
OUTPUT = AUDIT / "lambert_fieldhouse_r9_candidate.blend"

bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene

def node(material, kind, label=None):
    n = material.node_tree.nodes.new(kind)
    if label:
        n.label = label
    return n

def color_material(material_name, color_low, color_high, color_scale,
                   relief_scale, relief_distance, roughness=None):
    mat = bpy.data.materials.get(material_name)
    if not mat:
        return None
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        bsdf = node(mat, "ShaderNodeBsdfPrincipled")
    output = nodes.get("Material Output") or node(mat, "ShaderNodeOutputMaterial")
    if not any(l.from_node == bsdf and l.to_node == output for l in links):
        links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    # Reset only the nodes owned by this function; leave any material-specific
    # shader inputs and existing external links intact.
    for n in list(nodes):
        if n.get("LAMB_R9_texture"):
            nodes.remove(n)
    tex = node(mat, "ShaderNodeTexCoord", "R9 real-scale object coordinates")
    tex["LAMB_R9_texture"] = True
    broad = node(mat, "ShaderNodeTexNoise", "R9 surface color variation")
    broad["LAMB_R9_texture"] = True
    broad.inputs["Scale"].default_value = color_scale
    broad.inputs["Detail"].default_value = 3.0
    broad.inputs["Roughness"].default_value = 0.72
    ramp = node(mat, "ShaderNodeValToRGB", "R9 restrained material variation")
    ramp["LAMB_R9_texture"] = True
    ramp.color_ramp.elements[0].position = 0.2
    ramp.color_ramp.elements[0].color = (*color_low, 1.0)
    ramp.color_ramp.elements[1].position = 0.8
    ramp.color_ramp.elements[1].color = (*color_high, 1.0)
    links.new(tex.outputs["Object"], broad.inputs["Vector"])
    links.new(broad.outputs["Fac"], ramp.inputs["Fac"])
    # Keep the R8 packed brick image as the color source: the exterior brick
    # relief should remain mapped to actual brick courses instead of replacing
    # them with noise. Other materials get subtle procedurally varied color.
    has_packed_brick_image = (material_name == "LAMB | mottled Purdue red-brown brick"
                              and any(n.bl_idname == "ShaderNodeTexImage" and n.image
                                      for n in nodes))
    if not has_packed_brick_image:
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    fine = node(mat, "ShaderNodeTexNoise", "R9 fine scale relief")
    fine["LAMB_R9_texture"] = True
    fine.inputs["Scale"].default_value = relief_scale
    fine.inputs["Detail"].default_value = 2.0
    fine.inputs["Roughness"].default_value = 0.8
    links.new(tex.outputs["Object"], fine.inputs["Vector"])
    bump = node(mat, "ShaderNodeBump", "R9 subtle, scale-appropriate relief")
    bump["LAMB_R9_texture"] = True
    bump.inputs["Strength"].default_value = 0.16
    bump.inputs["Distance"].default_value = relief_distance
    links.new(fine.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    if roughness is not None:
        bsdf.inputs["Roughness"].default_value = roughness
    # The scene uses fully opaque masonry and an opaque weather roof. Avoid the
    # old hashed-material roof that exposed internal light geometry in renders.
    if hasattr(mat, "blend_method"):
        mat.blend_method = "OPAQUE"
    if hasattr(mat, "surface_render_method"):
        try:
            mat.surface_render_method = "DITHERED"
        except Exception:
            pass
    return mat

# Procedural colors and bump use object coordinates, so values are in meter-
# sized model space instead of being stretched over each object as a single
# gradient. These are subdued enough to retain the established material palette.
color_material("LAMB | mottled Purdue red-brown brick",
               (0.25, 0.070, 0.045), (0.39, 0.125, 0.082), 2.8, 48.0, 0.018, 0.78)
color_material("LAMB | warm pale limestone concrete round5",
               (0.43, 0.43, 0.39), (0.58, 0.57, 0.51), 2.1, 52.0, 0.012, 0.84)
color_material("LAMB | cast concrete",
               (0.37, 0.39, 0.37), (0.52, 0.53, 0.50), 2.0, 46.0, 0.014, 0.87)
color_material("LAMB | entrance context shadow-lift concrete",
               (0.39, 0.41, 0.39), (0.51, 0.52, 0.49), 1.8, 42.0, 0.012, 0.9)
color_material("LAMB | Stadium Avenue asphalt schematic",
               (0.095, 0.11, 0.105), (0.16, 0.17, 0.16), 0.9, 34.0, 0.008, 0.94)
color_material("LAMB | weathered membrane / standing seam",
               (0.19, 0.21, 0.22), (0.26, 0.28, 0.29), 1.3, 48.0, 0.009, 0.72)
color_material("LAMB | Rekortan-like red synthetic track",
               (0.27, 0.018, 0.022), (0.39, 0.035, 0.039), 5.0, 96.0, 0.0035, 0.72)
color_material("LAMB | round6 gym limestone",
               (0.44, 0.44, 0.41), (0.57, 0.57, 0.53), 2.2, 48.0, 0.012, 0.82)
color_material("LAMB | round6 gym glazing",
               (0.16, 0.25, 0.29), (0.20, 0.30, 0.34), 2.0, 45.0, 0.002, 0.28)

# All hurdle components need an intentional slot. R8 already supplied a Purdue-
# red/white crossbar; retain that material and add a low-gloss dark finish for
# the steel uprights and feet.
hurdle_steel = bpy.data.materials.get("LAMB | R9 hurdle upright and foot steel")
if hurdle_steel is None:
    hurdle_steel = bpy.data.materials.new("LAMB | R9 hurdle upright and foot steel")
hurdle_steel.diffuse_color = (0.12, 0.16, 0.17, 1.0)
hurdle_steel.use_nodes = True
hurdle_bsdf = hurdle_steel.node_tree.nodes.get("Principled BSDF")
if hurdle_bsdf:
    hurdle_bsdf.inputs["Base Color"].default_value = (0.12, 0.16, 0.17, 1.0)
    hurdle_bsdf.inputs["Metallic"].default_value = 0.48
    hurdle_bsdf.inputs["Roughness"].default_value = 0.38
hurdle_crossbar = bpy.data.materials.get("LAMB | R8 painted hurdle crossbar")
for obj in bpy.data.objects:
    if not obj.name.startswith("LAMB | R8 event hurdle") or obj.type != "MESH":
        continue
    if obj.name.endswith("crossbar") and hurdle_crossbar:
        mat = hurdle_crossbar
    else:
        mat = hurdle_steel
    if not obj.data.materials:
        obj.data.materials.append(mat)
    elif obj.data.materials[0] is None:
        obj.data.materials[0] = mat
    else:
        obj.data.materials[0] = mat

# Existing stone accents attached to the entrance and gym remain. Remove the
# full GIS perimeter-derived band mesh: its dimensions include an unresolved
# part of the U-shaped footprint and it reads as detached white rails around
# the illustrative hall/gym allocation. The actual GIS ground footprint remains.
misleading = bpy.data.objects.get("LAMB | round6 GIS-registered segmented perimeter stone bands")
if misleading:
    bpy.data.objects.remove(misleading, do_unlink=True)
# The earlier datum family was also drawn along the complete GIS polygon,
# including its open/notched edges. It creates horizontal white runs beyond the
# archival hall/gym volume hypothesis, so delete those unsourced facade lines.
for obj in list(bpy.data.objects):
    if obj.name.startswith("LAMB | level 1 horizontal datum"):
        bpy.data.objects.remove(obj, do_unlink=True)
# The matching south clerestory strip sits on a GIS edge outside both
# unregistered archival-volume hypotheses, so it reads as a floating line.
# Keep the north clerestory, which aligns with the hall envelope, and omit the
# unsupported south strip rather than pretending it is a surveyed facade.
south_clerestory = bpy.data.objects.get("LAMB | translucent clerestory band")
if south_clerestory:
    bpy.data.objects.remove(south_clerestory, do_unlink=True)
# The wall-banner strip at y=66.65 is outside the retained GIS footprint and
# beyond the 303 x 172 ft archival fieldhouse envelope; those banners had no
# supporting wall or source-verified location. Remove only that detached row.
removed_unlocated_banners = 0
for obj in list(bpy.data.objects):
    if (obj.name.startswith("LAMB | schematic wall banner") or
        obj.name.startswith("LAMB | schematic banner gold stripe")) and obj.location.y > 50.0:
        bpy.data.objects.remove(obj, do_unlink=True)
        removed_unlocated_banners += 1
# Historical postcard tower geometry is already hidden in the source candidate,
# and no current source verifies that it survives. Remove those hidden conjecture
# meshes from the exported asset so they cannot contaminate extents or placement.
removed_unverified_tower = 0
for obj in list(bpy.data.objects):
    if "round5 tower" in obj.name.lower() or "historic-only postcard tower" in obj.name.lower():
        bpy.data.objects.remove(obj, do_unlink=True)
        removed_unverified_tower += 1

# Stadium Avenue roadway, curb, and continuous 98 m sidewalk belong to site
# context and must not ship inside the building-only modular export. The campus
# master is responsible for roads/context, so these are removed from this asset.
removed_context_site_objects = []
for name in ("LAMB | Stadium sidewalk round4", "LAMB | Stadium curb round4", "LAMB | Stadium Avenue roadway round4"):
    obj = bpy.data.objects.get(name)
    if obj:
        removed_context_site_objects.append(name)
        bpy.data.objects.remove(obj, do_unlink=True)

# Preserve the actual model geometry, but eliminate the old material glow that
# caused paving to read as chalk-white in the exterior review render.
for mat_name in ("LAMB | entrance context shadow-lift concrete",):
    mat = bpy.data.materials.get(mat_name)
    if mat and mat.use_nodes:
        principled = mat.node_tree.nodes.get("Principled BSDF")
        if principled:
            emission = principled.inputs.get("Emission Strength")
            if emission:
                emission.default_value = 0.0

# Stabilize saved review cameras. Exterior is a low 3/4 view of the south entry
# and long arched fieldhouse while keeping the separate gym volume visible.
def aim_camera(name, location, target, lens=48):
    cam = bpy.data.objects.get(name)
    if cam is None:
        data = bpy.data.cameras.new(name + " data")
        cam = bpy.data.objects.new(name, data)
        bpy.context.scene.collection.objects.link(cam)
    cam.location = Vector(location)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.type = "PERSP"
    cam.data.lens = lens
    return cam

exterior = aim_camera("LAMB | three-quarter preview camera", (120, -124, 71), (0, -2, 7), 48)
interior = aim_camera("LAMB | interior review camera", (16, -54, 76), (0, 20.75, 0), 45)
interior.data.type = "ORTHO"
interior.data.ortho_scale = 99
event_cam = aim_camera("LAMB | R8 event detail review camera", (24, -6, 13), (8, 8.5, 0.55), 48)
event_cam.data.type = "ORTHO"
event_cam.data.ortho_scale = 44

scene.render.engine = "CYCLES"
scene.cycles.samples = 32
scene.render.resolution_x = 1440
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"
scene.camera = exterior

def render(path):
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)

# Hide the explicitly named context pavements from the building-only view;
# they remain in the asset and are documented as site context, not building.
temporarily_hidden = []
for obj in bpy.data.objects:
    if (obj.name in (
        "LAMB | Stadium sidewalk round4",
        "LAMB | Stadium curb round4",
        "LAMB | Stadium Avenue roadway round4",
        "LAMB | schematic overhead linear luminaires",
        ) or (obj.type == "LIGHT" and ("interior" in obj.name.lower() or "high-bay" in obj.name.lower())) or
        any(col.name == "LAMB_Roof" for col in obj.users_collection) and obj is not bpy.data.objects.get("LAMB | GIS-registered archival-dimension fieldhouse roof (R7 hypothesis)") or
        (obj.name.startswith("LAMB | level 1 horizontal datum")) or
        False):
        temporarily_hidden.append((obj, obj.hide_render))
        obj.hide_render = True
render(AUDIT / "exterior_round9.png")
for obj, old in temporarily_hidden:
    obj.hide_render = old

# Create a deliberate interior cutaway: remove shell, roof and gym roof slabs
# only during this evidence render. The final blend retains the complete model.
cutaway_hidden = []
for obj in bpy.data.objects:
    if (obj.name in (
        "Lambert Fieldhouse | GIS perimeter wall panels with real glazing openings",
        "LAMB | GIS-registered archival-dimension fieldhouse roof (R7 hypothesis)",
        "LAMB | GIS-registered gym roof slab (R8 hypothesis; gym interior schematic)",
        "LAMB | schematic overhead linear luminaires",
        "LAMB | Stadium sidewalk round4",
        "LAMB | Stadium curb round4",
        "LAMB | Stadium Avenue roadway round4",
        "Lambert Fieldhouse | official GIS footprint ground floor",
        "LAMB | R8 Purdue Track and Field infield mark",
    ) or obj.name.startswith("LAMB | round6 gym interior floor plate") or
        obj.name.startswith("LAMB | round5 upper spectator balcony") or
        obj.name.startswith("LAMB | round5 balcony") or
        any(term in obj.name.lower() for term in ("scoreboard", "display", "banner")) or
        any(col.name in ("LAMB_Facade", "LAMB_Structure", "LAMB_Roof") for col in obj.users_collection)):
        cutaway_hidden.append((obj, obj.hide_render))
        obj.hide_render = True
scene.camera = interior
render(AUDIT / "interior_round9_cutaway.png")
for obj, old in cutaway_hidden:
    obj.hide_render = old
scene.camera = event_cam
for obj, old in cutaway_hidden:
    obj.hide_render = True
render(AUDIT / "interior_event_round9.png")
for obj, old in cutaway_hidden:
    obj.hide_render = old

# Restore an informative exterior as the file's default camera; no evidence-
# only hide flags are serialized into the production asset.
scene.camera = exterior
scene.render.filepath = "//"
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))

# Save/reopen and validate the final serialized candidate before returning.
bpy.ops.wm.open_mainfile(filepath=str(OUTPUT))
scene = bpy.context.scene
collection = bpy.data.collections.get("Asset_lambert_fieldhouse")
if collection is None:
    raise RuntimeError("Asset_lambert_fieldhouse export collection missing")
objs = list(collection.all_objects)
unassigned = [o.name for o in objs if o.type == "MESH" and (not o.data.materials or all(m is None for m in o.data.materials))]
track = bpy.data.objects.get("LAMB | 6-lane 200 m stadium track surface")
lane_count = sum(1 for o in bpy.data.objects if o.name.startswith("LAMB | lane boundary "))
track_centerline_perimeter = None
if track and len(track.data.vertices) % 2 == 0:
    half_count = len(track.data.vertices) // 2
    centers = [(track.data.vertices[i].co + track.data.vertices[i + half_count].co) * 0.5 for i in range(half_count)]
    track_centerline_perimeter = sum((centers[(i + 1) % half_count] - centers[i]).length for i in range(half_count))
footprint = bpy.data.objects.get("Lambert Fieldhouse | official GIS footprint ground floor")
footprint_bounds = None
if footprint:
    footprint_bounds = {"min": [min(v.co.x for v in footprint.data.vertices), min(v.co.y for v in footprint.data.vertices)],
                        "max": [max(v.co.x for v in footprint.data.vertices), max(v.co.y for v in footprint.data.vertices)]}
asset_points = [o.matrix_world @ Vector(corner) for o in objs for corner in o.bound_box if o.type in {"MESH", "CURVE"}]
asset_bounds_world = None
if asset_points:
    asset_bounds_world = {"min": [min(v[i] for v in asset_points) for i in range(3)], "max": [max(v[i] for v in asset_points) for i in range(3)]}
def object_bounds(obj):
    points = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return {"min": [min(v[i] for v in points) for i in range(3)], "max": [max(v[i] for v in points) for i in range(3)]}
hall_roof = bpy.data.objects.get("LAMB | GIS-registered archival-dimension fieldhouse roof (R7 hypothesis)")
gym_roof = bpy.data.objects.get("LAMB | GIS-registered gym roof slab (R8 hypothesis; gym interior schematic)")
wall_shell = bpy.data.objects.get("Lambert Fieldhouse | GIS perimeter wall panels with real glazing openings")
context_names = {"LAMB | Stadium sidewalk round4", "LAMB | Stadium curb round4", "LAMB | Stadium Avenue roadway round4"}
context_meshes_remaining = [o.name for o in objs if o.name in context_names]

# Re-render all evidence from the exact saved file after reopening it. The
# cutaway visibility is temporary and restored before validation is written.
def hide_for_review(predicate):
    changed=[]
    for o in bpy.data.objects:
        if predicate(o):
            changed.append((o, o.hide_render))
            o.hide_render=True
    return changed

def restore_review(changed):
    for o, value in changed:
        o.hide_render=value

review_exterior = bpy.data.objects.get("LAMB | three-quarter preview camera")
review_interior = bpy.data.objects.get("LAMB | interior review camera")
review_event = bpy.data.objects.get("LAMB | R8 event detail review camera")
scene.camera = review_exterior
hidden = hide_for_review(lambda o:
    o.name in {"LAMB | Stadium sidewalk round4", "LAMB | Stadium curb round4", "LAMB | Stadium Avenue roadway round4", "LAMB | schematic overhead linear luminaires"} or
    (o.type == "LIGHT" and ("interior" in o.name.lower() or "high-bay" in o.name.lower())) or
    (any(c.name == "LAMB_Roof" for c in o.users_collection) and o is not bpy.data.objects.get("LAMB | GIS-registered archival-dimension fieldhouse roof (R7 hypothesis)")))
render(AUDIT / "exterior_round9.png")
restore_review(hidden)
hidden = hide_for_review(lambda o:
    o.name in {"Lambert Fieldhouse | GIS perimeter wall panels with real glazing openings",
               "LAMB | GIS-registered archival-dimension fieldhouse roof (R7 hypothesis)",
               "LAMB | GIS-registered gym roof slab (R8 hypothesis; gym interior schematic)",
               "LAMB | schematic overhead linear luminaires", "LAMB | Stadium sidewalk round4",
               "LAMB | Stadium curb round4", "LAMB | Stadium Avenue roadway round4",
               "Lambert Fieldhouse | official GIS footprint ground floor", "LAMB | R8 Purdue Track and Field infield mark"} or
    o.name.startswith("LAMB | round6 gym interior floor plate") or
    o.name.startswith("LAMB | round5 upper spectator balcony") or o.name.startswith("LAMB | round5 balcony") or
    any(t in o.name.lower() for t in ("scoreboard", "display", "banner")) or
    any(c.name in {"LAMB_Facade", "LAMB_Structure", "LAMB_Roof"} for c in o.users_collection))
scene.camera = review_interior
render(AUDIT / "interior_round9_cutaway.png")
scene.camera = review_event
render(AUDIT / "interior_event_round9.png")
restore_review(hidden)

report = {
    "revision": 9,
    "candidate": str(OUTPUT),
    "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
    "fresh_reopen": "PASS",
    "collection": collection.name,
    "collection_objects": len(objs),
    "collection_meshes": sum(o.type == "MESH" for o in objs),
    "unassigned_mesh_materials": unassigned,
    "material_nodes": {m.name: {"node_count": len(m.node_tree.nodes) if m.use_nodes else 0,
                                 "procedural_bump": any(n.bl_idname == "ShaderNodeBump" and n.get("LAMB_R9_texture") for n in m.node_tree.nodes) if m.use_nodes else False}
                       for m in bpy.data.materials if m.name.startswith("LAMB |")},
    "removed_detached_gis_band_object": bpy.data.objects.get("LAMB | round6 GIS-registered segmented perimeter stone bands") is None,
    "removed_unregistered_south_clerestory_strip": bpy.data.objects.get("LAMB | translucent clerestory band") is None,
    "removed_detached_north_wall_banner_count": removed_unlocated_banners,
    "removed_hidden_unverified_historic_tower_objects": removed_unverified_tower,
    "opaque_roof": {"blend_method": getattr(bpy.data.materials.get("LAMB | weathered membrane / standing seam"), "blend_method", None),
                    "surface_render_method": getattr(bpy.data.materials.get("LAMB | weathered membrane / standing seam"), "surface_render_method", None)},
    "track_mesh_dimensions_m": list(track.dimensions) if track else None,
    "track_lane_boundary_count": lane_count,
    "track_lane_one_centerline_perimeter_m": track_centerline_perimeter,
    "gis_footprint_bounds_local_m": footprint_bounds,
    "asset_bounds_world_m": asset_bounds_world,
    "rechecked_geometry_bounds_world_m": {"fieldhouse_roof": object_bounds(hall_roof) if hall_roof else None,
                                          "gym_roof_slab": object_bounds(gym_roof) if gym_roof else None,
                                          "gis_wall_shell": object_bounds(wall_shell) if wall_shell else None},
    "elevation_source_status": {"fieldhouse_wall_shell_height_model_m": list(wall_shell.dimensions)[2] if wall_shell else None,
                                "fieldhouse_roof_eave_and_crown_model_m": [object_bounds(hall_roof)["min"][2], object_bounds(hall_roof)["max"][2]] if hall_roof else None,
                                "gym_roof_slab_top_model_m": object_bounds(gym_roof)["max"][2] if gym_roof else None,
                                "archive_verifies_story_count_only": "one-story fieldhouse; four-story gym; no measured elevations or floor-to-floor heights",
                                "all_model_heights": "illustrative estimates, not verified measurements"},
    "review_cameras": [o.name for o in bpy.data.objects if o.type == "CAMERA"],
    "unassigned_hurdle_meshes": [o.name for o in objs if o.type == "MESH" and o.name.startswith("LAMB | R8 event hurdle") and (not o.data.materials or all(m is None for m in o.data.materials))],
    "brick_image_textures": [{"image": n.image.name, "packed": bool(n.image.packed_file)} for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.bl_idname == "ShaderNodeTexImage" and n.image],
    "archival_dimensions": {"fieldhouse_plan_m": [92.3544, 52.4256], "gym_plan_m": [64.008, 33.528], "gym_four_story_envelope_height": "estimated, not measured"},
    "volume_registration": "Illustrative local placement hypothesis. Purdue Archives plan dimensions are not georegistered to the current U-shaped GIS outline; no geometric recentering or rescaling performed in R9.",
    "gis_recheck": {"source_feature": 261, "source_crs": "WGS84 geographic, converted with the project's documented local approximate conversion", "footprint_geometry_changed_in_r9": False, "hall_gym_local_allocation": "not georeferenced by available archives; relative positions remain hypotheses and portions intersect/open beyond notched footprint regions", "registration_status": "unchanged, unresolved; only unlocated decorative bands removed"},
    "model_source_dimensions_conversion": {"fieldhouse": "303 x 172 ft = 92.3544 x 52.4256 m", "gymnasium": "210 x 110 ft = 64.008 x 33.528 m", "method": "source feet multiplied by exactly 0.3048 m/ft"},
    "removed_nonbuilding_site_context_objects": removed_context_site_objects,
    "nonbuilding_site_context_meshes_remaining_in_export": context_meshes_remaining,
    "previews": ["audit/lambert_fieldhouse/exterior_round9.png", "audit/lambert_fieldhouse/interior_round9_cutaway.png", "audit/lambert_fieldhouse/interior_event_round9.png"],
    "final_file_writes": [str(OUTPUT)],
}
(AUDIT / "validation_round9.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
