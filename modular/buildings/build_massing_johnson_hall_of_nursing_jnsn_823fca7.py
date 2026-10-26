import bpy, json, math, os
from mathutils import Vector

ASSET_ID='massing_johnson_hall_of_nursing_jnsn_823fca7'
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
ASSET_PATH=os.path.join(ROOT,'modular','buildings',ASSET_ID+'.blend')
AUDIT=os.path.join(ROOT,'audit',ASSET_ID)
SOURCE=os.path.join(AUDIT,'sources','purdue_building_shapes_fid218_jnsn.json')
RENDER=os.path.join(AUDIT,'renders')
os.makedirs(RENDER,exist_ok=True)
COLLECTION_NAME='Asset_'+ASSET_ID
SCENE_NAME='Building_'+ASSET_ID

with open(SOURCE,encoding='utf-8-sig') as f:
    feature=json.load(f)['feature']
assert feature['attributes']['FID']==218 and feature['attributes']['BLDG_ABBR']=='JNSN'
assert feature['attributes']['BUILDING_N']=='Helen R. Johnson Hall Of Nursing'
raw=feature['geometry']['rings'][0]
ring=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in raw]
if ring and math.dist(ring[0],ring[-1])<1e-8: ring=ring[:-1]
clean=[]
for p in ring:
    if not clean or math.dist(p,clean[-1])>.01: clean.append(p)
if len(clean)>2 and math.dist(clean[0],clean[-1])<=.01: clean.pop()
ring=clean
assert len(ring)==12
area2=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))
ccw=area2>0
ring_area=abs(area2)/2

# The manifest classifies JNSN as simple campus-coordinate massing. Preserve its ID,
# scene, collection and direct world-coordinate placement. Build only this building.
scene=bpy.data.scenes.get(SCENE_NAME) or bpy.context.scene
scene.name=SCENE_NAME
scene['building_id']=ASSET_ID
for ob in list(bpy.data.objects): bpy.data.objects.remove(ob,do_unlink=True)
for child in list(scene.collection.children): scene.collection.children.unlink(child)
for col in list(bpy.data.collections):
    if col.users==0: bpy.data.collections.remove(col)
coll=bpy.data.collections.new(COLLECTION_NAME); scene.collection.children.link(coll)
rig=bpy.data.collections.new('Render_Setup_JNSN'); scene.collection.children.link(rig)

