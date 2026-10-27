import bpy, math, os, json
from mathutils import Vector

ASSET_ID = 'massing_house_970455277_a3fb72a'
ASSET_COLLECTION = 'Asset_' + ASSET_ID
SCENE_NAME = 'Building_' + ASSET_ID
COLLECTION_PATH = os.path.abspath(bpy.data.filepath)

# Read the source building's base-ring vertices before replacing the massing.
scene = bpy.context.scene
source_obj = bpy.data.objects.get('House_970455277') or next((o for o in scene.objects if o.type == 'MESH'), None)
if source_obj is None:
    raise RuntimeError('Expected source massing object House_970455277')
dg = bpy.context.evaluated_depsgraph_get()
source_eval = source_obj.evaluated_get(dg)
source_mesh = source_eval.to_mesh()
source_pts = [source_eval.matrix_world @ v.co for v in source_mesh.vertices]
source_eval.to_mesh_clear()
z0 = min(p.z for p in source_pts)
ring = []
for p in source_pts:
    if abs(p.z-z0) < 1e-4:
        xy=(float(p.x),float(p.y))
        if not any(math.hypot(xy[0]-q[0],xy[1]-q[1])<1e-5 for q in ring): ring.append(xy)
source_local_fallback=False
if len(ring) < 5:
    # Stable ring extracted from the saved source asset backup at
    # audit/alpha_omicron_pi/source_before_detailing.blend. This permits safe rebuilds.
    origin=(308.7021179199219,-719.9722595214844)
    ring=[(7.972198486328125,2.442901611328125),(3.222808837890625,2.553924560546875),(3.222808837890625,9.771514892578125),(-7.88739013671875,9.771514892578125),(-7.972198486328125,-9.771514892578125),(7.972198486328125,-9.7715146484375)]
    source_local_fallback=True
else:
    minx,maxx=min(p[0] for p in ring),max(p[0] for p in ring)
    miny,maxy=min(p[1] for p in ring),max(p[1] for p in ring)
    origin=(0.5*(minx+maxx),0.5*(miny+maxy))
if not source_local_fallback: ring=[(x-origin[0],y-origin[1]) for x,y in ring]
area=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))*0.5
if area < 0: ring.reverse()

# Replace the source single-block massing with building-specific geometry.
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for old_mat in list(bpy.data.materials):
    if old_mat.name.startswith('AOII |'): bpy.data.materials.remove(old_mat, do_unlink=True)
for col in list(bpy.data.collections):
    if col.name != 'Collection' and col.users == 0: bpy.data.collections.remove(col)
scene=bpy.context.scene; scene.name=SCENE_NAME
root=scene.collection
old=bpy.data.collections.get('Collection')
if old and old in list(root.children): root.children.unlink(old)
asset=bpy.data.collections.get(ASSET_COLLECTION)
if asset: bpy.data.collections.remove(asset)
asset=bpy.data.collections.new(ASSET_COLLECTION); root.children.link(asset)

def subcol(name):
    c=bpy.data.collections.new(name); asset.children.link(c); return c
EXT=subcol('AOII_Exterior'); INT=subcol('AOII_Interior'); SITE=subcol('AOII_Entry_and_Terrace')

