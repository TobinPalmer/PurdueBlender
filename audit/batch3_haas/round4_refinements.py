import bpy, json, math, re
from pathlib import Path
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']; P=bpy.data.filepath
# Relocate modeled side bays to fit the preserved GIS long-wall run (x -25.85..2.24).
old_centers=[-21.0,-13.0,-5.0,3.0,10.0]; new_centers=[-22.0,-16.0,-10.0,-4.0,1.0]
for o in list(C.objects):
    if o.name.startswith('HAAS_Estimated_Side_Stone_Band_'):
        bpy.data.objects.remove(o,do_unlink=True)
        continue
    if not o.name.startswith('HAAS_Estimated_Side_'): continue
    # Bay index is encoded as _S_<index> on window/jamb/lintel objects.
    m=re.search(r'_S_(\d+)(?:_|$)',o.name)
    if not m: continue
    idx=int(m.group(1))
    if idx>=len(old_centers): continue
    o.location.x += new_centers[idx]-old_centers[idx]
# Remove any prior round-four repeated facade objects before idempotent rebuild.
for o in list(C.objects):
    if o.name.startswith(('HAAS_R4_Long_','HAAS_R4_West_')): bpy.data.objects.remove(o,do_unlink=True)
def mat(name,color,rough=.78):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough
    return m
stone=mat('HAAS_Photo_Limestone',(0.89,.77,.55))
for n in ['HAAS_Bedford_Limestone']:
    m=bpy.data.materials.get(n)
    if m:
        m.diffuse_color=(.89,.77,.55,1)
        if m.use_nodes and m.node_tree.nodes.get('Principled BSDF'):m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.89,.77,.55,1)
brickmat=bpy.data.materials.get('Purdue_Red_Brick.001')
if brickmat:
    brickmat.diffuse_color=(.36,.105,.045,1)
    for n in brickmat.node_tree.nodes:
        if n.type=='TEX_BRICK':
            n.inputs['Color1'].default_value=(.36,.105,.045,1); n.inputs['Color2'].default_value=(.23,.055,.025,1); n.inputs['Mortar'].default_value=(.24,.15,.105,1)
roof=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated']
roof.diffuse_color=(.20,.04,.02,1)
for n in roof.node_tree.nodes:
    if n.type=='TEX_BRICK':
        n.inputs['Color1'].default_value=(.22,.048,.022,1); n.inputs['Color2'].default_value=(.145,.026,.012,1); n.inputs['Mortar'].default_value=(.085,.018,.009,1)
        n.inputs['Brick Width'].default_value=.34; n.inputs['Row Height'].default_value=.17; n.inputs['Mortar Size'].default_value=.004
        n.inputs['Scale'].default_value=1.0
    if n.type=='BUMP': n.inputs['Strength'].default_value=.28; n.inputs['Distance'].default_value=.006
# Shared box helper; dimensions are authored in world meters, not inferred survey dimensions.
def box(name,loc,dims,material,description):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection):c.objects.unlink(o)
    C.objects.link(o);o.data.materials.clear();o.data.materials.append(material);o['evidence']=description;return o
ref='Visual interpretation of Purdue Events exterior photograph; bay locations and dimensions are estimates, not a measured elevation.'
# Establish continuous limestone base/belt/cornice lines on both long elevations.
for side,y in [('South',-26.08),('North',26.84)]:
    for i,(z,h) in enumerate([(1.02,.24),(5.15,.18),(9.55,.25)]):
        box(f'HAAS_R4_Long_{side}_Band_{i}',(-11.78,y,z),(27.65,.17,h),stone,ref)
    # Six aligned pilasters define five equally spaced bays inside the main GIS wall.
    for i,x in enumerate([-25.45,-19.75,-14.05,-8.35,-2.65,1.65]):
        box(f'HAAS_R4_Long_{side}_Pier_{i}',(x,y,5.18),(.48,.20,8.35),stone,ref)
        box(f'HAAS_R4_Long_{side}_PierBase_{i}',(x,y,1.02),(.70,.23,.32),stone,ref)
        box(f'HAAS_R4_Long_{side}_PierCap_{i}',(x,y,9.50),(.70,.23,.32),stone,ref)
