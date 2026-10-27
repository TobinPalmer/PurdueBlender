import bpy, math, json, os
from mathutils import Vector

ROOT = r'C:\Users\Tobin\Documents\Blender\PurdueMap'
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'massing_house_301837281_58ead22.blend')
OUT = os.path.join(ROOT, 'audit', 'phi_gamma_delta')
COLLECTION_NAME = 'Asset_massing_house_301837281_58ead22'
SCENE_NAME = 'Building_massing_house_301837281_58ead22'

# Vertices are the existing library mesh coordinates, which closely track the
# public Purdue GIS FID 787 roof-outline polygon. North is +Y, east is +X.
outline = [(-417.844879,423.562073),(-417.683746,409.626556),
           (-424.494049,409.548828),(-424.519470,412.158264),
           (-431.906494,412.069427),(-431.864075,408.471741),
           (-420.083893,408.604980),(-419.965149,397.878540),
           (-442.719849,397.623138),(-443.008179,423.273376)]
main_rect = (-443.008179, -419.965149, 397.623138, 423.273376)
GROUND = 0.0
ADDITION_EAVE = 4.25
MAIN_EAVE = 10.35
MAIN_RIDGE = 12.00
ROOF_OVERHANG = 0.32

scene = bpy.context.scene
assert scene.name == SCENE_NAME, scene.name
asset_col = bpy.data.collections.get(COLLECTION_NAME)
assert asset_col is not None
root_obj = bpy.data.objects.get('House_301837281')
assert root_obj is not None and root_obj.type == 'MESH'

# Remove only generated geometry from earlier runs; preserve the stable root object.
for obj in list(asset_col.objects):
    if obj != root_obj:
        bpy.data.objects.remove(obj, do_unlink=True)

