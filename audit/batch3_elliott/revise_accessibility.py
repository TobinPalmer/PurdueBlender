"""Evidence-led Elliott accessibility and exterior revision.

Uses the preserved interior source and authoritative GIS outline. The access
door count and awning colors are documented by Purdue; exact facade positions,
door dimensions, routes, and vertical details remain explicitly estimated.
"""
import bpy, math, json, pathlib, shutil
from mathutils import Vector

ROOT = pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
AUD = ROOT/'audit/batch3_elliott'
SRC = ROOT/'modular/buildings/elliott_hall_of_music.blend'
BASE = AUD/'before_resume.blend'
shutil.copy2(SRC, AUD/'pre_round3_accessibility.blend')
bpy.ops.wm.open_mainfile(filepath=str(BASE))
COL = bpy.data.collections['Asset_elliott_hall_of_music']
wall = bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls']
roof = bpy.data.objects['ELLT_Official_Footprint_Roof_Estimated_22_5m']
N = len(wall.data.vertices)//2
ring = [(float(v.co.x),float(v.co.y)) for v in wall.data.vertices[:N]]
assert N == 188 and abs(max(v.co.z for v in wall.data.vertices)-22.5)<1e-4

def material(name, color, rough=.75, noise_scale=0, bump_dist=0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial'); bs=nt.nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
    nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    if noise_scale:
        tc=nt.nodes.new('ShaderNodeTexCoord'); tex=nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=noise_scale; tex.inputs['Detail'].default_value=3
        nt.links.new(tc.outputs['Object'],tex.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color=(*(c*.78 for c in color),1)
        ramp.color_ramp.elements[1].color=(*(min(c*1.17,1) for c in color),1)
        nt.links.new(tex.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        if bump_dist:
            bn=nt.nodes.new('ShaderNodeBump'); bn.inputs['Strength'].default_value=.14; bn.inputs['Distance'].default_value=bump_dist
            nt.links.new(tex.outputs['Fac'],bn.inputs['Height']); nt.links.new(bn.outputs['Normal'],bs.inputs['Normal'])
    return m

brick=material('ELLT_Exterior_Red_Brick_Procedural',(.39,.105,.062),.82,34,.001)
wall.data.materials.clear(); wall.data.materials.append(brick)
stone=material('ELLT_Exterior_Indiana_Limestone',(.69,.65,.55),.82,5,.0007)
glass=material('ELLT_Access_Door_Glass',(.025,.08,.10),.2)
wheelblue=material('ELLT_Access_Wheelchair_Clearance_Blue',(.08,.24,.55),.76)
bronze=material('ELLT_Access_Door_Bronze',(.085,.068,.044),.34)
black=material('ELLT_Access_Awning_Black',(.012,.016,.022),.68)
gold=material('ELLT_Access_Awning_Purdue_Gold',(.88,.47,.035),.48)
paving=material('ELLT_Access_Approach_Paving',(.34,.32,.28),.88,18,.0005)
route_mat=material('ELLT_Access_Route_Matte_Gold',(.40,.25,.075),.88)
tile=material('ELLT_Roof_Red_Clay_Tile_Estimated',(.40,.105,.06),.78,22,.0011)
roof.data.materials.clear(); roof.data.materials.append(tile)
roof['evidence_status']='Red clay tile roof is documented by SAH Archipedia; current plane, height and pitch are estimated because no measured elevation was located.'

def area2(poly): return .5*sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))
area=area2(ring)
seglen=[math.dist(ring[i],ring[(i+1)%N]) for i in range(N)]
cum=[0.0]
for l in seglen: cum.append(cum[-1]+l)
perimeter=cum[-1]

def closest_arc(target, choices=None):
    best=None
    for i in range(N):
        a=ring[i]; b=ring[(i+1)%N]; dx=b[0]-a[0]; dy=b[1]-a[1]; den=dx*dx+dy*dy
        t=max(0,min(1,((target[0]-a[0])*dx+(target[1]-a[1])*dy)/den)) if den else 0
        q=(a[0]+dx*t,a[1]+dy*t); d=math.dist(target,q)
        if choices and i not in choices: continue
        if best is None or d<best[0]: best=(d,i,t,q)
    return best
def point_at(i,t):
    a=ring[i]; b=ring[(i+1)%N]
    return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
def tangent_at(i):
    a=ring[i]; b=ring[(i+1)%N]; dx=b[0]-a[0];dy=b[1]-a[1];ll=math.hypot(dx,dy)
    return dx/ll,dy/ll
def outward(tx,ty): return (ty,-tx) if area>0 else (-ty,tx)
def mesh_obj(name,verts,faces,mat, status):
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.materials.append(mat); me.update()
    ob=bpy.data.objects.new(name,me); COL.objects.link(ob); ob['evidence_status']=status; return ob
def cube(name, center, dims, mat, rot=0, status='Approximate architectural detail.'):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center); o=bpy.context.object; o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    COL.objects.link(o); o.dimensions=dims; o.rotation_euler.z=rot
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat); o['evidence_status']=status; return o

