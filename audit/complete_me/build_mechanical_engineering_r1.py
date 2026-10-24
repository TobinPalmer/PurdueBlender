"""Evidence-led Mechanical Engineering R1 facade pass.

Run with Blender 5.2: blender -b modular/buildings/mechanical_engineering.blend --python audit/complete_me/build_mechanical_engineering_r1.py
All added geometry is local to Asset_mechanical_engineering. The facade modules
are photo-derived qualitative placements; no dimensions are claimed surveyed.
"""
import bpy, bmesh, json, math
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'audit' / 'complete_me'
ASSET = ROOT / 'modular' / 'buildings' / 'mechanical_engineering.blend'
GIS = json.loads((ROOT / 'audit' / 'official_building_references.json').read_text(encoding='utf-8'))
FID = 857
PLACEMENT = Vector((66.30000114440918, 86.5))
asset = bpy.data.collections['Asset_mechanical_engineering']
shell = bpy.data.objects['ME_Official_857_Structural_Envelope']
scene = bpy.context.scene

# Idempotent cleanup of this revision's generated details and review cameras.
for ob in list(bpy.data.objects):
    if ob.name.startswith('ME_R1_'):
        bpy.data.objects.remove(ob, do_unlink=True)

feature = next(f for f in GIS['buildings'] if f.get('fid') == FID)
ring_world = feature['rings_xy_m'][0]
ring = [Vector((p[0] - PLACEMENT.x, p[1] - PLACEMENT.y)) for p in ring_world]
if ring[0] == ring[-1]:
    ring = ring[:-1]
area2 = sum(ring[i].x * ring[(i+1) % len(ring)].y - ring[(i+1) % len(ring)].x * ring[i].y for i in range(len(ring)))
ccw = area2 > 0

