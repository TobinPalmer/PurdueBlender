import bpy, bmesh, math, json, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = 'massing_duhme_ophelia_residence_hall_1bb4e9c'
ASSET_PATH = ROOT / 'modular' / 'buildings' / f'{ASSET_ID}.blend'
SOURCE_PATH = ROOT / 'audit' / 'duhme_ophelia_residence_hall' / 'purdue_gis_query_1.geojson'
OUT = ROOT / 'audit' / 'duhme_ophelia_residence_hall'
OUT.mkdir(parents=True, exist_ok=True)

# Read Purdue Campus GIS outline (WGS84 returned by ArcGIS). Convert to the project's local campus coordinates.
feature = json.loads(SOURCE_PATH.read_text(encoding='utf-8'))['features'][0]
ring_ll = feature['geometry']['coordinates'][0]
ring = [Vector(((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)), (lat - 40.4274) * 111040.0)) for lon,lat in ring_ll]
if ring[0].xy == ring[-1].xy: ring = ring[:-1]
N=len(ring)

scene_name = 'Building_' + ASSET_ID
root = bpy.data.collections.get('Asset_' + ASSET_ID)
if root is None: root=bpy.data.collections.new('Asset_' + ASSET_ID)
for c in list(root.children):
    # clear only prior Duhme-owned subcollections
    bpy.data.collections.remove(c)
