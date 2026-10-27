"""Build Delta Chi's local asset from verified GIS and 501 Russell photos."""
import bpy, json, math, os
from mathutils import Vector

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..")); AUDIT=os.path.join(ROOT,"audit","delta_chi")
GIS_FILE=os.path.join(AUDIT,"indiana_building_footprint_objectid_409891.json")
ASSET_FILE=os.path.join(ROOT,"modular","buildings","delta_chi.blend"); EVIDENCE_FILE=os.path.join(AUDIT,"evidence.json")
LAT0,LON0=40.4274,-86.9137; LAT_M,LON_M=111040.0,84810.60416539927
BUILDING_ID="delta_chi"; COLLECTION_NAME="Asset_delta_chi"
with open(GIS_FILE,encoding="utf-8-sig") as f: gis=json.load(f)
feature=gis["features"][0]; assert feature["attributes"]["objectid"]==409891
ring=feature["geometry"]["rings"][0]
projected=[((lon-LON0)*LON_M,(lat-LAT0)*LAT_M) for lon,lat in ring[:-1]]

def polygon_centroid(points):
    a2=sx=sy=0.0
    for i,(x1,y1) in enumerate(points):
        x2,y2=points[(i+1)%len(points)]; c=x1*y2-x2*y1; a2+=c; sx+=(x1+x2)*c; sy+=(y1+y2)*c
    return (sx/(3*a2),sy/(3*a2)),abs(a2/2)
origin,footprint_area=polygon_centroid(projected)
outline=[(x-origin[0],y-origin[1]) for x,y in projected]
cx=sum(x for x,y in outline)/len(outline); cy=sum(y for x,y in outline)/len(outline)

bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.meshes,bpy.data.curves,bpy.data.materials,bpy.data.cameras,bpy.data.lights):
    for block in list(datablocks):
        if block.users==0: datablocks.remove(block)
asset=bpy.data.collections.new(COLLECTION_NAME); bpy.context.scene.collection.children.link(asset)
preview=bpy.data.collections.new("Preview_Only"); bpy.context.scene.collection.children.link(preview)
asset["building_id"]=BUILDING_ID; asset["local_coordinates"]=True
asset["source_geometry_provider"]="Indiana GIS Data Hub, Indiana Building Footprints 2016-2020"
asset["source_feature_id"]=409891; asset["source_lidar_year"]="2018"
asset["placement_origin_xy_m"]=[origin[0],origin[1]]; asset["footprint_area_estimate_m2"]=footprint_area
asset["source_match_status"]="Current official chapter address 501 N Russell; county parcel and Indiana building-footprint geometry cross-matched"
asset["interior_status"]="schematic; no registered floor plan located"

def mat(name,base,rough=.75,texture="noise",scale=5,color2=None,mortar=(.3,.22,.16,1)):
    m=bpy.data.materials.new(name); m.diffuse_color=base; m.use_nodes=True; n=m.node_tree.nodes; l=m.node_tree.links; bs=n.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=base; bs.inputs["Roughness"].default_value=rough
    tex=n.new("ShaderNodeTexBrick" if texture=="brick" else "ShaderNodeTexNoise")
    if texture=="brick":
        tex.inputs["Color1"].default_value=base; tex.inputs["Color2"].default_value=color2 or (.40,.10,.055,1)
        tex.inputs["Mortar"].default_value=mortar; tex.inputs["Scale"].default_value=1.0; tex.inputs["Mortar Size"].default_value=.008
        tex.inputs["Mortar Smooth"].default_value=.04; tex.inputs["Brick Width"].default_value=.20; tex.inputs["Row Height"].default_value=.07
        tc=n.new("ShaderNodeTexCoord"); l.new(tc.outputs["UV"],tex.inputs["Vector"])
        l.new(tex.outputs["Color"],bs.inputs["Base Color"])
    else:
        tex.inputs["Scale"].default_value=scale; tex.inputs["Detail"].default_value=3.0
        ramp=n.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=tuple(max(0,c*.72) for c in base[:3])+(1,)
        ramp.color_ramp.elements[1].position=.82; ramp.color_ramp.elements[1].color=tuple(min(1,c*1.16) for c in base[:3])+(1,)
        l.new(tex.outputs["Fac"],ramp.inputs["Fac"]); l.new(ramp.outputs["Color"],bs.inputs["Base Color"])
    bump=n.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=.11; bump.inputs["Distance"].default_value=.035
    l.new(tex.outputs["Color"] if texture=="brick" else tex.outputs["Fac"],bump.inputs["Height"]); l.new(bump.outputs["Normal"],bs.inputs["Normal"])
    return m
