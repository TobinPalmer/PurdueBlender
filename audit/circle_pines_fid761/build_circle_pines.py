import bpy, json, math, os
from mathutils import Vector

ROOT = r"C:\Users\Tobin\Documents\Blender\PurdueMap"
AUDIT = os.path.join(ROOT, "audit", "circle_pines_fid761")
ASSET = os.path.join(ROOT, "modular", "buildings", "massing_house_301841609_c6c9ac4.blend")
INSPECT = json.load(open(os.path.join(AUDIT, "initial_inspection.json"), encoding="utf-8"))
ring = INSPECT["gis_ring_xy_local_m"]
if ring[0] == ring[-1]: ring = ring[:-1]
LAYOUT = json.load(open(os.path.join(AUDIT, "schematic_layout.json"), encoding="utf-8"))
bpy.ops.wm.open_mainfile(filepath=ASSET)

# Keep stable scene, collection and object names.  The official outline is used
# directly; all vertical and facade dimensions are estimates.
scene_name = "Building_massing_house_301841609_c6c9ac4"
collection_name = "Asset_massing_house_301841609_c6c9ac4"
object_name = "House_301841609"
scene = bpy.data.scenes.get(scene_name) or bpy.context.scene
scene.name = scene_name
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
for datablock in list(bpy.data.meshes):
    if datablock.users == 0: bpy.data.meshes.remove(datablock)
col = bpy.data.collections.get(collection_name)
if col is None:
    col = bpy.data.collections.new(collection_name)
    scene.collection.children.link(col)
else:
    for obj in list(col.objects): bpy.data.objects.remove(obj, do_unlink=True)

wall_h = 5.4  # estimated from the two visible window bands; not measured
roof_h = 0.35 # low parapet-like cap; roof behind it is obscured/unverified
n = len(ring)
verts = [(x,y,z) for z in (0.0,wall_h,wall_h+roof_h) for x,y in ring]
faces=[]; material_ids=[]
# vertical shell
for i in range(n):
    j=(i+1)%n
    faces.append((i,j,n+j,n+i)); material_ids.append(0)
# The saved April 2026 Street View image supports brick on only the visible
# camera-facing wall. Other elevations remain neutral/unverified.
source_facade_edge = 17
material_ids[source_facade_edge] = 9
# single planar top face avoids asserting an unsupported ridge direction/shape
faces.append(tuple(range(2*n,3*n))); material_ids.append(1)
# roof edge return and soffit
for i in range(n):
    j=(i+1)%n
    faces.append((2*n+i,2*n+j,n+j,n+i)); material_ids.append(1)

def solid_polygon(poly_xy,z0,z1,mi):
    """Add an extruded simple polygon to the single saved building mesh."""
    count=len(poly_xy); start=len(verts)
    verts.extend([(x,y,z) for z in (z0,z1) for x,y in poly_xy])
    faces.append(tuple(start+i for i in reversed(range(count)))); material_ids.append(mi)
    for i in range(count):
        j=(i+1)%count
        faces.append((start+i,start+j,start+count+j,start+count+i)); material_ids.append(mi)
    faces.append(tuple(start+count+i for i in range(count))); material_ids.append(mi)

def floor_polygon(poly_xy,z,mi):
    solid_polygon(poly_xy,z-.05,z,mi)

# The roof stays a low, flat, neutral massing cap because trees obscure its
# form. Only the current Street View-facing elevation receives visual facade
# cues; other elevations remain unverified. Interior floors, room dividers,
# circulation and furnishings are illustrative geometry contained within the
# GIS outline, not an as-built plan.
for i,poly in enumerate(LAYOUT["room_floor_polygons_xy"]): floor_polygon(poly,0.075,2+(i%3))
for poly in LAYOUT["corridor_polygons_xy"]: floor_polygon(poly,0.092,5)
for poly in LAYOUT["partition_polygons_xy"]: solid_polygon(poly,0.075,2.30,4)

angle=math.radians(LAYOUT["frame"]["axis_angle_degrees"])
u=(math.cos(angle),math.sin(angle)); v=(-math.sin(angle),math.cos(angle))
def oriented_box(center_xy,size_uv,z0,z1,mi):
    cx,cy=center_xy; du,dv=size_uv
    corners=[]
    for a,b in [(-du/2,-dv/2),(du/2,-dv/2),(du/2,dv/2),(-du/2,dv/2)]:
        corners.append((cx+u[0]*a+v[0]*b,cy+u[1]*a+v[1]*b))
    solid_polygon(corners,z0,z1,mi)