for o in list(root.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene=bpy.data.scenes.get(scene_name)
if scene is None: scene=bpy.data.scenes.new(scene_name)
if root.name not in [c.name for c in scene.collection.children]: scene.collection.children.link(root)

# For organized inspection, geometry remains in the stable exported collection; names identify each subsystem.

# Procedural, packed-asset-safe materials.
def mat(name, color, rough=0.82, metallic=0.0, noise_scale=None, bump_strength=0.0):
    m=bpy.data.materials.get('DUHME_' + name) or bpy.data.materials.new('DUHME_' + name)
    m.diffuse_color=(*color,1); m.use_nodes=True
    n=m.node_tree.nodes; l=m.node_tree.links; n.clear()
    out=n.new('ShaderNodeOutputMaterial'); out.location=(560,0)
    bs=n.new('ShaderNodeBsdfPrincipled'); bs.location=(300,0)
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metallic
    l.new(bs.outputs['BSDF'],out.inputs['Surface'])
    if noise_scale:
        tex=n.new('ShaderNodeTexNoise'); tex.location=(-500,100); tex.inputs['Scale'].default_value=noise_scale; tex.inputs['Detail'].default_value=3.0; tex.inputs['Roughness'].default_value=.72
        tc=n.new('ShaderNodeTexCoord'); tc.location=(-720,100); l.new(tc.outputs['Object'],tex.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB'); ramp.location=(-220,150); ramp.color_ramp.elements[0].position=.2; ramp.color_ramp.elements[0].color=(*tuple(v*.62 for v in color),1); ramp.color_ramp.elements[1].position=.82; ramp.color_ramp.elements[1].color=(*tuple(min(1,v*1.18) for v in color),1)
        l.new(tex.outputs['Fac'],ramp.inputs['Fac']); l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        if bump_strength:
            bump=n.new('ShaderNodeBump'); bump.location=(60,-170); bump.inputs['Strength'].default_value=bump_strength; bump.inputs['Distance'].default_value=.035; l.new(tex.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return m

brick=mat('Red_Oxide_Handmade_Brick',(0.38,.115,.065),.9,noise_scale=34,bump_strength=.2)
# A true mortar/brick course shader, UV-mapped in metres on the main perimeter wall.
brick_nodes=brick.node_tree.nodes; brick_links=brick.node_tree.links
brick_bs=next(n for n in brick_nodes if n.type=='BSDF_PRINCIPLED')
brick_uv=brick_nodes.new('ShaderNodeTexCoord'); brick_uv.location=(-760,-360)
brick_tex=brick_nodes.new('ShaderNodeTexBrick'); brick_tex.location=(-500,-360)
brick_tex.offset=.5; brick_tex.offset_frequency=2; brick_tex.inputs['Scale'].default_value=1.0
brick_tex.inputs['Brick Width'].default_value=.205; brick_tex.inputs['Row Height'].default_value=.062
brick_tex.inputs['Mortar Size'].default_value=.008; brick_tex.inputs['Mortar Smooth'].default_value=.08
brick_tex.inputs['Color1'].default_value=(.43,.15,.085,1);brick_tex.inputs['Color2'].default_value=(.31,.085,.05,1);brick_tex.inputs['Mortar'].default_value=(.52,.43,.34,1)
brick_links.new(brick_uv.outputs['UV'],brick_tex.inputs['Vector']);brick_links.new(brick_tex.outputs['Color'],brick_bs.inputs['Base Color'])
brick_bump=brick_nodes.new('ShaderNodeBump');brick_bump.location=(50,-320);brick_bump.inputs['Strength'].default_value=.25;brick_bump.inputs['Distance'].default_value=.012
brick_links.new(brick_tex.outputs['Fac'],brick_bump.inputs['Height']);brick_links.new(brick_bump.outputs['Normal'],brick_bs.inputs['Normal'])
brick_dark=mat('Brick_Shadow',(0.24,.065,.04),.92,noise_scale=28,bump_strength=.14)
limestone=mat('Warm_Limestone',(0.68,.61,.48),.72,noise_scale=22,bump_strength=.1)
roofmat=mat('Charcoal_Slate',(0.105,.12,.13),.8,noise_scale=45,bump_strength=.12)
roof_edge=mat('Slate_Ridge_and_Fascia',(.075,.083,.09),.78,noise_scale=30,bump_strength=.08)
wood=mat('Dark_Oak_Frames',(.16,.075,.035),.48,noise_scale=12,bump_strength=.08)
glass=mat('Window_Glass',(.09,.19,.23),.23,metallic=.18)
door_mat=mat('Entrance_Dark_Oak',(.075,.035,.022),.5,noise_scale=18,bump_strength=.08)
metal=mat('Black_Iron',(.055,.06,.058),.32,metallic=.72)
concrete=mat('Entry_Concrete',(.48,.46,.41),.86,noise_scale=18,bump_strength=.09)
carpet=mat('Interior_Warm_Carpet',(.28,.17,.115),.96,noise_scale=28,bump_strength=.16)
wood_floor=mat('Interior_Oak_Floor',(.31,.18,.09),.72,noise_scale=18,bump_strength=.1)
interior_wall=mat('Interior_Off_White_Paint',(.78,.72,.61),.88,noise_scale=20,bump_strength=.04)
fabric=mat('Lounge_Fabric_Purdue_Red',(.42,.12,.075),.84,noise_scale=25,bump_strength=.1)
fern=mat('Landscape_Shrubs',(.12,.23,.08),.95,noise_scale=16,bump_strength=.16)

# Object helpers. All coordinates remain in project campus space, as required for this massing ID.
def mesh_obj(name, verts, faces, material, collection=root):
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata([tuple(v) for v in verts],[],faces); me.materials.append(material); me.update()
    ob=bpy.data.objects.new(name,me); collection.objects.link(ob); return ob

def box(name, center, tangent, normal, width, depth, height, material, z_center=None):
    t=Vector((tangent[0],tangent[1],0)).normalized(); n=Vector((normal[0],normal[1],0)).normalized(); c=Vector((center[0],center[1],0))
    zc=(center[2] if len(center)>2 else 0) if z_center is None else z_center
    verts=[]
    for z in (-height/2,height/2):
        for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]:
            p=c+t*(a*width/2)+n*(b*depth/2)+Vector((0,0,zc+z)); verts.append(p)
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    return mesh_obj(name,verts,faces,material)

def cube_world(name, center, dims, material):
    cx,cy,cz=center; dx,dy,dz=[v/2 for v in dims]
    verts=[(cx-dx,cy-dy,cz-dz),(cx+dx,cy-dy,cz-dz),(cx+dx,cy+dy,cz-dz),(cx-dx,cy+dy,cz-dz),(cx-dx,cy-dy,cz+dz),(cx+dx,cy-dy,cz+dz),(cx+dx,cy+dy,cz+dz),(cx-dx,cy+dy,cz+dz)]
    return mesh_obj(name,verts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],material)

def triangulate_simple_polygon(points):
    # Ear clipping preserves concave courtyards and gaps in the GIS-derived U footprint.
    ids=list(range(len(points)))
    area=sum(points[i].x*points[(i+1)%len(points)].y-points[(i+1)%len(points)].x*points[i].y for i in range(len(points)))/2
    if area<0: ids.reverse()
    triangles=[]
    def cross(a,b,c): return (b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)
    def in_tri(p,a,b,c):
        x1=cross(a,b,p);x2=cross(b,c,p);x3=cross(c,a,p)
        return x1>=-1e-8 and x2>=-1e-8 and x3>=-1e-8
    guard=0
    while len(ids)>3 and guard<len(points)*len(points):
        guard+=1;clipped=False
        for k in range(len(ids)):
            ia,ib,ic=ids[k-1],ids[k],ids[(k+1)%len(ids)]
            a,b,c=points[ia],points[ib],points[ic]
            if cross(a,b,c)<=1e-8: continue
            if any(in_tri(points[j],a,b,c) for j in ids if j not in (ia,ib,ic)): continue
            triangles.append((ia,ib,ic));ids.pop(k);clipped=True;break
        if not clipped: raise ValueError('Could not triangulate Duhme GIS footprint; polygon may self-intersect')
    if len(ids)==3: triangles.append(tuple(ids))
    return triangles

FOOTPRINT_TRIANGLES=triangulate_simple_polygon(ring)
def prism_poly(name, pts2, z0,z1, material):
    n=len(pts2); verts=[(p.x,p.y,z0) for p in pts2]+[(p.x,p.y,z1) for p in pts2]
    faces=[]
    for i in range(n): faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    faces.extend(tuple(reversed(t)) for t in FOOTPRINT_TRIANGLES)
    faces.extend(tuple(i+n for i in t) for t in FOOTPRINT_TRIANGLES)
    return mesh_obj(name,verts,faces,material)

def floor_poly(name,z,material):
    verts=[(p.x,p.y,z) for p in ring]
    return mesh_obj(name,verts,FOOTPRINT_TRIANGLES,material)

def add_window(name, p, t, n, z, w=1.15,h=1.72):
    t=Vector((t[0],t[1],0)).normalized(); n=Vector((n[0],n[1],0)).normalized(); p=Vector((p[0],p[1],0))
    # window recess, stained dark glazing, oak frame, limestone sill/lintel, and mullions
    center=(p+n*.12).xy
    box(name+'_Glass',center,t,n,w,.07,h,glass,z_center=z)
    fw=.105
    for side in (-1,1):
        q=p+t*(side*(w/2+fw/2))+n*.19
        box(name+'_Jamb_'+str(side),q,t,n,fw,.22,h+.16,limestone,z_center=z)
    for side in (-1,1):
        q=p+n*.19
        box(name+('_Lintel' if side>0 else '_Sill'),q,t,n,w+.22,.24,.13,limestone,z_center=z+side*(h/2+.06))
    box(name+'_Center_Mullion',p+n*.22,t,n,.065,.18,h,wood,z_center=z)
    box(name+'_Cross_Mullion',p+n*.22,t,n,w,.18,.06,wood,z_center=z)
    box(name+'_Sash_Left',p+t*(-w*.22)+n*.23,t,n,.035,.16,h*.94,wood,z_center=z)
    box(name+'_Sash_Right',p+t*(w*.22)+n*.23,t,n,.035,.16,h*.94,wood,z_center=z)

# First, exact plan-derived continuous foundation and brick exterior shell.
prism_poly('DUHME_Continuous_GIS_Footprint_Foundation',ring,0,1.15,limestone)
# Walls are independent edge quads so the concave U footprint remains exact and watertight at corners.
wall_verts=[]; wall_faces=[]
for i in range(N):
    a,b=ring[i],ring[(i+1)%N]; base=len(wall_verts)
    wall_verts.extend([(a.x,a.y,1.05),(b.x,b.y,1.05),(b.x,b.y,12.25),(a.x,a.y,12.25)])
    wall_faces.append((base,base+1,base+2,base+3))
wall_obj=mesh_obj('DUHME_Continuous_Red_Brick_Wall_Envelope',wall_verts,wall_faces,brick)
uv=wall_obj.data.uv_layers.new(name='DUHME_Mortar_Course_UV')
perimeter_u=0.0
for poly in wall_obj.data.polygons:
    i=poly.index; a,b=ring[i],ring[(i+1)%N]; edge_length=(b-a).length
    # wall quad loop order: bottom start, bottom end, top end, top start; 1 UV unit = 1 meter
    uv_values=[(perimeter_u,1.05),(perimeter_u+edge_length,1.05),(perimeter_u+edge_length,12.25),(perimeter_u,12.25)]
    for loop_index,value in zip(poly.loop_indices,uv_values): uv.data[loop_index].uv=value
    perimeter_u+=edge_length
# Continuous stone water table and belt courses.
for z,h,name,matl in [(1.1,.22,'Stone_Water_Table',limestone),(4.05,.13,'First_Floor_Belt',limestone),(7.05,.10,'Second_Floor_Belt',limestone),(10.05,.10,'Third_Floor_Belt',limestone),(12.18,.22,'Cornice_Limestone',limestone)]:
    vv=[];ff=[]
    for i in range(N):
        a,b=ring[i],ring[(i+1)%N]; off=len(vv); vv.extend([(a.x,a.y,z-h/2),(b.x,b.y,z-h/2),(b.x,b.y,z+h/2),(a.x,a.y,z+h/2)]);ff.append((off,off+1,off+2,off+3))
    mesh_obj('DUHME_'+name,vv,ff,matl)

# Facade windows on the perimeter. Suppress short, angled bay returns and reserve main door/bay front.
rows=[2.55,5.55,8.55,11.05]
for i in range(N):
    a,b=ring[i],ring[(i+1)%N]; d=b-a; L=d.length
    if L<5.4: continue
    t=d.normalized(); n=Vector((t.y,-t.x)) # polygon ring is CCW; outward normal right hand
    # The 13 m south front is handled as a distinctive entry/bay composition.
    southfront=(i in (18,))
    if southfront: continue
    usable=max(0,L-2.2); count=max(1,int(usable/3.25))
    for k in range(count):
        s=(k+1)/(count+1)
        p=a+d*s
        for r,z in enumerate(rows):
            # Higher attic windows are limited to the upper storey to match the historic gabled front.
            if r==3 and L<7.0: continue
            add_window(f'DUHME_Exterior_Window_E{i:02d}_P{k+1}_F{r+1}',p,t,n,z,w=1.1 if r<3 else .82,h=1.55 if r<3 else 1.22)

# Two high gable roofs on the diagonal wings and a principal south-front gable roof over the central block.
def gable_roof(name, center, axis, width, length, eaves_z=12.25, ridge_z=15.35, brick_gable=True):
    a=Vector((axis[0],axis[1])).normalized(); side=Vector((-a.y,a.x)); c=Vector(center)
    halfL=length/2; halfW=width/2
    left=c-side*halfW; right=c+side*halfW
    s0=c-a*halfL; s1=c+a*halfL
    v=[(s0.x-side.x*halfW,s0.y-side.y*halfW,eaves_z),(s1.x-side.x*halfW,s1.y-side.y*halfW,eaves_z),(s1.x+side.x*halfW,s1.y+side.y*halfW,eaves_z),(s0.x+side.x*halfW,s0.y+side.y*halfW,eaves_z),(s0.x,s0.y,ridge_z),(s1.x,s1.y,ridge_z)]
    mesh_obj(name+'_Slate_Slopes',v,[(0,1,5,4),(4,5,2,3)],roofmat)
    # ridge and eaves
    box(name+'_Ridge_Cap',((s0.x+s1.x)/2,(s0.y+s1.y)/2),a,side,length,.24,.18,roof_edge,z_center=ridge_z+.05)
    for sign in (-1,1):
        edgec=c+side*(sign*(halfW+.1))
        box(name+'_Eave_'+str(sign),edgec,a,side,length,.2,.28,roof_edge,z_center=eaves_z+.05)
    # gable end triangles, oriented in a vertical plane normal to the ridge axis
    if brick_gable:
        for end,sgn in [(s0,-1),(s1,1)]:
            # face vertices base left/right and apex
            p1=end-side*halfW; p2=end+side*halfW
            verts=[(p1.x,p1.y,eaves_z),(p2.x,p2.y,eaves_z),(end.x,end.y,ridge_z)]
            mesh_obj(name+('_Gable_End_South' if sgn<0 else '_Gable_End_North'),verts,[(0,1,2)],brick)

# Principal entrance block; GIS form supports a southern central cross wing, dimensions inferred from historic footprint description.
gable_roof('DUHME_Principal_Central_Gable',(-595.0,-212.0),(0,1),14.0,15.0,12.25,15.35)
# Diagonal dormitory wings follow the two long arms in the GIS U plan.
gable_roof('DUHME_West_Wing_Roof',(-613.3,-199.8),(-.7071,.7071),12.2,31.8,12.25,15.25)
gable_roof('DUHME_East_Wing_Roof',(-577.0,-203.6),(.7071,.7071),12.2,31.8,12.25,15.25)

# Attic gable windows and stone verge/coping details at the south and north ends.
def gable_attic_window(name, center, tangent, normal, z):
    add_window(name,center,tangent,normal,z,w=.85,h=1.05)
gable_attic_window('DUHME_Front_Gable_Attic_Window',(-595.0,-219.14),(1,0),(0,-1),13.95)
# Decorative limestone gable verge lines, two pitched edges across the south face.
for sgn in (-1,1):
    start=Vector((-595.0+sgn*7.0,-219.2,12.3)); end=Vector((-595.0,-219.2,15.25)); d=end-start; L=d.length
    tangent=(d.x/L,d.z/L) # only XY basis helper cannot represent vertical tangent; create beam mesh directly
    verts=[]
    for y in (-.13,.13):
        for off in (-.09,.09):
            v1=start+Vector((d.x/L*off,y,d.z/L*off));v2=end+Vector((d.x/L*off,y,d.z/L*off));verts.extend([tuple(v1),tuple(v2)])
    faces=[(0,1,3,2)]
    mesh_obj('DUHME_Front_Gable_Limestone_Verge_'+str(sgn),verts,faces,limestone)

# Main projected stone bay above the entrance: three occupied levels, beveled corners, stone story bands.
bay_center=(-595.0,-219.55); bay_t=(1,0); bay_n=(0,-1)
box('DUHME_Central_Projecting_Bay',bay_center,bay_t,bay_n,4.35,1.05,7.0,brick,z_center=6.85)
for z in (3.05,6.0,8.95,9.8):
    box('DUHME_Bay_Stone_Belt_'+str(z),(bay_center[0],bay_center[1]-.56),bay_t,bay_n,4.65,.18,.20,limestone,z_center=z)
# Front face bay windows: three groups per upper floor.
for z in (2.55,5.55,8.55):
    for j,dx in enumerate((-1.28,0,1.28)):
        add_window(f'DUHME_Bay_Front_F{z}_W{j}',(bay_center[0]+dx,bay_center[1]-.57),(1,0),(0,-1),z,w=1.0,h=1.65)
# side return windows accent the polygonal bay
for sgn in (-1,1):
    for z in (2.55,5.55,8.55):
        p=(bay_center[0]+sgn*2.1,bay_center[1]-.18)
        add_window(f'DUHME_Bay_Side_{sgn}_F{z}',p,(0,1),(sgn,0),z,w=.78,h=1.55)

# Main entrance: round-headed opening, stone portal, door transom, stairs, handrail and threshold.
front_y=-219.22; door_x=-595.0
# broad limestone surround and arch voussoir ring
outerR=1.20; innerR=.82; spring=2.05; jamb=0.10; yfront=front_y-.21
# side jambs and threshold
box('DUHME_Entrance_Left_Stone_Jamb',(door_x-outerR-jamb/2,yfront),(1,0),(0,-1),jamb,.32,2.12,limestone,z_center=1.15)
box('DUHME_Entrance_Right_Stone_Jamb',(door_x+outerR+jamb/2,yfront),(1,0),(0,-1),jamb,.32,2.12,limestone,z_center=1.15)
# dark arched door panel fill with semicircular upper line
archverts=[]
for xsign in (-1,1): archverts.extend([(door_x+xsign*innerR,yfront-.02,0.35),(door_x+xsign*innerR,yfront-.02,spring)])
# door body rectangle and arch semi-circle as one polygon in XZ, extruded minimally
poly=[(door_x-innerR,0.35),(door_x+innerR,0.35),(door_x+innerR,spring)]
for k in range(1,13):
    ang=math.pi*k/12
    poly.append((door_x+innerR*math.cos(ang),spring+innerR*math.sin(ang)))
verts=[]
for yy in (yfront-.03,yfront+.04): verts.extend([(x,yy,z) for x,z in poly])
ln=len(poly); faces=[tuple(range(ln)),tuple(range(ln,2*ln))]
for k in range(ln): faces.append((k,(k+1)%ln,(k+1)%ln+ln,k+ln))
mesh_obj('DUHME_Arched_Dark_Oak_Main_Door',verts,faces,door_mat)
# arch stones in segmented voussoirs
for k in range(11):
    ang0=math.pi*k/11; ang1=math.pi*(k+1)/11; amid=(ang0+ang1)/2
    r=(innerR+outerR)/2; x=door_x+r*math.cos(amid); z=spring+r*math.sin(amid)
    # angled blocks as small rotated meshes in facade plane
    w=.36; h=.24
    tang=Vector((-math.sin(amid), math.cos(amid)))
    verts=[]
    for yy in (yfront-.22,yfront+.05):
      for aa,bb in [(-1,-1),(1,-1),(1,1),(-1,1)]:
        verts.append((x+aa*tang.x*w/2+bb*math.cos(amid)*h/2,yy,z+aa*tang.y*w/2+bb*math.sin(amid)*h/2))
    mesh_obj(f'DUHME_Entrance_Arch_Stone_{k:02d}',verts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],limestone)
