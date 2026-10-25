import bpy, math, json, os
from mathutils import Vector

ROOT = os.path.abspath('.')
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'northwest_chiller_plant.blend')
OUT = os.path.join(ROOT, 'audit', 'northwest_chiller_plant_refine')
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=ASSET)
col = bpy.data.collections['Asset_northwest_chiller_plant']

def shader(name, base, metallic=0.0, rough=.72, texture=True):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*base, 1)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear(); nt.links.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bs = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Base Color'].default_value = (*base, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = rough
    nt.links.new(bs.outputs['BSDF'], out.inputs['Surface'])
    if texture:
        tc = nt.nodes.new('ShaderNodeTexCoord')
        noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 1.8
        noise.inputs['Detail'].default_value = 3.0; noise.inputs['Roughness'].default_value = .68
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        # Close ramp stops keep the reading as manufactured material, with restrained tonal drift.
        a = tuple(max(0.0, x*.82) for x in base) + (1,)
        b = tuple(min(1.0, x*1.18) for x in base) + (1,)
        ramp.color_ramp.elements[0].color = a
        ramp.color_ramp.elements[1].color = b
        nt.links.new(tc.outputs['Object'], noise.inputs['Vector'])
        nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
        nt.links.new(ramp.outputs['Color'], bs.inputs['Base Color'])
        fine = nt.nodes.new('ShaderNodeTexNoise'); fine.inputs['Scale'].default_value = 42
        fine.inputs['Detail'].default_value = 2; fine.inputs['Roughness'].default_value = .65
        nt.links.new(tc.outputs['Object'], fine.inputs['Vector'])
        bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = .12
        bump.inputs['Distance'].default_value = .006
        nt.links.new(fine.outputs['Fac'], bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'], bs.inputs['Normal'])
    return m

concrete = shader('NWCP_refine_precast_concrete', (.36,.38,.37), 0, .82)
coping = shader('NWCP_refine_cast_stone', (.48,.49,.46), 0, .78)
metal = shader('NWCP_refine_powder_coated_metal', (.12,.16,.17), .42, .44)
blade = shader('NWCP_refine_galvanized_louver_blades', (.27,.31,.31), .56, .42)
roof = shader('NWCP_refine_membrane_roof', (.20,.23,.24), .18, .84)
hvac = shader('NWCP_refine_cooling_tower_panels', (.56,.59,.57), .36, .62)
rubber = shader('NWCP_refine_fan_grille_dark', (.055,.075,.08), .52, .48)

def bounds(o):
    p=[o.matrix_world @ Vector(v) for v in o.bound_box]
    return ([min(v[i] for v in p) for i in range(3)], [max(v[i] for v in p) for i in range(3)])

def box(name, loc, dims, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o); o.data.materials.clear(); o.data.materials.append(mat)
    return o

# Replace the overly flat source finishes with portable object-space concrete, metal and roof materials.
shell = bpy.data.objects['northwest_chiller_plant_official_GIS_shell']
shell.data.materials.clear(); shell.data.materials.append(concrete)
for o in col.all_objects:
    if not hasattr(o.data, 'materials'): continue
    if o.name.startswith('NWCP_stringcourse_') or o.name.startswith('NWCP_parapet_cap_'):
        o.data.materials.clear(); o.data.materials.append(coping)
    elif o.name.startswith('NWCP_acoustic_louver_bank_'):
        o.data.materials.clear(); o.data.materials.append(rubber)
    elif o.name.startswith('NWCP_louver_blade_'):
        o.data.materials.clear(); o.data.materials.append(blade)
    elif o.name == 'northwest_chiller_plant_flat_roof_surface':
        o.data.materials.clear(); o.data.materials.append(roof)
    elif o.name.startswith('NWCP_roof_cooling_cell_'):
        o.data.materials.clear(); o.data.materials.append(hvac)
    elif o.name.startswith(('NWCP_roof_fan_grille_', 'NWCP_revision_rooftop_axial_fan_')):
        o.data.materials.clear(); o.data.materials.append(rubber)
    elif o.name.startswith(('NWCP_revision_fan_blade_', 'NWCP_revision_fan_hub_')):
        o.data.materials.clear(); o.data.materials.append(metal)
    elif o.name.startswith(('NWCP_roof_chilled_water_header_', 'NWCP_vertical_pipe_riser_')):
        o.data.materials.clear(); o.data.materials.append(metal)

# Distinct panel joints on the broad upper equipment-room walls, stopping above the louver banks.
shell_lo, shell_hi = bounds(shell)
front_y, back_y = shell_lo[1]-.015, shell_hi[1]+.015
left_x, right_x = shell_lo[0]-.015, shell_hi[0]+.015
joint = shader('NWCP_refine_panel_joint_shadow', (.25,.28,.28), .12, .78, texture=False)
added=[]
for face, y in [('north',back_y), ('south',front_y)]:
    for i,x in enumerate([-13.2,-7.2,-1.2,4.8,10.8,16.8]):
        o=box(f'NWCP_refine_{face}_precast_joint_{i+1}', (x,y,8.83), (.035,.045,2.9), joint); added.append(o.name)
for face,x in [('east',right_x), ('west',left_x)]:
    for i,y in enumerate([-14.0,-8.0,-2.0,4.0,10.0,16.0]):
        o=box(f'NWCP_refine_{face}_precast_joint_{i+1}', (x,y,8.83), (.045,.035,2.9), joint); added.append(o.name)

# A subtle, consistent perimeter rail sharpens the large acoustic louver cassettes.
rail = shader('NWCP_refine_louver_frame', (.085,.11,.12), .55, .4, texture=False)
for bank in [o for o in col.all_objects if o.name.startswith('NWCP_acoustic_louver_bank_')]:
    lo,hi=bounds(bank); dx,dy,dz=[hi[i]-lo[i] for i in range(3)]
    cx,cy,cz=[(lo[i]+hi[i])/2 for i in range(3)]
    if dy < dx: # north/south wall, bank width runs east-west
        outside = -1 if cy < 1.4 else 1
        y=cy + outside*.17
        for side,x in [('L',lo[0]-.045),('R',hi[0]+.045)]:
            o=box(f'NWCP_refine_louver_frame_{bank.name}_{side}',(x,y,cz),(.09,.10,dz+.10),rail); added.append(o.name)
    else: # east/west wall, bank width runs north-south
        outside = -1 if cx < 1.7 else 1
        x=cx + outside*.17
        for side,y in [('L',lo[1]-.045),('R',hi[1]+.045)]:
            o=box(f'NWCP_refine_louver_frame_{bank.name}_{side}',(x,y,cz),(.10,.09,dz+.10),rail); added.append(o.name)

# Cooler-cell sheet-metal ribs and serviceable panel breaks. Existing cell count and positions remain intact.
for cell in [o for o in col.all_objects if o.name.startswith('NWCP_roof_cooling_cell_')]:
    lo,hi=bounds(cell); cx=(lo[0]+hi[0])/2; y=lo[1]-.035; z0=lo[2]+.40; z1=hi[2]-.35
    # Vertical folded ribs on the visible intake face.
    for j in range(1,8):
        x=lo[0]+(hi[0]-lo[0])*j/8
        o=box(f'NWCP_refine_{cell.name}_face_rib_{j}',(x,y,(z0+z1)/2),(.035,.055,z1-z0),coping); added.append(o.name)
    # Continuous side reveal, restrained in scale to avoid inventing extra equipment.
    o=box(f'NWCP_refine_{cell.name}_access_panel_seam',(hi[0]+.025,(lo[1]+hi[1])/2, (lo[2]+hi[2])/2),(.055,hi[1]-lo[1]-.35,.025),joint); added.append(o.name)
    if not any(m.name == 'NWCP_refine_cell_bevel' for m in cell.modifiers):
        bevel=cell.modifiers.new('NWCP_refine_cell_bevel','BEVEL'); bevel.width=.055; bevel.segments=3
        cell.modifiers.new('NWCP_refine_cell_weighted_normals','WEIGHTED_NORMAL')

# Detail the large industrial access double door with a recessed center seam, pull bars and hinges.
door=bpy.data.objects.get('NWCP_service_double_door')
if door:
    lo,hi=bounds(door); x0,x1=lo[0],hi[0]; y=lo[1]-.075; z0,z1=lo[2],hi[2]
    o=box('NWCP_refine_service_door_center_seam',((x0+x1)/2,y,(z0+z1)/2),(.025,.035,z1-z0-.15),rail); added.append(o.name)
    for side,x in [('left',x0+(x1-x0)*.43),('right',x0+(x1-x0)*.57)]:
        o=box(f'NWCP_refine_service_door_pull_{side}',(x,y-.03,(z0+z1)/2),(.055,.045,.55),coping); added.append(o.name)
    for side,x in [('L',x0+.04),('R',x1-.04)]:
        for j,z in enumerate((z0+.65,(z0+z1)/2,z1-.65)):
            o=box(f'NWCP_refine_service_door_hinge_{side}_{j+1}',(x,y-.015,z),(.08,.035,.18),metal); added.append(o.name)

# Ensure shell's authoritative GIS footprint and height are untouched.
verify_lo, verify_hi = bounds(shell)
assert all(abs(shell_lo[i]-verify_lo[i])<1e-5 and abs(shell_hi[i]-verify_hi[i])<1e-5 for i in range(3))

# Render a clean three-quarter overview and a close service-façade view; remove temporary cameras afterward.
scene=bpy.context.scene
old_camera=scene.camera
old_world=scene.world
world=bpy.data.worlds.new('NWCP_refine_preview_world'); world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.22,.28,.33,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
scene.world=world
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.render.image_settings.color_mode='RGBA'
scene.render.filepath=os.path.join(OUT,'northwest_chiller_plant_refine_overview.png')
def cam_at(name, pos, target, ortho):
    data=bpy.data.cameras.new(name); obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj)
    obj.location=pos; obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler(); data.type='ORTHO'; data.ortho_scale=ortho; return obj
