import bpy, math, json
from pathlib import Path
from mathutils import Vector

P = Path(bpy.data.filepath)
C = bpy.data.collections['Asset_felix_haas_hall']
AUDIT = Path('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas')

def link_export(o):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    C.objects.link(o)

def box(name, loc, dims, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_export(o)
    if mat:
        o.data.materials.append(mat)
    return o

def mat(name, color, rough=.75):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    return m

stone = bpy.data.materials.get('HAAS_Photo_Limestone') or mat('HAAS_Photo_Limestone', (.69,.61,.47))
stone.diffuse_color = (.69,.61,.47,1)
stone.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (.69,.61,.47,1)
glass = bpy.data.materials.get('HAAS_Photo_BlueGlass') or mat('HAAS_Photo_BlueGlass', (.035,.075,.09), .25)
glass.diffuse_color = (.025,.055,.06,1)
glass.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (.025,.055,.06,1)
brick = bpy.data.materials.get('Purdue_Red_Brick.001')
brick_changes = []
if brick:
    brick.diffuse_color = (.42,.16,.085,1)
    for n in brick.node_tree.nodes:
        if n.type == 'TEX_BRICK':
            n.inputs['Color1'].default_value = (.52,.205,.105,1)
            n.inputs['Color2'].default_value = (.38,.125,.065,1)
            n.inputs['Mortar'].default_value = (.28,.16,.11,1)
            n.inputs['Scale'].default_value = 4.0
            n.inputs['Mortar Size'].default_value = .004
            brick_changes.append('Brick Texture values and scale')
        if n.type == 'BUMP':
            n.inputs['Strength'].default_value = .12
            n.inputs['Distance'].default_value = .0012
            brick_changes.append('Bump reduced')

roofmat=bpy.data.materials.get('HAAS_GooglePhotos_RedClayTiles_estimated')
if roofmat:
    roofmat.diffuse_color=(.065,.008,.003,1)
    for n in roofmat.node_tree.nodes:
        if n.type=='TEX_BRICK':
            n.inputs['Color1'].default_value=(.085,.012,.004,1)
            n.inputs['Color2'].default_value=(.048,.006,.002,1)
            n.inputs['Mortar'].default_value=(.035,.007,.003,1)

# Put the documented lower arched openings visibly in front of the GIS shell,
# whose source mesh is not suitable for a clean boolean opening on this face.
for i,y in enumerate((-7.65,7.65)):
    box('HAAS_Photo_Visible_Arched_Glass_%02d'%i,(13.32,y,3.0),(.055,2.65,2.65),glass)
    for dy in (-1.42,1.42):
        box('HAAS_Photo_Visible_Arch_Jamb_%02d_%s'%(i,str(dy)),(13.38,y+dy,3.0),(.16,.14,2.9),stone)
    box('HAAS_Photo_Visible_Arch_Sill_%02d'%i,(13.38,y,1.55),(.16,2.98,.16),stone)
    cu=bpy.data.curves.new('HAAS Front Arched Head','CURVE');cu.dimensions='3D';cu.bevel_depth=.09;cu.bevel_resolution=3
    sp=cu.splines.new('POLY');sp.points.add(24)
    for k,p in enumerate(sp.points):
        t=math.pi*k/24;p.co=(13.4,y+1.32*math.cos(t),4.1+.52*math.sin(t),1)
    ob=bpy.data.objects.new('HAAS_Photo_Visible_Arch_Head_%02d'%i,cu);C.objects.link(ob);cu.materials.append(stone)
    ob['source']='Purdue Felix Haas Hall entrance photo; opening dimensions remain estimated.'

# Build the 17-step memorial flight: 17 visible top surfaces, 17 uniform rises,
# landing height is retained at 1.50 m. The historic source specifies 17 steps.
for o in list(C.objects):
    if o.name.startswith('HAAS_Photo_Entry_Stair_Tread_'):
        bpy.data.objects.remove(o, do_unlink=True)
count = 17
rise = 1.5 / count
depth = 5.78 / count
step_names = []
for i in range(count):
    top = 1.5 - i*rise
    x0 = 13.35 + i*depth
    o = box('HAAS_Photo_Entry_Stair_Tread_%02d' % i,
            (x0+depth/2, 0, top-.055), (depth+.012,4.6,.11), stone)
    o['tread_number'] = i+1
    o['riser_height_m_estimated'] = rise
    o['source'] = 'Purdue historical timeline documents 17 entrance steps; dimensions estimated from photo and existing raised threshold.'
    step_names.append(o.name)
# Short sloped stone cheek walls at the outer edges of the flight. Low enough to
# preserve the lower arched windows and based on the visible photo step treatment.
for side in (-1,1):
    y = side*2.43
    x0,x1 = 13.55,19.13
    z0,z1 = 1.48,.12
    verts=[(x0,y-.13,z0-.05),(x0,y+.13,z0-.05),(x1,y+.13,z1-.05),(x1,y-.13,z1-.05),
           (x0,y-.13,z0+.42),(x0,y+.13,z0+.42),(x1,y+.13,z1+.42),(x1,y-.13,z1+.42)]
    faces=[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7),(0,3,2,1)]
    me=bpy.data.meshes.new('HAAS Entry Cheek Mesh'); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new('HAAS_Photo_Entry_Low_Stone_Cheek_%s'%('N' if side>0 else 'S'),me)
    C.objects.link(ob); me.materials.append(stone)
    ob['source']='Purdue Felix Haas Hall exterior photo; low cheek wall proportion estimated.'

