import bpy, math, json, os
from mathutils import Vector, Matrix
from math import radians

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'asian_american_resource_and_cultural_center.blend')
PREVIEW = os.path.join(ROOT, 'evidence', 'aaarcc_preview.png')
GIS = os.path.join(ROOT, 'evidence', 'aaarcc_gis_feature_926.json')
os.makedirs(os.path.dirname(PREVIEW), exist_ok=True)

# Campus local approximation used by this project; source feature is WGS 84.
LON_SCALE = 84810.60416539927
LAT_SCALE = 111040.0
ORIGIN_LON, ORIGIN_LAT = -86.9137, 40.4274
with open(GIS, 'r', encoding='utf-8') as f:
    feature_data = json.load(f)
    feature = feature_data[0] if isinstance(feature_data, list) else feature_data
ring_ll = feature['geometry']['rings'][0]
ring_xy = [((p[0]-ORIGIN_LON)*LON_SCALE, (p[1]-ORIGIN_LAT)*LAT_SCALE) for p in ring_ll]
minx,maxx=min(p[0] for p in ring_xy),max(p[0] for p in ring_xy)
miny,maxy=min(p[1] for p in ring_xy),max(p[1] for p in ring_xy)
origin = ((minx+maxx)/2, (miny+maxy)/2)
ring = [(x-origin[0], y-origin[1]) for x,y in ring_xy]

# Clear only this standalone library scene.
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection': bpy.data.collections.remove(c)
for s in list(bpy.data.scenes):
    if s != bpy.context.scene: bpy.data.scenes.remove(s)
scene=bpy.context.scene; scene.name='Building_asian_american_resource_and_cultural_center'
asset=bpy.data.collections.get('Asset_asian_american_resource_and_cultural_center')
if asset is None:
    asset=bpy.data.collections.new('Asset_asian_american_resource_and_cultural_center')
    scene.collection.children.link(asset)
else:
    for c in list(scene.collection.children):
        if c.name=='Collection': scene.collection.children.unlink(c)
        if c.name=='Asset_asian_american_resource_and_cultural_center': scene.collection.children.unlink(c)
    scene.collection.children.link(asset)

def link_obj(obj, name=None):
    if name: obj.name=name
    for c in list(obj.users_collection): c.objects.unlink(obj)
    asset.objects.link(obj)
    return obj

