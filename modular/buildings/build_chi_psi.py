"""Build a detailed Chi Psi Epsilon Tau Lodge asset from its GIS crosswalk.

Run from the repository root with Blender 5.2:
  blender -b --python modular/buildings/build_chi_psi.py

The asset is local-coordinate geometry centered on the transformed Indiana
2018 LiDAR outline for the structure at 950 David Ross Road. Purdue GIS FID
748 anchors the address but has a poor outline fit and retains a conflicting
Zeta Psi label; see the building-specific evidence record.
"""
from pathlib import Path
import bpy, json, math
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "chi_psi"
GIS = AUDIT / "sources" / "purdue_gis_FID748_2026-10-27.json"
LIDAR = AUDIT / "sources" / "indiana_lidar_footprints_near_fid748_2026-10-26.json"
OUT = ROOT / "modular" / "buildings" / "chi_psi.blend"
AUDIT.mkdir(parents=True, exist_ok=True)
assert GIS.exists(), f"Missing preserved GIS source: {GIS}"

raw = json.loads(GIS.read_text(encoding="utf-8-sig"))
fid_feature = next(f for f in raw["features"] if f["attributes"]["FID"] == 748)
attrs = fid_feature["attributes"]
assert attrs["ADDRESS"] == "950 David Ross Rd"
lidar_raw = json.loads(LIDAR.read_text(encoding="utf-8-sig"))
lidar_feature = next(f for f in lidar_raw["features"] if f["attributes"]["objectid"] == 409718)
lidar_attrs = lidar_feature["attributes"]
assert str(lidar_attrs["lidaryear"]) == "2018"
# Purdue FID 748 anchors the exact civic address but its outline is a poor fit
# to the 2018 roof/building footprint. The detailed structural shell follows
# the independently sourced state LiDAR polygon at the same parcel/address.
ring_ll = lidar_feature["geometry"]["rings"][0]
if ring_ll[0] == ring_ll[-1]:
    ring_ll = ring_ll[:-1]
LAT0, LON0 = 40.4274, -86.9137
def campus_xy(lon, lat):
    return ((lon-LON0)*111412.84*math.cos(math.radians(LAT0)),
            (lat-LAT0)*111040.0)
world = [campus_xy(lon, lat) for lon,lat in ring_ll]
origin = (sum(p[0] for p in world)/len(world), sum(p[1] for p in world)/len(world))
ring = [(x-origin[0], y-origin[1]) for x,y in world]
# The raw rectangle's first edge is the long building axis. Set local X along
# the edge toward northwest, local Y into the polygon. This preserves absolute
# GIS orientation with zero extra yaw at the master placement marker.
p0,p1,p2,p3 = [Vector(p) for p in ring]
axis_x = (p0-p1).normalized()
axis_y = Vector((-axis_x.y, axis_x.x))
assert (p2-p1).normalized().dot(axis_y) > 0.999
length = (p1-p0).length
depth = (p2-p1).length
def local_xy(p):
    d = Vector(p)
    return (d.dot(axis_x), d.dot(axis_y))
foot = [local_xy(p) for p in ring]
half_x, half_y = length/2, depth/2
assert abs(max(x for x,y in foot)-half_x) < 0.05
assert abs(min(x for x,y in foot)+half_x) < 0.05
assert abs(max(y for x,y in foot)-half_y) < 0.05
assert abs(min(y for x,y in foot)+half_y) < 0.05
footprint_area_local = length*depth

# A clean library file: no environment, only one stable export collection.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    for datablock in list(datablocks):
        if datablock.users == 0:
            datablocks.remove(datablock)
scene = bpy.context.scene
scene.name = "Building_chi_psi"
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1400
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.filepath = str(AUDIT / "chi_psi_front_render.png")
scene.render.image_settings.color_mode = "RGBA"
scene.world.color = (0.34,0.40,0.5)

coll = bpy.data.collections.new("Asset_chi_psi")
scene.collection.children.link(coll)
schem = bpy.data.collections.new("Schematic_Interior_chi_psi")
coll.children.link(schem)
preview = bpy.data.collections.new("Preview_Only_Render_Rig")
scene.collection.children.link(preview)

