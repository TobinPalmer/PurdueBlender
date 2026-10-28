import bpy, bmesh, json, math, os
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = r"C:\Users\Tobin\Documents\Blender\PurdueMap"
AUDIT = os.path.join(ROOT, "audit", "stewart_fid802")
ASSET = os.path.join(ROOT, "modular", "buildings", "massing_house_1089875810_8c9b95d.blend")
SOURCE = json.load(open(os.path.join(AUDIT, "sources", "purdue_gis_fid802_raw.json"), encoding="utf-8-sig"))
feature = SOURCE["features"][0]
ring_ll = feature["geometry"]["rings"][0]
if ring_ll[0] == ring_ll[-1]: ring_ll = ring_ll[:-1]
ring=[]
for lon,lat in ring_ll:
    x=(lon+86.9137)*111412.84*math.cos(math.radians(40.4274))
    y=(lat-40.4274)*111040.0
    ring.append((x,y))

SCENE_NAME="Building_massing_house_1089875810_8c9b95d"
COLLECTION_NAME="Asset_massing_house_1089875810_8c9b95d"
ROOT_OBJECT="House_1089875810"
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.data.scenes.get(SCENE_NAME) or bpy.context.scene
scene.name=SCENE_NAME
col=bpy.data.collections.get(COLLECTION_NAME)
if col is None:
    col=bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(col)
for obj in list(col.objects): bpy.data.objects.remove(obj,do_unlink=True)

def material(name,color,rough=.72,metal=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.use_nodes=True
    bsdf=next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value=(*color,1)
    bsdf.inputs["Roughness"].default_value=rough
    bsdf.inputs["Metallic"].default_value=metal
    return m

stone=material("Stewart | observed pale masonry study",(.68,.55,.38),.82)
trim=material("Stewart | pale stone trim",(.78,.67,.48),.77)
roofmat=material("Stewart | dark gray roof from exterior photo",(.12,.14,.16),.7)
glass=material("Stewart | dark glazing",(.035,.060,.075),.23,.08)
frame=material("Stewart | dark window and door frame",(.17,.19,.19),.62)
metal=material("Stewart | muted metal hardware",(.26,.29,.30),.35,.65)
floor_mat=material("Stewart | schematic interior warm floor",(.40,.27,.16),.82)
upper_floor_mat=material("Stewart | schematic upper floor",(.51,.38,.24),.82)
wall_inside=material("Stewart | schematic partition walls",(.86,.82,.72),.86)
furn_mat=material("Stewart | schematic furniture",(.37,.26,.17),.78)
bed_mat=material("Stewart | schematic bedding",(.76,.77,.72),.8)

class MeshBuild:
    def __init__(self,name,mats):
        self.name=name; self.mats=mats; self.v=[]; self.f=[]; self.mi=[]
    def face(self,pts,mi=0):
        s=len(self.v); self.v.extend([tuple(p) for p in pts]); self.f.append(tuple(range(s,s+len(pts)))); self.mi.append(mi)
    def quad(self,a,b,c,d,mi=0): self.face([a,b,c,d],mi)
    def box(self,center,axes,size,mi=0):
        c=Vector(center); axes=[Vector(a) for a in axes]; h=[x/2 for x in size]
        pts=[]
        for k in range(8):
            s=[1 if k&(1<<i) else -1 for i in range(3)]
            q=c+sum((axes[i]*h[i]*s[i] for i in range(3)),Vector((0,0,0)))
            pts.append(tuple(q))
        for ids in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(1,5,7,3),(3,7,6,2),(2,6,4,0)]: self.face([pts[i] for i in ids],mi)
    def simple_box(self,center,size,mi=0): self.box(center,[(1,0,0),(0,1,0),(0,0,1)],size,mi)
    def to_object(self,col,materials=None):
        mesh=bpy.data.meshes.new(self.name+"_mesh"); mesh.from_pydata(self.v,[],self.f); mesh.update()
        bm=bmesh.new(); bm.from_mesh(mesh)
        bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.0001)
        bm.to_mesh(mesh); bm.free(); mesh.update()
        for m in materials or self.mats: mesh.materials.append(m)
        for p,idx in zip(mesh.polygons,self.mi): p.material_index=idx
        obj=bpy.data.objects.new(self.name,mesh); col.objects.link(obj)
        return obj

def normalized(v):
    v=Vector(v)
    return v.normalized() if v.length else Vector((1,0,0))

cx=(min(x for x,y in ring)+max(x for x,y in ring))/2
cy=(min(y for x,y in ring)+max(y for x,y in ring))/2
xmin,xmax=min(x for x,y in ring),max(x for x,y in ring)
ymin,ymax=min(y for x,y in ring),max(y for x,y in ring)
width=xmax-xmin; length=ymax-ymin
wall_top=8.7  # estimated to represent three floors; not a measured elevation
floor_levels=[0.0,2.9,5.8,8.7]

