import bpy, math, json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "new_psyc"
ASSET_PATH = ROOT / "modular" / "buildings" / "psychological_sciences.blend"
AUDIT.mkdir(parents=True, exist_ok=True)
MASSING = ROOT / "modular" / "buildings" / "massing_psychological_sciences_building_psyc_34efd04.blend"
ORIGIN_X, ORIGIN_Y = -106.6966, -48.2750

bpy.ops.wm.open_mainfile(filepath=str(MASSING))
old = bpy.data.objects['Psychological Sciences Building (PSYC)']
src = old.data
top_polys = [p for p in src.polygons if p.normal.z > 0.5]
edges = {}
for p in top_polys:
    for a,b in zip(p.vertices, list(p.vertices[1:])+[p.vertices[0]]):
        key = tuple(sorted((a,b)))
        edges[key] = edges.get(key, 0) + 1
boundary = [(a,b) for (a,b),n in edges.items() if n == 1]
triangles=[]
for p in top_polys:
    pts=[(src.vertices[i].co.x-ORIGIN_X,src.vertices[i].co.y-ORIGIN_Y) for i in p.vertices]
    if len(pts)==3: triangles.append(pts)

def point_in_triangle(px,py,t):
    (ax,ay),(bx,by),(cx,cy)=t
    d=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
    if abs(d)<1e-9: return False
    u=((by-cy)*(px-cx)+(cx-bx)*(py-cy))/d
    v=((cy-ay)*(px-cx)+(ax-cx)*(py-cy))/d
    w=1-u-v
    return u>=-1e-5 and v>=-1e-5 and w>=-1e-5

def inside_outline(x,y): return any(point_in_triangle(x,y,t) for t in triangles)