for item in LAYOUT["furnishings"]:
    center=item["center_xy"]; du,dv=item["size_uv_m"]; kind=item["kind"]
    if kind=="common_table":
        # Generic table with four legs, included only as a scale cue.
        legw=.10; legset=.18; top=.70
        for a in (-du/2+legset,du/2-legset):
            for b in (-dv/2+legset,dv/2-legset):
                c=(center[0]+u[0]*a+v[0]*b,center[1]+u[1]*a+v[1]*b)
                oriented_box(c,(legw,legw),.09,top,6)
        oriented_box(center,(du,dv),top,top+.07,6)
    elif kind=="bed_like":
        oriented_box(center,(du,dv),.15,.38,6)
        oriented_box(center,(du-.06,dv-.06),.38,.56,7)
        pillow=(center[0]-u[0]*du*.32,center[1]-u[1]*du*.32)
        oriented_box(pillow,(du*.22,dv*.7),.56,.64,7)
    elif kind=="chair":
        oriented_box(center,(du,dv),.40,.84,6)
        back=(center[0]-v[0]*dv*.38,center[1]-v[1]*dv*.38)
        oriented_box(back,(du,.09),.84,1.18,6)
    else:
        oriented_box(center,(du,dv),.12,.58,6)
        back=(center[0]-v[0]*dv*.37,center[1]-v[1]*dv*.37)
        oriented_box(back,(du,.12),.58,.95,6)

# One short illustrative stair feature; no floor above or stair destination is
# asserted. It represents a generic circulation/step zone at an unknown location.
stair=LAYOUT.get("stair")
if stair:
    cu,cv=stair["center_uv"]; origin=LAYOUT["frame"]["origin_xy_m"]
    cx=origin[0]+u[0]*cu+v[0]*cv; cy=origin[1]+u[1]*cu+v[1]*cv
    count=stair["steps"]; tread=stair["tread_m"]; width=stair["width_m"]
    run=stair["run_m"]; rise=stair["rise_each_m"]
    for i in range(count):
        a=-run/2+(i+.5)*tread
        c=(cx+u[0]*a,cy+u[1]*a)
        oriented_box(c,(tread,width),.075,.075+(i+1)*rise,8)

# Evidence-backed facade treatment for the single Street View-facing wall.
# The panorama identifies a brick elevation with two rectangular window bands,
# a taller central glazed entry bay and a shallow flat canopy. Exact opening
# locations/dimensions are interpreted from the oblique 900x600 panorama.
facade_a, facade_b = ring[source_facade_edge], ring[(source_facade_edge+1)%n]
facade_dx, facade_dy = facade_b[0]-facade_a[0], facade_b[1]-facade_a[1]
facade_length = math.hypot(facade_dx, facade_dy)
facade_u = (facade_dx/facade_length, facade_dy/facade_length)
ring_twice_area = sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1]))
if ring_twice_area < 0:
    facade_n = (-facade_u[1], facade_u[0])
else:
    facade_n = (facade_u[1], -facade_u[0])

def facade_box(t, width, depth, z0, z1, material_index, outward_offset=0.06):
    """Add a small box aligned to the observed wall plane in the root mesh."""
    cx = facade_a[0] + facade_u[0]*t + facade_n[0]*outward_offset
    cy = facade_a[1] + facade_u[1]*t + facade_n[1]*outward_offset
    start = len(verts)
    for z in (z0,z1):
        for along,normal in [(-width/2,-depth/2),(width/2,-depth/2),
                             (width/2,depth/2),(-width/2,depth/2)]:
            verts.append((cx + facade_u[0]*along + facade_n[0]*normal,
                          cy + facade_u[1]*along + facade_n[1]*normal,z))
    faces.extend([(start+3,start+2,start+1,start),
                  (start,start+1,start+5,start+4),
                  (start+1,start+2,start+6,start+5),
                  (start+2,start+3,start+7,start+6),
                  (start+3,start,start+4,start+7),
                  (start+4,start+5,start+6,start+7)])
    material_ids.extend([material_index]*6)

def observed_window(t, z0, width, height):
    # Light frame around dark glazing, with simple cross-mullions. These are
    # qualitative opening cues, not surveyed window schedules.
    facade_box(t,width+0.18,0.10,z0-0.09,z0+height+0.09,11,0.10)
    facade_box(t,width,0.06,z0,z0+height,10,0.17)
    facade_box(t,0.045,0.08,z0,z0+height,11,0.22)
    facade_box(t,width,0.08,z0+height*0.52-0.025,z0+height*0.52+0.025,11,0.22)

window_t = [facade_length*0.17, facade_length*0.38,
            facade_length*0.62, facade_length*0.83]
for t in window_t:
    observed_window(t,0.92,1.42,1.12)
    observed_window(t,3.92,1.34,0.82)

# Taller central glazed entry bay. The dark ground-level door and upper glazing
# share a simple frame, matching only the visible vertical center composition.
center_t = facade_length*0.50
facade_box(center_t,2.70,0.13,0.20,4.90,11,0.10)
facade_box(center_t,2.42,0.06,2.88,4.78,12,0.18)
facade_box(center_t,1.18,0.07,0.28,2.46,10,0.18)
facade_box(center_t,0.055,0.08,2.88,4.78,11,0.23)
facade_box(center_t,2.42,0.08,3.38,3.43,11,0.23)
# A modest flat canopy over the central entry is visible in the panorama.
facade_box(center_t,3.65,1.25,2.56,2.72,13,0.60)

