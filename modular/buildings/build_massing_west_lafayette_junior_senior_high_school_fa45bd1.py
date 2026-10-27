import bpy, json, math, os, sys
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
AUDIT = os.path.join(ROOT, 'audit', 'west_lafayette_junior_senior_high_school')
OSM_PATH = os.path.join(AUDIT, 'sources', 'osm_way_283537867_raw.json')
OUT = os.path.join(ROOT, 'modular', 'buildings', 'massing_west_lafayette_junior_senior_high_school_fa45bd1.blend')
ASSET_ID = 'massing_west_lafayette_junior_senior_high_school_fa45bd1'
COLL_NAME = 'Asset_' + ASSET_ID
SCENE_NAME = 'Building_' + ASSET_ID
OBJECT_NAME = 'West Lafayette Junior-Senior High School'
ORIGIN = (40.4274, -86.9137)
M_PER_LAT = 111040.0
M_PER_LON = 84810.60416539927

# Source-backed, deliberately conservative height interpretation:
# OSM tags the building as three levels but provides no measured height.
# Three 3.15 m stories plus roof structure/parapet place the primary roof at 10.5 m;
# roof service units reach the old source's 11.4 m envelope.
WALL_TOP = 10.0
ROOF_TOP = 10.5
ROOF_SERVICE_TOP = 11.4

# start with a clean, named building scene/collection
scene = bpy.data.scenes.get(SCENE_NAME) or bpy.context.scene
scene.name = SCENE_NAME
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for coll in list(bpy.data.collections):
    if coll.name != 'Collection':
        bpy.data.collections.remove(coll)
coll = bpy.data.collections.get(COLL_NAME) or bpy.data.collections.new(COLL_NAME)
if coll.name not in [c.name for c in scene.collection.children]:
    scene.collection.children.link(coll)
# Remove default child collection if empty
for c in list(scene.collection.children):
    if c.name == 'Collection' and not c.objects and not c.children:
        scene.collection.children.unlink(c)
        bpy.data.collections.remove(c)

def material(name, color, roughness=0.75, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = roughness
    bs.inputs['Metallic'].default_value = metallic
    return mat

brick = material('WLSHS | muted red-brown modular brick', (0.34,0.095,0.068), .86)
# Procedural running-bond relief/color, with restrained variation so facade reads as masonry.
nt = brick.node_tree
bs = nt.nodes.get('Principled BSDF')
tex = nt.nodes.new('ShaderNodeTexCoord')
brick_tex = nt.nodes.new('ShaderNodeTexBrick')
brick_tex.inputs['Color1'].default_value = (0.39,0.12,0.085,1)
brick_tex.inputs['Color2'].default_value = (0.28,0.075,0.058,1)
brick_tex.inputs['Mortar'].default_value = (0.20,0.19,0.17,1)
brick_tex.inputs['Scale'].default_value = 1.0
brick_tex.inputs['Mortar Size'].default_value = 0.018
brick_tex.inputs['Brick Width'].default_value = 0.50
brick_tex.inputs['Row Height'].default_value = 0.22
nt.links.new(tex.outputs['Object'], brick_tex.inputs['Vector'])
nt.links.new(brick_tex.outputs['Color'], bs.inputs['Base Color'])
stone = material('WLSHS | warm limestone / precast', (0.72,0.68,0.59), .68)
trim = material('WLSHS | dark bronze aluminum', (0.115,0.14,0.15), .32, .45)
glass = material('WLSHS | blue gray insulated glazing', (0.075,0.20,0.26), .17, .22)
roofmat = material('WLSHS | charcoal flat roof membrane', (0.075,0.085,0.09), .92)
service = material('WLSHS | rooftop equipment finish', (0.42,0.45,0.45), .72)
red = material('WLSHS | school red accent', (0.48,0.035,0.035), .54)

# Parse the authoritative 35-node closed OSM outline; coordinates are converted to the
# repository's campus world frame exactly as documented in modular/manifest.json.
raw = json.load(open(OSM_PATH, encoding='utf-8'))
way = next(e for e in raw['elements'] if e['type']=='way' and e['id']==283537867)
nodes = {e['id']:(e['lat'],e['lon']) for e in raw['elements'] if e['type']=='node'}
points = [((nodes[n][1]-ORIGIN[1])*M_PER_LON, (nodes[n][0]-ORIGIN[0])*M_PER_LAT) for n in way['nodes'][:-1]]
if len(points) != 34 or way['nodes'][0] != way['nodes'][-1]:
    raise RuntimeError('OSM outline changed: expected 34 unique vertices and closed ring')
area = sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))/2
if area < 0:
    points.reverse()

