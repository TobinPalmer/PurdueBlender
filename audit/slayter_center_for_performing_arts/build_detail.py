"""Rebuild the single-collection Slayter amphitheater library from source-backed geometry.

Run against the Slayter .blend in background Blender. It preserves the stable asset ID,
collection, scene, object name, campus coordinate frame and one-object export contract.
"""
import bpy, bmesh, json, math, os
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, 'build_config.json'), encoding='utf-8'))
FEATURE = json.load(open(os.path.join(HERE, CFG['source_feature_file']), encoding='utf-8'))
ASSET = CFG['asset_id']
OBJ_NAME = CFG['object_name']
COLL_NAME = CFG['collection_name']
obj = bpy.data.objects.get(OBJ_NAME)
coll = bpy.data.collections.get(COLL_NAME)
if not bpy.data.filepath or obj is None or coll is None or len(coll.objects) != 1 or obj not in coll.objects[:]:
    raise RuntimeError('Slayter asset structure mismatch; refusing to alter a different library')

# Purdue GIS feature 228 is a venue-envelope polygon (WGS 84), not a surveyed wall line.
# Use the repository's fixed local approximation and keep all structural geometry inside it.
ring = FEATURE['geometry']['rings'][0]
if ring[0] == ring[-1]: ring = ring[:-1]
lat0, lon0 = 40.4274, -86.9137
pts = [Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)), (lat-lat0)*111040.0)) for lon,lat in ring]
xmin,xmax=min(p.x for p in pts),max(p.x for p in pts)
ymin,ymax=min(p.y for p in pts),max(p.y for p in pts)
cx,cy=(xmin+xmax)/2,(ymin+ymax)/2
span=min(xmax-xmin,ymax-ymin)
stage_x=xmin+span*.25
stage_y=cy
back_w=34*.3048
front_w=56*.3048
depth=46*.3048

# Material system: fully procedural, packed into the mesh library, and portable without
# absolute texture paths. Noise and bump provide subtle aggregate instead of flat colors.
def material(name, low, high=None, rough=.8, metallic=0.0, noise_scale=5.0, bump=.12, emission=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*low,1)
    m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial'); bs=nt.nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metallic
    if 'Emission Color' in bs.inputs:
        bs.inputs['Emission Color'].default_value=(*low,1)
        bs.inputs['Emission Strength'].default_value=emission
    noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=noise_scale
    noise.inputs['Detail'].default_value=3.0; noise.inputs['Roughness'].default_value=.72
    ramp=nt.nodes.new('ShaderNodeValToRGB')
    c1=low; c2=high or tuple(min(1.0,v*1.14+.015) for v in low)
    ramp.color_ramp.elements[0].position=.25; ramp.color_ramp.elements[0].color=(*c1,1)
    ramp.color_ramp.elements[1].position=.78; ramp.color_ramp.elements[1].color=(*c2,1)
    bump_node=nt.nodes.new('ShaderNodeBump'); bump_node.inputs['Strength'].default_value=bump
    bump_node.inputs['Distance'].default_value=.035
    nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    nt.links.new(noise.outputs['Fac'],bump_node.inputs['Height'])
    nt.links.new(bump_node.outputs['Normal'],bs.inputs['Normal'])
    nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    return m

materials=[
    material('Slayter | stage concrete',(.39,.39,.36),(.48,.47,.43),.88,noise_scale=7,bump=.17),
    material('Slayter | white cast concrete stelae',(.64,.63,.57),(.78,.76,.68),.75,noise_scale=8,bump=.1),
    material('Slayter | French amber glass',(.48,.20,.055),(.95,.49,.12),.25,.05,noise_scale=16,bump=.025,emission=.035),
    material('Slayter | black epoxy resin',(.028,.032,.031),(.09,.085,.072),.32,.18,noise_scale=18,bump=.04),
    # The official photo shows dark painted/weathered steel rather than a bright
    # rust-colored frame; keep subtle variation but avoid a copper appearance.
    material('Slayter | weathering steel',(.035,.032,.029),(.12,.105,.085),.48,.55,noise_scale=12,bump=.09),
    material('Slayter | suspended concrete cloud',(.68,.67,.61),(.82,.80,.72),.68,noise_scale=9,bump=.08),
    material('Slayter | limestone retaining wall',(.24,.22,.18),(.43,.37,.28),.9,noise_scale=5,bump=.28),
    material('Slayter | lawn grass',(.025,.09,.018),(.15,.27,.055),.95,noise_scale=3.5,bump=.24),
    material('Slayter | warm stage apron',(.27,.25,.22),(.42,.37,.29),.84,noise_scale=11,bump=.14),
    material('Slayter | dark backstage recess',(.035,.04,.039),(.095,.095,.085),.78,noise_scale=9,bump=.05),
]
STAGE,STELAE,GLASS,RESIN,STEEL,CANOPY,STONE,GRASS,APRON,DARK=range(10)