mesh=bpy.data.meshes.new(object_name+"_GIS_shell_mesh")
mesh.from_pydata(verts,[],faces); mesh.update()
obj=bpy.data.objects.new(object_name,mesh); col.objects.link(obj)

def mat(name, color, roughness=0.8, metallic=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.use_nodes=True
    bsdf=next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value=(*color,1)
    bsdf.inputs["Roughness"].default_value=roughness
    bsdf.inputs["Metallic"].default_value=metallic
    if name=="CirclePines_Neutral_Unverified_Exterior":
        # Restrained broad tonal variation gives the study mass readable light
        # response without assigning brick, siding, stucco, or another unknown
        # finish. Avoid fine bump, which looked like unsupported horizontal siding.
        nodes=m.node_tree.nodes; links=m.node_tree.links
        texcoord=nodes.new("ShaderNodeTexCoord"); texcoord.location=(-620,40)
        tonal_noise=nodes.new("ShaderNodeTexNoise"); tonal_noise.location=(-420,80)
        tonal_noise.inputs["Scale"].default_value=.5
        tonal_noise.inputs["Detail"].default_value=0
        tonal_noise.inputs["Roughness"].default_value=.55
        ramp=nodes.new("ShaderNodeValToRGB"); ramp.location=(-200,80)
        ramp.color_ramp.elements[0].position=.35
        ramp.color_ramp.elements[0].color=(.52,.50,.46,1)
        ramp.color_ramp.elements[1].position=.65
        ramp.color_ramp.elements[1].color=(.58,.56,.52,1)
        links.new(texcoord.outputs["Generated"],tonal_noise.inputs["Vector"])
        links.new(tonal_noise.outputs["Fac"],ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value=.83
    return m
materials=[mat("CirclePines_Neutral_Unverified_Exterior",(.55,.54,.51)),
           mat("CirclePines_Neutral_Estimated_FlatCap",(.49,.50,.49)),
           mat("CirclePines_Schematic_Room_Floor_A",(.74,.72,.66)),
           mat("CirclePines_Schematic_Room_Floor_B",(.68,.71,.68)),
           mat("CirclePines_Schematic_Room_Floor_C",(.76,.70,.63)),
           mat("CirclePines_Schematic_Circulation",(.80,.74,.59)),
           mat("CirclePines_Schematic_Furnishing_Wood",(.40,.32,.23)),
           mat("CirclePines_Schematic_Bedding",(.80,.80,.74)),
           mat("CirclePines_Schematic_Stair",(.52,.47,.39)),
           mat("CirclePines_Observed_RedBrown_Brick",(.30,.075,.048)),
           mat("CirclePines_Observed_Dark_Window_Glass",(.035,.065,.075),.38),
           mat("CirclePines_Observed_Light_Window_Frames",(.66,.64,.59)),
           mat("CirclePines_Observed_Central_Glazing",(.025,.05,.06),.35),
           mat("CirclePines_Observed_Flat_Entry_Canopy",(.43,.44,.42),.72)]
for m in materials: mesh.materials.append(m)
for p,mi in zip(mesh.polygons,material_ids): p.material_index=mi
obj["source_feature_id"]=761
obj["footprint_source"]="Purdue GIS BuildingShapes FID 761; original polygon vertices"
obj["vertical_dimensions_status"]="estimated: 5.4 m wall + 0.35 m parapet-like cap based on two visible window bands; not measured; GIS NUM_LEVELS=1 conflict retained"
obj["facade_status"]="one visible facade interpreted from 2026-04 Google Street View pano ytu8Bz_eEp2xCv9QeF0xRw; other elevations unverified"
obj["roof_status"]="low parapet-like upper edge visible; roof form behind trees remains unverified"
obj["plan_status"]="schematic 3D floors, room divisions, circulation and furniture; not an as-built plan"
obj.select_set(True); bpy.context.view_layer.objects.active=obj
bpy.ops.wm.save_as_mainfile(filepath=ASSET)

result={"asset":ASSET,"scene":scene.name,"collection":col.name,"object":obj.name,
        "unique_gis_vertices":n,"wall_height_estimate_m":wall_h,"roof_cap_estimate_m":roof_h,
        "source_facade_ring_edge_index":source_facade_edge,"source_facade_length_m":facade_length,
        "vertex_count":len(mesh.vertices),"face_count":len(mesh.polygons),
        "bbox_min":[min(v[i] for v in verts) for i in range(3)],"bbox_max":[max(v[i] for v in verts) for i in range(3)],
        "geometry":"GIS-derived shell, conservative planar cap, and explicitly schematic 3D room/circulation/furnishing inserts"}
json.dump(result,open(os.path.join(AUDIT,"build_result.json"),"w",encoding="utf-8"),indent=2)
print(json.dumps(result,indent=2))
