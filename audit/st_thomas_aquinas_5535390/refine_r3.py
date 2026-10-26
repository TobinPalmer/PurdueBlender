"""R3 refinement: masonry UVs, component-aligned sanctuary, and schematic two-level classrooms."""
import bpy, json, math
from pathlib import Path
from mathutils import Matrix, Vector

ROOT=Path(__file__).resolve().parents[2]
AUDIT=Path(__file__).resolve().parent
ASSET_PATH=ROOT/"modular/buildings/massing_st_thomas_aquinas_5535390.blend"
ASSET_NAME="Asset_massing_st_thomas_aquinas_5535390"
asset=bpy.data.collections.get(ASSET_NAME)
if asset is None: raise RuntimeError("Expected stable asset collection is missing")
root=bpy.data.objects.get("AssetRoot_massing_st_thomas_aquinas_5535390")
if root is None: raise RuntimeError("Stable local root is missing")

# Remove R3 additions when rebuilding from the previous saved baseline.
for ob in list(asset.objects):
    if ob.name.startswith("SOTAC_R3_"):
        bpy.data.objects.remove(ob,do_unlink=True)
for c in list(asset.children):
    if c.name=="SOTAC_R3_Sanctuary_Local_Adjustment":
        for ob in list(c.objects):
            if ob.name.startswith("SOTAC_R3_"): bpy.data.objects.remove(ob,do_unlink=True)
        bpy.data.collections.remove(c)

def create_box(name,loc,dims,mat,angle=0.0,bevel=0.015):
    x,y,z=(float(v) for v in dims)
    verts=[(-x/2,-y/2,-z/2),(x/2,-y/2,-z/2),(x/2,y/2,-z/2),(-x/2,y/2,-z/2),
           (-x/2,-y/2,z/2),(x/2,-y/2,z/2),(x/2,y/2,z/2),(-x/2,y/2,z/2)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(name+"Mesh");me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);asset.objects.link(ob);ob.parent=root;ob.location=loc;ob.rotation_euler.z=angle
    if mat:me.materials.append(mat)
    if bevel>0:
        mod=ob.modifiers.new("R3 softly finished edge","BEVEL");mod.width=bevel;mod.segments=2;mod.limit_method="ANGLE"
        ob.modifiers.new("R3 weighted surface normals","WEIGHTED_NORMAL")
    return ob

def create_beam(name,a,b,width,depth,mat):
    av,bv=Vector(a),Vector(b);delta=bv-av
    ob=create_box(name,(av+bv)*0.5,(width,depth,delta.length),mat,bevel=0.008)
    ob.rotation_mode="QUATERNION";ob.rotation_quaternion=delta.to_track_quat("Z","Y")
    return ob

def create_polygon_slab(name,points,z0,z1,mat):
    pts=[tuple(p) for p in points]
    area=sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))/2
    if area<0:pts.reverse()
    n=len(pts);verts=[(x,y,z0) for x,y in pts]+[(x,y,z1) for x,y in pts]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    me=bpy.data.meshes.new(name+"Mesh");me.from_pydata(verts,[],faces);me.validate();me.update()
    ob=bpy.data.objects.new(name,me);asset.objects.link(ob);ob.parent=root;me.materials.append(mat)
    bevel=ob.modifiers.new("R3 slab edge","BEVEL");bevel.width=.012;bevel.segments=2
    ob.modifiers.new("R3 slab normals","WEIGHTED_NORMAL")
    return ob

def material(name):
    return bpy.data.materials.get(name)

brick=material("SOTAC_Procedural_Red_Brick")
interior_brick=material("SOTAC_Interior_Exposed_Brick")
stone=material("SOTAC_Limestone_Trim")
dark=material("SOTAC_Recess_Shadow")
wood=material("SOTAC_Warm_Oak")
wood_light=material("SOTAC_Pew_Oak")
floor_mat=material("SOTAC_Interior_Limestone_Floor")
glass=material("SOTAC_Glazing_Deep_Blue")