# muntins and push plate
box('DUHME_Entry_Door_Mullion',(door_x,yfront-.08),(1,0),(0,-1),.045,.06,2.9,metal,z_center=1.85)
box('DUHME_Entry_Door_Transom',(door_x,yfront-.08),(1,0),(0,-1),1.55,.08,.10,limestone,z_center=2.42)
box('DUHME_Entry_Plaque',(door_x-2.05,yfront-.15),(1,0),(0,-1),.75,.1,.35,limestone,z_center=1.75)
# Entry inscription as 3D text, facing south; plaque nearby.
cu=bpy.data.curves.new('DUHME_HALL_Plaque_Text_Curve','FONT');cu.body='DUHME HALL';cu.size=.17;cu.extrude=.003;cu.align_x='CENTER';
txt=bpy.data.objects.new('DUHME_HALL_Plaque_Text',cu);root.objects.link(txt);txt.location=(door_x-2.05,yfront-.22,1.68);txt.rotation_euler=(math.radians(90),0,0);cu.materials.append(door_mat)
# limestone threshold and short five-step approach, each riser has rail posts and metal handrails
cube_world('DUHME_Entry_Threshold',(door_x,-219.55,.25),(2.2,.95,.5),concrete)
for i in range(5):
    z=.08+i*.17; y=-221.0+i*.34
    cube_world(f'DUHME_Entry_Step_{i+1}',(door_x,y,z),(3.2,1.15,.2),concrete)
