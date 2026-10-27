"""Flex Lab facade correction R2 based on Ennead and CE Solutions references."""
import bpy, bmesh, math, json, hashlib
from pathlib import Path
from mathutils import Vector

ASSET = Path(bpy.data.filepath).resolve()
COLL = bpy.data.collections.get('Asset_flex_lab')
if COLL is None:
    raise RuntimeError('Asset_flex_lab missing')
root = bpy.context.scene.collection
before_sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()

# Idempotent replacement of R2-created details.
for obj in list(bpy.data.objects):
    if obj.name.startswith('FLEX_R2 |'):
        bpy.data.objects.remove(obj, do_unlink=True)

# Remove the fully opaque south wall face so the glazing and entry can be seen.
shell = bpy.data.objects.get('FLEX structural shell | GIS outline')
if shell is None or shell.type != 'MESH':
    raise RuntimeError('GIS structural shell missing')
bm = bmesh.new(); bm.from_mesh(shell.data); bm.faces.ensure_lookup_table()
remove = []
side_windows = []
south_face_count = 0
for face in bm.faces:
    n = face.normal
    c = face.calc_center_median()
    xs = [loop.vert.co.x for loop in face.loops]
    ys = [loop.vert.co.y for loop in face.loops]
    if n.y < -0.995 and abs(n.x) < 0.01 and abs(n.z) < 0.01 and c.y < -49.0 and (max(xs)-min(xs)) > 20.0:
        remove.append(face)
        south_face_count += 1
    elif abs(n.x) > 0.995 and abs(n.y) < 0.01 and abs(n.z) < 0.01 and (max(ys)-min(ys)) > 10.0:
        side_windows.append({'x':sum(xs)/len(xs),'normal_x':1.0 if n.x > 0 else -1.0,'y_min':min(ys),'y_max':max(ys)})
        remove.append(face)
if south_face_count != 1 or len(side_windows) < 8:
    bm.free()
    raise RuntimeError(f'Expected one south face and >=8 east/west glazing bays; south={south_face_count}, side bays={len(side_windows)}')
bmesh.ops.delete(bm, geom=remove, context='FACES_ONLY')
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(shell.data); bm.free(); shell.data.update()
shell['flex_r2_south_curtainwall_opening'] = True
shell['flex_r2_long_facade_curtainwall_bays'] = len(side_windows)

# Remove overlapping/inaccurate facade and canopy passes that obscured the source-backed composition.
remove_exact = {
    'Curtainwall vertical mullions',
    'FLEX | offset high-bay curtainwall',
    'FLEX | long white cantilever entrance canopy',
    'Flex Lab 20-foot entry canopy',
    'Flex Lab | entry canopy',
    'FLEX cast metal facade sign',
    'Continuous horizontal facade banding',
    'Flex Lab | entrance name panel',
}
for obj in list(bpy.data.objects):
    if (obj.name in remove_exact or
        obj.name.startswith('FLEX brick piers between glass bays') or
        obj.name.startswith('FLEX | aluminum vertical fin') or
        obj.name.startswith('FLEX | high-bay glazing mullion') or
        obj.name.startswith('FLEX shifting curtainwall | vertical curtainwall mullion') or
        obj.name.startswith('FLEX shifting curtainwall | horizontal spandrel') or
        (obj.name.startswith('Flex Lab | canopy column'))):
        bpy.data.objects.remove(obj, do_unlink=True)

# Find existing procedural materials. Create dependable node materials if needed.
def principled_material(name, color, metallic=0.0, roughness=0.35, alpha=1.0, transmission=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, alpha)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        if 'Alpha' in bsdf.inputs: bsdf.inputs['Alpha'].default_value = alpha
        if 'Transmission Weight' in bsdf.inputs: bsdf.inputs['Transmission Weight'].default_value = transmission
        if 'IOR' in bsdf.inputs: bsdf.inputs['IOR'].default_value = 1.48
    try:
        mat.surface_render_method = 'DITHERED' if alpha < 0.99 else 'DITHERED'
    except Exception:
        pass
    return mat

glass = principled_material('FLEX_R2 | low-iron blue gray curtainwall', (0.28,0.42,0.49), 0.12, 0.10, 0.18, 0.65)
glass_nodes=glass.node_tree.nodes; glass_nodes.clear()
glass_out=glass_nodes.new('ShaderNodeOutputMaterial')
glass_mix=glass_nodes.new('ShaderNodeMixShader'); glass_mix.inputs[0].default_value=0.20
glass_transparent=glass_nodes.new('ShaderNodeBsdfTransparent')
glass_surface=glass_nodes.new('ShaderNodeBsdfPrincipled')
glass_surface.inputs['Base Color'].default_value=(0.34,0.48,0.54,1)
glass_surface.inputs['Metallic'].default_value=0.10
glass_surface.inputs['Roughness'].default_value=0.12
if 'Transmission Weight' in glass_surface.inputs: glass_surface.inputs['Transmission Weight'].default_value=0.16
glass.node_tree.links.new(glass_transparent.outputs['BSDF'],glass_mix.inputs[1])
glass.node_tree.links.new(glass_surface.outputs['BSDF'],glass_mix.inputs[2])
glass.node_tree.links.new(glass_mix.outputs['Shader'],glass_out.inputs['Surface'])
metal = principled_material('FLEX_R2 | charcoal anodized aluminum', (0.16,0.19,0.20), 0.72, 0.27)
white_metal = bpy.data.materials.get('FLEX_LAB | evidence palette stone and painted metal')
brick = bpy.data.materials.get('FLEX_LAB | evidence palette textured masonry')
if white_metal is None: white_metal = principled_material('FLEX_R2 | pale silver metal', (0.68,0.70,0.68), 0.38, 0.31)
if brick is None: brick = principled_material('FLEX_R2 | red brick', (0.35,0.105,0.07), 0.0, 0.82)