# Main wall/roof shell: exact OSM outline, three storeys, flat parapeted roof.
verts = [(x,y,0.0) for x,y in points] + [(x,y,WALL_TOP) for x,y in points]
n=len(points); faces=[]; face_mats=[]
for i in range(n):
    j=(i+1)%n
    faces.append((i,j,j+n,i+n)); face_mats.append(0)
# Tessellate concave plan polygon for a sound, flat roof cap.
tris=tessellate_polygon([[Vector((x,y,0)) for x,y in points]])
for tri in tris:
    faces.append(tuple(v+n for v in tri)); face_mats.append(1)
mesh=bpy.data.meshes.new('WLSHS source footprint shell mesh'); mesh.from_pydata(verts, [], faces); mesh.materials.append(brick); mesh.materials.append(roofmat); mesh.update()
obj=bpy.data.objects.new(OBJECT_NAME,mesh); coll.objects.link(obj)
for p,mi in zip(mesh.polygons,face_mats): p.material_index=mi
obj['source_feature']='OpenStreetMap way 283537867'
obj['source_vertex_count']=34
obj['height_status']='estimated: OSM building:levels=3; no verified measured height'
obj['roof_form']='flat, parapeted; campus aerial and architect imagery'

# Geometry helpers. Wall-mounted elements are built in a true facade basis.
def add_box_mesh(name, material_obj, boxes):
    vv=[]; ff=[]
    for center, axes, dims in boxes:
        c=Vector(center); u,v,w=[Vector(a) for a in axes]; a,b,h=[d/2 for d in dims]
        start=len(vv)
        for su,sv,sw in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
            p=c+u*(su*a)+v*(sv*b)+w*(sw*h); vv.append(tuple(p))
        ff.extend([(start+0,start+3,start+2,start+1),(start+4,start+5,start+6,start+7),(start+0,start+1,start+5,start+4),(start+1,start+2,start+6,start+5),(start+2,start+3,start+7,start+6),(start+3,start+0,start+4,start+7)])
    me=bpy.data.meshes.new(name+' mesh'); me.from_pydata(vv,[],ff); me.materials.append(material_obj); me.update()
    ob=bpy.data.objects.new(name,me); coll.objects.link(ob); return ob

# Continuous pale base band and narrow floor/spandrel lines echo the precast accents in KJG's exterior views.
line_boxes=[]
for z,h in [(0.35,.28),(3.28,.16),(6.48,.16),(9.72,.18),(10.32,.20)]:
    for i,(x1,y1) in enumerate(points):
        x2,y2=points[(i+1)%n]; dx=x2-x1; dy=y2-y1; length=math.hypot(dx,dy)
        if length < 2: continue
        u=(dx/length,dy/length,0); outward=(dy/length,-dx/length,0) # outline is CCW
        mid=((x1+x2)/2+outward[1]*0, (y1+y2)/2+outward[1]*0, z)
        # For the accent band, skip short projections and keep a subtle 0.14 m reveal.
        if length < 5: continue
        line_boxes.append((mid,(u,outward,(0,0,1)),(length-.25,.14,h)))
add_box_mesh('Precast floor bands and roof parapet coping',stone,line_boxes)