for side in (-1,1):
    for i in range(4):
        cube_world(f'DUHME_Entry_Rail_Post_{side}_{i}',(door_x+side*1.55,-220.65+i*.40,.62+i*.05),(.11,.11,.95),metal)
    # slope rail as beam between end posts
    a=Vector((door_x+side*1.55,-221.15,.72));b=Vector((door_x+side*1.55,-219.75,1.2));d=b-a
    ob=box(f'DUHME_Entry_Handrail_{side}',((a.x+b.x)/2,(a.y+b.y)/2),(0,1),(1,0),d.length,.08,.08,metal,z_center=(a.z+b.z)/2)

# Chimneys, dormers, roof seams and lightning rods.
for idx,(x,y) in enumerate([(-587.0,-209.0),(-603.0,-209.0),(-574.0,-190.0),(-616.0,-190.0)]):
    cube_world(f'DUHME_Brick_Chimney_{idx}',(x,y,14.2),(1.1,1.1,3.0),brick_dark)
    cube_world(f'DUHME_Chimney_Stone_Cap_{idx}',(x,y,15.75),(1.3,1.25,.18),limestone)
# roof seam lines on long slopes, fine raised ribs/standing seams.
# Slate underlay closes roof intersections and keeps interior geometry out of exterior sightlines.
floor_poly('DUHME_Continuous_Slate_Roof_Underlay',12.22,roofmat)
for wi,(center,axis) in enumerate([((-595.0,-212.0),(0,1)),((-613.3,-199.8),(-.7071,.7071)),((-577.0,-203.6),(.7071,.7071))]):
    a=Vector(axis).normalized(); side=Vector((-a.y,a.x)); c=Vector(center)
    length=15 if wi==0 else 31
    roof_width=7.0 if wi==0 else 6.1
    for j,sgn in enumerate((-1,1)):
        for k in range(1,7):
            off=roof_width*(k/7)
            p=c+side*sgn*off
            slope_z=15.35-(15.35-12.25)*(off/roof_width)
            # Six raised slate seams run along each roof slope, parallel to the ridge.
            box(f'DUHME_Roof_Slate_Seam_{wi}_{j}_{k}',(p.x,p.y,slope_z),a,side,length,.035,.025,roof_edge,z_center=slope_z)

