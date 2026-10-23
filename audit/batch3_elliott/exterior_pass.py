"""Evidence-led exterior pass for the Elliott Hall source asset.

Writes only modular/buildings/elliott_hall_of_music.blend and this audit folder.
The GIS outline remains the horizontal placement reference; architectural detail
not confirmed by a measured elevation is tagged as inferred.
"""
import bpy, math, json, pathlib, shutil
from mathutils import Vector

ROOT=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
SRC=ROOT/'modular/buildings/elliott_hall_of_music.blend'
AUD=ROOT/'audit/batch3_elliott'
BACKUP=AUD/'before_exterior_pass.blend'
shutil.copy2(SRC,BACKUP)
bpy.ops.wm.open_mainfile(filepath=str(SRC))
COL=bpy.data.collections['Asset_elliott_hall_of_music']
for ob in list(COL.objects):
    if ob.name.startswith('ELLT_EXT_'):
        bpy.data.objects.remove(ob,do_unlink=True)
WALL=bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls']
ROOF=bpy.data.objects['ELLT_Official_Footprint_Roof_Estimated_22_5m']
N=len(WALL.data.vertices)//2
outline=[(float(v.co.x),float(v.co.y)) for v in WALL.data.vertices[:N]]
assert len(outline)==188 and all(abs(WALL.data.vertices[i+N].co.z-22.5)<1e-4 for i in range(N))

def mat(name,color,rough=.7,noise=0,bump=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1);m.use_nodes=True
    nt=m.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial')
    bs=nt.nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough
    nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    if noise:
        tc=nt.nodes.new('ShaderNodeTexCoord');tx=nt.nodes.new('ShaderNodeTexNoise');tx.inputs['Scale'].default_value=noise;tx.inputs['Detail'].default_value=3
        nt.links.new(tc.outputs['Object'],tx.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*(c*.76 for c in color),1);ramp.color_ramp.elements[1].color=(*(min(c*1.16,1) for c in color),1)
        nt.links.new(tx.outputs['Fac'],ramp.inputs['Fac']);nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        if bump:
            bn=nt.nodes.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.13;bn.inputs['Distance'].default_value=bump
            nt.links.new(tx.outputs['Fac'],bn.inputs['Height']);nt.links.new(bn.outputs['Normal'],bs.inputs['Normal'])
    return m

brick=WALL.data.materials[0]
brick.name='ELLT_Exterior_Red_Brick_Procedural'
limestone=mat('ELLT_Exterior_Indiana_Limestone',(.70,.66,.56),.82,5,.0007)
glass=mat('ELLT_Exterior_Recessed_Window_Glass',(.018,.045,.062),.22)
frame=mat('ELLT_Exterior_Bronze_Window_Frames',(.095,.075,.048),.38)
door_glass=mat('ELLT_Entry_Lobby_Glass',(.025,.065,.079),.19)
tile=mat('ELLT_Red_Clay_Tile_Roof',(.43,.115,.066),.78,18,.0014)
statue_mat=mat('ELLT_Sculpture_Warm_Limestone',(.63,.58,.48),.77,14,.001)
walk=mat('ELLT_Entry_Stone_Paving',(.50,.47,.39),.88,18,.0006)

# Recreate wall faces from the exact GIS ring and subdivide only where a window
# or the inferred lower south approach door creates a true opening.
def rdp(p,eps):
    if len(p)<3:return p
    ax,ay=p[0];bx,by=p[-1];dx=bx-ax;dy=by-ay;den=dx*dx+dy*dy
    best=-1;idx=0
    for i,(x,y) in enumerate(p[1:-1],1):
        t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/den)) if den else 0
        d=math.hypot(x-(ax+t*dx),y-(ay+t*dy))
        if d>best:best=d;idx=i
    if best>eps:return rdp(p[:idx+1],eps)[:-1]+rdp(p[idx:],eps)
    return [p[0],p[-1]]
def signed_area(p):return .5*sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))
area=signed_area(outline)
start=0;far=max(range(1,N),key=lambda i:(outline[i][0]-outline[start][0])**2+(outline[i][1]-outline[start][1])**2)
a=rdp(outline[start:far+1],.8);b=rdp(outline[far:]+outline[:start+1],.8)
simple=a[:-1]+b[:-1]+[outline[start]]
idxs=[]
for p in simple[:-1]:idxs.append(min(range(N),key=lambda i:(outline[i][0]-p[0])**2+(outline[i][1]-p[1])**2))

