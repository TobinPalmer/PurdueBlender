import bpy, json, math
from mathutils import Vector

ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET=ROOT+r'/modular/buildings/lambert_fieldhouse.blend'
OUT=ROOT+r'/audit/lambert_fieldhouse'
bpy.ops.wm.open_mainfile(filepath=ASSET)
roof=bpy.data.collections['LAMB_Roof']; facade=bpy.data.collections['LAMB_Facade']; interior=bpy.data.collections['LAMB_Interior']

def getmat(name,color,rough=.65,metal=0,emission=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=color; m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=color; bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    if emission and 'Emission Color' in bs.inputs:
        bs.inputs['Emission Color'].default_value=color; bs.inputs['Emission Strength'].default_value=emission
    return m

def cube(name,center,dims,mat,col):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o); o.data.materials.append(mat); return o

def append_beam(v,f,a,b,width,height=None):
    a,b=Vector(a),Vector(b); d=b-a
    if d.length<.001:return
    h=height if height is not None else width
    q=d.to_track_quat('Z','Y'); center=(a+b)*.5
    local=[Vector((sx*width/2,sy*width/2,sz*d.length/2)) for sx,sy,sz in
           ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1))]
    n=len(v); v.extend([tuple(center+q@Vector((p.x,p.y*height/width,p.z))) for p in local])
    f.extend([tuple(n+i for i in fc) for fc in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])

def mesh(name,verts,faces,mat,col):
    me=bpy.data.meshes.new(name+' mesh'); me.from_pydata(verts,[],faces); me.materials.append(mat); me.update()
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); return ob

# The historic fieldhouse record identifies steel in the structure; present and
# historic interior photos show the arched roof volume. Add readable bowstring
# roof trusses beneath the existing estimated roof shell rather than inventing a
# new roof covering or changing the measured building/track placement.
for o in list(roof.objects):
    if o.name.startswith('LAMB | round5 steel arch trusses'): bpy.data.objects.remove(o,do_unlink=True)
steel=getmat('LAMB | painted fieldhouse roof steel round5',(.24,.29,.31,1),.55,.48)
canopy=bpy.data.objects['LAMB | continuous arched fieldhouse roof canopy']
radius=min(canopy.dimensions.x,canopy.dimensions.y)*.5
rise=canopy.dimensions.z; eave=11.2; yspan=radius*.975
truss_v=[]; truss_f=[]
xstations=[-40.5+i*9.0 for i in range(10)]
nodes=12; ys=[-yspan+2*yspan*i/nodes for i in range(nodes+1)]
def roof_z(y): return eave+rise*math.sqrt(max(0,1-(y/radius)**2))-.36
for x in xstations:
    top=[(x,y,roof_z(y)) for y in ys]
    bottom=[(x,y,10.60) for y in ys]
    for i in range(nodes):
        append_beam(truss_v,truss_f,top[i],top[i+1],.20,.24)
        append_beam(truss_v,truss_f,bottom[i],bottom[i+1],.20,.24)
    for i in range(nodes+1): append_beam(truss_v,truss_f,bottom[i],top[i],.16,.18)
    for i in range(nodes):
        if i%2==0: append_beam(truss_v,truss_f,bottom[i],top[i+1],.14,.16)
        else: append_beam(truss_v,truss_f,top[i],bottom[i+1],.14,.16)
mesh('LAMB | round5 steel arch trusses',truss_v,truss_f,steel,roof)

# Create a restrained horizontal purlin grid between trusses, following the arch.
purl_v=[]; purl_f=[]
for y in (-36,-24,-12,0,12,24,36):
    z=roof_z(y)-.12
    append_beam(purl_v,purl_f,(-42,y,z),(42,y,z),.12,.14)
mesh('LAMB | round5 roof arch purlins',purl_v,purl_f,steel,roof)

# Contemporary visitor imagery supports pale vertical pilasters and large glass-
# block panels; the historic postcard supports stone accents and horizontal bands.
# Place pilasters just proud of the existing wall so the documented concrete rhythm
# reads clearly in the exterior view. Sizes/spacing are visual estimates.
limestone=getmat('LAMB | warm pale limestone concrete round5',(.60,.61,.58,1),.82)
for o in list(facade.objects):
    if o.name.startswith('LAMB | round5 facade pilasters') or o.name.startswith('LAMB | round5 horizontal stone bands'):
        bpy.data.objects.remove(o,do_unlink=True)
