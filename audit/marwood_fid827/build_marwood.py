import bpy, bmesh, json, math, hashlib
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
AUD=ROOT/'audit/marwood_fid827'
SRC=AUD/'sources'
ASSET=ROOT/'modular/buildings/massing_marwood_cooperative_fid827.blend'
GIS=SRC/'purdue_gis_fid827_2026-10-28_4326.json'

feat=json.loads(GIS.read_text(encoding='utf-8'))['features'][0]
ring_ll=feat['geometry']['rings'][0][:-1]
ring_xy=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in ring_ll]
# Orient the local long axis to the longest straight GIS edge. This is a modeling frame, not a measured facade bearing.
edges=[(math.hypot(ring_xy[(i+1)%len(ring_xy)][0]-ring_xy[i][0],ring_xy[(i+1)%len(ring_xy)][1]-ring_xy[i][1]),i) for i in range(len(ring_xy))]
edge_len,edge_i=max(edges)
ux0,uy0=ring_xy[edge_i]; ux1,uy1=ring_xy[(edge_i+1)%len(ring_xy)]
ux=(ux1-ux0)/edge_len; uy=(uy1-uy0)/edge_len
vx=-uy; vy=ux
cx=sum(x for x,y in ring_xy)/len(ring_xy); cy=sum(y for x,y in ring_xy)/len(ring_xy)
ring=[((x-cx)*ux+(y-cy)*uy,(x-cx)*vx+(y-cy)*vy) for x,y in ring_xy]
u_min=min(u for u,v in ring); u_max=max(u for u,v in ring); v_min=min(v for u,v in ring); v_max=max(v for u,v in ring)
uc=(u_min+u_max)/2; vc=(v_min+v_max)/2; theta=math.atan2(uy,ux)

if ASSET.exists():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene=bpy.context.scene
else:
    scene=bpy.context.scene
    scene.name='Building_massing_marwood_cooperative_fid827'
col=bpy.data.collections.get('Asset_massing_marwood_cooperative_fid827')
if col is None:
    col=bpy.data.collections.new('Asset_massing_marwood_cooperative_fid827'); scene.collection.children.link(col)
# Remove Blender factory-startup objects and collections; this standalone library must export only the named asset collection.
for ob in list(scene.objects):
    if ob.name not in col.objects: bpy.data.objects.remove(ob,do_unlink=True)
for other in list(scene.collection.children):
    if other!=col and len(other.objects)==0 and not other.children:
        bpy.data.collections.remove(other)
for ob in list(col.objects): bpy.data.objects.remove(ob,do_unlink=True)

def xyz(u,v,z): return (cx+u*ux+v*vx,cy+u*uy+v*vy,z)

def mat(name,color,rough=.78,metal=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); p=nt.nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    nt.links.new(p.outputs['BSDF'],out.inputs['Surface'])
    return m

stucco=mat('Marwood_Warm_Cream_Stucco',(0.85,0.78,0.67))
brick=mat('Marwood_Dark_Red_Brown_Brick',(0.20,0.065,0.035))
timber=mat('Marwood_Dark_Brown_Tudor_Timber',(0.11,0.038,0.018))
roofmat=mat('Marwood_Warm_Brown_Shingle_Roof',(0.24,0.15,0.10))
trim=mat('Marwood_Cream_Window_Trim',(0.88,0.80,0.66))
glass=mat('Marwood_Deep_Blue_Grey_Glass',(0.045,0.10,0.12),.25)
door=mat('Marwood_Dark_Wood_Entry',(0.14,0.045,0.02))
signmat=mat('Marwood_Sign_Brown',(0.25,0.09,0.03))
stone=mat('Marwood_Light_Stone',(0.53,0.48,0.39))
floor=mat('Marwood_Interior_Floor_Schematic',(0.82,0.75,0.64))
partition=mat('Marwood_Interior_Partition_Schematic',(0.31,0.24,0.18))
furnish=mat('Marwood_Interior_Furniture_Schematic',(0.19,0.29,0.38))
created=[]

def mesh_local(name,verts,faces,material):
    wverts=[xyz(*v) for v in verts]
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(wverts,[],faces); me.materials.append(material); me.validate(verbose=False); me.update()
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); created.append(ob); return ob