# Build real metre-based UVs on wall faces, aligned with each facade's longest horizontal edge.
# This fixes the R2 vertical banding from sampling a horizontal-plane brick texture on 3D walls.
def unwrap_masonry(obj):
    mesh=obj.data
    uv=mesh.uv_layers.active or mesh.uv_layers.new(name="Facade_Masonry_Meters")
    for poly in mesh.polygons:
        ids=list(poly.vertices)
        if abs(poly.normal.z)>0.55:
            tangent=Vector((1,0,0))
        else:
            best=Vector((1,0,0));best_len=0.0
            for j,idx in enumerate(ids):
                a=mesh.vertices[idx].co;b=mesh.vertices[ids[(j+1)%len(ids)]].co
                d=Vector((b.x-a.x,b.y-a.y,0))
                if d.length>best_len:best=d;best_len=d.length
            tangent=best.normalized() if best_len>1e-6 else Vector((1,0,0))
        for li in poly.loop_indices:
            co=mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv=(co.x*tangent.x+co.y*tangent.y,co.z if abs(poly.normal.z)<0.55 else co.y)

def set_brick_shader(mat,color1,color2,mortar):
    if not mat: return
    mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear()
    out=nt.nodes.new("ShaderNodeOutputMaterial");out.location=(560,20)
    bsdf=nt.nodes.new("ShaderNodeBsdfPrincipled");bsdf.location=(300,20)
    bsdf.inputs["Roughness"].default_value=.87
    texcoord=nt.nodes.new("ShaderNodeTexCoord");texcoord.location=(-700,60)
    bricknode=nt.nodes.new("ShaderNodeTexBrick");bricknode.location=(-430,100)
    bricknode.inputs["Color1"].default_value=(*color1,1)
    bricknode.inputs["Color2"].default_value=(*color2,1)
    bricknode.inputs["Mortar"].default_value=(*mortar,1)
    bricknode.inputs["Scale"].default_value=.90
    bricknode.inputs["Brick Width"].default_value=.42
    bricknode.inputs["Row Height"].default_value=.095
    bricknode.inputs["Mortar Size"].default_value=.014
    bricknode.inputs["Mortar Smooth"].default_value=.03
    nt.links.new(texcoord.outputs["UV"],bricknode.inputs["Vector"])
    bump=nt.nodes.new("ShaderNodeBump");bump.location=(80,-120)
    bump.inputs["Strength"].default_value=.14;bump.inputs["Distance"].default_value=.025
    nt.links.new(bricknode.outputs["Fac"],bump.inputs["Height"])
    nt.links.new(bricknode.outputs["Color"],bsdf.inputs["Base Color"])
    nt.links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs["BSDF"],out.inputs["Surface"])
    mat.diffuse_color=(*color1,1)

set_brick_shader(brick,(.43,.135,.075),(.27,.060,.036),(.20,.145,.105))
set_brick_shader(interior_brick,(.50,.245,.155),(.34,.115,.067),(.28,.205,.15))
# Tower, entry-bay and parapet masonry use the same physically scaled, portable texture.
for ob in list(asset.all_objects):
    if ob.type!="MESH": continue
    for i,mat in enumerate(list(ob.data.materials)):
        if mat and mat.name=="SOTAC_Tower_Brick":ob.data.materials[i]=brick
    if any(m and m.name in {"SOTAC_Procedural_Red_Brick","SOTAC_Interior_Exposed_Brick"} for m in ob.data.materials):
        unwrap_masonry(ob)
# The generic colored glass reads more credibly as consistent reflective glazing; the sanctuary altar
# keeps its own colored panel accents as a separate focal feature.
for ob in asset.all_objects:
    if ob.type=="MESH" and ob.name.startswith("SOTAC_Window_") and ob.name.endswith("_Glass"):
        if ob.data.materials:
            ob.data.materials[0]=glass