# Face soup is combined to one mesh object at the end to preserve the manifest contract.
verts=[]; faces=[]; mids=[]; vertex_map={}; group_id=0
def new_group():
    global group_id
    group_id+=1
def face(points, mi):
    indices=[]
    for p in points:
        v=Vector(p); key=(group_id,)+tuple(round(float(x),6) for x in v)
        if key not in vertex_map:
            vertex_map[key]=len(verts); verts.append(tuple(v))
        indices.append(vertex_map[key])
    faces.append(tuple(indices)); mids.append(mi)
def box(center, sx, sy, sz, mi, angle=0.0):
    new_group()
    c=Vector(center); a=Vector((math.cos(angle),math.sin(angle),0))*sx*.5
    b=Vector((-math.sin(angle),math.cos(angle),0))*sy*.5
    z=Vector((0,0,sz*.5)); lo=c-z; hi=c+z
    p=[lo-a-b,lo+a-b,lo+a+b,lo-a+b,hi-a-b,hi+a-b,hi+a+b,hi-a+b]
    for q in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): face([p[i] for i in q],mi)
def beam(a,b,width,mi,depth=None,segments=8):
    new_group()
    a,b=Vector(a),Vector(b); axis=(b-a).normalized(); ref=Vector((0,1,0)) if abs(axis.dot(Vector((0,1,0))))<.92 else Vector((1,0,0))
    u=axis.cross(ref).normalized(); v=axis.cross(u).normalized(); d=depth or width
    va=[]; vb=[]
    for i in range(segments):
        ang=2*math.pi*i/segments
        radial=u*(math.cos(ang)*width*.5)+v*(math.sin(ang)*d*.5)
        va.append(a+radial); vb.append(b+radial)
    face(list(reversed(va)),mi); face(vb,mi)
    for i in range(segments): face([va[i],va[(i+1)%segments],vb[(i+1)%segments],vb[i]],mi)
def pier(x,y,width,depth_p,height,mi,along_y=True,phase=0.0):
    new_group()
    # Poly-cylindrical stela: shallow convex/concave plan and a hand-varied cap silhouette.
    n=16; levels=(0.0,.12,.55,.88,1.0); rings=[]
    for zf in levels:
        z=zf*height
        shrink=1.0-.10*zf
        topwave=.10*math.sin(phase+z*.7)*zf
        row=[]
        for j in range(n):
            a=2*math.pi*j/n
            profile=1.0+.10*math.cos(2*a+phase)
            w=width*.5*shrink*profile; d=depth_p*.5*shrink*(1+.08*math.sin(2*a+phase))
            if along_y: row.append((x+math.cos(a)*d,y+math.sin(a)*w,z+.15*height*zf*zf+topwave))
            else: row.append((x+math.sin(a)*w,y+math.cos(a)*d,z+.15*height*zf*zf+topwave))
        rings.append(row)
    face(rings[0],mi); face(list(reversed(rings[-1])),mi)
    for k in range(len(rings)-1):
        for j in range(n): face([rings[k][j],rings[k][(j+1)%n],rings[k+1][(j+1)%n],rings[k+1][j]],mi)
def prism(outline,z0,z1,mi_top,mi_side=None):
    new_group()
    lo=[(x,y,z0) for x,y in outline]; hi=[(x,y,z1) for x,y in outline]
    face(list(reversed(lo)),mi_side if mi_side is not None else mi_top); face(hi,mi_top)
    for i in range(len(outline)): face([lo[i],lo[(i+1)%len(lo)],hi[(i+1)%len(hi)],hi[i]],mi_side if mi_side is not None else mi_top)

# Low, flared platform: published stage dimensions, with shallow stone plinth on the rear/sides.
outline=[(stage_x,stage_y-back_w/2),(stage_x+depth,stage_y-front_w/2),(stage_x+depth,stage_y+front_w/2),(stage_x,stage_y+back_w/2)]
prism(outline,.45,.82,STAGE,APRON)
for i in range(5):
    x=stage_x+depth+.32+i*.34
    box((x,stage_y,.37-i*.055),.36,4.6,.14,APRON)
# Raised podium wall follows only the rear and sides, leaving the performance front open.
wall_h=.85
for y in (stage_y-back_w/2-.36,stage_y+back_w/2+.36):
    beam((stage_x-.2,y,wall_h/2),(stage_x+depth,y+(1 if y>stage_y else -1)*((front_w-back_w)/2),wall_h/2),.68,STONE,wall_h,6)