wall=bpy.data.objects['Lambert Fieldhouse | GIS perimeter wall panels with real glazing openings']
zheight=wall.dimensions.z
front_y=-46.92; back_y=46.92; east_x=49.66; west_x=-49.66
pil_v=[]; pil_f=[]
for x in [-42,-33.6,-25.2,-16.8,-8.4,8.4,16.8,25.2,33.6,42]:
    append_box= None
    cube_obj=cube('LAMB | round5 facade pilasters south',(x,front_y-.20,zheight/2),(.60,.42,zheight-.12),limestone,facade)
    cube_obj.name='LAMB | round5 facade pilasters south '+str(x)
    cube_obj=cube('LAMB | round5 facade pilasters north',(x,back_y+.20,zheight/2),(.60,.42,zheight-.12),limestone,facade)
    cube_obj.name='LAMB | round5 facade pilasters north '+str(x)
for y in [-38,-28.5,-19,-9.5,0,9.5,19,28.5,38]:
    cube_obj=cube('LAMB | round5 facade pilasters east',(east_x+.20,y,zheight/2),(.42,.60,zheight-.12),limestone,facade)
    cube_obj.name='LAMB | round5 facade pilasters east '+str(y)
    cube_obj=cube('LAMB | round5 facade pilasters west',(west_x-.20,y,zheight/2),(.42,.60,zheight-.12),limestone,facade)
    cube_obj.name='LAMB | round5 facade pilasters west '+str(y)

# Stone bands align to the two existing glazed rows and split the brick panels
# into a more legible institutional facade; no glazing openings are relocated.
for z in (3.32,5.42,8.78,11.05):
    cube('LAMB | round5 horizontal stone bands south',(0,front_y-.22,z),(98.0,.44,.26),limestone,facade)
    cube('LAMB | round5 horizontal stone bands north',(0,back_y+.22,z),(98.0,.44,.26),limestone,facade)
    cube('LAMB | round5 horizontal stone bands east',(east_x+.22,0,z),(.44,92.0,.26),limestone,facade)
    cube('LAMB | round5 horizontal stone bands west',(west_x-.22,0,z),(.44,92.0,.26),limestone,facade)

# The ca. 1930–45 Purdue postcard depicts an entrance tower; the Purdue GIS
# record assigns five levels / 69 ft to this complex. Add a low-depth entrance
# tower mass as a historical facade cue. Its exact current survival/height is
# unverified, so the mass and three window bands remain schematic.
brick=bpy.data.materials.get('LAMB | mottled Purdue red-brown brick')
if brick is None: brick=getmat('LAMB | tower brick round5',(.40,.15,.09,1),.8)
glass=getmat('LAMB | tower glass-block glazing round5',(.32,.43,.45,1),.28,.05,.08)
tower=cube('LAMB | round5 schematic historic entrance tower',(0,-48.22,15.55),(13.2,2.6,8.7),brick,facade)
cap=cube('LAMB | round5 tower limestone cap',(0,-48.22,19.98),(14.0,3.0,.55),limestone,facade)
for i,z in enumerate((12.65,14.75,16.85,18.75)):
    cube('LAMB | round5 tower glass panel '+str(i+1),(0,-49.545,z),(6.4,.08,.92),glass,facade)
    for x in (-3.35,3.35): cube('LAMB | round5 tower limestone jamb',(x,-49.60,z),(.22,.20,1.16),limestone,facade)
    cube('LAMB | round5 tower limestone sill',(0,-49.60,z-.60),(6.9,.20,.18),limestone,facade)
    cube('LAMB | round5 tower limestone head',(0,-49.60,z+.60),(6.9,.20,.18),limestone,facade)