# Remove the face-sized overlays which covered the arched and rectangular openings.
removed=[]
for o in list(C.objects):
    if o.name.startswith('HAAS_Photo_StonePanel_'):
        removed.append(o.name); bpy.data.objects.remove(o,do_unlink=True)

# Place estimated repeated side windows and stone details on both long elevations.
# The official exterior image shows paired upper rectangular and lower arched
# window language; exact side-bay spacing is not measured.
side_windows=[]
for side in (-1,1):
    y = side*26.04
    sign='S' if side<0 else 'N'
    # Continuous pale base, belt, and cornice bands provide the photographed
    # stone/brick relationship without inventing a fully clad side wall.
    for z,h in [(1.08,.42),(5.15,.20),(9.55,.30)]:
        box('HAAS_Estimated_Side_Stone_Band_%s_%s'%(sign,str(z).replace('.','_')),
            (-6.0,y,z),(38.5,.12,h),stone)
    for idx,x in enumerate([-21,-13,-5,3,10]):
        # upper rectangular glazing
        box('HAAS_Estimated_Side_Upper_Glass_%s_%d'%(sign,idx),(x,y+side*.075,7.45),(2.35,.055,1.65),glass)
        for dx in (-1.27,1.27):
            box('HAAS_Estimated_Side_Upper_Jamb_%s_%d_%s'%(sign,idx,str(dx)),(x+dx,y+side*.11,7.45),(.14,.14,1.93),stone)
        for z in (6.57,8.33):
            box('HAAS_Estimated_Side_Upper_Lintel_%s_%d_%s'%(sign,idx,str(z)),(x,y+side*.11,z),(2.68,.14,.14),stone)
        # lower window with simple arched head profile approximated by a shallow
        # segmented curved trim. The measured image shows ground-floor arches.
        box('HAAS_Estimated_Side_Lower_Glass_%s_%d'%(sign,idx),(x,y+side*.075,3.10),(2.35,.055,2.35),glass)
        for dx in (-1.27,1.27):
            box('HAAS_Estimated_Side_Lower_Jamb_%s_%d_%s'%(sign,idx,str(dx)),(x+dx,y+side*.11,3.0),(.14,.14,2.7),stone)
        box('HAAS_Estimated_Side_Lower_Sill_%s_%d'%(sign,idx),(x,y+side*.11,1.62),(2.68,.14,.15),stone)
        cu=bpy.data.curves.new('HAAS Estimated Arch','CURVE'); cu.dimensions='3D'; cu.bevel_depth=.075; cu.bevel_resolution=2
        sp=cu.splines.new('POLY'); sp.points.add(16)
        for k,p in enumerate(sp.points):
            t=math.pi*k/16
            p.co=(x+1.175*math.cos(t), y+side*.115, 4.22+.72*math.sin(t),1)
        ob=bpy.data.objects.new('HAAS_Estimated_Side_Arch_%s_%d'%(sign,idx),cu);C.objects.link(ob);cu.materials.append(stone)
        ob['source']='https://events.purdue.edu/felix_haas_hall; arch language observed in qualitative Purdue exterior photo; side locations estimated.'
        side_windows.append(ob.name)