def path_between(i,j):
    out=[outline[i]];k=i
    while k!=j:
        k=(k+1)%N;out.append(outline[k])
        if len(out)>N+1:raise RuntimeError('ring traversal failed')
    return out
def path_length(p):return sum(math.dist(p[i],p[i+1]) for i in range(len(p)-1))
def path_at(p,dist):
    left=max(0,min(path_length(p),dist))
    for x,y in zip(p,p[1:]):
        d=math.dist(x,y)
        if left<=d or d==0:
            t=left/d if d else 0
            return (x[0]+(y[0]-x[0])*t,x[1]+(y[1]-x[1])*t)
        left-=d
    return p[-1]
def mesh_obj(name,verts,faces,material):
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update()
    ob=bpy.data.objects.new(name,me);COL.objects.link(ob);ob['evidence_status']='Architectural detail inferred from published references; not a measured elevation.'
    return ob
def cube_mesh(name,center,dims,material):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center);o=bpy.context.object;o.name=name
    for c in list(o.users_collection):c.objects.unlink(o)
    COL.objects.link(o);o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material);o['evidence_status']='Approximate architectural detail from published references.'
    return o

# Identify simplified outline runs. Use long straight runs for fenestration.
runs=[]
for k,i in enumerate(idxs):
    j=idxs[(k+1)%len(idxs)]
    p=path_between(i,j);L=path_length(p)
    if L<0.75:continue
    v=(p[-1][0]-p[0][0],p[-1][1]-p[0][1]);ang=math.degrees(math.atan2(v[1],v[0]))
    runs.append((p,L,ang))

# The long south/southwest run is the likely public approach: SAH notes entries
# between Elliott and Hovde; exact door coordinates are unverified.
door_run=max((r for r in runs if r[1]>30),key=lambda r:(-r[0][0][1]-r[0][-1][1])/2)
door_center=door_run[1]*.72
door_w=4.8;door_h=4.25
window_specs=[]
for ri,(p,L,ang) in enumerate(runs):
    if L<13:continue
    # Narrow vertical windows at regular bays only on substantial straight walls.
    usable=[L*t for t in (.13,.29,.45,.61,.77,.91)]
    for u in usable:
        if p is door_run[0] and abs(u-door_center)<door_w*1.5:continue
        for z0,z1 in ((3.7,5.75),(8.15,10.20),(12.6,14.65),(17.05,19.10)):
            window_specs.append((p,u,1.45,z0,z1))

# Collect normalized exterior window/door intervals on each straight run.
wallverts=[];wallfaces=[];frames=[];framefaces=[];glassverts=[];glassfaces=[];doorverts=[];doorfaces=[]
openings_by_run=[]
for p,L,ang in runs:
    openings=[]
    for qp,u,w,z0,z1 in window_specs:
        if qp is p:openings.append((max(0,u-w/2),min(L,u+w/2),z0,z1,'window'))
    if p is door_run[0]:openings.append((door_center-door_w/2,door_center+door_w/2,0,door_h,'door'))
    openings_by_run.append((p,L,openings))