brick=mat("DCI red brick",(.60,.205,.105,1),.9,"brick",30,(.47,.105,.055,1),(.43,.34,.26,1))
brick_dark=mat("DCI foundation brick",(.34,.115,.065,1),.92,"brick",30,(.29,.08,.05,1),(.32,.25,.20,1))
roofmat=mat("DCI charcoal asphalt shingles",(.16,.18,.19,1),.92,"noise",42)
trim=mat("DCI painted white trim",(.84,.82,.74,1),.68,"noise",18)
glass=mat("DCI blue gray window glass",(.105,.19,.23,1),.22,"noise",3)
stone=mat("DCI warm limestone",(.59,.55,.46,1),.85,"noise",26)
wood=mat("DCI interior oak",(.40,.24,.11,1),.78,"noise",8)
floor_mat=mat("DCI interior carpet",(.16,.18,.20,1),.95,"noise",55)
green=mat("DCI planted evergreen",(.08,.19,.12,1),.92,"noise",12)
leaf=mat("DCI leafy shrub",(.12,.27,.12,1),.9,"noise",17)
soil=mat("DCI dark mulch",(.12,.075,.045,1),.98,"noise",36)
interior_wall=mat("DCI schematic interior wall",(.77,.74,.66,1),.9,"noise",20)
furn=mat("DCI furniture dark wood",(.19,.12,.075,1),.72,"noise",10)

def mesh_object(name,verts,faces,material,collection=asset):
    me=bpy.data.meshes.new(name+"_mesh"); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    if name in {"DCI_2018_GIS_building_footprint_shell","DCI_stone_foundation_course"}:
        uv=me.uv_layers.new(name="UVMap"); n=len(outline)
        zheight=max(v[2] for v in verts)-min(v[2] for v in verts)
        for poly in me.polygons:
            for li in poly.loop_indices:
                vi=me.loops[li].vertex_index
                if poly.index>=2:
                    edge=poly.index-2; p=outline[edge]; q=outline[(edge+1)%n]; length=math.hypot(q[0]-p[0],q[1]-p[1])
                    if vi==edge: coord=(0.0,0.0)
                    elif vi==(edge+1)%n: coord=(length,0.0)
                    elif vi==(edge+1)%n+n: coord=(length,zheight)
                    else: coord=(0.0,zheight)
                else:
                    v=me.vertices[vi].co; coord=(float(v.x),float(v.y))
                uv.data[li].uv=coord
    ob=bpy.data.objects.new(name,me); collection.objects.link(ob); return ob
def cube(name,loc,dims,material,angle=0,collection=asset):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); ob=bpy.context.object; ob.name=name; ob.dimensions=dims; ob.rotation_euler[2]=angle
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    collection.objects.link(ob); ob.data.materials.append(material); return ob
def uv_sphere(name,loc,scale,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=loc); ob=bpy.context.object; ob.name=name; ob.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    asset.objects.link(ob); ob.data.materials.append(material); return ob
def extruded_polygon(name,points,z0,z1,material):
    n=len(points); verts=[(x,y,z0) for x,y in points]+[(x,y,z1) for x,y in points]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh_object(name,verts,faces,material)
def unit(v):
    l=math.hypot(*v); return (v[0]/l,v[1]/l) if l else (0,1)

# Footprint comes from state building-footprint data, not parcel boundaries.
shell=extruded_polygon("DCI_2018_GIS_building_footprint_shell",outline,.25,7.35,brick)
extruded_polygon("DCI_stone_foundation_course",outline,.25,1.05,brick_dark)
# Estimated two-story eaves and shallow hipped roof, interpreted from 2025 photo.
for i,(p,q) in enumerate(zip(outline,outline[1:]+outline[:1])):
    t=unit((q[0]-p[0],q[1]-p[1])); length=math.hypot(q[0]-p[0],q[1]-p[1])
    if length>1.1:
        mid=((p[0]+q[0])/2,(p[1]+q[1])/2)
        cube(f"DCI_white_cornice_{i:02d}",(mid[0],mid[1],7.28),(length+.12,.32,.28),trim,math.atan2(t[1],t[0]))
