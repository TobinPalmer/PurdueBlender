import bpy, json, math, os
from pathlib import Path
from mathutils import Vector, Quaternion

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = 'massing_hampton_hall_of_civil_engineering_hamp_9715f0e'
ASSET_COLLECTION = 'Asset_' + ASSET_ID
SCENE_NAME = 'Building_' + ASSET_ID
AUDIT = ROOT / 'audit' / ASSET_ID
RENDERS = AUDIT / 'renders'
MANIFEST = ROOT / 'modular' / 'manifest.json'
REFS = ROOT / 'audit' / 'official_building_references.json'
ASSET_PATH = ROOT / 'modular' / 'buildings' / (ASSET_ID + '.blend')

# The official campus-map ring is stored in the repository using its documented local
# approximation. It is not surveyed ground truth; retain it at native scale.
ref = json.loads(REFS.read_text(encoding='utf-8'))
hamp = next(b for b in ref['buildings'] if b['code'] == 'HAMP')
ring = [tuple(p) for p in hamp['rings_xy_m'][0][:-1]]
center = Vector((sum(p[0] for p in ring)/len(ring), sum(p[1] for p in ring)/len(ring), 0))
area = sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring))) / 2
# polygon offset in this world ring orientation
orient = 1 if area > 0 else -1

# Keep the manifest collection and scene contract stable. Rebuild only this library.
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for coll in list(bpy.data.collections):
    bpy.data.collections.remove(coll)
scene = bpy.context.scene
scene.name = SCENE_NAME
asset = bpy.data.collections.new(ASSET_COLLECTION)
scene.collection.children.link(asset)
support = bpy.data.collections.new('HAMP_Render_Support')
scene.collection.children.link(support)

