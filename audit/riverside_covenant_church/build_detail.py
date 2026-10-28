"""Source-led rebuild for the existing Riverside Covenant Church asset.

The project footprint and asset identity are retained. Exterior details are based on
Riverside's 2016 entrance photograph and the architect's 2022 exterior/interior work.
Unpublished dimensions and floor-plan details remain explicit estimates.
"""
import bpy, bmesh, json, math, os
from mathutils import Vector

HERE=os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE,'build_config.json'),encoding='utf-8') as f: cfg=json.load(f)
with open(os.path.join(HERE,'source_mesh_snapshot.json'),encoding='utf-8') as f: snap=json.load(f)
obj=bpy.data.objects.get(cfg['object_name']); coll=bpy.data.collections.get(cfg['collection_name'])
if not bpy.data.filepath or obj is None or coll is None or len(coll.objects)!=1 or obj not in coll.objects[:]:
    raise RuntimeError('Riverside collection identity mismatch; refusing to edit')

# Preserve the original four OSM corners exactly as the wall-floor ring. The source is
# OSM way/860918859; a state lidar footprint is independently recorded in the audit.
old=obj.data; world=obj.matrix_world.copy(); inv=world.inverted_safe()
ring=[]
for raw in snap['vertices_local']:
    p=Vector(raw)
    if abs(p.z)<1e-6:
        q=world@p
        if not any((q-v).length<1e-5 for v in ring): ring.append(q)
if len(ring)!=4: raise RuntimeError(f'Expected 4 footprint corners, found {len(ring)}')
end_a=(ring[0]+ring[1])*.5; end_b=(ring[2]+ring[3])*.5
axis=Vector((end_b.x-end_a.x,end_b.y-end_a.y,0)).normalized()
center=sum(ring,Vector((0,0,0)))/4
cross=Vector((-axis.y,axis.x,0))
if cross.dot((ring[1]+ring[2])*.5-center)<0: cross.negate()
length=abs((end_b-end_a).dot(axis))
width=abs(((ring[1]+ring[2])*.5-(ring[0]+ring[3])*.5).dot(cross))
x0=-length/2; x1=length/2; y0=-width/2; y1=width/2
eaves=float(cfg['wall_eaves_m']); ridge=float(cfg['main_roof_ridge_m'])
gableridge=float(cfg['stained_glass_gable_ridge_m'])
overhang=float(cfg['roof_overhang_m']); wall_t=.28
if not (0<eaves<ridge<gableridge and length>width>0): raise RuntimeError('Invalid source-backed dimensions')

