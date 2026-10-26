"""R4 local geometry/interior refinement from the registered roof proxy and Purdue program evidence."""
import bpy, json, math
from pathlib import Path
from mathutils import Matrix, Vector

ASSET=bpy.data.collections.get('Asset_tarkington_hall')
ROOT=bpy.data.objects.get('AssetRoot_tarkington_hall')
if not ASSET or not ROOT: raise RuntimeError('Tarkington asset collection/root missing')

# R3 shell limits in project-local coordinates. Interpolated GIS slices capture
# the visible wing-end steps without treating the GIS outline as a surveyed wall.
SOURCE={
 'NW':(-45.79887771606445,-33.598876953125),
 'SW':(-46.79887771606445,-34.598876953125),
 'NE':(28.001123046875,40.201123046875),
 'SE':(28.701123046875,40.901123046875),
}
PROFILES={
 'NW':[(17,-45.8,-33.6),(44,-45.8,-33.6),(48,-46.7,-33.6),(52,-46.7,-34.5),(56,-47.6,-34.5),(60,-46.6,-34.5),(64.5,-46.6,-34.5)],
 'NE':[(17,28.0,40.2),(44,28.0,40.2),(48,28.0,41.2),(52,28.9,41.1),(56,28.9,42.0),(60,28.9,41.1),(64.5,28.9,41.1)],
 'SW':[(-54.5,-48.55,-33.7),(-51,-48.55,-33.7),(-49,-47.8,-33.7),(-45,-47.8,-33.7),(-43,-47.7,-33.7),(-41,-46.8,-34.6),(-35,-47.7,-34.6),(-31,-47.7,-34.6),(-27,-46.8,-33.7),(-23,-46.8,-33.7),(-21,-45.9,-33.7),(-7,-45.9,-33.7)],
 'SE':[(-43.4,28.7,40.9),(-41,28.7,40.9),(-37,28.7,40.9),(-35,28.7,41.8),(-33,28.7,41.8),(-31,28.7,40.9),(-29,28.7,40.9),(-27,27.8,40.9),(-25,27.8,40.9),(-23,27.8,40.0),(-20,27.8,40.0),(-12,27.9,40.1),(-7,27.9,40.1)],
}

def target_bounds(code,y):
    rows=PROFILES[code]
    if y<=rows[0][0]: return rows[0][1:]
    if y>=rows[-1][0]: return rows[-1][1:]
    for a,b in zip(rows,rows[1:]):
        if a[0]<=y<=b[0]:
            t=(y-a[0])/(b[0]-a[0]); return (a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t)
    raise AssertionError

def remap_x(code,x,y):
    src0,src1=SOURCE[code]; dst0,dst1=target_bounds(code,y)
    t=(x-src0)/(src1-src0)
    return dst0+t*(dst1-dst0)

def move_world(obj, x=None, y=None, z=None):
    mw=obj.matrix_world.copy()
    if x is not None: mw.translation.x=x
    if y is not None: mw.translation.y=y
    if z is not None: mw.translation.z=z
    obj.matrix_world=mw

def transform_mesh(obj, fn):
    inv=obj.matrix_world.inverted()
    for v in obj.data.vertices:
        p=obj.matrix_world@v.co
        q=fn(p)
        v.co=inv@q
    obj.data.update()

# Refine wing structural faces to follow the source's local stepped edges.
shell_deformed=0
for obj in list(ASSET.objects):
    if obj.type!='MESH': continue
    code=next((c for c in PROFILES if obj.name.startswith(f'Tark_{c}_Wing_')),None)
    if code:
        transform_mesh(obj,lambda p,c=code:Vector((remap_x(c,p.x,p.y),p.y,p.z)))
        shell_deformed+=1