# Add horizontal stone stringcourses so the long brick elevations read as masonry construction
# and separate the two visible storeys. Offset just outside each polygon edge.
ev=json.loads((AUDIT/"projected_footprint_evidence.json").read_text(encoding="utf-8"))
outline=[tuple(p) for p in ev["local_outline_xy_m"][:-1]]
for course_index,z in enumerate((3.18,6.08)):
    for i,p in enumerate(outline):
        q=outline[(i+1)%len(outline)];dx=q[0]-p[0];dy=q[1]-p[1];length=math.hypot(dx,dy)
        if length<1.0:continue
        nx,ny=dy/length,-dx/length;mid=((p[0]+q[0])/2+nx*.07,(p[1]+q[1])/2+ny*.07,z)
        create_box(f"SOTAC_R3_Stone_Stringcourse_{course_index}_{i}",mid,(length,.22,.16),stone,math.atan2(dy,dx),.018)

# Align the sanctuary furnishings, arch, pews, and timber framing with the west component under the
# documented gabled sanctuary. The fit is approximate; the three parish buildings have no public plan.
adjust=bpy.data.objects.new("SOTAC_R3_Sanctuary_Alignment",None);asset.objects.link(adjust);adjust.parent=root
adjust.location=(-17.98,0,0);adjust.scale=(.72,1,1)
sanctuary_prefixes=("SOTAC_Interior_Sanctuary","SOTAC_Interior_Pew","SOTAC_Altar_","SOTAC_Ambo_",
                    "SOTAC_Baptismal_","SOTAC_CeilingTruss_","SOTAC_Sanctuary_Pendant_")
for ob in list(asset.objects):
    if ob is adjust:continue
    if ob.name.startswith(sanctuary_prefixes):
        # Compress the paired pew banks around their centerlines to create a plausible central aisle.
        if ob.name.startswith("SOTAC_Interior_Pew_") and ob.type=="MESH":
            center=4.3 if "_Left_" in ob.name else 13.7
            for v in ob.data.vertices:v.co.x=center+(v.co.x-center)*.70
        if ob.parent==root:
            ob.parent=adjust;ob.matrix_parent_inverse=Matrix.Identity(4)

# Expand the office/classroom portion into a legible, explicitly schematic second floor with a stair
# opening. The southern wing is described as office/classroom use; actual partitions are unverified.
south=ev["footprint_parts_local_xy_m"]["office_classroom_addition_south"][:-1]
south=[tuple(p) for p in south]
# Replace the original rectangular classroom floor with the connected component's exact plan region.
old_floor=bpy.data.objects.get("SOTAC_Interior_OfficeWing_Floor")
if old_floor:bpy.data.objects.remove(old_floor,do_unlink=True)
create_polygon_slab("SOTAC_R3_OfficeWing_GroundFloor",south,.585,.69,floor_mat)
# The office wing's broad southern rectangle receives an upper floor. We leave a stairwell void
# and keep this second-floor slab conservative to avoid asserting the exact extension layout.
def rectangle(x0,x1,y0,y1):return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
for name,pts in (("West",rectangle(-14.35,-2.35,-32.7,-15.45)),
                 ("East",rectangle(2.35,16.8,-32.7,-15.45)),
                 ("HallSouth",rectangle(-2.35,2.35,-32.7,-24.0)),
                 ("HallNorth",rectangle(-2.35,2.35,-18.0,-15.45)),
                 ("HallStairSideWest",rectangle(-2.35,-1.35,-24.0,-18.0)),
                 ("HallStairSideEast",rectangle(1.35,2.35,-24.0,-18.0))):
    create_polygon_slab("SOTAC_R3_OfficeWing_SecondFloor_"+name,pts,3.42,3.62,floor_mat)