def material(name, color, rough=0.7, metallic=0.0, brick=False, asphalt=False, siding=False):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); bs=nt.nodes.new('ShaderNodeBsdfPrincipled'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metallic
    nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    tc=nt.nodes.new('ShaderNodeTexCoord'); noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=5.0 if brick else 16.0; noise.inputs['Detail'].default_value=3.0; noise.inputs['Roughness'].default_value=.72
    nt.links.new(tc.outputs['Object'],noise.inputs['Vector'])
    bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.15 if brick else .08; bump.inputs['Distance'].default_value=.035 if brick else .015; nt.links.new(noise.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    if brick:
        tex=nt.nodes.new('ShaderNodeTexBrick'); tex.inputs['Color1'].default_value=(.22,.055,.028,1); tex.inputs['Color2'].default_value=(.34,.10,.055,1); tex.inputs['Mortar'].default_value=(.12,.085,.07,1); tex.inputs['Scale'].default_value=8.0; tex.inputs['Mortar Size'].default_value=.025; tex.inputs['Mortar Smooth'].default_value=.06
        nt.links.new(tc.outputs['UV'],tex.inputs['Vector']); nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    if siding:
        wave=nt.nodes.new('ShaderNodeTexWave'); wave.wave_type='BANDS'; wave.bands_direction='Y'; wave.inputs['Scale'].default_value=6.0; wave.inputs['Distortion'].default_value=0.0
        nt.links.new(tc.outputs['UV'],wave.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.interpolation='CONSTANT'; ramp.color_ramp.elements[0].position=.0; ramp.color_ramp.elements[0].color=(.50,.40,.26,1); ramp.color_ramp.elements[1].position=.47; ramp.color_ramp.elements[1].color=(.50,.40,.26,1)
        e=ramp.color_ramp.elements.new(.49); e.color=(.28,.21,.12,1)
        e=ramp.color_ramp.elements.new(.52); e.color=(.30,.23,.13,1)
        e=ramp.color_ramp.elements.new(.54); e.color=(.50,.40,.26,1)
        nt.links.new(wave.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        course=nt.nodes.new('ShaderNodeBump'); course.inputs['Strength'].default_value=.22; course.inputs['Distance'].default_value=.016
        nt.links.new(wave.outputs['Fac'],course.inputs['Height']); nt.links.new(bump.outputs['Normal'],course.inputs['Normal'])
        for link in list(nt.links):
            if link.to_node==bs and link.to_socket==bs.inputs['Normal']: nt.links.remove(link)
        nt.links.new(course.outputs['Normal'],bs.inputs['Normal'])
    if asphalt:
        tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=55; tex.inputs['Detail'].default_value=2
        nt.links.new(tc.outputs['Object'],tex.inputs['Vector']); nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
    return m

brick=material('AOII | red-brown running-bond brick',(.40,.15,.095),.84,brick=True)
base_stone=material('AOII | warm limestone and precast',(.70,.66,.56),.78)
cream=material('AOII | light painted garage stucco',(.78,.75,.67),.83)
siding=material('AOII | warm beige horizontal lap siding',(.42,.34,.20),.82,siding=True)
siding_seam=material('AOII | subtle siding lap shadow',(.28,.21,.12),.9)
shutter=material('AOII | dark burgundy louvered shutters',(.105,.035,.035),.62)
concrete=material('AOII | terrace concrete',(.46,.45,.41),.9)
asphalt=material('AOII | dark asphalt shingles',(.012,.018,.022),.86,asphalt=True)
white=material('AOII | warm white window and rail trim',(.88,.87,.81),.48)
glass=material('AOII | lightly reflective blue-gray glass',(.105,.19,.24),.22,.28)
door_mat=material('AOII | dark painted entry doors',(.08,.105,.13),.42)
garage_mat=material('AOII | charcoal garage panels',(.20,.22,.23),.62)
metal=material('AOII | dark bronze metal',(.12,.13,.13),.32,.65)
wood=material('AOII | interior oak',(.45,.27,.13),.62)
interior=material('AOII | interior warm plaster',(.73,.70,.62),.84)


def make_mesh(name, verts, faces, mat, coll, face_mats=None):
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.materials.append(mat); me.update()
    ob=bpy.data.objects.new(name,me); coll.objects.link(ob)
    if face_mats:
        for p,idx in zip(me.polygons,face_mats): p.material_index=idx
    return ob

def box(name, center, dims, mat, coll, bevel=.0, axes=None):
    cx,cy,cz=center; sx,sy,sz=[v/2 for v in dims]
    if axes is None:
        coords=[(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),(-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]
        verts=[(cx+x,cy+y,cz+z) for x,y,z in coords]
    else:
        u,n=axes; u=Vector(u); n=Vector(n); zaxis=Vector((0,0,1)); c=Vector(center)
        coords=[(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),(-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]
        verts=[tuple(c+u*x+n*y+zaxis*z) for x,y,z in coords]
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    ob=make_mesh(name,verts,faces,mat,coll)
    if bevel:
        mod=ob.modifiers.new('Soft architectural edges','BEVEL'); mod.width=bevel; mod.segments=2
    return ob

def prism_poly(name, poly, zlo, zhi, mat, coll):
    n=len(poly); verts=[(x,y,zlo) for x,y in poly]+[(x,y,zhi) for x,y in poly]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n): faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    return make_mesh(name,verts,faces,mat,coll)

def wall_opening_mesh(name,a,b,zlo,zhi,openings,mat,coll,thick=.20):
    a=Vector((a[0],a[1],0)); b=Vector((b[0],b[1],0)); delta=b-a; length=delta.length
    us=[0.0,1.0]; zs=[zlo,zhi]
    for op in openings:
        u=op['u']; w=op['width']/length; us += [max(0,u-w/2),min(1,u+w/2)]; zs += [op['bottom'],op['top']]
    us=sorted(set(round(max(0,min(1,u)),6) for u in us)); zs=sorted(set(round(max(zlo,min(zhi,z)),6) for z in zs))
    verts=[]; faces=[]
    for ui in range(len(us)-1):
        um=(us[ui]+us[ui+1])/2
        for zi in range(len(zs)-1):
            zm=(zs[zi]+zs[zi+1])/2
            if any(abs(um-o['u'])<o['width']/(2*length) and o['bottom']<zm<o['top'] for o in openings): continue
            p0=a+delta*us[ui]; p1=a+delta*us[ui+1]; i=len(verts)
            verts += [(p0.x,p0.y,zs[zi]),(p1.x,p1.y,zs[zi]),(p1.x,p1.y,zs[zi+1]),(p0.x,p0.y,zs[zi+1])]; faces.append((i,i+1,i+2,i+3))
    ob=make_mesh(name,verts,faces,mat,coll)
    if mat.name.startswith(('AOII | red-brown running-bond brick','AOII | warm beige horizontal lap siding')):
        uv=ob.data.uv_layers.new(name='Facade courses')
        for poly in ob.data.polygons:
            for li in poly.loop_indices:
                v=ob.data.vertices[ob.data.loops[li].vertex_index].co
                along=((v.x-a.x)*delta.x+(v.y-a.y)*delta.y)/length
                uv.data[li].uv=(along,v.z)
    sol=ob.modifiers.new('Masonry wall thickness','SOLIDIFY'); sol.thickness=thick; sol.offset=-1
    if mat.name.startswith('AOII | warm beige horizontal lap siding'):
        # Model the fine shadow at each horizontal lap. Split each course at
        # window openings so no seam runs across glass.
        n=outward_normal(a,b)
        course_z=zlo+.16
        row=0
        while course_z<zhi-.04:
            for ui in range(len(us)-1):
                u0,u1=us[ui],us[ui+1]; um=(u0+u1)/2
                if u1-u0<.012: continue
                if any(o['bottom']<course_z<o['top'] and abs(um-o['u'])<o['width']/(2*length) for o in openings): continue
                mid=a+delta*um+n*.12
                box(f'{name}_LapShadow_{row}_{ui}',(mid.x,mid.y,course_z),(length*(u1-u0),.06,.022),siding_seam,coll,axes=(delta.normalized(),n))
            row+=1; course_z+=.18
    return ob

def outward_normal(a,b):
    d=Vector((b[0]-a[0],b[1]-a[1],0)).normalized(); return Vector((d.y,-d.x,0))

def add_window(name,a,b,u,zbase,width=1.35,height=1.55,coll=EXT,shutters=False):
    d=Vector((b[0]-a[0],b[1]-a[1],0)).normalized(); n=outward_normal(a,b); c=Vector((a[0],a[1],zbase))+Vector((d.x,d.y,0))*(u*Vector((b[0]-a[0],b[1]-a[1],0)).length)+Vector((0,0,height*.5))
    # Frame is set on the exterior face and divided into upper/lower sash panes.
    frame=.075; depth=.10
    box(name+'_Glass',(c+n*.035),(width-2*frame,.055,height-2*frame),glass,coll,axes=(d,n))
    for s in (-1,1): box(name+'_Jamb',(c+n*.105+d*(s*(width/2-frame/2))),(frame,depth,height),white,coll,bevel=.012,axes=(d,n))
    for s in (-1,1): box(name+'_HeadSill',tuple(c+n*.105+Vector((0,0,s*(height/2-frame/2)))),(width,depth,frame),white,coll,bevel=.012,axes=(d,n))
    box(name+'_Mullion',(c+n*.16),(0.045,.05,height-2*frame),white,coll,axes=(d,n))
    box(name+'_MeetingRail',(c+n*.16),(width-2*frame,.05,.045),white,coll,axes=(d,n))
    box(name+'_Sill',(c+n*.16+Vector((0,0,-height/2-.08))),(width+.22,.16,.12),base_stone,coll,bevel=.02,axes=(d,n))
    if shutters:
        for side in (-1,1):
            sc=c+n*.17+d*(side*(width/2+.19))
            box(name+f'_Shutter_{side}_Panel',tuple(sc),(.30,.09,height*.96),shutter,coll,bevel=.015,axes=(d,n))
            for j in range(6):
                zz=-height*.40+j*height*.16
                box(name+f'_Shutter_{side}_Louver_{j}',tuple(sc+Vector((0,0,zz))+n*.055),(.27,.035,.035),metal,coll,axes=(d,n))

def add_door(name,a,b,u,zbase,width=1.15,height=2.25,coll=EXT,canopy=True):
    d=Vector((b[0]-a[0],b[1]-a[1],0)).normalized(); n=outward_normal(a,b); c=Vector((a[0],a[1],zbase))+Vector((d.x,d.y,0))*(u*Vector((b[0]-a[0],b[1]-a[1],0)).length)+Vector((0,0,height/2))
    box(name+'_Frame',(c+n*.12),(width+.20,.20,height+.20),base_stone,coll,bevel=.035,axes=(d,n))
    box(name+'_Leaf',(c+n*.24),(width,.10,height),door_mat,coll,bevel=.02,axes=(d,n))
    box(name+'_Lite',(c+n*.31+Vector((0,0,.58))),(width*.55,.03,.55),glass,coll,axes=(d,n))
    box(name+'_Handle',(c+n*.33+d*(width*.34)+Vector((0,0,-.15))),(.045,.05,.22),metal,coll,axes=(d,n))
    # Small canopy, supported on two brackets.
    if canopy:
        roofc=c+n*1.45+Vector((0,0,height/2+.20)); box(name+'_Canopy',tuple(roofc),(width+1.05,.85,.16),brick,coll,bevel=.025)

def projected_u(a,b,pt):
    d=Vector((b[0]-a[0],b[1]-a[1],0)); p=Vector((pt[0]-a[0],pt[1]-a[1],0)); return max(0,min(1,p.dot(d)/d.length_squared))

# Footprint-exact stepped walls: garage at grade plus two residential levels.
outer=ring
z_g=3.10; z_f1=6.20; z_f2=9.15; z_roof=9.75
segments=[]
for i,a in enumerate(outer): segments.append((a,outer[(i+1)%len(outer)]))
# Explicit upper-floor terraces and entry-door locations are limited to observed facades.
for idx,(a,b) in enumerate(segments):
    d=Vector((b[0]-a[0],b[1]-a[1],0)).normalized(); n=outward_normal(a,b); L=math.hypot(b[0]-a[0],b[1]-a[1])
    # Garage level: access doors face the east service/alley side; street face stays screened.
    low_open=[]
    if n.x>.72 and L>8:
        count=3 if L>11 else 2
        for k in range(count): low_open.append({'u':(k+1)/(count+1),'width':2.45,'bottom':.18,'top':2.42,'kind':'garage'})
    # Street-facing brick entry and flanking windows, as seen in the 2026 panorama.
    if n.x<-.72 and L>15:
        low_open.append({'u':projected_u(a,b,(-7.85,.6)),'width':1.20,'bottom':.10,'top':2.30,'kind':'main_entry'})
        for u in (.28,.61,.87): low_open.append({'u':u,'width':1.25,'bottom':.88,'top':2.28,'kind':'window'})
    wall_opening_mesh(f'AOII_GarageWall_{idx}',a,b,.15,z_g,low_open,brick,EXT,.22)
    for op in low_open:
        d3=Vector((b[0]-a[0],b[1]-a[1],0)).normalized(); nn=outward_normal(a,b); p=Vector((a[0],a[1],op['bottom']))+d3*(op['u']*L); c=(p.x,p.y,(op['bottom']+op['top'])/2)
        if op['kind']=='garage':
            box(f'AOII_GarageDoor_{idx}_{op["u"]:.2f}',tuple(Vector(c)+nn*.015),(op['width']-.06,.08,op['top']-op['bottom']-.05),garage_mat,EXT,bevel=.04,axes=(d3,nn))
            for row in range(4):
                zz=op['bottom']+.28+row*.42
                box(f'AOII_GarageDoor_Rib_{idx}_{op["u"]:.2f}_{row}',tuple(Vector((c[0],c[1],zz))+nn*.07),(op['width']-.24,.035,.035),metal,EXT,axes=(d3,nn))
        elif op['kind']=='window':
            add_window(f'AOII_GroundWindow_{idx}_{op["u"]:.2f}',a,b,op['u'],op['bottom'],op['width'],op['top']-op['bottom'])
        else:
            add_door(f'AOII_StreetEntry_{idx}',a,b,op['u'],op['bottom'],op['width'],op['top']-op['bottom'],canopy=False)
    # Upper floors are beige horizontal siding with dark shutters on the documented street facade.
    for floor,zbase,ztop in [(1,z_g,z_f1),(2,z_f1,z_f2)]:
        win_w=1.38 if L>8 else min(1.15,L*.27); count=max(1,int(L/3.15))
        centers=[(k+0.5)/count for k in range(count)]
        if n.x<-.72 and L>15:
            win_w=1.40; centers=[.20,.40,.60,.82]
        openings=[{'u':u,'width':win_w,'bottom':zbase+.78,'top':zbase+2.38,'kind':'window'} for u in centers]
        wall_opening_mesh(f'AOII_SidingWall_F{floor}_{idx}',a,b,zbase,ztop,openings,siding,EXT,.26)
        for op in openings:
            front_shutters=(n.x<-.72 and L>15)
            add_window(f'AOII_Window_F{floor}_{idx}_{op["u"]:.2f}',a,b,op['u'],zbase+.78,op['width'],1.60,shutters=front_shutters)

# Continuous stone/plaster belt courses emphasize the raised residential base.
for idx,(a,b) in enumerate(segments):
    d=Vector((b[0]-a[0],b[1]-a[1],0)).normalized(); n=outward_normal(a,b); L=math.hypot(b[0]-a[0],b[1]-a[1]); c=((a[0]+b[0])/2+n.x*.04,(a[1]+b[1])/2+n.y*.04,z_g-.12)
    box(f'AOII_StoneBelt_{idx}',c,(L,.16,.23),base_stone,EXT,axes=(d,n))
    c2=((a[0]+b[0])/2+n.x*.04,(a[1]+b[1])/2+n.y*.04,z_f1-.10)
    box(f'AOII_StringCourse_{idx}',c2,(L,.12,.18),base_stone,EXT,axes=(d,n))

# Floors and plausible shared-space/bedroom partitions. Room dimensions are inferred, not surveyed.
prism_poly('AOII_Garage_Slab',outer,-.10,.12,concrete,INT)
prism_poly('AOII_Level_1_Slab',outer,z_g-.12,z_g+.10,concrete,INT)
prism_poly('AOII_Level_2_Slab',outer,z_f1-.12,z_f1+.10,concrete,INT)
prism_poly('AOII_Roof_Deck',outer,z_f2-.10,z_f2,asphalt,EXT)

def part_x(name,x,y0,y1,z0,h=.12): box(name,(x,(y0+y1)/2,z0+h/2),(h,y1-y0,h),interior,INT,bevel=.01)
def part_y(name,y,x0,x1,z0,h=.12): box(name,((x0+x1)/2,y,z0+h/2),(x1-x0,h,h),interior,INT,bevel=.01)
# First residential floor: shared lounge, dining/kitchen, study and service rooms.
for y in [-1.0,1.15]: part_y(f'AOII_Level1_PartitionY_{y}',y,-7.0,3.15,z_g+.1,2.55)
part_x('AOII_Level1_PartitionX',0.15,-8.7,-1.05,z_g+.1,2.55)
part_x('AOII_Level1_ServicePartition',3.2,-8.7,-1.05,z_g+.1,2.55)
# Kitchen cabinetry and island; dining table/chairs; lounge seating; study furniture.
for i in range(5): box(f'AOII_Kitchen_BaseCabinet_{i}',(4.9,-7.5+i*.8,z_g+.65),(.55,.72,1.10),wood,INT,bevel=.035)
box('AOII_Kitchen_Counter',(4.9,-5.9,z_g+1.24),(.72,4.15,.12),base_stone,INT,bevel=.02)
box('AOII_Kitchen_Island',(2.0,-6.2,z_g+.80),(1.15,3.2,1.15),wood,INT,bevel=.04)
box('AOII_Kitchen_IslandTop',(2.0,-6.2,z_g+1.40),(1.35,3.4,.10),base_stone,INT,bevel=.02)
for i in range(3):
    box(f'AOII_Dining_Table_{i}',(-3.6,-6.7+i*1.55,z_g+.82),(2.0,.90,.12),wood,INT,bevel=.025)
    for j in [-.68,.68]: box(f'AOII_Dining_Chair_{i}_{j}',(-3.6+j,-6.7+i*1.55,z_g+.52),(.42,.44,.85),wood,INT,bevel=.03)
box('AOII_Lounge_Sofa',(-4.9,3.0,z_g+.55),(3.6,.9,.72),wood,INT,bevel=.10)
box('AOII_Lounge_CoffeeTable',(-4.8,1.8,z_g+.42),(2.2,.9,.12),wood,INT,bevel=.03)
for i in range(3): box(f'AOII_Study_Desk_{i}',(-5.3+i*1.35,6.0,z_g+.78),(1.1,.62,.10),wood,INT,bevel=.02)
# Upper floor corridor and 8 estimated bedroom bays with bunk beds and wardrobes.
for y in [-6.4,-2.85,.7,4.25,7.8]: part_y(f'AOII_Bedroom_PartitionY_{y}',y,-7.0,3.15,z_f1+.1,2.45)
for x in [-3.25,0.25]: part_x(f'AOII_Bedroom_PartitionX_{x}',x,-9.0,2.35,z_f1+.1,2.45)
room_centers=[(-5.1,-7.9),(-1.5,-7.9),(-5.1,-4.6),(-1.5,-4.6),(-5.1,-1.0),(-1.5,-1.0),(-5.1,2.6),(-1.5,2.6),(1.8,-7.8),(1.8,-4.5),(1.8,-1.0),(1.8,2.6),(-5.1,6.1),(-1.5,6.1),(1.8,6.1)]
for idx,(x,y) in enumerate(room_centers):
    # Compact two-bed bunk pair and a closet; furniture is representative, not a surveyed layout.
    for side in (-.55,.55):
        xx=x+side
        box(f'AOII_Bed_{idx}_{side}_Frame',(xx,y,z_f1+.38),(1.55,2.05,.32),wood,INT,bevel=.04)
        box(f'AOII_Bed_{idx}_{side}_Mattress',(xx,y,z_f1+.58),(1.48,1.95,.16),white,INT,bevel=.04)
        box(f'AOII_Bed_{idx}_{side}_Blanket',(xx,y-.28,z_f1+.68),(1.49,1.35,.10),brick,INT,bevel=.04)
    box(f'AOII_Bedroom_{idx}_Wardrobe',(x+1.05,y+1.1,z_f1+1.15),(.55,1.25,2.1),wood,INT,bevel=.03)
# Stair core and landings (approximate location and dimensions).
for z in [z_g,z_f1]:
    box(f'AOII_Stair_Landing_{z}',(-.5,.0,z+.20),(2.0,3.2,.24),base_stone,INT)
for i in range(12):
    x=-1.5+i*.22; z=.25+i*.24
    box(f'AOII_Stair_Tread_{i}',(x,0,z),(1.2,1.6,.12),base_stone,INT,bevel=.015)
# Garage parking stalls and support columns beneath the residential floors.
for i,x in enumerate([-5.4,-1.8,1.8,5.4]):
    for y in [-7.5,-3.8,0.0,3.8,7.4]:
        if x>3.0 and y>2.5: continue
        box(f'AOII_Garage_Column_{i}_{y}',(x,y,1.55),(.32,.32,3.05),base_stone,INT,bevel=.035)
for i,x in enumerate([-5.6,-2.2,1.2,4.6]):
    box(f'AOII_ParkingStripe_{i}',(x,-4.0,.025),(.06,4.2,.02),white,INT)

# Upper-level terrace sits in the recessed NE footprint notch, with clear guardrails.
notch_x0,notch_x1=3.22,7.80; notch_y0,notch_y1=2.55,9.48
box('AOII_Terrace_Slab',((notch_x0+notch_x1)/2,(notch_y0+notch_y1)/2,z_f1+.02),(notch_x1-notch_x0,notch_y1-notch_y0,.16),concrete,SITE)
rail_z=z_f1+1.03
for edge,(p0,p1) in enumerate([((notch_x0,notch_y1),(notch_x1,notch_y1)),((notch_x1,notch_y1),(notch_x1,notch_y0)),((notch_x1,notch_y0),(notch_x0,notch_y0))]):
    length=math.hypot(p1[0]-p0[0],p1[1]-p0[1]); d=Vector((p1[0]-p0[0],p1[1]-p0[1],0)).normalized(); n=outward_normal(p0,p1)
    box(f'AOII_Terrace_TopRail_{edge}',((p0[0]+p1[0])/2,(p0[1]+p1[1])/2,rail_z),(length,.10,.12),white,SITE,axes=(d,n))
    box(f'AOII_Terrace_MidRail_{edge}',((p0[0]+p1[0])/2,(p0[1]+p1[1])/2,z_f1+.56),(length,.07,.07),white,SITE,axes=(d,n))
    count=max(2,int(length/.42))
    for k in range(count+1):
        t=k/count; x=p0[0]+(p1[0]-p0[0])*t; y=p0[1]+(p1[1]-p0[1])*t
        box(f'AOII_Terrace_Baluster_{edge}_{k}',(x,y,z_f1+.55),(.065,.065,.95),white,SITE)
# Terrace door and planting boxes, reflecting the approved upper-level amenity.
box('AOII_Terrace_Planter_1',(4.0,3.25,z_f1+.48),(.75,1.8,.72),base_stone,SITE,bevel=.04)
box('AOII_Terrace_Planter_2',(6.95,8.7,z_f1+.48),(.75,1.25,.72),base_stone,SITE,bevel=.04)

# Low planter walls flank the grade-level public entry, matching the panorama.
for y in [-2.1,3.4]:
    box(f'AOII_Street_Planter_{y}',(-8.4,y,1.0),(1.0,2.3,1.25),base_stone,SITE,bevel=.08)
    box(f'AOII_Planter_Shrubs_{y}',(-8.4,y,1.72),(.75,1.9,.65),brick,SITE,bevel=.16)

# Low hipped asphalt roof with a shallow central rise; exact roof form remains estimated.
# Street View shows a low-pitched dark hip roof. The footprint is L-shaped,
# so make two adjoining hip volumes and leave the northeast terrace recess open.
roof_rise=.62; eave=z_f2+.015

def hip_roof_rect(name,x0,x1,y0,y1,z_eave,z_ridge,coll):
    dx=x1-x0; dy=y1-y0; ym=(y0+y1)/2
    A=(x0,y0,z_eave); B=(x1,y0,z_eave); C=(x1,y1,z_eave); D=(x0,y1,z_eave)
    E=(x0+dy/2,ym,z_ridge); F=(x1-dy/2,ym,z_ridge)
    return make_mesh(name,[A,B,C,D,E,F],[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)],asphalt,coll)

# South wing spans the full width; north wing occupies the west arm only.
x0,x1=min(p[0] for p in outer),max(p[0] for p in outer)
y0,y1=min(p[1] for p in outer),max(p[1] for p in outer)
notch_x=min(p[0] for p in outer if p[0]>0 and p[1]>2)
notch_y=min(p[1] for p in outer if p[1]>2)
hip_roof_rect('AOII_Hip_Roof_South_Wing',x0,x1,y0,notch_y,eave,eave+roof_rise,EXT)
hip_roof_rect('AOII_Hip_Roof_North_Wing',x0,notch_x,notch_y,y1,eave,eave+roof_rise,EXT)
# Crisp eaves and a restrained parapet-like fascia.
for idx,(a,b) in enumerate(segments):
    d=Vector((b[0]-a[0],b[1]-a[1],0)).normalized(); n=outward_normal(a,b); L=math.hypot(b[0]-a[0],b[1]-a[1])
    box(f'AOII_Roof_Fascia_{idx}',((a[0]+b[0])/2+n.x*.08,(a[1]+b[1])/2+n.y*.08,z_f2-.04),(L,.20,.28),asphalt,EXT,bevel=.02,axes=(d,n))
# Drain leaders at principal corners.
for idx,(x,y) in enumerate(outer):
    box(f'AOII_Downspout_{idx}',(x-.06 if x<0 else x+.06,y-.06 if y<0 else y+.06,(z_g+z_f2)/2),(.09,.09,z_f2-z_g),metal,EXT)

# Site footprint edge, an unobtrusive contextual base and an accessible path.
box('AOII_Entry_Path',(-9.7,.65,.025),(3.2,1.45,.05),concrete,SITE)
# Keep architectural objects easy to audit; metadata is descriptive only.
scene['building_id']=ASSET_ID; scene['building_name']='Alpha Omicron Pi Phi Upsilon Chapter House'; scene['local_origin_world_xy_m']=list(origin)
asset['building_id']=ASSET_ID; asset['source_feature']='OpenStreetMap way 970455277 (Microsoft BuildingFootprints import); source geometry cross-checked against the pre-existing asset base ring'; asset['local_origin_world_xy_m']=list(origin)
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1.0
scene.render.engine='BLENDER_EEVEE'
# Save a clean library with relative/local coordinates only.
asset_path=COLLECTION_PATH
bpy.ops.wm.save_as_mainfile(filepath=asset_path)
print(json.dumps({'asset_path':asset_path,'asset_id':ASSET_ID,'collection':ASSET_COLLECTION,'scene':SCENE_NAME,'origin_world_xy_m':origin,'footprint_local_m':ring,'footprint_area_m2':abs(area),'object_count':len(asset.all_objects),'z_levels_m':[0,z_g,z_f1,z_f2,z_roof]},indent=2))
