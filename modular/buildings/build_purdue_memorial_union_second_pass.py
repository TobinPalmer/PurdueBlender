"""PMU exterior reconstruction from FID644 and dated photographic evidence.

Run in Blender 5.2: blender --background --python THIS_FILE
Deterministic exterior; prior interior objects retained unchanged in a hidden
child collection. No master/marker/neighbor files are opened for writing.
Dimensions not established by survey remain documented estimates.
"""
import bpy, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/purdue_memorial_union.blend'
AUDIT=ROOT/'audit/purdue_memorial_union/second_pass'
SOURCES=ROOT/'research/second_pass/buildings/purdue_memorial_union/sources'
PREFIX='PMU_SP_'
REV=sys.argv[sys.argv.index('--revision')+1] if '--revision' in sys.argv else 'r02'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections['Asset_purdue_memorial_union']
root=bpy.data.objects.get('AssetRoot_purdue_memorial_union')
interior=bpy.data.collections.get('PMU_Preserved_FirstPass_Interior')
if interior is None:
    interior=bpy.data.collections.new('PMU_Preserved_FirstPass_Interior');col.children.link(interior)
    keys=('GreatHall','GH_','Memorial_','Hammerbeam','Fireplace','Chandelier','Candle','Chesterfield','CoffeeTable','StudyTable','BankerLamp','Dining_','WalkOns','BBQ_','Zen_','Starbucks','CommunityTable','Stool_','Pendant_','Crest_Text','Sign_WalkOns','Sign_BBQ','Sign_Zen','Sign_Starbucks')
    for o in list(col.objects):
        if any(k in o.name for k in keys):
            interior.objects.link(o);col.objects.unlink(o)
interior.hide_render=True;interior.hide_viewport=True
removed=[]
for o in list(col.objects):
    if o != root:
        removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
for child in list(col.children):
    if child!=interior:col.children.unlink(child)