# Move only the facade opening centers and adjust their horizontal span to the
# local wing boundary at the same end/side; keep vertical dimensions unchanged.
side_features_moved=0; end_features_resized=0; removed_se_openings=[]
for obj in list(ASSET.objects):
    if obj.type!='MESH' or not (obj.name.startswith('Tark_Win_') or obj.name.startswith('Tark_Sill_')): continue
    code=next((c for c in PROFILES if f'_{c}_' in obj.name),None)
    if not code: continue
    loc=obj.matrix_world.translation.copy()
    if code=='SE' and loc.y < -43.4:
        removed_se_openings.append(obj.name)
        for col in list(obj.users_collection): col.objects.unlink(obj)
        bpy.data.objects.remove(obj,do_unlink=True)
        continue
    src0,src1=SOURCE[code]; dst0,dst1=target_bounds(code,loc.y)
    if '_North_' in obj.name or '_South_' in obj.name:
        # End facade windows sit at a boundary; their apertures track the width
        # change so the original bay rhythm remains separate and plausible.
        oldx=loc.x; newx=remap_x(code,oldx,loc.y); ratio=(dst1-dst0)/(src1-src0)
        transform_mesh(obj,lambda p,cx=oldx,nx=newx,r=ratio:Vector((nx+(p.x-cx)*r,p.y,p.z)))
        move_world(obj,x=newx)
        end_features_resized+=1
    else:
        newx=remap_x(code,loc.x,loc.y)
        move_world(obj,x=newx)
        side_features_moved+=1

# Keep the four roof penthouses and HVAC units centered on their updated wings.
for obj in ASSET.objects:
    if not (obj.name.startswith('Tark_Roof_Penthouse_') or obj.name.startswith('Tark_Roof_HVAC_Louver_')): continue
    idx=obj.name.rsplit('_',1)[-1]; code={'0':'NW','1':'NE','2':'SW','3':'SE'}.get(idx)
    if code:
        x=obj.matrix_world.translation.x; y=obj.matrix_world.translation.y
        move_world(obj,x=remap_x(code,x,y))

# The north bridge visibly stops before the wings split. The R3 14 m depth was
# too long; compress every component together to the orthophoto/GIS transition.
NORTH_OLD=(19.0,33.0); NORTH_NEW=(19.0,28.0)
for obj in list(ASSET.objects):
    if obj.type=='MESH' and obj.name.startswith(('Tark_West_Connector_','Tark_East_Connector_')):
        a,b=NORTH_OLD; c,d=NORTH_NEW
        transform_mesh(obj,lambda p,a=a,b=b,c=c,d=d:Vector((p.x,c+(p.y-a)*(d-c)/(b-a),p.z)))

# Registered footprint profiles show a broader middle crossbar than the R3 core.
# Fill the two missing east/west connector masses around the modeled services.
M_BRICK=bpy.data.materials.get('Beering_Purdue_Red_Brick')
M_LIME=bpy.data.materials.get('Indiana_Bedford_Limestone')
M_ROOF=bpy.data.materials.get('Beering_Roof_Membrane')
M_GLASS=bpy.data.materials.get('Beering_Solar_Ribbon_Glass')
M_OAK=bpy.data.materials.get('Beering_Honey_Oak_Woodwork')
M_DARK=bpy.data.materials.get('Beering_Executive_Dark_Oak')
M_NAVY=bpy.data.materials.get('Tarkington_Navy_Carpet')
M_STEEL=bpy.data.materials.get('Tark_Stainless_Steel')
M_COUNTER=bpy.data.materials.get('Tark_Black_Countertop')

def make_material(name,color,rough=.7,metal=.0):
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color=(*color,1); mat.use_nodes=True
    bsdf=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if bsdf:
        bsdf.inputs['Base Color'].default_value=(*color,1)
        bsdf.inputs['Roughness'].default_value=rough
        bsdf.inputs['Metallic'].default_value=metal
    return mat

