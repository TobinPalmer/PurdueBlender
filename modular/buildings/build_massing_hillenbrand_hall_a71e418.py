import bpy, json, math
from mathutils import Vector
from pathlib import Path

ROOT=Path(r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender')
ASSET_ID='massing_hillenbrand_hall_a71e418'
ASSET=ROOT/'modular'/'buildings'/f'{ASSET_ID}.blend'
AUDIT=ROOT/'audit'/ASSET_ID
GIS= AUDIT/'sources'/'hillenbrand_gis_fid259_query.json'
RENDER=AUDIT/'review'/'preview_r3.png'
# Purdue's 2019 project summary: two towers, eight floors each. GIS floor levels are spaced
# 10.4 units apart and R=83.2; assuming feet gives an approximate 25.36 m roof level.
# The GIS field metadata has no units and Extrution=108 conflicts, so roof height remains estimated.
FLOORS=8
FLOOR_PITCH_M=10.4*0.3048
WALL_TOP=FLOOR_PITCH_M*7.5
ROOF_TOP=83.2*0.3048
PODIUM_TOP=FLOOR_PITCH_M

data=json.loads(GIS.read_text(encoding='utf-8'))
feature=data['features'][0]
assert feature['attributes']['FID']==259 and feature['attributes']['BUILDING_N']=='Hillenbrand Residence Hall'
ring=max(feature['geometry']['rings'],key=len)
xy=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in ring]
if xy[0]==xy[-1]: xy=xy[:-1]
area2=sum(xy[i][0]*xy[(i+1)%len(xy)][1]-xy[(i+1)%len(xy)][0]*xy[i][1] for i in range(len(xy)))
ccw=area2>0

# Approximate upper tower plan rectangles traced from the two separate hipped roof masses
# in the Esri orthophoto. The full ground-level connecting shell still uses the exact GIS ring.
WEST=-9676815.980339654; NORTH=4928324.291104144; SPAN=360.0; IMAGE_PX=1200; R=6378137.0
def px_to_local(p):
    px,py=p; xm=WEST+px*SPAN/IMAGE_PX; ym=NORTH-py*SPAN/IMAGE_PX
    lon=math.degrees(xm/R); lat=math.degrees(2*math.atan(math.exp(ym/R))-math.pi/2)
    return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0)
def cross_from_pixels(box):
    x0,y0,x1,y1=box
    # Each upper mass is represented as two intersecting wings, consistent with the
    # Purdue project summary and approximate roof geometry visible in the orthophoto.
    # Wing widths are image-derived estimates, not surveyed plan dimensions.
    dx=(x1-x0)*.32; dy=(y1-y0)*.30
    pts=[(x0+dx,y0),(x1-dx,y0),(x1-dx,y0+dy),(x1,y0+dy),
         (x1,y1-dy),(x1-dx,y1-dy),(x1-dx,y1),(x0+dx,y1),
         (x0+dx,y1-dy),(x0,y1-dy),(x0,y0+dy),(x0+dx,y0+dy)]
    return [px_to_local(p) for p in pts]
towers=[cross_from_pixels((596,428,667,488)),cross_from_pixels((692,428,765,488))]

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene; scene.name='Building_'+ASSET_ID
for datablocks in (bpy.data.meshes,bpy.data.cameras,bpy.data.lights):
    for datablock in list(datablocks):
        if datablock.users==0: datablocks.remove(datablock)
coll=bpy.data.collections.new('Asset_'+ASSET_ID); scene.collection.children.link(coll)
verts=[]; faces=[]; indices=[]
def face(points,mi):
    s=len(verts); verts.extend(tuple(p) for p in points); faces.append(tuple(range(s,s+len(points)))); indices.append(mi)
def vertical_prism(poly,z0,z1,mi):
    face([(x,y,z1) for x,y in poly],mi)
    face([(x,y,z0) for x,y in reversed(poly)],mi)
    for i,(x0,y0) in enumerate(poly):
        x1,y1=poly[(i+1)%len(poly)]
        face([(x0,y0,z0),(x1,y1,z0),(x1,y1,z1),(x0,y0,z1)],mi)
def edge_box(a,b,normal,depth,z0,z1,width,center_s,mi):
    dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);t=(dx/length,dy/length)
    c=(a[0]+t[0]*center_s+normal[0]*depth/2,a[1]+t[1]*center_s+normal[1]*depth/2)
    u=Vector((t[0],t[1],0));n=Vector((normal[0],normal[1],0));v=Vector((c[0],c[1],0))
    ps=[v-u*width/2-n*depth/2,v+u*width/2-n*depth/2,v+u*width/2+n*depth/2,v-u*width/2+n*depth/2]
    face([(p.x,p.y,z0) for p in ps],mi);face([(p.x,p.y,z1) for p in ps],mi)
    for i in range(4):
        a0=ps[i];b0=ps[(i+1)%4]
        face([(a0.x,a0.y,z0),(b0.x,b0.y,z0),(b0.x,b0.y,z1),(a0.x,a0.y,z1)],mi)