def area(name,loc,target,power,size):
    d=bpy.data.lights.new(name,'AREA'); o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler(); d.energy=power; d.shape='DISK'; d.size=size; return o
target=(1,0,7)
lights=[area('NWCP_refine_key',(-25,-35,40),target,4200,24),area('NWCP_refine_fill',(25,-5,28),target,2600,20),area('NWCP_refine_rim',(5,32,32),target,3300,18)]
cam=cam_at('NWCP_refine_overview_camera',(48,-58,42),target,66); scene.camera=cam
bpy.ops.render.render(write_still=True)
scene.render.filepath=os.path.join(OUT,'northwest_chiller_plant_refine_detail.png')
cam.location=(35,-43,18); cam.data.ortho_scale=32; cam.rotation_euler=(Vector((1,-4,7))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.render.render(write_still=True)
scene.camera=old_camera; scene.world=old_world
cam_data=cam.data
light_data=[l.data for l in lights]
for o in [cam,*lights]: bpy.data.objects.remove(o,do_unlink=True)
bpy.data.cameras.remove(cam_data)
for d in light_data: bpy.data.lights.remove(d)
bpy.data.worlds.remove(world)
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
summary={
 'building':'Northwest Chiller Plant', 'date':'2026-10-25',
 'sources':[
   {'url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','use':'Official Purdue GIS footprint and source elevations; the six-vertex shell is kept unchanged.'},
   {'url':'https://www.purdue.edu/bot/meetings/past-meetings/2022/07.%20aug/pfc/Northwest%20Chiller%20Plant.pdf','use':'Official project record confirms pump/supporting-equipment upgrades and chilled-water function.'},
   {'url':'https://www.purdue.edu/treasurer/finance/wp-content/uploads/2023/04/Northwest-Chiller-Plant-System-Improvements-B-1-23-2-04.pdf','use':'Official project record confirms active utility-plant operations and system-improvement scope.'},
   {'url':'https://purduesports.com/utility-project-altering-baseball-softball-track-traffic','use':'Purdue Athletics locates the plant southwest of Lambert Field.'}
 ],
 'changes':[
   'Replaced flat export finishes with portable procedural precast-concrete, cast-stone, galvanized-metal, dark louver, membrane-roof and cooling-cell materials.',
   'Added subtle upper-wall panel joints and cassette edge rails to give the large acoustic-louver fields a manufactured, assembled reading.',
   'Added folded sheet-metal ribs and bevelled edges to the five existing rooftop cooling-cell enclosures; their count and placement are unchanged and are typology-based, not verified from as-built plans.',
   'Added restrained service-door seam, pull bars and hinges; retained the source door position and footprint.',
   'Preserved authoritative GIS shell geometry, orientation and placement. Existing schematic interior and service-yard equipment remain interpretive, not as-built.'
 ],
 'new_objects':added,
 'limitations':['No construction drawings or verified close exterior photo were found in the source set; exact cooling-cell layout, pipe routing, panel rhythm and interior arrangements remain approximate.']
}
with open(os.path.join(OUT,'refinement_notes.json'),'w',encoding='utf-8') as f: json.dump(summary,f,indent=2)
print('SAVED',ASSET,'objects',len(col.all_objects),'added',len(added),flush=True)