beam((stage_x-.2,stage_y-back_w/2-.36,wall_h/2),(stage_x-.2,stage_y+back_w/2+.36,wall_h/2),.68,STONE,wall_h,6)
# Correct prior box-like shell: stage is an open-air pavilion with Stonehenge-like back/side stelae.
rear_n=13
for i in range(rear_n):
    t=i/(rear_n-1); y=stage_y-back_w*.48+t*back_w*.96
    h=3.35+.22*math.sin(i*1.41)
    pier(stage_x-.12,y,.58+.08*(i%3),.55,h,STELAE,True,i*.7)
for side in (-1,1):
    n=15
    for i in range(n):
        t=i/(n-1); x=stage_x+depth*.03+t*depth*.90
        half=back_w*.5+(front_w-back_w)*.5*t
        y=stage_y+side*(half-.18)
        h=3.2+.35*math.sin(i*.91+side)
        pier(x,y,.60+.07*(i%4),.52,h,STELAE,False,i*.6+side)
# Distinct amber and black epoxy panels between stelae; open gaps remain to the landscape.
for i in range(rear_n-1):
    y=stage_y-back_w*.48+(i+.5)*(back_w*.96/(rear_n-1))
    box((stage_x-.16,y,.45+1.22),.13,.17,2.44,GLASS if i%2==0 else RESIN)
    box((stage_x-.16,y+.20,.45+1.22),.13,.12,2.44,RESIN if i%2==0 else GLASS)
for side in (-1,1):
    n=15
    for i in range(n-1):
        t=(i+.5)/(n-1); x=stage_x+depth*.03+t*depth*.90
        half=back_w*.5+(front_w-back_w)*.5*t
        y=stage_y+side*(half-.18)
        box((x,y,.45+1.22),.18,.13,2.44,GLASS if i%2==0 else RESIN)
        box((x+.21,y,.45+1.22),.12,.13,2.44,RESIN if i%2==0 else GLASS)
# Small, dark support/service recess behind the rear stelae; it reads as backstage space, not an enclosed hall.
box((stage_x-.85,stage_y,1.75),.58,back_w*.56,2.55,DARK)
box((stage_x-.54,stage_y,1.35),.08,1.18,1.95,STEEL)

# Sculpted thin concrete cloud: a shallow, undulating canopy with a real open gap above the stelae.
new_group()
rx,ry=7.55,9.55
roof_cx=stage_x+depth*.52; roof_cy=stage_y
N=48; radii=(.12,.34,.58,.80,1.0); top=[]; bottom=[]
def roof_z(r,a): return 7.15+.32*(1-r)+.18*math.sin(4*a+.35)*r*r+.08*math.cos(2*a)*r
for r in radii:
    toprow=[]; botrow=[]
    for j in range(N):
        a=2*math.pi*j/N
        x=roof_cx+rx*r*math.cos(a); y=roof_cy+ry*r*math.sin(a); z=roof_z(r,a)
        toprow.append((x,y,z)); botrow.append((x,y,z-.34))
    top.append(toprow); bottom.append(botrow)
for k in range(len(radii)-1):
    for j in range(N):
        j2=(j+1)%N
        face([top[k][j],top[k][j2],top[k+1][j2],top[k+1][j]],CANOPY)
        face([bottom[k+1][j],bottom[k+1][j2],bottom[k][j2],bottom[k][j]],CANOPY)
        if k==len(radii)-2: face([top[k+1][j],top[k+1][j2],bottom[k+1][j2],bottom[k+1][j]],CANOPY)
# Close the small central cap; the suspension hub sits above a continuous concrete cloud.
center_top=(roof_cx,roof_cy,roof_z(0,0)); center_bottom=(roof_cx,roof_cy,roof_z(0,0)-.34)
for j in range(N):
    j2=(j+1)%N
    face([center_top,top[0][j],top[0][j2]],CANOPY)
    face([center_bottom,bottom[0][j2],bottom[0][j]],CANOPY)
# Corten-steel tripod and a dense fan of suspended stainless cables from the self-supporting apex.
apex=(roof_cx,roof_cy,12.35)
beam(apex,(stage_x+depth*.15,stage_y-front_w*.66,.38),.34,STEEL,.32,8)
beam(apex,(stage_x+depth*.15,stage_y+front_w*.66,.38),.34,STEEL,.32,8)
beam(apex,(stage_x-5.2,stage_y,.38),.34,STEEL,.32,8)
beam(apex,(apex[0],apex[1],13.15),.26,STEEL,.26,8)
beam((apex[0]-.36,apex[1],apex[2]-.1),(apex[0]+.36,apex[1],apex[2]-.1),.48,STEEL,.48,8)
for j in range(32):
    a=2*math.pi*j/32
    r=1.0
    anchor=(roof_cx+rx*r*math.cos(a),roof_cy+ry*r*math.sin(a),roof_z(r,a)-.04)
    beam(apex,anchor,.035,STEEL,.035,6)

