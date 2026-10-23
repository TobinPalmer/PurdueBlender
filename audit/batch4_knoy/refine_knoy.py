import bpy, math, os, json
from mathutils import Vector
ROOT = os.getcwd()
BLEND = os.path.join(ROOT, 'modular', 'buildings', 'knoy_hall.blend')
OUT = os.path.join(ROOT, 'audit', 'batch4_knoy')
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene=bpy.context.scene
# Remove prior generated audit parts before rerun.
for o in list(bpy.data.objects):
    if o.name.startswith('KNOY_Illustrative_') or o.name.startswith('KNOY_Audit_'):
        bpy.data.objects.remove(o, do_unlink=True)
# Remove unsupported cooling tower geometry: imagery supports roof masses and a south-edge panel strip, not this equipment.
obj=bpy.data.objects.get('KNOY_Roof_Cooling_Towers')
if obj:
    bpy.data.objects.remove(obj, do_unlink=True)
# Audit identity/uncertainty notes are embedded in the asset.
scene['roof_evidence']='Google Maps satellite view, 2026 copyright line, zoom scale 50 ft; imagery acquisition date not displayed. Stepped roof and south-edge PV-like strip observed. Cooling tower geometry removed as unverified.'
scene['interior_evidence']='Ground partition trace from Liu thesis Figure 3.19(d); 18 gaps are provisional from the raster. Twelve receive illustrative door leaves where no crossing partition blocks the gap; six stay clear where intersections make a leaf position unverified. Upper-floor and basement layouts/finishes are unverified.'
scene['registration']='GIS footprint manually checked against thesis raster at corners A/B/C; residuals ~0.05-0.07m at selected pixels, but source raster undimensioned and selection uncertainty ~0.13m/pixel; no north arrow, inferred orientation source-image right = north (+Y), down = east (+X).'
# Doors: model in only existing intentional gaps; use a restrained clear-glazed leaf with simple metal jambs.
mat=bpy.data.materials.get('KNOY_Illustrative_Door_Glazing') or bpy.data.materials.new('KNOY_Illustrative_Door_Glazing')
mat.diffuse_color=(0.15,0.22,0.25,1)
mat.use_nodes=True
bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Base Color'].default_value=(0.13,0.20,0.23,1)
bs.inputs['Metallic'].default_value=0.25
bs.inputs['Roughness'].default_value=0.35
frame=bpy.data.materials.get('KNOY_Illustrative_Door_Frame') or bpy.data.materials.new('KNOY_Illustrative_Door_Frame')
frame.diffuse_color=(0.35,0.31,0.24,1)
frame.use_nodes=True
fbs=next(n for n in frame.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
fbs.inputs['Base Color'].default_value=(0.35,0.31,0.24,1)
fbs.inputs['Metallic'].default_value=0.72; fbs.inputs['Roughness'].default_value=0.36

def segment_points(o):
    pts=[o.matrix_world @ v.co for v in o.data.vertices]
    # PCA direction is stable for axis-aligned and diagonal traces.
    c=sum(pts,Vector())/len(pts)
    xx=sum((p.x-c.x)**2 for p in pts); yy=sum((p.y-c.y)**2 for p in pts); xy=sum((p.x-c.x)*(p.y-c.y) for p in pts)
    ang=0.5*math.atan2(2*xy,xx-yy); d=Vector((math.cos(ang),math.sin(ang),0))
    proj=[(p-c).dot(d) for p in pts]
    return c+d*min(proj),c+d*max(proj),d

def cube(name, loc, dims, rot, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims; o.rotation_euler[2]=rot
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material); o['evidence']='Illustrative only: positioned within existing traced access gap; not a surveyed door schedule.'
    return o
for side in list(bpy.data.objects):
    if not side.name.endswith('_AccessSide'): continue
    base_name=side.name[:-11]
    base=bpy.data.objects.get(base_name)
    if not base: continue
    a0,a1,d=segment_points(base); b0,b1,_=segment_points(side)
    pairs=[(p,q) for p in (a0,a1) for q in (b0,b1)]
    p,q=min(pairs,key=lambda pq:(pq[0]-pq[1]).length)
    mid=(p+q)*0.5
    ang=math.atan2(d.y,d.x)
    ident=base_name.replace('KNOY_Ground_TracePartition_','')
    if ident in {'09','13','17','18','20','24'}: continue  # leave cross-partition gaps clear
    # Door leaf stays in the documented gap; swing is not guessed in the source asset.
    door=cube('KNOY_Illustrative_Door_'+ident, (mid.x,mid.y,1.22), (0.90,0.045,2.10), ang, mat)
    door['swing']='Closed in evidence view; opening direction and swing are unverified.'
# Mark openings clearly as provisional in source object names/metadata; no fictitious room fitout added.
# Camera/lighting helpers for evidence renders.
def aim(obj, target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def make_camera(name, loc, target, lens=50):
    data=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,data); scene.collection.objects.link(cam)
    cam.location=loc; data.lens=lens; data.sensor_width=36; aim(cam,target); return cam
# neutral studio daylight
world=scene.world or bpy.data.worlds.new('KNOY_Evidence_World'); scene.world=world; world.use_nodes=True
bg=world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.45,0.50,0.58,1); bg.inputs['Strength'].default_value=0.8
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
# studio area lights
for o in list(scene.objects):
    if o.type=='LIGHT' and o.name.startswith('KNOY_Audit'): bpy.data.objects.remove(o,do_unlink=True)