def material(name,color,rough=.7,metal=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    m.diffuse_color=(*color,1);n=m.node_tree.nodes;n.clear()
    out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;m.node_tree.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    return m,bs
brick,bs=material('PMU_SP_Warm_Red_Brick',(.30,.085,.047))
nt=brick.node_tree;g=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(g.outputs['Position'],sep.inputs[0]);norm=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(g.outputs['Normal'],norm.inputs[0]);absolute=nt.nodes.new('ShaderNodeMath');absolute.operation='ABSOLUTE';nt.links.new(norm.outputs['X'],absolute.inputs[0]);mix=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(absolute.outputs[0],mix.inputs[0]);nt.links.new(sep.outputs['X'],mix.inputs[1]);nt.links.new(sep.outputs['Y'],mix.inputs[2]);uv=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(mix.outputs[0],uv.inputs['X']);nt.links.new(sep.outputs['Z'],uv.inputs['Y']);tex=nt.nodes.new('ShaderNodeTexBrick');tex.offset=.5;tex.offset_frequency=2;tex.inputs['Scale'].default_value=1;tex.inputs['Brick Width'].default_value=.22;tex.inputs['Row Height'].default_value=.075;tex.inputs['Mortar Size'].default_value=.004;tex.inputs['Color1'].default_value=(.32,.095,.05,1);tex.inputs['Color2'].default_value=(.21,.055,.032,1);tex.inputs['Mortar'].default_value=(.36,.30,.22,1);nt.links.new(uv.outputs[0],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs['Base Color']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.005;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
stone,_=material('PMU_SP_Warm_Limestone',(.62,.54,.41),.78)
frame,_=material('PMU_SP_Cream_Sash',(.66,.60,.46),.55)
glass,_=material('PMU_SP_Reflective_Glazing',(.028,.046,.052),.24,.28)
lead,_=material('PMU_SP_Fine_Lead',(.15,.16,.14),.5,.25)
slate,_=material('PMU_SP_Charcoal_Slate',(.065,.075,.08),.78)
membrane,_=material('PMU_SP_Pale_Membrane',(.49,.50,.47),.88)
metal,_=material('PMU_SP_Dark_Metal',(.035,.04,.042),.48,.5)
panel,_=material('PMU_SP_Shaded_Stone',(.48,.41,.30),.82)
# Fine slate course relief, photographic size estimates. No image dependencies.
nt=slate.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');co=nt.nodes.new('ShaderNodeTexCoord');tx=nt.nodes.new('ShaderNodeTexBrick');tx.inputs['Scale'].default_value=1;tx.inputs['Brick Width'].default_value=.30;tx.inputs['Row Height'].default_value=.18;tx.inputs['Mortar Size'].default_value=.002;tx.inputs['Color1'].default_value=(.062,.072,.078,1);tx.inputs['Color2'].default_value=(.09,.10,.105,1);tx.inputs['Mortar'].default_value=(.025,.03,.035,1);nt.links.new(co.outputs['Object'],tx.inputs['Vector']);nt.links.new(tx.outputs['Color'],bs.inputs['Base Color']);bu=nt.nodes.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.18;bu.inputs['Distance'].default_value=.008;nt.links.new(tx.outputs['Fac'],bu.inputs['Height']);nt.links.new(bu.outputs['Normal'],bs.inputs['Normal'])

def mesh(name,v,f,mat):
    d=bpy.data.meshes.new(PREFIX+name);d.from_pydata(v,[],f);d.update();d.materials.append(mat);o=bpy.data.objects.new(PREFIX+name,d);col.objects.link(o)
    if root:o.parent=root
    o['evidence']='research/second_pass/buildings/purdue_memorial_union/supplement_2026-10-30.md';return o
def box(name,x0,x1,y0,y1,z0,z1,mat):
    return mesh(name,[(x,y,z) for z in (z0,z1) for y in (y0,y1) for x in (x0,x1)],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],mat)
def bar(name,pts,r,mat):
    d=bpy.data.curves.new(PREFIX+name,'CURVE');d.dimensions='3D';d.bevel_depth=r;d.bevel_resolution=2;s=d.splines.new('POLY');s.points.add(len(pts)-1)
    for p,co in zip(s.points,pts):p.co=(*co,1)
    o=bpy.data.objects.new(PREFIX+name,d);col.objects.link(o);d.materials.append(mat)
    if root:o.parent=root
    return o
def shallow(cx,w,z,rise,n=32):return [(cx-w/2+w*i/n,z+rise*math.sin(math.pi*i/n)**.8) for i in range(n+1)]
def arch(name,cx,y,z,w,h,rise,lights=3):
    # Glazing polygon and projecting stone head; dimensions are photographic estimates.
    spring=z+h-rise;curve=shallow(cx,w,spring,rise)
    outline=[(cx-w/2,z),(cx+w/2,z)]+list(reversed(curve))
    mesh(name+'_Glass',[(x,y+.045,zz) for x,zz in outline],[tuple(range(len(outline)))],glass)
    bar(name+'_Head',[(x,y-.07,zz) for x,zz in curve],.105,stone)
    for x in (cx-w/2,cx+w/2):box(name+'_Jamb_'+str(x),x-.105,x+.105,y-.12,y+.16,z-.12,spring+.04,stone)
    box(name+'_Sill',cx-w/2-.18,cx+w/2+.18,y-.18,y+.17,z-.16,z+.025,stone)
    for i in range(1,lights):
        x=cx-w/2+w*i/lights;top=spring+rise*math.sin(math.pi*i/lights)**.8
        box(name+'_Mullion_'+str(i),x-.045,x+.045,y-.08,y+.02,z,top,frame)
    # Fine rectangular leading within each light, clipped beneath the real arch.
    for i in range(lights):
        x0=cx-w/2+w*i/lights;x1=x0+w/lights
        for k in (1,2):
            x=x0+(x1-x0)*k/3;top=spring+rise*math.sin(math.pi*(x-(cx-w/2))/w)**.8
            bar(name+'_LeadV_'+str(i)+'_'+str(k),[(x,y-.025,z),(x,y-.025,top-.04)],.009,lead)
    for row in range(1,int((h-rise)/.32)+1):
        zz=z+row*.32
        if zz<spring:bar(name+'_LeadH_'+str(row),[(cx-w/2+.02,y-.03,zz),(cx+w/2-.02,y-.03,zz)],.009,lead)
    # The characteristic paired rising curves in the central field.
    for sign in (-1,1):
        pts=[]
        for k in range(17):
            t=k/16;x=cx+sign*w/3*t;zz=spring+rise-.08-(rise*.58)*math.sin(t*math.pi/2)
            pts.append((x,y-.10,zz))
        bar(name+'_SweptTracery_'+str(sign),pts,.045,frame)
def rectwin(name,cx,y,z,w,h,lights=3,door=False,rows=7):
    box(name+'_Glass',cx-w/2,cx+w/2,y,y+.055,z,z+h,glass)
    for x in (cx-w/2,cx+w/2):box(name+'_Side_'+str(x),x-.075,x+.075,y-.08,y+.15,z-.1,z+h+.1,frame)
    for zz in (z,z+h):box(name+'_Rail_'+str(zz),cx-w/2-.1,cx+w/2+.1,y-.09,y+.16,zz-.075,zz+.075,frame)
    for i in range(1,lights):
        x=cx-w/2+w*i/lights;box(name+'_Mullion_'+str(i),x-.045,x+.045,y-.10,y+.10,z,z+h,frame)
    for k in range(1,6 if door else rows):
        zz=z+h*k/(6 if door else rows);bar(name+'_Horizontal_'+str(k),[(cx-w/2,y-.10,zz),(cx+w/2,y-.10,zz)],.023 if door else .013,frame if door else lead)
    if not door:
        for i in range(lights):
            x=cx-w/2+w*(i+.5)/lights;bar(name+'_Fine_'+str(i),[(x,y-.08,z),(x,y-.08,z+h)],.012,lead)
def gable(name,x0,x1,y0,y1,eave,ridge):
    ym=(y0+y1)/2
    mesh(name,[(x,y,z) for x in (x0,x1) for y,z in [(y0,eave),(ym,ridge),(y1,eave)]],[(0,3,4,1),(1,4,5,2),(0,1,2),(3,5,4),(0,2,5,3)],slate)
    for yy in (y0,y1):box(name+'_Eave_'+str(yy),x0,x1,yy-.09,yy+.09,eave-.12,eave+.08,metal)
def terminal(name,cx,y,w,top):
    mesh(name+'_Gable',[(cx-w/2,y,11.6),(cx+w/2,y,11.6),(cx,y,top),(cx-w/2,y+.65,11.6),(cx+w/2,y+.65,11.6),(cx,y+.65,top)],[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],brick)
    bar(name+'_Coping',[(cx-w/2-.1,y-.13,11.6),(cx,y-.13,top+.06),(cx+w/2+.1,y-.13,11.6)],.11,stone)
    arch(name+'_Upper',cx,y-.20,8.0,w*.66,3.4,.75,3);rectwin(name+'_Lower',cx,y-.22,3.7,w*.62,3.0,3)

fid=json.loads((SOURCES/'purdue_footprint.json').read_text())['features'][0]
ring=fid['geometry']['rings'][0][:-1]
xy=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274))-205.75,(lat-40.4274)*111040+271.65) for lon,lat in ring]
# Walls follow the detailed inventory; the forward central apron is low entry steps,
# not an eleven-metre-high wall extrusion. Roof is handled as separate masses.
signed_area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(xy,xy[1:]+xy[:1]))
for i,(a,b) in enumerate(zip(xy,xy[1:]+xy[:1])):
    mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
    # The forward footprint apron is stairs; an enclosing face would conceal them.
    if my<-42.50 and 9<mx<19:continue
    h=1.5 if (my<-42.50 and 9<mx<19) else (10.2 if my>50 else (8.35 if mx>59 and -38<my<-12 else 11.6))
    mesh('Inventory_Wall_'+str(i),[(a[0],a[1],0),(b[0],b[1],0),(b[0],b[1],h),(a[0],a[1],h)],[(0,1,2,3)],brick)
    # Ground-floor pale base wraps inventory wall edges.
    dx,dy=b[0]-a[0],b[1]-a[1];length=max(math.hypot(dx,dy),1e-8);sg=1 if signed_area>0 else -1;nx,ny=sg*dy/length,-sg*dx/length
    mesh('Inventory_Base_'+str(i),[(a[0]+nx*.035,a[1]+ny*.035,0),(b[0]+nx*.035,b[1]+ny*.035,0),(b[0]+nx*.035,b[1]+ny*.035,min(h,2.8)),(a[0]+nx*.035,a[1]+ny*.035,min(h,2.8))],[(0,1,2,3)],stone)
