import bpy, math, os, json
from mathutils import Vector

ASSET_ID = 'massing_granite_student_living_3732ce0'
ASSET_PATH = os.path.join(os.path.dirname(__file__), 'massing_granite_student_living_3732ce0.blend')
OUT_PATH = os.path.join(os.path.dirname(__file__), 'massing_granite_student_living_3732ce0.blend')
EVIDENCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'audit', ASSET_ID))
PREVIEW_PATH = os.path.join(EVIDENCE_DIR, 'preview_exterior.png')
COLLECTION_NAME = 'Asset_' + ASSET_ID

# Dimensions from the architect's 2014 A105 final detailed floor plans, in meters.
# The 1st-floor shell is 151'-6 1/2" x 60'-8"; upper floors are about
# 151'-4 1/2" x 57'-11". Keep the stable campus center/orientation from the
# existing asset; A100's 8,936 sf footprint is slightly smaller than the rectangular
# shell area because the plan has small recesses and chamfers.
CX, CY = 464.1726837158203, -213.28562927246094
GROUND_HX = (60 + 8/12) * 0.3048 / 2
UPPER_HX = (57 + 11/12) * 0.3048 / 2
HY = (151 + 6.5/12) * 0.3048 / 2
HX = GROUND_HX
X0, X1 = CX-HX, CX+HX
Y0, Y1 = CY-HY, CY+HY
Z0, Z1 = 0.0, 19.5072
# Make builds repeatable while retaining the stable manifest collection and scene.
coll = bpy.data.collections.get(COLLECTION_NAME)
if coll is None:
    coll = bpy.data.collections.new(COLLECTION_NAME)
    bpy.context.scene.collection.children.link(coll)