# The architect's exterior view shows warm precast/concrete piers breaking up the brick.
# Add restrained piers on the longer elevations between window groups.
piers=[]
for i,(x1,y1) in enumerate(points):
    x2,y2=points[(i+1)%n]; dx=x2-x1; dy=y2-y1; length=math.hypot(dx,dy)
    if length < 24: continue
    u=(dx/length,dy/length,0); outward=(dy/length,-dx/length,0)
    count=max(1,int(length//26))
    for k in range(1,count+1):
        along=length*k/(count+1)
        piers.append(((x1+u[0]*along+outward[0]*.12,y1+u[1]*along+outward[1]*.12,4.85),(u,outward,(0,0,1)),(.34,.26,9.55)))
add_box_mesh('Warm precast vertical facade piers',stone,piers)

# Regular window bays at all supported levels; density follows each source outline edge length.
window_boxes=[]; frame_boxes=[]
levels=[1.08,4.23,7.38]
for i,(x1,y1) in enumerate(points):
    x2,y2=points[(i+1)%n]; dx=x2-x1; dy=y2-y1; length=math.hypot(dx,dy)
    if length < 9: continue
    u=(dx/length,dy/length,0); outward=(dy/length,-dx/length,0)
    bay_count=max(1,int((length-5)//6.2))
    spacing=(length-4)/bay_count
    for j in range(bay_count):
        along=2+spacing*(j+.5)
        cx=x1+u[0]*along+outward[0]*.09; cy=y1+u[1]*along+outward[1]*.09
        for z in levels:
            width=min(2.2,spacing*.58); height=1.65
            window_boxes.append(((cx,cy,z+.88),(u,outward,(0,0,1)),(width,.12,height)))
            fw=.10
            for sx in (-1,1):
                frame_boxes.append(((cx+u[0]*sx*(width/2-fw/2),cy+u[1]*sx*(width/2-fw/2),z+.88),(u,outward,(0,0,1)),(fw,.16,height+.12)))
            for sz in (-1,1):
                frame_boxes.append(((cx,cy,z+.88+sz*(height/2-fw/2)),(u,outward,(0,0,1)),(width,.16,fw)))
            # vertical mullion and one horizontal transom per bay
            frame_boxes.append(((cx,cy,z+.88),(u,outward,(0,0,1)),(.055,.17,height)))
            frame_boxes.append(((cx,cy,z+.88),(u,outward,(0,0,1)),(width,.17,.045)))
add_box_mesh('Repeated classroom glazing',glass,window_boxes)
add_box_mesh('Bronze window frames and mullions',trim,frame_boxes)

# Landmark three-storey curtain-wall bay on the long east street frontage (visible in KJG's
# contemporary addition photo). The block sits on the east-facing outline segment near center.
# Pick the longest outline edge whose outward normal faces due east and whose center is north
# of the south entrance zone; this is stable against node-order changes.
east_edges=[]
for i,(x1,y1) in enumerate(points):
    x2,y2=points[(i+1)%n]; dx=x2-x1; dy=y2-y1; length=math.hypot(dx,dy)
    if not length: continue
    outward=(dy/length,-dx/length,0); mid=((x1+x2)/2,(y1+y2)/2)
    if outward[0] > .7 and mid[1] > 945:
        east_edges.append((length,i,x1,y1,x2,y2,dx/length,dy/length,outward))
if east_edges:
    length,i,x1,y1,x2,y2,ux,uy,outward=max(east_edges)
    u=(ux,uy,0); cx=(x1+x2)/2+outward[0]*.12; cy=(y1+y2)/2+outward[1]*.12
    cw=min(12.0,length-5.0); ch=8.8; cz=5.05
    curtain=[((cx,cy,cz),(u,outward,(0,0,1)),(cw,.10,ch))]
    add_box_mesh('Signature east facade curtain wall',glass,curtain)
    mullions=[]
    for k in range(9):
        pos=-cw/2+cw*k/8
        mullions.append(((cx+ux*pos,cy+uy*pos,cz),(u,outward,(0,0,1)),(.09,.19,ch+.1)))
    for z in (1.9,5.0,8.1):
        mullions.append(((cx,cy,z),(u,outward,(0,0,1)),(cw,.19,.10)))
    add_box_mesh('Curtain wall bronze mullions',trim,mullions)
    # Broad entrance canopy projects toward Grant Street; its exact elevation is not documented,
    # so it is restrained and kept below the glass entry bay.
    canopy_center=(cx+outward[0]*2.0,cy+outward[1]*2.0,3.65)
    add_box_mesh('East main entrance canopy',trim,[(canopy_center,(u,outward,(0,0,1)),(cw*.78,4.0,.24))])
    entry=[((cx+outward[0]*.3,cy+outward[1]*.3,1.45),(u,outward,(0,0,1)),(cw*.44,.18,2.9))]
    add_box_mesh('Glazed entry doors',glass,entry)

# Low rooftop mechanical units, restrained below a screen parapet, consistent with a 3-storey school roof.
roof_units=[]
for x,y,sx,sy in [(130,950,7,4),(155,970,8,4),(188,990,9,5),(205,930,7,4),(125,1005,8,4)]:
    # avoid placing units outside the actual outline by using the centroid-safe inside test below
    def in_poly(px,py):
        inside=False
        for k,(ax,ay) in enumerate(points):
            bx,by=points[(k+1)%n]
            if ((ay>py)!=(by>py)) and px<(bx-ax)*(py-ay)/(by-ay+1e-12)+ax: inside=not inside
        return inside
    if in_poly(x,y): roof_units.append(((x,y,10.9),((1,0,0),(0,1,0),(0,0,1)),(sx,sy,1.0)))
add_box_mesh('Rooftop screened HVAC',service,roof_units)

# Subtle red school-identification plaque near the east entry; no unsupported interior claims.
if east_edges:
    plaque=[((cx+outward[0]*.10,cy+outward[1]*.10,9.25),(u,outward,(0,0,1)),(min(6.0,cw*.6),.12,.42))]
    add_box_mesh('Red school identity plaque',red,plaque)
    # Extruded geometric lettering would be unreadable at campus scale; text is omitted.

# Render setup for reusable, reviewable camera views.
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1280; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.world.color=(0.055,0.065,0.085)
scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='AgX'
# Area lighting and simple world fill.
for o in list(scene.objects):
    if o.type in {'CAMERA','LIGHT'}: bpy.data.objects.remove(o,do_unlink=True)
def area_light(name,loc,power,size,color):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size; data.color=color
    ob=bpy.data.objects.new(name,data); coll.objects.link(ob); ob.location=loc
    ob.rotation_euler=(Vector((155,962,4))-ob.location).to_track_quat('-Z','Y').to_euler()
area_light('Large soft key', (80,850,150), 220000,110,(1.0,.86,.7))
area_light('Cool fill', (260,1060,90), 140000,100,(.65,.78,1.0))
# ground plane only for individual previews; exclude this from exported asset by placing in non-asset scene collection.
# Keep export collection limited to school. Preview ground and cameras are linked at scene root but not the asset collection.
preview=bpy.data.collections.new('Preview only - excluded from building asset'); scene.collection.children.link(preview)
# Lights affect these local renders only; they must not become part of the linked building asset.
for light_obj in [o for o in list(coll.objects) if o.type == 'LIGHT']:
    coll.objects.unlink(light_obj)
    preview.objects.link(light_obj)
# ground mesh
bpy.ops.mesh.primitive_plane_add(size=400, location=(155,962,-.08)); ground=bpy.context.object; ground.name='Preview ground only'; ground.data.materials.append(material('Preview grass field',(0.22,.30,.15),.95));
for c in list(ground.users_collection): c.objects.unlink(ground)
preview.objects.link(ground)

# Build orthographic aerial and facade cameras around the campus-coordinate building center.
center=Vector((155.7,962.8,5.4))
def camera(name,loc,ortho):
    data=bpy.data.cameras.new(name); data.type='ORTHO'; data.ortho_scale=ortho
    cam=bpy.data.objects.new(name,data); preview.objects.link(cam); cam.location=loc; cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); return cam
cams={
 'aerial':camera('Preview camera aerial',(280,770,260),265),
 'east':camera('Preview camera east',(355,963,56),190),
 'south':camera('Preview camera south',(155,760,55),190),
 'northwest':camera('Preview camera northwest',(45,1070,85),205),
}
scene.camera=cams['aerial']
# Save the reusable project with school in its contract collection and previews outside it.
os.makedirs(os.path.dirname(OUT),exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
# Preview images are rendered after save. Use building-only views and save into the audit folder.
render_dir=os.path.join(AUDIT,'previews'); os.makedirs(render_dir,exist_ok=True)
for view,cam in cams.items():
    scene.camera=cam
    scene.render.filepath=os.path.join(render_dir,view+'.png')
    bpy.ops.render.render(write_still=True)
# Save with the aerial camera active for convenience.
scene.camera=cams['aerial']
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print('BUILT',OUT,'points',n,'bounds',[(min(p[i] for p in points),max(p[i] for p in points)) for i in (0,1)],'east_edges',len(east_edges),'roof_units',len(roof_units))