tag=cfg['asset_id']
def mat(name,color,rough=.75,metal=0.0,brick=False):
    m=bpy.data.materials.get(tag+'_'+name) or bpy.data.materials.new(tag+'_'+name)
    m.diffuse_color=(*color,1); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); bs=nt.nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    coord=nt.nodes.new('ShaderNodeTexCoord')
    if brick:
        tex=nt.nodes.new('ShaderNodeTexBrick'); tex.inputs['Scale'].default_value=2.8
        tex.inputs['Color1'].default_value=(.39,.17,.09,1); tex.inputs['Color2'].default_value=(.23,.082,.045,1)
        tex.inputs['Mortar'].default_value=(.34,.29,.23,1); tex.inputs['Mortar Size'].default_value=.035
        tex.inputs['Mortar Smooth'].default_value=.08; tex.inputs['Brick Width'].default_value=.5; tex.inputs['Row Height'].default_value=.24
        nt.links.new(coord.outputs['Object'],tex.inputs['Vector']); nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.18; bump.inputs['Distance'].default_value=.025
        nt.links.new(tex.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    else:
        noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=9.0; noise.inputs['Detail'].default_value=3.0
        ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(*(v*.78 for v in color),1); ramp.color_ramp.elements[1].color=(*(min(.98,v*1.18+.025) for v in color),1)
        nt.links.new(coord.outputs['Object'],noise.inputs['Vector']); nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.12; bump.inputs['Distance'].default_value=.018
        nt.links.new(noise.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return m

M={
 'brick':mat('Exterior_Red_Brown_Brick',(.31,.13,.075),brick=True),
 'mortar':mat('Mortar_And_Limestone',(.48,.42,.34),.88),
 'stone':mat('Entry_Limestone_Ashlar',(.34,.29,.22),.9),
 'glass':mat('Smoky_Blue_Glazing',(.035,.10,.14),.22,.15),
 'glassamber':mat('Stained_Glass_Warm',(.76,.28,.045),.28,.03),
 'glassblue':mat('Stained_Glass_Blue',(.06,.27,.48),.28,.04),
 'glassred':mat('Stained_Glass_Red',(.55,.07,.04),.3,.03),
 'glassgold':mat('Stained_Glass_Gold',(.95,.57,.10),.28,.02),
 'frame':mat('Dark_Bronze_Window_Frames',(.075,.065,.055),.4,.55),
 'roof':mat('Charcoal_Architectural_Shingle',(.035,.04,.045),.88),
 'rooftrim':mat('Dark_Metal_Canopies',(.025,.03,.035),.48,.55),
 'wood':mat('Warm_Oak',(.39,.22,.095),.7),
 'floorwood':mat('Lobby_Maple_Floor',(.57,.37,.17),.68),
 'carpet':mat('Sanctuary_Charcoal_Carpet',(.09,.105,.105),.92),
 'wall':mat('Interior_Warm_White',(.72,.69,.61),.9),
 'upholstery':mat('Sanctuary_Taupe_Upholstery',(.30,.24,.19),.85),
 'seatdark':mat('Chair_Frame_Dark',(.055,.06,.057),.45,.35),
 'metal':mat('Canopy_Soffit_Metal',(.30,.31,.30),.5,.45),
}
names=list(M); mids={k:i for i,k in enumerate(names)}; mats=[M[k] for k in names]
verts=[]; faces=[]; face_mats=[]
def P(x,y,z):
    # Bilinear interpolation follows the four imported OSM corners exactly, including
    # their tiny projection-induced non-parallelogram skew, while allowing offsets for
    # the roof/eaves and canopies beyond the wall base.
    u=(x-x0)/length; v=(y-y0)/width
    south=ring[0]*(1-u)+ring[3]*u
    north=ring[1]*(1-u)+ring[2]*u
    return south*(1-v)+north*v+Vector((0,0,z))
def face(points,material):
    start=len(verts); verts.extend(tuple(inv@Vector(p)) for p in points)
    faces.append(tuple(range(start,len(verts)))); face_mats.append(mids[material])
def oriented_box(c,u,v,su,sv,sz,material):
    c=Vector(c); u=Vector((u.x,u.y,0)).normalized(); v=Vector((v.x,v.y,0)).normalized(); z=Vector((0,0,1))
    a=u*su/2; b=v*sv/2; h=z*sz/2
    q=[c-a-b-h,c+a-b-h,c+a+b-h,c-a+b-h,c-a-b+h,c+a-b+h,c+a+b+h,c-a+b+h]
    for ids in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): face([q[i] for i in ids],material)
def box_xy(x,y,z,sx,sy,sz,material): oriented_box(P(x,y,z),axis,cross,sx,sy,sz,material)
def beam(a,b,diameter,material,depth=None):
    a,b=Vector(a),Vector(b); d=b-a; horiz=Vector((d.x,d.y,0))
    if horiz.length<1e-6: oriented_box((a+b)/2,axis,cross,diameter,depth or diameter,d.length,material); return
    u=d.normalized(); side=Vector((-horiz.y,horiz.x,0)).normalized()
    # A slender four-sided member along an arbitrary 3D beam.
    w=side*diameter/2; vertical=u.cross(side).normalized()*(depth or diameter)/2
    q=[a-w-vertical,a+w-vertical,a+w+vertical,a-w+vertical,b-w-vertical,b+w-vertical,b+w+vertical,b-w+vertical]
    for ids in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): face([q[i] for i in ids],material)