# Main base walls: use each source polygon edge without changing the footprint.
shell=MeshBuild(ROOT_OBJECT,[stone,trim,glass,frame])
for i,p0 in enumerate(ring):
    p1=ring[(i+1)%len(ring)]
    for za,zb in zip(floor_levels[:-1],floor_levels[1:]):
        shell.quad((p0[0],p0[1],za),(p1[0],p1[1],za),(p1[0],p1[1],zb),(p0[0],p0[1],zb),0)

# Main gable-end stone infill and a simple longitudinal gable roof.
roof_eave=wall_top
roof_peak=12.15  # image-supported form with estimated height
over=.22
rx0=xmin-over; rx1=xmax+over; ry0=ymin-over; ry1=ymax+over
ridge_x=(xmin+xmax)/2
for yy in (ymin,ymax):
    shell.face([(xmin,yy,roof_eave),(xmax,yy,roof_eave),(ridge_x,yy,roof_peak)],0)

# Photo-confirmed tower-like end mass on the north/west portion. It is a
# best-fit qualitative mass, kept inside the GIS outline at ground level.
tower_cx=xmin+2.25; tower_cy=ymax-3.0; tower_w=3.2; tower_l=4.0
tx0=tower_cx-tower_w/2; tx1=tower_cx+tower_w/2
ty0=tower_cy-tower_l/2; ty1=tower_cy+tower_l/2
tower_eave=10.25; tower_peak=13.35
for a,b in [((tx0,ty0),(tx1,ty0)),((tx1,ty0),(tx1,ty1)),((tx1,ty1),(tx0,ty1)),((tx0,ty1),(tx0,ty0))]:
    shell.quad((a[0],a[1],wall_top),(b[0],b[1],wall_top),(b[0],b[1],tower_eave),(a[0],a[1],tower_eave),0)

# Main front arched glazing is directly visible; only its facade placement is
# estimated because the source photograph is not georeferenced.
west_edges=[]
for i,p0 in enumerate(ring):
    p1=ring[(i+1)%len(ring)]
    dx=p1[0]-p0[0]; dy=p1[1]-p0[1]; L=math.hypot(dx,dy)
    midx=(p0[0]+p1[0])/2
    if L>5.0 and abs(dx)<1.5 and midx< -103.0: west_edges.append((L,i,p0,p1))
west_edges.sort(reverse=True)
if west_edges:
    _,west_i,wp0,wp1=west_edges[0]
    tangent=normalized((wp1[0]-wp0[0],wp1[1]-wp0[1],0))
    normal=Vector((-tangent.y,tangent.x,0))
    mid=Vector(((wp0[0]+wp1[0])/2,(wp0[1]+wp1[1])/2,0))
    if normal.dot(mid-Vector((cx,cy,0)))<0: normal=-normal
    # Put arched door/glazing toward the southward end of the visible facade.
    edge_len=math.hypot(wp1[0]-wp0[0],wp1[1]-wp0[1])
    p0=Vector((wp0[0],wp0[1],0)); p1=Vector((wp1[0],wp1[1],0))
    if (p1-p0).dot(Vector((0,1,0)))<0: p0,p1=p1,p0
    entry_center=p0+(p1-p0)*.28
    entry_center.z=0
    entry_w=2.25; base=.25; spring=2.65; arch_r=entry_w/2
    def arch_poly(center,w,zbase,zspring,peak,offset):
        pts=[center+normal*offset+tangent*(-w/2)+Vector((0,0,zbase)),center+normal*offset+tangent*(w/2)+Vector((0,0,zbase)),center+normal*offset+tangent*(w/2)+Vector((0,0,zspring))]
        for j in range(1,13):
            a=math.pi*j/12
            pts.append(center+normal*offset+tangent*(arch_r*math.cos(a))+Vector((0,0,zspring+arch_r*math.sin(a))))
        return pts
    # Pale masonry arch surround and inset dark glazing.
    shell.face(arch_poly(entry_center,2.80,base,2.68,4.08,.055),1)
    shell.face(arch_poly(entry_center,2.38,base+.12,2.64,3.83,.10),2)
    # Dark frame bars and door division.
    shell.box(entry_center+normal*.14+tangent*0+Vector((0,0,1.50)),[tangent,normal,Vector((0,0,1))],(.055,.08,2.45),3)
    shell.box(entry_center+normal*.14+Vector((0,0,.62)),[tangent,normal,Vector((0,0,1))],(2.28,.08,.06),3)
    shell.box(entry_center+normal*.14+Vector((0,0,2.63)),[tangent,normal,Vector((0,0,1))],(2.22,.08,.055),3)
    # Rectangular tall windows along the same visible wall, one per level.
    for tpos in (.72,):
        wc=p0+(p1-p0)*tpos
        for zc in (1.55,4.45,7.25):
            shell.box(wc+normal*.09+Vector((0,0,zc)),[tangent,normal,Vector((0,0,1))],(1.12,.07,1.42),2)
            # Stone reveal surround, sills and restrained mullions.
            for side in (-1,1):
                shell.box(wc+normal*.13+tangent*(side*.62)+Vector((0,0,zc)),[tangent,normal,Vector((0,0,1))],(.12,.08,1.62),1)
            for side in (-1,1):
                shell.box(wc+normal*.13+Vector((0,0,zc+side*.80)),[tangent,normal,Vector((0,0,1))],(1.36,.08,.12),1)
            shell.box(wc+normal*.16+Vector((0,0,zc)),[tangent,normal,Vector((0,0,1))],(.04,.08,1.28),3)
            shell.box(wc+normal*.16+Vector((0,0,zc)),[tangent,normal,Vector((0,0,1))],(1.16,.08,.04),3)