plaster=material("SOTAC_Interior_Warm_Plaster")
def wall_x(name,x,y0,y1,z0,z1,door_centers=()):
    intervals=[(y0,y1)]
    for center in door_centers:
        nexts=[]
        for a,b in intervals:
            lo=max(a,center-.55);hi=min(b,center+.55)
            if lo>a:nexts.append((a,lo))
            if hi<b:nexts.append((hi,b))
        intervals=nexts
    for j,(a,b) in enumerate(intervals):
        if b-a>.12:create_box(name+f"_Segment{j}",(x,(a+b)/2,(z0+z1)/2),(.16,b-a,z1-z0),plaster)
    for j,center in enumerate(door_centers):
        if center<y0 or center>y1:continue
        create_box(name+f"_DoorHeader{j}",(x,center,z0+2.3),(.20,1.14,max(.18,z1-z0-2.3)),plaster,.0,.008)
        create_box(name+f"_DoorPanel{j}",(x,center,z0+1.05),(.055,.92,2.10),wood,.0,.015)
def wall_y(name,y,x0,x1,z0,z1,corridor=(-1.2,1.2)):
    # Paired partition runs stop short of the central hall and stairwell.
    for side,(a,b) in enumerate(((x0,min(x1,corridor[0])),(max(x0,corridor[1]),x1))):
        if b-a>.15:create_box(name+f"_Side{side}",((a+b)/2,y,(z0+z1)/2),(b-a,.16,z1-z0),plaster,.0,.008)

# Existing generic cross-wing dividers are replaced by walls with door openings.
for ob in list(asset.objects):
    if ob.name.startswith(("SOTAC_Office_Interior_Partition_",)):
        bpy.data.objects.remove(ob,do_unlink=True)
for story,(z0,z1,ymin,ymax,door_ys,cross_ys) in enumerate((
    (.68,3.42,-31.7,-9.7,(-28.0,-21.0,-14.0),(-24.55,-17.55,-10.55)),
    (3.62,6.45,-31.7,-15.5,(-28.0,-21.0),(-24.55,-17.55)))):
    label=f"SOTAC_R3_Office_Story{story+1}"
    for x in (-2.35,2.35):
        wall_x(label+f"_HallWall_{x}",x,ymin,ymax,z0,z1,door_ys)
    for j,y in enumerate(cross_ys):
        wall_y(label+f"_ClassDivider{j}",y,-13.3,16.4,z0,z1)

# Move existing first-floor table groups out of the central corridor, one row per schematic room.
for i,y in enumerate((-28.0,-21.0,-14.0)):
    table=bpy.data.objects.get(f"SOTAC_Classroom_Table_{i}")
    if table:table.location.x=-8.3
    for side in (-1,1):
        for j in (-1,0,1):
            ob=bpy.data.objects.get(f"SOTAC_Classroom_Chair_{i}_{side}_{j}")
            if ob:ob.location.x-=8.3

def classroom_set(prefix,x,y,zfloor,chair_mat=wood):
    create_box(prefix+"_Tabletop",(x,y,zfloor+.78),(2.75,1.0,.12),wood_light,.0,.02)
    for dx in (-1.14,1.14):
        for dy in (-.35,.35):create_box(prefix+f"_Leg_{dx}_{dy}",(x+dx,y+dy,zfloor+.39),(.10,.10,.74),wood,.0,.008)
    for side in (-1,1):
        for dx in (-.76,0,.76):
            cx=x+dx;cy=y+side*.87
            create_box(prefix+f"_ChairSeat_{side}_{dx}",(cx,cy,zfloor+.45),(.46,.46,.10),chair_mat,.0,.015)
            create_box(prefix+f"_ChairBack_{side}_{dx}",(cx,cy+side*.19,zfloor+.73),(.46,.10,.48),chair_mat,.0,.015)

# Right-hand first floor room sets; the original tables/chairs now represent matching left rooms.
for i,y in enumerate((-28.0,-21.0,-14.0)):
    classroom_set(f"SOTAC_R3_Classroom_R1_{i}",8.8,y,.66)