# Large central membrane plate with two image-traced internal voids. Separate strips
# avoid a single concave n-gon across holes. Bounds from the north-up image are estimates.
for i,b in enumerate([(-35.3,-19.05,-28,45.4),(-11.85,16.6,-28,45.4),(-19.05,-11.85,-28,8.44),(-19.05,-11.85,13.61,28.31),(-19.05,-11.85,35.59,45.4)]):
    x0,x1,y0,y1=b;box('Flat_Membrane_'+str(i),x0,x1,y0,y1,12.45,12.65,membrane)
gable('SouthWest_Slate',-35.5,6.7,-42.7,-30,11.6,14.5)
gable('SouthEast_Slate',21.5,40.0,-37.2,-24.8,11.6,14.1)
mesh('East_Wing_Slate',[ (x,y,z) for y in (-37.7,-12.5) for x,z in [(40.0,11.6),(49.0,14.0),(58.0,11.6)] ],[(0,1,4,3),(1,2,5,4),(0,2,1),(3,4,5)],slate)
box('East_Upper_Setback_Wall',57.7,57.95,-37.5,-12.5,8.3,11.6,brick)
box('East_Lower_Parapet_Coping',59.9,60.2,-37.5,-12.5,8.3,8.45,stone)
# Slim west pitched perimeter; broad old U-shaped roof is deliberately removed.
mesh('West_Perimeter_Slate',[(-35.6,-30,11.6),(-28.4,-30,14.4),(-23.0,-30,12.65),(-35.6,56.9,11.6),(-28.4,56.9,14.4),(-23.0,56.9,12.65)],[(0,3,4,1),(1,4,5,2),(0,1,2),(3,5,4)],slate)
gable('North_Slate_Run',-35.4,16.7,45.4,57.25,10.2,12.9)
box('Tower_Brick',6.7,21.5,-42.35,-29.2,11.6,19.55,brick)
box('Tower_Flat_Roof',6.8,21.4,-42.25,-29.3,19.45,19.60,membrane)
C=14.1;Y=-42.54
# Brick parapet with thin stone courses rather than unsupported pale turrets/clock.
for z in (16.9,18.1,19.55):
    box('Tower_Course_'+str(z),6.55,21.65,-42.52,-42.25,z,z+.09,stone)