# Interior meet photography shows upper spectator/official balconies. Add narrow
# side overlooks at the upper wall with simple guardrails; their precise extent
# and access locations are schematic.
balcony_mat=getmat('LAMB | round5 balcony concrete',(.45,.47,.45,1),.82)
rail_mat=getmat('LAMB | round5 balcony guardrail steel',(.20,.24,.26,1),.46,.62)
for side in (-1,1):
    y=side*42.5
    cube('LAMB | round5 upper spectator balcony deck',(0,y,8.92),(66.0,3.8,.34),balcony_mat,interior)
    # Inner guardrail on the track-facing edge, with regular posts and top/bottom rails.
    edge=y-side*1.9
    for x in range(-32,33,4): cube('LAMB | round5 balcony railing post',(x,edge,9.82),(.11,.11,1.45),rail_mat,interior)
    cube('LAMB | round5 balcony top rail',(0,edge,10.54),(66.0,.12,.12),rail_mat,interior)
    cube('LAMB | round5 balcony mid rail',(0,edge,9.86),(66.0,.09,.09),rail_mat,interior)

# A compact generic meet display is visible in the indoor meet reference; avoid
# copied logos or unsupported event text.
boardmat=getmat('LAMB | round5 dark scoreboard',(.025,.035,.04,1),.45,.15)
gold=getmat('LAMB | round5 score display warm pixels',(.92,.58,.12,1),.34,.05,.35)
cube('LAMB | round5 generic meet display panel',(0,45.5,10.1),(8.2,.35,2.2),boardmat,interior)
for row in range(3):
    for col in range(14):
        x=-3.4+col*.52; z=9.55+row*.45
        cube('LAMB | round5 display segment',(x,45.29,z),(.25,.06,.22),gold,interior)

# Save/reopen then render with the saved exterior and the normal cutaway setup.
track=bpy.data.objects['LAMB | 6-lane 200 m stadium track surface']; n=len(track.data.vertices)//2
center=[(track.data.vertices[i].co+track.data.vertices[i+n].co)*.5 for i in range(n)]
perimeter=sum((center[(i+1)%n]-center[i]).length for i in range(n))
bpy.ops.wm.save_as_mainfile(filepath=ASSET); bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene; scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.camera=bpy.data.objects['LAMB | three-quarter preview camera']; scene.render.filepath=OUT+r'/exterior_round5.png'; bpy.ops.render.render(write_still=True)
for o in bpy.data.objects:
    if o.type=='LIGHT' and ('interior' in o.name.lower() or 'track fill' in o.name.lower()): o.hide_render=False
hidden=[]
for cname in ('LAMB_Structure','LAMB_Facade'):
    c=bpy.data.collections.get(cname)
    if c:
        for o in c.objects: hidden.append((o,o.hide_render)); o.hide_render=True
canopy=bpy.data.objects.get('LAMB | continuous arched fieldhouse roof canopy')
if canopy: hidden.append((canopy,canopy.hide_render)); canopy.hide_render=True
scene.camera=bpy.data.objects['LAMB | interior review camera']; scene.render.filepath=OUT+r'/interior_round5.png'; bpy.ops.render.render(write_still=True)
for o,val in hidden:o.hide_render=val
bpy.ops.wm.open_mainfile(filepath=ASSET)
asset=bpy.data.collections['Asset_lambert_fieldhouse']; pavers=bpy.data.objects['LAMB | Stadium entry brick inlay round4']
report={'revision':5,'saved_and_reopened':'PASS','asset_file':'modular/buildings/lambert_fieldhouse.blend','asset_object_count':len(list(asset.all_objects)),
        'track_mesh_measured_lane1_centerline_perimeter_m':perimeter,'track_lanes':6,'track_boundary_lines':7,
        'added':'steel bowstring roof truss/purlin grid, pale pilaster and stone-band facade rhythm, low-depth schematic historic entrance tower, upper spectator balconies, generic score display',
        'dimensions':'all new architectural feature dimensions and placements are visual estimates; no shell footprint, local origin, or track geometry changed',
        'previews':['audit/lambert_fieldhouse/exterior_round5.png','audit/lambert_fieldhouse/interior_round5.png'],'master_manifest_shared_files_edited':False}
with open(OUT+r'/validation_round5.json','w') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