# Color palette based on Purdue's official exterior photograph and facade evidence.
def mat(name, color, rough=0.8, metallic=0.0):
    m = bpy.data.materials.new(name); m.diffuse_color = (*color,1)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (*color,1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metallic
    return m
brick = mat('HAMP warm red brick', (0.48,0.18,0.12), .88)
stone = mat('HAMP pale limestone and precast', (0.69,0.64,0.53), .82)
glass = mat('HAMP blue gray glazing', (0.14,0.30,0.34), .28, .12)
dark = mat('HAMP charcoal roof and shadow', (0.24,0.26,0.26), .85)
metal = mat('HAMP dark bronze metal', (0.12,0.14,0.14), .42, .55)
white = mat('HAMP ivory lettering', (0.88,0.82,0.66), .65)

# Create a watertight official GIS envelope prism as the building's primary mass.
# Mesh caps use the exact map ring; height is an estimate based on five above-grade
# levels at approximately 3.45 m each. GIS Extrution/R fields are deliberately not used.
z_ground, z_roof = 0.0, 17.25
n = len(ring)
verts = [(x,y,z_ground) for x,y in ring] + [(x,y,z_roof) for x,y in ring]
faces = [tuple(reversed(range(n))), tuple(range(n,2*n))]
faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
mesh = bpy.data.meshes.new('HAMP official campus-map plan prism')
mesh.from_pydata(verts, [], faces); mesh.materials.append(brick); mesh.materials.append(dark); mesh.update()
for p in mesh.polygons:
    p.material_index = 1 if p.index == 1 else 0
shell = bpy.data.objects.new('HAMP primary masonry envelope (estimated 5 above-grade levels)', mesh)
asset.objects.link(shell)
shell['source_footprint'] = 'Official Purdue campus-map BuildingShapesZip4 FID 272 / HAMP'
shell['footprint_uncertainty'] = 'Map polygon, not a certified survey; local X/Y use project conversion.'
shell['height_status'] = 'Estimated: 5 above-grade levels x 3.45 m; not measured.'
shell['source_levels'] = 'Official Purdue HAMP safety report describes basement, ground, main/first, second, third, fourth.'

# Helpers for thin facade details aligned to every qualifying outer wall segment.
def link_mesh(name, vertices, polys, material, collection=asset):
    me=bpy.data.meshes.new(name+' mesh'); me.from_pydata(vertices, [], polys); me.materials.append(material); me.update()
    ob=bpy.data.objects.new(name, me); collection.objects.link(ob); return ob

def facade_box(name, p0, tangent, outward, s0, s1, z0, z1, depth, material):
    # p0 is a point on the wall baseline; surface sits slightly outside the masonry.
    q0 = Vector((p0[0],p0[1],0)) + tangent*s0 + outward*0.065
    q1 = Vector((p0[0],p0[1],0)) + tangent*s1 + outward*0.065
    front0=q0+outward*depth; front1=q1+outward*depth
    v=[(q0.x,q0.y,z0),(q1.x,q1.y,z0),(q1.x,q1.y,z1),(q0.x,q0.y,z1),
       (front0.x,front0.y,z0),(front1.x,front1.y,z0),(front1.x,front1.y,z1),(front0.x,front0.y,z1)]
    f=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    ob=link_mesh(name,v,f,material)
    ob['feature_method']='Facade detail placed against source-aligned GIS envelope; sizes are schematic.'
    return ob

# Facade bays: glazing repeats on long straight faces; limestone pilasters and sill/header
# strips follow the vertical-rhythm seen in Purdue's HAMP facade photograph.
facade_edges=[]
for i,p in enumerate(ring):
    q=ring[(i+1)%n]
    dx,dy=q[0]-p[0],q[1]-p[1]; length=math.hypot(dx,dy)
    if length < 7.0: continue
    t=Vector((dx/length,dy/length,0))
    outward=Vector((orient*t.y,-orient*t.x,0))
    facade_edges.append((p,q,length,t,outward))
    # Floor rhythm derived as an architectural representation, not surveyed levels.
    bay=3.8
    windows=max(1,int((length-1.0)//bay))
    span=(length-1.0)/windows
    for k in range(windows):
        c=(k+.5)*span+.5
        w=min(1.65,span*.52)
        left,right=c-w/2,c+w/2
        for level in range(5):
            base=.42+level*3.45
            bottom=base+.64; top=base+2.73
            # tall dark glazing and pale surround on each full visible story
            facade_box(f'HAMP window glazing edge{i+1} bay{k+1} level{level+1}',p,t,outward,left+.10,right-.10,bottom,top,.075,glass)
            facade_box(f'HAMP pale jamb edge{i+1} bay{k+1} L level{level+1}',p,t,outward,left-.02,left+.10,bottom-.09,top+.09,.11,stone)
            facade_box(f'HAMP pale jamb edge{i+1} bay{k+1} R level{level+1}',p,t,outward,right-.10,right+.02,bottom-.09,top+.09,.11,stone)
            facade_box(f'HAMP pale head edge{i+1} bay{k+1} level{level+1}',p,t,outward,left-.02,right+.02,top,top+.12,.12,stone)
            facade_box(f'HAMP pale sill edge{i+1} bay{k+1} level{level+1}',p,t,outward,left-.02,right+.02,bottom-.12,bottom,.12,stone)
    # floor and roof horizontal cornice lines on long wall faces
    for level in range(1,5):
        z=level*3.45
        facade_box(f'HAMP floor belt edge{i+1} level{level}',p,t,outward,.15,length-.15,z-.07,z+.07,.13,stone)
    facade_box(f'HAMP roof cornice edge{i+1}',p,t,outward,.12,length-.12,z_roof-.28,z_roof,.20,stone)

# Approximate the publicly documented accessible ground entry as a single glass vestibule
# on the longest southwest-ish wall. Its exact campus-facing wall is not confirmed.
entry_edge=max(facade_edges,key=lambda e:e[2])
p,q,length,t,outward=entry_edge
entry_center=length*.50
facade_box('HAMP estimated accessible entry glazing',p,t,outward,entry_center-2.4,entry_center+2.4,.05,3.05,.18,glass)
for s in (entry_center-2.5,entry_center+2.5):
    facade_box('HAMP entry limestone pier',p,t,outward,s-.16,s+.16,0,3.45,.24,stone)
facade_box('HAMP entry stone canopy edge',p,t,outward,entry_center-3.0,entry_center+3.0,3.12,3.42,.65,stone)
# Door leaves and mullions
for center_s in (entry_center-.65,entry_center+.65):
    facade_box('HAMP entry door leaf',p,t,outward,center_s-.58,center_s+.58,.10,2.45,.22,glass)
facade_box('HAMP entrance sign backplate',p,t,outward,entry_center-2.8,entry_center+2.8,3.58,4.38,.12,brick)
# Add a text label on same wall; text object's +Z normal faces out.
mid=Vector((p[0],p[1],0))+t*entry_center+outward*.20
text_data=bpy.data.curves.new('HAMP sign lettering','FONT'); text_data.body='HAMPTON HALL\nCIVIL ENGINEERING'; text_data.size=.27; text_data.extrude=.003; text_data.align_x='CENTER'; text_data.align_y='CENTER'
sign=bpy.data.objects.new('HAMP entrance identification lettering (schematic)',text_data)
asset.objects.link(sign); sign.location=(mid.x,mid.y,3.88)
from mathutils import Matrix
orientation=Matrix(((t.x,0,outward.x),(t.y,0,outward.y),(0,1,0)))
sign.rotation_euler=orientation.to_euler(); sign.data.materials.append(white)
sign['detail_status']='Approximate readable sign based on official Purdue facade photograph; exact surveyed placement and wording layout unavailable.'

# Roof equipment volume, restrained and low; no unsupported decorative silhouette.
# Central flat roof with stepped mechanical penthouse approximate.
def cube(name,loc,scale,material,collection=asset):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); ob=bpy.context.object; ob.name=name; ob.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    # move from default scene collection to intended collection
    for c in list(ob.users_collection): c.objects.unlink(ob)
    collection.objects.link(ob); ob.data.materials.append(material); return ob
# Roof marker inside source outline's central interior; small, low, non-prominent.
cube('HAMP low roof mechanical penthouse estimate',(center.x,center.y,z_roof+.5),(8.0,5.0,1.0),dark)

# Batch repeated facade elements by material to keep the exported library light.
# These detail meshes are made at world-coordinate vertices with identity transforms.
for material in (stone, glass, brick):
    old=[o for o in asset.objects if o.type=='MESH' and o != shell and o.data.materials and o.data.materials[0] == material]
    if not old: continue
    vertices=[]; polygons=[]; offset=0
    for ob in old:
        matrix=ob.matrix_world.copy()
        vertices.extend([tuple(matrix @ v.co) for v in ob.data.vertices])
        polygons.extend([tuple(offset+i for i in poly.vertices) for poly in ob.data.polygons])
        offset += len(ob.data.vertices)
    me=bpy.data.meshes.new('HAMP '+material.name+' detail mesh')
    me.from_pydata(vertices,[],polygons); me.materials.append(material); me.update()
    batch=bpy.data.objects.new('HAMP '+material.name+' facade detail batch',me); asset.objects.link(batch)
    batch['batch_source_count']=len(old)
    for ob in old: bpy.data.objects.remove(ob,do_unlink=True)

# Render support, outside the exported asset collection.
def support_obj(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    support.objects.link(obj)
# Ground/reference slab for previews only.
# A plain matte base provides shadow contact without suggesting a surveyed plaza.
ground=cube('HAMP preview ground',(center.x,center.y,-.22),(170,170,.35),mat('HAMP preview neutral ground',(0.48,.50,.52),.95),support)
# Camera and lights target the full campus-coordinate envelope.
def aim(obj, target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('HAMP Preview Camera'); cam=bpy.data.objects.new('HAMP Preview Camera',cam_data); support.objects.link(cam); scene.camera=cam
cam.location=(center.x+145,center.y-175,105); aim(cam,Vector((center.x,center.y,z_roof*.50))); cam.data.type='ORTHO'; cam.data.ortho_scale=180
for name,loc,power,size in [('Key',(center.x+40,center.y-100,115),180000,90),('Fill',(center.x-100,center.y-20,80),140000,80),('Rim',(center.x+20,center.y+100,100),180000,70)]:
    ld=bpy.data.lights.new(name,'AREA'); lo=bpy.data.objects.new(name,ld); support.objects.link(lo); lo.location=loc; lo.data.energy=power; lo.data.shape='DISK'; lo.data.size=size; aim(lo,Vector((center.x,center.y,7)))
scene.render.engine='BLENDER_EEVEE'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.render.resolution_x=1400; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.world.use_nodes=True
scene.world.color=(.55,.58,.62)
world_bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
world_bg.inputs['Color'].default_value=(.55,.58,.62,1)
world_bg.inputs['Strength'].default_value=.75
scene.render.filepath=str(RENDERS/'exterior_axonometric.png')
# Save a complete model before preview rendering so a render-backend failure cannot lose it.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
scene.view_settings.view_transform='Standard'; scene.view_settings.look='None'; scene.view_settings.exposure=0; scene.view_settings.gamma=1
scene.render.image_settings.color_mode='RGBA'
scene.render.resolution_percentage=65
RENDERS.mkdir(parents=True,exist_ok=True)
bpy.ops.render.render(write_still=True)
# roof plan render: replace camera orientation only, preserving objects.
cam.location=(center.x,center.y,z_roof+210); aim(cam,Vector((center.x,center.y,0))); cam.data.ortho_scale=155
scene.render.filepath=str(RENDERS/'roof_plan.png'); bpy.ops.render.render(write_still=True)
# close front render for entrance and facade rhythm.
cam.location=(mid.x+outward.x*75,mid.y+outward.y*75,13); aim(cam,Vector((mid.x,mid.y,9))); cam.data.ortho_scale=70
scene.render.filepath=str(RENDERS/'entry_facade.png'); bpy.ops.render.render(write_still=True)
# Restore exterior view settings and save the portable modular asset.
cam.location=(center.x+145,center.y-175,105); aim(cam,Vector((center.x,center.y,z_roof*.50))); cam.data.ortho_scale=180
scene.render.resolution_percentage=100
# Ensure all material node data and meshes are local; no images or absolute linked dependencies.
for ob in asset.objects:
    ob['asset_id']=ASSET_ID
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
print(json.dumps({'asset':str(ASSET_PATH),'collection':ASSET_COLLECTION,'objects':len(asset.objects),'footprint_vertices':n,'signed_area_m2':area,'bounds':[[min(v.co[i] for o in asset.objects if o.type=='MESH' for v in o.data.vertices),max(v.co[i] for o in asset.objects if o.type=='MESH' for v in o.data.vertices)] for i in range(3)],'renders':[str(RENDERS/x) for x in ('exterior_axonometric.png','roof_plan.png','entry_facade.png')]}))
