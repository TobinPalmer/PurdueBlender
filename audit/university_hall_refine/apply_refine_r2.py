"""University Hall architectural refinement, run from Blender 5.2 background.

Only edits the standalone building asset. Coordinates are its existing local
frame, with the original root, origin, footprint and campus placement intact.
"""
import bpy
import math
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "university_hall.blend"
COLLECTION = bpy.data.collections["Asset_university_hall"]
ASSET_ROOT = bpy.data.objects["AssetRoot_university_hall"]
CX, CY = -7.515, 0.0


def mat(name):
    return bpy.data.materials[name]


def box(name, loc, dims, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    COLLECTION.objects.link(ob)
    ob.parent = ASSET_ROOT
    ob.matrix_parent_inverse = ASSET_ROOT.matrix_world.inverted()
    if material:
        ob.data.materials.append(material)
    if bevel:
        mod = ob.modifiers.new("Soft dressed edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        ob.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return ob


def mesh_obj(name, verts, faces, material, bevel=0.0):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    COLLECTION.objects.link(ob)
    ob.parent = ASSET_ROOT
    ob.matrix_parent_inverse = ASSET_ROOT.matrix_world.inverted()
    if bevel:
        mod = ob.modifiers.new("Slate edge softness", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        ob.modifiers.new("Weighted roof normals", "WEIGHTED_NORMAL")
    return ob


def tune_procedural(material, color, scale, roughness, bump_strength, bump_distance):
    material.use_nodes = True
    nt = material.node_tree
    nodes, links = nt.nodes, nt.links
    shader = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    output = next((n for n in nodes if n.type == "OUTPUT_MATERIAL"), None)
    if not shader or not output:
        nodes.clear()
        shader = nodes.new("ShaderNodeBsdfPrincipled")
        output = nodes.new("ShaderNodeOutputMaterial")
        links.new(shader.outputs[0], output.inputs["Surface"])
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 4.0
    noise.inputs["Roughness"].default_value = 0.72
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = bump_distance
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    return noise


def circle_cylinder(name, location, radius, depth, material, vertices=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    ob = bpy.context.object
    ob.name = name
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    COLLECTION.objects.link(ob)
    ob.parent = ASSET_ROOT
    ob.matrix_parent_inverse = ASSET_ROOT.matrix_world.inverted()
    if material:
        ob.data.materials.append(material)
    bevel = ob.modifiers.new("Column edge details", "BEVEL")
    bevel.width = 0.06
    bevel.segments = 2
    ob.modifiers.new("Column weighted normals", "WEIGHTED_NORMAL")
    return ob


def remove_obj(name):
    ob = bpy.data.objects.get(name)
    if ob:
        bpy.data.objects.remove(ob, do_unlink=True)


# The previous block-shaped mansard was the chief silhouette error. Replace
# it with four sloped, thick roof planes. Extents follow the existing shell.
for name in ("UNIV_Mansard_Roof_Core", "UNIV_Mansard_Roof_Deck", "UNIV_Roof_WroughtIron_Cresting"):
    remove_obj(name)
for ob in list(bpy.data.objects):
    if ob.name.startswith(("UNIV_Dormer_Body_", "UNIV_Dormer_Glass_", "UNIV_Dormer_Pediment_")):
        bpy.data.objects.remove(ob, do_unlink=True)

slate = mat("Univ_Slate_Roof")
stone = mat("Univ_Bedford_Limestone")
brick = mat("Univ_Weathered_Red_Brick")
glass = mat("Univ_Window_Glass")
bronze = mat("Univ_Bronze")
wood = mat("Univ_Dark_Walnut")
iron = bpy.data.materials.new("UNIV_R2_Painted_Iron")
iron.diffuse_color = (0.13, 0.16, 0.14, 1)
iron.use_nodes = True
iron.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.095, 0.12, 0.105, 1)
iron.node_tree.nodes.get("Principled BSDF").inputs["Metallic"].default_value = 0.65
iron.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value = 0.33

noise = tune_procedural(slate, (0.14, 0.17, 0.21, 1), 115.0, 0.78, 0.23, 0.045)
# Slate variation: cloudy, subdued blue-gray rather than a featureless gray slab.
nt = slate.node_tree
shader = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
texr = nt.nodes.new("ShaderNodeValToRGB")
texr.color_ramp.elements[0].position = 0.20
texr.color_ramp.elements[0].color = (0.075, 0.095, 0.13, 1)
texr.color_ramp.elements[1].position = 0.82
texr.color_ramp.elements[1].color = (0.28, 0.32, 0.37, 1)
nt.links.new(noise.outputs["Fac"], texr.inputs["Fac"])
nt.links.new(texr.outputs["Color"], shader.inputs["Base Color"])

# Use an object-coordinate transform with meter-scale detail. The original
# brick material already has a brick pattern; reinforce its mortar relief.
bnodes = brick.node_tree.nodes
bs = next(n for n in bnodes if n.type == "BSDF_PRINCIPLED")
bump = bnodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.12
bump.inputs["Distance"].default_value = 0.025
noise_b = bnodes.new("ShaderNodeTexNoise")
noise_b.inputs["Scale"].default_value = 22.0
brick.node_tree.links.new(noise_b.outputs["Fac"], bump.inputs["Height"])
brick.node_tree.links.new(bump.outputs["Normal"], bs.inputs["Normal"])

# Extent uses the verified source wall bounds (width 21.92m, length 43.24m).
# An upper perimeter is kept as a measured-shape estimate, not surveyed roof.
bx0, bx1 = CX - 11.15, CX + 11.15
by0, by1 = CY - 22.05, CY + 22.05
tx0, tx1 = CX - 5.35, CX + 5.35
ty0, ty1 = CY - 15.10, CY + 15.10
z0, z1 = 12.58, 16.75
# Create four face pairs and a 0.2m inset underside shell; clipped/mitered
# corners overlap minimally so no daylight leaks through the mansard seam.
sides = [
    ("East", [(bx1,by0,z0),(bx1,by1,z0),(tx1,ty1,z1),(tx1,ty0,z1)], (0.2,0,0)),
    ("West", [(bx0,by1,z0),(bx0,by0,z0),(tx0,ty0,z1),(tx0,ty1,z1)], (-0.2,0,0)),
    ("North", [(bx1,by1,z0),(bx0,by1,z0),(tx0,ty1,z1),(tx1,ty1,z1)], (0,0.2,0)),
    ("South", [(bx0,by0,z0),(bx1,by0,z0),(tx1,ty0,z1),(tx0,ty0,z1)], (0,-0.2,0)),
]
for side, outer, offset in sides:
    inner = [(x-offset[0], y-offset[1], z+0.02) for x,y,z in outer]
    verts = outer + inner
    faces = [(0,1,2,3), (7,6,5,4), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0)]
    mesh_obj(f"UNIV_R2_Mansard_{side}", verts, faces, slate, bevel=0.035)

# Cornice/eaves trim defines the bottom edge; the upper edges turn into a
# restrained flat ridge/roof deck around the existing central tower.
box("UNIV_R2_Mansard_Eave_E", (bx1+0.08,0,12.65),(0.28,44.4,0.34),stone,0.04)
box("UNIV_R2_Mansard_Eave_W", (bx0-0.08,0,12.65),(0.28,44.4,0.34),stone,0.04)
box("UNIV_R2_Mansard_Eave_N", (CX,by1+0.08,12.65),(22.5,0.28,0.34),stone,0.04)
box("UNIV_R2_Mansard_Eave_S", (CX,by0-0.08,12.65),(22.5,0.28,0.34),stone,0.04)
box("UNIV_R2_RidgeDeck", (CX,0,16.61),(10.3,29.6,0.3),slate,0.05)

# Dormers are repeated on the long E/W roof slopes. Each has a brick cheek,
# limestone surround, glazed sash, and a small pitched roof rather than a cube.
for side, sign in (("East",1), ("West",-1)):
    for idx, y in enumerate((-13.0,-6.5,0.0,6.5,13.0)):
        # Evaluate slope: edge x=11.15 at z=12.58 to x=5.35 at z=16.75.
        z=14.7
        xabs=11.15-(11.15-5.35)*(z-z0)/(z1-z0)
        x=CX+sign*(xabs-0.22)
        box(f"UNIV_R2_Dormer_{side}_{idx}_Brick",(x,y,z),(1.38,1.6,2.1),brick,0.05)
        # The glazed face looks outward along X and sits just proud of the cheek.
        box(f"UNIV_R2_Dormer_{side}_{idx}_Glass",(x+sign*0.70,y,z),(0.075,0.95,1.35),glass,0.025)
        for dy in (-0.57,0.57):
            box(f"UNIV_R2_Dormer_{side}_{idx}_Jamb_{dy}",(x+sign*0.76,y+dy,z),(0.15,0.12,1.48),stone,0.018)
        box(f"UNIV_R2_Dormer_{side}_{idx}_Sill",(x+sign*0.76,y,z-0.77),(0.22,1.35,0.14),stone,0.025)
        # Two sloping cheeks of a shallow triangular pediment; ridge is along Y.
        rv=[(x+sign*0.15,y-0.92,z+0.9),(x+sign*0.15,y+0.92,z+0.9),(x+sign*0.15,y,z+1.55),
            (x+sign*1.15,y-0.92,z+0.9),(x+sign*1.15,y+0.92,z+0.9),(x+sign*1.15,y,z+1.55)]
        rf=[(0,1,2),(5,4,3),(0,3,4,1),(0,2,5,3),(1,4,5,2)]
        mesh_obj(f"UNIV_R2_Dormer_{side}_{idx}_Pediment",rv,rf,stone,0.02)
        # Small slate gabled cap as two clean slopes.
        roofv=[(x+sign*0.2,y-1.0,z+1.48),(x+sign*0.2,y,z+2.08),(x+sign*0.2,y+1.0,z+1.48),
               (x+sign*1.35,y-1.0,z+1.48),(x+sign*1.35,y,z+2.08),(x+sign*1.35,y+1.0,z+1.48)]
        mesh_obj(f"UNIV_R2_Dormer_{side}_{idx}_SlateCap",roofv,[(0,1,4,3),(1,2,5,4)],slate,0.025)

# Slate standing seams run from eaves up the steep face. Subtle charcoal strips
# are offset from the roof surface by 6 cm to avoid z fighting.
for side, sign in (("East",1),("West",-1)):
    for i,y in enumerate(range(-20,21,2)):
        outer_x=CX+sign*(11.15+0.055)
        inner_x=CX+sign*(5.35+0.055)
        verts=[(outer_x,y-0.018,z0),(outer_x,y+0.018,z0),
               (inner_x,y+0.018,z1),(inner_x,y-0.018,z1)]
        mesh_obj(f"UNIV_R2_SlateStandingSeam_{side}_{i}",verts,[(0,1,2,3)],iron)

# Add traditional stone jambs on existing E/W windows. Original window glass,
# sill and hood geometry is kept; these slim verticals make the hierarchy read.
for obj in list(bpy.data.objects):
    if not obj.name.startswith("UNIV_Win_") or "East" not in obj.name and "West" not in obj.name:
        continue
    p=obj.matrix_world.translation
    sign=1 if "East" in obj.name else -1
    for side in (-1,1):
        box(f"UNIV_R2_{obj.name}_StoneJamb_{side}",(p.x+sign*0.24,p.y+side*1.12,p.z),(0.22,0.20,2.55),stone,0.025)

# Replace broad interior floor plates with perimeter rings around the revived
# two-story gallery. The inner 7.6 x 12.0m opening is an estimate from the
# published two-story central-gallery description, not a measured as-built plan.
parquet=mat("Univ_Parquet_Wood")
floor_specs=(("UNIV_Interior_Floor_First",4.2,0.30,3.8,6.0),
             ("UNIV_Interior_Floor_Second",8.4,0.30,3.3,5.4))
for fname,z,thick,hx,hy in floor_specs:
    old=bpy.data.objects.get(fname)
    if not old: continue
    bpy.data.objects.remove(old,do_unlink=True)
    x0,x1=CX-10.36,CX+10.36
    y0,y1=-21.02,21.02
    zc=z
    # Four non-overlapping slabs surround the atrium opening.
    slabs=[((x0+CX-hx)/2,0,(CX-hx-x0),y1-y0),
           ((CX+hx+x1)/2,0,(x1-CX-hx),y1-y0),
           (CX,(y0+CY-hy)/2,2*hx,CY-hy-y0),
           (CX,(CY+hy+y1)/2,2*hx,y1-CY-hy)]
    for i,(x,y,dx,dy) in enumerate(slabs):
        if dx<=0 or dy<=0: continue
        box(f"UNIV_R2_{fname}_GalleryRing_{i}",(x,y,zc),(dx,dy,thick),parquet,0.025)

# Pale feature wall with bookshelves at north end of the gallery, inspired by
# Purdue's current gallery/first-library interpretation. At the second level,
# add an academy overlook and restrained iron balustrade around the void.
plaster=mat("Univ_Interior_Plaster")
box("UNIV_R2_Gallery_LibraryFeatureWall",(CX,6.9,4.4),(7.0,0.3,7.4),wood,0.04)
for i in range(9):
    x=CX-3.0+i*0.75
    box(f"UNIV_R2_Gallery_BookBay_{i}",(x,6.7,5.0),(0.56,0.12,5.3),wood,0.025)
    for row in range(8):
        box(f"UNIV_R2_Gallery_Book_{i}_{row}",(x,6.55,3.0+row*0.62),(0.44,0.12,0.43),
            mat("Univ_Burgundy_Leather") if (i+row)%3 else mat("Univ_Gold_Accent"),0.012)
box("UNIV_R2_Gallery_Overlook_FeatureWall",(CX+6.1,0,6.3),(0.25,8.0,3.4),plaster,0.04)

# Reclaimed cast-iron columns represented at two reported locations near the
# gallery and one at the south stairwell; schematic placement within plan.
for level,(base,top) in enumerate(((0.25,4.05),(4.45,8.25))):
    for ix,x in enumerate((CX-4.2,CX+4.2)):
        for iy,y in enumerate((-6.8,6.8)):
            label=f"UNIV_R2_ReclaimedCastIronColumn_{level}_{ix}_{iy}"
            circle_cylinder(label,(x,y,(base+top)/2),0.21,top-base,iron,24)
            for dz,rad in ((base+0.12,0.36),(base+0.30,0.28),(top-0.20,0.29)):
                circle_cylinder(label+f"_Capital_{dz:.1f}",(x,y,dz),rad,0.16,iron,24)

# Two compact stair flights against the south-west circulation bay, 18 risers
# per floor at 0.233m; these are representative rather than surveyed geometry.
for flight in range(2):
    base=flight*4.2
    for i in range(18):
        h=0.23*(i+1)
        y=-19.5+i*0.34 if flight==0 else -13.72-i*0.34
        z=base+h/2
        box(f"UNIV_R2_GalleryStair_{flight}_Tread_{i}",(CX-7.6,y,z),(2.7,0.43,h),wood,0.025)
    # Landings and continuous slender rails; glass/iron guards border overlooks.
    box(f"UNIV_R2_GalleryStair_{flight}_Landing",(CX-7.6,-13.15,base+4.05),(3.2,1.8,0.16),wood,0.035)
    for side in (-1,1):
        for i in range(7):
            z=base+0.55+i*0.52
            y=(-19.25+i*0.49) if flight==0 else (-13.7-i*0.49)
            box(f"UNIV_R2_GalleryStair_{flight}_GuardPost_{side}_{i}",(CX-7.6+side*1.28,y,z/2+base/2),(0.055,0.055,z-base+0.08),iron,0.018)
        # Handrail on the stair's outside edge.
        rail=box(f"UNIV_R2_GalleryStair_{flight}_Handrail_{side}",(CX-7.6+side*1.28,-16.1,base+2.65),(0.10,7.0,0.10),wood,0.03)
        rail.rotation_euler[0]=math.radians(0)
        rail.rotation_euler[1]=math.radians(-33 if flight==0 else 33)

# On the 8.4m academy overlook, keep a broad opening but guard its south and
# east edges with clear glass and iron cap rails.
for edge in ("South","East"):
    for i in range(13):
        if edge=="South": pos=(CX-3.0+i*0.5, -5.55, 8.95); dims=(0.055,0.055,1.05)
        else: pos=(CX+3.25, -5.4+i*0.9, 8.95); dims=(0.055,0.055,1.05)
        box(f"UNIV_R2_Overlook_{edge}_Baluster_{i}",pos,dims,iron,0.018)
    if edge=="South": box("UNIV_R2_Overlook_South_Handrail",(CX, -5.55, 9.5),(6.4,0.11,0.11),wood,0.035)
    else: box("UNIV_R2_Overlook_East_Handrail",(CX+3.25,0.0,9.5),(0.11,11.0,0.11),wood,0.035)

# A labeled, restrained north-gallery wall panel nods to Purdue's first library.
gold=mat("Univ_Gold_Accent")
box("UNIV_R2_Gallery_InterpretivePlaque_Frame",(CX,6.48,6.25),(2.2,0.10,1.0),stone,0.06)
box("UNIV_R2_Gallery_InterpretivePlaque",(CX,6.41,6.25),(1.95,0.045,0.72),gold,0.035)

# Daylight-friendly cleanup to the source materials.
for material in (brick, stone, slate):
    material.diffuse_color=(0.34,0.23,0.18,1) if material==brick else material.diffuse_color

bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print("SAVED", ASSET)
print("ROOT", ASSET_ROOT.name, list(ASSET_ROOT.location), list(ASSET_ROOT.rotation_euler), list(ASSET_ROOT.scale))
print("COLLECTION_OBJECTS",len(COLLECTION.all_objects))