# A gentle fan of grass represents the grassy knoll used as informal audience seating; no benches.
nx,ny=12,20
startx=stage_x+depth+1.0; endx=min(startx+16.0,xmax-9.0)
grass=[]
for i in range(nx+1):
    u=i/nx; row=[]
    for j in range(ny+1):
        v=(j/ny)*2-1
        x=startx+(endx-startx)*u
        width=front_w*.51+u*4.0
        y=stage_y+v*width
        z=.03+1.65*u*u*(1-.12*abs(v))
        row.append((x,y,z))
    grass.append(row)
new_group()
for i in range(nx):
    for j in range(ny):
        face([grass[i][j],grass[i+1][j],grass[i+1][j+1],grass[i][j+1]],GRASS)
        b0=(grass[i][j][0],grass[i][j][1],-.12); b1=(grass[i+1][j][0],grass[i+1][j][1],-.12)
        b2=(grass[i+1][j+1][0],grass[i+1][j+1][1],-.12); b3=(grass[i][j+1][0],grass[i][j+1][1],-.12)
        face([b0,b3,b2,b1],GRASS)
        if j==0: face([grass[i][j],b0,b1,grass[i+1][j]],GRASS)
        if j==ny-1: face([grass[i][j+1],grass[i+1][j+1],b2,b3],GRASS)
    if i==0:
        for j in range(ny): face([grass[i][j],grass[i][j+1],(grass[i][j+1][0],grass[i][j+1][1],-.12),(grass[i][j][0],grass[i][j][1],-.12)],GRASS)
    if i==nx-1:
        for j in range(ny): face([grass[i+1][j],(grass[i+1][j][0],grass[i+1][j][1],-.12),(grass[i+1][j+1][0],grass[i+1][j+1][1],-.12),grass[i+1][j+1]],GRASS)
# A few narrow contour walks sit at the edge of the knoll, separated from the venue's stage apron.
for u in (.28,.58,.84):
    x=startx+(endx-startx)*u
    z=.03+1.65*u*u*(1-.12*.6)+.025
    half=front_w*.51+u*4.0
    for side in (-1,1):
        box((x,stage_y+side*half,z),.52,.75,.09,APRON)

# Rebuild the single exported mesh and keep the original object/collection identifiers stable.
mesh=bpy.data.meshes.new('SlayterCenter_Detailed_2026')
mesh.from_pydata(verts,[],faces)
for m in materials: mesh.materials.append(m)
mesh.update()
for p,mi in zip(mesh.polygons,mids):
    p.material_index=mi
    p.use_smooth=mi in (STELAE,CANOPY,GRASS)
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update()
old=obj.data; obj.data=mesh; obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
mesh.name='SlayterCenter_Detailed_2026'
if old.users==0: bpy.data.meshes.remove(old)
obj['asset_id']=ASSET
obj['source_feature_id']=int(FEATURE['attributes']['FID'])
obj['geometry_status']='Detailed open-air amphitheater; orientation, support heights and site slope remain estimates.'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

# Machine-readable measurements for review; preserve uncertainty rather than claiming survey accuracy.
deps=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(deps)
world=[obj.matrix_world @ Vector(corner) for corner in ev.bound_box]
result={
 'asset_id':ASSET,'source_feature_id':int(FEATURE['attributes']['FID']),
 'object':obj.name,'collection':coll.name,'collection_object_count':len(coll.objects),
 'vertex_count':len(mesh.vertices),'face_count':len(mesh.polygons),'material_count':len(mesh.materials),
 'bounds_m':{'x':[min(v.x for v in world),max(v.x for v in world)],'y':[min(v.y for v in world),max(v.y for v in world)],'z':[min(v.z for v in world),max(v.z for v in world)]},
 'published_stage_dimensions_m':{'front_width':front_w,'back_width':back_w,'depth':depth},
 'canopy_apex_estimate_m':apex[2], 'venue_envelope_aabb_m':{'x':[xmin,xmax],'y':[ymin,ymax]},
 'all_bounds_within_source_envelope_xy':min(v.x for v in world)>=xmin-1e-4 and max(v.x for v in world)<=xmax+1e-4 and min(v.y for v in world)>=ymin-1e-4 and max(v.y for v in world)<=ymax+1e-4
}
print('SLAYTER_BUILD_RESULT='+json.dumps(result))
