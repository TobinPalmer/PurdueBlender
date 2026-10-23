import bpy, math, json
from pathlib import Path

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = ROOT / "modular/buildings/math_sciences.blend"
OUT = ROOT / "audit/batch3_math"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
EXPORT = bpy.data.collections["Asset_math_sciences"]
SHELL = bpy.data.objects["MATH_Corrected_GIS_Wall_Envelope"]
# Preserve the pre-cut GIS prism mesh in the .blend and reset it each iteration.
# This makes the opening cuts repeatable and recoverable inside this one asset.
backup_mesh=bpy.data.meshes.get("MATH_2026_Envelope_Source_Backup")
if backup_mesh is None:
    backup_mesh=SHELL.data.copy(); backup_mesh.name="MATH_2026_Envelope_Source_Backup"; backup_mesh.use_fake_user=True
previous_mesh=SHELL.data
SHELL.data=backup_mesh.copy()
if previous_mesh is not backup_mesh and previous_mesh.users==0:
    bpy.data.meshes.remove(previous_mesh)

# Make this script safe to rerun while iterating.
for nm in ("MATH_Facade_2026", "MATH_Library_2026", "MATH_Floors_2026"):
    old = bpy.data.collections.get(nm)
    if old:
        for obj in list(old.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(old)

def new_collection(name):
    c = bpy.data.collections.new(name)
    EXPORT.children.link(c)
    return c

facade = new_collection("MATH_Facade_2026")
library = new_collection("MATH_Library_2026")
floors = new_collection("MATH_Floors_2026")

def material(name, color, roughness=0.6, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return m

limestone = bpy.data.materials.get("MATH_Bedford_Limestone") or material("MATH_Bedford_Limestone", (.72,.69,.61), .72)
glass = material("MATH_2026_Facade_Glass", (.105,.19,.22), .18, .38)
aluminum = material("MATH_2026_Window_Metal", (.34,.37,.36), .33, .68)
groupglass = material("MATH_2026_Group_Room_Clear_Glass", (.54,.68,.70), .16, .08)
gbn=groupglass.node_tree.nodes; gbl=groupglass.node_tree.links
gbs=next(n for n in gbn if n.type=='BSDF_PRINCIPLED')
gbs.inputs["Transmission Weight"].default_value=.45
transparent=gbn.new("ShaderNodeBsdfTransparent")
mix=gbn.new("ShaderNodeMixShader"); mix.inputs[0].default_value=.32
outnode=next(n for n in gbn if n.type=='OUTPUT_MATERIAL')
for link in list(gbl):
    if link.to_node==outnode and link.to_socket==outnode.inputs['Surface']: gbl.remove(link)
gbl.new(gbs.outputs['BSDF'],mix.inputs[1]); gbl.new(transparent.outputs['BSDF'],mix.inputs[2]); gbl.new(mix.outputs[0],outnode.inputs['Surface'])
oak = material("MATH_2026_Library_Oak", (.42,.25,.12), .43)
steel = material("MATH_2026_Library_Steel", (.105,.12,.13), .36, .72)
seat = material("MATH_2026_Library_Chair", (.34,.25,.17), .56)
terrazzo = material("MATH_2026_Office_Floor", (.56,.54,.49), .76)
coremat = material("MATH_2026_Core_Partition", (.62,.59,.53), .78)
roofmat = material("MATH_2026_Roof_Membrane", (.17,.19,.19), .86)
roofnodes=roofmat.node_tree.nodes; rooflinks=roofmat.node_tree.links
roofbs=roofnodes.get("Principled BSDF")
for node in list(roofnodes):
    if node.type in {'TEX_NOISE','BUMP'}: roofnodes.remove(node)
rooftex=roofnodes.new("ShaderNodeTexNoise"); rooftex.inputs["Scale"].default_value=38
roofbump=roofnodes.new("ShaderNodeBump"); roofbump.inputs["Distance"].default_value=.0015; roofbump.inputs["Strength"].default_value=.18
rooflinks.new(rooftex.outputs["Fac"],roofbump.inputs["Height"]); rooflinks.new(roofbump.outputs["Normal"],roofbs.inputs["Normal"])

# The flat mechanical roof is shown as a dark membrane, a more plausible finish
# than the inherited bright white viewport material. Top elevations are unknown.
for roof_name in ("MATH_Corrected_GIS_Roof_Slab", "MATH_Rooftop_Penthouse_Base", "MATH_Rooftop_Penthouse_Copings"):
    roof_obj=bpy.data.objects.get(roof_name)
    if roof_obj and roof_obj.type=='MESH':
        if roofmat.name not in [m.name for m in roof_obj.data.materials if m]: roof_obj.data.materials.append(roofmat)
        idx=next(i for i,m in enumerate(roof_obj.data.materials) if m and m.name==roofmat.name)
        for poly in roof_obj.data.polygons:
            n=roof_obj.matrix_world.to_3x3()@poly.normal
            center=roof_obj.matrix_world@poly.center
            if n.z>.8 and center.z>32.8: poly.material_index=idx

def combine_boxes(name, coll, matlist, boxes):
    # Each box is (center xyz, dimensions xyz, material index).
    verts, faces, mids = [], [], []
    for (cx,cy,cz),(sx,sy,sz),mi in boxes:
        if min(sx,sy,sz) <= 0: continue
        base = len(verts)
        verts += [(cx+sx*x*.5, cy+sy*y*.5, cz+sz*z*.5)
                  for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                                (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
            faces.append(tuple(base+i for i in f)); mids.append(mi)
    me = bpy.data.meshes.new(name+"Mesh")
    me.from_pydata(verts, [], faces); me.materials.clear()
    for m in matlist: me.materials.append(m)
    for p,mi in zip(me.polygons,mids): p.material_index=mi
    uv=me.uv_layers.new(name="MATH_Physical_Metre")
    for poly in me.polygons:
        n=poly.normal
        for li in poly.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co
            if abs(n.x)>=abs(n.y) and abs(n.x)>=abs(n.z): uv.data[li].uv=(co.y,co.z)
            elif abs(n.y)>=abs(n.z): uv.data[li].uv=(co.x,co.z)
            else: uv.data[li].uv=(co.x,co.y)
    me.update()
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    return ob

def remove_prism_components(obj, component_ids):
    old=obj.data
    uv_old=old.uv_layers.active
    kept_verts=[]; remap={}; kept_faces=[]; kept_materials=[]; kept_uv=[]
    for i,v in enumerate(old.vertices):
        if i//8 not in component_ids:
            remap[i]=len(kept_verts); kept_verts.append(tuple(v.co))
    for p in old.polygons:
        if all(i//8 not in component_ids for i in p.vertices):
            kept_faces.append(tuple(remap[i] for i in p.vertices)); kept_materials.append(p.material_index)
            kept_uv.append([tuple(uv_old.data[li].uv) for li in p.loop_indices] if uv_old else None)
    mesh=bpy.data.meshes.new("MATH_2026_Envelope_Without_Windowed_Facades")
    mesh.from_pydata(kept_verts,[],kept_faces)
    for m in old.materials: mesh.materials.append(m)
    for p,mi in zip(mesh.polygons,kept_materials): p.material_index=mi
    if uv_old:
        uv=mesh.uv_layers.new(name=uv_old.name)
        for p,uvs in zip(mesh.polygons,kept_uv):
            for li,co in zip(p.loop_indices,uvs): uv.data[li].uv=co
    mesh.update(); obj.data=mesh
    return len(kept_faces)

# Rebuild the east tower wall and south end wall with real through-openings.
# The two removed pieces are stable GIS-derived 8-vertex wall prisms from the backup mesh.
component_count=len(backup_mesh.vertices)//8
east_component=next((i for i in range(component_count) if
    (lambda b: b[1][1]-b[1][0]>39 and b[0][1]-b[0][0]<.8 and b[0][0]>16)(
      tuple((min(backup_mesh.vertices[j].co[k] for j in range(i*8,i*8+8)),
             max(backup_mesh.vertices[j].co[k] for j in range(i*8,i*8+8))) for k in range(3)))),None)
south_component=next((i for i in range(component_count) if
    (lambda b: b[1][0]<-33 and b[1][1]<-33 and b[0][1]-b[0][0]>15 and b[1][1]-b[1][0]<.8)(
      tuple((min(backup_mesh.vertices[j].co[k] for j in range(i*8,i*8+8)),
             max(backup_mesh.vertices[j].co[k] for j in range(i*8,i*8+8))) for k in range(3)))),None)
if east_component is None or south_component is None:
    raise RuntimeError(f"Could not identify target wall prisms; east={east_component}, south={south_component}")
removed_faces=remove_prism_components(SHELL,{east_component,south_component})
SHELL["source_status"]="Purdue's exterior photograph supports light red-brown brick across the visible building and a repeated narrow-window/pale-frame treatment on the two visible elevations. Procedural brick and mortar are applied across the existing shell; no new west/north opening patterns are fabricated because no reliable elevation view was found."
brick=bpy.data.materials.get("MATH_Photo_Brick_Metre")
if brick is None: raise RuntimeError("Expected Purdue-photo brick material is missing")
# The prior review found brick coursing too subtle at campus-view scale. Keep
# the existing metric UVs and procedural brick shader, but increase mortar
# visibility and restrained brick variation so courses read across all faces.
brick.diffuse_color=(.43,.25,.19,1)
bn=brick.node_tree.nodes; bl=brick.node_tree.links
brick_tex=next((n for n in bn if n.type=='TEX_BRICK'),None)
brick_bump=next((n for n in bn if n.type=='BUMP'),None)
brick_bsdf=next((n for n in bn if n.type=='BSDF_PRINCIPLED'),None)
if brick_tex and brick_bsdf and brick_bump:
    brick_tex.inputs['Scale'].default_value=1.0
    brick_tex.inputs['Brick Width'].default_value=.25
    brick_tex.inputs['Row Height'].default_value=.078
    brick_tex.inputs['Mortar Size'].default_value=.008
    brick_tex.inputs['Mortar Smooth'].default_value=.02
    brick_tex.inputs['Color1'].default_value=(.39,.205,.155,1)
    brick_tex.inputs['Color2'].default_value=(.49,.285,.22,1)
    brick_tex.inputs['Mortar'].default_value=(.58,.53,.46,1)
    brick_bump.inputs['Distance'].default_value=.003
    brick_bump.inputs['Strength'].default_value=.34
    if not brick_tex.outputs['Color'].is_linked:
        bl.new(brick_tex.outputs['Color'],brick_bsdf.inputs['Base Color'])
    if not brick_bump.outputs['Normal'].is_linked:
        bl.new(brick_tex.outputs['Fac'],brick_bump.inputs['Height'])
        bl.new(brick_bump.outputs['Normal'],brick_bsdf.inputs['Normal'])
brick_boxes=[]
facade_y = [-23.1,-16.8,-10.5,-4.2,2.1,8.4]
floor_z = [5.15 + 3.18*i for i in range(9)]
window_w, window_h = 1.28, 1.88
def fill_wall_with_windows(axis, thickness_bounds, span_bounds, centers, width, zcenters, height, z_bounds=(0.0,33.2)):
    """Emit a brick panel grid around rectangular full-depth window holes."""
    tmin,tmax=thickness_bounds; umin,umax=span_bounds; zmin,zmax=z_bounds
    tc=(tmin+tmax)/2; td=tmax-tmin
    def wallbox(u0,u1,z0,z1):
        if u1<=u0 or z1<=z0: return
        if axis=='x': brick_boxes.append(((tc,(u0+u1)/2,(z0+z1)/2),(td,u1-u0,z1-z0),0))
        else: brick_boxes.append((((u0+u1)/2,tc,(z0+z1)/2),(u1-u0,td,z1-z0),0))
    # Full wall below the first window tier.
    first_low=zcenters[0]-height/2
    wallbox(umin,umax,zmin,first_low)
    previous_high=first_low
    for zc in zcenters:
        low=zc-height/2; high=zc+height/2
        wallbox(umin,umax,previous_high,low)
        cursor=umin
        for c in centers:
            left=c-width/2; right=c+width/2
            if left>cursor:
                wallbox(cursor,left,low,high)
            cursor=right
        if cursor<umax:
            wallbox(cursor,umax,low,high)
        previous_high=high
    wallbox(umin,umax,previous_high,zmax)

# East long elevation: exact bounds copied from removed source prism; bays estimated from photograph.
fill_wall_with_windows('x',(16.754,17.307),(-27.489,11.981),facade_y,window_w,floor_z,window_h)
# South end elevation: source wall outline preserved, three window bays inferred from end-wall photo angle.
fill_wall_with_windows('y',(-33.961,-33.594),(-2.303,12.924),[1.4,5.0,8.6],1.26,floor_z,1.82)
infill=combine_boxes("MATH_2026_Perforated_Brick_Facades",facade,[brick],brick_boxes)
infill["source_status"]="Rectangular openings cut through two GIS-derived prism wall segments. Bay locations/heights are estimated from Purdue exterior imagery; shell footprint and wall bounds are retained."
infill["source_wall_components_removed"]=[east_component,south_component]

# Repeating narrow, pale-framed windows match Purdue's exterior photograph.
# Existing structural walls are retained; the glazing sits inside a projecting
# limestone reveal. Bay locations and floor spacing are estimates from the photo.
glass_boxes=[]; stone_boxes=[]; metal_boxes=[]
facade_y = [-23.1,-16.8,-10.5,-4.2,2.1,8.4]
floor_z = [5.15 + 3.18*i for i in range(9)]
window_w, window_h = 1.28, 1.88
for side in (1,):
    wallx = side*17.30
    depth = .18
    glassx = side*(17.30 + .095)
    framex = side*(17.30 + .17)
    for yc in facade_y:
        for zc in floor_z:
            # Dark insulated glazing, recessed from the limestone frame.
            glass_boxes.append(((glassx,yc,zc),(depth,window_w,window_h),0))
            # Four light stone reveal pieces with real depth and a projecting sill.
            ft=.14; fd=.18; fw=window_w+.32; fh=window_h+.32
            stone_boxes += [((framex,yc-fw/2+ft/2,zc),(fd,ft,fh),0),
                            ((framex,yc+fw/2-ft/2,zc),(fd,ft,fh),0),
                            ((framex,yc,zc-fh/2+ft/2),(fd,fw-2*ft,ft),0),
                            ((framex+side*.025,yc,zc+fh/2-ft/2),(fd+.05,fw,ft),0)]
            # Two vertical divisions and one transom are visible in the source image.
            # Set the transom slightly proud of the verticals so their crossing
            # faces cannot z-fight in the close facade view.
            metal_boxes += [((framex+side*.01,yc-.19,zc),(.08,.045,window_h-.06),0),
                            ((framex+side*.01,yc+.19,zc),(.08,.045,window_h-.06),0),
                            ((framex+side*.035,yc,zc),(.08,window_w-.05,.045),0)]
    # Slim vertical limestone mullion piers connect the window tiers.
    for yc in [sum(facade_y[i:i+2])/2 for i in range(len(facade_y)-1)]:
        stone_boxes.append(((side*17.42,yc,18.1),(.25,.16,28.2),0))

# South end windows use fewer bays because that wall is shorter and irregular.
south_y=-33.78
for xc in [1.4,5.0,8.6]:
    for zc in floor_z:
        glass_boxes.append(((xc,south_y,zc),(1.26,.08,1.82),0))
        for item in [((xc-.76,south_y-.28,zc),( .14,.18,2.14),0),
                     ((xc+.76,south_y-.28,zc),( .14,.18,2.14),0),
                     ((xc,south_y-.28,zc-1.0),(1.38,.18,.14),0),
                     ((xc,south_y-.30,zc+1.0),(1.38,.22,.14),0)]: stone_boxes.append(item)
        metal_boxes += [((xc-.2,south_y-.30,zc),(.04,.05,1.78),0),
                        ((xc+.2,south_y-.30,zc),(.04,.05,1.78),0),
                        ((xc,south_y-.30,zc),(1.20,.05,.04),0)]

combine_boxes("MATH_2026_Recessed_Facade_Glazing",facade,[glass],glass_boxes)
combine_boxes("MATH_2026_Limestone_Window_Surrounds",facade,[limestone],stone_boxes)
combine_boxes("MATH_2026_Aluminum_Mullions",facade,[aluminum],metal_boxes)

# East-side main entrance: pale stone portal, paired glazing, and a flat canopy.
entryy=-13.5; entryx=17.52; entryz=1.82
door_boxes=[((entryx,entryy,entryz),(0.12,4.0,3.15),0)]
portal_boxes=[((17.48,entryy-2.25,entryz+0.1),(.34,.28,3.8),0),
              ((17.48,entryy+2.25,entryz+0.1),(.34,.28,3.8),0),
              ((17.48,entryy,3.75),(.34,4.78,.28),0),
              ((17.58,entryy,4.0),(2.0,5.8,.28),0)]
doorframes=[((17.61,entryy-1.95,entryz),(.10,.08,3.0),0),
            ((17.61,entryy+1.95,entryz),(.10,.08,3.0),0),
            ((17.61,entryy,entryz-1.45),(.10,3.9,.10),0),
            ((17.61,entryy,entryz+1.45),(.10,3.9,.10),0),
            ((17.61,entryy,entryz),(.10,.06,2.9),0)]
combine_boxes("MATH_2026_East_Entrance_Glazing",facade,[glass],door_boxes)
combine_boxes("MATH_2026_East_Entrance_Portal",facade,[limestone],portal_boxes)
combine_boxes("MATH_2026_East_Entrance_Mullions",facade,[aluminum],doorframes)

# A simple occupied-floor structure is visible through the new window system.
# The documented footprint and floor count are preserved; slab height is estimated.
for i in range(1,10):
    z=3.25*i
    ob=combine_boxes(f"MATH_2026_Typical_Floor_{i+1:02d}",floors,[terrazzo],
        [((0,-7.5,z),(31.5,37.3,.16),0)])
    ob["source_status"]="Estimated typical floor slab; no current architectural plan located."
# Third-floor elevator and stair features follow the 2022 Board plan. Exact dimensions
# and registration are schematic; this does not substitute for a measured core survey.
elev_frame=[]; elev_doors=[]; stair_boxes=[]; rail_boxes=[]
# The 2022 third-floor plan places a three-car elevator bank and stair at the
# south core, beyond the library's south edge.  Its plan position is translated
# from the sheet using the preserved library floor outline; exact dimensions are
# schematic.  The previous placeholder at y=-21.45 was outside that core.
elevator_y=-4.7
for x in [-.7,.8,2.3]:
    elev_frame += [((x-.68,elevator_y,11.88),(.12,.12,2.38),0),
                   ((x+.68,elevator_y,11.88),(.12,.12,2.38),0),
                   ((x,elevator_y,13.06),(1.48,.12,.12),0)]
    elev_doors.append(((x,elevator_y-.05,11.85),(1.22,.06,2.20),0))
combine_boxes("MATH_2026_Third_Floor_Elevator_Frames",floors,[limestone],elev_frame)
combine_boxes("MATH_2026_Third_Floor_Elevator_Doors",floors,[aluminum],elev_doors)
# Schematic U-flight stairs at the north and south cores shown on the plan.
# Their vertical rise follows the existing library story, whose elevation is
# not independently surveyed.
def add_u_stair(cx,cy):
    base=10.67
    for k in range(8):
        z=base+.18*(k+.5); yy=cy-1.25+k*.30
        stair_boxes.append(((cx-.72,yy,z),(1.2,.31,.18),0))
        z2=base+1.50+.18*(k+.5); yy2=cy+1.25-k*.30
        stair_boxes.append(((cx+.72,yy2,z2),(1.2,.31,.18),0))
    stair_boxes.append(((cx,cy,base+1.50),(2.75,1.0,.18),0))
    for xx in [cx-1.37,cx-.07,cx+.07,cx+1.37]:
        rail_boxes.append(((xx,cy,base+1.30),(.045,3.2,1.05),0))
for cx,cy in [(-4.0,29.5),(4.3,29.5),(5.4,-4.2)]:
    add_u_stair(cx,cy)
combine_boxes("MATH_2026_Third_Floor_Stair_Treads",floors,[terrazzo],stair_boxes)
combine_boxes("MATH_2026_Third_Floor_Stair_Guards",floors,[aluminum],rail_boxes)

# The 2025 Purdue Libraries reopening photo shows carpeted zones, beech carrels,
# book shelving and small group study. Furniture placement below is illustrative.
carpet=material("MATH_2026_Library_Carpet",(.34,.32,.28),.9)
cn=carpet.node_tree.nodes; cl=carpet.node_tree.links; cbs=cn.get("Principled BSDF")
for node in list(cn):
    if node.type in {'TEX_NOISE','BUMP'}: cn.remove(node)
noise=cn.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value=165
bump=cn.new("ShaderNodeBump"); bump.inputs["Distance"].default_value=.001; bump.inputs["Strength"].default_value=.12
cl.new(noise.outputs["Fac"],bump.inputs["Height"]); cl.new(bump.outputs["Normal"],cbs.inputs["Normal"])
floor_obj=bpy.data.objects.get("MATH_Lib_Floor_Terrazzo")
if floor_obj:
    if carpet.name not in [m.name for m in floor_obj.data.materials if m]: floor_obj.data.materials.append(carpet)
    cidx=next(i for i,m in enumerate(floor_obj.data.materials) if m and m.name==carpet.name)
    for p in floor_obj.data.polygons: p.material_index=cidx

# Shared collaboration tables in the south open reading zone; the room-boundary
# lines below follow the 2022 plan.  Furniture locations are inferred from the
# 2025 photograph because an as-built furniture plan is not public.
table_boxes=[]; chair_boxes=[]; desk_detail=[]
for y in [14.0,16.4]:
    x=0.0
    table_boxes.append(((x,y,11.42),(2.4,1.0,.08),0))
    for dx in [-1.02,1.02]: table_boxes.append(((x+dx,y,11.03),(.06,.06,.70),1))
    desk_detail.append(((x,y,11.47),(.12,.12,.018),0))
    for xx in [-.62,.62]:
        for sign in [-1,1]:
            cx=x+xx; cy=y+sign*.84
            chair_boxes += [((cx,cy,11.12),(.46,.44,.10),0),
                            ((cx,cy+sign*.18,11.47),(.42,.07,.70),0)]
            for lx in [-.18,.18]:
                for ly in [-.15,.15]: chair_boxes.append(((cx+lx,cy+ly,10.96),(.04,.04,.58),1))
combine_boxes("MATH_2026_Library_Group_Tables",library,[oak,steel],table_boxes)
combine_boxes("MATH_2026_Library_Group_Seats",library,[seat,steel],chair_boxes)
combine_boxes("MATH_2026_Library_Table_Power",library,[aluminum],desk_detail)

# Individual oak carrels follow the documented current furniture type. Their
# number and placement are inferred, so keep them clear of the plan-defined zones.
carrel_boxes=[]; carrel_panels=[]; carrel_chairs=[]
for x in [-8.15]:
    for y in [13.1,16.0,18.9,21.8]:
        carrel_boxes.append(((x,y,11.42),(1.45,.72,.08),0))
        for dx in [-.62,.62]: carrel_boxes.append(((x+dx,y,11.06),(.06,.06,.64),1))
        carrel_boxes += [((x-.76,y+.48,11.34),(.06,.06,1.26),0),
                         ((x+.76,y+.48,11.34),(.06,.06,1.26),0)]
        # Back privacy board, softly arched across its upper edge.
        w=.78; yb=y+.78; z0=10.70; th=.055
        profile=[(-w,0),(-w,1.00),(-.58,1.14),(-.30,1.22),(0,1.25),(.30,1.22),(.58,1.14),(w,1.00),(w,0)]
        verts=[]
        for yy in [yb-th/2,yb+th/2]: verts += [(x+px,yy,z0+pz) for px,pz in profile]
        n=len(profile); faces=[tuple(range(n)),tuple(range(n,2*n))]
        for i in range(n): faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
        carrel_panels.append((verts,faces))
        # task chair in front (south) of desk
        chair_boxes += []
        carrel_chairs += [((x,y-.78,11.12),(.48,.46,.10),0),
                           ((x,y-.94,11.45),(.44,.06,.66),0)]
        for dx in [-.18,.18]:
            for dy in [-.14,.14]: carrel_chairs.append(((x+dx,y-.78+dy,10.96),(.04,.04,.58),1))
combine_boxes("MATH_2026_Library_Carrel_Desks",library,[oak,steel],carrel_boxes)
combine_boxes("MATH_2026_Library_Carrel_Seats",library,[seat,steel],carrel_chairs)
verts=[]; faces=[]
for v,f in carrel_panels:
    baseidx=len(verts); verts.extend(v); faces.extend([tuple(baseidx+i for i in poly) for poly in f])
pm=bpy.data.meshes.new("MathCarrelPanelsMesh"); pm.from_pydata(verts,[],faces); pm.materials.append(oak); pm.update()
po=bpy.data.objects.new("MATH_2026_Library_Curved_Carrel_Screens",pm); library.objects.link(po)

# Three low double-sided shelf runs with shelves and colored spine blocks.
bookmats=[material("MATH_2026_Book_"+n,c,.78) for n,c in [
    ("Navy",(.08,.15,.20)),("Teal",(.10,.28,.31)),("Brick",(.38,.12,.09)),
    ("Olive",(.29,.31,.16)),("Tan",(.52,.37,.20))]]
shelf_boxes=[]; books=[]
for ycenter in [12.9,16.9,20.9]:
    x=9.0
    # end panels, shelves and toe kick
    shelf_boxes += [((x-.42,ycenter,11.55),(.12,2.95,1.65),0),
                    ((x+.42,ycenter,11.55),(.12,2.95,1.65),0),
                    ((x,ycenter,10.79),(.95,3.0,.12),0)]
    for level in range(4):
        z=10.90+level*.38
        shelf_boxes.append(((x,ycenter,z),(.95,3.0,.07),0))
        for j in range(18):
            by=ycenter-1.38+j*.16
            h=.22+((j*7+level*3)%7)*.035
            books.append(((x,by,z+.045+h/2),(.58,.12,h),1+((j+level)%len(bookmats))))
combine_boxes("MATH_2026_Library_Low_Bookcases",library,[oak],shelf_boxes)
combine_boxes("MATH_2026_Library_Book_Spines",library,bookmats,books)

# 2022 plan-backed third-floor room partitions.  Pixel-to-local mapping uses
# the existing library floor outline (x -9.5..10.5, y 4.615..26.615) against
# the shaded plan area. The room boundaries are plan-derived; the open doorways
# and the modern group-room enclosures/furniture are inferred from the 2025 text.
partition_x=[-7.1,-.85,4.52,8.13]
zone_bottom,zone_top=11.4,22.8
boundary_boxes=[]
for x in partition_x:
    for ya,yb in [(zone_bottom,12.0),(13.6,21.2),(22.8,zone_top)]:
        if yb>ya:
            boundary_boxes.append(((x,(ya+yb)/2,12.12),(.12,yb-ya,3.0),0))
for y in [zone_bottom,zone_top]:
    gaps=[(-1.5,.5)] if y==zone_bottom else [(-.8,1.4)]
    x_ranges=[(-7.1,8.13)]
    for ga,gb in gaps:
        next_ranges=[]
        for xa,xb in x_ranges:
            if ga>xa: next_ranges.append((xa,min(ga,xb)))
            if gb<xb: next_ranges.append((max(gb,xa),xb))
        x_ranges=next_ranges
    for xa,xb in x_ranges:
        if xb>xa:
            boundary_boxes.append((((xa+xb)/2,y,12.12),(xb-xa,.12,3.0),0))
combine_boxes("MATH_2026_Library_2022_Plan_Room_Boundaries",library,[coremat],boundary_boxes)
bpy.data.objects["MATH_2026_Library_2022_Plan_Room_Boundaries"]["source_status"]="Partition lines follow the 2022 third-floor plan's labeled 311.3/311.4/311.5/311.7/311.8 library zones. Local registration is fitted to the existing library floor bounds; doorway gaps are inferred to preserve circulation."
# A narrow darker base makes these plan-backed walls legible at eye level and
# from the cutaway render. It follows only the same modeled wall segments.
partition_base=material("MATH_2026_Library_Partition_Base",(.27,.25,.22),.82)
base_boxes=[((c[0],c[1],10.735),(d[0],d[1],.12),0) for c,d,_ in boundary_boxes]
combine_boxes("MATH_2026_Library_2022_Plan_Partition_Bases",library,[partition_base],base_boxes)
bpy.data.objects["MATH_2026_Library_2022_Plan_Partition_Bases"]["source_status"]="Low base trim follows the same 2022 plan-aligned segments as the partition object; trim profile is a visualization detail."

# Three glazed group-study rooms are included because Purdue's 2025 reopening
# notice confirms additional group-study rooms. Their exact locations and sizes
# are not shown in the public sources and are explicitly tagged as inferred.
group_rooms=[(-4.55,20.0,3.55,3.7),(1.65,20.0,3.75,3.7),(6.35,20.0,2.85,3.7)]
group_glass=[]; group_frames=[]; group_doors=[]; group_tables=[]; group_seats=[]; group_boards=[]
for idx,(cx,cy,w,d) in enumerate(group_rooms,1):
    x0,x1=cx-w/2,cx+w/2; y0,y1=cy-d/2,cy+d/2
    zc=12.05; h=2.72; t=.08
    # Rear and side glass, divided into pane panels by slim aluminum mullions.
    group_glass += [((cx,y1,zc),(w,t,h),0),((x0,cy,zc),(t,d,h),0),((x1,cy,zc),(t,d,h),0)]
    group_frames += [((cx,y1,zc),(w,.055,.06),0),((cx,y1,zc+h/2), (w,.055,.06),0),
                     ((x0,cy,zc),( .055,d,.06),0),((x1,cy,zc),(.055,d,.06),0)]
    for xx in [cx-w/3,cx,cx+w/3]:
        group_frames += [((xx,y1,zc),(.045,.06,h),0)]
    # South-facing front with a centered opening for the leaf.
    doorw=.88; sidew=(w-doorw)/2
    group_glass += [((cx-(doorw+sidew)/2,y0,zc),(sidew,t,h),0),
                    ((cx+(doorw+sidew)/2,y0,zc),(sidew,t,h),0)]
    group_frames += [((cx,y0,zc+h/2),(w,.055,.06),0),
                     ((x0,y0,zc),(.055,.06,h),0),((x1,y0,zc),(.055,.06,h),0),
                     ((cx-doorw/2,y0,zc),(.045,.06,h),0),((cx+doorw/2,y0,zc),(.045,.06,h),0)]
    group_doors.append(((cx,y0,11.92),(doorw,.055,2.25),0))
    # Four seats around a compact table; whiteboard at the back.
    group_tables += [((cx,cy,11.42),(min(w-1.0,1.95),.90,.08),0),
                     ((cx-.72,cy,11.05),(.06,.06,.66),1),((cx+.72,cy,11.05),(.06,.06,.66),1)]
    for sx in [-.65,.65]:
        for sy in [-.72,.72]:
            px,py=cx+sx,cy+sy
            group_seats += [((px,py,11.12),(.40,.40,.10),0),((px,py+(.16 if sy>0 else -.16),11.43),(.38,.06,.62),0)]
            for lx in [-.15,.15]:
                for ly in [-.13,.13]: group_seats.append(((px+lx,py+ly,10.96),(.035,.035,.55),1))
    group_boards.append(((cx,y1-.11,12.12),(min(w-1.0,1.7),.035,1.05),0))
combine_boxes("MATH_2026_Inferred_Group_Room_Glazing",library,[groupglass],group_glass)
combine_boxes("MATH_2026_Inferred_Group_Room_Frames",library,[aluminum],group_frames)
combine_boxes("MATH_2026_Inferred_Group_Room_Doors",library,[groupglass],group_doors)
combine_boxes("MATH_2026_Inferred_Group_Room_Tables",library,[oak,steel],group_tables)
combine_boxes("MATH_2026_Inferred_Group_Room_Seats",library,[seat,steel],group_seats)
combine_boxes("MATH_2026_Inferred_Group_Room_Whiteboards",library,[coremat],group_boards)
for nm in ["MATH_2026_Inferred_Group_Room_Glazing","MATH_2026_Inferred_Group_Room_Frames","MATH_2026_Inferred_Group_Room_Doors"]:
    bpy.data.objects[nm]["source_status"]="Group study rooms are documented in Purdue Libraries' 2025 reopening notice. Exact current positions, dimensions, glazing and furniture layout are inferred because no current as-built plan is public."

# Subtle carpet strips make the transverse entry circulation and main vertical
# aisle legible in the top-down review render without claiming exact 2025 routes.
aisle=material("MATH_2026_Library_Aisle_Carpet",(.30,.32,.29),.9)
combine_boxes("MATH_2026_Library_Circulation_Inlay",library,[aisle],[
    ((.35,10.28,10.656),(19.0,1.45,.018),0),
    ((-.2,23.66,10.656),(19.0,1.25,.018),0),
    ((-.1,16.9,10.657),(1.25,12.0,.018),0)])

# Windowless testing room 352: Purdue's 2022 plan labels room 352 at the south-east
# core. Its current use and desktop are confirmed by the 2025 Libraries article;
# the post-renovation partition dimensions remain inferred.
test_x,test_y=6.15,-2.35
roomfloor=combine_boxes("MATH_2026_Testing_Room_352_Carpet",library,[carpet],
    [((test_x,test_y,10.69),(2.45,2.05,.06),0)])
roomwalls=[]
roomwalls += [((test_x-1.225,test_y,12.15),(.12,2.05,2.9),0),
              ((test_x+1.225,test_y,12.15),(.12,2.05,2.9),0),
              ((test_x,test_y+1.025,12.15),(2.45,.12,2.9),0),
              ((test_x-.77,test_y-1.025,12.15),(.91,.12,2.9),0),
              ((test_x+.77,test_y-1.025,12.15),(.91,.12,2.9),0)]
combine_boxes("MATH_2026_Testing_Room_352_Walls",library,[coremat],roomwalls)
combine_boxes("MATH_2026_Testing_Room_352_Door",library,[oak],
    [((test_x,test_y-1.055,11.75),(.78,.06,2.1),0)])
combine_boxes("MATH_2026_Testing_Room_352_Desk",library,[oak,steel],
    [((test_x,test_y+.28,11.39),(1.25,.55,.08),0),((test_x-.44,test_y+.28,11.03),(.06,.06,.64),1),((test_x+.44,test_y+.28,11.03),(.06,.06,.64),1),
     ((test_x,test_y+.02,11.8),(.50,.06,.37),1)])
combine_boxes("MATH_2026_Testing_Room_352_Chair",library,[seat,steel],
    [((test_x,test_y-.53,11.12),(.42,.40,.10),0),((test_x,test_y-.69,11.45),(.40,.06,.66),0),
     ((test_x-.16,test_y-.53,10.96),(.04,.04,.58),1),((test_x+.16,test_y-.53,10.96),(.04,.04,.58),1)])
for nm in ["MATH_2026_Testing_Room_352_Walls","MATH_2026_Testing_Room_352_Door"]:
    bpy.data.objects[nm]["source_status"]="Room 352 label/location read from the 2022 third-floor plan. Windowless use and desktop are documented by Purdue Libraries in 2025. Current partition dimensions and exact door/furniture placement are inferred."

# Remove unsourced gold lettering that crossed a window and facade area.\nold_sign=bpy.data.objects.get("MATH_Signage_East")\nif old_sign:\n    bpy.data.objects.remove(old_sign, do_unlink=True)\n\n# Save source library and a machine-readable summary.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
summary={"asset":"math_sciences.blend","collection":"Asset_math_sciences",
 "new_objects":len(facade.objects)+len(library.objects)+len(floors.objects),
 "facade_window_count":len(glass_boxes),"east_west_primary_facade_bays":len(facade_y),
 "library_group_table_count":2,"library_group_seat_count":8,"individual_carrels":4,
 "bookcase_runs":3,"inferred_group_study_rooms":3,"plan_room_boundaries":6,
 "testing_room":"352","estimated_floor_slabs":9,"third_floor_elevator_count":3,"third_floor_stair_flights":3,
 "geometry_changes":["Removed two source wall prisms and rebuilt the east and south brick elevations with 81 full-depth window openings.",
 "Added pale limestone reveals, subdivided glazing and vertical piers on the major tower elevations.",
 "Retuned the embedded metric Brick Texture shader: visible stretcher courses, warmer red-brown variation, clearer mortar and subtle relief. Applied to the existing envelope and rebuilt panels; no new opening patterns added on the unverified north/west faces.",
 "Added an east-side ground-level glazed entrance portal and canopy.",
 "Added a 9-level estimated interior floor stack to make the existing ten-story envelope read as occupied.",
 "Matched library chair/screen timber and muted carpet colors to the 2025 photo; moved the three shelf runs into the plan-labeled library footprint, leaving counts and positions illustrative.",
 "Rebuilt six 2022 third-floor partition lines around the five labeled 311 library zones, with inferred openings connecting the south/north circulation bands.",
 "Added a low base trim to the same partition segments so room edges and inferred doorway gaps read clearly in the top-down view.",
 "Added three glazed group-study rooms from the 2025 article; their exact current positions and sizes are inferred.",
 "Moved windowless Testing Room 352 to the southeast location labeled 352 in the 2022 plan; current post-2025 partition dimensions remain inferred.",
 "Repositioned the three elevator doors and three schematic stair flights to the north/south core areas visible on the 2022 third-floor plan."],
 "uncertainties":["Only the third-floor plan is available; its room layout dates to 2022 and the current 2025 partition/furniture layout is not published.",
 "The exterior photograph supports narrow repeated windows and pale vertical surrounds, but does not establish exact bay spacing or dimensions.",
 "The official GIS feature includes floor-count and level fields, but field metadata provides no units/definitions; these values are not used to claim measured height. Slab elevations and upper-floor rooms remain estimated.",
 "The Purdue GIS polygon is public campus mapping, not a certified survey; its feature source date is unspecified."],
 "sources":[
 {"url":"https://www.stat.purdue.edu/images/about/Math-Bldg-.jpg","provider":"Purdue Department of Statistics","retrieved":"2026-10-23","source_date":"unknown","crs":"not georeferenced","use":"Exterior red brick, tall narrow window bays and pale vertical framing."},
 {"url":"https://ontour.admissions.purdue.edu/daily-visits/","provider":"Purdue University Office of Admissions","retrieved":"2026-10-23","source_date":"page describes a 2017 Purdue campus photo","crs":"not georeferenced; campus-tour text and photo reference","use":"The Math Building tour note warns visitors walking under its land bridge; supports a ground-level passage but gives no other elevation pattern or dimensions."},
 {"url":"https://www.math.purdue.edu/~lipeijun/conference/wip2013/directions.html","provider":"Purdue Department of Mathematics","retrieved":"2026-10-23","source_date":"2013","crs":"not georeferenced; text description","use":"Building described as light red brick; supports a pedestrian breezeway below the building (the Math Building 'breeze way underneath')."},
 {"url":"https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/Libraries%20Study%20Space%20Reno.pdf","provider":"Purdue University Board of Trustees / Administrative Operations","retrieved":"2026-10-23","source_date":"2022-09-28","crs":"not georeferenced; plan sheet","use":"Third-floor library area (2,884 GSF), circulation cores and renovation footprint."},
 {"url":"https://blogs.lib.purdue.edu/news/tag/general/page/6/","provider":"Purdue Libraries and School of Information Studies","retrieved":"2026-10-23","source_date":"2025-09-09","crs":"not georeferenced; interior photo and program description","use":"Current library's carpeted zones, rearranged bookshelves, added group rooms and windowless room 352 testing room."},
 {"url":"https://www.google.com/maps/place/Purdue+Mathematical+Sciences+Building/@40.4261348,-86.915642,17z/","provider":"Google Maps","retrieved":"2026-10-23","source_date":"imagery dates vary by panel","crs":"WGS84 map pin at 40.4261348,-86.915642; transformed with project local approximation","use":"Confirms 150 N University Street identity and east-side entrance area; pin lies about 15.4m from official polygon centroid and is not treated as a surveyed building center."},
 {"url":"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D227&outFields=*&returnGeometry=true&outSR=4326&f=geojson","provider":"Purdue University GIS / ArcGIS FeatureServer","feature_id":227,"retrieved":"2026-10-23","source_date":"not stated","source_crs":"EPSG:4326","use":"Raw MATH footprint polygon and attributes used for bidirectional structural edge comparison. Geometry snapshot: gis_fid227.geojson; feature attributes: gis_fid227_attributes.json. Story/elevation fields have no published descriptions or unit semantics and are not used as measured height evidence."}]}
(OUT/"changes.json").write_text(json.dumps(summary,indent=2))
print("MATH FINISH",summary)


