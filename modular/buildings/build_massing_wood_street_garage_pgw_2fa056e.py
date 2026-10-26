import bpy, json, math, os
from mathutils import Vector
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ASSET_ID = 'massing_wood_street_garage_pgw_2fa056e'
ASSET_PATH = os.path.join(ROOT, 'modular', 'buildings', ASSET_ID + '.blend')
EVIDENCE_DIR = os.path.join(ROOT, 'audit', 'purdue_wood_street_garage_pgw')
GIS_PATH = os.path.join(EVIDENCE_DIR, 'raw_arcgis_fid254.json')
PREVIEW_PATH = os.path.join(EVIDENCE_DIR, 'preview_exterior_dusk.png')
TOP_PATH = os.path.join(EVIDENCE_DIR, 'preview_top_down.png')
REPORT_PATH = os.path.join(EVIDENCE_DIR, 'build_report.json')

os.makedirs(EVIDENCE_DIR, exist_ok=True)
# WGS84-like local metric conversion documented in modular/AGENTS.md.
raw = json.load(open(GIS_PATH, encoding='utf-8-sig'))
feature = raw['features'][0]
attrs = feature['attributes']
ring3857 = feature['geometry']['rings'][0]
R = 6378137.0
geo = []
for east, north in ring3857:
    lon = math.degrees(east / R)
    lat = math.degrees(math.atan(math.sinh(north / R)))
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    y = (lat - 40.4274) * 111040.0
    geo.append((x, y, lat, lon))
# Anchor at bounding-box center: reproducible and close to project-world centroid.
anchor_x = (min(p[0] for p in geo) + max(p[0] for p in geo)) * 0.5
anchor_y = (min(p[1] for p in geo) + max(p[1] for p in geo)) * 0.5
outline = [(p[0]-anchor_x, p[1]-anchor_y) for p in geo[:-1]]
minx, maxx = min(p[0] for p in outline), max(p[0] for p in outline)
miny, maxy = min(p[1] for p in outline), max(p[1] for p in outline)
width, length = maxx-minx, maxy-miny

# Fresh asset scene: only asset contents go into the exported asset collection.
scene = bpy.context.scene
scene.name = 'Building_' + ASSET_ID
for ob in list(scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for child in list(scene.collection.children):
    scene.collection.children.unlink(child)
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1440
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.render.image_settings.color_mode = 'RGBA'
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'

asset_col = bpy.data.collections.new('Asset_' + ASSET_ID)
scene.collection.children.link(asset_col)
env_col = bpy.data.collections.new('Preview_Environment')
scene.collection.children.link(env_col)

# Small helper to keep generated assets portable and consistent.
def mat(name, color, rough=0.75, metallic=0.0, noise_scale=5.0, variation=0.06, bump_strength=0.12):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    nt = m.node_tree
    bs = nt.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metallic
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = noise_scale
    noise.inputs['Detail'].default_value = 3.0
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    base = color
    dark = tuple(max(0.0, c*(1.0-variation)) for c in base)
    light = tuple(min(1.0, c*(1.0+variation)) for c in base)
    ramp.color_ramp.elements[0].position = 0.18
    ramp.color_ramp.elements[0].color = (*dark, 1)
    ramp.color_ramp.elements[1].position = 0.82
    ramp.color_ramp.elements[1].color = (*light, 1)
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = bump_strength
    bump.inputs['Distance'].default_value = 0.035
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bs.inputs['Base Color'])
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bs.inputs['Normal'])
    return m