def material(name, color, rough=0.8, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metallic
    return m

brick = material('PhiGam_Buff_Tan_Brick', (0.55,0.34,0.18), .88)
brick_light = material('PhiGam_Brick_Variation', (0.48,0.36,0.23), .9)
stone = material('PhiGam_Limestone_Trim', (0.73,0.65,0.51), .75)
foundation = material('PhiGam_Foundation_Stone', (0.45,0.40,0.32), .9)
roofmat = material('PhiGam_Weathered_Slate', (0.105,0.12,0.13), .82)
glass = material('PhiGam_Window_Glass', (0.075,0.13,0.16), .26, .12)
frame = material('PhiGam_Painted_Window_Frames', (0.78,0.75,0.67), .62)
door = material('PhiGam_Entry_Door', (0.18,0.12,0.085), .66)
metal = material('PhiGam_Gutter_Metal', (0.16,0.18,0.18), .42, .55)

def reset_nodes(mat):
    for node in list(mat.node_tree.nodes):
        if node.type not in {'OUTPUT_MATERIAL','BSDF_PRINCIPLED'}: mat.node_tree.nodes.remove(node)
    return mat.node_tree.nodes, mat.node_tree.links, mat.node_tree.nodes['Principled BSDF']

# Repeating brick material uses real-size UV coordinates on wall faces. Texture
# remains embedded in nodes and has no external image dependency.
nodes,links,bsdf=reset_nodes(brick)
uvnode=nodes.new('ShaderNodeTexCoord')
bricktex=nodes.new('ShaderNodeTexBrick'); bricktex.inputs['Scale'].default_value=1.0
bricktex.inputs['Color1'].default_value=(.48,.30,.17,1); bricktex.inputs['Color2'].default_value=(.40,.24,.13,1)
bricktex.inputs['Mortar'].default_value=(.29,.22,.15,1); bricktex.inputs['Mortar Size'].default_value=.022
bricktex.inputs['Mortar Smooth'].default_value=.008
links.new(uvnode.outputs['UV'],bricktex.inputs['Vector']); links.new(bricktex.outputs['Color'],bsdf.inputs['Base Color'])
brick_bump=nodes.new('ShaderNodeBump'); brick_bump.inputs['Strength'].default_value=.15; brick_bump.inputs['Distance'].default_value=.009
links.new(bricktex.outputs['Fac'],brick_bump.inputs['Height']); links.new(brick_bump.outputs['Normal'],bsdf.inputs['Normal'])
bricktexrough=nodes.new('ShaderNodeMapRange'); bricktexrough.inputs['From Min'].default_value=0; bricktexrough.inputs['From Max'].default_value=1
bricktexrough.inputs['To Min'].default_value=.74; bricktexrough.inputs['To Max'].default_value=.94
links.new(bricktex.outputs['Fac'],bricktexrough.inputs['Value']); links.new(bricktexrough.outputs['Result'],bsdf.inputs['Roughness'])

# Noise and micro-bump give the dark slate a dry granular surface at building scale.
nodes,links,bsdf=reset_nodes(roofmat)
coord=nodes.new('ShaderNodeTexCoord'); noise=nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=75
noise.inputs['Detail'].default_value=3; links.new(coord.outputs['Generated'],noise.inputs['Vector'])
rooframp=nodes.new('ShaderNodeValToRGB'); rooframp.color_ramp.elements[0].position=.18
rooframp.color_ramp.elements[0].color=(.035,.042,.048,1)
rooframp.color_ramp.elements[1].position=.82; rooframp.color_ramp.elements[1].color=(.15,.17,.18,1)
links.new(noise.outputs['Fac'],rooframp.inputs['Fac']); links.new(rooframp.outputs['Color'],bsdf.inputs['Base Color'])
roofbump=nodes.new('ShaderNodeBump'); roofbump.inputs['Strength'].default_value=.2; roofbump.inputs['Distance'].default_value=.018
links.new(noise.outputs['Fac'],roofbump.inputs['Height']); links.new(roofbump.outputs['Normal'],bsdf.inputs['Normal'])
roofrough=nodes.new('ShaderNodeMapRange'); roofrough.inputs['To Min'].default_value=.62; roofrough.inputs['To Max'].default_value=.88
links.new(noise.outputs['Fac'],roofrough.inputs['Value']); links.new(roofrough.outputs['Result'],bsdf.inputs['Roughness'])

def add_obj(name, verts, faces, mat, bevel=0):
    mesh=bpy.data.meshes.new(name+'Mesh'); mesh.from_pydata(verts, [], faces); mesh.materials.append(mat); mesh.update()
    ob=bpy.data.objects.new(name,mesh); asset_col.objects.link(ob)
    if bevel:
        mod=ob.modifiers.new('Soft_Edges','BEVEL'); mod.width=bevel; mod.segments=2
        ob.modifiers.new('Weighted_Corner_Normals','WEIGHTED_NORMAL')
    return ob

def cube(name, loc, dims, mat, bevel=.025, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object
    o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.rotation_euler=rotation
    for c in list(o.users_collection): c.objects.unlink(o)
    asset_col.objects.link(o); o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('Fine_Edge_Bevel','BEVEL'); b.width=bevel; b.segments=2
        o.modifiers.new('Weighted_Corner_Normals','WEIGHTED_NORMAL')
    return o

def prism_polygon(name, poly, z0, z1, mat):
    n=len(poly); verts=[(x,y,z) for z in (z0,z1) for x,y in poly]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    ob=add_obj(name,verts,faces,mat); uv=ob.data.uv_layers.new(name='MasonryUV')
    for pi,p in enumerate(ob.data.polygons):
        if pi<2:
            coords=[(verts[v][0],verts[v][1]) for v in p.vertices]
        else:
            a,b=poly[pi-2],poly[(pi-1)%n]
            use_x=abs(b[0]-a[0])>=abs(b[1]-a[1])
            coords=[((verts[v][0]-a[0]) if use_x else (verts[v][1]-a[1]), verts[v][2]) for v in p.vertices]
        for li,co in zip(p.loop_indices,coords): uv.data[li].uv=co
    return ob

# Stable root object remains the footprint-base object. Its upper level is
# constructed separately so the documented addition massing can remain lower.
root_obj.data.clear_geometry(); root_obj.data.materials.clear(); root_obj.data.materials.append(brick)
base_mesh=bpy.data.meshes.new('PhiGam_GIS_Footprint_Base')
n=len(outline); vv=[(x,y,z) for z in (GROUND,ADDITION_EAVE) for x,y in outline]
ff=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
ff += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
base_mesh.from_pydata(vv,[],ff); base_mesh.materials.append(brick); base_mesh.update()
base_uv=base_mesh.uv_layers.new(name='MasonryUV')
for pi,p in enumerate(base_mesh.polygons):
    if pi<2: coords=[(vv[v][0],vv[v][1]) for v in p.vertices]
    else:
        a,b=outline[pi-2],outline[(pi-1)%n]
        use_x=abs(b[0]-a[0])>=abs(b[1]-a[1])
        coords=[((vv[v][0]-a[0]) if use_x else (vv[v][1]-a[1]),vv[v][2]) for v in p.vertices]
    for li,co in zip(p.loop_indices,coords): base_uv.data[li].uv=co
root_obj.data=base_mesh
root_obj.name='House_301837281'

# The GIS roof outline is a U-shaped plan with an open inset on its east side.
# Build the upper original-house mass in two outline-following arms, leaving the
# notch open instead of bridging it with a large bounding-box extrusion.
x0,x1,y0,y1=main_rect
west_edge=-431.864075
south_inner_y=408.471741
north_inner_y=412.069427
south_inner_x=-419.965149
north_east_x=-417.844879
west_upper=[(x0,y0),(west_edge,y0),(west_edge,y1),(x0,y1)]
south_upper=[(west_edge,y0),(south_inner_x,y0),(south_inner_x,south_inner_y),(west_edge,south_inner_y)]
prism_polygon('Original_Chapter_House_West_Upper_Stories',west_upper,ADDITION_EAVE,MAIN_EAVE,brick)
prism_polygon('Original_Chapter_House_South_Upper_Stories',south_upper,ADDITION_EAVE,MAIN_EAVE,brick)

def hip_roof(name, rect, eave, rise, overhang=.28):
    ax0,ax1,ay0,ay1=rect
    ax0-=overhang; ax1+=overhang; ay0-=overhang; ay1+=overhang
    dx=ax1-ax0; dy=ay1-ay0
    if dx>=dy:
        inset=min(dy*.25,1.65); ylo=ay0+inset; yhi=ay1-inset
        verts=[(ax0,ay0,eave),(ax1,ay0,eave),(ax1,ay1,eave),(ax0,ay1,eave),
               (ax0+inset,ylo,eave+rise),(ax1-inset,ylo,eave+rise),
               (ax1-inset,yhi,eave+rise),(ax0+inset,yhi,eave+rise)]
    else:
        inset=min(dx*.25,1.65); xlo=ax0+inset; xhi=ax1-inset
        verts=[(ax0,ay0,eave),(ax1,ay0,eave),(ax1,ay1,eave),(ax0,ay1,eave),
               (xlo,ay0+inset,eave+rise),(xhi,ay0+inset,eave+rise),
               (xhi,ay1-inset,eave+rise),(xlo,ay1-inset,eave+rise)]
    # Closed roof shell: upper hip planes plus eave fascias and a concealed bottom.
    topverts=verts[:]
    verts += [(ax0,ay0,eave-.16),(ax1,ay0,eave-.16),(ax1,ay1,eave-.16),(ax0,ay1,eave-.16)]
    faces=[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7),
           (11,10,9,8),(0,1,9,8),(1,2,10,9),(2,3,11,10),(3,0,8,11)]
    return add_obj(name,verts,faces,roofmat)

# Individual hip planes follow the GIS arms; the east/north wing is lower to
# distinguish the new addition, based on the official concept view and aerial.
hip_roof('Original_House_West_Hipped_Slate_Roof',(x0,west_edge,y0,y1),MAIN_EAVE,1.65)
hip_roof('Original_House_South_Hipped_Slate_Roof',(west_edge,south_inner_x,y0,south_inner_y),MAIN_EAVE,1.45)
addition_rect=(-431.864075,-417.683746,north_inner_y,423.562073)
hip_roof('Lyles_Addition_Low_Hipped_Slate_Roof',addition_rect,ADDITION_EAVE,.8,.20)

# Base course and corner stone detailing on the original home.
for side,y in [('south',y0-.045),('north',y1+.045)]:
    cube('Main_House_'+side+'_Stone_Base',((x0+x1)/2,y,.34),(x1-x0,.12,.68),foundation,.015)
for side,x in [('west',x0-.045),('east',x1+.045)]:
    cube('Main_House_'+side+'_Stone_Base',(x,(y0+y1)/2,.34),(.12,y1-y0,.68),foundation,.015)
for x,y,zheight in ((x0+.30,y0-.12,10.1),(x1-.30,y0-.12,10.1),
                    (x0+.30,y1+.12,10.1),(north_east_x-.30,y1+.12,4.0)):
    cube('Main_House_Stone_Corner_Pilaster',(x,y,zheight/2),(.48,.24,zheight),stone,.02)

def south_window(cx, zc, w=1.28, h=1.55):
    y=y0-.11
    # visible light limestone surround, dark recessed glazing, and simple sash bars
    cube('South_Window_Stone_Surround',(cx,y,zc),(w+.18,.16,h+.18),stone,.025)
    cube('South_Window_Glazing',(cx,y-.095,zc),(w,.055,h),glass,.01)
    cube('South_Window_Mullion_V',(cx,y-.14,zc),(.055,.035,h),frame,.01)
    cube('South_Window_Mullion_H',(cx,y-.14,zc),(w,.035,.055),frame,.01)
    cube('South_Window_Sill',(cx,y-.07,zc-h/2-.10),(w+.30,.28,.13),stone,.025)

def side_window(cy, zc, side='west', w=1.2, h=1.5):
    x=x0-.11 if side=='west' else north_east_x+.11
    sx=-1 if side=='west' else 1
    cube(side+'_Window_Stone_Surround',(x,cy,zc),(.16,w+.18,h+.18),stone,.02)
    cube(side+'_Window_Glazing',(x+sx*.095,cy,zc),(.055,w,h),glass,.01)
    cube(side+'_Window_Mullion_V',(x+sx*.14,cy,zc),(.035,.055,h),frame,.008)
    cube(side+'_Window_Mullion_H',(x+sx*.14,cy,zc),(.035,w,.055),frame,.008)
    cube(side+'_Window_Sill',(x+sx*.07,cy,zc-h/2-.1),(.28,w+.3,.13),stone,.02)

def addition_arch_window(cy):
    # Large round-headed glazed openings reflect the architect's published Lyles
    # Addition view; exact count/spacing is estimated, not measured.
    x=north_east_x+.14; base=.46; spring=2.10; r=.72; n=16; depth=.065
    points=[(cy-r,base),(cy+r,base),(cy+r,spring)]
    points += [(cy+r*math.cos(math.pi*i/n),spring+r*math.sin(math.pi*i/n)) for i in range(1,n+1)]
    verts=[(x,y,z) for y,z in points]+[(x-depth,y,z) for y,z in points]
    count=len(points); faces=[tuple(range(count)),tuple(range(2*count-1,count-1,-1))]
    faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    add_obj('Lyles_Addition_Arched_Glazing',verts,faces,glass)
    cube('Lyles_Arch_Sill',(x+.12,cy,base-.08),(.20,2*r+.36,.14),stone,.025)
    for sign in (-1,1):
        cube('Lyles_Arch_Jamb',(x+.12,cy+sign*(r+.10),(base+spring)/2),(.21,.20,spring-base),stone,.02)
    outer=r+.18; inner=r+.01; mid=(outer+inner)/2; nseg=12
    for i in range(nseg):
        a=math.pi*(i+.5)/nseg; seg=2*mid*math.sin(math.pi/(2*nseg))+.02
        cube('Lyles_Stone_Arch_Voussoir',(x+.12,cy+mid*math.cos(a),spring+mid*math.sin(a)),
             (.22,seg,outer-inner),stone,.012,(a+math.pi/2,0,0))
    cube('Lyles_Arched_Glazing_Mullion',(x+.20,cy,spring/2),(.045,.055,spring-base),frame,.008)
    cube('Lyles_Arched_Glazing_Transom',(x+.20,cy,spring-.10),(.045,2*r,.055),frame,.008)

def south_door(cx):
    # Arched glazed entry opening, framed by a cream stone arch and voussoir blocks.
    y=y0-.14; width=1.42; spring=2.05; radius=width/2
    cube('Arched_Entry_Door',(cx,y-.05,spring/2),(width,.11,spring),door,.015)
    cube('Entry_Door_Glazing',(cx,y-.12,1.12),(width-.23,.04,1.72),glass,.012)
    for dx in (-.34,0,.34): cube('Entry_Door_Mullion',(cx+dx,y-.16,1.12),(.035,.03,1.72),frame,.006)
    # Closed voussoir blocks follow the half-round arch; no single-face ring mesh.
    outer=radius+.19; inner=radius-.02; zc=spring; nseg=12
    for i in range(nseg):
        a=math.pi*(i+.5)/nseg; r=(outer+inner)/2
        seg=2*r*math.sin(math.pi/(2*nseg))+.015
        cube('Entry_Stone_Arch_Voussoir', (cx+r*math.cos(a),y-.13,zc+r*math.sin(a)),
             (seg,.20,outer-inner),stone,.012,(0,a-math.pi/2,0))
    for dx in (-radius-.10,radius+.10): cube('Entry_Stone_Jamb',(cx+dx,y-.11,1.08),(.20,.20,2.14),stone,.018)

# Front/south façade: three differentiated stories, repeated openings, and two
# arched entries are supported by the 2025 construction photograph / official concept view.
for cx,w in ((-439.1,1.12),(-436.0,1.05),(-432.8,1.15),(-429.6,1.12),(-421.8,1.25)):
    south_window(cx,9.62,w,1.22)
for cx,w in ((-439.0,1.30),(-434.1,1.20),(-428.8,1.28),(-421.8,1.35)):
    south_window(cx,6.70,w,1.58)
for cx in (-421.9,): south_window(cx,3.35,1.38,1.72)
for cx in (-438.2,-433.2): south_door(cx)

# The photographed long facade has clustered openings and a conspicuous blank
# wall span toward the addition end. The other elevation is less documented, so
# a sparser, staggered window pattern is retained there as an estimate.
for cy in (400.3,405.4,412.0,419.7): side_window(cy,9.62,'west',1.15,1.20)
for cy in (400.7,406.1,416.1,421.0): side_window(cy,6.70,'west',1.2,1.50)
for cy in (402.0,410.2,418.2): side_window(cy,3.35,'west',1.26,1.70)
for cy in (414.0,418.0,422.0):
    addition_arch_window(cy)

# Repeated brick pilaster/belt courses break the long facade while keeping the
# measured GIS wall footprint unchanged.
for z in (3.30,6.65):
    cube('South_Facade_Story_Belt_Course',((x0+x1)/2,y0-.095,z),(x1-x0,.11,.12),brick_light,.01)

# Gutters and downspouts are subtle metal details visible in the progress photo.
cube('South_Eave_Gutter',((x0+x1)/2,y0-.38,MAIN_EAVE-.08),(x1-x0+.6,.12,.13),metal,.03)
for x in (x0+.38,x1-.38): cube('South_Downspout',(x,y0-.39,5.0),(.09,.10,10.0),metal,.025)

# Keep every object in the stable exported collection and restore stable selection.
for ob in list(bpy.context.selected_objects): ob.select_set(False)
root_obj.select_set(True); bpy.context.view_layer.objects.active=root_obj
scene.render.engine='BLENDER_EEVEE'
scene.view_settings.view_transform='Standard'
scene.view_settings.look='Medium High Contrast'
scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=os.path.join(OUT,'phi_gamma_delta_south_oblique.png')
scene.render.film_transparent=False
scene.render.resolution_percentage=70
world=scene.world or bpy.data.worlds.new('PhiGam_Render_World'); scene.world=world
world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(.55,.62,.72,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.3

# Render camera from south-west, matching the publicly documented front facade.
cam_data=bpy.data.cameras.new('PhiGam_Southwest_Review_Camera')
cam=bpy.data.objects.new('PhiGam_Southwest_Review_Camera',cam_data); scene.collection.objects.link(cam)
cam.location=(-455,365,24); target=Vector((-430,410,5.5)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
cam_data.lens=52; scene.camera=cam
light_data=bpy.data.lights.new('PhiGam_Soft_Sun','AREA'); light=bpy.data.objects.new('PhiGam_Soft_Sun',light_data)
scene.collection.objects.link(light); light.location=(-450,370,36); light_data.energy=1300; light_data.shape='DISK'; light_data.size=25
light.rotation_euler=(Vector((-430,410,4))-light.location).to_track_quat('-Z','Y').to_euler()

bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.render.render(write_still=True)

# Second view checks the low Lyles wing's arched glazing and the roof inset.
cam.location=(-399,447,17); target=Vector((-429,413,4.8))
cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
light.location=(-398,450,30); light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=os.path.join(OUT,'phi_gamma_delta_northeast_oblique.png')
bpy.ops.render.render(write_still=True)

# The inspection rig is temporary: deliver a clean reusable building library.
for ob in (cam, light): bpy.data.objects.remove(ob, do_unlink=True)
scene.camera=None
bpy.ops.wm.save_as_mainfile(filepath=ASSET)

# Write measurements and high-level provenance for fresh-open validation.
report={'asset':ASSET,'scene':SCENE_NAME,'collection':COLLECTION_NAME,'root_object':'House_301837281',
        'fid':787,'retained_outline_vertices':len(outline),'wall_footprint_source':'existing GIS-derived mesh coordinates; no XY change',
        'upper_mass_layout':'west and south high arms plus northeast low addition; modeled to preserve open GIS inset',
        'main_eave_m':MAIN_EAVE,'estimated_ridge_m':MAIN_RIDGE,'addition_eave_m':ADDITION_EAVE,
        'objects_in_export_collection':len(asset_col.objects),'render':scene.render.filepath,
        'uncertainties':['Facade window spacing estimated from official oblique construction photo; no surveyed elevations found.',
        'Main/addition separation inferred from official 2025 plan shaded existing-house area and 2024 architect concept rendering.',
        'Which GIS outline arm belongs to the historic house versus the Lyles Addition is not explicitly tagged; the selected northeast-lower split is an estimate.',
        'Roof pitch and story heights estimated; GIS height/story fields are stale and conflict with direct imagery.',
        'No interior geometry modeled: first-floor plan establishes rooms but registration/orientation relative to GIS roof rings is not verified; basement and first-floor PDFs do not establish upper floors.']}
with open(os.path.join(OUT,'geometry_build_report.json'),'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print('BUILD_DONE',json.dumps(report))
