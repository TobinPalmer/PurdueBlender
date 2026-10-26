"""Build Rawls Hall R11 candidate from the assigned R10 asset."""
import bpy, hashlib, json, math, shutil
from pathlib import Path
from mathutils import Vector

root = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
src = root / "modular/buildings/rawls_hall.blend"
candidate = root / "audit/batch4_rawls/rawls_hall_r11_candidate.blend"
shutil.copy2(src, candidate)
bpy.ops.wm.open_mainfile(filepath=str(candidate))
coll = bpy.data.collections["Asset_rawls_hall"]
asset_hash = hashlib.sha256(src.read_bytes()).hexdigest()
expected = "d361f211a8177e234d475493d6242ad396981b7f3fed29dc57f37f54e1026d9e"
assert asset_hash == expected, f"Unexpected R10 source hash: {asset_hash}"

# Keep the 42 plan-derived tabletop locations. The 2023 Purdue 1086 guide lists
# 62 seats; twenty existing chair meshes are duplicated at the opposite table
# edge to document capacity. This is a schematic seating arrangement, not a
# claim that the plan supplies exact chair coordinates or table dimensions.
desks = sorted([o for o in bpy.data.objects if o.name.startswith("RAWL_2026_1086_Desk") and o.type == "MESH"], key=lambda o:o.name)
chairs = sorted([o for o in bpy.data.objects if o.name.startswith("RAWL_2026_1086_Chair") and o.type == "MESH"], key=lambda o:o.name)
assert len(desks) == len(chairs) == 42, (len(desks), len(chairs))
existing_pairs = {d.name.replace("Desk", "Chair"):d for d in desks}
assert all(c.name in existing_pairs for c in chairs)
new_seats = []
# Five desks per four rows, then three per two rows: twenty additional seats.
for row, count in enumerate([4, 3, 3, 3, 4, 3]):
    row_desks = desks[row*7:(row+1)*7]
    # Choose interleaved seat positions within each row to preserve clear aisles.
    picks = [0, 2, 4, 6][:count] if count == 4 else [1, 3, 5][:count]
    for local_idx in picks:
        desk = row_desks[local_idx]
        source = bpy.data.objects[desk.name.replace("Desk", "Chair")]
        seat = source.copy()
        seat.data = source.data
        seat.name = f"RAWL_2026_1086_Chair_R11_Seat_{len(new_seats)+1:02d}"
        coll.objects.link(seat)
        # Existing chairs sit at the west edge of each table; mirror to the east.
        seat.location.x = desk.location.x + (desk.location.x - source.location.x)
        seat.location.y = desk.location.y + (desk.location.y - source.location.y)
        seat.location.z = source.location.z
        seat["seat_count_basis"] = "Additional schematic chair; Purdue RAWL 1086 guide (2023) lists 62 seats."
        seat["arrangement_limit"] = "Position is illustrative; guide does not provide a dimensioned seat plan."
        new_seats.append(seat)
assert len(new_seats) == 20

# Put both documented projection surfaces where the existing pane/wall sightline
# check verifies visibility, without changing either room wall or exterior panes.
glass = bpy.data.objects["RAWL_SE_Diagonal_CurtainWall_Glass"]
base_obj = bpy.data.objects["RAWL_1086_R10_Schematic_Projection_Surface_01"]
base = base_obj.matrix_world.translation.copy()
tangent = Vector((math.cos(-1.27), math.sin(-1.27), 0.0))
screen_names = ["RAWL_1086_R10_Schematic_Projection_Surface_01", "RAWL_1086_R10_Schematic_Projection_Surface_02"]
screen_offsets = [-6.0, -5.0]
screen_centers=[]
for i,(name,offset) in enumerate(zip(screen_names,screen_offsets), start=1):
    obj = bpy.data.objects[name]
    loc = base + tangent*offset
    obj.location = loc
    obj.dimensions = (0.90, 0.055, 0.68)
    bpy.context.view_layer.update()
    obj["r11_note"] = "Dual-projection cue repositioned for a verified through-pane sightline; size/location remain schematic, not plan-surveyed."
    obj["source_note"] = "Purdue 2023 RAWL 1086 guide documents dual projectors; no exact screen size or position is published."
    screen_centers.append(obj.matrix_world.translation.copy())