top=[(cx+(x-cx)*.30,cy+(y-cy)*.30) for x,y in outline]; n=len(outline)
verts=[(x,y,7.37) for x,y in outline]+[(x,y,9.25) for x,y in top]
roof=mesh_object("DCI_hipped_shingle_roof_estimated",verts,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]+[tuple(range(n,2*n))],roofmat)

# East side faces Russell Street; choose the longest near-east vertical edge for entry.
maxx=max(x for x,y in outline); front_edges=[]
for p,q in zip(outline,outline[1:]+outline[:1]):
    if abs(p[0]-q[0])<.25 and max(p[0],q[0])>maxx-.35: front_edges.append((p,q))
if not front_edges: front_edges=sorted(zip(outline,outline[1:]+outline[:1]),key=lambda pq:(pq[0][0]+pq[1][0])/2,reverse=True)[:1]
p,q=max(front_edges,key=lambda pq:math.hypot(pq[1][0]-pq[0][0],pq[1][1]-pq[0][1]))
tangent=unit((q[0]-p[0],q[1]-p[1])); normal=unit((tangent[1],-tangent[0])); angle=math.atan2(tangent[1],tangent[0])
# Polygon rings in this source are clockwise, so the left normal faces out.
normal=(-normal[0],-normal[1])
entry_edge_index=outline.index(p)
entry_tangent=tangent; entry_normal=normal; entry_angle=angle
entry_span=math.hypot(q[0]-p[0],q[1]-p[1])
entry=((p[0]+q[0])/2,(p[1]+q[1])/2)
for side in (-1,1):
    px=entry[0]+tangent[0]*side*.94+normal[0]*.32
    py=entry[1]+tangent[1]*side*.94+normal[1]*.32
    cube(f"DCI_entry_white_pilaster_{side}",(px,py,2.35),(.22,.48,4.1),trim,angle)
cube("DCI_entry_white_lintel",(entry[0]+normal[0]*.32,entry[1]+normal[1]*.32,4.30),(2.12,.48,.24),trim,angle)
cube("DCI_entry_small_white_canopy",(entry[0]+normal[0]*.85,entry[1]+normal[1]*.85,4.55),(2.65,1.35,.20),trim,angle)
cube("DCI_recessed_front_door",(entry[0]+normal[0]*.56,entry[1]+normal[1]*.56,2.22),(1.38,.09,3.68),furn,angle)
cube("DCI_entry_door_glass_lite",(entry[0]+normal[0]*.63,entry[1]+normal[1]*.63,2.75),(.92,.055,2.2),glass,angle)
cube("DCI_entry_transom",(entry[0]+normal[0]*.62,entry[1]+normal[1]*.62,4.18),(1.72,.14,.30),glass,angle)
cube("DCI_entry_stone_landing",(entry[0]+normal[0]*1.3,entry[1]+normal[1]*1.3,.33),(5.4,2.7,.25),stone,angle)
for i in range(3): cube(f"DCI_front_step_{i}",(entry[0]+normal[0]*(2.5+i*.55),entry[1]+normal[1]*(2.5+i*.55),.16-i*.025),(5,.54,.16),stone,angle)

window_count=0
for edge_index,(p,q) in enumerate(zip(outline,outline[1:]+outline[:1])):
    dx,dy=q[0]-p[0],q[1]-p[1]; length=math.hypot(dx,dy)
    if length<4: continue
    tangent=unit((dx,dy)); normal=unit((tangent[1],-tangent[0]))
    mx,my=(p[0]+q[0])/2,(p[1]+q[1])/2
    if normal[0]*(mx-cx)+normal[1]*(my-cy)<0: normal=(-normal[0],-normal[1])
    angle=math.atan2(tangent[1],tangent[0]); nwin=max(1,int(length/3.4))
    for level,z in enumerate((2.25,5.45)):
        for j in range(nwin):
            u=(j+1)/(nwin+1); x,y=p[0]+u*dx+normal[0]*.07,p[1]+u*dy+normal[1]*.07
            if edge_index==entry_edge_index and math.hypot(x-entry[0],y-entry[1])<3.2: continue
            w,h=1.18,1.68
            cube(f"DCI_window_glass_{window_count}",(x,y,z),(w-.16,.045,h-.20),glass,angle)
            for sx in (-1,1): cube(f"DCI_window_jamb_{window_count}_{sx}",(x+sx*w/2,y,z),(.105,.19,h+.12),trim,angle)
            for sz in (-1,1): cube(f"DCI_window_head_sill_{window_count}_{sz}",(x,y,z+sz*h/2),(w+.10,.20,.105),trim,angle)
            cube(f"DCI_window_center_mullion_{window_count}",(x,y-.03,z),(.075,.10,h-.15),trim,angle)
            cube(f"DCI_window_horizontal_muntin_{window_count}",(x,y-.045,z),(w-.18,.09,.075),trim,angle); window_count+=1

