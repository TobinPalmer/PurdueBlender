import bpy, math, json, os
from mathutils import Vector

BLEND=r'modular/buildings/massing_house_301841248_fe939c7.blend'
OUT=r'audit/alpha_xi_delta_fid788'
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene=bpy.context.scene
root=bpy.data.collections.get('Asset_massing_house_301841248_fe939c7')
house=bpy.data.objects['House_301841248']
# Use the asset's existing campus-coordinate footprint as the geometric source.
pts=[(float(v.co.x),float(v.co.y)) for v in house.data.vertices[:16]]
# ensure exact source outline order from bottom ring
n=len(pts)
xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
x0,x1=min(xs),max(xs); y0,y1=min(ys),max(ys)
cx,cy=(x0+x1)/2,(y0+y1)/2

# clear all objects from the one-building asset except its stable root object
for ob in list(root.objects):
    if ob!=house:
        bpy.data.objects.remove(ob,do_unlink=True)
# remove stray scene objects if any, while leaving other data blocks untouched
for ob in list(scene.objects):
    if ob!=house:
        bpy.data.objects.remove(ob,do_unlink=True)

def mat(name, color, rough=.78, metallic=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metallic
    return m
brick=mat('AXiD • warm red-brown brick',(0.30,.12,.075))
cream=mat('AXiD • ivory plaster',(0.79,.73,.62))
timber=mat('AXiD • dark Tudor timber',(.085,.042,.02))
roofmat=mat('AXiD • charcoal slate',(.035,.045,.065),.7)
glass=mat('AXiD • blue-gray glass',(.12,.27,.38),.26)
frame=mat('AXiD • cream window trim',(.88,.83,.72))
wood=mat('AXiD • warm interior wood',(.38,.22,.12))
lightwood=mat('AXiD • floor and stair wood',(.58,.39,.22))
wallmat=mat('AXiD • interior plaster',(.59,.54,.46))
stone=mat('AXiD • limestone',(.65,.59,.49))
blue=mat('AXiD • chapter blue',(.04,.16,.34),.4)
gold=mat('AXiD • chapter gold',(.83,.63,.16),.45,.15)
white=mat('AXiD • warm white',(.91,.87,.79))

# helper build mesh from verts/faces, coords in campus frame
def mesh_obj(name, verts, faces, material, coll=root):
    me=bpy.data.meshes.new(name+'Mesh'); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    ob=bpy.data.objects.new(name,me); coll.objects.link(ob)
    return ob

def box(name, loc, scale, material, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob=bpy.context.object; ob.name=name; ob.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if ob.name not in root.objects: root.objects.link(ob)
    for c in list(ob.users_collection):
        if c!=root: c.objects.unlink(ob)
    ob.data.materials.append(material)
    if bevel:
        mod=ob.modifiers.new('Soft architectural edges','BEVEL'); mod.width=bevel; mod.segments=2
        ob.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return ob

def extruded(name,zlo,zhi,material):
    verts=[(x,y,zlo) for x,y in pts]+[(x,y,zhi) for x,y in pts]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh_obj(name,verts,faces,material)

# Remodel the stable base object as the lower brick story, leaving stable collection and object ID intact.
oldmat=house.data.materials[:]
me=bpy.data.meshes.new('House_301841248_LowerBrickMesh')
verts=[(x,y,z) for z in (0,3.75) for x,y in pts]
faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
me.from_pydata(verts,[],faces); me.materials.append(brick); me.update()
house.data=me; house.name='House_301841248'; house['building_id']='massing_house_301841248_fe939c7'; house['role']='Source-footprint lower brick story'; house['outline_source']='Purdue GIS BuildingShapesZip4 FeatureServer FID 788; footprint mesh simplified from imported candidate outline';
upper=extruded('AXiD_Upper_Tudor_Story',3.75,7.35,cream); upper['role']='Upper story massing inferred from exterior photography';
# Main interior floors visible in cutaway
for z in (0.12,3.72,7.28):
    ob=extruded('AXiD_FloorSlab_'+str(z).replace('.','_'),z,z+.12,lightwood if z>0 else stone)
    ob['role']='Schematic floor plate; internal plan is not documented'
# Roof as a simple hip/gable envelope on the main footprint; ridge follows north-south axis.
rx0,rx1=x0+.35,x1-.35; ry0,ry1=y0+.35,y1-.35; eave=7.35; ridge=13.25; half=(rx1-rx0)/2
rv=[(rx0,ry0,eave),(rx1,ry0,eave),(rx1,ry1,eave),(rx0,ry1,eave),(cx,ry0,ridge),(cx,ry1,ridge)]
rf=[(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5),(0,3,2,1)]
roof=mesh_obj('AXiD_DarkSlate_GabledRoof',rv,rf,roofmat); roof['role']='Roof form estimated from current exterior photos and artist illustration'
# roof thickness
sol=roof.modifiers.new('Roof thickness','SOLIDIFY'); sol.thickness=.22

# Exterior windows as framed blue-gray glazing on perimeter elevations.
def window_x(name,x,y,z,w=1.28,h=1.48,front=False):
    # x is façade plane; slight offset toward outside
    pane=box(name+'_Glass',(x,y,z),(0.11,w,h),glass,.015)
    pane['role']='Window position approximated from exterior photo'
    for yy in (y-w/2-.07,y+w/2+.07): box(name+'_Jamb',(x-.055,yy,z),(.18,.12,h+.20),frame,.02)
    for zz in (z-h/2-.08,z+h/2+.08): box(name+'_SillHead',(x-.06,y,zz),(.20,w+.25,.13),frame,.02)
    box(name+'_Mullion',(x-.12,y,z),(.12,.075,h),frame,.01)
    box(name+'_Crossbar',(x-.12,y,z),(.12,w,.065),frame,.01)
    return pane

def window_y(name,y,x,z,w=1.25,h=1.5):
    box(name+'_Glass',(x,y,z),(w,.11,h),glass,.015)
    for xx in (x-w/2-.07,x+w/2+.07): box(name+'_Jamb',(xx,y-.055,z),(.12,.18,h+.20),frame,.02)
    for zz in (z-h/2-.08,z+h/2+.08): box(name+'_SillHead',(x,y-.06,zz),(w+.25,.20,.13),frame,.02)
    box(name+'_Mullion',(x,y-.12,z),(.075,.12,h),frame,.01)
    box(name+'_Crossbar',(x,y-.12,z),(w,.12,.065),frame,.01)

# West elevation is presented as the front/courtyard approach; place windows away from central entry.
frontx=x0-.08
frontys=[y0+3.0,y0+6.8,y0+17.5,y0+21.2,y0+24.4]
for i,y in enumerate(frontys):
    window_x('AXiD_FrontWindow_%02d'%i,frontx,y,2.15,1.5,1.55,True)
    window_x('AXiD_UpperWindow_%02d'%i,frontx-.10,y,5.35,1.45,1.55,True)
# Tudor timber bands and uprights along the west and south facades
for z in (3.82,4.02,7.22): box('Tudor_Horizontal_West',(x0-.20,cy,z),(.28,y1-y0,.20),timber,.035)
for y in [y0+.35]+[y0+2.4*i for i in range(1,12) if y0+2.4*i<y1]:
    box('Tudor_Upright_West',(x0-.20,y,5.5),(.28,.22,3.35),timber,.035)
# modest diagonal braces in visible bays
for y in (y0+3.6,y0+8.0,y0+19.0,y0+23.0):
    # simple diagonal bars angled in facade plane
    ob=box('Tudor_Diagonal_West',(x0-.22,y,5.5),(.24,1.9,.18),timber,.03); ob.rotation_euler[0]=math.radians(45)
# windows on rear and end elevations
for i,x in enumerate([x0+3.3,x0+7.2,x0+12.0,x0+16.7,x0+20.2]):
    window_y('AXiD_SouthWindow_%02d'%i,y0-.06,x,2.15,1.35,1.48)
    window_y('AXiD_NorthWindow_%02d'%i,y1+.06,x,2.15,1.35,1.48)
for i,y in enumerate([y0+4.5,y0+10,y0+17,y0+23]):
    window_x('AXiD_EastWindow_%02d'%i,x1+.06,y,2.15,1.35,1.48)

# Entry portico, central stairs, stone surround, door and chapter mark.
entry_y=cy
portico_x=x0-.95
box('AXiD_EntryPorchRoof',(portico_x,entry_y,4.05),(2.25,4.7,.28),timber,.06)
for yy in (entry_y-1.95,entry_y+1.95): box('AXiD_PorticoPost',(portico_x,yy,2.0),(.28,.28,4.0),stone,.04)
box('AXiD_EntryDoor',(x0-.14,entry_y,1.55),(.18,1.55,2.65),wood,.04)
box('AXiD_EntryDoorPanel',(x0-.25,entry_y,1.55),(.08,1.12,2.15),timber,.03)
# stone arch cue, lintel and side jambs
for yy in (entry_y-.9,entry_y+.9): box('AXiD_StoneJamb',(x0-.22,yy,1.8),(.32,.22,3.05),stone,.04)
box('AXiD_StoneLintel',(x0-.22,entry_y,3.32),(.32,2.02,.28),stone,.04)
for i in range(6):
    z=.25+i*.28; d=(i+1)*.48
    box('AXiD_EntryStep_%02d'%i,(x0-1.1-d/2,entry_y,z),(d,3.2,.25),stone,.04)
# signage and three Greek letters on upper façade
bpy.ops.object.text_add(location=(x0-.43,entry_y,3.78),rotation=(math.radians(90),0,math.radians(90)))
t=bpy.context.object; t.name='AXiD_ChapterSign_Text'; t.data.body='ALPHA XI DELTA  •  ALPHA ETA'; t.data.size=.38; t.data.extrude=.015; t.data.materials.append(blue); root.objects.link(t)
for c in list(t.users_collection):
    if c!=root: c.objects.unlink(t)
t['role']='Sign text supported by current chapter photo; exact sign dimensions are illustrative'
# prominent chapter letters to the right of entry
bpy.ops.object.text_add(location=(x0-.36,entry_y-5.0,5.6),rotation=(math.radians(90),0,math.radians(90)))
g=bpy.context.object; g.name='AXiD_GreekLetters'; g.data.body='ΑΞΔ'; g.data.size=1.0; g.data.extrude=.025; g.data.materials.append(gold); root.objects.link(g)
for c in list(g.users_collection):
    if c!=root: c.objects.unlink(g)

# Two restrained roof dormers on the west-facing roof slope.
for j,y in enumerate((cy-4.0,cy+4.0)):
    dx=x0+2.8; z=9.35
    box('AXiD_Dormer_%d'%j,(dx,y,z),(1.1,2.6,1.9),cream,.035)
    window_x('AXiD_DormerWindow_%d'%j,x0+2.15,y,z,1.15,1.25,True)
    ob=box('AXiD_DormerCap_%d'%j,(dx-.05,y,10.40),(2.05,2.9,.18),roofmat,.025)

# schematic interior: lobby/common room and generic partitions/furniture, intentionally not a claimed surveyed plan
for y in (cy-4.4,cy+4.4):
    box('Interior_Partition_Lower',(cx,y,2.0),(x1-x0-3.0,.13,3.65),wallmat,.02)
    box('Interior_Partition_Upper',(cx,y,5.55),(x1-x0-3.0,.13,3.2),wallmat,.02)
# cross walls make generic rooms; leave front door axis open
for x in (cx-5.0,cx+5.0):
    box('Interior_CrossWall_Lower',(x,cy,2.0),(.13,y1-y0-3.0,3.65),wallmat,.02)
    box('Interior_CrossWall_Upper',(x,cy,5.55),(.13,y1-y0-3.0,3.2),wallmat,.02)
# lobby floor entry rug and living/dining pieces
box('Interior_Lobby_Rug',(cx,cy,0.30),(5.0,6.0,.08),blue,.03)
box('Interior_DiningTable',(cx+3.0,cy+6.0,4.08),(4.0,2.0,.16),wood,.06)
for x in (cx+1.3,cx+4.7):
    for y in (cy+4.8,cy+7.2): box('Interior_DiningChair',(x,y,3.55),(.7,.7,1.0),lightwood,.06)
box('Interior_LoungeTable',(cx-3.0,cy-5.5,4.08),(2.5,1.2,.15),wood,.05)
for xx,yy in ((cx-4.8,cy-5.5),(cx-1.2,cy-5.5)):
    box('Interior_LoungeSeat',(xx,yy,4.65),(1.2,.9,.8),blue,.10)
# Ground-level common lounge/dining furniture; placement is schematic, not a recovered floorplan.
box('Interior_GroundDiningTable',(cx+3.0,cy-5.6,.82),(4.0,2.0,.16),wood,.06)
for x in (cx+1.3,cx+4.7):
    for y in (cy-6.8,cy-4.4): box('Interior_GroundDiningChair',(x,y,.48),(.7,.7,.8),lightwood,.06)
box('Interior_GroundLoungeSeat',(cx-3.0,cy+6.0,.72),(3.0,1.0,.8),blue,.10)
box('Interior_GroundLoungeTable',(cx-3.0,cy+4.2,.56),(2.1,1.1,.12),wood,.04)

# stair stack visible in cutaway, along entry-to-interior axis
for i in range(12):
    box('Interior_StairStep_%02d'%i,(cx-5.6+i*.30,cy,4.0+i*.28),(.42,1.55,.17),lightwood,.02)
# upper corridor/bedroom beds are schematic
for xx,yy in ((cx-5.0,cy-8.0),(cx+5.0,cy+8.0)):
    box('Interior_UpperBed',(xx,yy,7.48),(2.1,3.0,.25),white,.06)
    box('Interior_UpperHeadboard',(xx,yy-1.35,7.85),(2.2,.18,.65),wood,.04)

# Arrange scene, create render camera and lighting. Render files are evidence only; saved asset opens with shell visible.
def aim(ob, target): ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
# backdrop/ground outside the asset collection is not added to the building library
bpy.ops.mesh.primitive_plane_add(size=200, location=(cx,cy,-.24)); ground=bpy.context.object; ground.name='PreviewGround'; ground.data.materials.append(mat('Preview • neutral green ground',(.24,.29,.22))); ground.hide_set(True); ground.hide_render=False
# camera
camdata=bpy.data.cameras.new('AXiD_PreviewCamera'); cam=bpy.data.objects.new('AXiD_PreviewCamera',camdata); scene.collection.objects.link(cam)
cam.location=(x0-47,y0-33,24); aim(cam,(cx,cy,4.4)); camdata.lens=52; scene.camera=cam
# lights
for name,loc,power,size in [('Key',(x0-22,y0-23,34),120,18),('Fill',(x1+20,cy+10,22),45,16),('Rim',(cx, y1+25,28),90,14)]:
    ld=bpy.data.lights.new(name,'AREA'); lo=bpy.data.objects.new(name,ld); scene.collection.objects.link(lo); lo.location=loc; ld.energy=power; ld.shape='DISK'; ld.size=size; aim(lo,(cx,cy,4))
scene.render.engine='BLENDER_EEVEE'; scene.eevee.taa_render_samples=32
scene.render.resolution_x=1500; scene.render.resolution_y=1125; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.world.color=(.02,.02,.02)
if scene.world.use_nodes:
    bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND'); bg.inputs['Color'].default_value=(.08,.08,.08,1)
scene.view_settings.view_transform='Standard'; scene.view_settings.exposure=-1.25
scene.render.filepath=os.path.abspath(OUT+'/exterior_preview.png')
# Hide context objects from asset collection linking; only building content stays in named asset collection.
for ob in (ground,cam):
    pass
# enforce materials and object transforms
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.render.render(write_still=True)
# Interior cutaway render: hide the two opaque mass volumes and roof, retaining floors, interior layout and exterior details.
for ob in (house,upper,roof): ob.hide_render=True
# Ground-floor cutaway: remove roof/envelope and upper floor plates to expose a single readable schematic level.
for ob in bpy.data.objects:
    if ob.name.startswith(('AXiD_FrontWindow','AXiD_UpperWindow','AXiD_EastWindow','AXiD_SouthWindow','AXiD_NorthWindow','Tudor_','AXiD_Dormer','AXiD_GreekLetters','AXiD_ChapterSign','AXiD_EntryPorch','AXiD_PorticoPost','AXiD_Stone','AXiD_EntryDoor','AXiD_EntryStep')):
        ob.hide_render=True
    if ob.name.startswith(('AXiD_FloorSlab_3_72','AXiD_FloorSlab_7_28','Interior_Partition_Upper','Interior_CrossWall_Upper','Interior_Upper')):
        ob.hide_render=True
# Raised oblique plan camera into the west side of the cutaway.
cam.location=(x0-29,cy-20,31); aim(cam,(cx,cy,.7)); camdata.lens=58
scene.render.filepath=os.path.abspath(OUT+'/interior_cutaway_preview.png')
bpy.ops.render.render(write_still=True)
print('SAVED',BLEND,'BOUNDS',(x0,x1,y0,y1),'N',n,'OBJECTS',len(scene.objects))