for x in (6.7,8.3,19.9,21.5):
    box('Tower_Parapet_Pier_'+str(x),x-.12,x+.12,-42.6,-42.25,17.9,19.75,brick)
box('Tower_Stone_Panel',C-3.75,C+3.75,Y-.05,Y+.16,6.4,17.7,stone)
rectwin('Tower_Middle_FiveLight',C,Y-.20,8.15,5.4,2.55,5)
for i in range(5):
    rectwin('Tower_Middle_Separate_SmallLight_'+str(i),C-2.7+1.08*(i+.5),Y-.20,10.95,.92,.75,1,rows=2)
arch('Tower_Upper_FiveLight',C,Y-.21,13.6,5.45,3.9,1.0,5)
for i in range(6):
    x=C-2.7+1.08*i
    box('Tower_Spandrel_Rib_'+str(i),x-.06,x+.06,Y-.22,Y-.04,6.65,7.95,stone)
    for z in (6.9,7.25,7.6):
        bar('Spandrel_Chevron_'+str(i)+'_'+str(z),[(x-.07,Y-.24,z+.10),(x,Y-.30,z),(x+.07,Y-.24,z+.10)],.025,panel)
# Four entrance leaves and arched fanlight, consistent with both current providers.
for i in range(4):
    x0=C-2.7+1.35*i;x1=x0+1.33
    box('Entry_Leaf_'+str(i),x0,x1,Y-.25,Y-.05,1.6,4.45,frame)
    box('Entry_Upper_Pane_'+str(i),x0+.17,x1-.17,Y-.29,Y-.26,3.13,4.22,glass)
    for k in (1,2):
        x=x0+.17+(x1-x0-.34)*k/3;bar('Entry_Pane_Lead_'+str(i)+str(k),[(x,Y-.31,3.16),(x,Y-.31,4.2)],.011,lead)
    for zz in (3.5,3.85):bar('Entry_Pane_H_'+str(i)+str(zz),[(x0+.17,Y-.31,zz),(x1-.17,Y-.31,zz)],.011,lead)
    for x in (x0+.12,x1-.12):box('Entry_Leaf_Recess_'+str(i)+str(x),x-.018,x+.018,Y-.27,Y-.25,1.75,2.95,panel)
    bar('Entry_Handle_'+str(i),[(x1-.16,Y-.39,2.65),(x1-.16,Y-.42,2.85)],.025,metal)