# Front dormers are estimated, and use the observed white trim and brick.
for i in range(3):
    u=(i+1)/4; span=min(20,entry_span)
    pos=(entry[0]+entry_tangent[0]*(u-.5)*span,entry[1]+entry_tangent[1]*(u-.5)*span)
    x,y=pos[0]+entry_normal[0]*.35,pos[1]+entry_normal[1]*.35
    cube(f"DCI_dormer_{i}_brick_face",(x,y,8.3),(2.15,.55,1.5),brick,entry_angle)
    cube(f"DCI_dormer_{i}_window",(x+entry_normal[0]*.31,y+entry_normal[1]*.31,8.28),(1.15,.06,1),glass,entry_angle)
    cube(f"DCI_dormer_{i}_white_trim",(x+entry_normal[0]*.35,y+entry_normal[1]*.35,8.87),(1.4,.11,.12),trim,entry_angle)
    cube(f"DCI_dormer_{i}_roof_cap",(x,y,9.08),(2.45,.9,.22),roofmat,entry_angle)

# Schematic interior based on property-gallery room types; no measured plan.
for z,name,material in ((.45,"first",stone),(4.,"second",floor_mat),(7.5,"attic",floor_mat)):
    extruded_polygon(f"DCI_schematic_{name}_floor",outline,z,z+.10,material)
xmin,xmax=min(x for x,y in outline)+2,max(x for x,y in outline)-2
ymin,ymax=min(y for x,y in outline)+2,max(y for x,y in outline)-2
cube("DCI_schematic_first_floor_cross_partition",(cx,ymin+(ymax-ymin)*.35,2.1),(xmax-xmin,.14,3.3),interior_wall)
cube("DCI_schematic_dining_study_partition",(cx,cy,2.1),(.14,xmax-xmin-4,3.3),interior_wall,math.pi/2)
cube("DCI_schematic_dining_table",(xmin+6,ymin+8,1.05),(5.5,1.7,.18),wood)
for i in range(6): cube(f"DCI_schematic_dining_chair_{i}",(xmin+4.1+i*.76,ymin+6.9,1.55),(.52,.52,.95),furn)
cube("DCI_schematic_study_table",(xmax-6,ymin+7,1.05),(5.8,1.2,.16),wood)
for i in range(4): cube(f"DCI_schematic_study_chair_{i}",(xmax-8.4+i*1.5,ymin+5.8,1.48),(.5,.5,.82),furn)
cube("DCI_schematic_lounge_sofa",(xmin+6,ymax-7,1.35),(3.2,.95,.9),furn)
cube("DCI_schematic_pool_table",(xmax-7,ymax-8,1.2),(3.4,1.8,.8),green)
for i in range(6):
    bx=xmin+4+(i%3)*5.2; by=cy+4+(i//3)*7.5
    cube(f"DCI_schematic_bed_{i}",(bx,by,4.95),(2,2.8,.3),trim)
    cube(f"DCI_schematic_desk_{i}",(bx+1.75,by+.3,5.45),(1.5,.72,.78),wood)

# Photo-inspired garden beds; plant species and 2018 planting plan are unverified.
garden_center=(entry[0]+entry_normal[0]*3.2,entry[1]+entry_normal[1]*3.2)
for i in range(11):
    off=(i-5)*1.8; x=garden_center[0]+entry_tangent[0]*off; y=garden_center[1]+entry_tangent[1]*off
    cube(f"DCI_mulch_bed_{i}",(x,y,.06),(2.5,1.35,.12),soil,entry_angle)
    if i%3==0:
        for j in range(3):
            ox=(j-1)*.42; sx=x+entry_tangent[0]*ox; sy=y+entry_tangent[1]*ox
            uv_sphere(f"DCI_shrub_{i}_{j}",(sx,sy,.55),(.70,.46,.58),leaf)
    else:
        for j in range(4):
            ox=(j-1.5)*.16; gx=x+entry_tangent[0]*ox; gy=y+entry_tangent[1]*ox
            blade=cube(f"DCI_ornamental_grass_{i}_{j}",(gx,gy,.47),(.07,.07,.80),green,entry_angle)
            blade.rotation_euler[1]=(-.24 if j%2 else .24)
    if i in (2,5,8):
        for j in range(4):
            fx=x+entry_tangent[0]*(j-1.5)*.22; fy=y+entry_tangent[1]*(j-1.5)*.22
            uv_sphere(f"DCI_small_flowering_shrub_{i}_{j}",(fx,fy,.75),(.12,.12,.12),trim)
for side in (-1,1):
    tx=entry[0]+entry_normal[0]*3.8+entry_tangent[0]*side*3.7
    ty=entry[1]+entry_normal[1]*3.8+entry_tangent[1]*side*3.7
    bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=.78,radius2=.12,depth=2.8,location=(tx,ty,1.45))
    conifer=bpy.context.object; conifer.name=f"DCI_small_blue_spruce_{side}"
    for c in list(conifer.users_collection): c.objects.unlink(conifer)
    asset.objects.link(conifer); conifer.data.materials.append(green)

