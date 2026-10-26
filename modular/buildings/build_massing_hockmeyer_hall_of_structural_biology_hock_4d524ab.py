"""Rebuild Hockmeyer Hall of Structural Biology from Purdue GIS and photo evidence.

The GIS ground footprint is preserved in campus coordinates. Three occupied floors
are supported by Purdue emergency records; floor-to-floor dimensions, penthouse
height and placement are visual massing estimates, not surveyed measurements.
"""
import bpy, json, math, os
from mathutils import Vector

ASSET_ID="massing_hockmeyer_hall_of_structural_biology_hock_4d524ab"
ASSET_NAME="Hockmeyer Hall of Structural Biology (HOCK)"
COLL_NAME="Asset_"+ASSET_ID
SCENE_NAME="Building_"+ASSET_ID
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
AUDIT=os.path.join(ROOT,"audit",ASSET_ID)
SOURCE=os.path.join(AUDIT,"sources","purdue_building_shapes_hock.json")
ASSET=os.path.join(os.path.dirname(__file__),ASSET_ID+".blend")
RENDER=os.path.join(AUDIT,"renders")
PREVIEW=os.path.join(RENDER,"hockmeyer_exterior_oblique.png")
COURT=os.path.join(RENDER,"hockmeyer_courtyard_entry.png")
PLAN=os.path.join(RENDER,"hockmeyer_roof_plan.png")
MAIN_H=11.4


def make_mat(name,color,rough=.8,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value=(*color,1); p.inputs["Roughness"].default_value=rough; p.inputs["Metallic"].default_value=metal
    return m

def make_mesh(name,verts,faces,collection,mats,face_mats=None):
    me=bpy.data.meshes.new(name+"_Mesh"); me.from_pydata(verts,[],faces)
    for m in mats: me.materials.append(m)
    me.update()
    ob=bpy.data.objects.new(name,me); collection.objects.link(ob)
    if face_mats:
        for poly,index in zip(me.polygons,face_mats): poly.material_index=index
    return ob

def append_box(v,f,center,axes,dims):
    c=Vector(center); xa,ya,za=axes; hx,hy,hz=(d*.5 for d in dims); base=len(v)
    for sx,sy,sz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]:
        v.append(tuple(c+xa*(sx*hx)+ya*(sy*hy)+za*(sz*hz)))
    f.extend([[base+i for i in q] for q in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]])

def append_axis_box(v,f,center,dims):
    append_box(v,f,center,(Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))),dims)

def area_centroid(poly):
    cross=[poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly))]
    a=sum(cross)*.5
    return (sum((poly[i][0]+poly[(i+1)%len(poly)][0])*cross[i] for i in range(len(poly)))/(6*a),sum((poly[i][1]+poly[(i+1)%len(poly)][1])*cross[i] for i in range(len(poly)))/(6*a))
def inside(pt,poly):
    x,y=pt; c=False
    for i,a in enumerate(poly):
        b=poly[(i+1)%len(poly)]
        if ((a[1]>y)!=(b[1]>y)) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:c=not c
    return c