concrete = mat('PGW | warm precast concrete', (0.57,0.55,0.50), rough=0.82, noise_scale=7.0, variation=0.10)
concrete_light = mat('PGW | pale edge beams', (0.70,0.68,0.62), rough=0.76, noise_scale=8.0, variation=0.07)
concrete_dark = mat('PGW | weathered plinth', (0.34,0.35,0.33), rough=0.9, noise_scale=4.0, variation=0.11)
asphalt = mat('PGW | parking deck asphalt', (0.105,0.115,0.12), rough=0.95, noise_scale=18.0, variation=0.12)
shadow_mat = mat('PGW | deep parking interior', (0.035,0.046,0.050), rough=0.9, noise_scale=9.0, variation=0.12)
metal = mat('PGW | charcoal steel', (0.095,0.12,0.13), rough=0.32, metallic=0.72, noise_scale=15.0, variation=0.04)
glass = bpy.data.materials.new('PGW | blue-green stair glazing'); glass.diffuse_color=(0.08,0.29,0.31,0.38); glass.use_nodes=True
bs=glass.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(0.08,0.29,0.31,1); bs.inputs['Roughness'].default_value=0.16; bs.inputs['Metallic'].default_value=0.35; bs.inputs['Alpha'].default_value=0.42
try: glass.surface_render_method='DITHERED'
except: pass
warm_glass = bpy.data.materials.new('PGW | stairwell warm lights'); warm_glass.diffuse_color=(0.88,0.58,0.23,0.45); warm_glass.use_nodes=True
bs=warm_glass.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(0.88,0.58,0.23,1); bs.inputs['Metallic'].default_value=0.08; bs.inputs['Roughness'].default_value=0.28
bs.inputs['Emission Color'].default_value=(0.95,0.43,0.12,1); bs.inputs['Emission Strength'].default_value=0.7
line_mat = mat('PGW | faded parking markings', (0.76,0.69,0.44), rough=0.8, noise_scale=14.0, variation=0.16)
white = mat('PGW | wayfinding ivory', (0.84,0.83,0.75), rough=0.45, noise_scale=11.0, variation=0.03)