def mat(name, color, rough=0.7, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color,1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    return m

brick = mat("ChiPsi_Warm_Red_Brick", (0.42,0.085,0.045), .83)
mortar = mat("ChiPsi_Light_Masonry_Mortar", (.60,.52,.43), .9)
stone = mat("ChiPsi_Light_Limestone_Trim", (.70,.66,.57), .78)
roofmat = mat("ChiPsi_Charcoal_Architectural_Shingle", (.075,.085,.095), .86)
glass = mat("ChiPsi_Reflective_Glass", (.035,.105,.15), .18, .22)
white = mat("ChiPsi_Painted_Window_Trim", (.88,.84,.74), .62)
wood = mat("ChiPsi_Stained_Entry_Door", (.18,.075,.035), .6)
concrete = mat("ChiPsi_Concrete", (.38,.38,.35), .9)
metal = mat("ChiPsi_Dark_Bronze_Metal", (.12,.10,.075), .3, .65)
interior = mat("ChiPsi_Schematic_Interior_Warm", (.44,.31,.18), .8)
floor_mat = mat("ChiPsi_Schematic_Floor", (.48,.43,.34), .85)

angle = math.atan2(axis_x.y, axis_x.x)
def link_obj(obj, collection=coll):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj
def cube(name, loc, dims, material, collection=coll, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0],loc[1],loc[2]))
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.rotation_euler[2]=angle
    link_obj(o,collection)
    if material: o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new("Soft masonry arris","BEVEL"); mod.width=bevel; mod.segments=2
    return o
def mesh_obj(name, verts, faces, material, collection=coll):
    me=bpy.data.meshes.new(name+"Mesh"); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    ob=bpy.data.objects.new(name,me); collection.objects.link(ob); return ob
def oriented_mesh(name, verts_local, faces, material, collection=coll):
    verts=[]
    for x,y,z in verts_local:
        wx=x*axis_x.x+y*axis_y.x
        wy=x*axis_x.y+y*axis_y.y
        verts.append((wx,wy,z))
    return mesh_obj(name,verts,faces,material,collection)
def oriented_cube(name,x,y,z,dx,dy,dz,material,collection=coll,bevel=0):
    loc=(x*axis_x.x+y*axis_y.x,x*axis_x.y+y*axis_y.y,z)
    # Cubes are created with local X along the long GIS axis.
    return cube(name,loc,(dx,dy,dz),material,collection,bevel)
def batch_local_box(vertices, faces, x,y,z,dx,dy,dz):
    base=len(vertices)
    points=[(x+sx*dx/2,y+sy*dy/2,z+sz*dz/2)
            for sx,sy,sz in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                             (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1))]
    vertices.extend(points)
    faces.extend([tuple(base+i for i in f) for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])