def cube_local(name,u,v,z,su,sv,sz,material,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(u,v,z))
    ob=bpy.context.object; ob.name=name; ob.rotation_euler.z=theta; ob.dimensions=(su,sv,sz)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    col.objects.link(ob); ob.data.materials.append(material)
    if bevel:
        mod=ob.modifiers.new('Soft_Edges','BEVEL'); mod.width=bevel; mod.segments=2
        bpy.context.view_layer.objects.active=ob; bpy.ops.object.modifier_apply(modifier=mod.name)
    created.append(ob); return ob

def box_between(name,a,b,thick,depth,material,normal_local_v=1):
    # A rectangular bar between local (u,v,z) endpoints, with its broad side in the facade plane.
    p1=Vector(xyz(*a)); p2=Vector(xyz(*b)); x=(p2-p1).normalized()
    # facade normal points toward the photo/presentation side (negative local v)
    z=Vector(((-1 if normal_local_v<0 else 1)*vx,(-1 if normal_local_v<0 else 1)*vy,0)).normalized()
    y=z.cross(x).normalized(); center=(p1+p2)*0.5
    hx=(p2-p1).length/2; hy=depth/2; hz=thick/2
    basis=[x,y,z]
    verts=[]
    for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
        q=center+sx*hx*x+sy*hy*y+sz*hz*z; verts.append(tuple(q))
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); created.append(ob); return ob