for p,L,opens in openings_by_run:
    breaks={0.0,L}
    for o0,o1,z0,z1,kind in opens:
        breaks.update((max(0,o0),min(L,o1)))
    # follow the original faceted GIS ring while putting opening edges exactly
    # at their horizontal coordinates.
    coarse=[0.0]
    u=1.5
    while u<L:coarse.append(u);u+=1.5
    coarse.append(L);breaks.update(coarse)
    us=sorted(breaks)
    zbreaks=sorted({0.0,2.3,3.7,5.75,6.8,8.15,10.2,11.25,12.6,14.65,15.5,17.05,19.1,20.3,22.5,door_h})
    for u0,u1 in zip(us,us[1:]):
        if u1-u0<1e-5:continue
        mid=(u0+u1)/2;P0=path_at(p,u0);P1=path_at(p,u1)
        for z0,z1 in zip(zbreaks,zbreaks[1:]):
            if z1-z0<1e-5:continue
            hole=None
            for o0,o1,h0,h1,kind in opens:
                if o0-1e-5<=mid<=o1+1e-5 and h0-1e-5<=((z0+z1)/2)<=h1+1e-5:
                    hole=(kind,o0,o1,h0,h1);break
            if hole:continue
            base=len(wallverts);wallverts.extend([(P0[0],P0[1],z0),(P1[0],P1[1],z0),(P1[0],P1[1],z1),(P0[0],P0[1],z1)]);wallfaces.append((base,base+1,base+2,base+3))
    # Window planes and limestone surrounds, set just behind the exterior face.
    for o0,o1,z0,z1,kind in opens:
        if kind=='door':
            # Actual gap in the brick wall; glazed double doors set back 0.22 m.
            midp=path_at(p,(o0+o1)/2);before=path_at(p,o0);after=path_at(p,o1)
            dx=after[0]-before[0];dy=after[1]-before[1];ll=math.hypot(dx,dy);tx,ty=dx/ll,dy/ll
            outward=(ty,-tx) if area>0 else (-ty,tx)
            def dv(u,z,offset=.22):
                q=path_at(p,u);return (q[0]-outward[0]*offset,q[1]-outward[1]*offset,z)
            dbase=len(doorverts);doorverts += [dv(o0+.20,.15),dv(o1-.20,.15),dv(o1-.20,door_h-.12),dv(o0+.20,door_h-.12)];doorfaces.append((dbase,dbase+1,dbase+2,dbase+3))
            # Limestone surround: pilasters and lintel, with a deep projecting canopy.
            cube_mesh('ELLT_EXT_Main_Entry_Pilaster_L',(*path_at(p,o0-.3),2.8),(.42,.42,5.6),limestone)
            cube_mesh('ELLT_EXT_Main_Entry_Pilaster_R',(*path_at(p,o1+.3),2.8),(.42,.42,5.6),limestone)
            # Reorienting the portal masonry to the facade tangent.
            for nm in ('ELLT_EXT_Main_Entry_Pilaster_L','ELLT_EXT_Main_Entry_Pilaster_R'):
                ob=bpy.data.objects[nm];ob.rotation_euler.z=math.atan2(ty,tx)
            lintel=cube_mesh('ELLT_EXT_Main_Entry_Limestone_Lintel',(*path_at(p,(o0+o1)/2),4.48),(door_w+1.0,.48,.44),limestone);lintel.rotation_euler.z=math.atan2(ty,tx)
            # Curved entrance canopy profile: shallow bowed front edge, tiled top.
            cv=[];cf=[];cu=(o0+o1)/2
            for k in range(9):
                t=k/8;u0c=o0-.8+(door_w+1.6)*t;pt=path_at(p,u0c)
                for z in (5.0,5.55-.45*math.sin(math.pi*t)):
                    cv.append((pt[0]-outward[0]*(.25+1.65),pt[1]-outward[1]*(.25+1.65),z))
            for k in range(8):cf.append((2*k,2*k+2,2*k+3,2*k+1))
            mesh_obj('ELLT_EXT_Curving_Limestone_Entry_Canopy',cv,cf,limestone)
            # Art Deco fluted entrance pier strips and glass-door mullions.
            for side in (-1,1):
                q=path_at(p,(o0+o1)/2+side*door_w*.24)
                cube_mesh('ELLT_EXT_Entry_Door_Mullion',(*q,2.0),(.07,.09,3.55),frame)
        else:
            before=path_at(p,o0);after=path_at(p,o1);dx=after[0]-before[0];dy=after[1]-before[1];ll=math.hypot(dx,dy);tx,ty=dx/ll,dy/ll
            outward=(ty,-tx) if area>0 else (-ty,tx)
            def wv(u,z,off=.12):
                q=path_at(p,u);return (q[0]-outward[0]*off,q[1]-outward[1]*off,z)
            gbase=len(glassverts);glassverts += [wv(o0+.10,z0+.10),wv(o1-.10,z0+.10),wv(o1-.10,z1-.10),wv(o0+.10,z1-.10)];glassfaces.append((gbase,gbase+1,gbase+2,gbase+3))
            # Stone sill/lintel and slim bronze jambs, framed just proud of wall.
            for nm,u,z,dims in [('ELLT_EXT_Window_Limestone_Sill', (o0+o1)/2,z0-.13,(o1-o0+.42,.34,.20)),('ELLT_EXT_Window_Limestone_Lintel',(o0+o1)/2,z1+.13,(o1-o0+.42,.34,.20))]:
                q=path_at(p,u);ob=cube_mesh(nm,(*q,z),dims,limestone);ob.rotation_euler.z=math.atan2(ty,tx)
            for u in (o0-.11,o1+.11):
                q=path_at(p,u);ob=cube_mesh('ELLT_EXT_Window_Limestone_Jamb',(*q,(z0+z1)/2),(.22,.34,z1-z0+.24),limestone);ob.rotation_euler.z=math.atan2(ty,tx)
            # Center mullion and transom divide each deep, recessed opening.
            q=path_at(p,(o0+o1)/2);ob=cube_mesh('ELLT_EXT_Window_Mullion',(*q,(z0+z1)/2),(.055,.12,z1-z0-.12),frame);ob.rotation_euler.z=math.atan2(ty,tx)
            q=path_at(p,(o0+o1)/2);ob=cube_mesh('ELLT_EXT_Window_Transom',(*q,(z0+z1)/2),((o1-o0)-.1,.12,.055),frame);ob.rotation_euler.z=math.atan2(ty,tx)