mats={}
def material(name,color,rough=.8,metal=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    mats[name]=m; return m
brick=material('JNSN | brick (Purdue historic record)',(.40,.13,.085),.84)
glass=material('JNSN | upper ribbon glazing (2007 panorama)',(.035,.15,.20),.28,.08)
frame=material('JNSN | restrained ribbon separators',(.075,.09,.095),.55,.18)
roofmat=material('JNSN | flat roof membrane',(.22,.23,.23),.9)
parts=[]
def add_mesh(name,verts,faces,mat):
    me=bpy.data.meshes.new(name+' mesh'); me.from_pydata(verts,[],faces); me.materials.append(mat); me.update()
    ob=bpy.data.objects.new(name,me); coll.objects.link(ob); parts.append(ob); return ob

def add_box(name,center,dims,mat,angle=0.0):
    x,y,z=center; dx,dy,dz=[v/2 for v in dims]
    local=[(-dx,-dy,-dz),(dx,-dy,-dz),(dx,dy,-dz),(-dx,dy,-dz),(-dx,-dy,dz),(dx,-dy,dz),(dx,dy,dz),(-dx,dy,dz)]
    c,s=math.cos(angle),math.sin(angle)
    verts=[(x+u*c-v*s,y+u*s+v*c,z+w) for u,v,w in local]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return add_mesh(name,verts,faces,mat)

def extruded_footprint(name,poly,z0,z1,mat,top_mat=None):
    n=len(poly); verts=[(x,y,z0) for x,y in poly]+[(x,y,z1) for x,y in poly]
    # Cap uses the source outline as one n-gon. The ring is a valid, simple footprint.
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
    ob=add_mesh(name,verts,faces,mat)
    if top_mat:
        ob.data.materials.append(top_mat)
        ob.data.polygons[1].material_index=1
    return ob

# Purdue BuildingShapes reports 3 levels. The 2018 Tippecanoe 3DEP LiDAR tile
# gives a median 8.14 m roof-surface height above the nearby class-2 ground
# median (622.87 US survey ft); the 95th percentile of interior roof returns is
# 8.18 m. Use the observed median as the main flat roof elevation. Story spacing
# is derived from roof height / GIS levels and remains an estimate.
LEVELS=int(feature['attributes'].get('NUM_LEVELS') or 3)
ROOF_HEIGHT_M=8.135
FLOOR_TO_FLOOR=ROOF_HEIGHT_M/LEVELS
WALL_TOP=ROOF_HEIGHT_M
PARAPET_TOP=ROOF_HEIGHT_M
extruded_footprint('Johnson Hall of Nursing | exact Purdue FID 218 shell',ring,0.0,WALL_TOP,brick,roofmat)

# The Purdue historic database identifies brick as the documented material. No
# Purdue elevation or digital archive photograph was located. A Sep 2007
# identity-matched Google Street View panorama corroborates one upper-story
# horizontal window ribbon on the southwest-facing long wall; foliage obscures
# the lower facade, so no entrance or lower-floor openings are inferred.
def outward(a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    return (dy/length,-dx/length) if ccw else (-dy/length,dx/length)
segments=[]
for i,a in enumerate(ring):
    b=ring[(i+1)%len(ring)]; dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    if length<1: continue
    nx,ny=outward(a,b); angle=math.atan2(dy,dx); mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
    segments.append({'index':i,'a':a,'b':b,'length':length,'nx':nx,'ny':ny,'angle':angle,'mid':mid})
# Segment 0 is the southwest-facing 29.3 m wall matched to the 2007 panorama
# position. The source supports the ribbon's presence and location, not exact
# dimensions or bay count; the 8 divisions are a deliberately coarse visual proxy.
facade_seg=next(s for s in segments if s['index']==0)
fa,fb=facade_seg['a'],facade_seg['b']; fnx,fny,fang=facade_seg['nx'],facade_seg['ny'],facade_seg['angle']
fdx,fdy=fb[0]-fa[0],fb[1]-fa[1]
ribbon_count=8
ribbon_margin=2.6
ribbon_length=facade_seg['length']-2*ribbon_margin
ribbon_width=ribbon_length/ribbon_count
ribbon_z=6.55
ribbon_height=.88
for j in range(ribbon_count):
    t=(ribbon_margin+(j+.5)*ribbon_width)/facade_seg['length']
    px=fa[0]+fdx*t+fnx*.10; py=fa[1]+fdy*t+fny*.10
    add_box('Johnson Hall | observed upper ribbon window, segment 0',(px,py,ribbon_z),(ribbon_width-.12,.08,ribbon_height),glass,fang)
    if j>0:
        # Bay divisions merely render the continuous ribbon legibly; their exact
        # dimensions are not claimed as measured.
        add_box('Johnson Hall | ribbon bay divider',(px-ribbon_width*.5*math.cos(fang)+fnx*.15,py-ribbon_width*.5*math.sin(fang)+fny*.15,ribbon_z),(.09,.07,ribbon_height),frame,fang)

# Roof is a flat field at the directly sampled LiDAR median. Do not model a
# full-height parapet: the available ortho supports a flat roof but not its edge height.

# Join the exported shell and architectural masses into one portable mesh object.
parts=list(dict.fromkeys(parts))
for ob in parts: ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
model=bpy.context.object; model.name='Johnson Hall of Nursing (JNSN)'
model['roof_height_m_lidar_median']=ROOF_HEIGHT_M
model['roof_height_m_lidar_interior_p95']=8.184
model['roof_height_source']='Indiana 2018 3DEP LiDAR COPC, tile in2018_29951885_12; interior of Purdue FID 218 ring eroded 3m; class-1 roof returns relative to nearby class-2 ground median.'
model['num_levels_source']=LEVELS
model['floor_to_floor_m_derived_estimate']=FLOOR_TO_FLOOR
for c in list(model.users_collection):
    if c!=coll: c.objects.unlink(model)
if coll not in model.users_collection: coll.objects.link(model)
model.select_set(False)

# Camera, floor and lights are outside the exported asset collection.
def link_rig(obj): rig.objects.link(obj); return obj
xmin,xmax=min(p[0] for p in ring),max(p[0] for p in ring)
ymin,ymax=min(p[1] for p in ring),max(p[1] for p in ring)
center_x=(xmin+xmax)/2; center_y=(ymin+ymax)/2
floor_mat=material('Render | neutral ground',(.64,.67,.68),.95)
gm=bpy.data.meshes.new('JNSN render ground mesh'); gm.from_pydata([(xmin-35,ymin-35,-.10),(xmax+35,ymin-35,-.10),(xmax+35,ymax+35,-.10),(xmin-35,ymax+35,-.10)],[],[(0,1,2,3)]); gm.materials.append(floor_mat)
ground=bpy.data.objects.new('Render only | JNSN ground',gm); link_rig(ground)
def aim(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('JNSN exterior camera'); cam=bpy.data.objects.new('JNSN exterior camera',cam_data); link_rig(cam)
cam.location=(center_x-66,center_y-85,38); aim(cam,(center_x,center_y,5.5)); cam.data.type='ORTHO'; cam.data.ortho_scale=74; scene.camera=cam
ld=bpy.data.lights.new('JNSN key light','AREA'); ld.energy=4400; ld.shape='DISK'; ld.size=42
light=bpy.data.objects.new('JNSN key light',ld); link_rig(light); light.location=(center_x-40,center_y-45,65); aim(light,(center_x,center_y,4))
world=bpy.data.worlds.new('JNSN preview world') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(.72,.76,.80,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
scene.render.engine='BLENDER_WORKBENCH'; scene.display.shading.light='STUDIO'; scene.display.shading.studio_light='paint.sl'; scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True; scene.display.shading.cavity_type='WORLD'; scene.display.shading.background_type='WORLD'
scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.render.filepath=os.path.join(RENDER,'johnson_hall_nursing_exterior_preview.png')
scene.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=ASSET_PATH)
bpy.ops.render.render(write_still=True)
# Top view exposes orientation and source-shell silhouette.
plan_data=bpy.data.cameras.new('JNSN plan camera'); plan=bpy.data.objects.new('JNSN plan camera',plan_data); link_rig(plan)
plan.location=(center_x,center_y,140); plan.rotation_euler=(0,0,0); plan.data.type='ORTHO'; plan.data.ortho_scale=65
scene.camera=plan; scene.render.resolution_x=1100; scene.render.resolution_y=1100; scene.render.filepath=os.path.join(RENDER,'johnson_hall_nursing_plan_preview.png')
bpy.ops.render.render(write_still=True)
# Facade elevation of the panorama-matched southwest wall, without an inferred entry.
elev_data=bpy.data.cameras.new('JNSN southwest facade camera'); elev=bpy.data.objects.new('JNSN southwest facade camera',elev_data); link_rig(elev)
elev.location=(facade_seg['mid'][0]+fnx*58,facade_seg['mid'][1]+fny*58,6.2); aim(elev,(facade_seg['mid'][0],facade_seg['mid'][1],5.4)); elev.data.type='ORTHO'; elev.data.ortho_scale=38
scene.camera=elev; scene.render.resolution_x=1400; scene.render.resolution_y=800
scene.render.filepath=os.path.join(RENDER,'johnson_hall_nursing_southwest_facade.png')
bpy.ops.render.render(write_still=True)
scene.camera=cam; scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.filepath=os.path.join(RENDER,'johnson_hall_nursing_exterior_preview.png')
bpy.ops.wm.save_as_mainfile(filepath=ASSET_PATH)
print('JNSN_BUILD_DONE',json.dumps({'asset':ASSET_PATH,'collection':coll.name,'scene':scene.name,'object':model.name,'footprint_vertices':len(ring),'ring_area_m2_local_approx':ring_area,'footprint_bounds_m':[[xmin,xmax],[ymin,ymax]],'levels_source':LEVELS,'roof_height_lidar_median_m':ROOF_HEIGHT_M,'roof_height_lidar_interior_p95_m':8.184,'floor_to_floor_derived_estimate_m':FLOOR_TO_FLOOR,'facade_evidence':'Purdue historic database says brick; Sep 2007 identity-matched Street View corroborates an upper-story ribbon on southwest long wall. Lower facade and entrance remain unverified and omitted.','facade_segment_index':facade_seg['index'],'facade_ribbon_bays_render_proxy':ribbon_count,'estimate_note':'2018 LiDAR supports a flat main roof at about 8.14 m above nearby grade. Ribbon bay count and dimensions are render proxies; entrance remains unverified and omitted.'}))
