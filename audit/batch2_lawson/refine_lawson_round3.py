import bpy, math, json, os
from mathutils import Vector, Matrix

ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET=ROOT+r'/modular/buildings/lawson_hall.blend'
OUT=ROOT+r'/audit/batch2_lawson'
bpy.ops.wm.open_mainfile(filepath=ASSET)
asset=bpy.data.collections['Asset_lawson_hall']
root=bpy.data.objects['AssetRoot_lawson_hall']

# Rerunnable source-only pass.
for o in list(bpy.data.objects):
    if o.name.startswith('LWSN_R3_'): bpy.data.objects.remove(o,do_unlink=True)

def setmat(name,color,rough=.5,metal=0,transmission=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=color; m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=color
    bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metal
    if 'Transmission Weight' in bs.inputs: bs.inputs['Transmission Weight'].default_value=transmission
    if 'Alpha' in bs.inputs: bs.inputs['Alpha'].default_value=1.0
    if 'Specular IOR Level' in bs.inputs: bs.inputs['Specular IOR Level'].default_value=.5
    if hasattr(m,'blend_method'): m.blend_method='OPAQUE'
    if hasattr(m,'surface_render_method'): m.surface_render_method='DITHERED'
    return m

# The saved mesh is intentionally reflective but should read as dark neutral
# curtain glass rather than a transparent green wall. Purdue photos show blue-
# gray/bronze reflections; no interior visibility is inferred from exterior glass.
glass=setmat('LWSN_Curtain_Glass',(.055,.085,.115,1),.19,.16,.08)
rotglass=setmat('LWSN_Rotunda_Glass',(.055,.085,.115,1),.19,.16,.08)
spandrel=setmat('LWSN_Spandrel_Glass',(.13,.17,.19,1),.31,.12,0)
bronze=bpy.data.materials['LWSN_Dark_Aluminum_Bronze']
limestone=bpy.data.materials['LWSN_Bedford_Limestone']
brick=bpy.data.materials['LWSN_Purdue_Red_Brick']
door_glass=glass
wood=setmat('LWSN_R3_Interior_Door_Wood',(.22,.14,.085,1),.72,0,0)
steel=setmat('LWSN_R3_Entrance_Railing_Steel',(.16,.18,.19,1),.35,.72,0)
signmat=setmat('LWSN_R3_Entrance_Sign_Bronze',(.08,.105,.12,1),.34,.55,0)

# The inherited brick material's final noise ramp was grayscale, so the model
# rendered pale instead of Purdue's documented red-brown brick. Restore the
# procedural brick color pattern on the facade's existing direction-correct UVs.
brick_nt=brick.node_tree; brick_bs=brick_nt.nodes.get('Principled BSDF')
brick_tex=brick_nt.nodes.get('Brick Texture')
brick_tex.inputs['Color1'].default_value=(.40,.115,.055,1)
brick_tex.inputs['Color2'].default_value=(.29,.065,.032,1)
brick_tex.inputs['Mortar'].default_value=(.55,.48,.39,1)
brick_tex.inputs['Scale'].default_value=1.0
brick_tex.inputs['Brick Width'].default_value=.203
brick_tex.inputs['Row Height'].default_value=.067
brick_tex.inputs['Mortar Size'].default_value=.008
brick_tex.inputs['Mortar Smooth'].default_value=.1
for link in list(brick_nt.links):
    if link.to_node==brick_bs and link.to_socket==brick_bs.inputs['Base Color']:
        brick_nt.links.remove(link)
brick_nt.links.new(brick_tex.outputs['Color'],brick_bs.inputs['Base Color'])
brick_bs.inputs['Roughness'].default_value=.68

def new_obj(name,mesh):
    ob=bpy.data.objects.new(name,mesh); asset.objects.link(ob)
    ob.parent=root; ob.matrix_parent_inverse=Matrix.Identity(4); ob.location=(0,0,0)
    return ob

def cube(name,center,dims,mat,rotation=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    ob=bpy.context.object; ob.name='LWSN_R3_'+name; ob.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    asset.objects.link(ob); ob.parent=root; ob.matrix_parent_inverse=Matrix.Identity(4)
    ob.rotation_euler.z=rotation
    if mat: ob.data.materials.append(mat)
    ob['evidence']='Added from documented Lawson first-floor plan and current/historic Purdue Computer Science exterior photographs; dimensions not measured unless stated.'
    return ob

# Principal south entry from the north-up Lawson first-floor plan. The source
# drawing places the main public vestibule at the south end; Google/Purdue images
# support a curved pale-stone canopy, glazed double doors and broad stair/rails.
cx=.9; wall_y=-42.60; canopy_depth=2.15; half_width=4.4; top_z=4.0; thick=.38
outline=[(cx-half_width,wall_y),(cx+half_width,wall_y)]
for k in range(1,25):
    t=math.pi*k/24
    outline.append((cx+half_width*math.cos(t),wall_y-canopy_depth*math.sin(t)))
verts=[(x,y,top_z-thick/2) for x,y in outline]+[(x,y,top_z+thick/2) for x,y in outline]
n=len(outline); faces=[tuple(range(n,2*n)),tuple(reversed(range(n)))]
for i in range(n): faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
me=bpy.data.meshes.new('Lawson south entry curved canopy r3 mesh'); me.from_pydata(verts,[],faces); me.materials.append(limestone); me.update()
canopy=new_obj('LWSN_R3_Curved_Limestone_Main_Entry_Canopy',me)
canopy['evidence']='Plan locates south public entrance; curved canopy and stone finish are visible in Purdue/CS exterior photos. Curvature and dimensions are illustrative.'

# Continuous glass vestibule face with paired doors, sidelights, bronze frames,
# transom, and source-visible building identification text.
front_y=wall_y-.08; door_base=.82; door_h=2.55; door_center_z=door_base+door_h/2
cube('Entry_Vestibule_Glazed_Face',(cx,front_y,door_center_z),(7.8,.10,door_h),door_glass)
for x in (cx-3.9,cx-2.25,cx,cx+2.25,cx+3.9):
    cube('Entry_Bronze_Jamb',(x,front_y-.10,door_center_z),(.10,.14,door_h+.10),bronze)
cube('Entry_Bronze_Transom',(cx,front_y-.10,door_base+door_h),(7.9,.14,.12),bronze)
cube('Entry_Bronze_Sill',(cx,front_y-.10,door_base),(7.9,.14,.09),limestone)
for side in (-1,1):
    # paired swing leaves and center meeting stile; four panels remain visibly glazed
    x=cx+side*1.12
    cube('Entry_Double_Door_Leaf',(x,front_y-.16,door_center_z),(2.16,.10,door_h-.12),door_glass)
    cube('Entry_Door_Meeting_Stile',(cx,front_y-.25,door_center_z),(.07,.08,door_h-.08),bronze)
    cube('Entry_Door_Push_Bar',(x-side*.62,front_y-.26,1.72),(.52,.07,.07),bronze)

# Curved stone fascia/sign under the canopy. Text and name are verified in the
# Purdue CS exterior images; no other logo or lettering is invented.
cube('Entry_Sign_Fascia',(cx,wall_y-canopy_depth-.025,3.72),(7.1,.10,.48),limestone)
bpy.ops.object.text_add(location=(cx,wall_y-canopy_depth-.09,3.57),rotation=(math.pi/2,0,0))
txt=bpy.context.object; txt.name='LWSN_R3_Entrance_Sign_Text'; txt.data.body='LAWSON COMPUTER SCIENCE BUILDING'
txt.data.align_x='CENTER'; txt.data.size=.30; txt.data.extrude=.003; txt.data.materials.append(signmat)
for c in list(txt.users_collection):c.objects.unlink(txt)
asset.objects.link(txt);txt.parent=root;txt.matrix_parent_inverse=Matrix.Identity(4)
txt['evidence']='Building name copied from Purdue exterior imagery; lettering size and exact fascia position are illustrative.'

# Three broad approach treads and paired handrails; these are visual estimates
# informed by the entry photograph, not a measured accessibility/stair survey.
for i in range(3):
    z=.70-i*.22; y=-43.15-i*.58
    cube('Entry_Approach_Tread_'+str(i+1),(cx,y,z),(9.2,1.05,.24),limestone)
for side in (-1,1):
    x=cx+side*4.25
    cube('Entry_Handrail_Main',(x,-44.18,.82),(.09,3.2,.09),steel,rotation=side*.035)
    for j in range(4):
        cube('Entry_Handrail_Post',(x,-43.1-j*.73,.47),(.09,.09,.84),steel)

# Add door leaves only where pairs of traced first-floor partition segments form
# a small, plan-scale opening. Larger corridor gaps stay open. All locations are
# derived from the saved partition centerlines, not guessed room placements.
infos=[]
for ob in asset.objects:
    if not ob.name.startswith('LWSN_Plan_Partition') or ob.type!='MESH': continue
    axis=ob.matrix_world.to_3x3() @ Vector((1,0,0)); center=ob.matrix_world.translation
    local_x=[v.co.x for v in ob.data.vertices]
    length=max(local_x)-min(local_x)
    if abs(axis.x)>.9:
        infos.append(('H',round(center.y,1),center.x-length/2,center.x+length/2,center.y))
    elif abs(axis.y)>.9:
        infos.append(('V',round(center.x,1),center.y-length/2,center.y+length/2,center.x))
groups={}
for info in infos:groups.setdefault((info[0],info[1]),[]).append(info)
door_count=0
for (orientation,line),group in groups.items():
    group.sort(key=lambda q:q[2])
    for a,b in zip(group,group[1:]):
        gap=b[2]-a[3]
        if not .82<=gap<=1.48: continue
        start=a[3]; width=min(.92,gap-.08); angle=(math.pi/4 if door_count%2==0 else -math.pi/4)
        if orientation=='H':
            theta=angle; hinge=Vector((start,line,.82))
        else:
            theta=math.pi/2+angle; hinge=Vector((line,start,.82))
        leaf_center=hinge+Vector((math.cos(theta),math.sin(theta),0))*width/2+Vector((0,0,1.04))
        cube('Plan_Door_Leaf_'+str(door_count+1),tuple(leaf_center),(width,.065,2.08),wood,rotation=theta)
        door_count+=1

# Provide missing landings and side rails at the three already traced stair runs.
# The stair run geometry stays in place; landing extents/guard details are visual
# circulation cues, not structural or accessibility certification.
stairs=[o for o in asset.objects if o.name.startswith('LWSN_Stair_Flight') and o.type=='MESH']
stair_groups={}
for ob in stairs:
    c=ob.matrix_world @ Vector((0,0,0)); stair_groups.setdefault(round(c.x),[]).append((c,ob))
for idx,(key,items) in enumerate(sorted(stair_groups.items())):
    items.sort(key=lambda q:q[0].z); low=items[0][0]; high=items[-1][0]
    x=sum(i[0].x for i in items)/len(items)
    low_y=max(i[0].y for i in items); high_y=min(i[0].y for i in items)
    cube('Stair_Landing_Lower_'+str(idx+1),(x,low_y+.95,.78),(3.0,1.6,.18),limestone)
    cube('Stair_Landing_Upper_'+str(idx+1),(x,high_y-.95,3.98),(3.0,1.6,.18),limestone)
    for side in (-1,1):
        px=x+side*1.32
        mid_y=(low_y+high_y)/2; mid_z=(low.z+high.z)/2+1.0
        dy=high_y-low_y; dz=high.z-low.z
        rail=cube('Stair_Steel_Rail_'+str(idx+1),(px,mid_y,mid_z),(.065,math.hypot(dy,dz),.065),steel)
        rail.rotation_euler.x=math.atan2(dz,dy)

# Save source library, then explicitly reopen it before generating the review views.
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.wm.open_mainfile(filepath=ASSET)
asset=bpy.data.collections['Asset_lawson_hall']
root=bpy.data.objects['AssetRoot_lawson_hall']

# Preview rig is temporary; it is not saved into the modular source.
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.render.resolution_x=1400; scene.render.resolution_y=950; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.view_settings.view_transform='AgX'
scene.world.color=(.18,.18,.18)
def aim_camera(name,loc,target,ortho):
    bpy.ops.object.camera_add(location=loc); c=bpy.context.object; c.name='LWSN_R3_TEMP_'+name
    c.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=ortho
    scene.camera=c;return c
def area(name,loc,power,size,target):
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='LWSN_R3_TEMP_'+name;o.data.energy=power;o.data.shape='DISK';o.data.size=size
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
area('Exterior_Softbox',(15,-50,46),4200,35,(0,0,5))
area('Exterior_Fill',(-42,-32,22),1700,28,(0,-5,6))
bpy.ops.object.light_add(type='SUN',location=(0,0,30));sun=bpy.context.object;sun.name='LWSN_R3_TEMP_Sun';sun.data.energy=.9;sun.rotation_euler=(.42,-.35,-.55)
aim_camera('Exterior_Camera',(44,-78,32),(0,-1,6),106)
scene.render.filepath=OUT+r'/exterior_round3.png';bpy.ops.render.render(write_still=True)
aim_camera('Entry_Close_Camera',(18,-61,12),(1,-43.5,2.2),24)
scene.render.filepath=OUT+r'/entry_close_round3.png';bpy.ops.render.render(write_still=True)

# First-floor cutaway: hide only envelope/exterior objects during render, leaving
# the traced first-floor partitions, furniture, doors and stair/landing detail.
hidden=[]
for ob in asset.all_objects:
    if ob is None: continue
    if ob.name in {'LWSN_Exterior_Brick','LWSN_Limestone_Bands','LWSN_Window_Glazing','LWSN_Window_Frames','LWSN_Rotunda_Curtain_Glass','LWSN_Rotunda_Spandrel_Panels','LWSN_Rotunda_Mullions','LWSN_Rotunda_Parapet_Coping','LWSN_Roof_Surface','LWSN_Mechanical_Penthouse','LWSN_Rooftop_Mechanical_Units'}:
        hidden.append((ob,ob.hide_render));ob.hide_render=True
aim_camera('First_Floor_Cutaway',(36,-42,64),(0,0,1.0),94)
scene.render.resolution_x=1200;scene.render.resolution_y=1200
scene.render.filepath=OUT+r'/interior_cutaway_round3.png';bpy.ops.render.render(write_still=True)
for ob,v in hidden:ob.hide_render=v
bpy.ops.wm.open_mainfile(filepath=ASSET)

print(json.dumps({'saved_reopened':True,'asset':'modular/buildings/lawson_hall.blend','new_plan_door_leaves':door_count,
 'stair_flight_groups':len(stair_groups),'export_collection_objects':len(list(bpy.data.collections['Asset_lawson_hall'].all_objects)),
 'previews':['audit/batch2_lawson/exterior_round3.png','audit/batch2_lawson/entry_close_round3.png','audit/batch2_lawson/interior_cutaway_round3.png']},indent=2))
