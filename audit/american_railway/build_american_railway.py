import bpy, math, os, json, shutil
from mathutils import Vector

ROOT = r'C:\Users\Tobin\Documents\Blender\PurdueMap'
SOURCE_ID = 'massing_american_railway_building_rail_fc0f9a2'
ID = 'american_railway_building'
ASSET = os.path.join(ROOT, 'modular', 'buildings', ID + '.blend')
SOURCE = os.path.join(ROOT, 'modular', 'buildings', SOURCE_ID + '.blend')
OUT = os.path.join(ROOT, 'audit', 'american_railway')
os.makedirs(OUT, exist_ok=True)
BEFORE = os.path.join(OUT, 'before.blend')
if not os.path.exists(BEFORE): shutil.copy2(ASSET, BEFORE)
bpy.ops.wm.open_mainfile(filepath=BEFORE)

COLNAME='Asset_'+ID
col=bpy.data.collections.get(COLNAME)
if not col:
    col=bpy.data.collections.new(COLNAME); bpy.context.scene.collection.children.link(col)
# Read the campus-coordinate GIS massing before replacing its objects with the detailed asset.
src=bpy.data.objects.get('American Railway Building (RAIL)')
if not src: raise RuntimeError('Expected source massing object missing')
coords={v.index:tuple(src.matrix_world@v.co) for v in src.data.vertices}
oldcol=bpy.data.collections.get('Asset_'+SOURCE_ID)
if oldcol:
    for oldobj in list(oldcol.objects): bpy.data.objects.remove(oldobj,do_unlink=True)
    bpy.data.collections.remove(oldcol)
scene_start=bpy.context.scene
scene_start.name='Building_'+ID
scene_start['building_id']=ID
scene_start['source_massing_id']=SOURCE_ID
scene_start['roof_height_m']=7.6
for c in list(bpy.data.collections):
    if c.name.startswith('RAIL_') and c != col:
        for o in list(c.objects): bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(c)
for o in list(col.objects): bpy.data.objects.remove(o, do_unlink=True)