def prism_x(x,outline_yz,material):
    # Surface polygon in the end-wall plane, at project-local x along the long axis.
    face([P(x,y,z) for y,z in outline_yz],material)

# Long walls use cut-outs instead of pasted-on windows; corresponding inner surfaces
# leave a real wall thickness and let the documented entry/interior read through.
def long_wall(y,inside_y,openings,outer_material='brick'):
    xs=sorted(set([x0,x1]+[max(x0,min(x1,c-w/2)) for c,w,z0,z1,k in openings]+[max(x0,min(x1,c+w/2)) for c,w,z0,z1,k in openings]))
    zs=sorted(set([0.0,eaves]+[z for c,w,z0,z1,k in openings for z in (z0,z1)]))
    for yy,mi in ((y,outer_material),(inside_y,'wall')):
        for ix in range(len(xs)-1):
            for iz in range(len(zs)-1):
                xm=(xs[ix]+xs[ix+1])/2; zm=(zs[iz]+zs[iz+1])/2
                if any(abs(xm-c)<w/2-1e-5 and z0-1e-5<zm<z1+1e-5 for c,w,z0,z1,k in openings): continue
                face([P(xs[ix],yy,zs[iz]),P(xs[ix+1],yy,zs[iz]),P(xs[ix+1],yy,zs[iz+1]),P(xs[ix],yy,zs[iz+1])],mi)
    for c,w,z0,z1,k in openings:
        if k=='window':
            inset=P(c,(y+inside_y)/2,z0+(z1-z0)/2); oriented_box(inset,axis,cross,w*.9,.10,z1-z0-.06,'glass')
            # Dark bronze perimeter and two vertical / one horizontal muntins.
            fy=(y+inside_y)/2
            oriented_box(P(c-w/2-.045,fy,(z0+z1)/2),cross,Vector((0,0,1)),.10,.09,z1-z0,'frame')
            oriented_box(P(c+w/2+.045,fy,(z0+z1)/2),cross,Vector((0,0,1)),.10,.09,z1-z0,'frame')
            oriented_box(P(c,fy,z0+.04),axis,cross,w+.18,.12,.08,'mortar')
            oriented_box(P(c,fy,z1-.04),axis,cross,w+.18,.12,.08,'frame')
            for dx in (-w*.22,w*.22): oriented_box(P(c+dx,fy,(z0+z1)/2),cross,Vector((0,0,1)),.06,.09,z1-z0-.08,'frame')
            oriented_box(P(c,fy,(z0+z1)/2),axis,cross,w,.08,.055,'frame')
        else:
            fy=(y+inside_y)/2
            oriented_box(P(c,fy,z0+(z1-z0)/2),axis,cross,w*.92,.08,z1-z0-.04,'glass')
            oriented_box(P(c-w/2-.05,fy,(z0+z1)/2),cross,Vector((0,0,1)),.10,.11,z1-z0,'frame')
            oriented_box(P(c+w/2+.05,fy,(z0+z1)/2),cross,Vector((0,0,1)),.10,.11,z1-z0,'frame')
            for dx in (-w*.25,0,w*.25): oriented_box(P(c+dx,fy,(z0+z1)/2),cross,Vector((0,0,1)),.055,.10,z1-z0-.08,'frame')
            oriented_box(P(c,fy,z0+.04),axis,cross,w+.2,.12,.08,'frame')
            oriented_box(P(c,fy,z1-.04),axis,cross,w+.2,.12,.08,'frame')