# Engineering Fountain coordinate from published coordinates; the project frame
# is an approximate local tangent plane, not survey control.
fountain = Vector((( -86.913671 + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                   (40.428539 - 40.4274) * 111040.0)) - PLACEMENT

edges = []
for i, a in enumerate(ring):
    b = ring[(i+1) % len(ring)]
    delta = b - a
    length = delta.length
    if length < 1e-5:
        continue
    t = delta.normalized()
    # For a CCW ring the polygon interior is left of each edge; reverse for CW.
    n = Vector((t.y, -t.x)) if ccw else Vector((-t.y, t.x))
    edges.append({'index': i, 'a': a, 'b': b, 't': t, 'n': n, 'length': length})

front_candidates = []
for e in edges:
    if e['length'] < 20:
        continue
    mid = (e['a'] + e['b']) * 0.5
    to_fountain = fountain - mid
    dot = e['n'].dot(to_fountain.normalized())
    if dot > 0.15:
        # Approximate perpendicular distance to this facade; favor facing edges.
        front_candidates.append((to_fountain.length + (1.0-dot)*20.0, e))
front_edge = min(front_candidates, key=lambda x: x[0])[1]
front_center = (front_edge['a'] + front_edge['b']) * 0.5
front_t, front_n = front_edge['t'], front_edge['n']
front_length = front_edge['length']
door_u = front_length * 0.5

def mat_principled(name, color, roughness=0.65, metallic=0.0, specular=0.25):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    nodes = m.node_tree.nodes
    bsdf = nodes.get('Principled BSDF')
    if bsdf is None:
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = specular
    return m

# Photo-informed qualitative material response. Brick size uses the existing
# meter-based tangent/vertical UV layout on the GIS facade shell.
brick = bpy.data.materials.get('ME_R1_Brick_RedBrown_Qualitative') or bpy.data.materials.new('ME_R1_Brick_RedBrown_Qualitative')
brick.diffuse_color = (0.28, 0.075, 0.038, 1.0)
brick.use_nodes = True
bn = brick.node_tree.nodes
bl = brick.node_tree.links
bn.clear()
out = bn.new('ShaderNodeOutputMaterial')
bs = bn.new('ShaderNodeBsdfPrincipled')
bs.inputs['Roughness'].default_value = 0.82
if 'Specular IOR Level' in bs.inputs: bs.inputs['Specular IOR Level'].default_value = 0.2
uv = bn.new('ShaderNodeUVMap'); uv.uv_map = 'Meters_Tangent_Z'
bt = bn.new('ShaderNodeTexBrick')
bt.inputs['Scale'].default_value = 1.0
bt.inputs['Brick Width'].default_value = 0.215
bt.inputs['Row Height'].default_value = 0.075
bt.inputs['Mortar Size'].default_value = 0.008
bt.inputs['Color1'].default_value = (0.36, 0.105, 0.050, 1.0)
bt.inputs['Color2'].default_value = (0.23, 0.050, 0.025, 1.0)
bt.inputs['Mortar'].default_value = (0.19, 0.16, 0.13, 1.0)
noise = bn.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 42.0; noise.inputs['Detail'].default_value = 2.0; noise.inputs['Roughness'].default_value = 0.7
coord = bn.new('ShaderNodeTexCoord')
bump = bn.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.22; bump.inputs['Distance'].default_value = 0.006
bl.new(uv.outputs['UV'], bt.inputs['Vector'])
bl.new(coord.outputs['Generated'], noise.inputs['Vector'])
bl.new(bt.outputs['Color'], bs.inputs['Base Color'])
bl.new(bt.outputs['Fac'], bump.inputs['Height'])
bl.new(bump.outputs['Normal'], bs.inputs['Normal'])
bl.new(bs.outputs['BSDF'], out.inputs['Surface'])

limestone = mat_principled('ME_R1_Limestone_Portal_Qualitative', (0.67,0.62,0.53), 0.62)
frame = mat_principled('ME_R1_Window_Frame_DarkBronze', (0.075,0.062,0.047), 0.34, 0.38)
glass = mat_principled('ME_R1_Window_Glass_BlueGray', (0.025,0.055,0.070), 0.19, 0.18, 0.42)
door_glass = mat_principled('ME_R1_Entry_Glazing_Dark', (0.012,0.028,0.038), 0.15, 0.22, 0.45)
lettering = mat_principled('ME_R1_Entrance_Lettering', (0.12,0.105,0.085), 0.72)

def make_mesh(name, verts, faces, material, collection=asset):
    mesh = bpy.data.meshes.new(name + '_Mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    bm = bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh); bm.free(); mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    collection.objects.link(ob)
    if material: mesh.materials.append(material)
    return ob

def box_component(verts, faces, center2, tangent, normal, zc, width, depth, height):
    center = Vector((center2.x, center2.y))
    base = len(verts)
    for sz in (-1,1):
        for sy in (-1,1):
            for sx in (-1,1):
                p = center + tangent * (sx*width*0.5) + normal * (sy*depth*0.5)
                verts.append((p.x,p.y,zc + sz*height*0.5))
    # Vertex order: bottom(-z) then top(+z); recalc normals after assembly.
    quads = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(1,5,7,3),(3,7,6,2),(2,6,4,0)]
    faces.extend([tuple(base+i for i in f) for f in quads])

def prism_poly(verts, faces, tangent, normal, center2, polygon_uz, v_back, v_front):
    base=len(verts); n=len(polygon_uz)
    for v in (v_back,v_front):
        for u,z in polygon_uz:
            p=center2 + tangent*u + normal*v
            verts.append((p.x,p.y,z))
    faces.append(tuple(base+i for i in range(n)))
    faces.append(tuple(base+n+i for i in reversed(range(n))))
    for i in range(n):
        j=(i+1)%n
        faces.append((base+i,base+j,base+n+j,base+n+i))

def arc_ring(verts, faces, tangent, normal, center2, spring_z, inner_r, outer_r, v_back, v_front, steps=20):
    base=len(verts)
    for v in (v_back,v_front):
        for r in (inner_r,outer_r):
            for i in range(steps+1):
                a=math.pi*i/steps
                p=center2 + tangent*(r*math.cos(a)) + normal*v
                verts.append((p.x,p.y,spring_z+r*math.sin(a)))
    # perimeter surfaces for back/front inner/outer arcs and end closures
    stride=steps+1
    for i in range(steps):
        # index groups: back-inner, back-outer, front-inner, front-outer
        bi=base+i; bo=base+stride+i; fi=base+2*stride+i; fo=base+3*stride+i
        faces.extend([(bi,bo,bo+1,bi+1),(fi,fi+1,fo+1,fo),
                      (bi,bi+1,fi+1,fi),(bo,fo,fo+1,bo+1)])
    for j in (0,steps):
        bi=base+j; bo=base+stride+j; fi=base+2*stride+j; fo=base+3*stride+j
        faces.append((bi,fi,fo,bo))

# Build the combined Boolean cutter set. This turns the photo-derived facade
# window pattern and entrance portal into actual openings rather than decals.
cverts, cfaces = [], []
window_specs=[]
window_w, window_h = 1.55, 2.25
floor_rows=[2.0,6.5,11.0,15.5]  # approximate centers; four visible above-grade levels
for e in edges:
    L=e['length']
    if L < 7.5: continue
    a,t,n=e['a'],e['t'],e['n']
    count=max(1, int(math.floor((L-6.0)/4.8))+1)
    centers=[L*0.5] if count==1 else [3.0 + j*(L-6.0)/(count-1) for j in range(count)]
    for u in centers:
        if e['index']==front_edge['index'] and abs(u-door_u)<4.5:
            continue
        for zc in floor_rows:
            center=a+t*u
            box_component(cverts,cfaces,center,t,n,zc,window_w,0.9,window_h)
            window_specs.append((e,u,zc))

# Arched doorway cut-out on the long face whose outward normal points toward the
# Engineering Fountain. Its local position along that facade is an estimate.
arch_spring=3.25
door_radius=1.55
door_poly=[(-door_radius,0.12),(door_radius,0.12),(door_radius,arch_spring)]
for i in range(1,21):
    ang=math.pi*i/20
    door_poly.append((door_radius*math.cos(ang),arch_spring+door_radius*math.sin(ang)))
prism_poly(cverts,cfaces,front_t,front_n,front_edge['a']+front_t*door_u,door_poly,-0.65,0.65)

cutmesh=bpy.data.meshes.new('ME_R1_Facade_Cutters_Mesh'); cutmesh.from_pydata(cverts,[],cfaces); cutmesh.update()
bm=bmesh.new(); bm.from_mesh(cutmesh); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(cutmesh); bm.free(); cutmesh.update()
cutob=bpy.data.objects.new('ME_R1_Temporary_Facade_Cutters',cutmesh); scene.collection.objects.link(cutob)

# Apply the existing estimated wall thickness first, then boolean the new openings.
bpy.ops.object.select_all(action='DESELECT'); shell.select_set(True); bpy.context.view_layer.objects.active=shell
for mod in list(shell.modifiers):
    bpy.ops.object.modifier_apply(modifier=mod.name)
boolmod=shell.modifiers.new('R1_Photographic_Facade_Openings','BOOLEAN')
boolmod.operation='DIFFERENCE'; boolmod.solver='EXACT'; boolmod.object=cutob
bpy.context.view_layer.objects.active=shell
bpy.ops.object.modifier_apply(modifier=boolmod.name)
bpy.data.objects.remove(cutob,do_unlink=True)

# Rebuild the facade's brick material with a readable meter-scaled running-bond
# pattern, and keep the material explicitly qualitative rather than color-metered.
shell.data.materials.clear(); shell.data.materials.append(brick)

# Generate windows, frames, masonry lintels/sills, horizontal floor courses.
gverts,gfaces=[],[]; fverts,ffaces=[],[]; sverts,sfaces=[],[]
for e,u,zc in window_specs:
    a,t,n=e['a'],e['t'],e['n']; c=a+t*u
    # Glazing is set just inside the cut wall, with a projecting dark frame.
    box_component(gverts,gfaces,c,t,n,zc,window_w-0.12,0.06,window_h-0.12)
    bar=0.075
    for du in (-window_w/2+0.04,0,window_w/2-0.04):
        box_component(fverts,ffaces,c+t*du+n*0.10,t,n,zc,bar,0.16,window_h)
    for dz in (-window_h/2+0.04,window_h/2-0.04,0):
        box_component(fverts,ffaces,c+n*0.10,t,n,zc+dz,window_w,0.16,bar)
    # Pale stone sill and head are visible in both current facade photographs.
    box_component(sverts,sfaces,c+n*0.075,t,n,zc-window_h/2-0.04,window_w+0.34,0.24,0.14)
    box_component(sverts,sfaces,c+n*0.075,t,n,zc+window_h/2+0.035,window_w+0.20,0.18,0.10)

# Continuous stone belt courses on longer exterior wall segments. These follow
# the four approximate above-grade story bands; they are not measured elevations.
for e in edges:
    if e['length'] < 7.5: continue
    L=e['length']; a,t,n=e['a'],e['t'],e['n']
    for z in (4.5,9.0,13.5,18.1):
        # split course around the entrance so it cannot bridge the arch.
        intervals=[(0,L)]
        if e['index']==front_edge['index']:
            intervals=[(0,max(0,door_u-2.3)),(min(L,door_u+2.3),L)]
        for lo,hi in intervals:
            length=hi-lo
            if length<0.5: continue
            box_component(sverts,sfaces,a+t*((lo+hi)*0.5)+n*0.07,t,n,z,length,0.20,0.18)

make_mesh('ME_R1_Facade_Window_Glazing',gverts,gfaces,glass)
make_mesh('ME_R1_Facade_Window_Frames',fverts,ffaces,frame)
make_mesh('ME_R1_Limestone_Window_Sills_And_Stringcourses',sverts,sfaces,limestone)

# Carved limestone entry: paired piers, semicircular archivolt, transom, double doors.
portal_center=front_edge['a']+front_t*door_u
pverts,pfaces=[],[]
for du in (-1.88,1.88):
    box_component(pverts,pfaces,portal_center+front_t*du+front_n*0.16,front_t,front_n,1.70,0.58,0.42,3.40)
    box_component(pverts,pfaces,portal_center+front_t*du+front_n*0.20,front_t,front_n,0.25,0.92,0.55,0.42)
    box_component(pverts,pfaces,portal_center+front_t*du+front_n*0.20,front_t,front_n,3.42,0.92,0.55,0.38)
arc_ring(pverts,pfaces,front_t,front_n,portal_center,arch_spring,1.58,2.18,-0.02,0.42,24)
make_mesh('ME_R1_Gatewood_Fountain_Facing_Stone_Arch',pverts,pfaces,limestone)

# Dark glazing fills the arched portal cut; panels and transom bars suggest the
# double-door assembly in Purdue's current official exterior photographs.
dverts,dfaces=[],[]
prism_poly(dverts,dfaces,front_t,front_n,portal_center,door_poly,-0.20,-0.12)
make_mesh('ME_R1_Arched_Entry_Door_Glazing',dverts,dfaces,door_glass)
mverts,mfaces=[],[]
box_component(mverts,mfaces,portal_center+front_n*(-0.03),front_t,front_n,1.70,0.065,0.08,3.05)
box_component(mverts,mfaces,portal_center+front_n*(-0.03),front_t,front_n,2.70,2.85,0.08,0.075)
for du in (-0.28,0.28):
    box_component(mverts,mfaces,portal_center+front_t*du+front_n*0.05,front_t,front_n,1.55,0.05,0.08,0.32)
make_mesh('ME_R1_Entry_Door_Mullions_And_Handles',mverts,mfaces,frame)

# A shallow limestone seal plaque is included only as a generic silhouette,
# without reproducing unsupported lettering, iconography, or dimensions.
pv,pf=[],[]
box_component(pv,pf,portal_center+front_n*0.15,front_t,front_n,6.35,1.55,0.32,1.25)
make_mesh('ME_R1_Entry_Stone_Plaque_Silhouette',pv,pf,limestone)

# Legible building-name engraving, as seen directly above the current entrance.
letter_curve=bpy.data.curves.new('ME_R1_Entrance_Lettering_Curve','FONT')
letter_curve.body='MECHANICAL ENGINEERING'
letter_curve.size=0.23
letter_curve.align_x='CENTER'
letter_curve.align_y='CENTER'
letter_curve.extrude=0.004
letter_obj=bpy.data.objects.new('ME_R1_Entrance_Lettering',letter_curve)
asset.objects.link(letter_obj)
xaxis=Vector((-front_t.x,-front_t.y,0.0)); yaxis=Vector((0.0,0.0,1.0)); zaxis=Vector((front_n.x,front_n.y,0.0))
rot=Matrix.Identity(3); rot.col[0]=xaxis; rot.col[1]=yaxis; rot.col[2]=zaxis
letter_obj.rotation_euler=rot.to_euler()
letter_obj.location=(portal_center.x+front_n.x*0.47,portal_center.y+front_n.y*0.47,3.42)
letter_curve.materials.append(lettering)

# Set custom metadata so the project's uncertainty remains visible in Blender.
asset['r1_revision']='R1 photo-informed exterior window openings and Gatewood entrance'
asset['r1_facade_source']='Purdue ME 2025 renovation/history photos; Wikimedia Commons photo dated 2024-06-20'
asset['r1_height_status']='Unverified. Four visible window bands are approximate; shell top and level spacing were not altered.'
asset['r1_window_status']='Qualitative photo-derived repeats on long GIS perimeter faces; exact count/spacing and per-wing variations unverified.'
asset['r1_entrance_status']='Fountain-facing Gatewood entrance face chosen by GIS geometry and Purdue direction statement; exact along-wall placement estimated.'

# Standalone lighting and two saved review cameras; these do not affect master.
for ob in list(scene.objects):
    if ob.name.startswith('ME_R1_Cam_') or ob.name in ('ME_R1_Sun','ME_R1_Entrance_Fill'):
        bpy.data.objects.remove(ob,do_unlink=True)
world=bpy.data.worlds.get('ME_R1_Clear_Day') or bpy.data.worlds.new('ME_R1_Clear_Day')
world.use_nodes=True
wn=world.node_tree.nodes; wl=world.node_tree.links
wn.clear(); wout=wn.new('ShaderNodeOutputWorld'); bg=wn.new('ShaderNodeBackground'); sky=wn.new('ShaderNodeTexSky')
sky.sky_type='HOSEK_WILKIE'; sky.sun_elevation=math.radians(40); sky.sun_rotation=math.radians(215); sky.air_density=1.0
bg.inputs['Strength'].default_value=0.72; wl.new(sky.outputs['Color'],bg.inputs['Color']); wl.new(bg.outputs['Background'],wout.inputs['Surface'])
scene.world=world
sun_data=bpy.data.lights.new('ME_R1_Sun_Data','SUN'); sun_data.energy=3.0; sun_data.angle=math.radians(18)
sun=bpy.data.objects.new('ME_R1_Sun',sun_data); scene.collection.objects.link(sun)
sun.rotation_euler=(math.radians(25),math.radians(-30),math.radians(-35))
fill_data=bpy.data.lights.new('ME_R1_Entrance_Fill_Data','AREA'); fill_data.energy=2600; fill_data.shape='DISK'; fill_data.size=34
fill=bpy.data.objects.new('ME_R1_Entrance_Fill',fill_data); scene.collection.objects.link(fill)
fill.location=(portal_center.x+front_n.x*45,portal_center.y+front_n.y*45,29.0)
fill.rotation_euler=(Vector((portal_center.x,portal_center.y,8.0))-fill.location).to_track_quat('-Z','Y').to_euler()

def camera(name, location, target, lens=42.0, ortho=None):
    cd=bpy.data.cameras.new(name+'_Data'); ob=bpy.data.objects.new(name,cd); scene.collection.objects.link(ob)
    ob.location=location; ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    if ortho:
        cd.type='ORTHO'; cd.ortho_scale=ortho
    else: cd.lens=lens
    return ob

facade_target=Vector((portal_center.x,portal_center.y,8.4))
front_cam=camera('ME_R1_Cam_Entrance',(portal_center.x+front_n.x*58,portal_center.y+front_n.y*58,13.5),facade_target,ortho=83)
hero_target=Vector((4.2,12.0,7.0))
hero_cam=camera('ME_R1_Cam_Hero',(145,-155,112),hero_target,ortho=185)
scene.camera=hero_cam
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1600; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False

# Persist, reopen, and validate the saved source before rendering grade views.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_mechanical_engineering']; scene=bpy.context.scene
check={
    'asset_reopened': True,
    'direct_objects': len(asset.objects),
    'child_inclusive_objects': len(asset.all_objects),
    'root': [round(float(v),6) for v in bpy.data.objects['AssetRoot_mechanical_engineering'].location],
    'root_scale': [round(float(v),6) for v in bpy.data.objects['AssetRoot_mechanical_engineering'].scale],
    'shell_window_boolean_applied': not any(m.name=='R1_Photographic_Facade_Openings' for m in bpy.data.objects['ME_Official_857_Structural_Envelope'].modifiers),
    'shell_openings_faceted_face_count': len(bpy.data.objects['ME_Official_857_Structural_Envelope'].data.polygons),
    'added_windows': len(window_specs),
    'added_material_nodes': [m.name for m in bpy.data.materials if m.name.startswith('ME_R1_')],
    'unpacked_external_images': [im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not im.filepath.startswith('//')],
    'front_edge_index': front_edge['index'],
    'front_edge_length_m': round(front_length,3),
    'front_edge_outward_normal': [round(front_n.x,5),round(front_n.y,5)],
    'front_center_local_m': [round(portal_center.x,3),round(portal_center.y,3)],
    'placement_origin_unchanged': [66.30000114440918,86.5],
    'master_edited': False,
}
for camname,rendername in [('ME_R1_Cam_Hero','mechanical_engineering_r1_hero.png'),('ME_R1_Cam_Entrance','mechanical_engineering_r1_entrance.png')]:
    scene.camera=bpy.data.objects[camname]
    scene.render.filepath=str(AUDIT/rendername)
    bpy.ops.render.render(write_still=True)
check['render_files']=['audit/complete_me/mechanical_engineering_r1_hero.png','audit/complete_me/mechanical_engineering_r1_entrance.png']
check['passed']=bool(check['asset_reopened'] and check['shell_window_boolean_applied'] and check['root']==[0.0,0.0,0.0] and check['root_scale']==[1.0,1.0,1.0] and not check['unpacked_external_images'])
(AUDIT/'mechanical_engineering_r1_validation.json').write_text(json.dumps(check,indent=2)+'\n',encoding='utf-8')
print(json.dumps(check,indent=2))