shell_obj=shell.to_object(col)
shell_obj["source_feature_id"]=802
shell_obj["footprint_source"]="Purdue GIS BuildingShapes FID 802; exact 16-vertex ring at z=0"
shell_obj["elevation_status"]="estimated; three floors are supported by official house-tour reference, heights are not measured"
shell_obj["facade_status"]="light masonry, gables, tower-like mass, dark roofing, and arched glazing qualitatively supported by official Stewart Cooperative About photo; unseen features estimated"
shell_obj["plan_status"]="official polygon footprint with schematic interior room/furniture inserts"

# Roof surfaces are separate so a roof-open interior evidence render can expose
# the schematic floor plates. The ridge direction and sizes remain inferred.
roof=MeshBuild(ROOT_OBJECT+"_roof",[roofmat,trim,stone])
roof.quad((rx0,ry0,roof_eave),(ridge_x,ry0,roof_peak),(ridge_x,ry1,roof_peak),(rx0,ry1,roof_eave),0)
roof.quad((ridge_x,ry0,roof_peak),(rx1,ry0,roof_eave),(rx1,ry1,roof_eave),(ridge_x,ry1,roof_peak),0)
roof.face([(rx0,ry0,roof_eave),(rx1,ry0,roof_eave),(ridge_x,ry0,roof_peak)],2)
roof.face([(rx1,ry1,roof_eave),(rx0,ry1,roof_eave),(ridge_x,ry1,roof_peak)],2)
# narrow ridge cap
roof.box((ridge_x,(ry0+ry1)/2,roof_peak+.06),[(0,1,0),(1,0,0),(0,0,1)],(length+.44,.22,.14),0)
# tower upper gable and roof
for yy in (ty0,ty1): roof.face([(tx0,yy,tower_eave),(tx1,yy,tower_eave),((tx0+tx1)/2,yy,tower_peak)],2)
roof.quad((tx0,ty0,tower_eave),((tx0+tx1)/2,ty0,tower_peak),((tx0+tx1)/2,ty1,tower_peak),(tx0,ty1,tower_eave),0)
roof.quad(((tx0+tx1)/2,ty0,tower_peak),(tx1,ty0,tower_eave),(tx1,ty1,tower_eave),((tx0+tx1)/2,ty1,tower_peak),0)
roof_obj=roof.to_object(col)
roof_obj["roof_status"]="qualitative gable/tower form based on official exterior photograph; ridge, pitch, overhang and heights are estimates"

# Chimney visible above the main roof in the official exterior reference.
chimney=MeshBuild(ROOT_OBJECT+"_chimney",[stone,trim])
chimney.simple_box((ridge_x+1.3,ymax-6.0,12.45),(.72,.78,2.1),0)
chimney.simple_box((ridge_x+1.3,ymax-6.0,13.55),(.90,.92,.18),1)
chimney_obj=chimney.to_object(col)

# Polygon tessellation for schematic floors. Interior room locations, partitions,
# and furniture blocks are not a measured or as-built floor plan.
floor_poly=[Vector((x,y,0)) for x,y in ring]
tris=tessellate_polygon([floor_poly])
floor_zs=[("basement",-2.45,floor_mat),("ground",.12,floor_mat),("second",3.02,upper_floor_mat),("third",5.92,upper_floor_mat)]
interior_objects=[]
for level,z,m in floor_zs:
    slab=MeshBuild(ROOT_OBJECT+"_schematic_floor_"+level,[m])
    for tri in tris:
        slab.face([(floor_poly[idx].x,floor_poly[idx].y,z) for idx in tri],0)
    obj=slab.to_object(col); obj["interior_status"]="schematic floor surface; polygon-derived footprint, no source floor plan"
    obj["story_level"]=level; interior_objects.append(obj)