# South facade: documented 2022 entry canopies, columns, entry glass, and side windows.
# Their precise positions within the long wall are estimated from non-georeferenced photos.
main_doors=[(-7.4,1.45,.0,2.35,'door'),(-5.65,1.45,.0,2.35,'door'),(-3.9,1.45,.0,2.35,'door'),(-2.15,1.45,.0,2.35,'door')]
secondary=[(7.0,1.65,.0,2.35,'door'),(8.9,1.65,.0,2.35,'door')]
front_windows=[(-13.6,1.75,1.15,2.65,'window'),(13.2,1.75,1.15,2.65,'window')]
front_clerestory=[(c,1.10,3.35,4.18,'window') for c in (-12,-9,-6,-3,0,3,6,9,12)]
south_y=y0; south_inner=y0+wall_t
long_wall(south_y,south_inner,main_doors+secondary+front_windows+front_clerestory)
# North wall: repeated sanctuary/meeting-room windows, with upper clerestories.
back_openings=[(c,1.65,1.25,2.75,'window') for c in (-12.8,-8.5,-4.2,0,4.2,8.5,12.8)]
back_openings += [(c,1.15,3.45,4.18,'window') for c in (-10,-5,0,5,10)]
long_wall(y1,y1-wall_t,back_openings)

# Floor and interior finish zones. The exact full-building plan is not published; this
# uses the KJG photo-supported sanctuary-at-gable, lounge/cafe lobby and furniture forms.
floor_half=width/2-wall_t
face([P(x0+wall_t,-floor_half,.08),P(x1-wall_t,-floor_half,.08),P(x1-wall_t,floor_half,.08),P(x0+wall_t,floor_half,.08)],'floorwood')
sanct_x0=x0+1.0; sanct_x1=x0+18.0
face([P(sanct_x0,-floor_half+.25,.105),P(sanct_x1,-floor_half+.25,.105),P(sanct_x1,floor_half-.25,.105),P(sanct_x0,floor_half-.25,.105)],'carpet')
# Raised worship platform beneath the stained-glass end.
stage_cx=x0+2.4; stage_len=2.0; stage_w=width-2.2
oriented_box(P(stage_cx,0,.30),axis,cross,stage_len,stage_w,.44,'wood')
oriented_box(P(stage_cx-.38,0,.58),axis,cross,.68,1.0,.14,'wood')
oriented_box(P(stage_cx-.58,0,1.75),axis,cross,.16,.14,2.4,'wood')
oriented_box(P(stage_cx-.58,0,1.75),cross,axis,.14,1.15,.16,'wood')
# Seven simple chair rows, separated by a center aisle; scaled to the small sanctuary.
for row in range(7):
    x=sanct_x0+3.6+row*1.65
    for side in (-1,1):
        for j in range(3):
            y=side*(1.45+j*1.27)
            # upholstered seat and back, with four dark slender legs
            oriented_box(P(x,y,.62),axis,cross,.68,.68,.18,'upholstery')
            oriented_box(P(x-.28,y,.98),axis,cross,.12,.68,.72,'upholstery')
            for dx in (-.25,.25):
                for dy in (-.23,.23): box_xy(x+dx,y+dy,.30,.055,.055,.58,'seatdark')
# Sanctuary stage fittings / cross and lectern.
oriented_box(P(stage_cx-.65,-1.35,1.25),axis,cross,.35,.42,1.45,'wood')
oriented_box(P(stage_cx-.72,-1.35,2.02),axis,cross,.48,.42,.10,'wood')
# Front lobby/cafe on the east half: wood planks floor, dark rugs, coffee bar, tables, sofas.
lobby_x0=x0+18.5; lobby_x1=x1-1.0
for yy in (-2.2,2.2):
    face([P(lobby_x0,yy-1.75,.12),P(lobby_x1,yy-1.75,.12),P(lobby_x1,yy+1.75,.12),P(lobby_x0,yy+1.75,.12)],'carpet')