mesh_obj('ELLT_EXT_GIS_Facades_With_True_Openings',wallverts,wallfaces,brick)
mesh_obj('ELLT_EXT_Recessed_Window_Glazing',glassverts,glassfaces,glass)
mesh_obj('ELLT_EXT_Glazed_Main_Entry_Doors',doorverts,doorfaces,door_glass)
WALL.hide_render=True;WALL.hide_viewport=True;WALL['replaced_by']='ELLT_EXT_GIS_Facades_With_True_Openings';WALL['horizontal_source']='Official GIS footprint FID 617, retained at perimeter sample vertices.'

# Limestone string courses and cornice follow the GIS perimeter.
def perimeter_band(name,z,width=.22,projection=.16):
    verts=[];faces=[];pts=outline
    for k,p0 in enumerate(pts):
        p1=pts[(k+1)%len(pts)];dx=p1[0]-p0[0];dy=p1[1]-p0[1];ll=math.hypot(dx,dy)
        if ll<1e-6:continue
        nx,ny=(dy/ll,-dx/ll) if area>0 else (-dy/ll,dx/ll)
        ids=[]
        for off,zz in ((0,z-width/2),(projection,z-width/2),(projection,z+width/2),(0,z+width/2)):
            ids.append(len(verts));verts.extend([(p0[0]+nx*off,p0[1]+ny*off,zz),(p1[0]+nx*off,p1[1]+ny*off,zz)])
        for j in range(4):
            a=ids[j];b=ids[(j+1)%4];faces.append((a,a+1,b+1,b))
    mesh_obj(name,verts,faces,limestone)
for z in (2.25,7.5,12.75,18.0,22.35):perimeter_band('ELLT_EXT_Limestone_String_Course',z,.18,.14)

# Pilasters on two long principal elevations echo the stripped-classical facade.
pilv=[];pilf=[]
for p,L,ang in runs:
    if L<35:continue
    for u in (L*.10,L*.30,L*.50,L*.70,L*.90):
        q=path_at(p,u);a=path_at(p,max(0,u-.25));b=path_at(p,min(L,u+.25));dx=b[0]-a[0];dy=b[1]-a[1];ll=math.hypot(dx,dy);tx,ty=dx/ll,dy/ll
        nx,ny=(ty,-tx) if area>0 else (-ty,tx);cx=q[0]+nx*.11;cy=q[1]+ny*.11
        corners=[]
        for x,y,z in [(-.34,-.18,.6),(.34,-.18,.6),(.34,.18,.6),(-.34,.18,.6),(-.34,-.18,22.5),(.34,-.18,22.5),(.34,.18,22.5),(-.34,.18,22.5)]:
            corners.append((cx+x*tx+y*nx,cy+x*ty+y*ny,z))
        base=len(pilv);pilv.extend(corners);pilf.extend([tuple(base+i for i in f) for f in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]])
mesh_obj('ELLT_EXT_Indiana_Limestone_Pilasters',pilv,pilf,limestone)

