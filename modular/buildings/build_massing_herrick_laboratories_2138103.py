import bpy, json, math, os
from mathutils import Vector

ASSET_ID='massing_herrick_laboratories_2138103'
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
ASSET_PATH=os.path.join(ROOT,'modular','buildings',ASSET_ID+'.blend')
AUDIT=os.path.join(ROOT,'audit',ASSET_ID)
SOURCE=os.path.join(AUDIT,'sources','purdue_building_shapes_fid246_herl_2026-10-26.json')
R2=os.path.join(AUDIT,'r2')
os.makedirs(R2,exist_ok=True)
COLLECTION_NAME='Asset_'+ASSET_ID
SCENE_NAME='Building_'+ASSET_ID

with open(SOURCE,encoding='utf-8-sig') as f:
    feature=json.load(f)['features'][0]
assert feature['attributes']['FID']==246 and feature['attributes']['BLDG_ABBR']=='HERL'
raw=feature['geometry']['rings'][0]
ring=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in raw]
if ring[0]==ring[-1]: ring=ring[:-1]
clean=[]
for p in ring:
    if not clean or math.dist(p,clean[-1])>.01: clean.append(p)
if len(clean)>2 and math.dist(clean[0],clean[-1])<=.01: clean.pop()
ring=clean
assert len(ring)>3
area2=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))
ccw=area2>0
ring_area_m2=abs(area2)/2
# The returned FID 246 polygon is retained vertex-for-vertex after duplicate cleanup.
# A valid single-ring polygon gives ~2993.81 m2 in the project's local approximation;
# the service's Shape__Area field says 5174.79 m2. The source metadata does not explain
# the conflict. Use the returned boundary, never the area attribute, for the shell.
gis_area_m2=feature['attributes'].get('Shape__Area')
area_discrepancy_ratio=(gis_area_m2/ring_area_m2) if gis_area_m2 and ring_area_m2 else None

# Preserve the building's campus-coordinate frame and stable manifest IDs.
scene=bpy.data.scenes.get(SCENE_NAME) or bpy.context.scene
scene.name=SCENE_NAME
for ob in list(bpy.data.objects): bpy.data.objects.remove(ob,do_unlink=True)
for child in list(scene.collection.children): scene.collection.children.unlink(child)
for col in list(bpy.data.collections):
    if col.users==0: bpy.data.collections.remove(col)
coll=bpy.data.collections.new(COLLECTION_NAME); scene.collection.children.link(coll)
rig=bpy.data.collections.new('Render_Setup_Herrick'); scene.collection.children.link(rig)