# Furnish three rooms per side upstairs; exact classroom counts and furniture are not documented.
for i,y in enumerate((-28.0,-21.0)):
    classroom_set(f"SOTAC_R3_Classroom_R2_L_{i}",-8.3,y,3.62)
    classroom_set(f"SOTAC_R3_Classroom_R2_R_{i}",8.8,y,3.62)
    for side,x in (("L",-12.2),("R",12.6)):
        create_box(f"SOTAC_R3_Upstairs_Bookcase_{side}_{i}",(x,y+1.9,4.75),(2.0,.42,2.0),wood,.0,.025)
        for row in range(3):
            create_box(f"SOTAC_R3_Upstairs_Bookshelf_{side}_{i}_{row}",(x,y+1.9,4.05+row*.60),(1.9,.46,.08),wood_light,.0,.008)

# A compact open stair runs inside the central hall through a 2.5 x 6 m floor opening.
# Second-floor slab is partitioned around that void; no exact placement is claimed.
# Use visible landing markers and stepped treads so the level connection reads clearly in cutaway.
stair_w=2.25
for i in range(12):
    yy=-24.0+i*.50;zz=.82+i*.225
    create_box(f"SOTAC_R3_Stair_Tread_{i:02d}",(0.0,yy,zz),(stair_w,.55,.16),stone,.0,.025)
for side in (-1,1):
    x=side*(stair_w/2+.10)
    create_beam(f"SOTAC_R3_Stair_Handrail_{side}",(x,-24.0,1.5),(x,-18.5,3.45),.045,.045,dark)
    for i in range(0,12,2):
        yy=-24.0+i*.50;zz=.93+i*.225
        create_box(f"SOTAC_R3_Stair_Post_{side}_{i}",(x,yy,zz+.38),(.045,.045,.76),dark,.0,.004)

# Store building-specific uncertainty and source trail next to the rendered review package.
record={"revision":"R3","retrieved_utc_date":"2026-10-25",
 "stable_asset_id":"massing_st_thomas_aquinas_5535390","GIS_FID":852,"OSM_way_id":117396617,
 "local_origin_xy_m":[21.32823749544109,-412.2141452954931],"GIS_source_crs":"EPSG:3857 (WKID 102100)",
 "projection":"EPSG:4326 geometry transformed with Purdue local approximate conversion per modular/AGENTS.md",
 "sources":[{"url":"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/852","provider":"Purdue GIS ArcGIS FeatureServer","feature":"FID 852, St. Thomas Aquinas Center","retrieved":"2026-10-25"},
 {"url":"https://www.openstreetmap.org/way/117396617","provider":"OpenStreetMap","feature":"way 117396617, St. Thomas Aquinas","retrieved":"2026-10-25"},
 {"url":"https://www.jwmcq.com/st-thomas-aquinas","provider":"J.W. McQuiston Architecture","feature":"St. Thomas Aquinas; project description and images View from 46th St., Narthex entry, Chapel exterior","retrieved":"2026-10-25"},
 {"url":"https://www.boilercatholics.org/project-renewal","provider":"St. Thomas Aquinas Catholic Center at Purdue","feature":"Project Renewal: three connected buildings; office/classroom windows; 2026 accessibility ramp/confessionals","retrieved":"2026-10-25"}],
 "geometry_edits":["Added metre-based facade UVs so brick courses run horizontally rather than sampling as vertical stripes.","Moved the schematic sanctuary interior under the west/north gabled church component and compressed paired pews around a central aisle.","Added stone story stringcourses to long elevations.","Added schematic second-floor classroom slab, partitions with door openings, classroom groups, bookcases, stair treads, and railings."],
 "uncertainty":["Parish confirms three connected components but public plans do not identify their exact current junctions or internal partitions.","The sanctuary-to-gable placement is an evidence-guided interpretation; exact room layout, furniture, stair position, dimensions, roof pitch and tower height remain unverified.","The second-floor classroom plan and stair are schematic, not measured; source GIS outline is a footprint reference, not surveyed wall lines."]}
(AUDIT/"r3_design_evidence.json").write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
print("R3 saved",str(ASSET_PATH),"objects",len(asset.all_objects))
