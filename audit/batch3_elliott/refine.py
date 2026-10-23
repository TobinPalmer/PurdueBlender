"""Refine the Elliott source library from Purdue's current official seat map.

Only this building library is written. Position scale inside the auditorium is
an estimate because the published map is a seating diagram, not a scaled plan.
"""
import bpy, math, json, pathlib, shutil
from mathutils import Vector

ROOT = pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
SRC = ROOT / 'modular/buildings/elliott_hall_of_music.blend'
AUD = ROOT / 'audit/batch3_elliott'
shutil.copy2(SRC, AUD / 'before_resume.blend')
bpy.ops.wm.open_mainfile(filepath=str(SRC))
COL = bpy.data.collections['Asset_elliott_hall_of_music']
WALL = bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls']
ROT = math.radians(-129.36)
COS, SIN = math.cos(ROT), math.sin(ROT)

# Remove the preceding conceptual interior so the eight-section layout is clean.
for ob in list(COL.objects):
    if ob.name.startswith('ELLT_B3_'):
        bpy.data.objects.remove(ob, do_unlink=True)

def material(name, color, rough=.75, noise_scale=None, bump_distance=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bs = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = rough
    nt.links.new(bs.outputs['BSDF'], out.inputs['Surface'])
    if noise_scale:
        tex = nt.nodes.new('ShaderNodeTexCoord')
        noise = nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = noise_scale
        noise.inputs['Detail'].default_value = 2
        nt.links.new(tex.outputs['Object'], noise.inputs['Vector'])
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .2
        ramp.color_ramp.elements[0].color = (*tuple(v*.83 for v in color), 1)
        ramp.color_ramp.elements[1].position = .8
        ramp.color_ramp.elements[1].color = (*tuple(min(1,v*1.12) for v in color), 1)
        nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
        nt.links.new(ramp.outputs['Color'], bs.inputs['Base Color'])
        if bump_distance:
            bump = nt.nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value = .12
            bump.inputs['Distance'].default_value = bump_distance
            nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
            nt.links.new(bump.outputs['Normal'], bs.inputs['Normal'])
    return m

MAT = {
    'stage': material('ELLT_B3_Stage_Oak_Grain', (.25,.14,.075), .55, 36, .0008),
    'plaster': material('ELLT_B3_Auditorium_Wall_Pale_Plaster', (.72,.68,.57), .86, 9, .00025),
    'side_teal': material('ELLT_B3_Interior_Wainscot_Teal', (.018,.09,.095), .64),
    'curtain': material('ELLT_B3_Stage_Curtain_Red_Velour', (.25,.012,.02), .92, 110, .0005),
    'blackout': material('ELLT_B3_Stage_Main_Drape', (.009,.012,.016), .93, 110, .0005),
    'seat': material('ELLT_B3_Theatre_Seat_Brown_Fabric', (.35,.22,.13), .9, 170, .00055),
    'access': material('ELLT_B3_Accessible_Seat_Blue', (.045,.16,.42), .88, 140, .00045),
    'frame': material('ELLT_B3_Seat_Frame_Dark_Bronze', (.035,.038,.04), .55),
    'carpet': material('ELLT_B3_Theatre_Carpet', (.16,.15,.14), .94, 42, .0004),
    'stair': material('ELLT_B3_Aisle_Stair_Stone', (.28,.29,.29), .82, 32, .0003),
    'balcony': material('ELLT_B3_Balcony_Fascia_Teal', (.025,.105,.11), .68),
    'rail': material('ELLT_B3_Balcony_Railing_Bronze', (.10,.085,.058), .48),
    'ceiling': material('ELLT_B3_Acoustic_Ceiling_Tile', (.73,.71,.66), .93, 7, .0002),
    'ceiling_edge': material('ELLT_B3_Ceiling_Tile_Joint', (.39,.39,.37), .8),
    'light': material('ELLT_B3_Work_Light_Housing', (.09,.095,.10), .4),
    'glow': material('ELLT_B3_Auditorium_Light', (.96,.78,.48), .3),
}

# Combined meshes keep the linked library compact while preserving seat details.
batches = {}
FACES = [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
def cube(name, center, dims, matkey, yaw=0.0, tilt=0.0):
    verts, faces = batches.setdefault(matkey, ([], []))
    base = len(verts)
    cx,cy,cz = center; dx,dy,dz = dims
    cyaw, syaw = math.cos(yaw), math.sin(yaw)
    ctilt, stilt = math.cos(tilt), math.sin(tilt)
    for ix,iy,iz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]:
        x,y,z = ix*dx/2, iy*dy/2, iz*dz/2
        # Chair-back tilt about local Y, then yaw toward the stage.
        x,z = x*ctilt + z*stilt, -x*stilt + z*ctilt
        x,y = x*cyaw-y*syaw, x*syaw+y*cyaw
        x += cx; y += cy; z += cz
        verts.append((x*COS-y*SIN, x*SIN+y*COS, z))
    faces.extend(tuple(base+i for i in f) for f in FACES)

# Official seating illustration has three levels, 8 named sections, and row
# labels A-Z plus AA-ZZ on the main floor, A-U first balcony, A-M second.
widths = [4.4, 4.8, 5.1, 5.4, 5.4, 5.1, 4.8, 4.4]
gaps = [.65] * 7
left = -(sum(widths)+sum(gaps))/2
centers = []
for i,w in enumerate(widths):
    centers.append(left + w/2)
    left += w + (gaps[i] if i < len(gaps) else 0)

outline = [(float(v.co.x), float(v.co.y)) for v in WALL.data.vertices if abs(v.co.z) < .01]
def inside(px, py):
    # Check against official GIS perimeter in source local coordinates.
    q = False
    for i,(ax,ay) in enumerate(outline):
        bx,by = outline[i-1]
        if (ay > py) != (by > py) and px < (bx-ax)*(py-ay)/(by-ay)+ax:
            q = not q
    return q

section_start = [12,7,2,0,0,2,7,12]
levels = [
    {'name':'main_floor','rows':52,'x0':-12.5,'dx':.64,'z0':.32,'dz':.073,'active':section_start},
    {'name':'first_balcony','rows':21,'x0':7.0,'dx':.70,'z0':6.30,'dz':.155,'active':[0]*8},
    {'name':'second_balcony','rows':13,'x0':9.0,'dx':.70,'z0':10.25,'dz':.15,'active':[0]*8},
]
seat_pitch = .50
seat_count = 0
accessible_count = 0
seat_corners = [(-.23,-.25),(.23,-.25),(-.23,.25),(.23,.25)]
chair_records = []
for li,lev in enumerate(levels):
    for r in range(lev['rows']):
        rowx = lev['x0'] + r*lev['dx']
        floorz = lev['z0'] + r*lev['dz']
        # Omit the official blocked central area at the rear of the second balcony.
        for si,(cy,w) in enumerate(zip(centers,widths)):
            if r < lev['active'][si]:
                continue
            if li == 2 and r >= 10 and si in (3,4):
                continue
            n = int(w/seat_pitch)
            y0 = cy - (n-1)*seat_pitch/2
            # Seat-section flooring follows each fan bank; aisles remain open.
            xrow = rowx + .007*cy*cy
            cube(f'{lev["name"]}_carpet', (xrow+.30,cy,floorz-.015),(.62,w,.075),'carpet')
            for k in range(n):
                y = y0 + k*seat_pitch
                x = rowx + .007*y*y
                if not all(inside((x+xx)*COS-(y+yy)*SIN,(x+xx)*SIN+(y+yy)*COS) for xx,yy in seat_corners):
                    continue
                yaw = math.atan2(-y, -22.0-x) - math.pi
                # Four small groups shown in Purdue's map use blue accessible-seat marks.
                accessible = (li == 0 and ((si in (2,5) and r in (1,2) and k in (1,n-2)) or
                              (si in (0,7) and r in (19,20) and k in (1,n-2))))
                mkey = 'access' if accessible else 'seat'
                accessible_count += int(accessible)
                # Sculpted cushion, reclined back, side supports and armrests.
                cube('Seat_Cushion', (x,y,floorz+.40),(.48,.46,.135),mkey,yaw)
                cube('Seat_Back', (x+.235,y,floorz+.83),(.135,.46,.59),mkey,yaw,math.radians(8))
                for sy in (-1,1):
                    cube('Seat_Side_Support',(x+.14,y+sy*.232,floorz+.39),(.06,.055,.70),'frame',yaw)
                    cube('Seat_Armrest',(x+.01,y+sy*.255,floorz+.69),(.55,.05,.055),'frame',yaw)
                for sx in (-.16,.16):
                    for sy in (-.19,.19):
                        cube('Seat_Leg',(x+sx,y+sy,floorz+.16),(.038,.038,.31),'frame',yaw)
                seat_count += 1
                chair_records.append([li,r,si,k])
        # Stair treads rise with the seating rows and connect every seating bank.
        for gi in range(7):
            gy = (centers[gi]+widths[gi]/2 + centers[gi+1]-widths[gi+1]/2)/2
            if li == 2 and r >= 10 and gi in (3,):
                continue
            xx = rowx + .007*gy*gy
            if inside(xx*COS-gy*SIN, xx*SIN+gy*COS):
                cube(f'{lev["name"]}_Aisle_Tread',(xx+.30,gy,floorz+.035),(.64,.70,.07),'stair')

# Stage is the northeast end within the official perimeter; its measurements are estimates.
cube('Stage_Deck',(-22,0,1.05),(11,34,.60),'stage')
cube('Stage_Front_Apron',(-16.3,0,1.20),(.60,34,.35),'stage')
cube('Proscenium_Left_Pier',(-15.9,-17,6.8),(.55,.72,11.8),'plaster')
cube('Proscenium_Right_Pier',(-15.9,17,6.8),(.55,.72,11.8),'plaster')
cube('Proscenium_Header',(-15.9,0,12.6),(.60,34.7,1.0),'plaster')
for y in [i*.56-15.4 for i in range(56)]:
    cube('Stage_Curtain_Fold',(-27.2,y,6.7),(.22,.48,10.4),'blackout' if abs(y)<11.8 else 'curtain')
for y in [-16.8,16.8]:
    cube('Stage_Side_Drape',(-22.4,y,6.8),(8.8,.28,10.6),'curtain')

# Pale wall panels and teal lower band reproduce the auditorium colors visible
# in Purdue's 2024 interior gallery. Wall heights and panel spacing are estimated.
for side in (-1,1):
    cube('Auditorium_Teal_Wainscot',(0,side*21.7,1.65),(48,.28,3.1),'side_teal')
    cube('Auditorium_Pale_Sidewall',(0,side*21.68,10.35),(48,.30,14.3),'plaster')
    for x in [-21,-16,-11,-6,-1,4,9,14,19,24]:
        cube('Auditorium_Vertical_Pier',(x,side*21.42,10.2),(.34,.30,15.3),'plaster')
cube('Auditorium_Rear_Interior_Wall',(26.6,0,9.0),(.30,43,18.0),'plaster')
cube('Stage_Back_Interior_Wall',(-29.3,0,9.0),(.30,43,18.0),'plaster')
for x in (26.43,-29.13):
    for y in (-16,-8,0,8,16):
        cube('Interior_Egress_Door_Panel',(x,y,1.8),(.10,1.55,2.65),'side_teal')
        cube('Interior_Egress_Door_Lintel',(x,y,3.18),(.14,1.8,.18),'plaster')

# Two balcony fascias, rails and regularly spaced supports follow the eight-bank layout.
for li,lev in enumerate(levels[1:], start=1):
    front_x = lev['x0']-.38
    topz = lev['z0']+.55
    cube(f'{lev["name"]}_Fascia',(front_x,0,topz-0.25),(.72,41,.95),'balcony')
    cube(f'{lev["name"]}_Handrail',(front_x-.12,0,topz+.83),(.09,41,.07),'rail')
    for yy in [centers[0]-widths[0]/2,centers[-1]+widths[-1]/2]:
        cube(f'{lev["name"]}_Side_Rail',(front_x-.12,yy,topz+.46),(.09,.09,.85),'rail')
    for j in range(27):
        yy = -19.5 + j*1.5
        cube(f'{lev["name"]}_Railing_Post',(front_x-.12,yy,topz+.42),(.075,.055,.82),'rail')

# Purdue's 2025 facilities request calls out replacement acoustic ceiling tiles
# at a 60 ft ceiling. Scale is approximate; tile color/spacing is representational.
ceiling_z = 18.288
for x in [ -28 + i*1.22 for i in range(45) ]:
    for y in [ -20 + j*1.22 for j in range(33) ]:
        cube('Acoustic_Ceiling_Tile',(x,y,ceiling_z), (1.17,1.17,.07),'ceiling')
for x in [-22,-7,8,23]:
    cube('Ceiling_Lighting_Track',(x,0,ceiling_z-.28),(.06,38,.06),'light')
    for y in [-16,-8,0,8,16]:
        cube('Auditorium_Light_Housing',(x,y,ceiling_z-.39),(.72,.42,.18),'glow')

# Build each material group as one mesh object. Keep local asset and collection names unchanged.
for key,(verts,faces) in batches.items():
    if not verts:
        continue
    mesh = bpy.data.meshes.new(f'ELLT_B3_{key}_Mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(MAT[key])
    mesh.update()
    ob = bpy.data.objects.new(f'ELLT_B3_{key}',mesh)
    COL.objects.link(ob)
    ob['evidence_status'] = 'Seating map/photo informed; interior dimensions and seat pitch are estimates'
    if key in ('seat','access'):
        bevel = ob.modifiers.new('Soft upholstered cushion edges','BEVEL')
        bevel.width = .018
        bevel.segments = 2
        bevel.limit_method = 'ANGLE'
    if key == 'carpet':
        ob['row_counts'] = {'main_floor':52,'first_balcony':21,'second_balcony':13}

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 20
bpy.context.scene.render.resolution_x = 1250
bpy.context.scene.render.resolution_y = 850
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.view_settings.view_transform = 'AgX'
world = bpy.data.worlds.new('ELLT_Review_World')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (.22,.22,.22,1)
bpy.context.scene.world = world
for obj in list(bpy.context.scene.objects):
    if obj.name.startswith(('ELLT_B3_ReviewCam','ELLT_B3_ReviewLight')):
        bpy.data.objects.remove(obj,do_unlink=True)
def camera(name,loc,target,lens=30):
    data=bpy.data.cameras.new(name); obj=bpy.data.objects.new(name,data); bpy.context.scene.collection.objects.link(obj)
    def rotate_xy(p):
        return Vector((p[0]*COS-p[1]*SIN,p[0]*SIN+p[1]*COS,p[2]))
    data.lens=lens;obj.location=rotate_xy(loc);obj.rotation_euler=(rotate_xy(target)-obj.location).to_track_quat('-Z','Y').to_euler();return obj
ld=bpy.data.lights.new('ELLT_B3_Review_Area','AREA');ld.energy=5000;ld.shape='DISK';ld.size=16
light=bpy.data.objects.new('ELLT_B3_ReviewLight',ld);bpy.context.scene.collection.objects.link(light)
def rotate_xy(p):
    return Vector((p[0]*COS-p[1]*SIN,p[0]*SIN+p[1]*COS,p[2]))
light.location=rotate_xy((-12,-3,16));light.rotation_euler=(rotate_xy((0,0,6))-light.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene
for name,loc,target in [('from_stage',(-24,0,11),(17,0,9)),('from_rear',(24,0,14),(-18,0,6)),('from_balcony',(4,-18,13),(-9,0,6))]:
    cam=camera('ELLT_B3_ReviewCam_'+name,loc,target,30);scene.camera=cam
    scene.render.filepath=str(AUD/f'{name}.png')
    bpy.ops.render.render(write_still=True)

# Review helpers stay in the audit renders only, never in the library scene.
for ob in list(bpy.context.scene.objects):
    if ob.name.startswith(('ELLT_B3_ReviewCam','ELLT_B3_ReviewLight')):
        bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SRC))
bpy.ops.wm.open_mainfile(filepath=str(SRC))
COL=bpy.data.collections['Asset_elliott_hall_of_music']
mesh_objects=[o for o in COL.all_objects if o.type=='MESH']
world_bounds=[[(o.matrix_world@Vector(corner))[i] for i in range(3)] for o in mesh_objects for corner in o.bound_box]
minimum=[min(v[i] for v in world_bounds) for i in range(3)]
maximum=[max(v[i] for v in world_bounds) for i in range(3)]
report={
    'saved_and_reopened':True,
    'export_collection':'Asset_elliott_hall_of_music',
    'export_objects':len(COL.all_objects),
    'mesh_objects':len(mesh_objects),
    'modeled_seats':seat_count,
    'accessible_marked_seats':accessible_count,
    'row_counts':{'main_floor':52,'first_balcony':21,'second_balcony':13},
    'seat_sections':8,
    'dimensions_local_m':{'min':minimum,'max':maximum},
    'floorplan_scale':'Estimated from unscaled Purdue seating illustration; seats constrained to official GIS perimeter.',
    'height_evidence':'Ceiling height 60 ft from Purdue facilities 2025 project request; balcony elevations estimated.',
    'remaining':'Exterior facade subdivision, measured seat coordinates, lobby/backstage partition plan, fly tower, and exact balcony elevations remain unverified.'
}
(AUD/'result_refined.json').write_text(json.dumps(report,indent=2))
(AUD/'seat_centers.json').write_text(json.dumps(chair_records))
print(json.dumps(report,indent=2))