# Footprint shell, walls, and floor bands. Geometry dimensions follow the GIS
# rectangle; facade components add only shallow trim/porch overhangs.
z0, zbase, zupper, zeave, zr = 0.0, .34, 3.75, 7.05, 11.65
oriented_cube("ChiPsi_LiDAR_Footprint_Foundation",0,0,zbase/2,length,depth,zbase,concrete,bevel=.08)
oriented_cube("ChiPsi_Main_Red_Brick_Shell",0,0,(zbase+zeave)/2,length-.24,depth-.24,zeave-zbase,brick)
oriented_cube("ChiPsi_Entry_Stone_Water_Table",0,-half_y+.04,.48,length-.35,.14,.28,stone)
oriented_cube("ChiPsi_Sill_Course_Floor_2",0,-half_y+.05,3.72,length-.38,.13,.18,stone)
oriented_cube("ChiPsi_Cornice_Front",0,-half_y+.02,zeave-.05,length-.2,.25,.30,stone)
oriented_cube("ChiPsi_Cornice_Back",0,half_y-.02,zeave-.05,length-.2,.25,.30,stone)
# Twin steep gables reproduce the two clearly legible front peaks in the
# chapter's own lodge photograph; their unmeasured dimensions are estimates.
gables=[(-6.15,10.0),(6.15,10.0)]
gwidth=7.4
for idx,(cx,peak) in enumerate(gables,1):
    left,right=cx-gwidth/2,cx+gwidth/2
    yfront=-half_y-.18; roof_front=-half_y+.30; yback=half_y+.18
    # Triangular brick infill on the front, solid and well-named.
    oriented_mesh(f"ChiPsi_Front_Gable_{idx}",[(left,yfront,zeave),(right,yfront,zeave),(cx,yfront,peak)],[(0,1,2)],brick)
    # Paired pitched roofing planes from the ridge to each gable edge.
    oriented_mesh(f"ChiPsi_Roof_Left_Slope_{idx}",[(left,roof_front,zeave),(cx,roof_front,peak),(cx,yback,peak),(left,yback,zeave)],[(0,1,2,3)],roofmat)
    oriented_mesh(f"ChiPsi_Roof_Right_Slope_{idx}",[(cx,roof_front,peak),(right,roof_front,zeave),(right,yback,zeave),(cx,yback,peak)],[(0,1,2,3)],roofmat)
    # Front rake boards and peak cap.
    # Light rake trim follows each slope as a true front-facing curve.
    for side,xa,xb,za,zb in (("L",left,cx,zeave,peak),("R",cx,right,peak,zeave)):
        cu=bpy.data.curves.new(f"ChiPsi_Gable_Rake_{side}_{idx}","CURVE"); cu.dimensions="3D"; cu.bevel_depth=.075; cu.bevel_resolution=3
        spl=cu.splines.new("POLY"); spl.points.add(1)
        for k,(xx,zz) in enumerate(((xa,za),(xb,zb))):
            wx=xx*axis_x.x+yfront*axis_y.x; wy=xx*axis_x.y+yfront*axis_y.y
            spl.points[k].co=(wx,wy,zz,1)
        ob=bpy.data.objects.new(f"ChiPsi_Gable_Rake_{side}_{idx}",cu); coll.objects.link(ob); cu.materials.append(white)
    # Tall paired upper-storey feature windows: glazing + casing and mullions.
    for j,wx in enumerate((cx-1.18,cx+1.18),1):
        bottom=5.05; top=8.95; width=.94
        oriented_cube(f"ChiPsi_ArchWindow_{idx}_{j}_Glass",wx,yfront-.09,(bottom+top)/2,width,.07,top-bottom,glass)
        for dx in (-width/2-.09,width/2+.09):
            oriented_cube(f"ChiPsi_ArchWindow_{idx}_{j}_Jamb_{dx:+.2f}",wx+dx,yfront-.14,(bottom+top)/2,.12,.14,top-bottom+.24,white)
        oriented_cube(f"ChiPsi_ArchWindow_{idx}_{j}_Sill",wx,yfront-.14,bottom,width+.30,.14,.14,stone)
        oriented_cube(f"ChiPsi_ArchWindow_{idx}_{j}_Lintel",wx,yfront-.14,top,width+.30,.14,.12,white)
        oriented_cube(f"ChiPsi_ArchWindow_{idx}_{j}_Mullion",wx,yfront-.15,(bottom+top)/2,.08,.08,top-bottom,white)
        # Rounded arch cap (segmented trim curve) completes the tall arched look.
        cu=bpy.data.curves.new(f"ChiPsi_ArchTrim_{idx}_{j}","CURVE"); cu.dimensions="3D"; cu.bevel_depth=.055; cu.bevel_resolution=2
        spl=cu.splines.new("POLY"); spl.points.add(16)
        radius=width/2+.10; centerz=top-.04
        for k,pt in enumerate(spl.points):
            a=math.pi*k/16; xx=wx+radius*math.cos(a); zz=centerz+radius*math.sin(a)
            qx=xx*axis_x.x+(yfront-.17)*axis_y.x; qy=xx*axis_x.y+(yfront-.17)*axis_y.y
            pt.co=(qx,qy,zz,1)
        ob=bpy.data.objects.new(f"ChiPsi_ArchTrim_{idx}_{j}",cu); coll.objects.link(ob); cu.materials.append(white)

