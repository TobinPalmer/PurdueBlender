import bpy, json, math
from pathlib import Path
from mathutils import Vector, Quaternion, geometry
import bmesh

ROOT = Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
AUDIT = ROOT / 'audit/phi_mu_fid772'
ASSET = ROOT / 'modular/buildings/massing_house_301836574_fff1661.blend'
FID_JSON = AUDIT / 'purdue_gis_fid772_2026-10-28_4326.json'

# Rebuild the footprint using the project's documented local approximation.
data = json.loads(FID_JSON.read_text(encoding='utf-8'))
feat = data['features'][0]
ring_ll = feat['geometry']['rings'][0][:-1]
ring = [((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
         (lat - 40.4274) * 111040.0) for lon, lat in ring_ll]
cx = sum(p[0] for p in ring) / len(ring)
cy = sum(p[1] for p in ring) / len(ring)
ring = [(x, y) for x, y in ring]
xmin, xmax = min(x for x, y in ring), max(x for x, y in ring)
ymin, ymax = min(y for x, y in ring), max(y for x, y in ring)
width, depth = xmax-xmin, ymax-ymin

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
asset_col = bpy.data.collections.get('Asset_massing_house_301836574_fff1661')
if asset_col is None:
    raise RuntimeError('Expected stable asset collection missing')
for obj in list(asset_col.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

def mat(name, color, rough=0.82, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1.0)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metallic
    return m

brick = mat('PhiMu_Red_Brick_Illustrative', (0.26, 0.068, 0.036))
cream = mat('PhiMu_Painted_White_Trim', (0.88, 0.85, 0.77))
roofmat = mat('PhiMu_Dark_Slate_Roof', (0.035, 0.043, 0.052))
glass = mat('PhiMu_Window_Glass_Dark', (0.045, 0.075, 0.09), 0.26)
frame = mat('PhiMu_Window_Frame_White', (0.91, 0.88, 0.79))
gold = mat('PhiMu_Sign_Letter_Gold', (0.66, 0.46, 0.19), 0.55, 0.12)
door_mat = mat('PhiMu_Entry_Door_Wood', (0.22, 0.085, 0.045))
floor_mat = mat('PhiMu_Schematic_Floor', (0.20, 0.17, 0.14))
upper_floor_mat = mat('PhiMu_Schematic_Upper_Floor', (0.38, 0.31, 0.23))
partition_mat = mat('PhiMu_Schematic_Partitions', (0.86, 0.81, 0.70))
furniture_mat = mat('PhiMu_Schematic_Furniture', (0.16, 0.09, 0.045))
fabric_mat = mat('PhiMu_Schematic_Fabric', (0.12, 0.22, 0.36))

created = []
def mesh_obj(name, verts, faces, material, col=asset_col):
    me = bpy.data.meshes.new(name + '_Mesh')
    me.from_pydata(verts, [], faces)
    me.materials.append(material)
    me.validate(verbose=False); me.update()
    ob = bpy.data.objects.new(name, me); col.objects.link(ob)
    created.append(ob)
    return ob

def cube(name, center, scale, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    ob = bpy.context.object; ob.name = name
    ob.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    asset_col.objects.link(ob)
    ob.data.materials.clear(); ob.data.materials.append(material)
    if bevel:
        mod = ob.modifiers.new('Soft_edges', 'BEVEL'); mod.width=bevel; mod.segments=2
        bpy.context.view_layer.objects.active=ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
    created.append(ob)
    return ob

def cylinder(name, center, radius, height, material, vertices=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=height, location=center)
    ob=bpy.context.object; ob.name=name
    for c in list(ob.users_collection): c.objects.unlink(ob)
    asset_col.objects.link(ob); ob.data.materials.append(material); created.append(ob)
    return ob

# One GIS-grounded footprint volume. Height is explicitly an architectural estimate;
# the layer's single-level and Extrution=12 attributes have no reliable documented unit.
wall_h = 6.2
roof_eave = wall_h + 0.22
ridge_h = 9.4
verts = [(x,y,z) for x,y in ring for z in (0.0, wall_h)]
n=len(ring)
faces=[tuple(range(0,n)), tuple(range(n,2*n))]
for i in range(n): faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
body=mesh_obj('House_301836574', verts, faces, brick)
body.data.materials.append(cream)
body.data.polygons[0].material_index=0
body.data.polygons[1].material_index=0

# Small painted cornice band wraps the wall perimeter as visible white trim.
for i, (a,b) in enumerate(zip(ring, ring[1:]+ring[:1])):
    dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    ob=cube('Cornice_%02d'%i, ((a[0]+b[0])/2,(a[1]+b[1])/2,wall_h-0.08),
            (length+0.12,0.24,0.20), cream, 0.025)
    ob.rotation_euler[2]=math.atan2(dy,dx)

# The 2010 source shows a light-painted front gable, paired classical columns,
# dark brick field and sash windows. Compass orientation of that photographed face
# is unknown, so the modeled presentation face is selected only for legibility.
front_y=ymax+0.22
front_x=(xmin+xmax)/2
overhang=0.55
rx0,rx1=xmin-overhang,xmax+overhang
ry0,ry1=ymin-0.35,ymax+0.35
ridge_x=(rx0+rx1)/2
roofverts=[(rx0,ry0,roof_eave),(rx1,ry0,roof_eave),(ridge_x,ry0,ridge_h),
           (rx0,ry1,roof_eave),(rx1,ry1,roof_eave),(ridge_x,ry1,ridge_h)]
roof=mesh_obj('Main_Gable_Roof',roofverts,[(0,2,5,3),(2,1,4,5),(0,1,2),(3,5,4),(0,3,4,1)],roofmat)
roof.data.materials.append(cream)
roof.data.polygons[2].material_index=1; roof.data.polygons[3].material_index=1

# White pediment face and layered horizontal cornice at the camera-facing end.
pediment_y=ymax+0.42
mesh_obj('Front_Pediment_Face',[(xmin+0.7,pediment_y,wall_h-0.05),(xmax-0.7,pediment_y,wall_h-0.05),(front_x,pediment_y,ridge_h-0.28)],[(0,1,2)],cream)
cube('Pediment_Base_Cornice',(front_x,pediment_y,wall_h+0.06),(width-1.0,0.48,0.30),cream,0.04)
cube('Portico_Upper_Entablature',(front_x,ymax+2.80,6.45),(width*0.76,0.62,0.42),cream,0.05)
cube('Portico_Front_Fascia',(front_x,ymax+3.12,6.67),(width*0.76,0.10,0.18),cream,0.02)

# Three wide, evenly spaced front windows plus centered entry; these repeat only the
# visible facade rhythm, not a surveyed opening schedule.
front_width=width-3.0
door_w=2.1
door_h=3.25
face_y=ymax+0.12
cube('Front_Entry_Door',(front_x,face_y,door_h/2+0.05),(door_w,0.22,door_h),door_mat,0.05)
for side in (-1,1):
    cube('Door_Sidelight',(front_x+side*(door_w/2+0.34),face_y-0.13,2.1),(0.34,0.05,2.0),glass,0.015)
window_centers=[front_x-10.1,front_x-4.2,front_x+4.2,front_x+10.1]
for j,wx in enumerate(window_centers):
    for floor,zlow in enumerate((1.25,4.35)):
        ww=2.25; wh=1.72; wz=zlow+wh/2
        cube('Window_Glass_%d_%d'%(j,floor),(wx,face_y-0.08,wz),(ww,0.09,wh),glass,0.025)
        for sx in (-1,1): cube('Window_Frame_V_%d_%d_%d'%(j,floor,sx),(wx+sx*(ww/2+0.08),face_y-0.15,wz),(0.14,0.16,wh+0.30),frame,0.02)
        for sz in (-1,1): cube('Window_Frame_H_%d_%d_%d'%(j,floor,sz),(wx,face_y-0.15,wz+sz*(wh/2+0.08)),(ww+0.30,0.16,0.14),frame,0.02)
        cube('Window_Mullion_V_%d_%d'%(j,floor),(wx,face_y-0.17,wz),(0.065,0.10,wh),frame)
        cube('Window_Mullion_H_%d_%d'%(j,floor),(wx,face_y-0.17,wz),(ww,0.10,0.065),frame)

# Portico columns are separated and evenly spaced; count/spacing is an illustrative
# reading of the 2010 photograph, not a verified architectural survey.
portico_span=width*0.62
for i in range(4):
    x=front_x-portico_span/2+i*portico_span/3
    cyl_y=ymax+2.78
    cylinder('Portico_Column_%d'%i,(x,cyl_y,3.15),0.28,6.20,cream,24)
    cylinder('Column_Base_%d'%i,(x,cyl_y,0.15),0.42,0.30,cream,24)
    cylinder('Column_Capital_%d'%i,(x,cyl_y,6.30),0.41,0.26,cream,24)

# Gold Greek-letter badge, built as joined curve-to-mesh strokes to avoid external fonts.
def stroke(name, points, radius=0.075):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=8; cu.bevel_depth=radius; cu.bevel_resolution=3
    sp=cu.splines.new('POLY'); sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points): p.co=(co[0],co[1],co[2],1)
    ob=bpy.data.objects.new(name,cu); asset_col.objects.link(ob); ob.data.materials.append(gold); created.append(ob)
    bpy.context.view_layer.objects.active=ob; ob.select_set(True); bpy.ops.object.convert(target='MESH'); ob=bpy.context.object; ob.select_set(False)
    return ob
letter_y=pediment_y+0.15; letter_z=wall_h+2.05; scale=0.74
# Phi: circular ring + vertical stem; Mu: two vertical stems linked by a shallow valley.
bpy.ops.mesh.primitive_torus_add(major_radius=0.43*scale, minor_radius=0.07*scale, major_segments=32, minor_segments=8,
    location=(front_x+0.42,letter_y,letter_z), rotation=(math.pi/2,0,0))
phi_ring=bpy.context.object; phi_ring.name='Phi_Ring'; phi_ring.data.materials.append(gold)
for c in list(phi_ring.users_collection): c.objects.unlink(phi_ring)
asset_col.objects.link(phi_ring); created.append(phi_ring)
stroke('Phi_Stem',[(front_x+0.42,letter_y-0.06,letter_z-0.62*scale),(front_x+0.42,letter_y-0.06,letter_z+0.62*scale)],0.07*scale)
stroke('Mu_Letter',[(front_x-0.08,letter_y,letter_z-0.55*scale),(front_x-0.08,letter_y,letter_z+0.55*scale),
                    (front_x-0.44,letter_y,letter_z+0.03*scale),(front_x-0.82,letter_y,letter_z+0.55*scale),
                    (front_x-0.82,letter_y,letter_z-0.55*scale)],0.09*scale)

# Add several understated side windows, aligned to the long elevation. Their positions
# remain illustrative because only the end facade is documented by a source photo.
for side in (-1,1):
    x=(xmin-0.12 if side<0 else xmax+0.12)
    for i in range(4):
        y=ymin+5+i*(depth-10)/3
        face_x=x+(-0.06 if side<0 else 0.06)
        tag='W' if side<0 else 'E'
        for floor,z in enumerate((2.1,5.2)):
            cube('Side_Window_Glass_%s_%d_%d'%(tag,i,floor),(face_x,y,z),(0.10,1.65,1.65),glass,0.02)
            trim_x=face_x+(-0.08 if side<0 else 0.08)
            for sy in (-1,1): cube('Side_Window_Frame_Y_%s_%d_%d_%d'%(tag,i,floor,sy),(trim_x,y+sy*0.87,z),(0.13,0.14,1.86),frame,0.02)
            for sz in (-1,1): cube('Side_Window_Frame_Z_%s_%d_%d_%d'%(tag,i,floor,sz),(trim_x,y,z+sz*0.87),(0.13,1.86,0.14),frame,0.02)
            cube('Side_Window_Mullion_%s_%d_%d'%(tag,i,floor),(trim_x,y,z),(0.13,0.07,1.65),frame)

# Schematic interior inserts. No plan or interior source was found; the organization,
# rooms, stairs, and furnishings below are deliberately generic and are not as-built.
def inset_floor(name, z, inset_scale, material):
    mx=sum(x for x,y in ring)/len(ring); my=sum(y for x,y in ring)/len(ring)
    pts=[Vector((mx+(x-mx)*inset_scale,my+(y-my)*inset_scale,0.0)) for x,y in ring]
    tris=geometry.tessellate_polygon([pts])
    faces=[tuple(int(i) for i in tri) for tri in tris]
    mesh_obj(name,[(p.x,p.y,z) for p in pts],faces,material)

inset_floor('Schematic_Ground_Floor_Plate',0.20,0.975,floor_mat)
# The interpretative upper level uses room-sized floor panels with gaps for the
# corridor and stair opening, keeping a roof-open cutaway readable from above.
for i,(center,size) in enumerate([
    ((-386.0,-80.5),(7.0,10.0)), ((-395.0,-81.0),(9.0,9.0)),
    ((-394.0,-98.0),(7.0,8.0)), ((-389.0,-108.0),(7.0,7.0))]):
    cube('Schematic_Upper_Floor_Panel_%02d'%i,(center[0],center[1],3.18),
         (size[0],size[1],0.12),upper_floor_mat,0.015)

# A restrained generic layout, kept in the wider interior body zone. These low
# partition walls read as diagrammatic room divisions rather than source-derived rooms.
for i,(a,b) in enumerate([
    ((-399.0,-104.0),(-384.4,-104.0)), ((-392.2,-113.0),(-392.2,-104.0)),
    ((-384.4,-104.0),(-384.4,-94.0)), ((-398.5,-94.0),(-384.4,-94.0)),
    ((-399.0,-104.0),(-399.0,-94.0)), ((-397.5,-84.1),(-378.0,-84.1)),
    ((-389.0,-91.0),(-389.0,-84.1)), ((-381.5,-84.1),(-381.5,-76.8)),
    ((-397.5,-76.8),(-381.5,-76.8)), ((-397.5,-84.1),(-397.5,-76.8))]):
    (ax,ay),(bx,by)=a,b
    length=math.hypot(bx-ax,by-ay)
    cube('Schematic_Partition_%02d'%i,((ax+bx)/2,(ay+by)/2,1.45 if i<5 else 4.40),
         (length,0.16,2.45),partition_mat,0.015)

# Generic living/dining furniture and sleeping-room blocks on the two plates.
for name,loc,size,material in [
    ('Dining_Table',(-390.5,-99.0,0.72),(3.3,1.5,0.20),furniture_mat),
    ('Kitchen_Counter',(-396.1,-99.0,0.73),(0.85,5.7,0.95),partition_mat),
    ('Lounge_Table',(-388.0,-109.5,0.72),(2.2,1.2,0.18),furniture_mat),
    ('Upper_Common_Table',(-390.0,-80.8,3.70),(2.4,1.3,0.18),furniture_mat),
    ('Upper_Storage',(-395.9,-80.2,3.95),(0.55,2.4,1.3),furniture_mat),
    ('Bed_Block_A',(-386.0,-109.0,3.58),(2.0,0.95,0.25),fabric_mat),
    ('Bed_Block_B',(-386.0,-105.8,3.58),(2.0,0.95,0.25),fabric_mat),
    ('Bed_Block_C',(-389.5,-79.1,3.58),(2.0,0.95,0.25),fabric_mat)]:
    cube('Schematic_'+name,loc,size,material,0.045)
for i,(x,y,z) in enumerate([
    (-393.4,-99.0,0.48),(-387.8,-99.0,0.48),(-390.5,-96.9,0.48),
    (-387.0,-109.5,0.48),(-389.0,-80.8,3.48),(-392.8,-80.8,3.48)]):
    cube('Schematic_Chair_%02d'%i,(x,y,z),(0.52,0.52,0.75),fabric_mat,0.035)

# A simple stair run is shown as repeated treads with a handrail line, without
# asserting an exact circulation plan or code-compliant stair dimensions.
for i in range(10):
    z=0.40+i*0.26
    y=-110.0+i*0.50
    cube('Schematic_Stair_Tread_%02d'%i,(-394.0,y,z),(2.6,0.56,0.14),partition_mat,0.015)
cube('Schematic_Stair_Rail',(-392.65,-107.75,1.85),(0.08,5.1,0.18),furniture_mat,0.02)

# Join only building geometry to retain the stable one-object collection interface.
bpy.ops.object.select_all(action='DESELECT')
for ob in list(asset_col.objects):
    if ob.type=='MESH': ob.select_set(True)
    elif ob.type=='CURVE':
        ob.select_set(True); bpy.context.view_layer.objects.active=ob; bpy.ops.object.convert(target='MESH')
        bpy.context.object.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in asset_col.objects if o.select_get())
bpy.ops.object.join()
house=bpy.context.object; house.name='House_301836574'; house.data.name='PhiMu_201Waldron_GIS_Footprint_Illustrative_Details'
house.select_set(False)

# Render-only setup is created outside the asset collection and removed after previews.
render_col=bpy.data.collections.new('Temporary_Render_Setup'); scene.collection.children.link(render_col)
def point_camera(cam,target): cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
def setup_camera(name,loc,target,lens=52):
    camdat=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,camdat); render_col.objects.link(cam)
    cam.location=loc; camdat.type='ORTHO'; camdat.ortho_scale=66; point_camera(cam,target); scene.camera=cam; return cam