# 1938 Art Deco relief sculptures on the south wall are modeled as abstract
# heroic figures. Exact poses and plinth spacing are not established by plans.
south_runs=[r for r in runs if r[1]>8 and sum(q[1] for q in (r[0][0],r[0][-1]))/2<-28]
if south_runs:
    p,L,ang=max(south_runs,key=lambda r:r[1]); dx=p[-1][0]-p[0][0];dy=p[-1][1]-p[0][1];ll=math.hypot(dx,dy);tx,ty=dx/ll,dy/ll;nx,ny=(ty,-tx) if area>0 else (-ty,tx)
    for j,u in enumerate((L*.28,L*.50,L*.72),1):
        q=path_at(p,u);px=q[0]+nx*.38;py=q[1]+ny*.38
        cube_mesh(f'ELLT_EXT_Sculpture_{j}_Limestone_Plinth',(px,py,.55),(.72,.66,1.1),limestone)
        # stylized draped figure: tapered torso, raised shoulders, head and arms
        bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=.48,radius2=.30,depth=1.65,location=(px,py,1.93));body=bpy.context.object;body.name=f'ELLT_EXT_Sculpture_{j}_Heroic_Figure';body.rotation_euler.z=math.atan2(ty,tx)
        for c in list(body.users_collection):c.objects.unlink(body)
        COL.objects.link(body);body.data.materials.append(statue_mat);body['evidence_status']='Interpretive figure; references establish six heroic sculptures, not exact pose.'
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.28,location=(px,py,2.97));head=bpy.context.object;head.name=f'ELLT_EXT_Sculpture_{j}_Head'
        for c in list(head.users_collection):c.objects.unlink(head)
        COL.objects.link(head);head.data.materials.append(statue_mat)
        for side in (-1,1):
            bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=.16,radius2=.12,depth=1.05,location=(px+tx*side*.44,py+ty*side*.44,2.08));arm=bpy.context.object;arm.name=f'ELLT_EXT_Sculpture_{j}_Arm';arm.rotation_euler.z=math.atan2(ty,tx)
            for c in list(arm.users_collection):c.objects.unlink(arm)
            COL.objects.link(arm);arm.data.materials.append(statue_mat)

# Upper flytower at the stage end: the published description confirms a tower,
# but its exact footprint and elevation remain unmeasured in accessible sources.
stage=bpy.data.objects['ELLT_B3_stage'];stagepts=[stage.matrix_world@Vector(v) for v in stage.bound_box]
sx=(min(v.x for v in stagepts)+max(v.x for v in stagepts))/2;sy=(min(v.y for v in stagepts)+max(v.y for v in stagepts))/2
# Fit the mass to the GIS ring and back it off until all plan corners stay inside.
def inside(x,y):
    q=False
    for i,(ax,ay) in enumerate(outline):
        bx,by=outline[i-1]
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:q=not q
    return q
tw,td=26.0,25.0
while not all(inside(sx+xx*tw/2,sy+yy*td/2) for xx,yy in ((-1,-1),(-1,1),(1,-1),(1,1))) and tw>10:
    tw*=.9;td*=.9
tower=cube_mesh('ELLT_EXT_Stage_Fly_Tower',(sx,sy,27.8),(tw,td,10.6),brick)
tower['evidence_status']='Flytower confirmed by architectural history; estimated 10.6 m above roof and footprint fitted inside GIS outline.'
cap=cube_mesh('ELLT_EXT_Flytower_Limestone_Cornice',(sx,sy,33.15),(tw+.55,td+.55,.34),limestone)
cap2=cube_mesh('ELLT_EXT_Flytower_Clay_Tile_Cap',(sx,sy,33.48),(tw+.85,td+.85,.32),tile)
# Stage-end high windows/vents on the flytower.
for sign in (-1,1):
    for j in range(5):
        cube_mesh('ELLT_EXT_Flytower_High_Vent',(sx-tw/2-.035,sy+(j-2)*3.6,29.4),(.08,1.35,3.8),glass)

# Add a real clay tile finish to the GIS roof plate, plus a raised tiled eave.
ROOF.data.materials.clear();ROOF.data.materials.append(tile)
ROOF['surface']='Procedural red clay tile. Roof level remains 22.5 m estimated; roof form unmeasured.'
ROOF.hide_render=False;ROOF.hide_viewport=False
perimeter_band('ELLT_EXT_Roof_Eave_Limestone',22.38,.32,.25)