# Twin lower storefront-like sash rhythm and side elevations.
front_y=-half_y-.08
# Repeating horizontal bed joints and staggered vertical joints provide legible
# masonry courses without relying on object-generated texture coordinates.
row_index=0
zline=.52
mortar_vertices=[]; mortar_faces=[]
while zline < zeave-.1:
    width_here=length-.55
    batch_local_box(mortar_vertices,mortar_faces,0,front_y+.04,zline,width_here,.035,.022)
    start=-width_here/2 + (0 if row_index%2==0 else .32)
    x=start
    col=0
    while x < width_here/2:
        batch_local_box(mortar_vertices,mortar_faces,x,front_y+.035,zline+.125,.018,.035,.22)
        x+=.64; col+=1
    row_index+=1; zline+=.26
# Courses taper into both front gables; these remain deliberately subtle.
for idx,(cx,peak) in enumerate(gables,1):
    zline=zeave+.24; rid=0
    while zline < peak-.1:
        halfw=(gwidth/2)*(peak-zline)/(peak-zeave)
        batch_local_box(mortar_vertices,mortar_faces,cx,-half_y-.18,zline,max(.1,2*halfw-.1),.035,.022)
        rid+=1; zline+=.26
oriented_mesh("ChiPsi_Front_Brick_Courses_and_Mortar",mortar_vertices,mortar_faces,mortar)
for row,zc in enumerate((1.72,5.05),1):
    xpositions=(-10.1,-3.3,3.3,10.1) if row==1 else (-10.1,-3.3,3.3,10.1)
    for i,x in enumerate(xpositions,1):
        w,h=(1.55,1.65) if row==1 else (1.32,1.9)
        oriented_cube(f"ChiPsi_FrontWindow_R{row}_{i}_Glass",x,front_y,zc,w,.06,h,glass)
        for dx in (-w/2-.09,w/2+.09):
            oriented_cube(f"ChiPsi_FrontWindow_R{row}_{i}_Jamb_{dx:+.2f}",x+dx,front_y-.07,zc,.12,.11,h+.20,white)
        oriented_cube(f"ChiPsi_FrontWindow_R{row}_{i}_Head",x,front_y-.07,zc+h/2,w+.30,.11,.13,white)
        oriented_cube(f"ChiPsi_FrontWindow_R{row}_{i}_Sill",x,front_y-.08,zc-h/2,w+.34,.15,.17,stone)
        oriented_cube(f"ChiPsi_FrontWindow_R{row}_{i}_Mullion",x,front_y-.08,zc,.07,.08,h,white)

# Entry bay, door, transom, pediment and landing. Location is inferred from the
# official frontal photo; it is not a surveyed opening coordinate.
doorx=-7.0
oriented_cube("ChiPsi_Entry_Stone_Pilasters",doorx,front_y-.14,1.7,1.82,.26,3.35,stone)
oriented_cube("ChiPsi_Entry_Wood_Double_Door",doorx,front_y-.30,1.55,1.40,.12,2.55,wood)
oriented_cube("ChiPsi_Entry_Transom_Glass",doorx,front_y-.32,2.93,1.05,.07,.42,glass)
oriented_cube("ChiPsi_Entry_Lintel",doorx,front_y-.35,3.32,2.14,.32,.23,stone)
oriented_cube("ChiPsi_Entry_Portico_Roof",doorx,front_y-.67,3.68,3.0,1.18,.24,roofmat)
oriented_cube("ChiPsi_Entry_Portico_Fascia",doorx,front_y-1.20,3.62,3.0,.10,.34,white)
oriented_mesh("ChiPsi_Entry_Portico_Gable",[(doorx-1.40,front_y-.18,3.72),(doorx+1.40,front_y-.18,3.72),(doorx,front_y-.18,4.62)],[(0,1,2)],white)
oriented_cube("ChiPsi_Entry_Landing",doorx,front_y-1.55,.24,3.7,2.6,.28,concrete)
for i in range(5):
    oriented_cube(f"ChiPsi_Entry_Stair_{i+1}",doorx,front_y-2.0-i*.36,.17+i*.04,3.0, .42,.18,concrete)