scene=bpy.context.scene; scene.render.engine="BLENDER_EEVEE"; scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"; scene.view_settings.view_transform="AgX"
scene.world.use_nodes=True
scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.53,.60,.69,1)
scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.6
sun_data=bpy.data.lights.new("DCI_sun","SUN"); sun_data.energy=2.0; sun_data.angle=.25
sun=bpy.data.objects.new("DCI_sun",sun_data); preview.objects.link(sun); sun.location=(15,-20,30); sun.rotation_euler=(Vector((cx,cy,4))-sun.location).to_track_quat("-Z","Y").to_euler()
for loc,energy,size in [((20,-25,40),5200,22),((-28,-6,24),2600,16)]:
    d=bpy.data.lights.new("DCI_softbox","AREA"); d.energy=energy; d.shape="DISK"; d.size=size; o=bpy.data.objects.new("DCI_softbox",d); preview.objects.link(o); o.location=loc; o.rotation_euler=(Vector((cx,cy,4))-o.location).to_track_quat("-Z","Y").to_euler()
def camera(name,loc,target,lens):
    d=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,d); preview.objects.link(o); o.location=loc; o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler(); d.lens=lens; return o
overview_loc=(cx+38,cy-52,28)
cam=camera("DCI_overview_camera",overview_loc,(cx,cy,4.5),52); scene.camera=cam
scene.render.filepath=os.path.join(AUDIT,"preview_overview.png"); bpy.ops.render.render(write_still=True)
cam.location=(entry[0]+entry_normal[0]*39,entry[1]+entry_normal[1]*39,7.0)
cam.rotation_euler=(Vector((entry[0],entry[1],4.4))-cam.location).to_track_quat("-Z","Y").to_euler(); cam.data.lens=48
scene.render.filepath=os.path.join(AUDIT,"preview_front_elevation.png"); bpy.ops.render.render(write_still=True)
old_hidden={o.name:o.hide_render for o in asset.all_objects}
for o in asset.all_objects:
    o.hide_render=not (o.name.startswith("DCI_schematic_") and "second_floor" not in o.name and "attic" not in o.name)
cam.location=(cx+23,cy-28,29); cam.rotation_euler=(Vector((cx,cy,1))-cam.location).to_track_quat("-Z","Y").to_euler(); cam.data.lens=38
scene.render.filepath=os.path.join(AUDIT,"preview_schematic_interior.png"); bpy.ops.render.render(write_still=True)
for o in asset.all_objects: o.hide_render=old_hidden[o.name]
cam.location=overview_loc; cam.rotation_euler=(Vector((cx,cy,4.5))-cam.location).to_track_quat("-Z","Y").to_euler(); cam.data.lens=52
scene.render.filepath=os.path.join(AUDIT,"preview_overview.png")
os.makedirs(os.path.dirname(ASSET_FILE),exist_ok=True); bpy.ops.wm.save_as_mainfile(filepath=ASSET_FILE)

