import bpy, json, math, os
from mathutils import Matrix, Vector

ASSET = r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/lawson_hall.blend'
GIS = r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/target_buildings_gis.json'
bpy.ops.wm.open_mainfile(filepath=ASSET)
asset = bpy.data.collections['Asset_lawson_hall']
root = bpy.data.objects['AssetRoot_lawson_hall']

# Replace only the prior R7 vestibule geometry.  The vertex sequence is taken
# directly from ordered GIS FID 59 vertices 42 through 51 in target_buildings_gis.json.
removed = []
for ob in list(asset.objects):
    if ob.name.startswith(('LWSN_R7_Vestibule_','LWSN_R7_Entrance_Rail_','LWSN_R7_Entrance_Handrail_')) or ob.name in {'LWSN_R7_GIS_Matched_Vestibule_Canopy','LWSN_R7_Entrance_Canopy','LWSN_R7_North_GIS_Footprint_Closure'}:
        removed.append(ob.name)
        bpy.data.objects.remove(ob, do_unlink=True)

entry = json.load(open(GIS, encoding='utf8'))['LWSN']['world_polygon']
marker = (-282.5, 44.0)
ring = [(round(p[0]-marker[0], 3), round(p[1]-marker[1], 3)) for p in entry]
# FID 59 sequence includes the full transition from the curved Commons shell
# around the southeast vestibule to the south wall. Keep every GIS vertex; the
# source shell already supplies the next south-wall edge after vertex 52.
segments = list(zip(ring[42:52], ring[43:53]))
assert len(segments) == 10 and segments[0][0] == (14.661, -31.902) and segments[-1][1] == (4.2, -42.543)
pts = [segments[0][0]] + [b for a,b in segments]

Z0, ZTOP, ZCANOPY = .80, 3.55, 3.78
props = {
    'source': 'Purdue CS first-floor plan and Purdue GIS FID 59',
    'footprint_status': 'Wall perimeter follows ordered FID 59 boundary vertices 42-53 in the documented local frame.',
    'height_status': 'One-storey wall and canopy heights are appearance estimates from Purdue exterior photographs; not measured.',
    'uncertainty': 'GIS footprint verifies plan perimeter only. Elevation, canopy projection, glazing, mullion spacing, and exact door position are not dimensioned.'
}
glass = bpy.data.materials['LWSN_Curtain_Glass']
bronze = bpy.data.materials['LWSN_Dark_Aluminum_Bronze']
stone = bpy.data.materials['LWSN_Bedford_Limestone']

def create_mesh(name, verts, faces, mat, custom):
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    asset.objects.link(ob)
    ob.parent = root
    ob.matrix_parent_inverse = Matrix.Identity(4)
    for key, value in custom.items(): ob[key] = value
    return ob

def panel(name, a, b, z0, z1, mat, custom):
    return create_mesh(name, [(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)], [(0,1,2,3)], mat, custom)