def make_mat(name,color,roughness=.75,metallic=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bsdf=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value=(*color,1);bsdf.inputs['Roughness'].default_value=roughness;bsdf.inputs['Metallic'].default_value=metallic
    return m
mats=[make_mat('Red brick, documented in Purdue entrance photo',(0.40,.12,.08)),
      make_mat('Dark glazing, photo-informed schematic',(0.055,.12,.16),.25),
      make_mat('Green metal tower roof, aerial-informed approximate',(0.20,.36,.28),.32,.25),
      make_mat('Low shared hall roof',(0.28,.29,.27))]

# Shared ground-floor/base envelope uses the GIS outline; height ties to GIS F02=10.4 assumption.
vertical_prism(xy,0,PODIUM_TOP,0)
# Flat low connector/dining/common-area roof over the complete source footprint.
face([(x,y,PODIUM_TOP) for x,y in xy],3)

# Two separate eight-floor tower volumes; the approximate cross plan reflects two wings per
# tower as documented by Purdue and interpreted from distinct aerial roof masses.
for poly in towers:
    vertical_prism(poly,PODIUM_TOP,WALL_TOP,0)
    # Small regularly spaced upper-floor glazing bays are schematic; no exact count or dimensions are claimed.
    for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
        dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);t=(dx/length,dy/length)
        normal=(t[1],-t[0]) if ccw else (-t[1],t[0])
        count=max(2,int(length//4.0));step=length/count;win_w=min(1.4,step*.42)
        for k in range(count):
            s=(k+.5)*step
            for floor in range(1,FLOORS):
                z0=floor*FLOOR_PITCH_M + .75
                z1=min(z0+1.4,WALL_TOP-.3)
                if z1>z0: edge_box(a,b,normal,.12,z0,z1,win_w,s,1)
    # Low hipped roof cap, supported as a form by the two visible roof peaks; pitch/height estimated.
    cx=sum(x for x,y in poly)/len(poly);cy=sum(y for x,y in poly)/len(poly);apex=(cx,cy,ROOF_TOP)
    roof_z=WALL_TOP
    for i,(x0,y0) in enumerate(poly):
        x1,y1=poly[(i+1)%len(poly)]
        face([(x0,y0,roof_z),(x1,y1,roof_z),apex],2)

mesh=bpy.data.meshes.new('Hillenbrand_GIS_podium_two_towers_r2');mesh.from_pydata(verts,[],faces);mesh.update()
obj=bpy.data.objects.new('Hillenbrand Hall',mesh);coll.objects.link(obj)
for m in mats:mesh.materials.append(m)
for p,mi in zip(mesh.polygons,indices):p.material_index=mi
obj['asset_id']=ASSET_ID
obj['source_shell']='Purdue BuildingShapesZip4 FID 259, exact source ring'
obj['tower_count_evidence']='Purdue Treasurer project summary: two towers, eight floors each; each tower has two wings; connected at first floor/basement by common areas and dining hall.'
obj['floor_count_status']='8 floors per tower documented in Purdue project summary; no floor labels drawn as measured elevations.'
obj['height_status']='estimated: GIS R=83.2 interpreted as feet gives 25.36 m; GIS field units undocumented and Extrution=108 conflicts.'
obj['roof_status']='two low hipped caps and intersecting two-wing plans inferred from aerial plus official project summary; exact roof pitch, ridge height and top equipment unverified.'
obj['facade_status']='red brick/windows are photo-informed; window count/size/rhythm schematic and unverified.'
obj['entry_status']='entry canopy/door removed from geometry because its compass position and dimensions could not be supported.'

scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=32
scene.render.resolution_x=1100;scene.render.resolution_y=850;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(RENDER);scene.render.film_transparent=False
scene.world.use_nodes=True;bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.62,.68,.78,1);bg.inputs['Strength'].default_value=.8
center=Vector((sum(x for x,y in xy)/len(xy),sum(y for x,y in xy)/len(xy),ROOF_TOP*.53))
camd=bpy.data.cameras.new('HillenbrandPreviewCamera');cam=bpy.data.objects.new('HillenbrandPreviewCamera',camd);scene.collection.objects.link(cam)
cam.location=center+Vector((185,-220,120));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=205;scene.camera=cam
ld=bpy.data.lights.new('HillenbrandKey','AREA');light=bpy.data.objects.new('HillenbrandKey',ld);scene.collection.objects.link(light);light.location=center+Vector((30,-80,150));ld.energy=100000;ld.size=120
sund=bpy.data.lights.new('HillenbrandSun','SUN');sund.energy=2.2;sund.angle=.18;suno=bpy.data.objects.new('HillenbrandSun',sund);scene.collection.objects.link(suno);suno.location=center+Vector((-70,-110,180));suno.rotation_euler=(center-suno.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.render.render(write_still=True)
for temp in (cam,light,suno):bpy.data.objects.remove(temp,do_unlink=True)
scene.camera=None;scene.render.filepath='//'
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps({'asset':str(ASSET),'render':str(RENDER),'objects':len([o for o in bpy.data.objects if o.type=='MESH']),'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'footprint_vertices':len(xy),'tower_polygons':[p for p in towers],'podium_top_m':PODIUM_TOP,'wall_top_m':WALL_TOP,'roof_top_m':ROOF_TOP},indent=2))