evidence={
 "building_id":BUILDING_ID,"asset":"modular/buildings/delta_chi.blend","collection":COLLECTION_NAME,"retrieved_date":"2026-10-27","status":"built; pending independent review",
 "sources":[
  {"provider":"Delta Chi International Fraternity","url":"https://deltachi.org/chapter-directory/indiana/","use":"official Purdue chapter listing and 501 N Russell address"},
  {"provider":"Delta Chi Purdue chapter","url":"https://deltachipurdue.org/rush","use":"current address and 2026 house-tour schedule"},
  {"provider":"501 Russell property site","url":"https://501russell.com/gallery/","photo_url":"https://501russell.com/wp-content/uploads/2025/06/IMG_4032-scaled.jpeg","gallery_upload_date":"2025-06","photo_capture_date_exif":"2021-08-06","use":"exterior and interior reference photographs; image was not embedded in model"},
  {"provider":"Indiana GIS Data Hub","url":"https://gisdata.in.gov/server/rest/services/Hosted/Building_Footprints/FeatureServer/0","feature_id":409891,"source_date":"2018 lidar year","source_crs":"source EPSG:3857, requested EPSG:4326","use":"building shell footprint; not height"},
  {"provider":"Tippecanoe County GIS / Schneider Corp","url":"https://wfs.schneidercorp.com/arcgis/rest/services/TippecanoeCountyIN_WFS/MapServer/58","feature_id":"PIN 164018000124 / parcel 79-07-19-127-011.000-026","use":"address-parcel cross-check; parcel boundary is not the building wall"},
  {"provider":"Tippecanoe County GIS / Schneider Corp Finished SQFT","url":"https://wfs.schneidercorp.com/arcgis/rest/services/TippecanoeCountyIN_WFS/MapServer/79","feature_id":"PIN 164018000124","use":"assessor 1952 year built and 25,352 finished sq ft; not measured height"}],
 "placement":{"origin_xy_m_projected":list(origin),"formula":"X=(lon+86.9137)*84810.60416539927; Y=(lat-40.4274)*111040.0","origin_method":"area centroid of building-footprint objectid 409891 in project local metric frame"},
 "geometry":{"footprint_area_m2":footprint_area,"vertex_count":len(outline),"source_area_attribute":feature["attributes"]["SHAPE__Area"],"lidar_year":"2018","window_count_per_floor":window_count,"eaves_estimate_m":7.35,"roof_peak_estimate_m":9.25},
 "edits":["Built local-coordinate shell from Indiana 2018 footprint.","Added red brick procedural texture, white cornice and trim, double-hung windows, dormers and an estimated hipped roof from the 2025 property photograph.","Added a principal east-side porch/entry toward Russell Street; exact historic entrance position remains estimated.","Added a schematic multi-floor interior (bedrooms, dining/study, lounge/game room) based on gallery room types; no registered floor plan was found.","Added photo-inspired beds, shrubs and grasses; species and exact planting positions are unverified."],
 "uncertainties":["Delta Chi official and chapter sources identify 501 N Russell as current facility and schedule house tours; a May 2024 city record listed Alpha Tau Omega at the same address, indicating an occupancy/branding transition.","Indiana building footprint is from 2018; no current registered architectural drawing or current official building footprint was found.","The exterior reference photo is in the property-site gallery uploaded in June 2025 but its EXIF capture date is 2021-08-06, so post-2021 facade changes may be unshown.","Roof shape, height, storey count, dormers and entrance dimensions are photo-derived estimates; assessor square footage is not a height measurement.","Interior floor plan and room coordinates are schematic, not surveyed.","Property gallery photos are not georegistered to individual facades."],
 "evidence_files":["audit/delta_chi/indiana_building_footprint_objectid_409891.json","audit/delta_chi/tippecanoe_parcel_501_n_russell.json","audit/delta_chi/finished_sqft_501_russell.json","audit/delta_chi/501russell_gallery.html","audit/delta_chi/gallery_ref_61.jpeg","audit/delta_chi/gallery_ref_60.jpeg","audit/delta_chi/osm_geocode_501_russell.json","audit/delta_chi/preview_overview.png","audit/delta_chi/preview_schematic_interior.png"]}
with open(EVIDENCE_FILE,"w",encoding="utf-8") as f: json.dump(evidence,f,indent=2); f.write("\n")
print(json.dumps({"asset":ASSET_FILE,"origin":origin,"footprint_area_m2":footprint_area,"window_objects":window_count,"objects":len(asset.all_objects)},indent=2))