# Give the two sourced projector surfaces enough contrast to read through the
# tinted curtain wall. The inset marks are generic projection cues, not copied
# slide content or evidence of a particular room AV layout.
screen_mat=bpy.data.materials.get("RAWL_R11_Projection_Screen_Luminous") or bpy.data.materials.new("RAWL_R11_Projection_Screen_Luminous")
screen_mat.use_nodes=True
screen_bsdf=next(n for n in screen_mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
screen_bsdf.inputs["Base Color"].default_value=(0.88,0.88,0.78,1)
screen_bsdf.inputs["Roughness"].default_value=0.82
screen_bsdf.inputs["Emission Color"].default_value=(0.85,0.88,0.78,1)
screen_bsdf.inputs["Emission Strength"].default_value=1.5
screen_mat.diffuse_color=(0.88,0.88,0.78,1)
screen_mat["r11_note"]="Screen luminance is a render-legibility treatment, not a measured projection brightness."
for n in screen_names:
    obj=bpy.data.objects[n]
    obj.data.materials.clear(); obj.data.materials.append(screen_mat)

content_mat=bpy.data.materials.get("RAWL_R11_Projection_Content_Cool") or bpy.data.materials.new("RAWL_R11_Projection_Content_Cool")
content_mat.use_nodes=True
content_bsdf=next(n for n in content_mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
content_bsdf.inputs["Base Color"].default_value=(0.10,0.23,0.30,1)
content_bsdf.inputs["Roughness"].default_value=0.8
content_bsdf.inputs["Emission Color"].default_value=(0.08,0.17,0.22,1)
content_bsdf.inputs["Emission Strength"].default_value=0.18

pane2=glass.data.polygons[2]
pane2_center=sum((glass.matrix_world@glass.data.vertices[i].co for i in pane2.vertices),Vector())/len(pane2.vertices)
for si,center in enumerate(screen_centers, start=1):
    view_offset=(pane2_center-center).normalized()*0.04
    for bi,zoff in enumerate([-0.11,0.0,0.11], start=1):
        bpy.ops.mesh.primitive_cube_add(size=1, location=center+view_offset+Vector((0,0,zoff)))
        bar=bpy.context.object; bar.name=f"RAWL_1086_R11_Projector_Content_{si:02d}_{bi:02d}"
        bar.dimensions=(0.40,0.014,0.018); bar.rotation_euler[2]=-1.27
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for c in list(bar.users_collection): c.objects.unlink(bar)
        coll.objects.link(bar); bar.data.materials.append(content_mat)
        bar["r11_note"]="Abstract screen-content cue for readability only; not a source-derived slide or user interface."

# Rebuild the two horizontal screen rails at the compact R11 panel bounds.
for i, (center, offset) in enumerate(zip(screen_centers, screen_offsets), start=1):
    for suffix,zoff in [("top",0.375),("bottom",-0.375)]:
        obj=bpy.data.objects.get(f"RAWL_1086_R10_Screen_Frame_{i:02d}_{suffix}")
        if obj:
            obj.location=center+Vector((0,0,zoff))
            obj.dimensions=(0.98,0.07,0.055)
            obj["r11_note"]="Frame adjusted with the illustrative R11 screen position."

# Soften glass reflections further in response to the independent review.
# This remains a visual estimate; the actual glazing specification is unknown.
mat=bpy.data.materials["RAWL_CurtainWall_Glass"]
bsdf=next(n for n in mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
bsdf.inputs["Roughness"].default_value=0.26
bsdf.inputs["Transmission Weight"].default_value=0.90
bsdf.inputs["Coat Weight"].default_value=0.0
bsdf.inputs["Specular IOR Level"].default_value=0.04
mat.diffuse_color=(0.56,0.66,0.70,0.72)
mat["r11_note"]="Higher roughness/lower specular reduces reflected highlight for interior legibility; visual estimate, not a sourced glazing specification."

bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(candidate))
result={"source_sha256":asset_hash,"candidate":str(candidate),"desk_count":len(desks),"original_chair_count":len(chairs),"additional_schematic_chairs":len(new_seats),"total_chair_objects":len(chairs)+len(new_seats),"screen_positions":[[round(v,4) for v in p] for p in screen_centers],"glass":{"roughness":0.26,"transmission":0.90,"specular_ior":0.04},"pane_count":len(glass.data.polygons),"wall_geometry_changed":False}
(root/"audit/batch4_rawls/round11_change_set.json").write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