# Coffee bar against the north wall, countertop and back cabinet.
oriented_box(P(x1-3.2,1.95,1.0),axis,cross,5.2,.72,1.5,'wood')
oriented_box(P(x1-3.2,1.90,1.82),axis,cross,5.5,.86,.16,'floorwood')
oriented_box(P(x1-3.2,1.42,1.42),axis,cross,5.2,.08,.60,'frame')
# Lobby cafe tables with pedestal stems, chairs, lounge sofas and low tables.
for tx,ty in ((x1-8,-2.1),(x1-4.8,-2.1),(x1-8,2.2)):
    oriented_box(P(tx,ty,.92),axis,cross,1.35,.85,.10,'floorwood')
    box_xy(tx,ty,.54,.10,.10,.72,'seatdark')
    for dx in (-.45,.45):
        box_xy(tx+dx,ty-.65,.53,.42,.40,.48,'seatdark')
        box_xy(tx+dx,ty-.65,.84,.42,.32,.18,'upholstery')
for sx in (x1-13.0,x1-10.0):
    oriented_box(P(sx,-2.0,.70),axis,cross,2.3,.78,.40,'upholstery')
    oriented_box(P(sx,-2.0,1.00),axis,cross,2.3,.22,.82,'upholstery')
oriented_box(P(x1-11.4,-2.0,.42),axis,cross,1.25,.70,.14,'wood')

# Gable end walls and an A-frame stained-glass window. The exact bearing is unverified;
# this west-end orientation follows the compact OSM rectangle and the historic front photo.
def gable_end(x, high=False, glazed=False):
    peak=gableridge if high else ridge
    half=width/2
    # Main entry is below the west stained-glass gable in the 2016 entrance photo.
    # Its exact width/placement are estimated from that unscaled view.
    if glazed:
        door_half=3.15; door_top=2.42
        prism_x(x,[(y0,0),(-door_half,0),(-door_half,eaves),(y0,eaves)],'brick')
        prism_x(x,[(door_half,0),(y1,0),(y1,eaves),(door_half,eaves)],'brick')
        prism_x(x,[(-door_half,door_top),(door_half,door_top),(door_half,eaves),(-door_half,eaves)],'brick')
        # Four dark-framed glazed door leaves with paired stiles and top rail.
        oriented_box(P(x-.045,0,door_top/2),cross,axis,door_half*2,.09,door_top-.04,'glass')
        for yy in (-door_half-.06,-door_half/2,0,door_half/2,door_half+.06):
            oriented_box(P(x-.10,yy,door_top/2),cross,axis,.08,.12,door_top,'frame')
        oriented_box(P(x-.10,0,.08),cross,axis,door_half*2+.12,.14,.12,'frame')
        oriented_box(P(x-.10,0,door_top-.06),cross,axis,door_half*2+.12,.14,.12,'frame')
    else:
        prism_x(x,[(y0,0),(y1,0),(y1,eaves),(y0,eaves)],'brick')
    # upper gable is divided into horizontal courses; glass triangle replaces central wall.
    base=eaves+.04; glass_peak=peak-.24; glass_half=min(width*.38,4.55)
    rows=12
    for r in range(rows):
        zlo=eaves+(peak-eaves)*r/rows; zhi=eaves+(peak-eaves)*(r+1)/rows
        rooflo=half*(1-(zlo-eaves)/(peak-eaves)); roofhi=half*(1-(zhi-eaves)/(peak-eaves))
        if glazed and zhi>base and zlo<glass_peak:
            # Break the gable wall into outside shoulders around the inside triangle.
            def wh(z): return 0.0 if z>=glass_peak else glass_half*max(0,(glass_peak-z)/(glass_peak-base))
            gl0=wh(max(zlo,base)); gl1=wh(min(zhi,glass_peak))
            # before window base or above its point, fill whole roof triangle course
            if zhi<=base or zlo>=glass_peak:
                prism_x(x,[(-rooflo,zlo),(rooflo,zlo),(roofhi,zhi),(-roofhi,zhi)],'brick')
            else:
                if rooflo>gl0 or roofhi>gl1:
                    prism_x(x,[(-rooflo,zlo),(-gl0,zlo),(-gl1,zhi),(-roofhi,zhi)],'brick')
                    prism_x(x,[(gl0,zlo),(rooflo,zlo),(roofhi,zhi),(gl1,zhi)],'brick')
                # subdivide the colored window band into glass panels with bronze mullions
                ncol=8
                for col in range(ncol):
                    yl0=-gl0+2*gl0*col/ncol; yr0=-gl0+2*gl0*(col+1)/ncol
                    yl1=-gl1+2*gl1*col/ncol; yr1=-gl1+2*gl1*(col+1)/ncol
                    clr=('glassamber','glassblue','glassred','glassgold')[(col+r*3)%4]
                    prism_x(x-.012,[(yl0,zlo),(yr0,zlo),(yr1,zhi),(yl1,zhi)],clr)
                # horizontal transom and repeated thin vertical lead bars
                beam(P(x-.045,-gl0,zlo),P(x-.045,gl0,zlo),.065,'frame',.055)
                for col in range(ncol+1):
                    yy0=-gl0+2*gl0*col/ncol; yy1=-gl1+2*gl1*col/ncol
                    beam(P(x-.05,yy0,zlo),P(x-.05,yy1,zhi),.045,'frame',.045)
        else:
            prism_x(x,[(-rooflo,zlo),(rooflo,zlo),(roofhi,zhi),(-roofhi,zhi)],'brick')
    if glazed:
        # A-frame perimeter trim and a lower glazed strip below the large triangle.
        beam(P(x-.06,-glass_half,base),P(x-.06,0,glass_peak),.24,'mortar',.20)
        beam(P(x-.06,glass_half,base),P(x-.06,0,glass_peak),.24,'mortar',.20)
        beam(P(x-.06,-glass_half,base),P(x-.06,glass_half,base),.20,'mortar',.18)
        for yy in (-width*.32,width*.32):
            oriented_box(P(x-.04,yy,3.2),cross,Vector((0,0,1)),.12,.09,1.7,'glass')
    else:
        # small, high glazed accent under the far-end gable (unmeasured)
        for yy in (-2.8,-1.7,-.6,.6,1.7,2.8):
            oriented_box(P(x-.025,yy,2.5),cross,Vector((0,0,1)),.75,.07,1.25,'glass')