# Interior room divisions and uses are schematic. The official house tour
# supports bedrooms, a basement, and second/third-floor hallways, but not a plan.
interior_objects=[]
inside_levels=[("basement",-2.45),("ground",.12),("second",3.02),("third",5.92)]
for level,z in inside_levels:
    interior=MeshBuild(ROOT_OBJECT+"_schematic_interior_"+level,[wall_inside,furn_mat,bed_mat])
    if level in ("second","third"):
        y0=ymin+2.2; y1=ymax-2.2; row_h=(y1-y0)/4
        for xoff in (-.82,.82):
            interior.simple_box((cx+xoff,(y0+y1)/2,z+1.15),(.16,y1-y0,2.3),0)
        for i in range(1,4):
            yy=y0+i*row_h
            for side in (-1,1):
                interior.simple_box((cx+side*3.25,yy,z+1.15),(5.3,.16,2.3),0)
        # Eight paired bedrooms per floor, two generic beds in each room.
        for i in range(4):
            yy=y0+(i+.5)*row_h
            for side in (-1,1):
                for xshift in (2.55,3.65):
                    bx=cx+side*xshift
                    interior.simple_box((bx,yy,z+.32),(.82,1.95,.55),1)
                    interior.simple_box((bx,yy,z+.61),(.74,1.78,.10),2)
                    interior.simple_box((bx,yy-.72,z+.68),(.68,.32,.08),2)
    elif level=="ground":
        # Great-room and kitchen/dining use zones follow official descriptions;
        # their locations and furniture placement are schematic.
        yy=cy-1.5
        for side in (-1,1):
            interior.simple_box((cx+side*3.2,yy,z+1.15),(5.4,.16,2.3),0)
        for table_y in (cy-7.0,cy-4.0):
            interior.simple_box((cx-1.7,table_y,z+.84),(2.2,.95,.12),1)
            for dx in (-.85,.85):
                for dy in (-.55,.55): interior.simple_box((cx-1.7+dx,table_y+dy,z+.42),(.14,.14,.78),1)
        interior.simple_box((cx+3.3,cy+6.3,z+.48),(3.4,.75,.9),1)
        interior.simple_box((cx+4.3,cy+3.8,z+.50),(.75,.75,1.0),2)
    else:
        # Basement lounge, laundry and bath zones are documented; arrangement
        # remains illustrative, not a measured plan.
        interior.simple_box((cx-3.2,cy-1.2,z+1.15),(5.0,.16,2.3),0)
        interior.simple_box((cx+2.0,cy+2.8,z+1.15),(.16,7.0,2.3),0)
        interior.simple_box((cx-2.7,cy-4.2,z+.42),(2.2,.9,.68),1)
        interior.simple_box((cx-2.2,cy-2.8,z+.72),(.75,.75,1.3),2)
        interior.simple_box((cx+2.8,cy-4.0,z+.50),(.85,.85,.95),2)
    # Stairs are separate by level so plan previews can isolate each floor.
    next_z=inside_levels[inside_levels.index((level,z))+1][1] if level!="third" else None
    if next_z is not None:
        count=16; run=4.0; tread=run/count; rise=(next_z-z)/count
        for i in range(count):
            yy=cy-2.0+(i+.5)*tread
            interior.simple_box((cx+.7,yy,z+(i+1)*rise/2),(1.0,tread,(i+1)*rise),1)
    interior_obj=interior.to_object(col)
    interior_obj["interior_status"]="schematic room, partition, furniture and stair geometry; no source floor plan"
    interior_obj["story_level"]=level
    interior_obj["supports"]="official House Tour page documents bedrooms/rooms, basement renovation, and second- and third-floor hallways"
    interior_objects.append(interior_obj)

# Preserve the stable exported scene, collection, and root object identifiers.
scene.world.color=(.045,.055,.07)
scene.render.engine="BLENDER_EEVEE"
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
result={"asset":ASSET,"scene":scene.name,"collection":col.name,"root_object":shell_obj.name,"object_count":len(col.objects),"source_fid":802,"source_ring_vertex_count":len(ring),"bounds_xy_m":[[xmin,xmax],[ymin,ymax]],"wall_top_estimate_m":wall_top,"main_ridge_estimate_m":roof_peak,"tower_peak_estimate_m":tower_peak,"story_evidence":"official house-tour page explicitly mentions second- and third-floor hallways; modeled 3 stories despite GIS NUM_LEVELS=1","interior":"schematic floor plates, partitions, use/furniture blocks, stairs and basement insert; not as-built","geometry":"exact official GIS base ring, photo-supported pale-masonry/gabled/tower/arched-entry study, inferred unseen geometry"}
json.dump(result,open(os.path.join(AUDIT,"build_result.json"),"w",encoding="utf-8"),indent=2)
print(json.dumps(result,indent=2))