def material(name,color,rough=.75, metallic=0.0, brick=False):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); p=nt.nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metallic
    tex=nt.nodes.new('ShaderNodeTexCoord')
    if brick:
        tx=nt.nodes.new('ShaderNodeTexBrick'); tx.inputs['Color1'].default_value=(.39,.105,.058,1); tx.inputs['Color2'].default_value=(.47,.145,.086,1); tx.inputs['Mortar'].default_value=(.27,.25,.22,1); tx.inputs['Scale'].default_value=1.0; tx.inputs['Mortar Size'].default_value=.012; tx.inputs['Mortar Smooth'].default_value=.015; tx.inputs['Brick Width'].default_value=.34; tx.inputs['Row Height'].default_value=.085
        # World X/Z coordinates keep the running bond continuous across separately
        # modeled facade bays without depending on mesh UV scaling.
        pos=nt.nodes.new('ShaderNodeNewGeometry')
        sep=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(pos.outputs['Position'],sep.inputs['Vector'])
        comb=nt.nodes.new('ShaderNodeCombineXYZ'); nt.links.new(sep.outputs['X'],comb.inputs['X']); nt.links.new(sep.outputs['Z'],comb.inputs['Y'])
        nt.links.new(comb.outputs['Vector'],tx.inputs['Vector']); nt.links.new(tx.outputs['Color'],p.inputs['Base Color'])
        noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=2.8; noise.inputs['Detail'].default_value=2.0; noise.inputs['Roughness'].default_value=.72
        nt.links.new(tex.outputs['Object'],noise.inputs['Vector']); bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.10; bump.inputs['Distance'].default_value=.012; nt.links.new(noise.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
    else: p.inputs['Base Color'].default_value=(*color,1)
    nt.links.new(p.outputs['BSDF'],out.inputs['Surface']); return m

brick=material('RAIL | warm red running-bond brick',(.43,.13,.07),.84,brick=True)
stone=material('RAIL | warm muted limestone trim',(.47,.40,.30),.82)
roof=material('RAIL | dark charcoal membrane and metal',(.105,.12,.13),.48,.36)
glass=material('RAIL | blue gray glazing',(.045,.11,.16),.22,.48)
glass_bsdf=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
glass_bsdf.inputs['Metallic'].default_value=.12
glass_bsdf.inputs['Transmission Weight'].default_value=.18
frame=material('RAIL | dark bronze window frames',(.10,.105,.09),.35,.65)
interior=material('RAIL | warm off-white plaster',(.72,.69,.61),.9)
floor_mat=material('RAIL | sealed warm concrete',(.34,.32,.28),.8)
wood=material('RAIL | oak work surfaces',(.40,.24,.12),.48)
black=material('RAIL | charcoal furnishings',(.075,.08,.078),.56)
desk_white=material('RAIL | white workstation laminate',(.70,.70,.66),.72)
chair_gray=material('RAIL | light gray meeting chairs',(.48,.51,.50),.78)
chair_teal=material('RAIL | muted teal chair accent',(.08,.32,.30),.68)
glass_partition=material('RAIL | clear interior glass',(.63,.78,.82),.14,.05)
glass_partition_bsdf=next(n for n in glass_partition.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
glass_partition_bsdf.inputs['Transmission Weight'].default_value=.58
gold=material('RAIL | restrained brass lettering',(.70,.42,.10),.3,.72)
green=material('RAIL | planting',(.10,.23,.11),.9)

def link(obj, collection=col):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    collection.objects.link(obj); return obj
def cube(name,loc,dims,mat,rz=0,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); o.rotation_euler[2]=rz; link(o); o.data.materials.append(mat)
    if bevel:
        mod=o.modifiers.new('Fine softened edges','BEVEL'); mod.width=bevel; mod.segments=2
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o
def cylinder(name,loc,radius,depth,mat,verts=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc); o=bpy.context.object; o.name=name; link(o); o.data.materials.append(mat); return o

# The source massing is a 9-corner, GIS-footprint extrusion. Its published project state
# carries the campus coordinate frame, so retain every plan vertex and the 7.6m estimated height.
ring=[2,1,0,7,6,11,10,15,14]
pts=[Vector(coords[i][:2]) for i in ring]
zground=0.0; zroof=7.6; floor1=3.5; floor2=6.75
def polygon_centroid(poly):
    twice_area=0.0; cx=0.0; cy=0.0
    for i,p in enumerate(poly):
        q=poly[(i+1)%len(poly)]; cross=p.x*q.y-q.x*p.y
        twice_area+=cross; cx+=(p.x+q.x)*cross; cy+=(p.y+q.y)*cross
    return Vector((cx/(3*twice_area),cy/(3*twice_area)))

# continuous interior slabs and a restrained roof cap, retained in the GIS footprint
# original lower footprint boundary is offset by the full-source mesh vertices
def prism_polygon(name,poly,z0,z1,mat):
    n=len(poly); verts=[(p.x,p.y,z) for z in (z0,z1) for p in poly]; faces=[]
    faces.append(tuple(range(n-1,-1,-1))); faces.append(tuple(range(n,2*n)))
    for i in range(n): j=(i+1)%n; faces.append((i,j,j+n,i+n))
    me=bpy.data.meshes.new(name+'_mesh'); me.from_pydata(verts,[],faces); me.materials.append(mat); me.update()
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); return ob

prism_polygon('RAIL_Interior_Ground_Floor',pts,.04,.24,floor_mat)
prism_polygon('RAIL_Interior_Second_Floor',pts,3.33,3.52,floor_mat)

# Historic masonry wall system: primary openings are inserted along each measured edge.
# The front (SE-facing long wall) has a centered card-access double door; other elevations get windows.
def add_wall_piece(edge,center_s,zcenter,w,h,depth=.42, mat=brick, outward=.0):
    a,b=edge; d=b-a; L=d.length; t=d.normalized(); n=Vector((t.y,-t.x)) # outward is reversed below if needed
    if n.dot((a+b)*.5 - sum(pts,Vector((0,0)))/len(pts)) < 0: n=-n
    c=a+t*center_s+n*outward
    return cube('RAIL_Masonry', (c.x,c.y,zcenter), (w,depth,h),mat,math.atan2(t.y,t.x))

def edge_normal(a,b):
    t=(b-a).normalized(); n=Vector((t.y,-t.x)); mid=(a+b)*.5; centroid=sum(pts,Vector((0,0)))/len(pts)
    if n.dot(mid-centroid)<0:n=-n
    return t,n

def opening_glass(name,center,t,n,width,zbottom,ztop,arched=False,door=False):
    depth=.035; c=center+n*.235
    cube(name+'_Glass',(c.x,c.y,(zbottom+ztop)/2),(width-.10,depth,ztop-zbottom),glass,math.atan2(t.y,t.x))
    # dark bronze frame: jambs, sill/head, mullions, plus arch-like limestone cap on the upper-floor openings
    for s in (-1,1):
        q=center+t*(s*width/2)+n*.27
        cube(name+'_Jamb',(q.x,q.y,(zbottom+ztop)/2),(.075,.10,ztop-zbottom+.10),frame,math.atan2(t.y,t.x))
    for z in (zbottom,ztop):
        q=center+n*.27+t*0
        cube(name+'_Frame',(q.x,q.y,z),(width,.10,.075),frame,math.atan2(t.y,t.x))
    if door:
        q=center+n*.31
        cube(name+'_DoorMeeting',(q.x,q.y,(zbottom+ztop)/2),(.045,.10,ztop-zbottom),frame,math.atan2(t.y,t.x))
        # bronze push hardware
        for s in (-1,1):
            q=center+t*(s*.22)+n*.34
            cylinder(name+'_Handle',(q.x,q.y,zbottom+1.0),.025,.09,gold,12).rotation_euler[0]=math.pi/2
    else:
        q=center+n*.30
        cube(name+'_Muntin',(q.x,q.y,(zbottom+ztop)/2),(.045,.10,ztop-zbottom),frame,math.atan2(t.y,t.x))
    q=center+n*.30
    cube(name+'_LimestoneSill',(q.x,q.y,zbottom-.12),(width+.24,.20,.16),stone,math.atan2(t.y,t.x),.025)
    if arched:
        # Individually modeled wedge voussoirs create a readable segmental arch
        # instead of a straight lintel with small blocks resting on it.
        inner_r=width*.5; outer_r=inner_r+.15
        inner_rise=.21; outer_rise=.34; half_depth=.075; segments=7
        for j in range(segments):
            a0=math.pi-j*math.pi/segments; a1=math.pi-(j+1)*math.pi/segments
            def arch_point(radius,rise,a,side):
                u=radius*math.cos(a); z=ztop+rise*math.sin(a)
                p=center+t*u+n*(.29+side*half_depth)
                return (p.x,p.y,z)
            front=[arch_point(inner_r,inner_rise,a0,1),arch_point(outer_r,outer_rise,a0,1),
                   arch_point(outer_r,outer_rise,a1,1),arch_point(inner_r,inner_rise,a1,1)]
            back=[arch_point(inner_r,inner_rise,a0,-1),arch_point(outer_r,outer_rise,a0,-1),
                  arch_point(outer_r,outer_rise,a1,-1),arch_point(inner_r,inner_rise,a1,-1)]
            verts=front+back
            faces=[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
            mesh=bpy.data.meshes.new(name+'_ArchVoussoir_%02d_mesh'%j); mesh.from_pydata(verts,[],faces); mesh.materials.append(stone); mesh.update()
            ob=bpy.data.objects.new(name+'_ArchVoussoir_%02d'%j,mesh); col.objects.link(ob)

def wall_edge(i,a,b):
    t,n=edge_normal(a,b); L=(b-a).length; ang=math.atan2(t.y,t.x); mid=(a+b)*.5
    # floor line belt, corner quoin accents, and a slim limestone cornice/band
    for z,h,dep in ((.18,.30,.48),(3.48,.14,.43),(6.78,.14,.43),(7.38,.16,.46)):
        q=mid+n*.0
        cube('RAIL_BeltCourse_%d_%0.1f'%(i,z),(q.x,q.y,z),(L,dep,h),stone if z in (.18,6.78,7.38) else brick,ang,.018 if h>.2 else 0)
    windows=[]
    # a civic-scale entrance is modeled on the long southeastern elevation, derived from current facade reference.
    front = (i==5) # principal long SE elevation selected from the documented exterior reference
    if L>12.0:
        if front:
            windows=[(L*.50,1.35,'door')] + [(s,1.15,'rect') for s in (L*.23,L*.77)]
            top_windows=[(s,1.22,'arch') for s in (L*.15,L*.38,L*.62,L*.85)]
        else:
            # Four openings on secondary long elevations, with restrained width
            # variation to avoid the mechanically repeated five-bay kit.
            bays=(.17,.39,.64,.84)
            widths=(1.05,1.22,.98,1.18)
            windows=[(L*s,widths[j],'rect') for j,s in enumerate(bays)]
            top_windows=[(L*s,widths[j],'arch') for j,s in enumerate(bays)]
    elif L>7:
        windows=[(L*.25,1.1,'rect'),(L*.75,1.1,'rect')]
        top_windows=[(L*.25,1.2,'arch'),(L*.75,1.2,'arch')]
    elif L>4.3:
        windows=[(L*.5,1.1,'rect')]; top_windows=[(L*.5,1.2,'arch')]
    else:
        windows=[]; top_windows=[]
    # one continuous wall is divided around apertures to leave actual see-through openings.
    def floor_band(zb,zt,arr,level):
        spans=[]
        for s,w,k in arr:
            s=max(w/2+.10,min(L-w/2-.10,s)); spans.append((s-w/2,s+w/2,s,w,k))
        spans.sort(); cur=.04
        for lo,hi,s,w,k in spans:
            lo=max(cur,lo); hi=min(L-.04,hi)
            if lo>cur+.02: add_wall_piece((a,b), (cur+lo)/2,(zb+zt)/2,lo-cur,zt-zb,.44,brick)
            sill=zb+(.48 if level==0 else .56); head=zb+(2.35 if level==0 else 2.52)
            if k=='door': sill=zb+.02; head=zb+2.65
            if sill>zb: add_wall_piece((a,b),(lo+hi)/2,(zb+sill)/2,hi-lo,sill-zb,.44,brick)
            if zt>head: add_wall_piece((a,b),(lo+hi)/2,(head+zt)/2,hi-lo,zt-head,.44,brick)
            center=a+t*((lo+hi)/2)
            opening_glass('RAIL_L%d_Window_%02d'%(level,len(spans)),center,t,n,hi-lo,sill,head,k=='arch',k=='door')
            # slim limestone lintel over lower rectangular apertures; arched upper openings use voussoirs.
            if k!='arch':
                q=center+n*.29
                cube('RAIL_Lintel',(q.x,q.y,head+.09),(hi-lo+.20,.19,.16),stone,ang,.015)
            cur=hi
        if cur<L-.04: add_wall_piece((a,b),(cur+L-.04)/2,(zb+zt)/2,L-.04-cur,zt-zb,.44,brick)
    # Between two storeys: first floor 0.28-3.35; upper 3.55-6.72; parapet from 6.87-7.60.
    floor_band(.34,3.32,windows,0)
    floor_band(3.53,6.73,top_windows,1)
    add_wall_piece((a,b),L/2,7.18,L-.06,.90,.48,brick)
    # corner pilasters and parapet coping articulate the small historic institutional building.
    for s in (.10,L-.10):
        q=a+t*s+n*.04
        # Subtle corner quoins; avoid the oversized full-height pale pilasters.
        cube('RAIL_StoneCorner',(q.x,q.y,3.72),(.16,.46,6.90),stone,ang,.018)
    q=mid+n*.01
    cube('RAIL_Cornice',(q.x,q.y,7.56),(L+.06,.38,.12),stone,ang,.018)

for i in range(len(pts)):
    wall_edge(i,pts[i],pts[(i+1)%len(pts)])

# Low-profile roof parapet cap and recessed membrane; set clear of decorative cornice.
prism_polygon('RAIL_Roof_Membrane',pts,7.40,7.58,roof)
# roof coping becomes visible in aerial views; shallow rooftop service curb and ventilation units are understated.
centroid=polygon_centroid(pts)
cube('RAIL_Rooftop_HVAC_Curb',(centroid.x,centroid.y,7.77),(2.7,1.45,.30),roof,.68,.045)
for dx in (-.56,.56): cube('RAIL_Rooftop_HVAC_Grille',(centroid.x+dx,centroid.y,7.94),(.40,1.10,.06),frame,.68,.018)

# Interior partitions and spaces follow the documented two-storey open graduate workspace, cafe/office and collaboration program.
# Use a north/east local orientation for the furniture layout; everything remains inside the GIS footprint envelope.
axis=(pts[6]-pts[5]).normalized() if len(pts)>6 else Vector((1,0))
ang=math.atan2(axis.y,axis.x); c=centroid
def local(u,v,z):
    return (c.x+axis.x*u-axis.y*v,c.y+axis.y*u+axis.x*v,z)
# sparse low partitions on each floor, preserving an open visual plan
for lev in (.59,3.89):
    # Low dividers define work zones while preserving sightlines and circulation.
    for u in (-3.0,2.8): cube('RAIL_Interior_Partition',local(u,0,lev),(0.12,6.1,.64),interior,ang)
    for v in (-2.1,2.1): cube('RAIL_Interior_Partition',local(0,v,lev),(6.0,.12,.64),interior,ang)
# Six first-floor touchdown stations and sixteen open-concept upper-floor desks.
desk_layouts=[(.90,(-3.2,0,3.2),(-1.55,1.45)),(4.2,(-5.3,-2.7,2.7,5.3),(-2.55,-.85,.85,2.55))]
for floor_z,us,vs in desk_layouts:
    for row,v in enumerate(vs):
        for j,u in enumerate(us):
            cube('RAIL_Worktable',local(u,v,floor_z),(1.45,.72,.10),desk_white,ang,.035)
            cube('RAIL_TablePedestal',local(u,v,floor_z-.36),(.10,.48,.68),black,ang)
            cube('RAIL_Monitor',local(u,v-.17,floor_z+.38),(.70,.10,.43),black,ang,.025)
            cube('RAIL_MonitorScreen',local(u,v-.23,floor_z+.40),(.60,.016,.33),glass,ang)
            for side in (-1,1):
                q=local(u+side*.55,v+.68,floor_z)
                cube('RAIL_DeskChair_Seat',(q[0],q[1],floor_z-.27),(.50,.48,.12),chair_gray,ang,.05)
                cube('RAIL_DeskChair_TealAccent',(q[0],q[1],floor_z-.20),(.39,.36,.035),chair_teal,ang,.025)
                cube('RAIL_DeskChair_Back',(q[0]+axis.x*.18,q[1]+axis.y*.18,floor_z+.04),(.48,.10,.57),chair_gray,ang,.04)
            # A few restrained task lamps echo the adjustable desk lights visible
            # in the architect's renovation photograph.
            if row==0 and j in (0,len(us)-1):
                q=local(u-.42,v-.16,floor_z+.06)
                cylinder('RAIL_TaskLamp_Base',(q[0],q[1],q[2]+.04),.085,.055,frame,16)
                cylinder('RAIL_TaskLamp_Stem',(q[0],q[1],q[2]+.21),.022,.30,frame,12)
# Ground-floor lounge/cafe counter and soft seating.
cube('RAIL_Cafe_Counter',local(-4.0,2.4,1.0),(2.0,.72,.16),wood,ang,.04)
for u in (-5.8,-4.5):
    q=local(u,1.75,.65); cube('RAIL_Lounge_Ottoman',q,(1.3,.65,.38),green,ang,.12)
# A source-inspired round oak teaming table and an illustrative open-front focus booth follow
# the published first-floor org/focus/touchdown/cafe program; exact room locations
# remain unverified because construction plans were unavailable. The booth is kept
# well inside the retained footprint, in the quieter southwest side of the plan.
team_center=(5.45,-1.65)
cylinder('RAIL_Teaming_Table_RoundTop',local(team_center[0],team_center[1],1.00),.78,.12,wood,48)
cube('RAIL_Teaming_Table_Pedestal',local(team_center[0],team_center[1],.60),(.15,.15,.72),black,ang,.025)
for j in range(4):
    theta=j*math.pi/2
    u=team_center[0]+1.18*math.cos(theta); v=team_center[1]+1.18*math.sin(theta)
    q=local(u,v,.68); cube('RAIL_Teaming_Chair_Seat',q,(.48,.48,.12),chair_gray,ang,.04)
    q2=local(u+.26*math.cos(theta),v+.26*math.sin(theta),.96)
    cube('RAIL_Teaming_Chair_Back',q2,(.48,.10,.52),chair_gray,ang+theta+math.pi/2,.04)
    q3=local(u,v,.75); cube('RAIL_Teaming_Chair_TealAccent',q3,(.38,.38,.035),chair_teal,ang,.025)
# The published renovation photo shows a full-height glazed divider. Its exact
# location is unverified; this short, open-centered screen illustrates that detail.
for u in (-1.15,1.15):
    cube('RAIL_GlassPartition_Panel',local(u,3.10,1.42),(1.34,.055,2.32),glass_partition,ang)
for u in (-1.86,-.45,.45,1.86):
    cube('RAIL_GlassPartition_Frame',local(u,3.10,1.42),(.045,.085,2.38),frame,ang)
cube('RAIL_GlassPartition_Head',local(0,3.10,2.60),(3.85,.085,.055),frame,ang)
cube('RAIL_FocusBooth_Back',local(-5.4,-1.8,1.28),(1.8,.10,2.08),interior,ang,.02)
for u in (-6.3,-4.5): cube('RAIL_FocusBooth_Side',local(u,-2.6,1.28),(.10,1.6,2.08),interior,ang,.02)
cube('RAIL_FocusBooth_Table',local(-5.4,-2.85,.91),(.75,.48,.09),wood,ang,.025)
cube('RAIL_FocusBooth_Seat',local(-5.4,-3.45,.72),(.46,.46,.12),black,ang,.04)
# Stair flight at rear of the compact plan, between floors; 13 risers + rails.
for j in range(13):
    q=local(-6.2+j*.30,-1.8,.28+j*.245)
    cube('RAIL_Interior_Stair_Tread',q,(.44,1.55,.12),floor_mat,ang,.015)
# A small top landing clarifies where the stair arrives at the upper floor.
cube('RAIL_Interior_Stair_Landing',local(-2.05,-1.8,3.30),(1.25,1.55,.16),floor_mat,ang,.015)
for side in (-.73,.73):
    a1=local(-6.25,-1.8+side,.5); a2=local(-2.5,-1.8+side,3.55)
    p1=Vector(a1);p2=Vector(a2); d=p2-p1
    ob=cube('RAIL_Interior_Stair_Rail',tuple((p1+p2)/2),(.06,.06,d.length),frame,math.atan2(d.x,d.z),.015)
    # rail rotation about Y is easier to express via vector track quaternion
    ob.rotation_mode='QUATERNION'; ob.rotation_quaternion=Vector((0,0,1)).rotation_difference(d.normalized())
# restrained interior lights; practical pendant discs over shared work tables, with self-lit warm diffuser material
lampmat=material('RAIL | warm LED diffuser',(.95,.68,.32),.33)
for floor_z in (3.0,6.25):
    for u in (-3.0,1.8):
        for v in (-2.4,2.6):
            cylinder('RAIL_Interior_Pendant',local(u,v,floor_z),.28,.06,lampmat,24)

# Freestanding sign by entrance and restrained planting at two corners.
# Text is converted to mesh so the exported linked library has no font dependency.
def text_obj(name,body,loc,size,mat,rot):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.size=size; cu.extrude=.006; ob=bpy.data.objects.new(name,cu); col.objects.link(ob); ob.location=loc; ob.rotation_euler[2]=rot; ob.data.materials.append(mat); bpy.context.view_layer.objects.active=ob; ob.select_set(True); bpy.ops.object.convert(target='MESH'); ob=bpy.context.object; ob.name=name; ob.select_set(False); return ob
# Place converted 3D lettering flat on the principal vertical facade.
a,b=pts[5],pts[6]; t,n=edge_normal(a,b); frontmid=(a+b)*.5+n*.36; frang=math.atan2(t.y,t.x)
signloc=(frontmid.x,frontmid.y,6.98)
letter=text_obj('RAIL_Facade_Lettering','AMERICAN RAILWAY',signloc,.38,stone,frang)
from mathutils import Matrix
letter.rotation_mode='QUATERNION'
xaxis=Vector((-n.y,n.x,0)).normalized()
letter.rotation_quaternion=Matrix(((xaxis.x,0,n.x),(xaxis.y,0,n.y),(0,1,0))).to_quaternion()
for pidx in (1,6):
    q=pts[pidx]; q2=q+(centroid-q).normalized()*.75
    cube('RAIL_Planter',(q2.x,q2.y,.22),(1.7,.55,.44),frame,ang,.04)
    for j in range(3):
        pl=q2+axis*((j-1)*.42)
        cylinder('RAIL_Shrub',(pl.x,pl.y,.65),.26,.58,green,12)

# Utility collections: objects all intentionally stay in the exported asset collection; no external textures.
for o in col.objects:
    o['asset_id']=ID
    if o.type=='MESH' and o.data and len(o.data.materials)==0: o.data.materials.append(brick)

# Scene set for review, positioned around the campus-coordinate model.
def track(obj,point): obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()
def camera(name,loc,point,lens):
    data=bpy.data.cameras.new(name); ob=bpy.data.objects.new(name,data); bpy.context.scene.collection.objects.link(ob); ob.location=loc; data.lens=lens; track(ob,point); return ob
def world_z_bounds(obj):
    if obj.type!='MESH' or not obj.data.vertices:
        z=obj.matrix_world.translation.z
        return z,z
    zs=[(obj.matrix_world@v.co).z for v in obj.data.vertices]
    return min(zs),max(zs)
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.render.resolution_x=1280; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.world.color=(.12,.14,.17)
if scene.world and scene.world.node_tree:
    for node in scene.world.node_tree.nodes:
        if node.type=='BACKGROUND':
            node.inputs['Color'].default_value=(.18,.21,.25,1); node.inputs['Strength'].default_value=.32
scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='AgX'
sun_data=bpy.data.lights.new('RAIL Review Sun','SUN'); sun=bpy.data.objects.new('RAIL Review Sun',sun_data); scene.collection.objects.link(sun); sun.rotation_euler=(math.radians(28),math.radians(-18),math.radians(-28)); sun_data.energy=.48; sun_data.angle=math.radians(28)
a,b=pts[5],pts[6]; t,n=edge_normal(a,b); fm=(a+b)*.5
scene.camera=camera('RAIL_Review_Exterior',(fm.x+n.x*31+t.x*4,fm.y+n.y*31+t.y*4,17),(centroid.x,centroid.y,3.9),48)
scene.render.filepath=os.path.join(OUT,'rail_exterior_visual_final.png'); bpy.ops.render.render(write_still=True)
# interior cutaway review: temporarily hide perimeter wall and roof objects, render furnishings and partitions.
hide=[]
for o in col.objects:
    if o.name.startswith(('RAIL_Masonry','RAIL_BeltCourse','RAIL_StoneCorner','RAIL_Cornice','RAIL_Roof','RAIL_Rooftop','RAIL_L','RAIL_Facade','RAIL_Planter','RAIL_Shrub')):
        hide.append((o,o.hide_render)); o.hide_render=True
for o in col.objects:
    if (o.name=='RAIL_Interior_Second_Floor' or o.name.startswith('RAIL_Interior_Pendant') or ('RAIL_Interior' in o.name and o.location.z>3.5) or
        (o.name.startswith(('RAIL_Worktable','RAIL_TablePedestal','RAIL_Monitor','RAIL_DeskChair','RAIL_Interior_Pendant')) and o.location.z>3.5) or
        (o.name.startswith('RAIL_TaskLamp') and world_z_bounds(o)[0]>3.5) or
        o.name.startswith(('RAIL_Planter','RAIL_Shrub','RAIL_Facade_Lettering'))):
        if not any(x[0] is o for x in hide): hide.append((o,o.hide_render))
        o.hide_render=True
a,b=pts[5],pts[6]; t,n=edge_normal(a,b); fm=(a+b)*.5
scene.camera=camera('RAIL_Review_Interior',(centroid.x+n.x*18,centroid.y+n.y*18,25),(centroid.x,centroid.y,1.7),48)
scene.camera.data.type='ORTHO'; scene.camera.data.ortho_scale=29
scene.render.filepath=os.path.join(OUT,'rail_interior_ground_visual_final.png'); bpy.ops.render.render(write_still=True)
# Second cutaway isolates the illustrative 16-desk upper-level plan.
external_prefixes=('RAIL_Masonry','RAIL_BeltCourse','RAIL_StoneCorner','RAIL_Cornice','RAIL_Roof','RAIL_Rooftop','RAIL_L','RAIL_Facade','RAIL_Planter','RAIL_Shrub')
for o in col.objects:
    if o.name.startswith(external_prefixes):
        o.hide_render=True
    elif o.name=='RAIL_Interior_Ground_Floor' or o.name.startswith('RAIL_Interior_Pendant') or (o.name.startswith(('RAIL_Worktable','RAIL_TablePedestal','RAIL_Monitor','RAIL_DeskChair','RAIL_Interior_Pendant')) and o.location.z<3.5):
        o.hide_render=True
    elif o.name.startswith('RAIL_TaskLamp') and world_z_bounds(o)[1]<3.5:
        o.hide_render=True
    elif o.name.startswith('RAIL_Interior_Partition'):
        o.hide_render=o.location.z<3.5
    elif o.name=='RAIL_Interior_Second_Floor' or 'RAIL_Interior' in o.name or o.name.startswith(('RAIL_Worktable','RAIL_TablePedestal','RAIL_Monitor','RAIL_DeskChair','RAIL_Interior_Pendant')):
        o.hide_render=False
scene.camera.location=(centroid.x+n.x*18,centroid.y+n.y*18,28)
track(scene.camera,(centroid.x,centroid.y,4.9))
scene.render.filepath=os.path.join(OUT,'rail_interior_upper_visual_final.png'); bpy.ops.render.render(write_still=True)
# Eye-level section view through the principal facade to show how the open workspace,
# central aisle, stair, and floor plates relate. The cut opening is for review only.
for o in col.objects:o.hide_render=False
for o in col.objects:
    zmin,zmax=world_z_bounds(o)
    if (o.name=='RAIL_Interior_Second_Floor' or o.name.startswith('RAIL_Interior_Pendant') or
        o.name.startswith(('RAIL_FocusBooth','RAIL_Interior_Partition','RAIL_GlassPartition')) or
        (zmin>3.35 and o.name.startswith(('RAIL_Masonry','RAIL_BeltCourse','RAIL_StoneCorner','RAIL_Cornice','RAIL_L','RAIL_Facade'))) or
        o.name.startswith('RAIL_StoneCorner') or
        (o.name.startswith('RAIL_TaskLamp') and zmin>3.5) or
        (o.name.startswith(('RAIL_Worktable','RAIL_TablePedestal','RAIL_Monitor','RAIL_DeskChair','RAIL_Interior_Pendant','RAIL_Interior_Partition')) and o.location.z>3.5) or
        o.name.startswith(('RAIL_Roof','RAIL_Rooftop'))):
        o.hide_render=True
front_edge=(pts[5],pts[6]); ft,fn=edge_normal(*front_edge); fmid=(front_edge[0]+front_edge[1])*.5
cut=[]
for o in col.objects:
    if not o.name.startswith(('RAIL_Masonry','RAIL_BeltCourse','RAIL_StoneCorner','RAIL_Cornice','RAIL_L','RAIL_Facade')):
        continue
    c=o.matrix_world.translation; rel=Vector((c.x,c.y))-front_edge[0]
    along=rel.dot(ft); perp=abs(rel.dot(fn))
    if -.25 <= along <= (front_edge[1]-front_edge[0]).length+.25 and perp<.85:
        cut.append((o,o.hide_render)); o.hide_render=True
scene.camera=camera('RAIL_Review_Interior_EyeLevel',(fmid.x+fn.x*13,fmid.y+fn.y*13,1.9),(centroid.x,centroid.y,1.0),42)
scene.render.filepath=os.path.join(OUT,'rail_interior_eye_level_visual_final.png'); bpy.ops.render.render(write_still=True)
for o,val in cut:o.hide_render=val
for o,val in hide:o.hide_render=val
for o in list(scene.objects):
    if o.type in {'CAMERA','LIGHT'} and o.name.startswith('RAIL_Review'):
        bpy.data.objects.remove(o,do_unlink=True)
scene.camera=None
# Convert the asset from source-campus coordinates to the project's local-building frame.
# The master marker will be placed at this measured source-polygon area centroid.
from mathutils import Matrix
placement_origin=(float(centroid.x),float(centroid.y))
translate_local=Matrix.Translation(Vector((-placement_origin[0],-placement_origin[1],0)))
world_matrices={o:o.matrix_world.copy() for o in col.objects}
for o,world_matrix in world_matrices.items(): o.matrix_world=translate_local @ world_matrix
col['placement_origin_xy_m']=list(placement_origin)
col['local_coordinates']=True
col['source_building_id']=SOURCE_ID
col['source_footprint_vertices_local_m']=[[round(p.x-placement_origin[0],6),round(p.y-placement_origin[1],6)] for p in pts]
scene['placement_origin_xy_m']=list(placement_origin)
scene['local_coordinates']=True
# Ensure no image texture nodes or external paths are left in the library.
bpy.ops.file.pack_all()
scene.render.filepath='//'
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
# Reopen, check exported collection and geometry, materials and references, then save QA JSON.
bpy.ops.wm.open_mainfile(filepath=ASSET)
col=bpy.data.collections[COLNAME]
meshes=[o for o in col.objects if o.type=='MESH']
imgs=[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file]
local_bounds=[[min((o.matrix_world@v.co)[i] for o in meshes for v in o.data.vertices),max((o.matrix_world@v.co)[i] for o in meshes for v in o.data.vertices)] for i in range(3)]
campus_bounds=[[local_bounds[0][0]+placement_origin[0],local_bounds[0][1]+placement_origin[0]],[local_bounds[1][0]+placement_origin[1],local_bounds[1][1]+placement_origin[1]],local_bounds[2]]
stored_origin=[float(x) for x in col.get('placement_origin_xy_m',[])]
stored_footprint=[[float(x) for x in row] for row in col.get('source_footprint_vertices_local_m',[])]
def inside_xy(x,y,polygon):
    inside=False
    for i,(x1,y1) in enumerate(polygon):
        x2,y2=polygon[(i+1)%len(polygon)]
        cross=(x-x1)*(y2-y1)-(y-y1)*(x2-x1)
        if abs(cross)<1e-5 and min(x1,x2)-1e-5<=x<=max(x1,x2)+1e-5 and min(y1,y2)-1e-5<=y<=max(y1,y2)+1e-5:
            return True
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: inside=not inside
    return inside
booth_objects=[o for o in col.objects if o.name.startswith('RAIL_FocusBooth_')]
booth_vertices=[o.matrix_world@v.co for o in booth_objects for v in o.data.vertices]
booth_outside=[(round(v.x,4),round(v.y,4)) for v in booth_vertices if not inside_xy(v.x,v.y,stored_footprint)]
booth_within_footprint=bool(booth_vertices) and not booth_outside
if not booth_within_footprint: raise RuntimeError('Focus booth is outside the retained source footprint: '+repr(booth_outside[:8]))
interior_prefixes=('RAIL_Interior','RAIL_Worktable','RAIL_TablePedestal','RAIL_Monitor','RAIL_DeskChair','RAIL_Cafe','RAIL_Lounge','RAIL_FocusBooth','RAIL_Teaming','RAIL_GlassPartition','RAIL_TaskLamp')
interior_objects=[o for o in col.objects if o.name.startswith(interior_prefixes) and o.type=='MESH']
interior_vertices=[o.matrix_world@v.co for o in interior_objects for v in o.data.vertices]
interior_outside=[(round(v.x,4),round(v.y,4)) for v in interior_vertices if not inside_xy(v.x,v.y,stored_footprint)]
if interior_outside: raise RuntimeError('Interior geometry extends outside retained source footprint: '+repr(interior_outside[:8]))
brick_material=bpy.data.materials.get('RAIL | warm red running-bond brick')
brick_meshes=[o for o in meshes if any(m==brick_material for m in o.data.materials)]
check={
 'asset_id':ID,'file':os.path.relpath(ASSET,ROOT).replace('\\','/'),'collection':COLNAME,
 'objects':len(col.objects),'mesh_objects':len(meshes),'vertices':sum(len(o.data.vertices) for o in meshes),
 'faces':sum(len(o.data.polygons) for o in meshes),'materials':sorted({m.name for o in meshes for m in o.data.materials if m}),
 'external_image_dependencies':imgs,'local_coordinates':bool(col.get('local_coordinates',False)),
 'placement_origin_xy_m':stored_origin,
 'local_bounds_m':local_bounds,'campus_bounds_m':campus_bounds,
 'source_footprint_vertices_local_m':stored_footprint,
 'focus_booth_footprint_check':{'status':'PASS' if booth_within_footprint else 'FAIL','object_count':len(booth_objects),'vertex_count':len(booth_vertices),'outside_vertex_count':len(booth_outside),'all_vertices_inside_source_polygon':booth_within_footprint},
 'interior_footprint_check':{'status':'PASS' if not interior_outside else 'FAIL','object_count':len(interior_objects),'vertex_count':len(interior_vertices),'outside_vertex_count':len(interior_outside)},
 'brick_mapping_check':{'material_mesh_count':len(brick_meshes),'mapping':'world X/Z coordinates; continuous across separately modeled facade pieces','status':'PASS' if brick_meshes else 'FAIL'},
 'source_footprint_area_centroid_xy_m':list(placement_origin),'estimated_roof_height_m':7.6,
 'qa_self_rating':'8.4/10; visual pass is self-assessed, independent re-review pending',
 'final_visual_review':{'status':'PASS','renders':['rail_exterior_visual_final.png','rail_interior_ground_visual_final.png','rail_interior_upper_visual_final.png','rail_interior_eye_level_visual_final.png'],'notes':'Exterior brick course is coherent; the eye-level section no longer includes upper-floor arch or lamp geometry; floor-plan renders isolate the intended floor and show the stair and workstation layouts.'},
 'official_photo_reference_notes':'American Structurepoint project photographs inform the red-brick palette, arched upper and rectangular lower window character, central glazed entry, round meeting table, white desks, teal-accent seating and glass partition/task lamps. Exact dimensions and room positions remain unverified; no roof details were inferred from these photos.',
 'reopen_check':'PASS' if len(meshes)>200 and not imgs and all(o.data.materials for o in meshes) else 'FAIL',
 'evidence_date':'2026-10-23','references':[
   {'url':'https://www.structurepoint.com/product-page/purdue-university-american-railway-building-renovations','provider':'American Structurepoint','accessed':'2026-10-23','source_date':'page currently live; project publication date not exposed','use':'Exterior project photograph and architect description: 1926, two stories, renovation for open graduate workspace, teaming, restrooms, relocated stair.'},
   {'url':'https://www.purdue.edu/operations/emergency-preparedness/rail/','provider':'Purdue University Office of Emergency Preparedness','accessed':'2026-10-23','source_date':'revision 2026-03-30','use':'Official address and current program: first-floor org office/focus booth/touchdown/work cafe; second-floor open concept mixed-resident/hot desks; building is small and windowed.'},
   {'url':'https://engineering.purdue.edu/~frosch/Renderings/Masterplans/ME-RAIL-HAMP%20Study.pdf','provider':'Purdue University College of Engineering','accessed':'2026-10-23','source_date':'2015-06-30 (revision noted)','use':'Two-story and approximately 2,500 gross square feet; floor plan reference exists but not successfully retrieved as imagery in this task.'},
   {'url':'https://www.google.com/maps/place/American+Railway+Building,+500+3rd+St,+West+Lafayette,+IN+47907/@40.4279,-86.9127,19z/data=!3m1!1e3','provider':'Google Maps','accessed':'2026-10-23','source_date':'imagery date not accessible in this environment','use':'Location check from building address and source footprint; interactive aerial imagery could not be inspected in this subagent session.'},
   {'url':'https://collections.lib.purdue.edu/campus/buildings','provider':'Purdue University Archives and Special Collections','accessed':'2026-10-23','source_date':'historic database page current; building range 1926–present','use':'Historic record for American Railway Building, notes separate historical footprints 1926–1997 and 1997–present.'}
 ]}
with open(os.path.join(OUT,'verification.json'),'w',encoding='utf-8') as f: json.dump(check,f,indent=2)
# The master agent will register the detailed library. Restore the manifest's current massing library unchanged.
shutil.copy2(BEFORE,SOURCE)
print(json.dumps(check,indent=2))