# Interior floors and schematic room zones. Floor outlines follow the verified concave GIS polygon; partitions and furniture are illustrative.
for floor,z in enumerate((1.30,4.30,7.30,10.30),1):
    floor_poly(f'DUHME_Interior_Floor_{floor}',z,wood_floor if floor==1 else carpet)
# Raised room partitions on the wings: paired corridors, room doors and representative student-room furniture.
wing_defs=[(('WEST',Vector((-613.3,-199.8)),Vector((-.7071,.7071))),), (('EAST',Vector((-577.0,-203.6)),Vector((.7071,.7071))),)]
for sideidx,pack in enumerate(wing_defs):
    label,c,axis=pack[0]; axis=axis.normalized(); across=Vector((-axis.y,axis.x))
    # central carpeted corridors run down both wings; side rooms are simple inferred partitions.
    for floor,zfloor in enumerate((1.32,4.32,7.32,10.32),1):
        mid=c
        # corridor floor strip
        for t in [k*2.5 for k in range(-5,6)]:
            pass
        box(f'DUHME_{label}_F{floor}_Corridor_Runner', (mid.x,mid.y),axis,across,30.0,2.1,.035,carpet,z_center=zfloor+.035)
        for k in range(1,7):
            t=(k-3.5)*4.1
            pt=c+axis*t
            # room divider wall pairs; reserve center corridor width
            for sign in (-1,1):
                wc=pt+across*sign*2.4
                box(f'DUHME_{label}_F{floor}_Room_Partition_{k}_{sign}',(wc.x,wc.y),across,axis,0.16,4.1,2.65,interior_wall,z_center=zfloor+1.35)
                # one simple brown room door on corridor side of each partition
                dc=pt+axis*.58+across*sign*1.65
                box(f'DUHME_{label}_F{floor}_Room_Door_{k}_{sign}',(dc.x,dc.y),across,axis,.85,.09,2.05,door_mat,z_center=zfloor+1.04)
        # furnishings in representative rooms only; do not claim a measured room plan.
        for t,sign in [(-8.2,-1),(-8.2,1),(8.2,-1),(8.2,1)]:
            room=c+axis*t+across*sign*3.2
            # bed platform and pale mattress, desk, chair and wardrobe
            bedc=room+axis*.6
            box(f'DUHME_{label}_F{floor}_Sample_Bed_Frame_{t}_{sign}',(bedc.x,bedc.y),axis,across,1.0,2.0,.22,wood_floor,z_center=zfloor+.16)
            box(f'DUHME_{label}_F{floor}_Sample_Bed_Mattress_{t}_{sign}',(bedc.x,bedc.y),axis,across,.93,1.88,.18,interior_wall,z_center=zfloor+.36)
            deskc=room-axis*1.2+across*sign*.25
            box(f'DUHME_{label}_F{floor}_Sample_Desk_{t}_{sign}',(deskc.x,deskc.y),axis,across,1.3,.65,.12,wood,z_center=zfloor+.78)
            cube_world(f'DUHME_{label}_F{floor}_Sample_Desk_Legs_{t}_{sign}',(deskc.x,deskc.y,zfloor+.39),(1.2,.55,.68),wood)
            cube_world(f'DUHME_{label}_F{floor}_Sample_Wardrobe_{t}_{sign}',(room.x,room.y,zfloor+1.0),(.75,.55,2.0),wood)
