"""Build 3rd and West from the project-cached OSM building footprint and public project evidence.
Run with Blender 4.5 from the repository root after opening the existing asset.
The footprint remains in campus coordinates; no transform or campus origin changes are made.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / 'modular' / 'buildings' / 'massing_3rd_and_west_ffa3d05.blend'
OSM = ROOT / 'audit' / 'massing_3rd_and_west_ffa3d05' / 'sources' / 'osm_way_1324500897_snapshot.json'
OUT = ROOT / 'audit' / 'massing_3rd_and_west_ffa3d05'
COLLECTION_NAME = 'Asset_massing_3rd_and_west_ffa3d05'
SCENE_NAME = 'Building_massing_3rd_and_west_ffa3d05'

with OSM.open(encoding='utf-8') as f: src = json.load(f)
way = src['way']; node_data = {n['id']:n for n in src['nodes']}
coords=[]
for nid in way['nodes'][:-1]:
    n=node_data[nid]
    lat,lon=float(n['lat']),float(n['lon'])
    x=(lon + 86.9137)*111412.84*math.cos(math.radians(40.4274))
    y=(lat - 40.4274)*111040.0
    coords.append((x,y))
assert len(coords)==14 and way['nodes'][0]==way['nodes'][-1]
# OSM outer ring is counter-clockwise in campus XY; its right-hand side normals point out.
area=sum(coords[i][0]*coords[(i+1)%len(coords)][1]-coords[(i+1)%len(coords)][0]*coords[i][1] for i in range(len(coords)))/2
assert area > 0, area

def mat(name, color, metallic=0.0, roughness=0.65):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Base Color'].default_value=(*color,1)
        bs.inputs['Metallic'].default_value=metallic
        bs.inputs['Roughness'].default_value=roughness
    return m

shell_mat=mat('3W | pale limestone facade',(0.48,0.50,0.47))
brick_mat=mat('3W | warm red brick',(0.32,0.12,0.08))
glass_mat=mat('3W | blue grey glazing',(0.025,0.07,0.09),0.15,0.28)
frame_mat=mat('3W | charcoal window frames',(0.035,0.04,0.045),0.25,0.38)
roof_mat=mat('3W | light roof and parapet',(0.40,0.42,0.40))

scene=bpy.context.scene
scene.name=SCENE_NAME
col=bpy.data.collections.get(COLLECTION_NAME)
if col is None:
    col=bpy.data.collections.new(COLLECTION_NAME); scene.collection.children.link(col)
for obj in list(col.objects): bpy.data.objects.remove(obj,do_unlink=True)

# 5 stories are supported by Purdue Research Foundation project material. A 3.6 m
# floor module is an estimate. The 18 m eave plus parapet is not surveyed height.
story_h=3.6
stories=5
eave=story_h*stories
parapet_h=0.9
# Side-wall prism with each story represented by separate faces for readable banding.
n=len(coords); verts=[]
for z in [0.0,eave]: verts.extend((x,y,z) for x,y in coords)
faces=[]; face_story=[]
faces.append(tuple(range(n-1,-1,-1))); face_story.append(-2)
faces.append(tuple(range(n,2*n))); face_story.append(-1)
for s in range(stories):
    lo=s*story_h; hi=(s+1)*story_h
    # use local ring pair for each floor for face material assignments
    base=len(verts)
    verts.extend((x,y,lo) for x,y in coords)
    verts.extend((x,y,hi) for x,y in coords)
    for i in range(n):
        j=(i+1)%n
        faces.append((base+i,base+j,base+n+j,base+n+i)); face_story.append(s)
mesh=bpy.data.meshes.new('3W exact OSM footprint extrusion'); mesh.from_pydata(verts,[],faces); mesh.update()
obj=bpy.data.objects.new('3rd and West | five story footprint shell',mesh); col.objects.link(obj)
for m in [shell_mat,brick_mat,roof_mat]: mesh.materials.append(m)
for p,tag in zip(mesh.polygons,face_story):
    if tag==-1: p.material_index=2
    elif tag==-2: p.material_index=0
    else: p.material_index=0

# Build repeated glazed openings on each OSM perimeter segment. These are facade
# rhythm proxies: one continuous apartment opening per approximate 3.1 m bay.
win_v=[];win_f=[];frame_v=[];frame_f=[]
def add_quad(store_v,store_f, points):
    b=len(store_v);store_v.extend(points);store_f.append((b,b+1,b+2,b+3))
def edge_points(a,b,t,z):
    return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, z)
def rect_surface(a,b,t0,t1,z0,z1,offset=0.10):
    dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy); nx=dy/L;ny=-dx/L
    return [tuple(edge_points(a,b,t,z)[k]+(nx*offset if k==0 else ny*offset if k==1 else 0) for k in range(3)) for t,z in [(t0,z0),(t1,z0),(t1,z1),(t0,z1)]]
for i,a in enumerate(coords):
    b=coords[(i+1)%n]; L=math.dist(a,b)
    if L < 5.0: continue
    bays=max(1,int(L/3.15))
    pitch=L/bays
    width=min(2.05,pitch*0.70)
    # keep a modest corner pier; exact bay spacing is illustrative
    for s in range(stories):
        zlo=s*story_h
        z0=zlo+(0.62 if s==0 else 1.02)
        z1=zlo+(3.05 if s==0 else 2.64)
        for k in range(bays):
            c=(k+0.5)/bays; dt=(width/L)/2
            t0=max(0.035,c-dt);t1=min(0.965,c+dt)
            add_quad(win_v,win_f,rect_surface(a,b,t0,t1,z0,z1,0.12))
            # slim perimeter rails and one central mullion
            rail=0.07; side=0.07/L
            for q in [
                rect_surface(a,b,t0,t1,z0,z0+rail,0.16),
                rect_surface(a,b,t0,t1,z1-rail,z1,0.16),
                rect_surface(a,b,t0,t0+side,z0,z1,0.16),
                rect_surface(a,b,t1-side,t1,z0,z1,0.16),
                rect_surface(a,b,c-0.05/L,c+0.05/L,z0,z1,0.17),
            ]: add_quad(frame_v,frame_f,q)

def mesh_obj(name,vertices,polygons,material):
    me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],polygons);me.update(); ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(material);return ob
mesh_obj('3rd and West | repeated dark glazing',win_v,win_f,glass_mat)
mesh_obj('3rd and West | window frames and mullions',frame_v,frame_f,frame_mat)

# Brick-clad corner/amenity accents visible in the Purdue opening photo. Their
# placement at opposite ends of the south courtyard wing is a visual proxy, not a surveyed plan.
south_edges=[(i,coords[i],coords[(i+1)%n],math.dist(coords[i],coords[(i+1)%n])) for i in range(n) if abs(coords[(i+1)%n][1]-coords[i][1])<1.4 and (coords[i][1]+coords[(i+1)%n][1])/2 < -80]
if south_edges:
    i,a,b,L=max(south_edges,key=lambda q:q[3])
    dx=b[0]-a[0];dy=b[1]-a[1];ll=math.hypot(dx,dy);nx=dy/ll;ny=-dx/ll
    for idx,fraction in enumerate((0.12,0.88),1):
        center=(a[0]+dx*fraction,a[1]+dy*fraction)
        mid=(center[0]+nx*0.10,center[1]+ny*0.10)
        bpy.ops.mesh.primitive_cube_add(size=1,location=(mid[0],mid[1],eave/2))
        tower=bpy.context.object;tower.name=f'3rd and West | brick amenity end {idx}';tower.dimensions=(min(13.0,L*0.24),0.28,eave+parapet_h)
        tower.rotation_euler[2]=math.atan2(dy,dx)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for c in list(tower.users_collection): c.objects.unlink(tower)
        col.objects.link(tower); tower.data.materials.append(brick_mat)

# Flat parapet represented as a low, restrained roof-edge volume around the silhouette.
# create narrow segments per edge using cubes, avoiding any change to the surveyed outline.
for i,a in enumerate(coords):
    b=coords[(i+1)%n];dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy)
    if L<0.5: continue
    nx=dy/L;ny=-dx/L
    mid=((a[0]+b[0])/2+nx*0.05,(a[1]+b[1])/2+ny*0.05)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(mid[0],mid[1],eave+parapet_h/2))
    ob=bpy.context.object;ob.name=f'3rd and West | parapet {i+1:02d}';ob.dimensions=(L+0.08,0.42,parapet_h);ob.rotation_euler[2]=math.atan2(dy,dx)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    col.objects.link(ob);ob.data.materials.append(roof_mat)

# Make asset-only render camera, lights and ground-free studio preview. These are
# outside the exported collection and will not be linked with the asset.
for name in ['3W Preview Camera','3W Preview Key','3W Preview Fill']:
    old=bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old,do_unlink=True)
center=Vector((sum(p[0] for p in coords)/n,sum(p[1] for p in coords)/n,eave/2))
cam_data=bpy.data.cameras.new('3W Preview Camera');cam=bpy.data.objects.new('3W Preview Camera',cam_data);scene.collection.objects.link(cam)
cam.location=(center.x-135,center.y-150,center.z+78);target=center;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam_data.type='ORTHO';cam_data.ortho_scale=160;scene.camera=cam
for name,loc,power,size in [('3W Preview Key',(center.x-60,center.y-100,120),7000,90),('3W Preview Fill',(center.x+60,center.y+40,90),3500,75)]:
    ld=bpy.data.lights.new(name,'AREA');lo=bpy.data.objects.new(name,ld);scene.collection.objects.link(lo);lo.location=loc;ld.energy=power;ld.shape='DISK';ld.size=size;lo.rotation_euler=(target-lo.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1300;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.render.filepath=str(OUT/'3rd_and_west_preview.png')
scene.world.color=(0.52,0.60,0.68)
scene.view_settings.view_transform='Standard'
scene.view_settings.look='Medium High Contrast'
scene.view_settings.exposure=-1.2
# temporary green courtyard/context surface for the preview only
ground_mat=mat('3W preview only | muted planting',(0.10,0.15,0.08))
bpy.ops.mesh.primitive_plane_add(size=220,location=(center.x,center.y,-0.12))
ground=bpy.context.object;ground.name='3W Preview Ground';ground.data.materials.append(ground_mat)
# camera/lights remain outside asset collection
scene.render.resolution_percentage=100
# Store the named library scene and single asset collection.
bpy.ops.render.render(write_still=True)
# Remove preview-only camera, lights, and ground before saving the portable library.
for name in ['3W Preview Camera','3W Preview Key','3W Preview Fill','3W Preview Ground']:
    ob=bpy.data.objects.get(name)
    if ob: bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
# quick machine-readable build metrics
bounds=[]
for ob in col.all_objects:
    if ob.type=='MESH':
        for corner in ob.bound_box: bounds.append(ob.matrix_world @ Vector(corner))
metrics={'asset':str(ASSET),'collection':COLLECTION_NAME,'story_count':stories,'story_height_estimate_m':story_h,'main_shell_eave_estimate_m':eave,'parapet_estimate_m':parapet_h,'bounds_world_m':[[min(v[k] for v in bounds),max(v[k] for v in bounds)] for k in range(3)],'object_count':len(col.all_objects),'mesh_object_count':sum(o.type=='MESH' for o in col.all_objects),'footprint_area_signed_m2':area,'osm_node_count':n,'source_way_id':way['id'],'source_timestamp':src['retrieved_snapshot_timestamp']}
(OUT/'build_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8')
print(json.dumps(metrics,indent=2))