for sx in (-1.35,1.35):
    oriented_cube(f"ChiPsi_Entry_Railing_Post_{sx}",doorx+sx,front_y-2.45,.80,.09,.09,1.0,metal)
oriented_cube("ChiPsi_Entry_Railing",doorx,front_y-2.45,1.18,2.7,.07,.07,metal)

# Chi Psi name/sign plaque centered between the front gables.
oriented_cube("ChiPsi_Chapter_Sign_Backplate",0,front_y-.13,2.65,2.75,.10,.82,stone)
oriented_cube("ChiPsi_Chapter_Sign_Inset",0,front_y-.20,2.65,2.43,.07,.55,metal)
txt=bpy.data.curves.new("ChiPsi_Chapter_Sign_Lettering","FONT"); txt.body="CHI PSI"; txt.align_x="CENTER"; txt.align_y="CENTER"; txt.size=.34; txt.extrude=.004
textob=bpy.data.objects.new("ChiPsi_Chapter_Sign_Lettering",txt); coll.objects.link(textob)
textob.location=(0*axis_x.x+(front_y-.25)*axis_y.x,0*axis_x.y+(front_y-.25)*axis_y.y,2.65)
textob.rotation_euler=(math.pi/2,0,angle); txt.materials.append(white)

# Side/back fenestration gives the structure a readable full exterior.
for side_y,tag in ((half_y+.05,"Rear"),(-half_y-.05,"FrontSide")):
    for floor,z in enumerate((1.72,5.02),1):
        for i,x in enumerate((-10,-3.3,3.3,10),1):
            oriented_cube(f"ChiPsi_{tag}_SideWindow_F{floor}_{i}_Glass",x,side_y,z,1.25,.06,1.60,glass)
            for dx in (-.70,.70):
                oriented_cube(f"ChiPsi_{tag}_SideWindow_F{floor}_{i}_Jamb_{dx:+.1f}",x+dx,side_y-.04,z,.10,.10,1.8,white)
            oriented_cube(f"ChiPsi_{tag}_SideWindow_F{floor}_{i}_Sill",x,side_y-.05,z-.85,1.5,.12,.12,stone)
for xside,tag in ((half_x+.03,"East"),(-half_x-.03,"West")):
    for floor,z in enumerate((1.75,5.05),1):
        for j,y in enumerate((-6,0,6),1):
            # end wall windows use dimensions swapped in the long/depth axes.
            oriented_cube(f"ChiPsi_{tag}_EndWindow_F{floor}_{j}_Glass",xside,y,z,.06,1.35,1.65,glass)
            oriented_cube(f"ChiPsi_{tag}_EndWindow_F{floor}_{j}_Header",xside-.06,y,z+.88,.12,1.60,.12,white)
            oriented_cube(f"ChiPsi_{tag}_EndWindow_F{floor}_{j}_Sill",xside-.06,y,z-.88,.12,1.65,.14,stone)

# Schematic only: floor plates and common-room partitions; no room plan source
# was located, so these are labeled cues, not claims about actual layout.
for z in (3.35,6.65):
    oriented_cube(f"ChiPsi_SCHEMATIC_FloorPlate_{z:.2f}",0,0,z,length-.8,depth-.8,.16,floor_mat,schem)
for y in (-5.1,0,5.1):
    oriented_cube(f"ChiPsi_SCHEMATIC_Partition_{y:+.1f}",0,y,4.8,length-2,.10,2.7,interior,schem)
oriented_cube("ChiPsi_SCHEMATIC_CommonRoom_Table",-2.0,0,4.05,3.3,1.3,.12,wood,schem)
for x in (-3.1,-.9):
    for y in (-.8,.8): oriented_cube(f"ChiPsi_SCHEMATIC_Chair_{x}_{y}",x,y,3.75,.45,.45,.48,wood,schem)
oriented_cube("ChiPsi_SCHEMATIC_DiningCounter",5.5,0,4.15,5.0,.65,.25,stone,schem)
for ob in schem.objects:
    ob["representation"]="Schematic interior cue; no georeferenced interior plan source found."