# central main living room arrangement and fireplace as documented; interior location/plan inferred.
cube_world('DUHME_Main_Living_Room_Fireplace_Stone',(door_x,-207.5,1.75),(3.3,.45,2.2),limestone)
cube_world('DUHME_Main_Living_Room_Fireplace_Opening',(door_x,-207.22,1.45),(1.5,.06,.95),door_mat)
# central lounge arrangement: sofa, two armchairs, side tables, bookcases.
for name,center,dims,material in [
 ('Sofa_Base',(door_x-2.3,-211.0,1.8),(2.5,.9,.35),wood_floor),('Sofa_Cushion',(door_x-2.3,-211.0,2.12),(2.4,.85,.55),fabric),
 ('Armchair_Left_Base',(door_x+2.1,-211.0,1.8),(1.0,.9,.32),wood_floor),('Armchair_Left_Cushion',(door_x+2.1,-211.0,2.05),(1.0,.85,.52),fabric),
 ('Reading_Table',(door_x,-213.2,1.65),(1.7,.9,.15),wood),('Bookcase',(door_x+3.6,-207.8,2.5),(.5,2.1,2.5),wood)]:
    cube_world('DUHME_Lounge_'+name,center,dims,material)
# lighting poles in common lounge, warm fixtures
for j,(x,y) in enumerate([(door_x-3,-208),(door_x+3,-208)]):
    cube_world(f'DUHME_Interior_Lounge_Lamp_Stem_{j}',(x,y,3.25),(.07,.07,2.2),metal)
    cube_world(f'DUHME_Interior_Lounge_Lamp_Shade_{j}',(x,y,4.35),(.48,.48,.18),limestone)