# The paired entry is on the prominent southeast sloping edge (FID vertices 46-47).
# The plan supplies the opening; exact opening width and leaf split remain illustrative.
door_i = 4  # edge 46->47 in the source ring slice starting at vertex 42
door_a, door_b = segments[door_i]
door_len = math.dist(door_a, door_b)
opening = 2.1
t0, t1 = (1-opening/door_len)/2, 1-(1-opening/door_len)/2
lerp = lambda a,b,t:(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
for i, (a,b) in enumerate(segments):
    if i == door_i:
        l, r = lerp(a,b,t0), lerp(a,b,t1)
        m = lerp(a,b,(t0+t1)/2)
        panel('LWSN_R7_Vestibule_Glass_Panel_%02d'%i, a, l, Z0, ZTOP, glass, props)
        panel('LWSN_R7_Vestibule_Door_Leaf_L', l, m, Z0, ZTOP, glass, {**props,'opening':'Paired entry inferred from plan swing marks; leaf widths illustrative.'})
        panel('LWSN_R7_Vestibule_Door_Leaf_R', m, r, Z0, ZTOP, glass, {**props,'opening':'Paired entry inferred from plan swing marks; leaf widths illustrative.'})
        panel('LWSN_R7_Vestibule_Glass_Panel_%02d'%i, r, b, Z0, ZTOP, glass, props)
    else:
        panel('LWSN_R7_Vestibule_Glass_Panel_%02d'%i, a, b, Z0, ZTOP, glass, props)

# Photo-supported entrance canopy is limited to the principal door wall, rather
# than incorrectly wrapping the whole vestibule perimeter. The wall length is
# GIS-backed; extension and projection below are visual estimates.
L=math.dist(door_a,door_b); tx=(door_b[0]-door_a[0])/L; ty=(door_b[1]-door_a[1])/L
nx,ny=-ty,tx; side=.70; projection=1.20; sagitta=.40
start=(door_a[0]-tx*side,door_a[1]-ty*side); end=(door_b[0]+tx*side,door_b[1]+ty*side)
inner=[(start[0]+(end[0]-start[0])*i/8,start[1]+(end[1]-start[1])*i/8) for i in range(9)]
outer=[]
for i,p in enumerate(inner):
    t=i/8; depth=projection+sagitta*math.sin(math.pi*t)
    outer.append((p[0]+nx*depth,p[1]+ny*depth))
poly=inner+list(reversed(outer)); count=len(poly)
verts=[(x,y,3.43) for x,y in poly]+[(x,y,3.78) for x,y in poly]
faces=[tuple(count+i for i in range(count)),tuple(reversed(range(count)))]
for i in range(count):faces.append((i,(i+1)%count,(i+1)%count+count,i+count))
canopy_props={**props,'feature':'Shallow curved limestone entrance canopy visible in Purdue exterior photograph.','footprint_status':'Centered on the plan/GIS-supported entrance edge; 0.70 m side extensions, 1.20 m projection and 0.40 m convex bow are illustrative estimates.'}
create_mesh('LWSN_R7_Entrance_Canopy',verts,faces,stone,canopy_props)

# Mullions follow actual GIS boundary breaks; member dimensions and vertical spacing are illustrative.
for i,(x,y) in enumerate(pts[:-1]):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x,y,(Z0+ZTOP)/2))
    ob=bpy.context.object; ob.name='LWSN_R7_Vestibule_Mullion_%02d'%i
    ob.dimensions=(.075,.075,ZTOP-Z0); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    asset.objects.link(ob); ob.parent=root; ob.matrix_parent_inverse=Matrix.Identity(4); ob.data.materials.append(bronze)
    ob['evidence_status']='GIS/plan edge position; profile and spacing illustrative.'

# Door frame and pulls align with the plan/GIS opening; their profiles are illustrative.
a=Vector((door_a[0],door_a[1],0)); b=Vector((door_b[0],door_b[1],0)); d=(b-a).normalized()
mid=a.lerp(b,.5); left=a.lerp(b,t0); center=a.lerp(b,(t0+t1)/2); right=a.lerp(b,t1)
normal=Vector((-d.y,d.x,0)); angle=math.atan2(d.y,d.x)
def beam(name, point, length, depth, height, z):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(point.x,point.y,z))
    ob=bpy.context.object; ob.name=name; ob.dimensions=(length,depth,height); ob.rotation_euler.z=angle
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    asset.objects.link(ob); ob.parent=root; ob.matrix_parent_inverse=Matrix.Identity(4); ob.data.materials.append(bronze)
    ob['source']='Purdue entrance photograph and first-floor plan'; ob['evidence_status']='Presence and opening approximate; member dimensions illustrative.'
    return ob
beam('LWSN_R7_Vestibule_Door_Jamb_L',left,.075,.075,2.75,2.175)
beam('LWSN_R7_Vestibule_Door_Jamb_R',right,.075,.075,2.75,2.175)
beam('LWSN_R7_Vestibule_Door_Center_Stile',center,.055,.08,2.75,2.175)
beam('LWSN_R7_Vestibule_Door_Head',center,opening,.075,.08,3.51)
for s in (-1,1): beam('LWSN_R7_Vestibule_Door_Pull_'+str(s),center+d*(s*.38)+normal*.055,.32,.045,.045,1.75)

# Label text is supported by the entrance photograph; typographic size/placement is illustrative.
bpy.ops.object.text_add(location=(center.x+normal.x*.14,center.y+normal.y*.14,3.56))
txt=bpy.context.object;txt.name='LWSN_R7_Vestibule_Sign_Text';txt.data.body='LAWSON COMPUTER SCIENCE BUILDING';txt.data.align_x='CENTER';txt.data.size=.20;txt.data.extrude=.002
txt.rotation_euler=Matrix((Vector((-d.x,-d.y,0)),Vector((0,0,1)),Vector((normal.x,normal.y,0)))).transposed().to_euler()
front=Vector(((door_a[0]+door_b[0])/2+normal.x*(projection+sagitta),(door_a[1]+door_b[1])/2+normal.y*(projection+sagitta),3.49))
txt.location=front+normal*.025;txt.data.size=.22
for c in list(txt.users_collection): c.objects.unlink(txt)
asset.objects.link(txt);txt.parent=root;txt.matrix_parent_inverse=Matrix.Identity(4);txt.data.materials.append(bronze)
txt['source']='Purdue exterior photograph';txt['evidence_status']='Building name source-supported; type size and placement illustrative.'