# Replace glass slots on the existing center bay and entry doors.
for name in ['FLEX shifting curtainwall | curtainwall glass', 'Flex Lab | glazed entrance doors']:
    obj = bpy.data.objects.get(name)
    if obj and obj.type == 'MESH':
        obj.data.materials.clear(); obj.data.materials.append(glass)

# Cube builder creates real local-space shell pieces, mullions, and the one verified canopy.
def add_box(name, center, size, material):
    cx,cy,cz = center; sx,sy,sz = size
    v=[(cx+dx*sx/2,cy+dy*sy/2,cz+dz*sz/2) for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    f=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh=bpy.data.meshes.new(name+' | mesh'); mesh.from_pydata(v,[],f); mesh.materials.append(material); mesh.update()
    obj=bpy.data.objects.new(name,mesh); COLL.objects.link(obj); return obj

def add_beam(name, a, b, width, depth, material):
    a=Vector(a); b=Vector(b); d=b-a
    obj=add_box(name,(a+b)*0.5,(width,depth,d.length),material)
    obj.rotation_mode='QUATERNION'; obj.rotation_quaternion=d.to_track_quat('Z','Y')
    return obj

# Flanking brick planes are the source-supported full-height solids. Keep narrow reveals at their edges.
front_y = -49.2375
for name,x,w in [('left',-6.20,1.20),('right',5.02,1.20)]:
    add_box(f'FLEX_R2 | {name} full-height brick plane', (x,front_y-0.20,6.9), (w,0.42,14.8), brick)
# Close the wall opening below grade with a continuous concrete/brick plinth.
foundation = bpy.data.materials.get('FLEX | foundation concrete') or brick
add_box('FLEX_R2 | south facade foundation sill',(-0.5885,front_y-0.12,-0.52),(23.96,0.28,0.96),foundation)

# Side curtainwall wings: floor-to-floor glazing with slender anodized mullions and projecting fins.
# Their extents fill the documented gaps between the GIS shell edge, brick planes and central glazed lobby.
wing_specs=[('west',-12.10,-6.82),('east',5.62,11.12)]
for wing,x0,x1 in wing_specs:
    span=x1-x0
    z_levels=[(0.32,4.55),(5.02,9.48),(10.00,14.35)]
    for floor,(z0,z1) in enumerate(z_levels,1):
        # 5 narrow glass lites per storey; slight gaps expose readable mullion rhythm.
        gap=0.035; n=7; lite=(span-gap*(n+1))/n
        for i in range(n):
            x=x0+gap+i*(lite+gap)+lite/2
            add_box(f'FLEX_R2 | {wing} floor {floor} curtainwall lite {i+1:02d}',(x,front_y-0.075,(z0+z1)/2),(lite,0.08,z1-z0),glass)
    # Continuous floor rails match the three-level floor rhythm visible in the architect photographs.
    for z in [4.77,9.76]:
        add_box(f'FLEX_R2 | {wing} opaque floor spandrel {z:.2f}',((x0+x1)/2,front_y-0.10,z),(span,0.16,0.36),white_metal)
        add_box(f'FLEX_R2 | {wing} aluminum floor transom {z:.2f}',((x0+x1)/2,front_y-0.19,z),(span,0.11,0.075),metal)
    # Mullions every ~0.75 m, with stronger projecting vertical fins at alternating bays.
    count=7
    for i in range(count+1):
        x=x0+span*i/count
        add_box(f'FLEX_R2 | {wing} vertical mullion {i:02d}',(x,front_y-0.14,7.35),(0.065,0.12,14.18),metal)
    for i in range(2,count,3):
        x=x0+span*i/count
        add_box(f'FLEX_R2 | {wing} projecting curtainwall fin {i:02d}',(x,front_y-0.25,7.35),(0.11,0.30,14.2),metal)

# The architect's full-facade images show alternating glass bays and projecting brick planes.
# Open the long GIS perimeter faces at their existing stepped bay rhythm and infill with curtainwall.
side_windows.sort(key=lambda w:(round(w['x'],3),w['y_min']))
for bay_index,bay in enumerate(side_windows,1):
    xwall=bay['x']; outward=bay['normal_x']; y0=bay['y_min']+0.38; y1=bay['y_max']-0.38
    span=y1-y0; xc=xwall+outward*0.075; yc=(y0+y1)/2
    tag=f'{int(outward):+d} bay {bay_index:02d}'
    for floor,(z0,z1) in enumerate([(0.32,4.55),(5.02,9.48),(10.00,14.35)],1):
        add_box(f'FLEX_R2 | long facade {tag} floor {floor} curtainwall',(xc,yc,(z0+z1)/2),(0.08,span,z1-z0),glass)
    count=max(6,round(span/1.0))
    for i in range(count+1):
        y=y0+span*i/count
        add_box(f'FLEX_R2 | long facade {tag} mullion {i:02d}',(xwall+outward*0.15,y,7.35),(0.13,0.065,14.18),metal)
    for i in range(2,count,3):
        y=y0+span*i/count
        add_box(f'FLEX_R2 | long facade {tag} projecting fin {i:02d}',(xwall+outward*0.27,y,7.35),(0.30,0.12,14.2),metal)
    for z in [4.77,9.76]:
        add_box(f'FLEX_R2 | long facade {tag} floor spandrel {z:.2f}',(xwall+outward*0.10,yc,z),(0.16,span,0.36),white_metal)
        add_box(f'FLEX_R2 | long facade {tag} floor transom {z:.2f}',(xwall+outward*0.19,yc,z),(0.11,span,0.075),metal)

# Recess the source-supported central glass lobby behind the flanking brick planes.
center_glass=bpy.data.objects.get('FLEX shifting curtainwall | curtainwall glass')
if center_glass:
    xs=[v.co.x for v in center_glass.data.vertices]
    cx=(min(xs)+max(xs))*0.5
    for v in center_glass.data.vertices: v.co.x=cx+(v.co.x-cx)*(9.5/(max(xs)-min(xs)))
    center_glass.data.update(); center_glass.location.y += 3.55
    center_glass['flex_r2_role']='central full-height entry lobby glazing; set behind paired brick planes'
    center_glass['flex_r2_recess_m']=3.55
    cmin=min(v.co.x for v in center_glass.data.vertices); cmax=max(v.co.x for v in center_glass.data.vertices)
    center_x=cx
    center_y=-49.4+3.55
    # A simple 7-bay / 3-floor grid follows the central entrance glazing in the source photograph.
    for i in range(8):
        x=cmin+(cmax-cmin)*i/7
        add_box(f'FLEX_R2 | lobby vertical mullion {i:02d}',(x,center_y-0.07,7.2),(0.065,0.12,14.3),metal)
    for z in [4.77,9.76]:
        add_box(f'FLEX_R2 | lobby horizontal transom {z:.2f}',(center_x,center_y-0.07,z),(cmax-cmin,0.12,0.08),metal)

# Recess doors, inscription and vestibule details with the glazing, leaving the approach open.
for name in ['Flex Lab | glazed entrance doors','Flex Lab | entrance lettering','FLEX_LAB | schematic vestibule visible through entry']:
    obj=bpy.data.objects.get(name)
    if obj:
        obj.location.y += 3.55
        if name == 'Flex Lab | entrance lettering':
            obj.scale *= 1.7
            obj.data.materials.clear(); obj.data.materials.append(white_metal)
        obj['flex_r2_recess_m']=3.55

# Brick side returns frame the recessed vestibule; a low threshold floor connects to the existing walk.
for name,x in [('west',-5.48),('east',4.32)]:
    add_box(f'FLEX_R2 | {name} recessed vestibule brick return',(x,front_y+1.78,6.9),(0.26,3.55,14.8),brick)
add_box('FLEX_R2 | recessed vestibule threshold floor',(-0.5885,-47.45,-0.78),(9.3,3.8,0.22),foundation)
# One documented 20-foot (6.10 m) entry cantilever; older duplicate canopies were removed.
canopy=add_box('FLEX_R2 | 20 ft cantilever entry canopy',(-0.5885,-52.28,5.25),(10.2,6.10,0.48),white_metal)
canopy['source_dimension']='20 ft / 6.096 m canopy projection reported by CE Solutions; modeled depth 6.10 m'
# Structural steel vestibule supports are set clear of the doors, aligned with the brick/glass bay edges.
for side,x in [('west',-5.15),('east',3.97)]:
    add_box(f'FLEX_R2 | {side} vestibule steel support',(x,-50.12,2.52),(0.32,0.38,5.04),white_metal)

# Refresh scene-bound geometry only; do not change the manifest placement origin or collection identity.
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
after_sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
print(json.dumps({'status':'built','asset':str(ASSET),'before_sha256':before_sha,'after_sha256':after_sha,'new_facade_objects':sum(o.name.startswith('FLEX_R2 |') for o in COLL.objects),'collection_object_count':len(COLL.all_objects),'south_face_removed':True,'long_facade_bays':len(side_windows),'canopy_projection_m':6.10}))