# Exterior landscaping and entrance lanterns kept inside the building asset only; these are illustrative edge items.
for side in (-1,1):
    for k in range(5):
        x=door_x+side*(4.1+k*.8); y=-219.8
        # low hedge strips and a few flowering blocks
        cube_world(f'DUHME_South_Front_Hedge_{side}_{k}',(x,y,.58),(.68,.65,.72),fern)
for side in (-1,1):
    cube_world(f'DUHME_Entrance_Lantern_Post_{side}',(door_x+side*2.65,-219.65,2.65),(.14,.14,3.0),metal)
    cube_world(f'DUHME_Entrance_Lantern_Glass_{side}',(door_x+side*2.65,-219.65,4.1),(.4,.4,.48),limestone)

# Basic descriptive metadata stored as custom properties on the stable collection.
root['building_id']=ASSET_ID;root['source']='Purdue Campus GIS feature OBJECTID 229 / historic database buildingidlong 351';root['geometry_units']='metres, project campus coordinates; directly linked massing form';root['height_status']='estimated 15.84 m ridge; four stories documented; no surveyed roof-height source found';root['interior_status']='schematic; official room programs documented but floor plans unavailable publicly'
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100
# Remove inherited, unused raster materials/textures from the starter massing library.
for _ in range(3):
    try: bpy.data.orphans_purge(do_recursive=True,do_local_ids=True,do_linked_ids=True)
    except TypeError: bpy.data.orphans_purge(do_recursive=True)