# GIS FID 59 includes a short north-edge closure between vertices 6 and 7
# that is absent from the prior structural brick baseline. Close this 3.965 m
# plan edge with the building's brick material. The vertical extent is copied
# from the existing schematic exterior wall solely for mass continuity; no
# measured north elevation or opening rhythm was found.
na,nb=ring[6],ring[7]
dx,dy=nb[0]-na[0],nb[1]-na[1]; length=math.hypot(dx,dy); nx,ny=dy/length,-dx/length
thickness=.14; zlo=.80; zhi=14.55
verts=[(na[0],na[1],zlo),(nb[0],nb[1],zlo),(nb[0]+nx*thickness,nb[1]+ny*thickness,zlo),(na[0]+nx*thickness,na[1]+ny*thickness,zlo),
       (na[0],na[1],zhi),(nb[0],nb[1],zhi),(nb[0]+nx*thickness,nb[1]+ny*thickness,zhi),(na[0]+nx*thickness,na[1]+ny*thickness,zhi)]
faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
wall_props={'source':'Purdue GIS FID 59 and Purdue CS first-floor plan','footprint_status':'The north closure follows FID 59 edge 6->7; 3.965 m plan length.','height_status':'14.55 m top copied from the neighboring schematic exterior wall; unverified estimate, not a measured elevation.','facade_status':'Window/opening cadence on this short north edge is unknown; no windows inferred.'}
create_mesh('LWSN_R7_North_GIS_Footprint_Closure',verts,faces,bpy.data.materials['LWSN_Purdue_Red_Brick'],wall_props)

# Steps remain schematic and sit outside the entrance plane.
nx,ny=normal.x,normal.y
for i in range(3):
    loc=(mid.x+nx*(.5+i*.34),mid.y+ny*(.5+i*.34),.70-i*.18)
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=bpy.context.object;ob.name='LWSN_R7_Vestibule_Approach_Tread_%d'%(i+1)
    ob.dimensions=(5.4,.34,.16);ob.rotation_euler.z=angle;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    asset.objects.link(ob);ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.data.materials.append(stone)
    ob['evidence_status']='Steps visible in Purdue entrance photograph; size and placement estimated.'

# Photo-visible stainless guardrails and handrails flank the main stair. Rail
# routing, posts, dimensions and height are illustrative, not surveyed.
steel=bpy.data.materials.get('LWSN_R7_Entrance_Rail_Brushed_Stainless') or bpy.data.materials.new('LWSN_R7_Entrance_Rail_Brushed_Stainless')
steel.use_nodes=True
principled=next((n for n in steel.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
if principled:
    principled.inputs['Base Color'].default_value=(.48,.52,.55,1);principled.inputs['Metallic'].default_value=.68;principled.inputs['Roughness'].default_value=.24
def cylinder_between(name,p0,p1,radius,mat):
    v0=Vector(p0);v1=Vector(p1);axis=v1-v0
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=radius,depth=axis.length,location=(v0+v1)/2)
    ob=bpy.context.object;ob.name=name;ob.rotation_euler=axis.to_track_quat('Z','Y').to_euler()
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection):c.objects.unlink(ob)
    asset.objects.link(ob);ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.data.materials.append(mat)
    ob['source']='Purdue 2024 Lawson entrance photograph';ob['evidence_status']='Rail presence photo-supported; exact arrangement, height, and dimensions illustrative.'
    return ob
for side_sign in (-1,0,1):
    lateral=side_sign*1.95
    p_inner=(mid.x+d.x*lateral+nx*.25,mid.y+d.y*lateral+ny*.25,.80)
    p_outer=(mid.x+d.x*lateral+nx*2.20,mid.y+d.y*lateral+ny*2.20,.35)
    q_inner=(p_inner[0],p_inner[1],1.65);q_outer=(p_outer[0],p_outer[1],1.20)
    cylinder_between('LWSN_R7_Entrance_Rail_Post_'+str(side_sign)+'_A',p_inner,q_inner,.045,steel)
    cylinder_between('LWSN_R7_Entrance_Rail_Post_'+str(side_sign)+'_B',p_outer,q_outer,.045,steel)
    cylinder_between('LWSN_R7_Entrance_Handrail_'+str(side_sign),q_inner,q_outer,.045,steel)

bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.wm.open_mainfile(filepath=ASSET)
print(json.dumps({'saved':bpy.data.filepath,'reopened':os.path.normcase(os.path.abspath(bpy.data.filepath))==os.path.normcase(os.path.abspath(ASSET)),'removed_prior_r7_objects':len(removed),'exact_source_edges':len(segments),'gis_vertex_indices_inclusive':[42,52],'door_boundary_edge_index':46},indent=2))