arch('Entry_Fanlight',C,Y-.24,4.48,5.6,1.65,1.4,5)
for tier,z0,z1 in [('Middle',10.75,11.7),('Upper',16.2,17.25)]:
    box('Tower_'+tier+'_Separate_Upper_Rail',C-2.7,C+2.7,Y-.31,Y-.19,z0-.07,z0+.07,frame)
    for sign in (-1,1):
        pts=[]
        for k in range(21):
            t=k/20;pts.append((C+sign*(.54+1.1*t),Y-.34,z0+.72*(1-math.cos(t*math.pi/2))))
        bar('Tower_'+tier+'_Curved_Center_'+str(sign),pts,.046,frame)
for i in range(5):
    x=C-2.7+1.08*(i+.5);box('Tower_Recessed_Panel_'+str(i),x-.43,x+.43,Y-.11,Y-.06,11.93,12.8,panel)
    for xx in (x-.45,x+.45):box('Tower_Panel_Jamb_'+str(i)+str(xx),xx-.04,xx+.04,Y-.20,Y-.08,11.86,12.88,stone)
for inset in (0,.15,.30):
    pts=shallow(C,5.9+inset*2,4.47,1.7+inset*.5)
    bar('Entry_Archivolt_'+str(inset),[(x,Y-.33-inset*.25,z) for x,z in pts],.08,stone)
for x in (C-3.2,C+3.2):box('Entry_Pier_'+str(x),x-.24,x+.24,Y-.28,Y+.18,1.5,4.55,stone)
for k in range(8):box('Entry_Step_'+str(k),10.5,17.7,-46.3+k*.40,-42.5,0,1.6*(k+1)/8,stone)
for x in (10.8,17.4):
    bar('Entry_Rail_'+str(x),[(x,-46.1,1.0),(x,-42.7,2.5)],.035,metal)
    for y in (-45.8,-44.5,-43):bar('Entry_Rail_Post_'+str(x)+str(y),[(x,y,.25+(y+46.1)*.44),(x,y,1.0+(y+46.1)*.44)],.03,metal)
# Paired shallow reliefs retain supported overall layout; fine carving remains a gap.
for side,x in [('W',C-3.75),('E',C+3.75)]:
    box('Relief_Panel_'+side,x-.63,x+.63,Y-.23,Y+.02,8.0,12.55,stone)
    for j,dx in enumerate((-.29,.29)):
        xx=x+dx;box('Relief_Robe_'+side+str(j),xx-.19,xx+.19,Y-.38,Y-.23,8.65,11.65,stone)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=(xx,Y-.38,11.85));o=bpy.context.object;o.name=PREFIX+'Relief_Head_'+side+str(j);o.scale=(.16,.12,.24)
        for c in list(o.users_collection):c.objects.unlink(o)
        col.objects.link(o);o.data.materials.append(stone)
        for sg in (-1,1):bar('Relief_Arm_'+side+str(j)+str(sg),[(xx+sg*.2,Y-.39,11.4),(xx+sg*.23,Y-.44,10.75),(xx,Y-.46,10.6)],.07,stone)