gable_end(x0-.02,high=True,glazed=True)
gable_end(x1+.02,high=False,glazed=False)
# The architect's sanctuary photograph shows large exposed timber A-frame members
# behind the stained glass; their section and exact location are approximate.
beam(P(x0+.30,-4.25,4.65),P(x0+.30,0,8.75),.34,'wood',.28)
beam(P(x0+.30,4.25,4.65),P(x0+.30,0,8.75),.34,'wood',.28)
beam(P(x0+.31,-4.15,5.05),P(x0+.31,4.15,5.05),.25,'wood',.22)
beam(P(x0+.31,-3.25,6.0),P(x0+.31,3.25,6.0),.18,'wood',.18)

# Shallow gabled roof along the long axis. A separate tall west-end glass gable emerges
# behind the low eave roof, matching the distinctive A-frame silhouette in the photo.
rx0=x0-overhang; rx1=x1+overhang; ry0=y0-overhang; ry1=y1+overhang
south_eave=P(0,ry0,eaves); north_eave=P(0,ry1,eaves)
roof_ridge=P(0,0,ridge)
face([P(rx0,ry0,eaves),P(rx1,ry0,eaves),P(rx1,0,ridge),P(rx0,0,ridge)],'roof')
face([P(rx0,0,ridge),P(rx1,0,ridge),P(rx1,ry1,eaves),P(rx0,ry1,eaves)],'roof')
for y in (ry0,ry1): beam(P(rx0,y,eaves),P(rx1,y,eaves),.24,'rooftrim',.22)
for t in range(10):
    x=rx0+(rx1-rx0)*t/9
    beam(P(x,ry0,eaves-.22),P(x,0,ridge-.22),.12,'wood',.10)
    beam(P(x,0,ridge-.22),P(x,ry1,eaves-.22),.12,'wood',.10)