def area_light(name,loc,power,size,target):
    d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size
    ob=bpy.data.objects.new(name,d); render_col.objects.link(ob); ob.location=loc; point_camera(ob,target)
def render(path,camname,loc,target,ortho=66):
    cam=setup_camera(camname,loc,target); cam.data.ortho_scale=ortho
    scene.render.filepath=str(path); bpy.ops.render.render(write_still=True)

scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.render.image_settings.color_mode='RGBA'
scene.render.resolution_percentage=80
scene.render.filepath=str(AUDIT/'exterior_preview.png')
scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='AgX'
world=scene.world or bpy.data.worlds.new('PhiMu_Studio_World'); scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.45,0.48,0.52,1)
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.66,0.69,0.73,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.28
target=(cx,cy,3.4)
area_light('Key', (cx-28,cy-38,38), 1150, 26, target)
area_light('Fill', (cx+35,cy-2,25), 600, 24, target)
area_light('Rim', (cx+10,cy+38,34), 700, 22, target)
render(AUDIT/'exterior_preview.png','Exterior_Camera',(cx-14,ymax+38,13),target,55)
render(AUDIT/'top_preview.png','Top_Camera',(cx,cy,72),(cx,cy,0),65)
render(AUDIT/'exterior_rear_oblique.png','Rear_Camera',(cx+37,ymin-30,23),target,70)