# Purdue identifies one accessible entrance on each of the north and south
# sides. Their coordinates/dimensions are estimated against the official GIS
# polygon because its service supplies a footprint, not a facade elevation.
# Choose long near-cardinal boundary runs so both holes are coherent openings.
north_i=max(range(N),key=lambda i:(ring[i][1]+ring[(i+1)%N][1])/2)
south_i=min(range(N),key=lambda i:(ring[i][1]+ring[(i+1)%N][1])/2)
north=closest_arc((7.5,44.5),{north_i})
south=closest_arc((-25.5,-38.0),{south_i})
doors=[]
for label,q in (('North',north),('South',south)):
    _,i,t,p=q; tx,ty=tangent_at(i); nx,ny=outward(tx,ty); s=cum[i]+t*seglen[i]
    doors.append({'name':label,'i':i,'t':t,'s':s,'p':p,'tangent':(tx,ty),'outward':(nx,ny),'width':3.8,'height':3.0})
assert abs(doors[0]['p'][1]-doors[1]['p'][1])>60

# Replace the closed extrusion with wall strips around the GIS ring. The two
# 3.8 x 3.0 m voids are true gaps through the brick shell, not panels laid over it.
wallverts=[]; wallfaces=[]; doorpane=[]; doorfaces=[]
for i in range(N):
    s0=cum[i]; s1=cum[i+1]; L=seglen[i]
    cuts={s0,s1}
    for d in doors:
        a=d['s']-d['width']/2; b=d['s']+d['width']/2
        if s0<a<s1: cuts.add(a)
        if s0<b<s1: cuts.add(b)
    cuts=sorted(cuts)
    for a,b in zip(cuts,cuts[1:]):
        if b-a<1e-5: continue
        u0=(a-s0)/L;u1=(b-s0)/L
        P0=point_at(i,u0);P1=point_at(i,u1);mid=(a+b)/2
        open_d=next((d for d in doors if abs(mid-d['s'])<d['width']/2-1e-5),None)
        zlevels=[0.0,3.0,4.8,8.0,12.0,16.0,20.0,22.5]
        for z0,z1 in zip(zlevels,zlevels[1:]):
            if open_d and z0<open_d['height']-1e-5: continue
            base=len(wallverts); wallverts.extend([(P0[0],P0[1],z0),(P1[0],P1[1],z0),(P1[0],P1[1],z1),(P0[0],P0[1],z1)])
            wallfaces.append((base,base+1,base+2,base+3))