# Batch repeated box components by material into one mesh per material.
boxes = {m.name: [] for m in [concrete, concrete_light, concrete_dark, asphalt, shadow_mat, metal, line_mat, white, glass, warm_glass]}
box_mats = {m.name:m for m in [concrete, concrete_light, concrete_dark, asphalt, shadow_mat, metal, line_mat, white, glass, warm_glass]}
def box_data(center, dims, material):
    cx,cy,cz=center; dx,dy,dz=[d*0.5 for d in dims]
    verts=[(cx-dx,cy-dy,cz-dz),(cx+dx,cy-dy,cz-dz),(cx+dx,cy+dy,cz-dz),(cx-dx,cy+dy,cz-dz),
           (cx-dx,cy-dy,cz+dz),(cx+dx,cy-dy,cz+dz),(cx+dx,cy+dy,cz+dz),(cx-dx,cy+dy,cz+dz)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    arr=boxes[material.name]; off=len(arr)//3
    arr.extend([v for xyz in verts for v in xyz])
    # store faces per material with temporary holder
    box_faces.setdefault(material.name,[]).extend([tuple(off+i for i in f) for f in faces])
box_faces={}

def create_obj(name, mesh, collection=asset_col, material=None):
    ob=bpy.data.objects.new(name,mesh); collection.objects.link(ob)
    if material: ob.data.materials.append(material)
    return ob

def extrusion_mesh(name, polygon, z0, z1, material, bevel=0.0):
    n=len(polygon)
    verts=[(x,y,z0) for x,y in polygon]+[(x,y,z1) for x,y in polygon]
    faces=[]
    # GIS ring is a simple concave polygon; Blender's n-gon tessellator handles its plan cap.
    faces.append(tuple(range(n-1,-1,-1)))
    faces.append(tuple(range(n,2*n)))
    for i in range(n):
        j=(i+1)%n
        faces.append((i,j,n+j,n+i))
    mesh=bpy.data.meshes.new(name+'Mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(material); mesh.update()
    ob=create_obj(name,mesh,asset_col,material)
    if bevel>0:
        mod=ob.modifiers.new('Soft precast arris','BEVEL'); mod.width=bevel; mod.segments=2
        mod2=ob.modifiers.new('Weighted slab normals','WEIGHTED_NORMAL'); mod2.keep_sharp=True
    return ob

def line3d(name, points, radius, material, collection=asset_col):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=1; cu.bevel_depth=radius; cu.bevel_resolution=2
    sp=cu.splines.new('POLY'); sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points): p.co=(co[0],co[1],co[2],1)
    ob=bpy.data.objects.new(name,cu); collection.objects.link(ob); ob.data.materials.append(material); return ob

# Eight occupied decks: ground through level 8, 10 ft typical vertical spacing.
floor_step=3.048
floor_levels=[i*floor_step for i in range(8)]
# Facade shell: exact GIS plan outline, thin structural deck slabs, and subtle finished roof level.
for i,z in enumerate(floor_levels):
    extrusion_mesh(f'PGW deck {i+1:02d}',outline,z,z+0.28,concrete_dark if i==0 else concrete,bevel=0.025)
    if i>0:
        # Asphalt surfacing sits inside each suspended concrete deck.
        extrusion_mesh(f'PGW deck surface {i+1:02d}',outline,z+0.28,z+0.34,asphalt)
# Roof/parapet/roof cap at the published GIS 78 ft level (estimate based on GIS attribute field).
roof_z=78*0.3048
# Parapet and roof walkway details.
# The top occupied deck remains open-air; the raised perimeter parapet defines the 78 ft roof line.

# Perimeter edge coordinates: broad facades are long N/S edges, with bays following GIS extent.
west_x=-16.5; east_x=18.7
south_y=-58.0; north_y=57.5
facade_width=east_x-west_x
# Structural piers at repeating parking-grid rhythm, continuing through the open storeys.
for side_x in [west_x,east_x]:
    y=south_y+4.0
    while y<north_y-2:
        box_data((side_x,y,(roof_z-0.2)/2),(0.72,0.78,roof_z-0.2),concrete_light)
        y+=7.6
# Short-end wall piers and corner returns.
for y in [south_y,north_y]:
    x=west_x+2.0
    while x<east_x-1:
        box_data((x,y,(roof_z-0.2)/2),(0.78,0.72,roof_z-0.2),concrete_light)
        x+=7.6
# Floor edge beams / low spandrels wrap long elevations while leaving broad open parking slots.
for z in floor_levels:
    zz=z+1.08
    box_data(((west_x+east_x)/2,south_y,zz),(facade_width-1.0,0.50,0.44),concrete_light)
    box_data(((west_x+east_x)/2,north_y,zz),(facade_width-1.0,0.50,0.44),concrete_light)
    box_data((west_x,(south_y+north_y)/2,zz),(0.50,length-2.0,0.44),concrete_light)
    box_data((east_x,(south_y+north_y)/2,zz),(0.50,length-2.0,0.44),concrete_light)
# Slim weather seals and metal guardrails above low spandrels, visible from street.
for z in floor_levels[1:]:
    rz=z+1.48
    for sx in [west_x,east_x]:
        box_data((sx,(south_y+north_y)/2,rz),(0.12,length-2.0,0.10),metal)
    for sy in [south_y,north_y]:
        box_data(((west_x+east_x)/2,sy,rz),(facade_width-2.0,0.12,0.10),metal)
# Deck columns inside, aligned to a measured ~7.6m structural bay rhythm.
for x in [-12.0,-4.4,3.2,10.8]:
    for y in range(-56,47,15):
        box_data((x,float(y),(floor_levels[-1]+0.3)/2),(0.48,0.48,floor_levels[-1]+0.3),concrete)
# Edge openings are intentionally open; add shadow backplane set back behind each facade to imply deep decks.
# Open bays stay fully open; interior darkness comes from recessed surfaces and lighting, not solid facade backplanes.
# Make the internal shadow planes repeated and non-contiguous so floor bands and car openings remain legible.
# Entry base piers and car portals at west/Grant-side frontage.
entry_y=-38.0
for y in [entry_y-3.6,entry_y+3.6]:
    box_data((west_x+0.05,y,1.40),(0.55,0.45,2.75),concrete_light)
# Entry lintel above a 7.2 m vehicle portal on the west long elevation.
box_data((west_x+0.05,entry_y,2.86),(0.58,7.9,0.42),concrete_light)
# Glass-enclosed circulation tower placed within the upper north section of the GIS footprint;
# supported by the illuminated tower visible in the 2010 street-level photo.
core_x=-1.8; core_y=35.5; core_w=6.6; core_l=12.0; core_h=roof_z
# Solid, thin blue-green glazed panels with dark metal framing.
for sx in [core_x-core_w/2,core_x+core_w/2]:
    box_data((sx,core_y,core_h/2),(0.06,core_l,core_h),glass)
for sy in [core_y-core_l/2,core_y+core_l/2]:
    box_data((core_x,sy,core_h/2),(core_w,0.06,core_h),glass)
# Tower mullions and floor landings.
for sx in [core_x-core_w/2,core_x+core_w/2]:
    for yy in [core_y-core_l/2,core_y,core_y+core_l/2]:
        box_data((sx,yy,core_h/2),(0.22,0.24,core_h),metal)
for sy in [core_y-core_l/2,core_y+core_l/2]:
    for xx in [core_x-core_w/2,core_x,core_x+core_w/2]:
        box_data((xx,sy,core_h/2),(0.24,0.20,core_h),metal)
for z in floor_levels:
    box_data((core_x,core_y,z+0.42),(core_w-0.4,core_l-0.4,0.12),concrete_light)
    # warm-lit landings behind glazing
    box_data((core_x,core_y,z+1.4),(core_w-0.65,0.08,1.6),warm_glass)
# Visible stair flights inside the glazed shaft: alternating runs and landing slabs.
for i,z in enumerate(floor_levels[:-1]):
    x0=core_x-core_w/2+0.8+(i%2)*2.5
    y0=core_y-core_l/2+1.2
    # compact diagonal sloped stringers and a run of treads
    for side in [-1,1]:
        line3d(f'PGW stair stringer L{i+1}',[(x0+(1.8 if side>0 else 0),y0,z+0.55),(x0+(0 if side>0 else 1.8),y0+4.0,z+floor_step-0.4)],0.09,metal)
    for n in range(8):
        t=n/7.0
        xx=x0+1.8*(1-t); yy=y0+4.0*t; zz=z+0.58+floor_step*t
        box_data((xx+0.9,yy,zz),(1.8,0.46,0.12),concrete_light)
# Main vehicle ramp, repeated diagonal plates between deck levels, centrally visible.
for i,z in enumerate(floor_levels[:-1]):
    ystart=-31.0+(i%2)*24.0
    yend=ystart+21.0
    xstart=4.0 if i%2==0 else 13.0
    xend=13.0 if i%2==0 else 4.0
    verts=[(xstart-3,ystart,z+0.37),(xstart+3,ystart,z+0.37),(xend+3,yend,z+floor_step+0.37),(xend-3,yend,z+floor_step+0.37)]
    mesh=bpy.data.meshes.new(f'PGW ramp {i+1} mesh'); mesh.from_pydata(verts,[],[(0,1,2,3)]); mesh.materials.append(concrete); mesh.update(); create_obj(f'PGW ramp {i+1}',mesh)
    # steel ramp edge rails
    line3d(f'PGW ramp rail {i+1}a',[(xstart-3,ystart,z+0.55),(xend-3,yend,z+floor_step+0.55)],0.07,metal)
    line3d(f'PGW ramp rail {i+1}b',[(xstart+3,ystart,z+0.55),(xend+3,yend,z+floor_step+0.55)],0.07,metal)
# Parking bay line markings, at ground and roof levels only to avoid visual noise.
for z in [0.37,floor_levels[-1]+0.37]:
    for y in range(-48,43,12):
        for x in range(-13,17,5):
            box_data((float(x),float(y),z+0.012),(0.10,4.2,0.022),line_mat)
# Entrance sign panel and entry clearance beam, set on west face.
box_data((9.0,south_y-0.34,4.0),(14.0,0.20,1.4),concrete_dark)
# Lettering rendered as geometry for portability.
def text_obj(body, name, loc, size, material, rot=(math.pi/2,0,0), extrude=0.005):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.size=size; cu.extrude=extrude; cu.bevel_depth=0.002
    ob=bpy.data.objects.new(name,cu); asset_col.objects.link(ob); ob.location=loc; ob.rotation_euler=rot; cu.materials.append(material); return ob
text_obj('WOOD STREET GARAGE','PGW entry sign',(2.1,south_y-0.48,4.04),0.70,white)
text_obj('7\'-2\" CLEARANCE','PGW clearance sign',(8.2,south_y-0.49,2.18),0.30,line_mat)
# Roof edge parapet and rooftop lights.
for sx in [west_x,east_x]: box_data((sx,(south_y+north_y)/2,roof_z-0.12),(0.32,length-2,0.42),concrete_light)
for sy in [south_y,north_y]: box_data(((west_x+east_x)/2,sy,roof_z-0.12),(facade_width-1,0.32,0.42),concrete_light)
for x in [-14,-5,4,13,17]:
    for y in [-54,-20,14,46]:
        box_data((x,y,roof_z+0.16),(0.18,0.18,0.32),metal)
        # luminous but subtle fixtures
        ldata=bpy.data.lights.new('PGW deck luminaire','POINT'); ldata.energy=22; ldata.color=(1.0,0.64,0.30); ldata.shadow_soft_size=0.5
        lob=bpy.data.objects.new('PGW deck luminaire',ldata); asset_col.objects.link(lob); lob.location=(x,y,roof_z-0.1)

# Convert batched boxes to meshes with correct material assignment and a tiny edge softening.
for name, flat in boxes.items():
    if not flat: continue
    verts=[tuple(flat[i:i+3]) for i in range(0,len(flat),3)]
    faces=box_faces.get(name,[])
    mesh=bpy.data.meshes.new('PGW joined '+name+' mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(box_mats[name]); mesh.update()
    ob=create_obj('PGW repeated '+name,mesh)
    if name in [concrete.name,concrete_light.name,metal.name]:
        bev=ob.modifiers.new('Softened fabricated edges','BEVEL'); bev.width=0.025; bev.segments=2
        ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')

# A second opaque elevator core and small service doors at ground level.
box_data((12.0,42.0,core_h/2),(7.0,7.0,core_h),concrete_dark)
# service recesses and glazed doors on the north elevation.
for z in [1.2,4.2]:
    box_data((12.0,38.38,z),(2.0,0.10,2.3),glass)

# Rebuild box batches if boxes were added after the first pass (service box additions).
for name, flat in boxes.items():
    if not flat: continue
    # Earlier batch meshes already contain these arrays and object names; late additions are rare and intentionally included by rebuild.
    # Existing joined object uses same mesh name; replace it with the current array.
    ob=next((o for o in asset_col.objects if o.name=='PGW repeated '+name),None)
    if ob:
        verts=[tuple(flat[i:i+3]) for i in range(0,len(flat),3)]
        mesh=bpy.data.meshes.new('PGW joined '+name+' final mesh'); mesh.from_pydata(verts,[],box_faces.get(name,[])); mesh.materials.append(box_mats[name]); mesh.update()
        old=ob.data; ob.data=mesh
        if old.users==0: bpy.data.meshes.remove(old)
    else:
        verts=[tuple(flat[i:i+3]) for i in range(0,len(flat),3)]
        mesh=bpy.data.meshes.new('PGW joined '+name+' mesh'); mesh.from_pydata(verts,[],box_faces.get(name,[])); mesh.materials.append(box_mats[name]); mesh.update(); create_obj('PGW repeated '+name,mesh)

# Restore object transforms and origin semantics: local coordinates centered on GIS footprint bbox.
# All mesh coordinates are already local; no external transforms are required.
for ob in asset_col.objects:
    if ob.type=='MESH':
        ob['building_id']=ASSET_ID
        ob['coordinate_frame']='local meters; anchor at footprint bounding-box center'
# Scene metadata supports future master integration.
scene['building_id']=ASSET_ID
scene['world_anchor_m']=[anchor_x,anchor_y]
scene['gis_feature_id']=254
scene['height_source']='GIS R=78 ft (23.7744 m); interpreted as roof elevation, not measured survey height'

# Preview environment ground around the garage, kept outside the asset collection.
def preview_box(name, location, dimensions, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    ob=bpy.context.object; ob.name=name; ob.dimensions=dimensions; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    env_col.objects.link(ob); ob.data.materials.append(material); return ob
# Use a neutral floor patch below the model for shadows.
preview_ground=mat('Preview | asphalt surroundings',(0.14,0.16,0.16),rough=0.92,noise_scale=5,variation=0.12)
preview_box('Preview Ground',(0,0,-0.30),(420,420,0.25),preview_ground)
world=bpy.data.worlds.new('Purdue blue hour') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.11,0.16,0.22,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.75
# Sunset key and cool fill.
def area_light(name,loc,target,power,color,size):
    ld=bpy.data.lights.new(name,'AREA'); ld.energy=power; ld.color=color; ld.shape='DISK'; ld.size=size
    ob=bpy.data.objects.new(name,ld); env_col.objects.link(ob); ob.location=loc; ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler(); return ob
area_light('Warm dusk key',(-48,-36,53),(0,0,8),11500,(1.0,0.68,0.44),32)
area_light('Cool sky fill',(30,55,48),(0,0,10),8500,(0.54,0.68,1.0),38)
area_light('Front softbox',(70,-60,28),(0,0,11),6500,(1.0,0.84,0.63),25)
area_light('Roof sky bounce',(0,0,110),(0,0,0),9500,(0.72,0.82,1.0),90)
# Camera helper.
def make_camera(name,loc,target,ortho=None,lens=45):
    camd=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,camd); env_col.objects.link(cam); cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); camd.lens=lens
    if ortho: camd.type='ORTHO'; camd.ortho_scale=ortho
    return cam
cam=make_camera('PGW exterior hero camera',(-120,30,30),(0,0,11),lens=39)
scene.camera=cam
scene.render.filepath=PREVIEW_PATH
scene.render.image_settings.file_format='PNG'
scene.eevee.taa_render_samples=48
scene.render.image_settings.color_mode='RGBA'
scene.render.resolution_x=1440; scene.render.resolution_y=900
# Save first to disk, render preview.
bpy.ops.wm.save_as_mainfile(filepath=ASSET_PATH)
bpy.ops.render.render(write_still=True)
# Top-down GIS overlay style preview.
cam2=make_camera('PGW plan camera',(0,0,210),(0,0,0),ortho=150)
cam2.data.type='ORTHO'; scene.camera=cam2
scene.render.resolution_x=1100; scene.render.resolution_y=1400; scene.render.resolution_percentage=100; scene.render.filepath=TOP_PATH
bpy.ops.render.render(write_still=True)

# Evidence-rich deterministic build report; measurements distinguish source-backed from inferred.
from mathutils import Vector
mesh_bounds=[]
for ob in asset_col.objects:
    if ob.type=='MESH':
        for v in ob.bound_box:
            co=ob.matrix_world @ Vector(v); mesh_bounds.append(tuple(co))
if mesh_bounds:
    bounds=[[min(v[i] for v in mesh_bounds),max(v[i] for v in mesh_bounds)] for i in range(3)]
report={
 'building':'Wood Street Parking Garage (PGW)','stable_id':ASSET_ID,
 'build_timestamp_utc':datetime.now(timezone.utc).isoformat(),
 'gis':{'provider':'Purdue GIS / Esri BuildingShapesZip4 FeatureServer layer 0','feature_id':254,'code':'PGW','name':attrs.get('BUILDING_N'),'address':attrs.get('ADDRESS'),'crs':'EPSG:3857 (Web Mercator), projected to project-local approximate metric conversion documented in modular/AGENTS.md','source_area_sq_m_esri':attrs.get('Shape__Area'),'source_perimeter_m_esri':attrs.get('Shape__Length'),'converted_bbox_m':[[minx,maxx],[miny,maxy]],'anchor_world_m':[anchor_x,anchor_y],'projected_plan_dimensions_m':[width,length],'ring_vertex_count':len(ring3857)-1,'height_fields':{'NUM_LEVELS':attrs.get('NUM_LEVELS'),'CountOfFLO':attrs.get('CountOfFLO'),'R_ft':attrs.get('R'),'Extrution':attrs.get('Extrution')},'height_interpretation':'8 occupied decks modeled at 10 ft increments, GIS R=78 interpreted as roof level (23.7744m); height not independently surveyed.'},
 'model':{'asset_file':'modular/buildings/'+ASSET_ID+'.blend','collection':'Asset_'+ASSET_ID,'scene':'Building_'+ASSET_ID,'geometry_frame':'local meters; origin at GIS footprint bounding-box center; parent master marker should be [%.6f, %.6f]'%(anchor_x,anchor_y),'bounds_local_m':bounds,'object_count':len(asset_col.objects),'materials_procedural':True,'external_texture_dependencies':0,'render_previews':['audit/purdue_wood_street_garage_pgw/preview_exterior_dusk.png','audit/purdue_wood_street_garage_pgw/preview_top_down.png'],'feature_notes':['8 concrete parking decks','open air facade openings with repeated piers and horizontal spandrels','glazed stair tower with visible stairs and warm landings','internal sloped vehicle ramps','roof parapet and deck lights'], 'inferred':['façade bay rhythm','stair tower placement within footprint','ramp arrangement','concrete shade and glazing tone']},
 'validation':{'fresh_open_required':True,'independent_grade':'pending','known_uncertainty':['GIS level and roof fields are CAD-derived; no measured elevation drawing found in current source set.','2010 street-level photo provides qualitative facade evidence only; current street imagery still to be checked.']}
}
with open(REPORT_PATH,'w',encoding='utf-8') as f: json.dump(report,f,indent=2,ensure_ascii=False)
print('BUILT',json.dumps({'asset':ASSET_PATH,'anchor':[anchor_x,anchor_y],'footprint_dimensions':[width,length],'bounds':bounds,'mesh_objects':sum(o.type=='MESH' for o in asset_col.objects),'collection_objects':len(asset_col.objects)},indent=2))