for obj in list(coll.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Helpers
def mat(name, color, rough=0.68, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metallic
    return m

brick = mat('Granite | warm red brick', (0.19, 0.035, 0.025), .86)
brick_alt = mat('Granite | secondary brick', (0.28, 0.06, 0.035), .86)
limestone = mat('Granite | pale limestone', (0.48, 0.42, 0.33), .78)
glass = mat('Granite | blue gray glazing', (0.025, 0.075, 0.095), .22, .18)
frame = mat('Granite | charcoal metal', (0.075, 0.085, 0.09), .45, .5)
roofmat = mat('Granite | dark roof membrane', (0.12, 0.14, 0.14), .9)
cladding = mat('Granite | warm gray siding', (0.42, 0.38, 0.32), .82)
awning = mat('Granite | oxblood red awning', (0.5, 0.025, 0.02), .72)
concrete = mat('Granite | sidewalk concrete', (.47, .46, .42), .92)


def box(name, center, dims, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o=bpy.context.object
    o.name=name
    o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material: o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Softened fabricated edges','BEVEL'); mod.width=bevel; mod.segments=2
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    for c in list(o.users_collection): c.objects.unlink(o)
    coll.objects.link(o)
    return o

# A200/A201 finish elevations are 0', 14'-8", 25'-6 5/8", 36'-4 1/2",
# 47'-2 3/8"; truss bearing is 56'-2 3/4". A100 gives 64'-0" overall height.
body_bottom, ground_top, top = 0.0, 4.4704, 17.1391
box('Granite | brick apartment volume',(CX,CY,(ground_top+top)/2),(2*UPPER_HX,2*HY,top-ground_top),brick,.06)
box('Granite | ground level limestone plinth',(CX,CY,(body_bottom+ground_top)/2),(2*HX,2*HY,ground_top-body_bottom),limestone,.04)
box('Granite | limestone belt course',(CX,CY,ground_top-.12),(2*HX+.12,2*HY+.12,.24),limestone,.025)
for z in (7.7883,11.0871,14.3859):
    box(f'Granite | cast stone floor band {z:.3f}',(CX,CY,z),(2*UPPER_HX+.08,2*HY+.08,.16),limestone,.018)

# Ground-floor glazing on the north and south end faces, plus the long west/east retail elevations.
# Recessed glazing reads as active frontage and open garage/retail bays without claiming a precise tenant layout.
for side in (-1,1):
    x=CX+side*(HX-.035)
    n=12 if side==1 else 8
    for i in range(n):
        y=CY-HY+2.5+i*((2*HY-5.0)/(n-1))
        w=2.1 if side==1 else 1.4
        h=2.75 if side==1 else 1.55
        gz=2.45 if side==1 else 2.1
        box(f'Granite | ground storefront or garage glazing {side} {i+1}',(x,y,gz),(.10,w,h),glass,.025)
        box(f'Granite | ground glazing mullion {side} {i+1}',(x+side*.065,y,gz),(.06,.07,h),frame,.008)
    for i in range(n+1):
        y=CY-HY+1.25+i*((2*HY-2.5)/n)
        box(f'Granite | limestone ground-floor pier {side} {i}',(x+side*.025,y,2.25),(.24,.38,4.0),limestone,.02)
    if side==1:
        for i in (2,6,10):
            y=CY-HY+2.5+i*((2*HY-5.0)/(n-1))
            box(f'Granite | red shop awning {side} {i}',(x+side*.65,y,4.12),(1.2,2.5,.14),awning,.04)
# Main residential/office entry with limestone surround at north end, on corner frontage
for i,y in enumerate((CY+HY-.15, CY-HY+.15)):
    box(f'Granite | end facade entry glazing {i}',(CX,y,2.45),(7.0,.12,2.7),glass,.02)

# Four residential levels, repetitive but varied fenestration on long facades.
levels=[6.13,9.44,12.74,15.76]
for side in (-1,1):
    x=CX+side*(UPPER_HX-.05)
    count=16
    if side==-1:
        for i in (2,5,8,11,14):
            y=CY-HY+2.25+i*((2*HY-4.5)/(count-1))
            box(f'Granite | gray siding bay {i}',(x+side*.10,y,10.8),(.075,2.15,12.55),cladding,.012)
    for floor,z in enumerate(levels, start=2):
        for i in range(count):
            y=CY-HY+2.25+i*((2*HY-4.5)/(count-1))
            width=1.15 if i%4 else 1.40
            # paired dark frames and blue-gray glazing
            box(f'Granite | apartment window glass {side} F{floor} B{i+1}',(x,y,z),(.12,width,1.55),glass,.018)
            box(f'Granite | apartment window jamb {side} F{floor} B{i+1}',(x+side*.08,y-width/2,(z)),(.08,.075,1.7),limestone,.01)
            box(f'Granite | apartment window jamb {side} F{floor} B{i+1}',(x+side*.08,y+width/2,(z)),(.08,.075,1.7),limestone,.01)
            box(f'Granite | apartment window lintel {side} F{floor} B{i+1}',(x+side*.08,y,z+.82),(.08,width+.15,.10),limestone,.008)
            # Projecting balcony deck and black rail, alternating windows to reflect photographed bay rhythm.
            if i%3==1:
                bx=x+side*.70
                box(f'Granite | balcony slab {side} F{floor} B{i+1}',(bx,y,z-.72),(1.32,2.35,.16),concrete,.035)
                # front rail and side returns
                railz=z-.10
                box(f'Granite | balcony rail top {side} F{floor} B{i+1}',(bx+side*.65,y,railz),( .07,2.35,.07),frame,.015)
                for j in range(6):
                    yy=y-1.08+j*.432
                    box(f'Granite | balcony baluster {side} F{floor} B{i+1} {j}',(bx+side*.65,yy,railz-.52),(.045,.045,1.0),frame,.008)
                for ey in (-1,1):
                    box(f'Granite | balcony side rail {side} F{floor} B{i+1} {ey}',(bx+side*.16,y+ey*1.12,railz-.46),(.82,.06,.92),frame,.02)
        # continuous subtle brick sill course
        box(f'Granite | floor belt {side} F{floor}',(x+side*.055,CY,z-1.43),(.10,2*HY-.28,.09),brick_alt,.008)

# End façades with central windows; visible from oblique corners.
for side in (-1,1):
    y=CY+side*(HY+.02)
    gable_mesh=bpy.data.meshes.new(f'Granite | end gable {side} mesh')
    gable_mesh.from_pydata([(CX-UPPER_HX,y,top),(CX+UPPER_HX,y,top),(CX,y,19.5072)],[],[(0,1,2)])
    gable_mesh.materials.append(brick)
    gable=bpy.data.objects.new(f'Granite | end gable {side}',gable_mesh); coll.objects.link(gable)
    y=CY+side*(HY-.05)
    for floor,z in enumerate(levels,start=2):
        for i,xoff in enumerate((-6.4,-3.2,0.0,3.2,6.4)):
            x=CX+xoff
            box(f'Granite | end apartment window {side} F{floor} B{i+1}',(x,y,z),(1.55,.12,1.55),glass,.018)
            box(f'Granite | end window lintel {side} F{floor} B{i+1}',(x,y+side*.08,z+.82),(1.72,.08,.1),limestone,.008)

# Main roof and raised gable dormers, based on A200/A201 elevations.
roof_mesh=bpy.data.meshes.new('Granite | hipped roof mesh')
ridge_start=HY-3.0; eave_z=top; ridge_z=17.85
roof_mesh.from_pydata(
 [(CX-HX,CY-HY,eave_z),(CX+HX,CY-HY,eave_z),
  (CX+HX,CY+HY,eave_z),(CX-HX,CY+HY,eave_z),
  (CX,CY-ridge_start,ridge_z),(CX,CY+ridge_start,ridge_z)],
 [],[(0,3,5,4),(1,2,5,4),(0,1,4),(2,3,5)])
roof_mesh.materials.append(roofmat)
roof=bpy.data.objects.new('Granite | hipped roof',roof_mesh); coll.objects.link(roof)

# Three raised gable-front sections per long side echo the dormers in A200.
peak_z=19.5072
for side in (-1,1):
    x_front=CX+side*(UPPER_HX+0.10)
    x_back=CX+side*(UPPER_HX-3.6)
    for idx,offset in enumerate((-13.0,0.0,13.0),start=1):
        yc=CY+offset; half=4.0
        verts=[(x_front,yc-half,eave_z),(x_front,yc+half,eave_z),(x_front,yc,peak_z),
               (x_back,yc-half,eave_z),(x_back,yc+half,eave_z),(x_back,yc,peak_z)]
        mesh=bpy.data.meshes.new(f'Granite | raised gable {side} {idx} mesh')
        mesh.from_pydata(verts,[],[(0,1,2),(3,5,4),(0,3,4,1),(0,2,5,3),(1,4,5,2)])
        mesh.materials.append(brick); mesh.materials.append(roofmat)
        for poly in mesh.polygons:
            poly.material_index=0 if poly.index<2 else 1
        gable=bpy.data.objects.new(f'Granite | raised gable {side} {idx}',mesh); coll.objects.link(gable)
box('Granite | roof ridge cap',(CX,CY,ridge_z),(.22,2*ridge_start,.10),frame,.025)

# Set asset metadata and camera render settings for a review preview.
scene=bpy.context.scene
scene['building_id']=ASSET_ID
scene['source_geometry']='2014 KJG/TBIRD final detailed plans for 225 Northwestern; current imagery confirms the retained campus orientation and envelope.'
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1200; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.22,0.27,0.32,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.45
# review camera looking from street-side southwest, retaining entire silhouette
cam_data=bpy.data.cameras.new('Granite review camera')
cam=bpy.data.objects.new('Granite review camera',cam_data); scene.collection.objects.link(cam)
cam.location=(CX-63,CY-54,37.5)
target=Vector((CX,CY,8.3)); direction=target-Vector(cam.location)
cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); cam.data.lens=52
scene.camera=cam
# Neutral ground plane is preview-only and is not part of the exported asset collection.
ground=box('Granite | preview ground',(CX,CY,-.05),(160,150,.10),concrete,0)
for c in list(ground.users_collection): c.objects.unlink(ground)
scene.collection.objects.link(ground)
# lighting
for o in list(scene.objects):
    if o.type=='LIGHT': bpy.data.objects.remove(o,do_unlink=True)
light_data=bpy.data.lights.new('Granite large softbox','AREA'); light_data.energy=1800; light_data.shape='DISK'; light_data.size=36
light=bpy.data.objects.new('Granite large softbox',light_data); scene.collection.objects.link(light); light.location=(CX-28,CY-8,48)
light.rotation_euler=(Vector((CX,CY,7))-Vector(light.location)).to_track_quat('-Z','Y').to_euler()
scene.view_settings.view_transform='Standard'; scene.view_settings.look='Medium High Contrast'; scene.view_settings.exposure=0; scene.view_settings.gamma=1
scene.render.filepath=PREVIEW_PATH
os.makedirs(EVIDENCE_DIR,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT_PATH)
bpy.ops.render.render(write_still=True)
print('GRANITE_BUILD_COMPLETE',OUT_PATH,PREVIEW_PATH)