# Verified visible five-bay run: provisional east-wing registration retained in audit.
for side,centers,y in [('East',[23.1,26.5,29.9,33.3,36.7],-37.25),('West_Original',[-8.4,-4.4,-.4,3.6],-41.95)]:
    for i,x in enumerate(centers):
        arch(side+'_Main_'+str(i),x,y,4.05,2.65,3.65,.8,3)
        rectwin(side+'_Upper_'+str(i),x,y-.015,8.7,2.65,2.25,3)
        rectwin(side+'_LowerDoor_'+str(i),x,y-.035,.15,2.65,2.75,2,True)
        for xx in (x-1.6,x+1.6):
            for z in (3.6,7.9,10.8):box(side+'_Quoin_'+str(i)+str(xx)+str(z),xx-.11,xx+.11,y-.10,y+.05,z,z+.20,stone)
terminal('West_Terminal',-15.0,-42.7,7.5,15.6)
terminal('East_Terminal',43.2,-42.05,6.5,15.1)
# North 2009 panorama: tall rectangular lights, small separate upper lights,
# lower paired groups and a slate roof, rather than south-style arched repetition.
for i,x in enumerate((-30,-23.8,-17.6,-11.4,-5.2,1.0,7.2,13.4)):
    lights=2 if i in (0,7) else 3;w=2.45 if lights==2 else 3.2
    before=set(col.objects)
    rectwin('North_Tall_'+str(i),x,0,3.6,w,4.1,lights)
    rectwin('North_Clerestory_'+str(i),x,0,7.95,w,1.05,lights,rows=2)
    rectwin('North_Lower_'+str(i),x,0,.45,w,1.95,lights,rows=4)
    # Rotate generated south-facing assemblies to face north about their facade plane.
    for o in set(col.objects)-before:
        if o.type=='MESH':
            for v in o.data.vertices:v.co.y=57.32-v.co.y
        elif o.type=='CURVE':
            for spline in o.data.splines:
                for p in spline.points:p.co.y=57.32-p.co.y
for i,x in enumerate((-19.0,1.0)):
    # The north dormers are distinct from the south triangular run.
    y=56.1;mesh('North_Dormer_'+str(i),[(x-.85,y,10.7),(x+.85,y,10.7),(x,y,12.15)],[(0,1,2)],brick)
    bar('North_Dormer_Trim_'+str(i),[(x-.9,y+.04,10.7),(x,y+.04,12.2),(x+.9,y+.04,10.7)],.065,stone)
# Northwest projecting entrance: two-light vertical family visible in north references.
before=set(col.objects);rectwin('Northwest_Upper',-23.4,0,5.0,2.2,4.2,2);rectwin('Northwest_Entry',-23.4,0,.25,2.8,2.9,2,True)
for o in set(col.objects)-before:
    if o.type=='MESH':
        for v in o.data.vertices:v.co.y=62.8-v.co.y
    elif o.type=='CURVE':
        for spline in o.data.splines:
            for p in spline.points:p.co.y=62.8-p.co.y
box('Northwest_Entry_Canopy',-26.0,-20.8,62.4,64.0,3.35,3.58,metal)
# Registered east entrance photograph: four broad arched groups (two either side of entry),
# lower rectangular triples and upper setback triples. Registration/sizes are
# approximate; no whole-elevation completeness inferred from this single view.
def to_east(objects,xplane):
    for o in objects:
        if o.type=='MESH':
            for v in o.data.vertices:v.co.x,v.co.y=xplane-v.co.y,v.co.x
        elif o.type=='CURVE':
            for sp in o.data.splines:
                for p in sp.points:p.co.x,p.co.y=xplane-p.co.y,p.co.x
for i,y in enumerate((-34.3,-29.3,-20.6,-15.6)):
    before=set(col.objects);arch('East_Arch_'+str(i),y,0,4.0,3.15,3.65,.8,3);rectwin('East_Lower_'+str(i),y,0,.5,3.15,2.7,3);to_east(set(col.objects)-before,60.22)
for i,y in enumerate((-35,-31,-27,-23,-19,-15)):
    before=set(col.objects);rectwin('East_Setback_Upper_'+str(i),y,0,9.0,2.4,2.1,3);to_east(set(col.objects)-before,58.02)