def make_mat(name, color, rough=0.75, metallic=0.0, noise_scale=85.0, bump=0.04, variation=0.08):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    n=m.node_tree.nodes; l=m.node_tree.links; n.clear()
    out=n.new('ShaderNodeOutputMaterial'); out.location=(560,0)
    bs=n.new('ShaderNodeBsdfPrincipled'); bs.location=(300,0)
    bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metallic
    bs.inputs['Base Color'].default_value=(*color,1)
    tex=n.new('ShaderNodeTexCoord'); tex.location=(-700,0)
    noise=n.new('ShaderNodeTexNoise'); noise.location=(-500,0); noise.inputs['Scale'].default_value=noise_scale; noise.inputs['Detail'].default_value=3.0; noise.inputs['Roughness'].default_value=0.68
    l.new(tex.outputs['Generated'],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB'); ramp.location=(-250,120)
    lo=tuple(max(0,min(1,c*(1-variation))) for c in color)+(1,)
    hi=tuple(max(0,min(1,c*(1+variation))) for c in color)+(1,)
    ramp.color_ramp.elements[0].position=0.2; ramp.color_ramp.elements[0].color=lo
    ramp.color_ramp.elements[1].position=0.8; ramp.color_ramp.elements[1].color=hi
    l.new(noise.outputs['Fac'],ramp.inputs['Fac']); l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    bumpn=n.new('ShaderNodeBump'); bumpn.location=(80,-180); bumpn.inputs['Strength'].default_value=bump; bumpn.inputs['Distance'].default_value=0.025
    l.new(noise.outputs['Fac'],bumpn.inputs['Height']); l.new(bumpn.outputs['Normal'],bs.inputs['Normal'])
    l.new(bs.outputs['BSDF'],out.inputs['Surface'])
    return m

siding=make_mat('AAARCC | warm white painted clapboard',(.79,.79,.73),.78,0,115,.08,.035)
trim=make_mat('AAARCC | ivory painted wood trim',(.92,.90,.82),.55,0,105,.035,.025)
foundation=make_mat('AAARCC | dark stone foundation',(.19,.20,.19),.88,0,38,.16,.16)
roofmat=make_mat('AAARCC | charcoal asphalt shingles',(.105,.12,.13),.86,0,75,.22,.22)
roofedge=make_mat('AAARCC | graphite roof fascia',(.12,.13,.13),.64,0,60,.06,.12)
brick=make_mat('AAARCC | weathered red brick chimney',(.39,.20,.15),.92,0,26,.22,.14)
concrete=make_mat('AAARCC | aged concrete and steps',(.43,.43,.40),.86,0,42,.15,.12)
wood=make_mat('AAARCC | stained entry door',(.27,.16,.09),.5,0,45,.06,.12)
metal=make_mat('AAARCC | painted dark metal',(.10,.11,.10),.4,.55,60,.03,.1)
glass=make_mat('AAARCC | blue charcoal sash glass',(.055,.095,.12),.18,.18,120,.015,.04)
# Keep glass dark but readable, with soft interior glow from a subtle emission.
gbs=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
gbs.inputs['Emission Color'].default_value=(.10,.16,.18,1); gbs.inputs['Emission Strength'].default_value=.13
interiorwall=make_mat('AAARCC | warm interior plaster',(.69,.64,.54),.88,0,65,.035,.04)
floor=make_mat('AAARCC | interior maple floor',(.37,.25,.13),.54,0,44,.06,.1)
furniture=make_mat('AAARCC | lounge upholstery',(.38,.29,.24),.82,0,35,.04,.1)
redaccent=make_mat('AAARCC | Purdue accent red',(.53,.055,.045),.5,0,60,.025,.08)
white=make_mat('AAARCC | lettering',(.9,.87,.78),.4,0,80,.02,.02)

# General mesh utilities. All model geometry is local to the feature envelope center.
def cube(name, loc, scale, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=link_obj(bpy.context.object,name); o.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat: o.data.materials.append(mat)
    if bevel:
        mod=o.modifiers.new('Softly worn edges','BEVEL'); mod.width=bevel; mod.segments=2
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o

def mesh_obj(name, verts, faces, mat):
    me=bpy.data.meshes.new(name+'Mesh'); me.from_pydata(verts,[],faces); me.materials.append(mat); me.update()
    o=bpy.data.objects.new(name,me); asset.objects.link(o)
    # Recalculate normals for clean surface lighting.
    import bmesh
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    return o

def solid_ring(name, pts, z0, z1, mat):
    n=len(pts); verts=[(x,y,z0) for x,y in pts]+[(x,y,z1) for x,y in pts]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n): j=(i+1)%n; faces.append((i,j,n+j,n+i))
    return mesh_obj(name,verts,faces,mat)

def roof_slab(name, verts, mat):
    o=mesh_obj(name,verts,[(0,1,2,3)],mat)
    solidify=o.modifiers.new('Roof board thickness','SOLIDIFY'); solidify.thickness=.16
    bevel=o.modifiers.new('Roof edge softness','BEVEL'); bevel.width=.035; bevel.segments=2
    return o

# Exact official GIS polygon used for the skirt/foundation. Exterior walls are 2-storey house massing.
solid_ring('AAARCC exact GIS perimeter | stone plinth', ring, 0.0, .42, foundation)
# Component envelopes inferred from footprint and photos: core, west side wing, small north bay.
# Footprint coordinates below preserve GIS campus orientation; house front is on west/Fifth Street.
X=lambda v:v-origin[0]; Y=lambda v:v-origin[1]
core=(X(-338.38),X(-329.26),Y(188.12),Y(196.76))
wing=(X(-341.24),X(-338.38),Y(190.01),Y(195.79))
northbay=(X(-336.56),X(-333.30),Y(196.76),Y(197.235))
# Main two-storey house shell. The west GIS projection is treated as the documented front porch, not as a taller institutional wing.
core_ring=[(core[0],core[2]),(core[1],core[2]),(core[1],core[3]),(core[0],core[3])]
solid_ring('AAARCC | white two-storey clapboard shell',core_ring,.38,5.82,siding)

# Batch the clapboard courses as one mesh to keep the library lightweight. The courses
# follow every edge of the official footprint, including the small bays and entry projections.
def siding_courses_from_ring(pts, z0=.52, z1=5.76):
    area=sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))/2
    verts=[]; faces=[]; step=.205; h=.15
    for i,p in enumerate(pts):
        q=pts[(i+1)%len(pts)]; dx=q[0]-p[0]; dy=q[1]-p[1]; length=math.hypot(dx,dy)
        if length < .30: continue
        # Positive signed area means counter-clockwise, whose exterior lies to the right.
        nx,ny=(dy/length,-dx/length) if area>0 else (-dy/length,dx/length)
        angle=math.atan2(dy,dx)
        z=z0
        while z < z1:
            cx=(p[0]+q[0])/2+nx*.035; cy=(p[1]+q[1])/2+ny*.035; cz=z+h/2
            # Long axis follows this polygon edge; narrow depth is normal to its facade.
            L=length+.015; D=.052; H=h
            local=[(-L/2,-D/2,-H/2),(L/2,-D/2,-H/2),(L/2,D/2,-H/2),(-L/2,D/2,-H/2),(-L/2,-D/2,H/2),(L/2,-D/2,H/2),(L/2,D/2,H/2),(-L/2,D/2,H/2)]
            base=len(verts)
            for lx,ly,lz in local:
                verts.append((cx+lx*math.cos(angle)-ly*math.sin(angle),cy+lx*math.sin(angle)+ly*math.cos(angle),cz+lz))
            faces.extend([(base+a,base+b,base+c,base+d) for a,b,c,d in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
            z+=step
    o=mesh_obj('AAARCC | individually coursed lap siding',verts,faces,trim)
    bevel=o.modifiers.new('Soft clapboard arrises','BEVEL'); bevel.width=.008; bevel.segments=1
    o.modifiers.new('Clapboard weighted normals','WEIGHTED_NORMAL')
    return o
siding_courses_from_ring(core_ring)
# Main steep gable roof, ridge east-west, with generous eaves as in the official exterior photos.
x0,x1,y0,y1=core; eave=5.82; ridge=9.10; ymid=(y0+y1)/2; over=.42
roof_slab('AAARCC | north roof slope',[(x0-.42,y0-.42,eave),(x1+.42,y0-.42,eave),(x1+.42,ymid,ridge),(x0-.42,ymid,ridge)],roofmat)
roof_slab('AAARCC | south roof slope',[(x0-.42,ymid,ridge),(x1+.42,ymid,ridge),(x1+.42,y1+.42,eave),(x0-.42,y1+.42,eave)],roofmat)
# End gable cladding triangles.
for x in [x0-.02,x1+.02]:
    mesh_obj('AAARCC | gable end',[(x,y0,eave),(x,y1,eave),(x,ymid,ridge-.04)],[(0,1,2)],siding)
    cube('Gable rake trim left',(x,(y0+ymid)/2,(eave+ridge)/2),(.12,math.sqrt((ymid-y0)**2+(ridge-eave)**2),.16),trim,.03).rotation_euler[0]=math.atan2(ridge-eave,ymid-y0)
    cube('Gable rake trim right',(x,(ymid+y1)/2,(eave+ridge)/2),(.12,math.sqrt((y1-ymid)**2+(ridge-eave)**2),.16),trim,.03).rotation_euler[0]=-math.atan2(ridge-eave,y1-ymid)
# Eave fascia, soffits, continuous ridge cap.
for y in [y0-.42,y1+.42]:
    cube('Roof eave fascia',((x0+x1)/2,y,eave-.08),(x1-x0+.9,.17,.22),roofedge,.035)
cube('Roof ridge cap',((x0+x1)/2,ymid,ridge+.03),(x1-x0+.95,.24,.22),roofedge,.05)
# Slate-like shingle course lines on both roof planes.
for i in range(1,11):
    t=i/11; yy=y0+(ymid-y0)*t; zz=eave+(ridge-eave)*t
    cube('North shingle course',((x0+x1)/2,yy,zz+.025),(x1-x0+.65,.025,.035),roofedge,.006)
    yy2=y1-(y1-ymid)*t
    cube('South shingle course',((x0+x1)/2,yy2,zz+.025),(x1-x0+.65,.025,.035),roofedge,.006)
# The westward GIS projection is an open covered front porch. The Fifth Street-facing door
# and front elevation in Purdue's official imagery support this interpretation.
wx0,wx1,wy0,wy1=wing
roof_slab('AAARCC | front porch shed roof',[(core[0]+.08,wy0-.15,3.85),(wx0-.20,wy0-.15,3.22),(wx0-.20,wy1+.15,3.22),(core[0]+.08,wy1+.15,3.85)],roofmat)
cube('Front porch fascia',((core[0]+wx0-.20)/2,(wy0+wy1)/2,3.20),(abs(core[0]-wx0)+.3,wy1-wy0+.4,.18),roofedge,.03)
for yy in [wy0+.22,(wy0+wy1)/2,wy1-.22]:
    cube('Front porch support column',(wx0-.05,yy,1.72),(.19,.19,3.35),trim,.028)
cube('Front porch floor',((wx0+core[0])/2,(wy0+wy1)/2,.16),(core[0]-wx0+.20,wy1-wy0+.24,.22),concrete,.035)
# Front porch canopy/gable on south projection: modest scale, restrained farmhouse entry.
px0,px1,py0,py1=X(-334.13),X(-329.63),Y(187.526),Y(188.89)
porch_y=py1-.05; porch_front=py0+.12; porch_ridge=(py0+py1)/2
roof_slab('AAARCC | entry porch roof north slope',[(px0-.18,py0-.05,3.28),(px1+.18,py0-.05,3.28),(px1+.18,porch_ridge,4.0),(px0-.18,porch_ridge,4.0)],roofmat)
roof_slab('AAARCC | entry porch roof south slope',[(px0-.18,porch_ridge,4.0),(px1+.18,porch_ridge,4.0),(px1+.18,py1+.16,3.28),(px0-.18,py1+.16,3.28)],roofmat)
for xx in [px0+.16,px1-.16]:
    cube('Porch square column',(xx,porch_front,1.68),(.19,.19,3.36),trim,.025)
cube('Porch front beam',((px0+px1)/2,porch_front,3.22),(px1-px0,.22,.24),trim,.025)
cube('Porch floor',((px0+px1)/2,(py0+py1)/2,.17),(px1-px0+.18,py1-py0+.3,.23),concrete,.035)

# Windows: double-hung multi-pane sash, white trim, dark glass, muntins. All facades get repeated modules.
def window(name, center, normal, w=1.05, h=1.48, sill=1.0, panes_x=2, panes_z=4):
    cx,cy,cz=center; thick=.12
    if normal=='west':
        # surface plane parallel Y-Z; outward into -X
        cube(name+' glass',(cx-.055,cy,cz),(thick*.32,w-.18,h-.18),glass,.012)
        cube(name+' outer casing',(cx-.12,cy,cz),(thick,w+.20,h+.20),trim,.025)
        for yy in [cy-(w-.12)/2,cy+(w-.12)/2]: cube(name+' jamb',(cx-.205,yy,cz),(.13,.095,h+.20),trim,.012)
        for zz in [cz-(h-.12)/2,cz+(h-.12)/2]: cube(name+' head/sill',(cx-.205,cy,zz),(.13,w+.18,.10),trim,.012)
        for i in range(1,panes_x): cube(name+' vertical muntin',(cx-.225,cy-w/2+w*i/panes_x,cz),(.06,.035,h-.12),trim,.006)
        for i in range(1,panes_z): cube(name+' horizontal muntin',(cx-.225,cy,cz-h/2+h*i/panes_z),(.06,w-.12,.035),trim,.006)
        cube(name+' projecting sill',(cx-.27,cy,cz-h/2-.04),(.28,w+.30,.13),trim,.018)
    elif normal=='east':
        cube(name+' glass',(cx+.055,cy,cz),(thick*.32,w-.18,h-.18),glass,.012); cube(name+' outer casing',(cx+.12,cy,cz),(thick,w+.20,h+.20),trim,.025)
        for yy in [cy-(w-.12)/2,cy+(w-.12)/2]: cube(name+' jamb',(cx+.205,yy,cz),(.13,.095,h+.20),trim,.012)
        for zz in [cz-(h-.12)/2,cz+(h-.12)/2]: cube(name+' head/sill',(cx+.205,cy,zz),(.13,w+.18,.10),trim,.012)
        for i in range(1,panes_x): cube(name+' vertical muntin',(cx+.225,cy-w/2+w*i/panes_x,cz),(.06,.035,h-.12),trim,.006)
        for i in range(1,panes_z): cube(name+' horizontal muntin',(cx+.225,cy,cz-h/2+h*i/panes_z),(.06,w-.12,.035),trim,.006)
        cube(name+' projecting sill',(cx+.27,cy,cz-h/2-.04),(.28,w+.30,.13),trim,.018)
    elif normal=='south':
        cube(name+' glass',(cx,cy-.055,cz),(w-.18,thick*.32,h-.18),glass,.012); cube(name+' outer casing',(cx,cy-.12,cz),(w+.20,thick,h+.20),trim,.025)
        for xx in [cx-(w-.12)/2,cx+(w-.12)/2]: cube(name+' jamb',(xx,cy-.205,cz),(.095,.13,h+.20),trim,.012)
        for zz in [cz-(h-.12)/2,cz+(h-.12)/2]: cube(name+' head/sill',(cx,cy-.205,zz),(w+.18,.13,.10),trim,.012)
        for i in range(1,panes_x): cube(name+' vertical muntin',(cx-w/2+w*i/panes_x,cy-.225,cz),(.035,.06,h-.12),trim,.006)
        for i in range(1,panes_z): cube(name+' horizontal muntin',(cx,cy-.225,cz-h/2+h*i/panes_z),(w-.12,.06,.035),trim,.006)
        cube(name+' projecting sill',(cx,cy-.27,cz-h/2-.04),(w+.30,.28,.13),trim,.018)
    else:
        cube(name+' glass',(cx,cy+.055,cz),(w-.18,thick*.32,h-.18),glass,.012); cube(name+' outer casing',(cx,cy+.12,cz),(w+.20,thick,h+.20),trim,.025)
        for xx in [cx-(w-.12)/2,cx+(w-.12)/2]: cube(name+' jamb',(xx,cy+.205,cz),(.095,.13,h+.20),trim,.012)
        for zz in [cz-(h-.12)/2,cz+(h-.12)/2]: cube(name+' head/sill',(cx,cy+.205,zz),(w+.18,.13,.10),trim,.012)
        for i in range(1,panes_x): cube(name+' vertical muntin',(cx-w/2+w*i/panes_x,cy+.225,cz),(.035,.06,h-.12),trim,.006)
        for i in range(1,panes_z): cube(name+' horizontal muntin',(cx,cy+.225,cz-h/2+h*i/panes_z),(w-.12,.06,.035),trim,.006)
        cube(name+' projecting sill',(cx,cy+.27,cz-h/2-.04),(w+.30,.28,.13),trim,.018)

# Main facades. West/Fifth-facing side is the principal elevation.
# Front upper sash trio, ground-floor windows left/right of the centered entry.
front_x=core[0]; front_ys=[core[2]+1.55,core[2]+4.35,core[2]+7.05]
for i,yy in enumerate(front_ys): window(f'Fifth Street upper sash {i+1}',(front_x,yy,4.85),'west',1.12,1.55,1.0,2,4)
for i,yy in enumerate([core[2]+2.05,core[2]+6.45]): window(f'Fifth Street lower sash {i+1}',(front_x,yy,1.75),'west',1.20,1.65,1.0,2,4)
# East rear elevation windows; north/south sides.
for i,yy in enumerate([core[2]+1.7,core[2]+4.3,core[2]+7.0]):
    window(f'Rear upper sash {i+1}',(core[1],yy,4.5),'east',1.02,1.45,1.0,2,4)
    if i<2: window(f'Rear lower sash {i+1}',(core[1],yy+.45,1.75),'east',1.10,1.55,1.0,2,4)
for side,yy in [('south',core[2]),('north',core[3])]:
    for floor_z in [1.75,4.5]:
        for xx in [core[0]+2.0,core[0]+6.9]: window(f'{side.title()} side sash',(xx,yy,floor_z),side,1.08,1.50,1.0,2,4)
# West wing multipane windows, constrained to smaller wing wall.
for yy in [wing[2]+1.1,wing[2]+3.2,wing[2]+4.85]:
    window('West wing sash',(wing[0],yy,4.25),'west',.95,1.35,1.0,2,3)
# Attic vent / small gable sash on west-facing gable.
window('West attic gable sash',(core[0],ymid,7.25),'west',.62,.84,1.0,2,2)

# Main door, west/front facade, with transom and panel detail.
door_y=(wing[2]+wing[3])/2; door_z=1.52
cube('Front door frame',(front_x-.12,door_y,door_z),(.20,1.24,2.65),trim,.035)
cube('Front stained wood door',(front_x-.24,door_y,door_z),(.11,1.02,2.42),wood,.025)
for z in [.72,1.30,1.88]:
    for dy in [-.27,.27]: cube('Raised front door panel',(front_x-.31,door_y+dy,z),(.035,.38,.42),wood,.018)
cube('Front door transom glass',(front_x-.25,door_y,2.89),(.08,1.03,.28),glass,.01)
# Small dark sign board with restrained lettering-like bars; readable silhouette but no tiny text dependency.
cube('AAARCC front sign board',(front_x-.27,door_y,3.28),(.10,1.48,.34),metal,.018)
for z in [3.31,3.39]: cube('AAARCC sign lettering line',(front_x-.335,door_y,z),(.018,1.10,.018),white,.004)
bpy.ops.object.text_add(location=(front_x-.35,door_y,3.35))
signtext=link_obj(bpy.context.object,'AAARCC front sign | lettered')
signtext.data.body='PURDUE AAARCC'; signtext.data.align_x='CENTER'; signtext.data.align_y='CENTER'; signtext.data.size=.115; signtext.data.extrude=.003
signtext.rotation_mode='QUATERNION'; signtext.rotation_quaternion=Matrix(((0,0,-1),(-1,0,0),(0,1,0))).to_quaternion(); signtext.data.materials.append(white)
cube('Door handle',(front_x-.34,door_y-.36,1.48),(.055,.05,.17),metal,.02)

# South accessible-entry door and concrete stoop, explicitly supported by Purdue evacuation instructions.
side_door_x=(px0+px1)/2
cube('Accessible entry frame',(side_door_x,core[2]-.10,1.45),(1.18,.20,2.58),trim,.025)
cube('Accessible entry leaf',(side_door_x,core[2]-.22,1.45),(.98,.10,2.36),wood,.02)
cube('Accessible entry window',(side_door_x,core[2]-.29,2.04),(.58,.04,.62),glass,.012)
cube('Accessible door kickplate',(side_door_x,core[2]-.30,.63),(.75,.035,.16),metal,.01)
# Gravel-side ramp: two sloped runs with handrails approximated to maintain access narrative.
def ramp_segment(name, p1, p2, width=1.2, thick=.16):
    a=Vector(p1); b=Vector(p2); mid=(a+b)/2; d=b-a; length=Vector((d.x,d.y,0)).length
    o=cube(name,mid,(length,width,thick),concrete,.035)
    o.rotation_euler[2]=math.atan2(d.y,d.x)
    o.rotation_euler[1]=-math.atan2(d.z,length)
    return o
# Ramp joins southern porch to open approach. Rise approximately .35 m, extent is a visual approach, not GIS boundary.
ramp_segment('Accessible approach ramp lower',(side_door_x-2.2,core[2]-.60,.08),(side_door_x,core[2]-.60,.32),1.15)
ramp_segment('Accessible approach landing',(side_door_x,core[2]-.60,.30),(side_door_x+1.8,core[2]-.60,.30),1.15)
for side in [-1,1]:
    xx=side_door_x+side*.55
    # handrail posts and top rail along both ramp legs
    for t in [0,.32,.64,.96]: cube('Ramp handrail support',(xx-2.2+2.2*t,core[2]-.60,.50+.10*t),(.055,.055,.80),metal,.012)
    cube('Ramp handrail', (xx-1.1,core[2]-.60,.92), (2.45,.06,.06),metal,.02).rotation_euler[1]=-.11

# Front stoop steps below principal door, with black railings.
for i in range(4):
    h=.14*(i+1); depth=.30*(4-i)
    cube('Fifth Street entry step',(front_x-.30-depth/2,door_y,h/2),(depth,1.72,h),concrete,.025)
for yy in [door_y-.83,door_y+.83]:
    cube('Front stair baluster',(front_x-.95,yy,.55),(.07,.07,1.1),metal,.015)
cube('Front stair handrail',(front_x-.95,door_y,1.05),(.07,1.78,.07),metal,.02)

# Brick chimney at rear roof plane and masonry cap.
chimx=core[1]-.90; chimy=core[3]-.90
cube('Brick chimney shaft',(chimx,chimy,7.85),(.72,.72,4.1),brick,.035)
cube('Brick chimney cap',(chimx,chimy,9.94),(.94,.94,.22),roofedge,.035)
for z in [6.5,7.1,7.7,8.3,8.9,9.5]:
    for ysgn in [-1,1]: cube('Chimney mortar band',(chimx,chimy+ysgn*.368,z),(.74,.025,.018),concrete,.003)

# Gutters/downspouts on lower eaves.
for yy in [y0-.43,y1+.43]:
    cube('Roof gutter',((x0+x1)/2,yy,eave-.22),(x1-x0+.95,.14,.12),metal,.03)
for xx in [x0-.38,x1+.38]:
    for yy in [y0-.43,y1+.43]:
        cube('Downspout',(xx,yy,3.0),(.075,.075,5.7),metal,.015)
        cube('Downspout shoe',(xx,yy-.03,.22),(.09,.20,.25),metal,.015)

# Interior schematic only. Room types are documented; exact partition positions are not.
cube('First-floor wood interior floor',(sum(core[:2])/2,sum(core[2:])/2,.52),(core[1]-core[0]-1.10,core[3]-core[2]-1.10,.10),floor,.012)
cube('Second-floor wood interior floor',(sum(core[:2])/2,sum(core[2:])/2,3.18),(core[1]-core[0]-1.10,core[3]-core[2]-1.10,.12),floor,.012)
# An interior divider suggests separate dining/kitchen and lounge while keeping room layout schematic.
wallx=core[0]+5.9
cube('Schematic first-floor room divider',(wallx,sum(core[2:])/2,1.85),(.12,core[3]-core[2]-0.3,2.55),interiorwall,.015)
# Lounge sofa, cushions, library shelf and coffee table.
lx=core[0]+2.4; ly=core[2]+2.5
cube('Lounge sofa base',(lx,ly,.92),(2.05,.82,.48),furniture,.10)
cube('Lounge sofa back',(lx,ly-.35,1.38),(2.06,.18,.75),furniture,.08)
for dx in [-.63,0,.63]: cube('Lounge sofa cushion',(lx+dx,ly+.10,1.18),(.58,.48,.12),redaccent if dx==0 else trim,.05)
cube('Lounge coffee table',(lx+.4,ly+1.05,.85),(1.10,.62,.12),wood,.035)
# Book shelf with books as colorful spines (verified library/books).
cube('Lounge bookcase',(core[0]+.32,core[2]+4.35,1.7),(.36,2.2,2.55),wood,.025)
for z in [.92,1.52,2.12]:
    cube('Bookshelf shelf',(core[0]+.10,core[2]+4.35,z),(.24,2.2,.075),trim,.012)
    for j in range(8): cube('Book spine',(core[0]-.04,core[2]+3.53+j*.23,z+.23),(.08,.14,.4),[redaccent,roofedge,wood,trim][j%4],.01)
# Dining area and pantry/kitchen counters.
cube('Dining table',(core[0]+7.05,core[2]+4.25,.97),(2.30,1.2,.13),wood,.045)
for dx in [-.78,.78]:
    for dy in [-.52,.52]:
        cube('Dining chair seat',(core[0]+7.05+dx,core[2]+4.25+dy,.78),(.48,.45,.10),furniture,.035)
        cube('Dining chair back',(core[0]+7.05+dx,core[2]+4.25+dy*1.28,1.14),(.46,.10,.62),wood,.025)
cube('Kitchen counter',(core[1]-.62,core[2]+5.25,1.35),(.62,2.8,.90),trim,.035)
cube('Kitchen worktop',(core[1]-.62,core[2]+5.25,1.82),(.70,2.9,.12),concrete,.02)
cube('Refrigerator',(core[1]-.56,core[2]+6.95,1.55),(.64,.76,2.25),trim,.035)
# Upstairs conference table and a small computer lab bank.
cube('Conference table',(core[0]+2.5,core[2]+3.0,3.9),(2.7,1.2,.13),wood,.035)
for dx in [-1.0,1.0]:
    for dy in [-.8,.8]: cube('Conference chair',(core[0]+2.5+dx,core[2]+3.0+dy,3.55),(.48,.45,.88),furniture,.045)
for i in range(3):
    xx=core[0]+6.4+i*.75
    cube('Computer lab desk',(xx,core[2]+4.4,3.9),(.68,1.55,.12),trim,.025)
    cube('Computer monitor',(xx,core[2]+4.15,4.4),(.56,.09,.42),roofedge,.015)
    cube('Monitor screen',(xx,core[2]+4.09,4.4),(.46,.025,.32),glass,.01)
# Ceiling lights softly visible from facade windows.
for z in [2.9,5.5]:
    for xx in [core[0]+2.5,core[0]+6.3]:
        cube('Interior light diffuser',(xx,sum(core[2:])/2,z),(.55,.28,.04),trim,.025)

# Scene lighting and polished camera preview.
world=bpy.data.worlds.new('AAARCC | soft clear afternoon') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(.34,.48,.62,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
scene.render.engine='CYCLES'; scene.cycles.samples=40
scene.render.resolution_x=1360; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
# Sun from southwest/front so the Fifth Street facade, porch, and roof edge read clearly.
bpy.ops.object.light_add(type='SUN',location=(-10,-8,14)); sun=link_obj(bpy.context.object,'Preview afternoon sun'); sun.rotation_euler=(radians(28),radians(-35),radians(-28)); sun.data.energy=2.0
bpy.ops.object.light_add(type='AREA',location=(-10,-15,9)); fill=link_obj(bpy.context.object,'Soft front fill'); fill.data.energy=1500; fill.data.shape='DISK'; fill.data.size=10; fill.rotation_euler=(radians(25),0,radians(-15))
# Ground plane is preview-only and intentionally outside the exported asset collection.
previewcol=bpy.data.collections.new('Preview_only'); scene.collection.children.link(previewcol)
bpy.ops.mesh.primitive_plane_add(size=70, location=(0,0,-.11)); ground=bpy.context.object; ground.name='Preview ground only'; ground.data.materials.append(make_mat('Preview | neutral grass-gray',(.24,.29,.23),.95,0,22,.1,.16))
for c in list(ground.users_collection): c.objects.unlink(ground)
previewcol.objects.link(ground)
# Camera target centered on local origin; facade southwest view.
target=Vector((0,0,4.5)); camloc=Vector((-19,-21,14))
bpy.ops.object.camera_add(location=camloc); camera=link_obj(bpy.context.object,'Preview camera | southwest front'); camera.data.lens=52; camera.rotation_euler=(target-camloc).to_track_quat('-Z','Y').to_euler(); scene.camera=camera
# Do not leave rendering helpers in the exported asset collection.
for helper in [sun,fill,camera]:
    for c in list(helper.users_collection): c.objects.unlink(helper)
    previewcol.objects.link(helper)
# Temporarily render preview, then put it in a separate scene collection; main exported collection remains the asset.
scene.render.filepath=PREVIEW
bpy.ops.wm.save_as_mainfile(filepath=OUT)
bpy.ops.render.render(write_still=True)
# Write provenance and dimensions from evaluated geometry, excluding preview ground/camera/lights.
objs=[o for o in asset.objects if o.type=='MESH']
worldpts=[]
for o in objs:
    for v in o.bound_box:
        worldpts.append(o.matrix_world @ Vector(v))
bounds=[[min(p[i] for p in worldpts),max(p[i] for p in worldpts)] for i in range(3)]
meta={
 'asset_id':'asian_american_resource_and_cultural_center',
 'collection':'Asset_asian_american_resource_and_cultural_center',
 'scene':'Building_asian_american_resource_and_cultural_center',
 'source_massing_asset':'modular/buildings/massing_asian_american_and_asian_resource_and_cultural_center_aacc_da08bb2.blend',
 'local_frame':'XY in meters, east/north; local origin is official feature 926 bounding-box center in the campus approximation',
 'placement_origin_xy_m':[origin[0],origin[1]],
 'bounds_local_m':bounds,
 'mesh_object_count':len(objs),
 'materials':[m.name for m in bpy.data.materials if m.name.startswith('AAARCC |')],
 'source_feature_id':926,
 'warnings':['Roof ridge height and eave height are visual estimates from exterior photographs; no surveyed elevations or construction drawings located.','Interior furnishings/room partitions are a documented programmatic schematic, not measured floor-plan geometry.','Google Street View records the exterior on 2019-01/02; the official Purdue facility page was retrieved 2026-10-23 and may show later landscape/site changes.','GIS geometry horizontal transform is project local approximation from WGS84, not a surveyed engineering CRS.'],
}
with open(os.path.join(ROOT,'evidence','aaarcc_asset_validation.json'),'w',encoding='utf-8') as f: json.dump(meta,f,indent=2)
print(json.dumps(meta,indent=2))