# Shrink the unsupported rooftop ornament toward a modest, clearly marked estimate.
cupola=[]
for o in list(C.objects):
    if any(k in o.name.lower() for k in ['cupola','spire']):
        o['shape_height_status']='estimated from image only; no measured elevation or archival overhead source located'
        if o.type=='MESH':
            # Preserve the roof connection and center while reducing vertical dominance.
            o.scale.z *= .62
            o.location.z = 14 + (o.location.z-14)*.62
        cupola.append(o.name)

# Label the plan directly above its walls; positions derive from the published
# nondimensioned floor-plan drawing. Labels identify adjacency, not certified dimensions.
labelmat=mat('HAAS_Plan_Label_Charcoal',(.92,.84,.66),.8)
labeldata=[
 ('STAIR 1', ( -15.05,22.9)), ('STAIR 2',(-22.3,-16.2)), ('STAIR 3',(4.5,5.5)),
 ('ELEVATOR',(-15.4,-14.0)),('RESTROOM 117',(-9.0,-7.0)),('RESTROOM 119',(-5.8,-7.0)),
 ('CONF 111',(0.0,-4.2)),('CONF 101',(0.6,0.0)),('STUDENT ORG',(4.6,-4.5)),
 ('TA OFFICES',( -5.8,1.0)),('OFFICES',(10.5,14.5)),('OFFICES',(-21.7,8.5))]
labels=[]
for i,(txt,(x,y)) in enumerate(labeldata):
    cu=bpy.data.curves.new('HAAS Plan Label Font','FONT');cu.body=txt;cu.size=.82;cu.extrude=.008
    ob=bpy.data.objects.new('HAAS_Plan_Label_%02d'%i,cu);C.objects.link(ob);ob.location=(x,y,3.35);cu.materials.append(labelmat)
    ob['source']='Purdue CS HAAS_first.pdf; plan location traced approximately; labels identify published rooms/core symbols.'
    labels.append(ob.name)

# Keep the GIS wall shell and campus registration geometry untouched.
assert tuple(round(x,2) for x in bpy.data.objects['HAAS_Corrected_GIS_Wall_Envelope'].scale)==(1,1,1)
bpy.ops.wm.save_as_mainfile(filepath=str(P))
Path(AUDIT/'reviewer_corrections.json').write_text(json.dumps({
 'saved_asset':str(P),'GIS_shell_scale':[1,1,1],'entrance_treads':count,'riser_m_estimated':rise,
 'threshold_z_m':1.5,'removed_occluding_panels':removed,'side_window_units':len(side_windows),
 'cupola_spire_objects_tagged_estimated':cupola,'plan_labels':labeldata,
 'brick_adjustments':brick_changes,
 'source':'https://collections.lib.purdue.edu/timelines/puhistorical; https://events.purdue.edu/felix_haas_hall; https://www.cs.purdue.edu/resources/docs/HAAS_first.pdf',
 'limits':'GIS footprint/origin retained. Side window bays, facade dimensions, step dimensions, room scale, and roof ornament height are estimates from qualitative photo or nondimensioned plan. No upper-floor plan or measured elevation found.'
},indent=2))