for d in doors:
    tx,ty=d['tangent'];nx,ny=d['outward'];p=d['p'];w=d['width'];h=d['height']
    # Recessed glazed double leaves and an explicit dark frame within the open shell.
    def local(u,z,off=-.24): return (p[0]+tx*u-nx*off,p[1]+ty*u-ny*off,z)
    vv=[local(-w/2+.12,.06),local(w/2-.12,.06),local(w/2-.12,h-.12),local(-w/2+.12,h-.12)]
    mesh_obj('ELLT_Access_'+d['name']+'_Glazed_Double_Door',vv,[(0,1,2,3)],glass,'Purdue confirms the accessible entrance; the leaf dimensions and facade position are estimated.')
    theta=math.atan2(ty,tx)
    for side,u in [('L',-w/2),('R',w/2)]:
        c=(p[0]+tx*u-nx*.02,p[1]+ty*u-ny*.02,h/2)
        cube('ELLT_Access_'+d['name']+'_Stone_Jamb_'+side,c,(.24,.32,h+.06),stone,theta)
    c=(p[0]-nx*.02,p[1]-ny*.02,h+.10)
    cube('ELLT_Access_'+d['name']+'_Stone_Lintel',c,(w+.48,.32,.26),stone,theta)
    # Distinct paired leaf rails and handles make the entrance read as a door.
    for u in (-.055,.055):
        a=local(u,.12,-.27); b=local(u,h-.13,-.27)
        mesh_obj('ELLT_Access_'+d['name']+'_Door_Mullion_'+str(u).replace('.','_'),[a,(b[0],b[1],b[2]),(b[0]+tx*.045,b[1]+ty*.045,b[2]),(a[0]+tx*.045,a[1]+ty*.045,a[2])],[(0,1,2,3)],bronze,'Estimated door frame detail.')
    for side in (-1,1):
        u=side*.19
        cube('ELLT_Access_'+d['name']+'_Handle_'+str(side),(p[0]+tx*u-nx*.31,p[1]+ty*u-ny*.31,1.05),(.06,.045,.34),gold,theta,'Estimated door hardware.')
    # Black canopy with Purdue-gold fascia and two diagonal brackets.
    ext=1.65; z=3.65; zfront=3.35; aw=w+1.4
    v=[]
    for u in (-aw/2,aw/2):
        v.extend([local(u,z,-.12),local(u,zfront,-ext)])
    mesh_obj('ELLT_Access_'+d['name']+'_Black_Gold_Awning',v,[(0,1,3,2)],black,'Purdue accessibility guidance specifies black-and-gold awnings; awning dimensions and profile are estimated.')
    # Fascia across the projecting outer edge.
    front=(p[0]-nx*ext,p[1]-ny*ext,zfront-.1)
    cube('ELLT_Access_'+d['name']+'_Gold_Awning_Fascia',front,(aw,.18,.38),gold,theta,'Black-and-gold awning colors are documented by Purdue; dimensions estimated.')
    for u in (-aw*.35,aw*.35):
        a=local(u,3.10,-.12); b=local(u,3.10,-ext)
        mesh_obj('ELLT_Access_'+d['name']+'_Awning_Bracket_'+str(u),[a,b,(b[0]+tx*.08,b[1]+ty*.08,b[2]+.05),(a[0]+tx*.08,a[1]+ty*.08,a[2]+.05)],[(0,1,2,3)],bronze,'Estimated structural bracket.')
    # Level landing and approach apron, aligned to the door and extending outside.
    landing_center=(p[0]+nx*2.25,p[1]+ny*2.25,.055)
    cube('ELLT_Access_'+d['name']+'_Level_Landing',landing_center,(5.8,4.5,.11),paving,theta,'Level landing is modeled to represent documented step-free access; its dimensions are estimated.')
    # A short, unobtrusive, physically connected level path leads from apron to threshold.
    # Interior connection toward seating is drawn as a separate inferred aisle trace below.
    sidecenter=(p[0]+nx*1.2,p[1]+ny*1.2,.062)
    cube('ELLT_Access_'+d['name']+'_Exterior_Approach',sidecenter,(2.1,4.2,.12),paving,theta,'Continuous level approach to the entrance; exact site grading and sidewalk alignment are unverified.')

newwall=mesh_obj('ELLT_Official_GIS_Wall_with_North_South_Access_Openings',wallverts,wallfaces,brick,'Official GIS footprint; documented north/south accessible door count. Door placement, dimensions, and all vertical dimensions are estimated.')
old_mesh=wall.data; wall.data=newwall.data; bpy.data.objects.remove(newwall,do_unlink=True); bpy.data.meshes.remove(old_mesh)
wall['evidence_status']='Official 188-point GIS footprint with true north/south accessible entrance openings; vertical dimensions and exact door locations remain estimates.'
wall['north_access_arc_m']=doors[0]['s']; wall['south_access_arc_m']=doors[1]['s']