def extruded_outline(name,z0,z1,material):
    n=len(ring); verts=[(u,v,z) for u,v in ring for z in (z0,z1)]
    faces=[tuple(range(n)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh_local(name,verts,faces,material)

def roof_slope(name,upper,material,thickness=.16):
    # upper is four local points describing a sloped roof quad; add a thin lower skin and closed perimeter.
    lower=[(u,v,z-thickness) for u,v,z in upper]; verts=upper+lower
    faces=[(0,1,2,3),(7,6,5,4)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
    return mesh_local(name,verts,faces,material)

# GIS perimeter is the lower wall ring; all upper form, facade and roof heights are estimates.
foundation_h=.78; wall_h=3.70; roof_eave=3.85; roof_ridge=7.35
extruded_outline('Foundation_Red_Brick',0,foundation_h,brick)
extruded_outline('Main_Cream_Stucco_Walls',foundation_h,wall_h,stucco)

# Broad main gabled roof. The projection covers the stepped footprint as a single illustrative roof mass.
u0=u_min-.45; u1=u_max+.45; v0=v_min-.35; v1=v_max+.35; vr=(v0+v1)/2
roof_slope('Main_Roof_Front_Slope',[(u0,v0,roof_eave),(u1,v0,roof_eave),(u1,vr,roof_ridge),(u0,vr,roof_ridge)],roofmat)
roof_slope('Main_Roof_Back_Slope',[(u0,vr,roof_ridge),(u1,vr,roof_ridge),(u1,v1,roof_eave),(u0,v1,roof_eave)],roofmat)
# Gable infills at both ends of the main roof.
for u,tag in [(u0,'West'),(u1,'East')]:
    mesh_local('Main_Gable_Infill_'+tag,[(u,v0,wall_h),(u,v1,wall_h),(u,vr,roof_ridge-.12)],[(0,1,2)],stucco)
# Dark fascia and ridge seam visually articulate the roof edge.
cube_local('Front_Eave_Fascia',uc,v0,roof_eave-.06,u1-u0,.18,.25,timber,.025)
cube_local('Rear_Eave_Fascia',uc,v1,roof_eave-.06,u1-u0,.18,.25,timber,.025)
cube_local('Ridge_Cap',uc,vr,roof_ridge+.03,u1-u0,.13,.12,roofmat,.025)

# Raised central front gable echoing the prominent Marwood entry photo.
g_u0=1.6; g_u1=8.8; g_uc=(g_u0+g_u1)/2; g_front=v_min-.38; g_back=1.3; g_base=wall_h-.06; g_peak=7.15
mesh_local('Central_Gable_Front_Infill',[(g_u0,g_front,g_base),(g_u1,g_front,g_base),(g_uc,g_front,g_peak)],[(0,1,2)],stucco)
roof_slope('Central_Gable_Left_Roof',[(g_u0,g_front,g_base),(g_uc,g_front,g_peak),(g_uc,g_back,g_peak),(g_u0,g_back,g_base)],roofmat)
roof_slope('Central_Gable_Right_Roof',[(g_uc,g_front,g_peak),(g_u1,g_front,g_base),(g_u1,g_back,g_base),(g_uc,g_back,g_peak)],roofmat)
# Heavy dark Tudor trim around the gable and paired decorative braces.
box_between('Gable_Rake_Left',(g_u0,g_front,g_base),(g_uc,g_front,g_peak),.28,.27,timber,-1)
box_between('Gable_Rake_Right',(g_uc,g_front,g_peak),(g_u1,g_front,g_base),.28,.27,timber,-1)
cube_local('Gable_Base_Beam',g_uc,g_front-.04,g_base,g_u1-g_u0,.30,.26,timber,.025)
box_between('Gable_Center_Post',(g_uc,g_front-.12,g_base+.10),(g_uc,g_front-.12,g_peak-.16),.19,.20,timber,-1)
for side in (-1,1):
    box_between('Gable_Brace_'+str(side),(g_uc+side*.12,g_front-.13,g_base+.30),(g_uc+side*2.3,g_front-.13,g_base+1.78),.15,.18,timber,-1)

# Main facade timber bands and restrained vertical posts; the orientation remains illustrative.
front_segments=[(2.49,8.41,-4.4),(8.23,17.72,-2.8),(-5.39,2.10,-.84),(-10.54,-5.40,-3.85)]
for seg,(a,b,vf) in enumerate(front_segments):
    cube_local('Facade_Timber_Belt_Lower_%d'%seg,(a+b)/2,vf-.035,1.12,b-a,.20,.22,timber,.025)
    cube_local('Facade_Timber_Eave_Band_%d'%seg,(a+b)/2,vf-.04,3.35,b-a,.22,.27,timber,.025)
    for x in (a+.15,(a+b)/2,b-.15):
        cube_local('Facade_Timber_Post_%d_%.2f'%(seg,x),x,vf-.035,2.22,.18,.20,2.25,timber,.018)

# Multi-pane front windows and shutterless dark brown Tudor surrounds, placed on the known stepped facade edges.
def front_window(name,u,v,z,w=1.55,h=1.72,frame=timber):
    # Camera-facing side is lower local v.
    cube_local(name+'_Glazing',u,v-.13,z,w,.08,h,glass,.02)
    for du in (-w/2-.07,w/2+.07): cube_local(name+'_Jamb',u+du,v-.20,z,.14,.15,h+.24,frame,.015)
    for dz in (-h/2-.07,h/2+.07): cube_local(name+'_Rail',u,v-.20,z+dz,w+.28,.15,.14,frame,.015)
    cube_local(name+'_MullionV',u,v-.24,z,.07,.08,h,trim,.01)
    cube_local(name+'_MullionH',u,v-.24,z,w,.08,.07,trim,.01)
    cube_local(name+'_StoneSill',u,v-.26,z-h/2-.17,w+.36,.22,.11,stone,.015)

front_window('LeftWing_Window',-7.95,-3.85,2.05,1.36,1.64)
front_window('MainFront_Window_A',-3.55,-.84,2.05,1.45,1.72)
front_window('MainFront_Window_B',-.35,-.84,2.05,1.45,1.72)
front_window('Gable_Front_Large_Window',5.35,-4.42,2.16,2.10,1.80)
front_window('RightWing_Window',14.0,-2.82,2.08,1.52,1.72)
# Small lower-level foundation windows present in the source photograph.
for i,(u,vf) in enumerate([(-8.0,-3.85),(-2.4,-.84),(3.8,-4.4),(12.8,-2.82)]):
    cube_local('Basement_Window_%d'%i,u,vf-.12,.36,.76,.08,.32,glass,.01)
    for dz in (-.21,.21): cube_local('Basement_Frame_H_%d'%i,u,vf-.18,.36+dz,.92,.10,.07,stone,.01)

# Upper gable window, paired trim and slat details.
front_window('Attic_Gable_Window',g_uc,g_front,5.74,1.45,1.44,trim)

# Marwood lettering on the gable below its attic window.
cube_local('Marwood_Name_Backdrop',g_uc,g_front-.35,4.57,3.55,.09,.50,stucco,.01)
font=bpy.data.curves.new('Marwood_Name_Text','FONT'); font.body='MARWOOD'; font.size=.39; font.align_x='CENTER'; font.extrude=.006
textob=bpy.data.objects.new('Marwood_Name_Text',font); col.objects.link(textob)
normal=Vector((-vx,-vy,0)); basis=Matrix((Vector((ux,uy,0)),Vector((0,0,1)),normal)).transposed()
textob.location=xyz(g_uc,g_front-.43,4.45); textob.rotation_mode='QUATERNION'; textob.rotation_quaternion=basis.to_quaternion(); textob.data.materials.append(signmat); created.append(textob)
bpy.ops.object.select_all(action='DESELECT'); textob.select_set(True); bpy.context.view_layer.objects.active=textob; bpy.ops.object.convert(target='MESH'); textob=bpy.context.view_layer.objects.active; textob.name='Marwood_Name_Text_Mesh'; textob.select_set(False)

# Entry is to the right of the projecting gable in the official image.
entry_u=9.9; entry_v=-3.05
cube_local('Main_Entry_Door',entry_u,entry_v-.12,1.92,1.35,.20,2.38,door,.04)
for du in (-.85,.85): cube_local('Entry_Sidelight_'+str(du),entry_u+du,entry_v-.22,1.98,.24,.08,2.10,glass,.02)
cube_local('Entry_Transom',entry_u,entry_v-.23,3.20,2.05,.10,.35,glass,.015)
# Simple covered entry roof and columns.
porch_v=entry_v-1.45
cube_local('Entry_Canopy',(entry_u+entry_u)/2,porch_v,3.48,4.25,2.25,.28,timber,.035)
for du in (-1.82,1.82):
    cube_local('Entry_Post_'+str(du),entry_u+du,porch_v,1.92,.24,.24,3.05,timber,.025)
cube_local('Entry_Stone_Landing',entry_u,entry_v-1.8,.82,4.3,3.1,.30,stone,.04)
for i in range(4): cube_local('Entry_Step_%d'%i,entry_u,entry_v-3.2-i*.52,.67-i*.11,3.7-i*.3,.55,.20,stone,.025)
for du in (-1.78,1.78):
    cube_local('Entry_Rail_Post_'+str(du),entry_u+du,entry_v-3.0,1.28,.10,.10,1.2,timber,.012)
    cube_local('Entry_Rail_'+str(du),entry_u+du,entry_v-4.0,1.55,.10,2.2,.10,timber,.012)

# Brick chimney rising from the rear roof field, visible in the official photograph.
cube_local('Brick_Chimney',10.3,vc,8.0,1.2,1.1,2.1,brick,.04)
cube_local('Chimney_Cap',10.3,vc,9.12,1.55,1.4,.22,timber,.025)

# Schematic ground-floor interior. Room layout/furnishings are placeholders, not as-built.
mesh_local('Schematic_Ground_Floor',[(u,v,.18) for u,v in ring],[tuple(range(len(ring)))],floor)
def divider(name,a,b,z=1.55,h=2.65):
    (u1,v1),(u2,v2)=a,b; length=math.hypot(u2-u1,v2-v1)
    midu=(u1+u2)/2; midv=(v1+v2)/2
    # Partition boxes stay aligned to the house axes; all are approximate.
    if abs(v2-v1)<.25: cube_local(name,midu,midv,z,length,.14,h,partition,.01)
    else: cube_local(name,midu,midv,z,.14,length,h,partition,.01)

# Draw only generic separations and circulation; no sourced room labels or dimensions.
for i,(a,b) in enumerate([
    ((-8.6,-.2),(-8.6,7.0)),((-3.2,-.7),(-3.2,9.0)),((2.0,1.3),(2.0,9.0)),((8.7,1.4),(8.7,9.4)),((13.5,2.5),(13.5,9.5)),
    ((-10.5,3.2),(-3.3,3.2)),((-3.1,4.8),(2.1,4.8)),((2.2,2.2),(8.7,2.2)),((8.9,5.5),(15.5,5.5))]): divider('Schematic_Partition_%02d'%i,a,b)
# Generic tables, bed-like rectangles, counters and compact stair placeholder.
for name,u,v,z,su,sv,sz,material in [
    ('Common_Table',-5.8,1.3,.72,2.2,1.0,.16,stone),('Dining_Table',5.0,5.2,.72,2.8,1.25,.16,stone),
    ('Furniture_Block_A',-6.5,6.2,.55,1.8,.85,.30,furnish),('Furniture_Block_B',11.2,7.3,.55,1.8,.85,.30,furnish),
    ('Counter',-10.2,6.1,.7,.55,3.8,.85,partition)]: cube_local('Schematic_'+name,u,v,z,su,sv,sz,material,.025)
for i in range(8): cube_local('Schematic_Stair_Tread_%02d'%i,4.8,-2.8+i*.42,.32+i*.16,1.8,.42,.11,trim,.01)

# Join all architectural geometry into the single named massing root.
bpy.ops.object.select_all(action='DESELECT')
for ob in list(col.objects):
    if ob.type!='MESH': raise RuntimeError('Non-mesh geometry before merge: '+ob.name)
    ob.select_set(True)
bpy.context.view_layer.objects.active=next(iter(col.objects)); bpy.ops.object.join()
root=bpy.context.object; root.name='House_Marwood_Cooperative'; root.data.name='Marwood_FID827_GIS_Shell_Illustrative_Details'; root.select_set(False)
root['building_id']='massing_marwood_cooperative_fid827'
root['identity']='Purdue GIS FID 827 / Marwood / 136 Littleton St'
root['interior_representation']='Schematic only; no as-built floor plan or interior photograph found.'
root['height_status']='Estimated. GIS NUM_LEVELS=1 and Extrution=12 are not treated as measured height.'
root['orientation_status']='Model presentation facade bearing is illustrative; no source camera bearing was recovered.'

# Preview render setup is temporary and removed before saving the asset.
rcol=bpy.data.collections.new('Temporary_Render_Setup'); scene.collection.children.link(rcol)
def aim(ob,target): ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
def camera(name,loc,target,scale):
    d=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,d); rcol.objects.link(o); o.location=loc; d.type='ORTHO'; d.ortho_scale=scale; aim(o,target); scene.camera=o; return o
def light(name,loc,power,size,target):
    d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size; o=bpy.data.objects.new(name,d); rcol.objects.link(o); o.location=loc; aim(o,target)
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=80
scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'; scene.view_settings.view_transform='AgX'
world=scene.world or bpy.data.worlds.new('Marwood_Studio_World'); world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(.48,.51,.55,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.82
target=xyz(uc,vc,4.0); light('Marwood_Key',xyz(uc-20,v_min-18,28),7500,28,target); light('Marwood_Fill',xyz(uc+22,v_min-5,20),3800,24,target); light('Marwood_Rim',xyz(uc,v_max+10,24),2600,20,target)
scene.camera=camera('Marwood_Exterior_Camera',xyz(uc+7,v_min-39,12),target,43)
scene.render.filepath=str(AUD/'exterior_preview.png'); bpy.ops.render.render(write_still=True)
scene.camera=camera('Marwood_Roof_Oblique_Camera',xyz(uc-20,v_min-34,27),target,49)
scene.render.filepath=str(AUD/'roof_oblique_preview.png'); bpy.ops.render.render(write_still=True)
scene.camera=camera('Marwood_Top_Camera',xyz(uc,vc,86),xyz(uc,vc,0),48)
scene.render.filepath=str(AUD/'top_preview.png'); bpy.ops.render.render(write_still=True)
# Interior-only cutaway render from a temporary filtered copy.
cut=root.copy(); cut.data=root.data.copy(); cut.name='Temporary_Interior_Cutaway'; rcol.objects.link(cut)
interior_markers=('Marwood_Interior_Floor_Schematic','Marwood_Interior_Partition_Schematic','Marwood_Interior_Furniture_Schematic')
keep={i for i,m in enumerate(cut.data.materials) if m and any(q in m.name for q in interior_markers)}
bm=bmesh.new(); bm.from_mesh(cut.data); bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index not in keep],context='FACES'); bm.to_mesh(cut.data); bm.free(); cut.data.update()
root.hide_render=True
scene.camera=camera('Marwood_Interior_Schematic_Camera',xyz(uc,vc,80),xyz(uc,vc,0.4),56)
scene.render.filepath=str(AUD/'schematic_interior_cutaway.png'); bpy.ops.render.render(write_still=True)
root.hide_render=False
for ob in list(rcol.objects): bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.collections.remove(rcol); scene.camera=None; scene.render.filepath='//'
for im in list(bpy.data.images):
    if im.users==0: bpy.data.images.remove(im)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('SAVED',ASSET,'OBJECTS',len(col.objects),'RING_VERTICES',len(ring),'LOCAL_BOUNDS',u_min,u_max,v_min,v_max,'HEIGHT',roof_ridge)