before=set(col.objects);rectwin('East_Entry',-24.9,0,.8,2.6,3.0,2,True);to_east(set(col.objects)-before,60.25)
for y in (-26.5,-23.3):box('East_Entry_Stone_Jamb_'+str(y),60.10,60.38,y-.16,y+.16,.4,4.8,stone)
box('East_Entry_Stone_Head',60.10,60.38,-26.7,-23.1,4.6,4.9,stone)
# Curved dark canvas canopy also visible in March 2026 registered Street View.
pts=shallow(-24.9,4.3,3.55,.75)
vs=[(x,y,z) for x in (60.05,62.3) for y,z in pts]
N=len(pts);fs=[(i,i+1,N+i+1,N+i) for i in range(N-1)]
mesh('East_Entry_Curved_Canopy',vs,fs,metal)
for y in (-27.0,-22.8):bar('East_Canopy_Support_'+str(y),[(62.0,y,3.4),(60.4,y,2.6)],.025,metal)
for k in range(4):box('East_Entry_Step_'+str(k),60.0,62.4-k*.4,-26.5,-23.3,0,.2*(k+1),stone)
# Dated west extension is intentionally not filled with an invented repeated grid.
for i,x in enumerate((-31,-26,-21)):
    rectwin('West_Extension_Estimated_'+str(i),x,-42.72,8.7,2.6,2.2,3)
    arch('West_Extension_Lower_Estimated_'+str(i),x,-42.73,4.0,2.6,3.6,.75,3)
# Dormer geometry follows the photographed small triangular forms; sizes estimated.
for i,x in enumerate((-29,-24,-19,-7,-1,25,32)):
    y=-40.7 if x<7 else -35.3
    box('Dormer_'+str(i),x-.65,x+.65,y,y+1.4,12.0,13.05,brick)
    mesh('Dormer_Gable_'+str(i),[(x-.7,y-.02,13.0),(x+.7,y-.02,13.0),(x,y-.02,13.85)],[(0,1,2)],brick)
    bar('Dormer_Coping_'+str(i),[(x-.73,y-.06,13.0),(x,y-.06,13.9),(x+.73,y-.06,13.0)],.055,stone)
    rectwin('Dormer_Window_'+str(i),x,y-.04,12.2,.78,.72,2)
for i,(x,y) in enumerate([(-26,-34),(-4,-34),(29,-28),(52,-23)]):
    box('Chimney_'+str(i),x-.45,x+.45,y-.55,y+.55,12.3,15.2,brick);box('Chimney_Cap_'+str(i),x-.58,x+.58,y-.68,y+.68,15.15,15.3,stone)
# Attached pale vestibule at east terminal; estate-wide terrace landscaping excluded.
box('East_Vestibule',40.0,46.7,-42.0,-38.6,0,2.9,stone)
rectwin('East_Vestibule_Door',43.3,-42.08,.05,3.8,2.55,2,True)
box('East_Vestibule_Cap',39.9,46.8,-42.15,-38.4,2.9,3.12,stone)
col['second_pass_status']=REV+', independently unaccepted; side/service coverage and fine ornament unresolved'
col['source_footprint']='Purdue GIS FID644; current inventory replaces approximate historic phases'
col['vertical_status']='Region-constrained estimates, not survey roof planes; see lidar_regions.json'
bpy.context.scene.unit_settings.system='METRIC'
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET),compress=True)
record=dict(revision=REV,asset_sha256=hashlib.sha256(ASSET.read_bytes()).hexdigest(),collection=col.name,removed_legacy_exterior_objects=len(removed),new_exterior_objects=len(col.objects),preserved_interior_objects=len(interior.objects),interior_status='Geometry and transforms retained in hidden child collection; not reworked or validated',master_edited=False,source_footprint='FID644',known_gaps=['Current side/service/inner opening schedules','Opposite wing complete counts and exact face registration','Fine carved figures and tracery profiles','Survey roof heights/planes','Current terrace/site ownership and dimensions'])
(AUDIT/('revision_'+REV)).mkdir(parents=True,exist_ok=True)
(AUDIT/('revision_'+REV)/'change_record.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record,indent=2))