M_CURTAIN=make_material('Tark_Room_Curtain_Fabric',(0.10,0.17,0.24),.92)
M_WARM=make_material('Tark_Interior_Warm_Paint',(0.77,0.72,0.62),.85)
M_PLANTER=make_material('Tark_Interior_Planter_Ceramic',(0.23,0.28,0.29),.65)
M_LEAF=make_material('Tark_Interior_Plant_Leaf',(0.10,0.26,0.16),.9)
M_MONITOR=make_material('Tark_Interior_Monitor',(0.018,0.024,0.032),.25)
M_LAMP=make_material('Tark_Interior_Lamp',(0.82,0.68,0.42),.35)

def add_box(name,bounds,material,bevel=0):
    x0,x1,y0,y1,z0,z1=bounds
    verts=[(0,0,0),(x1-x0,0,0),(x1-x0,y1-y0,0),(0,y1-y0,0),(0,0,z1-z0),(x1-x0,0,z1-z0),(x1-x0,y1-y0,z1-z0),(0,y1-y0,z1-z0)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh=bpy.data.meshes.new(name+'_Mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); ASSET.objects.link(obj); obj.parent=ROOT
    if material: obj.data.materials.append(material)
    obj.matrix_world=Matrix.Translation(Vector((x0,y0,z0)))
    if bevel:
        mod=obj.modifiers.new('Soft furniture edges','BEVEL'); mod.width=bevel; mod.segments=2
    return obj

def add_connector(prefix,x0,x1,y0,y1,window_cols):
    add_box(prefix+'_Limestone_Base',(x0,x1,y0,y1,0.0,1.5),M_LIME)
    add_box(prefix+'_Brick_Shaft',(x0,x1,y0,y1,1.5,15.2),M_BRICK)
    for level,z in enumerate((3.8,7.6,11.4,15.2),1):
        add_box(f'{prefix}_Limestone_Belt_{level}',(x0,x1,y0,y1,z-.11,z+.11),M_LIME)
    add_box(prefix+'_Roof_Membrane',(x0+.35,x1-.35,y0+.35,y1-.35,15.2,15.38),M_ROOF)
    add_box(prefix+'_Roof_Parapet',(x0-.05,x1+.05,y0-.05,y1+.05,15.5,15.9),M_LIME)
    xs=[x0+(x1-x0)*(i+.5)/window_cols for i in range(window_cols)]
    for side,y in [('N',y1+.08),('S',y0-.08)]:
        for col,x in enumerate(xs):
            for row,z in enumerate((2.4,6.2,10.0,13.8)):
                add_box(f'{prefix}_Win_{side}_{col}_{row}',(x-.82,x+.82,y-.09,y+.09,z-.73,z+.73),M_GLASS)
                add_box(f'{prefix}_Sill_{side}_{col}_{row}',(x-.96,x+.96,y-.16,y+.16,z-1.48,z-1.32),M_LIME)

# East/west crossbars occupy the open intervals seen in the official polygon and
# aerial. Their room programming below sits inside these four-floor masses.
add_connector('Tark_West_Core_Connector',-45.8,-21.4,-6.0,19.0,6)
add_connector('Tark_East_Core_Connector',14.6,40.1,-6.0,19.0,6)

# Correct the north pavilion core width only where the source outline carries it.
for obj in list(ASSET.objects):
    if obj.type!='MESH' or not obj.name.startswith('Tark_North_Entrance_Pavilion_'): continue
    if not any(token in obj.name for token in ('Brick_Shaft','Limestone_Base','Limestone_Belt_','Roof_Membrane','Roof_Parapet_Coping')): continue
    transform_mesh(obj,lambda p:Vector((-21.4+(p.x+15.38751220703125)*(37.2/24.0),p.y,p.z)))

# The GIS slices and aerial show only a small southern central projection. Shrink
# its shell footprint; shift the documented front doors, canopy and stairs to it.
for obj in list(ASSET.objects):
    if obj.type!='MESH' or not obj.name.startswith('Tark_South_Entrance_Pavilion_'): continue
    transform_mesh(obj,lambda p:Vector((-7.2+(p.x+15.38751220703125)*(14.3/24.0),-15.0+(p.y+23.0)*(2.0/14.0),p.z)))

# The source footprint steps outward at the lobby/core and narrows again at the
# south entry. Model that as two connected structural masses, rather than the
# old oversized uniform rectangle.
add_box('Tark_South_Lobby_Core_Limestone_Base',(-21.4,15.7,-13.0,-9.0,0.0,1.5),M_LIME)
add_box('Tark_South_Lobby_Core_Brick_Shaft',(-21.4,15.7,-13.0,-9.0,1.5,15.2),M_BRICK)
for level,z in enumerate((3.8,7.6,11.4,15.2),1):
    add_box(f'Tark_South_Lobby_Core_Limestone_Belt_{level}',(-21.4,15.7,-13.0,-9.0,z-.11,z+.11),M_LIME)
add_box('Tark_South_Lobby_Core_Roof_Membrane',(-21.0,15.3,-12.7,-9.3,15.2,15.38),M_ROOF)
add_box('Tark_South_Lobby_Core_Roof_Parapet',(-21.45,15.75,-13.05,-8.95,15.5,15.9),M_LIME)
for obj in ASSET.objects:
    if obj.type!='MESH': continue
    if obj.name.startswith(('Tark_South_Door_Bronze_Frame_','Tark_South_Glass_Door_')):
        move_world(obj,x=obj.matrix_world.translation.x+3.34,y=-15.15)
    elif obj.name.startswith('Tark_South_Portico_'):
        move_world(obj,x=obj.matrix_world.translation.x+3.34,y=-17.6)
    elif obj.name=='Tark_South_Entrance_Plinth_Stairs':
        move_world(obj,x=obj.matrix_world.translation.x+3.34,y=-17.45)

# Compress the lobby floor and seating into the revised south-entry zone while
# keeping its actual reception, mail, and lounge furnishings.
floor=bpy.data.objects.get('Tark_Lobby_Terrazzo_Floor')
if floor:
    transform_mesh(floor,lambda p:Vector((p.x,-15.5+(p.y+20.5)*(10.0/15.0),p.z)))
for name,y in [('Tark_Lobby_Lounge_Sofa_0',-11.0),('Tark_Lobby_Lounge_Sofa_1',-12.5),('Tark_Lobby_Digital_Directory',-13.0)]:
    obj=bpy.data.objects.get(name)
    if obj: move_world(obj,y=y)

# Existing R3 room 118 had two beds/desks but omitted several amenities in
# Purdue's approximate room illustration. Add desk lamps, closet pulls,
# book/desktop storage, trash cans, and curtains without changing the room shell.
room_additions=[]
def add_dorm_accessories(prefix,dy=0.0):
    for idx,y0 in enumerate((-32.2,-29.8)):
        y=y0+dy
        # Small brass task light and a restrained desktop organizer/bookshelf.
        room_additions.append(add_box(f'{prefix}_DeskLampBase_{idx}',(-35.90,-35.70,y-.09,y+.09,1.035,1.085),M_LAMP))
        room_additions.append(add_box(f'{prefix}_DeskLampStem_{idx}',(-35.84,-35.76,y-.035,y+.035,1.08,1.30),M_LAMP))
        room_additions.append(add_box(f'{prefix}_DeskLampShade_{idx}',(-35.97,-35.63,y-.12,y+.12,1.27,1.38),M_LAMP,.02))
        room_additions.append(add_box(f'{prefix}_Bookshelf_{idx}',(-35.50,-35.24,y-.36,y+.36,1.04,1.75),M_OAK,.025))
        room_additions.append(add_box(f'{prefix}_Bookshelf_Shelf_{idx}_A',(-35.49,-35.22,y-.36,y+.36,1.28,1.34),M_LIME))
        room_additions.append(add_box(f'{prefix}_Bookshelf_Shelf_{idx}_B',(-35.49,-35.22,y-.36,y+.36,1.52,1.58),M_LIME))
        # A short chest at the bed foot (+X) with clearance from the mattress and desk.
        cx=-37.20; cy=y0+dy
        room_additions.append(add_box(f'{prefix}_Dresser_{idx}',(cx-.43,cx+.43,cy-.33,cy+.33,.16,.86),M_OAK,.035))
        for drawer,z in enumerate((.34,.52,.70)):
            room_additions.append(add_box(f'{prefix}_Dresser_Drawer_{idx}_{drawer}',(cx-.36,cx+.36,cy-.345,cy-.32,z-.065,z+.065),M_OAK,.012))
            room_additions.append(add_box(f'{prefix}_Dresser_Pull_{idx}_{drawer}',(cx-.04,cx+.04,cy-.365,cy-.345,z-.018,z+.018),M_DARK))
        # Canvas panels flank the window fan so the opening stays visible.
        for side,cy0 in [('a',-31.62),('b',-30.58)]:
            yy=cy0+dy
            room_additions.append(add_box(f'{prefix}_Curtain_{idx}_{side}',(-40.26,-40.18,yy-.14,yy+.14,1.0,2.65),M_CURTAIN))
    # One waste basket beside the entry/desk zone.
    x=-35.0; y=-31.0+dy
    room_additions.append(add_box(f'{prefix}_Wastebasket',(x-.15,x+.15,y-.15,y+.15,.08,.48),M_PLANTER,.025))

add_dorm_accessories('Tark_Dorm_Room118_Accessory')

# Duplicate the documented typical room module once along the existing wing as
# a representative two-room/corridor bay. Dimensions and furnishings are not
# scaled; this is a viewable sample floor segment, not a 50-room count claim.
room_base=[o for o in list(ASSET.objects) if o.type=='MESH' and o.name.startswith('Tark_Dorm_') and not o.name.startswith('Tark_Dorm_Room118_Accessory_')]
for obj in room_base:
    dup=obj.copy(); dup.data=obj.data.copy(); dup.name='Tark_Representative_Room119_'+obj.name.removeprefix('Tark_Dorm_')
    ASSET.objects.link(dup); dup.parent=ROOT
    mw=obj.matrix_world.copy(); mw.translation.y-=6.0; dup.matrix_world=mw
add_dorm_accessories('Tark_Representative_Room119_Accessory',-6.0)
add_box('Tark_Representative_Floor_Corridor_Carpet',(-34.42,-32.75,-42.0,-26.0,.08,.16),M_NAVY)
add_box('Tark_Representative_Corridor_East_Wall',(-32.78,-32.58,-42.0,-26.0,0,3.8),M_WARM)
for i,y in enumerate((-38.3,-31.7)):
    add_box(f'Tark_Representative_Corridor_Door_{i}',(-34.36,-34.18,y-.48,y+.48,.1,2.25),M_OAK,.025)
    add_box(f'Tark_Representative_Corridor_Door_Handle_{i}',(-34.15,-34.10,y+.28,y+.36,1.05,1.18),M_LAMP)

# A separately dimensioned sample room follows Purdue's published approximate
# 11 ft 7 in x 16 ft 2 in double-room dimensions. Its placement within the wing
# and furnishing coordinates remain schematic because no room-plan coordinates
# or measured as-built room survey were published.
SW_X0,SW_X1=-42.765,-39.235
SW_Y0,SW_Y1=-44.465,-39.535
add_box('Tark_Program_Standard_Double_Room_Floor',(SW_X0,SW_X1,SW_Y0,SW_Y1,.02,.14),M_NAVY)
# Perimeter wall segments retain an open, evidence-friendly south doorway and north window.
add_box('Tark_Program_Standard_Room_Wall_West',(SW_X0,SW_X0+.14,SW_Y0,SW_Y1,.1,2.9),M_WARM)
add_box('Tark_Program_Standard_Room_Wall_East',(SW_X1-.14,SW_X1,SW_Y0,SW_Y1,.1,2.9),M_WARM)
# south entry opening near the east side
add_box('Tark_Program_Standard_Room_Wall_South_A',(SW_X0,SW_X1-.98,SW_Y0,SW_Y0+.14,.1,2.9),M_WARM)
add_box('Tark_Program_Standard_Room_Wall_South_B',(SW_X1-.14,SW_X1,SW_Y0,SW_Y0+.14,.1,2.9),M_WARM)
add_box('Tark_Program_Standard_Room_Door',(SW_X1-.93,SW_X1-.19,SW_Y0+.04,SW_Y0+.11,.1,2.15),M_OAK,.015)
# North wall window with sill/header, glass, and paired curtains.
wx0,wx1=-41.80,-40.20
add_box('Tark_Program_Standard_Room_Wall_North_L',(SW_X0,wx0,SW_Y1-.14,SW_Y1,.1,2.9),M_WARM)
add_box('Tark_Program_Standard_Room_Wall_North_R',(wx1,SW_X1,SW_Y1-.14,SW_Y1,.1,2.9),M_WARM)
add_box('Tark_Program_Standard_Room_Window_Sill',(wx0,wx1,SW_Y1-.16,SW_Y1+.02,.75,.9),M_LIME)
add_box('Tark_Program_Standard_Room_Window_Header',(wx0,wx1,SW_Y1-.16,SW_Y1+.02,2.35,2.50),M_LIME)
add_box('Tark_Program_Standard_Room_Window_Glass',(wx0,wx1,SW_Y1-.08,SW_Y1+.02,.90,2.35),M_GLASS)
for j,x in enumerate((wx0+.04,wx1-.12)):
    add_box(f'Tark_Program_Standard_Room_Curtain_{j}',(x,x+.08,SW_Y1-.27,SW_Y1-.12,.9,2.35),M_CURTAIN,.02)
# Two single beds, paired desks, and chairs sized to fit the published plan.
for i,cx in enumerate((-41.98,-40.02)):
    add_box(f'Tark_Program_Standard_Room_BedFrame_{i}',(cx-.48,cx+.48,-43.45,-41.45,.28,.58),M_OAK,.04)
    add_box(f'Tark_Program_Standard_Room_Mattress_{i}',(cx-.45,cx+.45,-43.40,-41.50,.58,.83),M_WARM,.07)
    add_box(f'Tark_Program_Standard_Room_Bedding_{i}',(cx-.44,cx+.44,-42.85,-41.50,.84,.87),M_NAVY,.03)
    add_box(f'Tark_Program_Standard_Room_Pillow_{i}',(cx-.30,cx+.30,-43.34,-42.96,.84,.96),M_LIME,.035)
    add_box(f'Tark_Program_Standard_Room_Desk_{i}',(cx-.50,cx+.50,-40.43,-39.83,.72,.80),M_OAK,.025)
    add_box(f'Tark_Program_Standard_Room_Desk_ChairSeat_{i}',(cx-.25,cx+.25,-41.10,-40.62,.43,.55),M_DARK,.04)
    add_box(f'Tark_Program_Standard_Room_Desk_ChairBack_{i}',(cx-.25,cx+.25,-40.70,-40.60,.55,1.12),M_NAVY,.04)
    add_box(f'Tark_Program_Standard_Room_DeskLamp_{i}',(cx-.10,cx+.10,-40.30,-40.10,.81,1.12),M_LAMP,.025)
# Compact closets and dressers sit in the south end corners clear of door swing.
add_box('Tark_Program_Standard_Room_Closet',(SW_X0+.16,SW_X0+.76,SW_Y0+.20,SW_Y0+1.25,.15,2.25),M_OAK,.025)
add_box('Tark_Program_Standard_Room_Dresser',(SW_X1-.82,SW_X1-.16,SW_Y0+.20,SW_Y0+.76,.15,.88),M_OAK,.025)
for j,z in enumerate((.38,.57,.76)):
    add_box(f'Tark_Program_Standard_Room_Dresser_Drawer_{j}',(SW_X1-.77,SW_X1-.21,SW_Y0+.16,SW_Y0+.22,z-.05,z+.05),M_DARK,.012)
# Source metadata on the asset root makes the documented dimension and estimates explicit.
ROOT['sample_room_dimensions']='11 ft 7 in x 16 ft 2 in (approximately 3.53 x 4.93 m), Purdue housing page; schematic interior sample'
ROOT['sample_room_location_status']='schematic placement within west wing; Purdue page gives approximate room size but no room-plan coordinates'
# Clearer reception details and lobby lounge grouping.
add_box('Tark_Lobby_Reception_Monitor_Base',(-9.15,-8.85,-9.68,-9.34,1.28,1.34),M_DARK,.02)
add_box('Tark_Lobby_Reception_Monitor_Screen',(-9.18,-8.82,-9.66,-9.60,1.35,1.78),M_MONITOR,.025)
add_box('Tark_Lobby_Reception_Chair_Base',(-12.0,-11.5,-10.9,-10.3,.18,.34),M_DARK,.04)
add_box('Tark_Lobby_Reception_Chair_Seat',(-12.0,-11.5,-10.9,-10.3,.36,.55),M_NAVY,.04)
add_box('Tark_Lobby_Reception_Chair_Back',(-12.0,-11.5,-10.36,-10.2,.55,1.08),M_NAVY,.04)
add_box('Tark_Lobby_Lounge_Rug',(-11.2,-3.3,-14.9,-10.3,.17,.21),M_NAVY)
add_box('Tark_Lobby_Lounge_CoffeeTable_Top',(-8.1,-5.8,-13.7,-12.5,.56,.66),M_OAK,.04)
add_box('Tark_Lobby_Lounge_CoffeeTable_Base',(-7.4,-6.5,-13.35,-12.85,.22,.56),M_DARK,.035)
# Mailbox grid: shallow bronze doors and pulls on the established mail wall.
for row in range(4):
    for col in range(8):
        x=1.1+col*.74; z=.75+row*.48
        add_box(f'Tark_Lobby_Mailbox_Door_{row}_{col}',(x,x+.62,-9.34,-9.24,z,z+.37),M_LIME,.015)
        add_box(f'Tark_Lobby_Mailbox_Pull_{row}_{col}',(x+.47,x+.53,-9.38,-9.33,z+.16,z+.21),M_DARK)

# A compact recreation/study lounge in the verified north common-area mass.
add_box('Tark_North_Lounge_Carpet',(-20.0,14.8,19.8,32.0,.10,.18),M_NAVY)
def sofa(prefix,x,y):
    add_box(prefix+'_Seat',(x,x+2.5,y,y+1.0,.35,.85),M_NAVY,.12)
    add_box(prefix+'_Back',(x,x+2.5,y+.78,y+1.0,.82,1.55),M_NAVY,.10)
    add_box(prefix+'_Arm_L',(x,x+.22,y,y+1.0,.65,1.18),M_NAVY,.08)
    add_box(prefix+'_Arm_R',(x+2.28,x+2.5,y,y+1.0,.65,1.18),M_NAVY,.08)
sofa('Tark_North_Lounge_Sofa_0',-17.0,22.0)
sofa('Tark_North_Lounge_Sofa_1',-17.0,27.0)
add_box('Tark_North_Lounge_CoffeeTable',(-13.8,-10.7,24.2,25.5,.62,.72),M_OAK,.04)
add_box('Tark_North_Lounge_Piano_Case',(-20.0,-18.3,29.0,30.6,.52,1.45),M_DARK,.05)
add_box('Tark_North_Lounge_Piano_Keys',(-19.9,-18.25,28.92,29.04,1.15,1.2),M_LIME)
add_box('Tark_North_Lounge_Piano_Bench',(-20.0,-19.0,27.5,28.0,.42,.65),M_OAK,.035)
# Four student study stations with monitors and simple upholstered chairs.
for i in range(4):
    x=1.0+i*3.2
    add_box(f'Tark_North_Study_Desk_{i}',(x,x+2.4,22.0,23.0,.72,.82),M_OAK,.025)
    add_box(f'Tark_North_Study_Monitor_{i}',(x+.55,x+1.85,22.82,22.94,1.12,1.88),M_MONITOR,.025)
    add_box(f'Tark_North_Study_Chair_{i}_Seat',(x+.75,x+1.65,23.5,24.25,.44,.58),M_DARK,.035)
    add_box(f'Tark_North_Study_Chair_{i}_Back',(x+.75,x+1.65,24.05,24.24,.58,1.2),M_DARK,.035)
# One restrained pair of planters beside the lounge, not in circulation.
for i,x in enumerate((-19.0,13.2)):
    add_box(f'Tark_North_Lounge_Planter_{i}',(x,x+.65,20.0,20.65,.18,.7),M_PLANTER,.06)
    for leaf in range(5):
        cx=x+.12+(leaf%2)*.23; cy=20.12+(leaf//2)*.17
        add_box(f'Tark_North_Lounge_Plant_Leaf_{i}_{leaf}',(cx,cx+.18,cy,cy+.18,.68,1.18+(leaf%3)*.12),M_LEAF,.05)

# An unobtrusive evidence label on the library root records the confidence limit.
ROOT['roof_height_status']='estimated; approximately 19.1 m to modeled roof penthouse, no measured as-built elevation found'
ROOT['footprint_boundary_status']='Purdue GIS FID 662 is an outline of undocumented wall/roof-edge semantics; compared to registered 2023 orthophoto roof edges'

report={
 'revision':'R4',
 'asset':'Tarkington Hall',
 'source_height_status':'The 19.1 m maximum model extent is an estimate only; no reliable measured roof elevation was identified.',
 'footprint_updates':{
   'wing_shell_meshes_deformed':shell_deformed,
   'side_facade_windows_sills_repositioned':side_features_moved,
   'north_south_end_openings_resized':end_features_resized,
   'southeast_windows_sills_removed_below_roof_end':removed_se_openings,
   'north_bridge_depth_m':{'before':[19.0,33.0],'after':[19.0,28.0]},
   'middle_east_west_core_bridges_added':['west X[-45.8,-21.4], Y[-6,19]','east X[14.6,40.1], Y[-6,19]'],
   'north_pavilion_x_target_m':[-21.4,15.8],
   'south_entry_pavilion_x_y_target_m':{'x':[-7.2,7.1],'y':[-15,-13]},
   'south_lobby_core_x_y_target_m':{'x':[-21.4,15.7],'y':[-13,-9]},
 },
 'interior_updates':{
   'purdue_program_basis':['central lounge/reception','dining and kitchen (Pete’s Za)','study/recreation','mailroom','typical furnished double room'],
   'added_typical_room119_and_corridor_bay':True,
   'room118_and_room119_accessories':['desk lamps','bookshelves','drawers/dressers','closet handles','curtains','waste baskets'],
   'enhanced_reception_mailboxes_lobby_lounge':True,
   'north_common_lounge_study_piano_and_planters_added':True,
   'interior_program_locations_are_schematic_estimates_not_published_room-plan coordinates':True,
 },
 'gis_boundary_uncertainty':'Purdue GIS FID 662 is not documented as surveyed wall faces. The local wing profiles were selected from straight roof edges visible in the Spring 2023 Indiana ortho. The model boundary should be interpreted as a GIS/roof-edge proxy; no measured exterior wall line or as-built elevation was found.',
}
Path(bpy.path.abspath('//')).joinpath('refinement_r4_changes.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
out=Path(bpy.data.filepath).parent/'tarkington_hall_r4_candidate.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print(json.dumps(report,indent=2))