# Stone entry walk, aligned to the inferred public opening and extending outward.
if door_run:
    p,L,_=door_run;before=path_at(p,door_center-.2);after=path_at(p,door_center+.2);dx=after[0]-before[0];dy=after[1]-before[1];ll=math.hypot(dx,dy);tx,ty=dx/ll,dy/ll;nx,ny=(ty,-tx) if area>0 else (-ty,tx)
    q=path_at(p,door_center);walkobj=cube_mesh('ELLT_EXT_Entry_Accessible_Approach',(q[0]+nx*5.4,q[1]+ny*5.4,.12),(3.2,10.8,.24),walk);walkobj.rotation_euler.z=math.atan2(ny,nx)
    # Threshold landing is level with the entry and ties into the public door.
    cube_mesh('ELLT_EXT_Entry_Level_Landing',(q[0]+nx*1.15,q[1]+ny*1.15,.14),(6.8,2.6,.28),walk).rotation_euler.z=math.atan2(ty,tx)

# Roof tile pattern uses the real object coordinates for repeating courses.
nt=tile.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');tc=nt.nodes.new('ShaderNodeTexCoord');bt=nt.nodes.new('ShaderNodeTexBrick')
bt.inputs['Color1'].default_value=(.48,.14,.08,1);bt.inputs['Color2'].default_value=(.30,.075,.045,1);bt.inputs['Mortar'].default_value=(.14,.085,.065,1);bt.inputs['Scale'].default_value=1.0;bt.inputs['Mortar Size'].default_value=.018;bt.inputs['Brick Width'].default_value=.48;bt.inputs['Row Height'].default_value=.22
nt.links.new(tc.outputs['Object'],bt.inputs['Vector']);nt.links.new(bt.outputs['Color'],bs.inputs['Base Color'])
bn=nt.nodes.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.18;bn.inputs['Distance'].default_value=.012;nt.links.new(bt.outputs['Fac'],bn.inputs['Height']);nt.links.new(bn.outputs['Normal'],bs.inputs['Normal'])

# Camera renders for evidence: front approach, angled exterior, and flytower.
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1250;scene.render.resolution_y=875;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.show_shadows=True
world=bpy.data.worlds.get('ELLT_Exterior_Review_World') or bpy.data.worlds.new('ELLT_Exterior_Review_World');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.28,.33,.39,1);scene.world=world
sun_data=bpy.data.lights.new('ELLT_Exterior_Sun','SUN');sun_data.energy=2.2;sun=bpy.data.objects.new('ELLT_Exterior_Sun',sun_data);scene.collection.objects.link(sun);sun.rotation_euler=(math.radians(28),math.radians(-22),math.radians(-36))
def cam(name,loc,target,scale):
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=loc;data.type='ORTHO';data.ortho_scale=scale;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
target=(0,2,11)
for name,loc,scale in [('southwest',(126,-135,82),155),('east',(145,65,76),155),('flytower',(22,105,97),140)]:
    c=cam('ELLT_EXT_ReviewCam_'+name,loc,target,scale);cd=c.data;scene.camera=c;scene.render.filepath=str(AUD/f'exterior_{name}.png');bpy.ops.render.render(write_still=True);bpy.data.objects.remove(c,do_unlink=True);bpy.data.cameras.remove(cd)
bpy.data.objects.remove(sun,do_unlink=True);bpy.data.lights.remove(sun_data)

bpy.ops.wm.save_as_mainfile(filepath=str(SRC));bpy.ops.wm.open_mainfile(filepath=str(SRC))
COL=bpy.data.collections['Asset_elliott_hall_of_music']
report={'saved_and_reopened':True,'source_file':str(SRC),'export_collection':'Asset_elliott_hall_of_music','export_mesh_objects':sum(o.type=='MESH' for o in COL.objects),'export_total_objects':len(COL.objects),'footprint_vertices':N,'window_openings':len(window_specs),'door_openings':1,'limestone_course_elevations_m':[2.25,7.5,12.75,18.0,22.35],'flytower_top_m':33.15,'roof_elevation_m':22.5,'known_uncertainty':'Exterior window rhythm, entry position, sculpture form and flytower dimensions are inferred; no dimensioned elevation was retrieved. The public footprint ring remains the authoritative GIS shape.'}
(AUD/'exterior_pass_result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