# Broad dark metal entrance canopies with ashlar piers; the KJG 2022 facade photo shows
# two canopies, the larger main entrance and a shorter childcare/check-in entrance.
for cx,canopy_len,projection in ((-5.0,10.8,3.25),(7.6,6.3,2.75)):
    cy=south_y-projection/2-.08; cz=4.00
    oriented_box(P(cx,cy,cz),axis,cross,canopy_len,projection,.58,'rooftrim')
    oriented_box(P(cx,cy,cz-.31),axis,cross,canopy_len-.12,projection-.12,.055,'metal')
    # two limestone piers near the outer edge, plus a centered support where necessary
    for dx in (-canopy_len*.42,canopy_len*.42):
        box_xy(cx+dx,south_y-projection+.24,1.85,.72,.62,3.7,'stone')
        box_xy(cx+dx,south_y-projection+.24,.14,.95,.82,.28,'mortar')
# Front-facing low canopy below the stained-glass sanctuary gable, as shown in the
# historic entrance photo; stone piers stand at either side of its glass door bank.
front_proj=3.4; front_x=x0-front_proj/2-.14
oriented_box(P(front_x,0,4.05),cross,axis,width-.55,front_proj,.58,'rooftrim')
oriented_box(P(front_x,0,3.74),cross,axis,width-.68,front_proj-.12,.055,'metal')
for yy in (-width*.38,width*.38):
    box_xy(x0-front_proj+.23,yy,1.82,.64,.72,3.64,'stone')
    box_xy(x0-front_proj+.23,yy,.13,.86,.92,.26,'mortar')
# Dark foundation band and limestone entrance sills.
for y in (south_y-.015,y1+.015):
    beam(P(x0,y,.28),P(x1,y,.28),.30,'mortar',.18)

# Rebuild the one-object export. The mesh intentionally combines architectural pieces;
# the original stable object, collection, world-space coordinates and file path remain.
mesh=bpy.data.meshes.new('RiversideCovenant_Detailed_2026'); mesh.from_pydata(verts,[],faces)
for m in mats: mesh.materials.append(m)
mesh.update()
for p,mi in zip(mesh.polygons,face_mats): p.material_index=mi
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update()
obj.data=mesh; obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
mesh.name='RiversideCovenant_Detailed_2026'
if old.users==0: bpy.data.meshes.remove(old)
# Use the repository's CC0 Poly Haven masonry maps with project-scale UVs, then pack
# them so this standalone library never depends on an absolute texture path.
import sys
from pathlib import Path
repo_root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(repo_root))
from materials import pbr_upgrade
pbr_upgrade.metric_uv(obj,tile_m=1.4)
pbr_upgrade.upgrade_brick(M['brick'],tint=(.52,.24,.12,1.0),tile_m=1.4,texture_set='red_brick')
pbr_upgrade.upgrade_surface(M['stone'],'stone')
pbr_upgrade.upgrade_surface(M['glass'],'glass')
pbr_upgrade.upgrade_surface(M['frame'],'metal')
pbr_upgrade.pack_textures()
obj['asset_id']=tag; obj['source_feature_id']=860918859
obj['secondary_source_feature_id']='Indiana Building Footprints OBJECTID 409445 (LidarYear 2018)'
obj['geometry_status']='Photo-referenced church exterior and illustrative lobby/sanctuary interior; height, bearing and detailed plan remain estimated.'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
world_verts=[obj.matrix_world@v.co for v in mesh.vertices]
result={'asset_id':tag,'object':obj.name,'collection':coll.name,'collection_objects':len(coll.objects),'vertex_count':len(mesh.vertices),'face_count':len(mesh.polygons),'material_count':len(mesh.materials),'source_ring_vertices':len(ring),'footprint_dimensions_m':{'long_axis':length,'short_axis':width},'wall_eaves_estimate_m':eaves,'main_roof_ridge_estimate_m':ridge,'stained_glass_gable_peak_estimate_m':gableridge,'bounds_world_m':[[min(v[i] for v in world_verts),max(v[i] for v in world_verts)] for i in range(3)]}
print('RIVERSIDE_BUILD_RESULT='+json.dumps(result))