# Fresh evidence view: make a temporary duplicate, remove roof panels and the
# structural top cap, then render straight down through the roof opening. The saved
# deliverable remains a single joined mesh with a complete exterior roof.
cut=house.copy(); cut.data=house.data.copy(); cut.name='Temporary_Roof_Open_Cutaway'; render_col.objects.link(cut)
house.hide_render=True
bm=bmesh.new(); bm.from_mesh(cut.data)
interior_materials={floor_mat.name,upper_floor_mat.name,partition_mat.name,furniture_mat.name,fabric_mat.name}
interior_indices={i for i,m in enumerate(cut.data.materials) if m and m.name in interior_materials}
remove=[f for f in bm.faces if f.material_index not in interior_indices]
bmesh.ops.delete(bm,geom=remove,context='FACES')
bm.to_mesh(cut.data); bm.free(); cut.data.update()
render(AUDIT/'schematic_interior_cutaway.png','Schematic_Cutaway_Camera',
       (cx-18,ymax+35,30),(cx,cy,1.5),60)
house.hide_render=False
bpy.data.objects.remove(cut,do_unlink=True)

# Remove transient camera/light objects to keep the delivered library clean.
for obj in list(render_col.objects): bpy.data.objects.remove(obj,do_unlink=True)
bpy.data.collections.remove(render_col)
scene.camera=None
scene.render.filepath='//'
# Drop stale source-image datablocks and unused starter materials left by the
# previous library so the final asset has no hidden absolute-path dependencies.
for material in list(bpy.data.materials):
    if material.users == 0:
        bpy.data.materials.remove(material)
for image in list(bpy.data.images):
    if image.users == 0:
        bpy.data.images.remove(image)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))

print('SAVED',ASSET)
print('FOOTPRINT_BOUNDS',xmin,xmax,ymin,ymax,'HEIGHT',ridge_h,'VERTS',len(house.data.vertices),'FACES',len(house.data.polygons))