def aim(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()


def build():
    os.makedirs(RENDER,exist_ok=True)
    with open(SOURCE,encoding="utf-8-sig") as f: feature=json.load(f)["features"][0]
    attrs=feature["attributes"]
    assert attrs.get("FID")==669 and attrs.get("BLDG_ABBR")=="HOCK" and "Hockmeyer" in attrs.get("BUILDING_N","")
    raw=feature["geometry"]["rings"][0]
    ring=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in raw]
    if ring and math.dist(ring[0],ring[-1])<1e-8: ring.pop()
    assert len(ring)==58, f"Unexpected HOCK GIS ring count: {len(ring)}"
    signed=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))*.5
    if signed<0: ring.reverse(); signed=-signed

    # Fresh scene: never open or overwrite the 5.2 source file through Blender 4.5.
    scene=bpy.context.scene; scene.name=SCENE_NAME; scene["building_id"]=ASSET_ID
    scene["expected_scene_name"]=SCENE_NAME
    scene["scene_name_compatibility_note"]="Blender 4.5 truncates this expected name; preserve the full ID here and keep the exported collection name exact."
    for other in list(bpy.data.scenes):
        if other != scene: bpy.data.scenes.remove(other)
    for ob in list(scene.objects): bpy.data.objects.remove(ob,do_unlink=True)
    for child in list(scene.collection.children): scene.collection.children.unlink(child)
    coll=bpy.data.collections.new(COLL_NAME); scene.collection.children.link(coll)
    rig=bpy.data.collections.new("Render_Setup_HOCK"); scene.collection.children.link(rig)
    brick=make_mat("HOCK | red-brown brick based on Purdue 2009 exterior",(.43,.16,.105),.86)
    roof=make_mat("HOCK | flat roof membrane estimate",(.26,.29,.30),.9)
    glass=make_mat("HOCK | blue-green glazing based on Purdue photo",(.035,.20,.25),.24,.10)
    mullion=make_mat("HOCK | pale aluminum curtainwall frames",(.72,.75,.73),.42,.42)
    metal=make_mat("HOCK | pale opaque upper facade panels from Purdue photo",(.76,.79,.80),.72,.08)
    panel_joint=make_mat("HOCK | pale facade panel joints",(.88,.90,.90),.5,.12)
    trim=make_mat("HOCK | light limestone and entry trim",(.69,.65,.56),.75)

    n=len(ring); verts=[(x,y,z) for z in (0.0,MAIN_H) for x,y in ring]
    faces=[tuple(reversed(range(n)))]
    for i in range(n):
        j=(i+1)%n; faces.append((i,j,n+j,n+i))
    faces.append(tuple(range(n,2*n)))
    face_mats=[0]*(n+2); face_mats[-1]=1
    shell=make_mesh(ASSET_NAME,verts,faces,coll,[brick,roof],face_mats)

    # Identify GIS re-entrant corners and treat the associated interior-facing
    # wall runs as the photo-backed courtyard glazing zone. This is a broad
    # architectural cue, not a compass registration of the source photograph.
    concave=[False]*n
    for i,p in enumerate(ring):
        prev=ring[(i-1)%n]; nxt=ring[(i+1)%n]
        ax,ay=p[0]-prev[0],p[1]-prev[1]; bx,by=nxt[0]-p[0],nxt[1]-p[1]
        concave[i]=(ax*by-ay*bx)<-1.0
    edges=[]
    for i,a in enumerate(ring):
        b=ring[(i+1)%n]; dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
        tangent=Vector((dx/length,dy/length,0)) if length else Vector((1,0,0))
        normal=Vector((tangent.y,-tangent.x,0))
        # Expand the concavity cue by one ring segment on either side. The
        # courtyard photo is not georeferenced; these are facade candidates,
        # not compass-registered claims about the photographed wall.
        court=any(concave[(i+d)%n] for d in (-1,0,1,2))
        edges.append({"i":i,"a":a,"b":b,"length":length,"tangent":tangent,"normal":normal,"mid":((a[0]+b[0])*.5,(a[1]+b[1])*.5),"court":court})
    court_edges=[e for e in edges if e["court"] and e["length"]>2.0]
    if not court_edges: court_edges=[max(edges,key=lambda e:e["length"])]
    entry=max(court_edges,key=lambda e:e["length"])
    # Two broad opaque upper facade runs represent the pale panel volume in
    # Purdue's official exterior photo. Their exact GIS registration is unknown.
    cladding_edges={e["i"] for e in sorted(court_edges,key=lambda e:e["length"],reverse=True)[:2]}

    frame_v=[]; frame_f=[]; glass_v=[]; glass_f=[]; trim_v=[]; trim_f=[]
    cladding_v=[]; cladding_f=[]; joints_v=[]; joints_f=[]
    main_floor=MAIN_H/3.0
    for e in edges:
        length=e["length"]
        if length<2.0: continue
        a=e["a"]; b=e["b"]; t=e["tangent"]; norm=e["normal"]; axes=(t,norm,Vector((0,0,1)))
        if e["court"]:
            # Extensive multi-storey curtainwall. Opaque upper panels interrupt
            # two runs, matching the large pale-cladding volume in the photo.
            count=max(1,math.ceil(length/4.0)); bay=length/count*.94
            glazed_top=MAIN_H*.68 if e["i"] in cladding_edges else MAIN_H*.94
            for k in range(count):
                u=(k+.5)/count; p=Vector((a[0],a[1],0)).lerp(Vector((b[0],b[1],0)),u)
                center=p+norm*.16
                append_box(glass_v,glass_f,(center.x,center.y,glazed_top*.5),axes,(bay,.09,glazed_top*.94))
                # Curtainwall vertical mullions and floor rails.
                for side in (-.5,0,.5):
                    q=center+t*(side*bay*.86)+norm*.10
                    append_box(frame_v,frame_f,(q.x,q.y,glazed_top*.5),axes,(.095,.12,glazed_top*.94))
                for z in (main_floor,2*main_floor):
                    if z<glazed_top:
                        q=p+norm*.24
                        append_box(frame_v,frame_f,(q.x,q.y,z),axes,(bay,.13,.12))
            if e["i"] in cladding_edges:
                panel_bottom=MAIN_H*.69; panel_top=MAIN_H-.12
                panel_count=max(1,math.ceil(length/4.0)); panel_w=length/panel_count
                for k in range(panel_count):
                    u=(k+.5)/panel_count; q=Vector((a[0],a[1],0)).lerp(Vector((b[0],b[1],0)),u)+norm*.17
                    append_box(cladding_v,cladding_f,(q.x,q.y,(panel_bottom+panel_top)*.5),axes,(panel_w*.97,.13,panel_top-panel_bottom))
                    if k:
                        seam=Vector((a[0],a[1],0)).lerp(Vector((b[0],b[1],0)),k/panel_count)+norm*.255
                        append_box(joints_v,joints_f,(seam.x,seam.y,(panel_bottom+panel_top)*.5),axes,(.045,.055,panel_top-panel_bottom))
        else:
            # The GIS ring is densely sampled along curved walls, so place a
            # compact window on each meaningful straight segment instead of
            # spacing bays only on the few long polygon edges.
            if length<2.0: continue
            count=max(1,math.ceil(length/7.0)); bay=min(2.4,length/(count+1)*.68)
            for k in range(count):
                u=(k+1)/(count+1); p=Vector((a[0],a[1],0)).lerp(Vector((b[0],b[1],0)),u)
                for floor in range(3):
                    z=floor*main_floor+.48+1.48/2
                    fc=p+norm*.14; gc=p+norm*.24
                    append_box(frame_v,frame_f,(fc.x,fc.y,z),axes,(bay+.22,.16,1.66))
                    append_box(glass_v,glass_f,(gc.x,gc.y,z),axes,(bay,.08,1.46))
                    append_box(frame_v,frame_f,((p+norm*.25).x,(p+norm*.25).y,z),axes,(.08,.11,1.42))
        # Light horizontal bands keep the red-brick elevations at the 3-floor rhythm.
        if not e["court"] and length>8:
            for z in (main_floor,2*main_floor):
                p=Vector((e["mid"][0],e["mid"][1],z))+norm*.12
                append_box(trim_v,trim_f,(p.x,p.y,p.z),axes,(length,.14,.12))

    if frame_f: make_mesh("HOCK | mullions and brick window frames",frame_v,frame_f,coll,[mullion])
    if glass_f: make_mesh("HOCK | courtyard curtainwall and window glazing",glass_v,glass_f,coll,[glass])
    if trim_f: make_mesh("HOCK | estimated floor bands",trim_v,trim_f,coll,[trim])
    if cladding_f: make_mesh("HOCK | pale opaque upper facade panels",cladding_v,cladding_f,coll,[metal])
    if joints_f: make_mesh("HOCK | pale facade panel joints",joints_v,joints_f,coll,[panel_joint])

    # Render-only cameras and lights remain outside the exported building collection.
    scene.render.engine="BLENDER_EEVEE_NEXT"
    scene.render.resolution_percentage=100; scene.render.image_settings.file_format="PNG"; scene.render.film_transparent=False
    scene.view_settings.view_transform="AgX"
    world=bpy.data.worlds.new("HOCK review world"); scene.world=world; world.use_nodes=True
    world.node_tree.nodes["Background"].inputs["Color"].default_value=(.67,.73,.79,1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value=.65
    center=Vector((sum(x for x,y in ring)/n,sum(y for x,y in ring)/n,6.6))
    def rig(obj): scene.collection.children.get("Render_Setup_HOCK").objects.link(obj); return obj
    cd=bpy.data.cameras.new("HOCK review camera"); cam=rig(bpy.data.objects.new("HOCK review camera",cd)); cd.type="ORTHO"; scene.camera=cam
    ld=bpy.data.lights.new("HOCK review key","AREA"); ld.energy=6800; ld.shape="DISK"; ld.size=45
    light=rig(bpy.data.objects.new("HOCK review key",ld))
    def render(path,location,target,scale,res=(1400,1000)):
        cam.location=location; cd.ortho_scale=scale; aim(cam,target)
        light.location=(center.x-40,center.y-50,55); aim(light,target)
        scene.render.resolution_x=res[0]; scene.render.resolution_y=res[1]; scene.render.filepath=path
        bpy.ops.render.render(write_still=True)
    render(PREVIEW,center+Vector((-75,-82,38)),center,112)
    # Representative courtyard view; source images are not geo-registered.
    eye=center+Vector((-75,-82,35))
    render(COURT,eye,center,105,(1400,900))
    render(PLAN,(center.x,center.y,150),(center.x,center.y,0),78,(1100,1100))
    cam.location=center+Vector((-75,-82,38)); aim(cam,center); cd.ortho_scale=112
    scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.filepath=PREVIEW
    bpy.ops.wm.save_as_mainfile(filepath=ASSET)
    print(json.dumps({"asset":ASSET,"scene":scene.name,"collection":coll.name,"asset_object_count":len(coll.objects),"asset_object_names":[o.name for o in coll.objects],"gis_feature":attrs.get("FID"),"ring_vertices":n,"ring_area_m2_local_approx":round(signed,3),"main_occupied_floors":3,"main_wall_height_estimate_m":MAIN_H,"total_height_estimate_m":MAIN_H,"source_height_attribute":{"NUM_LEVELS":attrs.get("NUM_LEVELS"),"Extrution_raw":attrs.get("Extrution"),"units":"undocumented; not used"},"bounds_xy_m":[[min(x for x,y in ring),max(x for x,y in ring)],[min(y for x,y in ring),max(y for x,y in ring)]],"cladding_edge_indices_estimate":sorted(cladding_edges)},indent=2))

build()