for image in list(bpy.data.images):
    if image.users==0: bpy.data.images.remove(image)
# Review camera and lights live outside the exported asset collection.
from mathutils import Vector as _V
camdata=bpy.data.cameras.new('DUHME_Evidence_Camera'); cam=bpy.data.objects.new('DUHME_Evidence_Camera',camdata);scene.collection.objects.link(cam)
target=_V((-595.0,-202.0,7.0)); cam.location=(-565.0,-250.0,35.0); cam.rotation_euler=(target-_V(cam.location)).to_track_quat('-Z','Y').to_euler();camdata.lens=32;scene.camera=cam
for name,loc,power,size in [('Key',(-610,-235,38),3600,24),('Fill',(-570,-195,32),2400,20)]:
    ld=bpy.data.lights.new('DUHME_'+name,'AREA');lo=bpy.data.objects.new('DUHME_'+name,ld);scene.collection.objects.link(lo);lo.location=loc;ld.energy=power*.72;ld.shape='DISK';ld.size=size;lo.rotation_euler=(target-_V(loc)).to_track_quat('-Z','Y').to_euler()
world=scene.world or bpy.data.worlds.new('DUHME_Review_World');scene.world=world;world.use_nodes=True;world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.42,.48,.58,1);world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.35
# Save with the target scene active; all model materials are procedural, and no external image maps are needed.
if bpy.context.window: bpy.context.window.scene=scene
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
# Render a review image for the independent grader.
scene.view_settings.view_transform='Standard';scene.render.filepath=str(OUT/'exterior_candidate.png');bpy.ops.render.render(write_still=True)
# Produce machine-readable geometry summary for the evaluator/coordinator.
objs=[o for o in root.all_objects]
coords=[]
for o in objs:
    if o.type=='MESH':
        for v in o.bound_box: coords.append(o.matrix_world @ Vector(v))
if coords:
    bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
else: bounds=None
report={'building_id':ASSET_ID,'file':str(ASSET_PATH),'scene':scene.name,'collection':root.name,'object_count':len(objs),'mesh_count':sum(o.type=='MESH' for o in objs),'font_count':sum(o.type=='FONT' for o in objs),'bounds_world_m':bounds,'source_gis_area_attribute_native_units':round(feature['properties'].get('Shape.STArea()',0),3),'projected_planar_area_m2':round(abs(sum(ring[i].x*ring[(i+1)%N].y-ring[(i+1)%N].x*ring[i].y for i in range(N))/2),3),'source_polygon_vertices':N,'export_materials':sorted({m.name for o in objs if hasattr(o.data,'materials') for m in o.data.materials if m}),'external_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and im.packed_file is None]}
(OUT/'build_report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