# Small porch lanterns flank the entry.
for sx in (-1.45,1.45):
    oriented_cube(f"ChiPsi_Entry_Lantern_{sx:+.1f}",doorx+sx,front_y-.24,2.75,.16,.14,.42,metal)

# Render camera: normal to the broad entrance facade, slightly above ground.
def aim(obj, target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
front_center=Vector((0,-half_y,5.4)); fworld=Vector((front_center.x*axis_x.x+front_center.y*axis_y.x,front_center.x*axis_x.y+front_center.y*axis_y.y,front_center.z))
outdir=Vector((-axis_y.x,-axis_y.y,0))
cam_data=bpy.data.cameras.new("ChiPsi_EvidenceCamera"); cam=bpy.data.objects.new("ChiPsi_EvidenceCamera",cam_data); preview.objects.link(cam)
cam.location=fworld+outdir*48+Vector((0,0,3)); aim(cam,fworld+Vector((0,0,1.6))); cam_data.type="ORTHO"; cam_data.ortho_scale=32; scene.camera=cam
ld=bpy.data.lights.new("ChiPsi_Softbox_Key","AREA"); lo=bpy.data.objects.new("ChiPsi_Softbox_Key",ld); preview.objects.link(lo); lo.location=fworld+outdir*22+Vector((-10,-12,21)); ld.energy=3600; ld.shape="DISK"; ld.size=18; aim(lo,fworld)
ld2=bpy.data.lights.new("ChiPsi_Fill","AREA"); lo2=bpy.data.objects.new("ChiPsi_Fill",ld2); preview.objects.link(lo2); lo2.location=fworld+outdir*8+Vector((18,10,11)); ld2.energy=1200; ld2.size=16; aim(lo2,fworld)
# The render ground is isolated from the exported building collection.
groundmat=mat("ChiPsi_Preview_Ground",(.15,.23,.13),.95)
ground=oriented_cube("ChiPsi_Preview_Ground_Plane",0,0,-.16,80,80,.18,groundmat,preview)
scene.view_settings.view_transform="AgX"
scene.world.use_nodes=True
bg=next(n for n in scene.world.node_tree.nodes if n.type=="BACKGROUND"); bg.inputs["Color"].default_value=(.35,.45,.58,1); bg.inputs["Strength"].default_value=.4

# Metadata, orthographic/top inspection render, and portable save.
scene["building_id"]="chi_psi"
scene["source_feature_id"]=748
scene["source_address"]="950 David Ross Rd"
scene["source_identity_note"]="Chi Psi official lodge opening/newsletter evidence; Purdue FID 748 at 950 David Ross is labeled Zeta Psi but its ring is a poor footprint fit. Structural shell follows Indiana 2018 LiDAR OBJECTID 409718. See audit/chi_psi/evidence.md."
scene["placement_origin_xy_m"]=[origin[0],origin[1]]
scene["structural_footprint_area_m2"]=footprint_area_local
scene["structural_footprint_source"]="Indiana 2018 Building Footprints objectid 409718"
scene["interior_note"]="Only named schematic cues; no measured interior plan source found."
bpy.context.view_layer.objects.active=None
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
scene.render.filepath=str(AUDIT/"chi_psi_front_render.png")
bpy.ops.render.render(write_still=True)

summary={"asset":str(OUT.relative_to(ROOT)).replace("\\","/"),"scene":scene.name,"collection":coll.name,"placement_origin_xy_m":list(origin),"site_reference_purdue_gis_fid":748,"site_reference_gis_label":attrs["BUILDING_N"],"site_address":attrs["ADDRESS"],"structural_footprint_source":"Indiana Building Footprints 2018 objectid 409718","structural_footprint_area_m2":footprint_area_local,"footprint_dimensions_m":[length,depth],"export_object_count_recursive":len(coll.all_objects),"direct_asset_collection_object_count":len(coll.objects),"export_mesh_count_recursive":sum(1 for o in coll.all_objects if o.type=="MESH"),"schematic_interior_object_count":len(schem.objects),"preview_only_object_count":len(preview.objects),"render":str((AUDIT/"chi_psi_front_render.png").relative_to(ROOT)).replace("\\","/")}
(AUDIT/"build_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
print(json.dumps(summary,indent=2))