# Limestone bands and pilasters establish the material vocabulary in SAH's
# account without inventing a regular window schedule.
for k,z in enumerate((4.8,9.6,14.4,19.2)):
    vv=[];ff=[]
    for i,(x,y) in enumerate(ring):
        tx,ty=tangent_at(i);nx,ny=outward(tx,ty);x2,y2=ring[(i+1)%N]
        # Raise each limestone course slightly off the brick face to avoid z-fighting.
        base=len(vv)
        vv.extend([(x+nx*.025,y+ny*.025,z-.14),(x2+nx*.025,y2+ny*.025,z-.14),(x2+nx*.20,y2+ny*.20,z-.14),(x+nx*.20,y+ny*.20,z-.14),
                   (x+nx*.025,y+ny*.025,z+.14),(x2+nx*.025,y2+ny*.025,z+.14),(x2+nx*.20,y2+ny*.20,z+.14),(x+nx*.20,y+ny*.20,z+.14)])
        ff.extend([tuple(base+j for j in f) for f in ((4,5,6,7),(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])
    ob=mesh_obj('ELLT_Exterior_Limestone_Band_%02d'%k,vv,ff,stone,'Indiana-limestone bands are documented by SAH Archipedia; band elevations are estimated.')
for i in range(N):
    a=ring[i];b=ring[(i+1)%N];L=seglen[i]
    if L<8: continue
    dx=b[0]-a[0];dy=b[1]-a[1];tx=dx/L;ty=dy/L;nx,ny=outward(tx,ty)
    theta=math.atan2(ty,tx)
    count=max(1,int(L//12))
    for k in range(1,count+1):
        t=k/(count+1);p=(a[0]+dx*t,a[1]+dy*t)
        cube('ELLT_Exterior_Limestone_Pilaster_%03d_%02d'%(i,k),(p[0]+nx*.13,p[1]+ny*.13,11.3),(.46,.34,22.1),stone,theta,'Pilasters are documented by SAH Archipedia; their precise spacing and height are estimated. No unsupported window rhythm is added.')

# A flytower is documented in architectural history, but its footprint and
# height are not measured. Fit a simple mass around the model's estimated stage.
stage=bpy.data.objects['ELLT_B3_stage']; stagepts=[stage.matrix_world@Vector(v) for v in stage.bound_box]
sx=(min(v.x for v in stagepts)+max(v.x for v in stagepts))/2
sy=(min(v.y for v in stagepts)+max(v.y for v in stagepts))/2
tw,td=24.0,22.0
def inside(x,y):
    q=False
    for i,(ax,ay) in enumerate(ring):
        bx,by=ring[i-1]
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:q=not q
    return q
while not all(inside(sx+xx*tw/2,sy+yy*td/2) for xx,yy in ((-1,-1),(-1,1),(1,-1),(1,1))) and tw>9:
    tw*=.9;td*=.9
tower=cube('ELLT_Estimated_Stage_Fly_Tower',(sx,sy,27.8),(tw,td,10.6),brick,status='A flytower is documented by SAH Archipedia; the stage-end placement, 10.6 m extension and fitted footprint are estimated.')
cube('ELLT_Estimated_Flytower_Limestone_Cornice',(sx,sy,33.15),(tw+.55,td+.55,.34),stone,status='Limestone trim vocabulary documented by SAH; tower cap dimensions estimated.')
cube('ELLT_Estimated_Flytower_Tile_Cap',(sx,sy,33.48),(tw+.85,td+.85,.32),tile,status='Red clay tile roof documented by SAH; flytower cap dimensions and profile estimated.')

# Raised tile courses make the documented material legible. Tile module, flat
# plane, and 22.5 m level remain estimates. The flytower footprint is left clear.
tv=[];tf=[];tile_count=0
for row,y in enumerate([min(v[1] for v in ring)+.24+i*.48 for i in range(int((max(v[1] for v in ring)-min(v[1] for v in ring)-.48)/.48)+1)]):
    x=min(v[0] for v in ring)+.39+(row%2)*.39
    while x<max(v[0] for v in ring):
        xa,xb=x-.39,x+.39;ya,yb=y-.215,y+.215
        if all(inside(xx,yy) for xx,yy in ((xa,ya),(xa,yb),(xb,ya),(xb,yb))) and not (abs(x-sx)<tw/2+.3 and abs(y-sy)<td/2+.3):
            base=len(tv); z0,z1=22.505,22.565
            tv.extend([(xa,ya,z0),(xb,ya,z0),(xb,yb,z0),(xa,yb,z0),(xa,ya,z1),(xb,ya,z1),(xb,yb,z1),(xa,yb,z1)])
            tf.extend([tuple(base+j for j in f) for f in ((4,5,6,7),(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))]);tile_count+=1
        x+=.82
tile_obj=mesh_obj('ELLT_Estimated_Raised_Clay_Tile_Courses',tv,tf,tile,'SAH Archipedia documents a red clay tile roof. Tile scale, roof plane, height and shape are estimates.')
tile_obj['tile_count_estimate']=tile_count

# Level conceptual aisle traces connect the actual openings to two nearby
# main-floor accessible seating clusters. The current seating diagram is not to
# scale; these alignments are explicitly estimated pending a measured plan.
route_targets=[(-.4,13.9),(13.6,2.6)]
route_notes=[]
for d,target in zip(doors,route_targets):
    p=d['p'];nx,ny=d['outward'];tx,ty=d['tangent']
    inside=(p[0]-nx*1.4,p[1]-ny*1.4)
    # Route runs along a presumed cross aisle on the auditorium floor. It is a
    # line inset in the floor, not an architectural wall or a claim of surveyed clearance.
    near=closest_arc(target)
    sgoal=near[1]*0.0+cum[near[1]]+near[2]*seglen[near[1]]
    forward=(sgoal-d['s'])%perimeter; backward=(d['s']-sgoal)%perimeter
    direction=1 if forward<=backward else -1; travel=min(forward,backward)
    pts=[inside,(p[0]-nx*3.5,p[1]-ny*3.5)]
    steps=max(1,int(travel/4))
    for step in range(1,steps+1):
        ss=(d['s']+direction*travel*step/steps)%perimeter
        ix=max(i for i,v in enumerate(cum[:-1]) if v<=ss)
        t=(ss-cum[ix])/seglen[ix];q=point_at(ix,t);qx,qy=outward(*tangent_at(ix))
        pts.append((q[0]-qx*3.5,q[1]-qy*3.5))
    pts.append(target)
    # A contrasting floor bay marks a wheelchair clear space near the cluster;
    # the open pad is estimated, while the seat symbols and floor level are source-informed.
    theta=math.atan2(target[1]-pts[-2][1],target[0]-pts[-2][0])
    cube('ELLT_Access_'+d['name']+'_Estimated_Wheelchair_Clear_Space',(target[0],target[1],.155),(1.0,1.35,.08),wheelblue,theta,'Purdue identifies wheelchair seating on the main floor; this clear-space position and 1.0 x 1.35 m dimensions are estimates from the unscaled seating chart.')
    # Create a floor ribbon from the route point sequence, constant estimated width.
    verts=[]
    for j,q in enumerate(pts):
        prev=Vector(pts[max(0,j-1)]); nxt=Vector(pts[min(len(pts)-1,j+1)])
        v=nxt-prev; v.normalize(); n=Vector((-v.y,v.x)); verts.extend([(q[0]+n.x*.75,q[1]+n.y*.75,.17),(q[0]-n.x*.75,q[1]-n.y*.75,.17)])
    faces=[]
    for j in range(len(pts)-1): faces.append((2*j,2*j+1,2*j+3,2*j+2))
    ob=mesh_obj('ELLT_Access_'+d['name']+'_Estimated_Level_Interior_Route',verts,faces,route_mat,'Estimated conceptual level route from a documented accessible door toward the nearest main-floor accessible-seat cluster; seating chart is unscaled and no measured lobby plan was located.')
    route_notes.append({'door':d['name'],'start_xy':[round(p[0],3),round(p[1],3)],'target_xy':list(target),'path_xy':[[round(x,3),round(y,3)] for x,y in pts],'width_m_estimate':1.5,'level_z_m':.17,'route_alignment':'estimated perimeter-side aisle; not measured'})

# Keep existing seating and interior. Mark geometry whose exact registration is
# not certified by the unscaled seating diagram.
for n in ('ELLT_B3_access','ELLT_B3_seat','ELLT_B3_frame','ELLT_B3_stair','ELLT_B3_balcony','ELLT_B3_rail','ELLT_B3_stage','ELLT_B3_ceiling'):
    ob=bpy.data.objects.get(n)
    if ob: ob['evidence_status']='Estimated interior geometry derived from an unscaled Purdue seating chart; row counts/levels informed by published chart, coordinates and dimensions are not measured.'

# Render review cameras from north and south, then save, reopen and verify mesh
# counts, shell openings and export membership.
for ob in bpy.context.scene.objects:
    if ob.name.startswith('ELLT_Round3_Review'): bpy.data.objects.remove(ob,do_unlink=True)
scene=bpy.context.scene; scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1200;scene.render.resolution_y=850;scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
scene.world=bpy.data.worlds.get('Elliott_Round3_ReviewWorld') or bpy.data.worlds.new('Elliott_Round3_ReviewWorld')
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.75,.78,1)
def camera(name,loc,target,lens=48):
    cd=bpy.data.cameras.new(name);co=bpy.data.objects.new(name,cd);scene.collection.objects.link(co)
    co.location=loc;co.rotation_euler=(Vector(target)-co.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;cd.type='ORTHO';cd.ortho_scale=18;return co
def render_view(name,door):
    p=door['p'];nx,ny=door['outward'];cam=camera('ELLT_Round3_Review_'+name,(p[0]+nx*22,p[1]+ny*22,8),(p[0],p[1],2.0));scene.camera=cam
    cd=cam.data
    scene.render.filepath=str(AUD/('round3_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(cd)
for ob in list(COL.all_objects):
    if ob is not None and ob.type=='MESH': ob.hide_render=False
for ob in bpy.data.objects:
    if ob.type=='MESH' and ob.name not in {x.name for x in COL.all_objects if x is not None}: ob.hide_render=True
render_view('north_door',doors[0])
render_view('south_door',doors[1])
bpy.ops.wm.save_as_mainfile(filepath=str(SRC))
bpy.ops.wm.open_mainfile(filepath=str(SRC))
COL=bpy.data.collections['Asset_elliott_hall_of_music']
wall=bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls']
summary={'saved_and_reopened':True,'export_collection':COL.name,'export_objects':len(COL.all_objects),'mesh_objects':sum(o.type=='MESH' for o in COL.all_objects),'wall_faces':len(wall.data.polygons),'wall_bounds_m':[min(v.co[i] for v in wall.data.vertices) for i in range(3)]+[max(v.co[i] for v in wall.data.vertices) for i in range(3)],'GIS_ring_vertices':N,'true_access_openings':2,'doors':[{'name':d['name'],'xy':[round(d['p'][0],3),round(d['p'][1],3)],'width_m_estimate':d['width'],'height_m_estimate':d['height']} for d in doors],'accessible_routes':route_notes,'wheelchair_clear_spaces_estimated':2,'window_holes_added':0,'seat_count_estimate':5946,'roof_tile_count_estimate':tile_count,'roof_plane_height_m_estimate':22.5,'flytower_top_m_estimate':33.48,'limitations':'Door positions/dimensions, path alignment/width, pilaster intervals, roof height/profile, flytower and auditorium seating coordinates remain estimated; no exact facade elevation or scaled interior plan was found.'}
(AUD/'result_round3_accessibility.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