scene = bpy.context.scene
for obj in list(scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for col in list(bpy.data.collections):
    if col.name != scene.collection.name:
        bpy.data.collections.remove(col)
asset = bpy.data.collections.new('Asset_psychological_sciences')
scene.collection.children.link(asset)
asset['asset_id'] = 'psychological_sciences'
asset['building_name'] = 'Psychological Sciences Building (PSYC)'
asset['geometry_coordinate_frame'] = 'local meters; local origin is footprint bounds center; X east, Y north, Z up'
asset['evidence_status'] = 'GIS perimeter retained; exterior and interior detail evidence-limited and partly inferred'
asset['interior_status'] = 'five illustrative floor levels; room functions and layouts are schematic, no public PSYC floor plans verified'

def mat(name, color, rough=0.75, metallic=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metallic
    return m

brick=mat('PSYC | warm red-brown brick', (0.39,0.105,0.052), .88)
brick_nt=brick.node_tree; nodes=brick_nt.nodes; links=brick_nt.links
tex=nodes.new('ShaderNodeTexBrick'); tex.inputs['Color1'].default_value=(0.42,0.13,0.072,1); tex.inputs['Color2'].default_value=(0.30,0.075,0.038,1); tex.inputs['Mortar'].default_value=(0.22,0.20,0.17,1); tex.inputs['Scale'].default_value=1.0; tex.inputs['Mortar Size'].default_value=.025; tex.inputs['Mortar Smooth'].default_value=.02; tex.offset=0.5; tex.offset_frequency=2
uv=nodes.new('ShaderNodeTexCoord'); links.new(uv.outputs['UV'],tex.inputs['Vector']); links.new(tex.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
bump=nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.15; bump.inputs['Distance'].default_value=.035; links.new(tex.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],nodes.get('Principled BSDF').inputs['Normal'])
concrete=mat('PSYC | warm precast concrete', (.58,.55,.49), .82)
glass=mat('PSYC | smoked bronze window glass', (.035,.075,.086), .19, .25)
frame=mat('PSYC | dark bronze anodized frames', (.085,.071,.054), .36, .48)
roofmat=mat('PSYC | dark membrane roof', (.075,.085,.09), .88)
floor_mat=mat('PSYC | charcoal gray terrazzo and carpet', (.105,.12,.13), .88)
wallmat=mat('PSYC | warm painted interior partitions', (.52,.46,.37), .9)
wood=mat('PSYC | oak furniture', (.30,.16,.075), .66)
seat=mat('PSYC | charcoal upholstery', (.11,.13,.14), .8)
metal=mat('PSYC | brushed utility metal', (.25,.27,.28), .42, .55)
signmat=mat('PSYC | wayfinding charcoal', (.035,.044,.045), .5)
labelmat=mat('PSYC | cutaway room labels', (1.0,.86,.48), .32)
label_bsdf=next(n for n in labelmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
label_bsdf.inputs['Emission Color'].default_value=(1.0,.78,.30,1.0)
label_bsdf.inputs['Emission Strength'].default_value=1.2

def new_mesh_obj(name, verts, faces, material, collection=asset, uv_faces=None):
    mesh=bpy.data.meshes.new(name+'_Mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(material); mesh.update()
    obj=bpy.data.objects.new(name,mesh); collection.objects.link(obj)
    if uv_faces:
        layer=mesh.uv_layers.new(name='UVMap')
        for pi,coords in enumerate(uv_faces):
            for li,co in zip(mesh.polygons[pi].loop_indices,coords): layer.data[li].uv=co
    return obj

def local(v): return (v.x-ORIGIN_X, v.y-ORIGIN_Y, v.z)

# Rebuild the massing shell as vertical brick envelope panels from the GIS-derived perimeter.
verts=[]; faces=[]; uvfaces=[]; perimeter=[]
wall_h=15.0
entry_x=-8.2; entry_y=-24.30
for ia,ib in boundary:
    a=local(src.vertices[ia].co); b=local(src.vertices[ib].co)
    dx=b[0]-a[0]; dy=b[1]-a[1]; length=math.hypot(dx,dy)
    if length < .15: continue
    split_entry = abs(a[1]-entry_y) < .15 and abs(b[1]-entry_y) < .15 and min(a[0],b[0]) < entry_x < max(a[0],b[0])
    if split_entry:
        lo,hi=sorted((a[0],b[0])); gap_lo,gap_hi=entry_x-1.45,entry_x+1.45
        panels=[(lo,gap_lo,0,wall_h),(gap_hi,hi,0,wall_h),(gap_lo,gap_hi,2.85,wall_h)]
        for x0,x1,z0,z1 in panels:
            if x1-x0 < .02: continue
            st=len(verts); verts += [(x0,a[1],z0),(x1,a[1],z0),(x1,a[1],z1),(x0,a[1],z1)]
            faces.append((st,st+1,st+2,st+3)); uvfaces.append(((0,z0),(x1-x0,z0),(x1-x0,z1),(0,z1)))
    else:
        start=len(verts); verts += [(a[0],a[1],0.0),(b[0],b[1],0.0),(b[0],b[1],wall_h),(a[0],a[1],wall_h)]
        faces.append((start,start+1,start+2,start+3)); uvfaces.append(((0,0),(length,0),(length,wall_h),(0,wall_h)))
    perimeter.append((a,b,length))
walls=new_mesh_obj('PSYC_Exterior_Brick_Envelope',verts,faces,brick,uv_faces=uvfaces); walls['role']='exterior'; walls['source_geometry']='GIS-aligned massing perimeter; wall height retained from source estimate (15 m)'

# Roof slab copies the source roof triangulation at a small parapet inset elevation.
rv=[]; rf=[]
for p in top_polys:
    ids=[]
    for vi in p.vertices:
        q=local(src.vertices[vi].co); ids.append(len(rv)); rv.append((q[0],q[1],14.92))
    rf.append(tuple(ids))
roof=new_mesh_obj('PSYC_Roof_Membrane',rv,rf,roofmat); roof['role']='roof'

# Purdue GIS lists five floors. Exact elevations are unavailable; these levels are
# evenly spaced to fit the inherited 15 m estimated shell height.
floor_levels=[.28,3.24,6.20,9.16,12.12]
asset['gis_feature_id']=239
asset['gis_floor_count']=5
asset['estimated_shell_wall_height_m']=15.0
asset['schematic_floor_levels_m']=floor_levels
for story,z in enumerate(floor_levels):
    floor_verts=[]; floor_faces=[]; base=0
    for p in top_polys:
        for vi in p.vertices:
            q=local(src.vertices[vi].co); floor_verts.append((q[0],q[1],z))
        floor_faces.append(tuple(range(base,base+len(p.vertices)))); base += len(p.vertices)
    floors=new_mesh_obj(f'PSYC_Interior_Floor_S{story}',floor_verts,floor_faces,floor_mat); floors['role']='interior'; floors['story_level_m']=z

# Batch repeated box geometry into a small number of objects.
boxes={}
active_story=None
def add_box(name, center, dims, material, angle=0.0):
    w,d,h=dims; cx,cy,cz=center; co=math.cos(angle); si=math.sin(angle)
    points=[]
    for x,y,z in [(-w/2,-d/2,-h/2),(w/2,-d/2,-h/2),(w/2,d/2,-h/2),(-w/2,d/2,-h/2),(-w/2,-d/2,h/2),(w/2,-d/2,h/2),(w/2,d/2,h/2),(-w/2,d/2,h/2)]:
        points.append((cx+x*co-y*si,cy+x*si+y*co,cz+z))
    faces_local=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    bucket=boxes.setdefault((material.name,active_story),{'material':material,'verts':[],'faces':[],'name':name,'story':active_story})
    off=len(bucket['verts']); bucket['verts'].extend(points); bucket['faces'].extend(tuple(off+i for i in f) for f in faces_local)

def flush_boxes(prefix='PSYC'):
    made={}
    for k,b in boxes.items():
        suffix='' if b['story'] is None else f'_S{b["story"]}'
        obj=new_mesh_obj(prefix+'_'+b['name']+suffix,b['verts'],b['faces'],b['material']); made[k]=obj
    boxes.clear(); return made

# Punched window rhythm, expressed as framed, smoked glazing with brick lintels and precast sills.
for a,b,length in perimeter:
    dx=b[0]-a[0]; dy=b[1]-a[1]; angle=math.atan2(dy,dx)
    mx=(a[0]+b[0])*.5; my=(a[1]+b[1])*.5
    # Radial outward normal from footprint center is a robust approximation for this convex/stepped massing.
    nx,ny=-dy/length,dx/length
    # Select the outward of the two segment normals using the source GIS top-face triangulation.
    if inside_outline(mx+nx*.25,my+ny*.25): nx,ny=-nx,-ny
    count=max(0,int((length-2.0)//3.5))
    for k in range(count):
        u=(k+1)/(count+1); x=a[0]+dx*u; y=a[1]+dy*u
        for story,z0 in enumerate([.30,3.26,6.22,9.18,12.14]):
            zw=z0+1.18
            # Recess shadow, glass panel, perimeter frame and sill/lintel.
            add_box('Window_Shadow', (x+nx*.025,y+ny*.025,zw), (1.72,.10,2.12), signmat,angle)
            add_box('Insulated_Glazing', (x+nx*.09,y+ny*.09,zw), (1.42,.08,1.78), glass,angle)
            add_box('Window_Frame_Horizontal', (x+nx*.14,y+ny*.14,zw), (1.54,.11,.07), frame,angle)
            add_box('Window_Frame_Vertical', (x+nx*.14,y+ny*.14,zw), (.07,.11,1.83), frame,angle)
            add_box('Concrete_Sill', (x+nx*.18,y+ny*.18,z0+.20), (1.88,.24,.18), concrete,angle)
            add_box('Concrete_Lintel', (x+nx*.12,y+ny*.12,z0+2.18), (1.90,.20,.16), concrete,angle)

# Storey bands and parapet cap follow every perimeter segment.
for a,b,length in perimeter:
    angle=math.atan2(b[1]-a[1],b[0]-a[0]); mx=(a[0]+b[0])*.5; my=(a[1]+b[1])*.5; nx,ny=mx/math.hypot(mx,my),my/math.hypot(mx,my)
    for z in (3.00,5.96,8.92,11.88,14.84):
        add_box('Precast_Datum_Band',(mx+nx*.08,my+ny*.08,z),(length+.08,.26,.14),concrete,angle)
    add_box('Parapet_Coping',(mx+nx*.10,my+ny*.10,15.08),(length+.12,.42,.22),concrete,angle)

# Main public entrance faces south (negative local Y), with a recessed glazed vestibule and canopy.
add_box('Entry_Glazed_Double_Doors',(entry_x,entry_y-.08,1.45),(2.35,.16,2.70),glass)
add_box('Entry_Frame_Jambs',(entry_x-1.15,entry_y-.18,1.45),(.12,.20,2.9),frame)
add_box('Entry_Frame_Jambs',(entry_x+1.15,entry_y-.18,1.45),(.12,.20,2.9),frame)
add_box('Entry_Transom',(entry_x,entry_y-.18,2.90),(2.4,.20,.16),frame)
add_box('Entry_Canopy',(entry_x,entry_y-.90,3.25),(6.0,1.8,.28),concrete)
for x in (entry_x-2.45,entry_x+2.45): add_box('Entry_Canopy_Support',(x,entry_y-1.55,1.65),(.18,.18,3.2),frame)
add_box('Entry_Stair_Landing',(entry_x,entry_y-1.55,.18),(5.2,2.2,.35),concrete)
add_box('Entry_Name_Plaque',(entry_x,entry_y-.205,3.65),(4.5,.12,.65),signmat)

# Roof mechanical and skylight elements, deliberately grouped away from primary facade lines.
add_box('Mechanical_Penthouse',(-1,2.5,15.14),(14,7,1.3),concrete)
for x in (-5,0,5): add_box('Rooftop_Louver',(x,2.5,15.84),(1.0,7.15,.50),metal)
for x in (-25,-20,20,25): add_box('Roof_Skylight',(x,4.0,15.04),(4.8,3.5,.16),glass)

# No public PSYC floor plans were located. These floor layouts are explicitly schematic,
# but distinguish teaching, research, participant, office, and circulation functions.
room_names=[
    [('Reception / waiting','Reception'),('Participant suite','Observation'),('Research seminar','Teaching'),('Research office','Office'),('Behavioral lab','Lab'),('Faculty office','Office'),('Graduate research hub','GradHub')],
    [('Faculty offices','Office'),('Cognitive research lab','Lab'),('Interview / testing','Interview'),('Research office','Office'),('Data analysis lab','Computer'),('Graduate research hub','GradHub'),('Research support','Office')],
    [('Faculty offices','Office'),('Developmental research','Lab'),('Interview / testing','Interview'),('Research office','Office'),('Behavioral lab','Lab'),('Graduate research hub','GradHub'),('Research support','Office')],
    [('Faculty offices','Office'),('Cognitive research lab','Lab'),('Research seminar','Teaching'),('Research office','Office'),('Data analysis lab','Computer'),('Graduate research hub','GradHub'),('Research support','Office')],
    [('Faculty offices','Office'),('Cognitive research lab','Lab'),('Research seminar','Teaching'),('Research office','Office'),('Data analysis lab','Computer'),('Graduate research hub','GradHub'),('Research support','Office')]
]
room_xs=(-30,-20,-10,0,10,20,30)
def add_room_label(label,x,y,z,story):
    curve=bpy.data.curves.new('Room_Label_Curve','FONT'); curve.body=label; curve.size=.68; curve.align_x='CENTER'; curve.align_y='CENTER'
    ob=bpy.data.objects.new(f'Schematic_Room_Label_S{story}_'+label.replace(' ','_').replace('/','_'),curve); asset.objects.link(ob); ob.location=(x,y+math.copysign(2.25,y),z+.04); ob.data.materials.append(labelmat); ob['role']='interior_label'

for floor,zbase in enumerate(floor_levels):
    active_story=floor; wh=2.72
    # Continuous, open east-west corridor with deliberate breaks for room doors.
    for side in (-1,1):
        y=side*2.65
        for x in room_xs:
            if not inside_outline(x,side*4.0): continue
            for cx in (x-3.15,x+3.15):
                add_box('Corridor_Wall_Return',(cx,y,zbase+wh/2),(2.7,.16,wh),wallmat)
    # Two room rows connect directly to the corridor. Door gaps remain clear in every bay.
    for row,side in enumerate((1,-1)):
        for i,x in enumerate(room_xs):
            y=side*7.45
            if not inside_outline(x,y): continue
            name,kind=room_names[floor][i]
            outer_y=side*12.25
            add_box('Room_Rear_Wall',(x,outer_y,zbase+wh/2),(8.5,.16,wh),wallmat)
            for sx in (-1,1): add_box('Room_Side_Wall',(x+sx*4.25,y,zbase+wh/2),(.16,9.6,wh),wallmat)
            for sx in (-1,1): add_box('Room_Door_Return',(x+sx*2.85,side*2.65,zbase+wh/2),(2.8,.16,wh),wallmat)
            add_room_label(name,x,y,zbase,floor)
            if kind in ('Office','GradHub'):
                n=1 if kind=='Office' else 3
                for di in range(n):
                    dx=x+(di-(n-1)/2)*2.1
                    add_box('Oak_Research_Desk',(dx,y,zbase+.76),(1.65,.72,.12),wood)
                    add_box('Desk_Pedestal',(dx-.58,y,zbase+.38),(.34,.56,.72),wood)
                    add_box('Research_Chair',(dx,y-side*.85,zbase+.50),(.62,.62,.14),seat)
                    add_box('Desk_Monitor',(dx,y+side*.30,zbase+1.26),(.72,.12,.48),metal)
            elif kind=='Lab':
                for dy in (-1.0,1.0):
                    add_box('Psychology_Research_Bench',(x,y+dy,zbase+.78),(3.6,.82,.14),wood)
                    for dx in (-1.1,0,1.1): add_box('Lab_Workstation_Monitor',(x+dx,y+dy,zbase+1.19),(.48,.10,.36),metal)
                add_box('Lab_Equipment_Cabinet',(x+3.45,y+side*.8,zbase+1.05),(.72,1.1,2.1),metal)
            elif kind=='Interview':
                add_box('Interview_Table',(x,y,zbase+.72),(1.6,1.0,.14),wood)
                for dx in (-1.15,1.15): add_box('Interview_Chair',(x+dx,y,zbase+.48),(.62,.62,.14),seat)
                add_box('Observation_Window',(x,y+side*1.6,zbase+1.85),(1.6,.10,.62),glass)
            elif kind=='Teaching':
                for dx in (-2.4,0,2.4):
                    add_box('Seminar_Table',(x+dx,y,zbase+.74),(1.8,.85,.14),wood)
                    for sy in (-1,1): add_box('Seminar_Chair',(x+dx,y+sy*.7,zbase+.47),(.56,.56,.14),seat)
                add_box('Teaching_Display',(x,y+side*1.9,zbase+1.75),(2.2,.10,1.25),signmat)
            elif kind=='Computer':
                for dx in (-2.4,0,2.4):
                    add_box('Computer_Analysis_Desk',(x+dx,y,zbase+.74),(1.8,.72,.14),wood)
                    add_box('Computer_Monitor',(x+dx,y+side*.2,zbase+1.2),(.78,.12,.48),metal)
                    add_box('Computer_Chair',(x+dx,y-side*.82,zbase+.48),(.58,.58,.14),seat)
            elif kind=='Observation':
                add_box('Observation_Control_Desk',(x,y-side*1.0,zbase+.74),(2.8,.75,.14),wood)
                add_box('One_Way_Observation_Glazing',(x,y+side*1.8,zbase+1.65),(2.5,.10,.95),glass)
                for dx in (-1.4,1.4): add_box('Participant_Chair',(x+dx,y+side*.25,zbase+.48),(.62,.62,.14),seat)
            elif kind=='Reception':
                add_box('Reception_Counter',(x,y+side*1.0,zbase+1.0),(3.4,.78,1.25),wood)
                for dx in (-2.6,-1.3,0,1.3,2.6): add_box('Waiting_Seat',(x+dx,y-side*1.35,zbase+.48),(.68,.70,.14),seat)
            # A door leaf sits inside its framed opening while leaving the doorway passable.
            add_box('Door_Leaf',(x,side*2.65,zbase+1.08),(.92,.055,2.12),wood)

objs=flush_boxes()
for obj in objs.values():
    obj['role']='detail'
    if any(s in obj.name for s in ('Window','Glazing','Concrete_Sill','Concrete_Lintel','Datum_Band','Parapet','Entry')): obj['role']='exterior_detail'
    elif any(s in obj.name for s in ('Corridor','Room_Partition','Desk','Chair','Seminar','Stair')): obj['role']='interior'
    elif 'Roof' in obj.name or 'Mechanical' in obj.name: obj['role']='roof_detail'

# Sign text objects are modeled as raised geometry and travel with the export collection.
def add_text_obj(name,text,location,size,rotation,material):
    curve=bpy.data.curves.new(name+'_Curve','FONT'); curve.body=text; curve.size=size; curve.align_x='CENTER'; curve.align_y='CENTER'; curve.extrude=.008; curve.bevel_depth=.002
    obj=bpy.data.objects.new(name,curve); asset.objects.link(obj); obj.location=location; obj.rotation_euler=rotation; obj.data.materials.append(material); obj['role']='signage'; return obj
add_text_obj('Entry_Wall_Lettering','PSYCHOLOGICAL SCIENCES',(entry_x,entry_y-.30,3.66),.32,(math.pi/2,0,0),concrete)
add_box('Freestanding_Wayfinding_Sign_Plate',(entry_x+4.3,-26.7,1.9),(2.7,.18,1.5),signmat)
add_box('Freestanding_Wayfinding_Sign_Post',(entry_x+4.3,-26.7,.85),(.18,.18,1.7),frame)
add_text_obj('Freestanding_Wayfinding_Sign_Text','PSYCHOLOGICAL\nSCIENCES\nBUILDING',(entry_x+4.3,-26.82,1.92),.24,(math.pi/2,0,0),concrete)

# Store source-data identity/limits in the scene and collection without altering the campus master.
scene.name='Building_psychological_sciences'
scene['building_id']='psychological_sciences'
scene['source_massing_id']='massing_psychological_sciences_building_psyc_34efd04'
scene['bounds_origin_world_m']=[ORIGIN_X,ORIGIN_Y,0.0]
scene['source_evidence']='Purdue GIS feature 239 retrieved 2026-10-23; Purdue Archives history record; Wikimedia Commons building-door and sign photos; Google Maps satellite view checked 2026-10-23.'

# Dedicated stage collection holds presentation camera/lights only; master links the Asset collection.
stage=bpy.data.collections.new('PSYC_Render_Stage'); scene.collection.children.link(stage)
def aim(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def camera(name,loc,target,ortho):
    data=bpy.data.cameras.new(name); obj=bpy.data.objects.new(name,data); stage.objects.link(obj); obj.location=loc; aim(obj,target); data.type='ORTHO'; data.ortho_scale=ortho; return obj
def area(name,loc,power,size,target):
    data=bpy.data.lights.new(name,'AREA'); obj=bpy.data.objects.new(name,data); stage.objects.link(obj); obj.location=loc; data.energy=power; data.shape='DISK'; data.size=size; aim(obj,target)
area('Key', (50,-70,85), 420,70,(0,0,6)); area('Fill',(-55,-5,52),260,60,(0,0,7)); area('Rim',(5,60,48),180,45,(0,0,6))
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1600; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.world.color=(.12,.12,.12)
scene.view_settings.view_transform='Standard'; scene.view_settings.exposure=-2.0; scene.view_settings.gamma=1.0
extcam=camera('QA_Exterior_Overview',(76,-93,76),(0,0,6),118)
entrycam=camera('QA_Entrance_Detail',(12,-70,20),(-8,-22,5),51)
intcam=camera('QA_Interior_Cutaway',(8,-34,45),(0,0,1),78)
scene.camera=extcam

def render(path,cam,hide_names=()):
    scene.camera=cam
    previous={o.name:o.hide_render for o in asset.objects}
    previous_exposure=scene.view_settings.exposure
    fill=None
    if path.stem=='interior_cutaway':
        scene.view_settings.exposure=-1.25
        fill_data=bpy.data.lights.new('PSYC_Cutaway_Fill','AREA'); fill=bpy.data.objects.new('PSYC_Cutaway_Fill',fill_data); stage.objects.link(fill)
        fill.location=(0,-18,36); fill_data.energy=950; fill_data.shape='DISK'; fill_data.size=42; aim(fill,(0,0,0))
    for o in asset.objects:
        if any(s in o.name for s in hide_names): o.hide_render=True
    scene.render.filepath=str(path); bpy.ops.render.render(write_still=True)
    for o in asset.objects: o.hide_render=previous[o.name]
    scene.view_settings.exposure=previous_exposure
    if fill is not None: bpy.data.objects.remove(fill,do_unlink=True)
render(AUDIT/'exterior_overview.png',extcam)
render(AUDIT/'entry_detail.png',entrycam)
render(AUDIT/'interior_cutaway.png',intcam,('Exterior_Brick','Roof_Membrane','Window','Glazing','Concrete_Sill','Concrete_Lintel','Datum_Band','Parapet','Entry_','Freestanding_','Interior_Floor_S1','Interior_Floor_S2','Interior_Floor_S3','Interior_Floor_S4','_S1','_S2','_S3','_S4','Mechanical','Rooftop','Skylight'))

# Keep the deliverable scene uncluttered; render camera/light staging stays in its own collection.
for obj in list(stage.objects):
    bpy.data.objects.remove(obj,do_unlink=True)
bpy.data.collections.remove(stage)
scene.camera=None
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH),compress=True)
try: bpy.data.orphans_purge(do_recursive=True)
except TypeError: bpy.data.orphans_purge()
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH),compress=True)
pts=[o.matrix_world @ Vector(c) for o in asset.all_objects for c in o.bound_box]
bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
print(json.dumps({'saved':str(ASSET_PATH),'boundary_edges':len(perimeter),'objects':len(asset.all_objects),'origin_world_m':[ORIGIN_X,ORIGIN_Y,0],'bounds_local':bounds}))