mats={}
def material(name,color,rough=.78,metal=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    mats[name]=m; return m
brick=material('Herrick | red-brown brick',(.34,.085,.052),.84)
brick_light=material('Herrick | brick piers',(.46,.15,.09),.84)
cream=material('Herrick | pale stone / painted trim',(.68,.63,.54),.7)
roofmat=material('Herrick | red tile roof',(.25,.045,.035),.9)
flatmat=material('Herrick | low-wing roof',(.30,.31,.29),.9)
glass=material('Herrick | blue-gray glazing',(.025,.13,.18),.26,.1)
frame=material('Herrick | dark metal frames',(.08,.095,.10),.55,.25)
concrete=material('Herrick | concrete entry',(.48,.47,.43),.9)

parts=[]
def add_mesh(name,verts,faces,mat,face_indices=None):
    mesh=bpy.data.meshes.new(name+' mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(mat)
    if face_indices:
        for poly,idx in zip(mesh.polygons,face_indices): poly.material_index=idx
    mesh.update(); ob=bpy.data.objects.new(name,mesh); coll.objects.link(ob); parts.append(ob); return ob

def add_box(name,center,dims,mat,angle=0.0):
    x,y,z=center; dx,dy,dz=[v/2 for v in dims]
    local=[(-dx,-dy,-dz),(dx,-dy,-dz),(dx,dy,-dz),(-dx,dy,-dz),(-dx,-dy,dz),(dx,-dy,dz),(dx,dy,dz),(-dx,dy,dz)]
    c,s=math.cos(angle),math.sin(angle)
    verts=[(x+u*c-v*s,y+u*s+v*c,z+w) for u,v,w in local]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return add_mesh(name,verts,faces,mat)

def extruded_footprint(name,poly,z0,z1,mat):
    n=len(poly); verts=[(x,y,z0) for x,y in poly]+[(x,y,z1) for x,y in poly]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
    return add_mesh(name,verts,faces,mat)

# Exact official FID 246 footprint forms the low wings and central base. The 2009
# institutional photos show one-story flanking wings against a distinctly taller barn;
# without a scale-bearing elevation, retain an explicitly estimated 5.0 m wing height.
# The photo supports relative massing only, not this measured value.
wing_height=5.0
extruded_footprint('Herrick Acoustics | official GIS structural footprint',ring,0.0,wing_height,brick)

xs=[p[0] for p in ring]; ys=[p[1] for p in ring]
# GIS geometry reads as a U-shaped courtyard, open to the north. The gabled barn core
# is positioned on the south crossbar; its exact internal wall line is not surveyed.
center_x=(min(xs)+max(xs))/2
barn_x0,barn_x1=-630.8,-596.0
barn_y0,barn_y1=-519.8,-489.1
wall_eave=6.9  # photo-derived estimate; no dimensioned elevation is available
add_box('Herrick Acoustics | raised historic barn walls',((barn_x0+barn_x1)/2,(barn_y0+barn_y1)/2,(wing_height+wall_eave)/2),(barn_x1-barn_x0,barn_y1-barn_y0,wall_eave-wing_height),brick)
# The courtyard photo shows the barn's broad gable facing the courtyard, with the ridge
# running back from the entrance. Two roof planes now slope across the facade width.
# Roof pitch/height remains photo-derived; no dimensioned elevation is available.
y_ridge=(barn_y0+barn_y1)/2; x_ridge=(barn_x0+barn_x1)/2; ridge_z=9.25; eave_z=wall_eave
roofv=[(barn_x0,barn_y0,eave_z),(x_ridge,barn_y0,ridge_z),(x_ridge,barn_y1,ridge_z),(barn_x0,barn_y1,eave_z),
       (x_ridge,barn_y0,ridge_z),(barn_x1,barn_y0,eave_z),(barn_x1,barn_y1,eave_z),(x_ridge,barn_y1,ridge_z)]
add_mesh('Herrick Acoustics | pitched red barn roof',roofv,[(0,1,2,3),(4,5,6,7)],roofmat)
# Gable walls under the front and rear roof planes.
for y in (barn_y0,barn_y1):
    add_mesh('Herrick Acoustics | gable end',[(barn_x0,y,eave_z),(barn_x1,y,eave_z),(x_ridge,y,ridge_z)],[(0,1,2)],brick)
# Cupola on center ridge, matching the archival exterior photo.
cx=(barn_x0+barn_x1)/2; cy=y_ridge
add_box('Herrick Acoustics | cupola base', (cx,cy,9.85),(2.9,2.7,1.0),brick)
for angle in (0,math.pi/2):
    # louver openings shown as dark inset panels on two pairs of faces
    add_box('Herrick Acoustics | cupola louver', (cx,cy,9.85),(2.05,.04,.42),frame,angle)
# Four-sided pyramidal cupola cap.
cap_base_z=10.36; cap_top_z=10.95; r=1.75
vv=[(cx-r,cy-r,cap_base_z),(cx+r,cy-r,cap_base_z),(cx+r,cy+r,cap_base_z),(cx-r,cy+r,cap_base_z),(cx,cy,cap_top_z)]
add_mesh('Herrick Acoustics | cupola cap',vv,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],roofmat)

# Long ribbon windows on each outer and courtyard-facing perimeter wall. The historic
# courtyard photo shows tighter, repeated glazing bays divided by slender piers than the
# first pass. Use ~3 m centers and align support piers to this rhythm.
def outward(a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    return (dy/length,-dx/length) if ccw else (-dy/length,dx/length)
for i,a in enumerate(ring):
    b=ring[(i+1)%len(ring)]; dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    if length<5.0: continue
    nx,ny=outward(a,b); angle=math.atan2(dy,dx)
    count=max(1,round(length/3.1))
    for j in range(count):
        t=(j+.5)/count; px=a[0]+dx*t+nx*.055; py=a[1]+dy*t+ny*.055
        width=min(2.25,length/count*.72)
        add_box('Herrick Acoustics | wing window frame',(px,py,2.72),(width, .16, 1.55),frame,angle)
        add_box('Herrick Acoustics | wing window glazing',(px+nx*.09,py+ny*.09,2.72),(width-.25,.055,1.28),glass,angle)
        # Two narrow vertical mullions subdivide each wide glazing bay.
        for u in (-width*.22,width*.22):
            ux,uy=u*math.cos(angle),u*math.sin(angle)
            add_box('Herrick Acoustics | wing window mullion',(px+ux+nx*.13,py+uy+ny*.13,2.72),(.065,.07,1.42),frame,angle)
        # Pale sill and head band define the continuous horizontal window strip.
        add_box('Herrick Acoustics | wing window sill',(px+nx*.10,py+ny*.10,1.92),(width+.10,.18,.14),cream,angle)
        add_box('Herrick Acoustics | wing window head',(px+nx*.10,py+ny*.10,3.52),(width+.10,.16,.14),cream,angle)
# Light horizontal cornice bands on courtyard and long outer wing facades are represented by a
# restrained trim line along perimeter edges; support posts are limited to long visible elevations.
for i,a in enumerate(ring):
    b=ring[(i+1)%len(ring)]; dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    if length<12: continue
    nx,ny=outward(a,b); ang=math.atan2(dy,dx); mid=((a[0]+b[0])/2+nx*.08,(a[1]+b[1])/2+ny*.08,4.85)
    add_box('Herrick Acoustics | wing eave trim',mid,(length,.22,.18),cream,ang)
    nposts=max(1,int(length/3.5))
    for j in range(nposts+1):
        t=j/nposts; px=a[0]+dx*t+nx*.13; py=a[1]+dy*t+ny*.13
        add_box('Herrick Acoustics | courtyard facade pier',(px,py,2.7),(.23,.30,4.9),cream,ang)

# Central courtyard entrance on the barn's north-facing elevation.
front_y=barn_y1+.42; door_x=cx  # project entrance trim beyond the wall plane for a readable elevation
add_box('Herrick Acoustics | central entrance glazing',(door_x,front_y,1.8),(6.4,.16,3.4),frame)
add_box('Herrick Acoustics | central entrance glass',(door_x,front_y+.11,1.8),(5.95,.05,3.05),glass)
add_box('Herrick Acoustics | entrance transom',(door_x,front_y+.14,3.55),(6.0,.08,.42),cream)
# Door mullions make the photo-supported multi-panel entrance legible at massing scale.
for xoff in (-1.95,-.65,.65,1.95):
    add_box('Herrick Acoustics | entrance door mullion',(door_x+xoff,front_y+.17,1.78),(.075,.07,3.0),frame)
add_box('Herrick Acoustics | entrance threshold',(door_x,front_y+.12,.12),(7.0,.5,.24),cream)
# Wide canopy fascia and four slim supports reflect the photographed entrance bay.
add_box('Herrick Acoustics | entrance canopy',(door_x,front_y+1.1,3.8),(14.2,2.2,.32),cream)
for xoff in (-6.3,-3.2,3.2,6.3): add_box('Herrick Acoustics | canopy column',(door_x+xoff,front_y+.25,1.9),(.26,.32,3.8),cream)
# Sign converted to mesh; the wording is directly legible in the archival photo.
cu=bpy.data.curves.new('Herrick Laboratories sign text','FONT'); cu.body='HERRICK LABORATORIES'; cu.size=1.05; cu.extrude=.012; cu.align_x='CENTER'
text=bpy.data.objects.new('Herrick Acoustics | entrance lettering',cu); coll.objects.link(text); text.location=(door_x,front_y+.22,4.35); text.rotation_euler=(math.radians(-90),0,0); text.scale.y=-1
bpy.context.view_layer.objects.active=text; text.select_set(True); bpy.ops.object.convert(target='MESH'); text.select_set(False); parts.append(bpy.context.object)

# Main barn facade window groupings follow the photo's paired side bays around the entry.
# Their stationing is illustrative; the image has no dimensioned facade measurements.
for offset in (-14.0,-10.0,-6.7,6.7,10.0,14.0):
    add_box('Herrick Acoustics | barn facade window frame',(door_x+offset,front_y,2.35),(2.75,.14,1.55),frame)
    add_box('Herrick Acoustics | barn facade glazing',(door_x+offset,front_y+.10,2.35),(2.4,.05,1.28),glass)
    add_box('Herrick Acoustics | barn facade window sill',(door_x+offset,front_y+.12,1.56),(2.85,.18,.12),cream)
# Two front-slope dormers visible in the archival facade photo. Locate each just above
# the roof plane at its x station; these are visual approximations, not measured sections.
for dxoff in (-9.0,9.0):
    dormer_y=barn_y1-4.5
    roof_at_station=eave_z+(abs(dxoff)/(barn_x1-barn_x0)*2)*(ridge_z-eave_z)
    dormer_z=roof_at_station+.45
    add_box('Herrick Acoustics | roof dormer brick cheeks',(door_x+dxoff,dormer_y,dormer_z),(4.4,2.0,1.25),brick)
    add_box('Herrick Acoustics | dormer window',(door_x+dxoff,dormer_y+.95,dormer_z),(3.55,.12,.72),glass)
    add_box('Herrick Acoustics | dormer hood',(door_x+dxoff,dormer_y+.45,dormer_z+.73),(4.8,2.35,.18),roofmat)

# Join all building parts into a single portable mesh, preserving material slots.
for ob in list(coll.objects):
    if ob.type=='MESH': parts.append(ob)
parts=list(dict.fromkeys(parts))
for ob in parts: ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
model=bpy.context.object; model.name='Herrick Acoustics | historic barn and wings'
for c in list(model.users_collection):
    if c!=coll: c.objects.unlink(model)
if coll not in model.users_collection: coll.objects.link(model)
model.select_set(False)

# Simple camera, lights and ground live outside the exported building collection.
def link_rig(obj): rig.objects.link(obj); return obj
# Ground plane for render only.
mat_ground=material('Render | pale courtyard ground',(.68,.70,.69),.95)
add_ground_mesh=bpy.data.meshes.new('Render ground mesh'); add_ground_mesh.from_pydata([(-850,-700,-.08),(-350,-700,-.08),(-350,-300,-.08),(-850,-300,-.08)],[],[(0,1,2,3)]); add_ground_mesh.materials.append(mat_ground)
ground=bpy.data.objects.new('Render only | ground',add_ground_mesh); link_rig(ground)

def aim(obj,point): obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('Herrick facade camera'); cam=bpy.data.objects.new('Herrick facade camera',cam_data); link_rig(cam)
cam.location=(center_x,-414,20); aim(cam,(center_x,-495,4)); cam.data.type='ORTHO'; cam.data.ortho_scale=118; scene.camera=cam

def area_light(name,loc,power,size,target):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    obj=bpy.data.objects.new(name,data); link_rig(obj); obj.location=loc; aim(obj,target)
area_light('Key light',(-655,-450,62),4800,42,(center_x,-495,4))
area_light('Fill light',(-570,-460,48),2800,35,(center_x,-495,4))
world=bpy.data.worlds.new('Herrick preview world') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(.68,.72,.78,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'; scene.display.shading.studio_light='paint.sl'; scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True; scene.display.shading.cavity_type='WORLD'
scene.display.shading.background_type='WORLD'; scene.world.color=(.82,.84,.86)
scene.render.resolution_x=1400; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.render.filepath=os.path.join(R2,'herrick_acoustics_courtyard_preview_r2.png')
bpy.ops.wm.save_as_mainfile(filepath=ASSET_PATH)
bpy.ops.render.render(write_still=True)
# Plan view, separate camera, saved as an evidence render.
plan_data=bpy.data.cameras.new('Herrick plan camera'); plan=bpy.data.objects.new('Herrick plan camera',plan_data); link_rig(plan)
plan.location=(center_x,-495,170); plan.rotation_euler=(0,0,0); plan.data.type='ORTHO'; plan.data.ortho_scale=112
scene.camera=plan; scene.render.resolution_x=1100; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.filepath=os.path.join(R2,'herrick_acoustics_plan_preview_r2.png')
bpy.ops.render.render(write_still=True)
# Keep the hero camera active in the saved library.
scene.camera=cam; scene.render.resolution_x=1400; scene.render.resolution_y=900; scene.render.filepath=os.path.join(R2,'herrick_acoustics_courtyard_preview_r2.png')
bpy.ops.wm.save_as_mainfile(filepath=ASSET_PATH)
print('HERRICK_BUILD_DONE',json.dumps({'asset':ASSET_PATH,'collection':coll.name,'scene':scene.name,'object':model.name,'footprint_vertices':len(ring),'footprint_bounds_m':[[min(xs),max(xs)],[min(ys),max(ys)]],'ring_area_m2':ring_area_m2,'gis_shape_area_attribute_m2':gis_area_m2,'area_attribute_to_ring_ratio':area_discrepancy_ratio,'wing_height_estimate_m':wing_height,'nominal_gis_extrusion_raw':feature['attributes'].get('Extrution'),'height_uncertainty':'No dimensioned elevation found; 36 is interpreted as feet (~10.97 m) but not confirmed; wing height is qualitative photo-derived estimate.','facade_basis':'Purdue 2009 newsletter and Lab Manager original-Herrick photo; exact window/entrance stations not dimensioned.','photos':2}))