# Mirrored window overlays on the far long elevation. Nondimensional plan/photo do not establish this fenestration schedule.
shift_y=52.92
for o in list(C.objects):
    if not o.name.startswith('HAAS_Estimated_Side_'): continue
    if 'Stone_Band' in o.name: continue
    dup=o.copy(); dup.data=o.data.copy() if o.data else None; dup.name=o.name.replace('_S_','_N_',1)+'_R4'
    dup.location=o.location.copy(); dup.location.y+=shift_y
    C.objects.link(dup); dup['evidence']=ref+' Opposite elevation is mirrored as an explicit estimate; no measured or archival side elevation located.'
# Give the west end a consistent estimated masonry rhythm. Its shell runs x=-26.22 across y -25.98..26.56.
westx=-26.34
for i,y in enumerate([-24.5,-14.5,-4.5,5.5,15.5,25.0]):
    box(f'HAAS_R4_West_Pier_{i}',(westx,y,5.18),(.20,.48,8.35),stone,ref)
    box(f'HAAS_R4_West_Base_{i}',(westx,y,1.02),(.23,.70,.32),stone,ref)
    box(f'HAAS_R4_West_Cap_{i}',(westx,y,9.50),(.23,.70,.32),stone,ref)
for i,y in enumerate([-19.5,-9.5,.5,10.5,20.5]):
    # Three-part dark glazing, stone jambs/sill/lintel make a readable two-storey bay.
    for floor,z,w,h in [('Lower',3.1,2.2,2.2),('Upper',7.35,2.1,1.65)]:
        box(f'HAAS_R4_West_{floor}Glass_{i}',(westx-.035,y,z),(.06,w,h),mat('HAAS_Estimated_Glazing',(.045,.095,.12),.28),ref)
        for sgn in [-1,1]:box(f'HAAS_R4_West_{floor}Jamb_{i}_{sgn}',(westx-.12,y+sgn*(w/2+.07),z),(.20,.14,h+.18),stone,ref)
        box(f'HAAS_R4_West_{floor}Head_{i}',(westx-.12,y,z+h/2+.07),(.20,w+.28,.14),stone,ref)
        box(f'HAAS_R4_West_{floor}Sill_{i}',(westx-.12,y,z-h/2-.07),(.23,w+.32,.16),stone,ref)
# Put the unverified cupola/spire in the hidden reference archive; Purdue's accessible period and current sources do not verify its form.
archive=bpy.data.collections.get('Reference_Incompatible_Geometry_felix_haas_hall')
if not archive:
    archive=bpy.data.collections.new('Reference_Incompatible_Geometry_felix_haas_hall'); bpy.context.scene.collection.children.link(archive)
for n in ['HAAS_Cupola_Base','HAAS_Cupola_Drum','HAAS_Cupola_Dome','HAAS_Cupola_Spire']:
    o=bpy.data.objects.get(n)
    if o:
        for c in list(o.users_collection):c.objects.unlink(o)
        archive.objects.link(o);o['verification']='Removed from export: no reliable overhead/archival image verified this roof ornament. Shape/height remain uncertain.'
archive.hide_render=True;archive.hide_viewport=True
C['interior_scope']='Only the published nondimensional first-floor diagram was modeled. Room dimensions and registration, doors, wall heights and furniture are estimates; no measured interior survey was verified.'
C['roof_ornament_status']='No overhead/archival source verified the modeled cupola/spire; those objects are excluded from export and retained in a hidden reference archive.'
bpy.ops.wm.save_as_mainfile(filepath=P)
Path('audit/batch3_haas/round4_changes.json').write_text(json.dumps({'source':ref,'side_bays':'Five upper/lower near-side bays moved inside GIS wall; corresponding far-side bays mirrored as estimates; detached former outer bays corrected.','facades':'Repeated limestone bands and piers on both long elevations; matching piers and estimated window rhythm on west end. Entrance elevation retained.','materials':'Brick and limestone retuned; procedural tile scale tightened to 0.34 m by 0.17 m and color contrast increased for full-roof readability.','ornament':'Cupola, drum, dome and spire moved out of export to hidden archive because no verified overhead/archival source supports them.','interior':'Nondimensioned plan; dimensions/registration are estimates, explicitly recorded on collection.','GIS':'Footprint shell, origin, unit scale and main roof transforms untouched.'},indent=2))