def area(name, loc, target, power, size):
    d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size
    o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc; aim(o,target)
area('KNOY_Audit_Key',(90,-100,100),(0,0,8),36000,70)
area('KNOY_Audit_Fill',(-100,70,70),(0,0,9),26000,80)
# Exterior oblique: massing and PV panel strip
cam=make_camera('KNOY_Audit_Exterior',(95,-112,82),(0,0,9),52)
scene.camera=cam
scene.render.filepath=os.path.join(OUT,'knoy_exterior_roof_oblique.png')
bpy.ops.render.render(write_still=True)
# Ground interior-eye view looking into several traced partitions and illustrative door fills
cam=make_camera('KNOY_Audit_Interior_Eye',(0.75,-17.0,1.65),(0.75,-28.0,1.65),38)
scene.camera=cam
# isolate from non-ground floors/site/exterior shell to make the partial interior legible
hide=[]
for o in scene.objects:
    if o.name.startswith(('KNOY_FloorSlab_L2','KNOY_FloorSlab_L3','KNOY_FloorSlab_L4','KNOY_FloorSlab_L5','KNOY_FloorSlab_RoofDeck','KNOY_Exterior_Masonry_Walls','KNOY_Fenestration','KNOY_Entrances_And_Canopies','KNOY_Plaza','KNOY_Roof_','KNOY_Structural_Columns')):
        o.hide_render=True; hide.append(o)
scene.render.filepath=os.path.join(OUT,'knoy_interior_eye_level.png'); bpy.ops.render.render(write_still=True)
for o in hide: o.hide_render=False
# top cutaway of ground floor at scale
cam=make_camera('KNOY_Audit_Cutaway',(0,0,120),(0,0,1.3),48)
cam.data.type='ORTHO'; cam.data.ortho_scale=108; scene.camera=cam
# hide roof/upper slabs, all exterior wall except south/east facade still? keep cutaway clear via hide shell and upper stories.
hide=[]
for o in scene.objects:
    if o.name.startswith(('KNOY_FloorSlab_L2','KNOY_FloorSlab_L3','KNOY_FloorSlab_L4','KNOY_FloorSlab_L5','KNOY_FloorSlab_RoofDeck','KNOY_Exterior_Masonry_Walls','KNOY_Fenestration','KNOY_Roof_','KNOY_Structural_Columns','KNOY_Plaza')):
        o.hide_render=True; hide.append(o)
scene.render.filepath=os.path.join(OUT,'knoy_ground_plan_cutaway.png'); bpy.ops.render.render(write_still=True)
for o in hide: o.hide_render=False
# technical shader record and counts
brick=bpy.data.materials.get('KNOY_Purdue_Red_Brick')
brick_info={}
if brick and brick.node_tree:
    tex=next((n for n in brick.node_tree.nodes if n.type=='TEX_BRICK'),None)
    brick_info={'texcoord_source':[(l.from_socket.name,l.to_node.type) for l in brick.node_tree.links if l.from_node.type=='TEX_COORD'], 'brick_width_m':tex.inputs['Brick Width'].default_value if tex else None,'row_height_m':tex.inputs['Row Height'].default_value if tex else None,'scale':tex.inputs['Scale'].default_value if tex else None,'mortar_size':tex.inputs['Mortar Size'].default_value if tex else None}
scene.render.resolution_x=1200; scene.render.resolution_y=900
scene.camera=make_camera('Cam_KNOY_02_Grant_Street_East',(70,-85,65),(0,0,9),50)
# Save clean, with the main render camera and all audit geometry visible in model; evidence cameras remain in asset.
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
with open(os.path.join(OUT,'model_validation.json'),'w') as f:
    json.dump({'object_count':len(scene.objects),'door_fill_count':len([o for o in scene.objects if o.name.startswith('KNOY_Illustrative_Door_') and '.00' not in o.name]),'removed_unverified_roof_towers':obj is not None,'brick_shader':brick_info,'bounds':{},'file':BLEND},f,indent=2)
print('saved',BLEND,'door fills',len([o for o in scene.objects if o.name.startswith('KNOY_Illustrative_Door_')]), 'brick',brick_info)









