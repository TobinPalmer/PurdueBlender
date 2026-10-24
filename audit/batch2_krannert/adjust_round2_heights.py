import bpy, os

ROOT = r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET = ROOT + r'/modular/buildings/krannert_building.blend'
bpy.ops.wm.open_mainfile(filepath=ASSET)
C = bpy.data.collections['Asset_krannert_building']

# Bring conference table legs down to the floor and into the tabletop underside.
for o in C.objects:
    if o.name.startswith('KRAN_R2_Conference_Table_Leg'):
        o.location.z = 4.32
        o.dimensions.z = 0.84
        o.location.y = 1.48 if o.location.y < 1.8 else 2.55
    elif o.name.startswith('KRAN_R2_DrawingRoom_Conference_Table'):
        o.location.y = 2.02
    elif o.name.startswith('KRAN_R2_Conference_Chair_Seat'):
        o.location.y = 0.90 if o.location.y < 2.0 else 3.00
    elif o.name.startswith('KRAN_R2_Conference_Chair_Back'):
        o.location.y = 1.13 if o.location.y < 2.0 else 3.23
    elif o.name.startswith('KRAN_R2_Conference_Chair_Leg'):
        if o.location.y < 2.0:
            o.location.y = .71 if o.location.y < 1.0 else 1.09
        else:
            o.location.y = 2.81 if o.location.y < 3.0 else 3.19

# Extend the group room 15 cm north while keeping the modeled shell/carpet frame.
for o in C.objects:
    if o.name in {'KRAN_R2_DrawingRoom_Glass_Panel', 'KRAN_R2_DrawingRoom_Glass_Panel.001'}:
        o.location.y = 1.70
        o.dimensions.y = 3.70
    elif o.name == 'KRAN_R2_DrawingRoom_Glass_Panel.002':
        o.location.y = 3.55
    elif o.name.startswith('KRAN_R2_DrawingRoom_Glass_Mullion') and o.location.y > 3.3:
        o.location.y = 3.55

# High-top tables: 1.07 m worktop height from the Drawing Room floor (z=3.90).
for o in C.objects:
    if o.name.startswith('KRAN_R2_DrawingRoom_Window_HighTop'):
        o.location.z = 4.97
    elif o.name.startswith('KRAN_R2_DrawingRoom_HighTop_Pedestal'):
        o.location.z = 4.43
        o.dimensions.z = 0.98
    elif o.name.startswith('KRAN_R2_DrawingRoom_HighTop_Foot'):
        o.location.z = 3.94

# Seat surfaces at roughly 0.73 m, with pedestals/feet meeting the floor rather
# than passing through it. Add a narrow metal foot ring to each stool.
for o in C.objects:
    if o.name.startswith('KRAN_R2_DrawingRoom_HighStool_Seat'):
        o.location.z = 4.62
    elif o.name.startswith('KRAN_R2_DrawingRoom_HighStool_Pedestal'):
        o.location.z = 4.26
        o.dimensions.z = 0.67
    elif o.name.startswith('KRAN_R2_DrawingRoom_HighStool_Foot'):
        o.location.z = 3.94

metal = bpy.data.materials['KRAN_R2_Furniture_Metal']
if not any(o.name.startswith('KRAN_R2_DrawingRoom_HighStool_FootRing') for o in C.objects):
    for x in [-18.68, -17.72, -16.08, -15.12]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.014,
                                         major_segments=24, minor_segments=8,
                                         location=(x, 2.10, 4.18))
        o = bpy.context.object
        o.name = 'KRAN_R2_DrawingRoom_HighStool_FootRing'
        for cc in list(o.users_collection): cc.objects.unlink(o)
        C.objects.link(o)
        o.parent = bpy.data.objects['AssetRoot_krannert_building']
        o.matrix_parent_inverse = o.parent.matrix_world.inverted()
        o.data.materials.append(metal)
        o['layout_status'] = 'Bar-stool foot ring, material and proportions estimated from the photo-supported high-top seating type.'

bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print('Adjusted support heights and added four stool foot rings.')
