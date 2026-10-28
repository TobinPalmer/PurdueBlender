import bpy, json, math, os
from mathutils import Vector, Matrix
from mathutils.geometry import tessellate_polygon
BLEND=r'modular/buildings/massing_house_301840869_1b80ace.blend'
OUT=r'audit/sigma_kappa_fid780'
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene=bpy.context.scene
root=bpy.data.collections['Asset_massing_house_301840869_1b80ace']
house=bpy.data.objects['House_301840869']
with open(OUT+'/source_fid780.json','r',encoding='utf-8-sig') as f: packet=json.load(f)
raw=packet['features'][0]['geometry']['rings'][0][:-1]
pts=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in raw]
n=len(pts); xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
x0,x1=min(xs),max(xs); y0,y1=min(ys),max(ys); cx,cy=(x0+x1)/2,(y0+y1)/2
signed_area=sum(pts[i][0]*pts[(i+1)%n][1]-pts[(i+1)%n][0]*pts[i][1] for i in range(n))/2
# Reset the owned collection while retaining the stable root object and stable IDs.
for ob in list(root.objects):
    if ob!=house: bpy.data.objects.remove(ob,do_unlink=True)
for ob in list(scene.objects):
    if ob!=house: bpy.data.objects.remove(ob,do_unlink=True)

def material(name,color,rough=.78,metal=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.use_nodes=True
    bs=next(q for q in m.node_tree.nodes if q.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    return m
brick=material('SK • red-brown brick',(.34,.11,.075))
roofmat=material('SK • charcoal slate',(.16,.20,.27))
trim=material('SK • warm ivory trim',(.82,.78,.68))
glass=material('SK • blue-gray glass',(.13,.30,.43),.28)
wood=material('SK • dark entry wood',(.20,.09,.055))
stone=material('SK • pale entry limestone',(.70,.66,.57))
white=material('SK • portico white',(.88,.85,.77))
interior=material('SK • schematic warm floor',(.76,.65,.49))
wall=material('SK • schematic partition',(.43,.31,.22))
furn=material('SK • schematic furniture',(.12,.25,.37))

def mesh_obj(name,verts,faces,mats,indices=None,coll=root):
    me=bpy.data.meshes.new(name+'Mesh'); me.from_pydata(verts,[],faces)
    for m in mats: me.materials.append(m)
    me.update(); ob=bpy.data.objects.new(name,me); coll.objects.link(ob)
    if indices:
        for poly,mi in zip(me.polygons,indices): poly.material_index=mi
    return ob

def extrude(name,z0,z1,mat):
    v=[(x,y,z0) for x,y in pts]+[(x,y,z1) for x,y in pts]
    f=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    f += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    o=mesh_obj(name,v,f,[mat]); o['geometry_basis']='Purdue GIS FID 780 ring, projected with repository local approximation'; return o

# Exact GIS ring is the wall base; heights are estimates from the stylized house illustration.
base_story=extrude('TMP',0,3.5,brick)
house.data=base_story.data
bpy.data.objects.remove(base_story,do_unlink=True)
house.name='House_301840869'; house.data.name='SK_ExactGIS_LowerStoryMesh'
house['building_id']='massing_house_301840869_1b80ace'; house['role']='Lower brick story following the GIS FID 780 footprint'; house['outline_source']='21 unique Purdue GIS FID 780 vertices transformed with repository local approximation.'
upper=extrude('SK_Upper_Brick_Story',3.5,7.0,brick); upper['role']='Estimated second story, same source footprint'
# Band and base courses along all boundary runs.
def polyline_box(name,pts2,z,h,depth,mat):
    # Build axis-aligned courses centered on each real boundary segment.
    verts=[]; faces=[]
    for i,a in enumerate(pts2):
        b=pts2[(i+1)%len(pts2)]; dx=b[0]-a[0]; dy=b[1]-a[1]; L=math.hypot(dx,dy)
        if L<.45: continue
        ang=math.atan2(dy,dx); mx=(a[0]+b[0])/2; my=(a[1]+b[1])/2
        add_box(verts,faces,(mx,my,z),(L,depth,h),ang)
    return mesh_obj(name,verts,faces,[mat])

def add_box(v,f,center,size,yaw=0):
    x,y,z=center; sx,sy,sz=size; c=math.cos(yaw); s=math.sin(yaw); base=len(v)
    for zz in (-sz/2,sz/2):
      for yy in (-sy/2,sy/2):
       for xx in (-sx/2,sx/2): v.append((x+xx*c-yy*s,y+xx*s+yy*c,z+zz))
    # order 0(-x,-y,-z),1(+x,-y,-z),2(-x,+y,-z),3(+x,+y,-z), top 4..7
    f.extend([(base,base+2,base+3,base+1),(base+4,base+5,base+7,base+6),(base,base+1,base+5,base+4),(base+2,base+6,base+7,base+3),(base,base+4,base+6,base+2),(base+1,base+3,base+7,base+5)])

# White foundation/belt details are placed on wall faces as restrained trim.
polyline_box('SK_BaseCourse',pts,0.28,.22,.20,stone)
polyline_box('SK_StoryBelt',pts,3.55,.20,.18,trim)

# Place flush visual windows on long straight GIS boundary segments.
# Polygon signed area determines the outward normal of each edge.
window_v=[]; window_f=[]; window_idx=[]
def append_window_box(center,size,yaw,mi):
    start=len(window_v); add_box(window_v,window_f,center,size,yaw)
    window_idx.extend([mi]*6)

def add_window(center,z,width=1.35,height=1.45,angle=0,outward=(0,-1)):
    tang=Vector((math.cos(angle),math.sin(angle),0)); normal=Vector((outward[0],outward[1],0)); c=Vector((center[0],center[1],z))
    # Glass is slightly proud of the masonry so it reads in a solid-wall proxy.
    append_window_box(c+normal*.10,(width,.07,height),angle,1)
    for side in (-1,1): append_window_box(c+normal*.13+tang*side*(width/2+.075),(.12,.10,height+.18),angle,2)
    for dz in (-height/2-.09,height/2+.09): append_window_box(c+normal*.13+Vector((0,0,dz)),(width+.26,.10,.14),angle,2)
    append_window_box(c+normal*.17,(.055,.08,height),angle,2)
    append_window_box(c+normal*.17+Vector((0,0,.08)),(width,.08,.055),angle,2)

edges=[]
for i,a in enumerate(pts):
    b=pts[(i+1)%n]; dx=b[0]-a[0]; dy=b[1]-a[1]; L=math.hypot(dx,dy)
    if L<5.8: continue
    ang=math.atan2(dy,dx)
    if signed_area>0: out=(dy/L,-dx/L)
    else: out=(-dy/L,dx/L)
    edges.append((L,a,b,ang,out))
# North-facing facade is a provisional interpretation of the wide GIS edge;
# the illustration does not establish its bearing.
front_y=y1; front_x=cx
for L,a,b,ang,out in edges:
    # Skip first story opening at the centered entry; all positions remain interpretive.
    count=max(1,int((L-2.5)//4.2))
    for z in (1.9,5.2):
        for j in range(count):
            t=(j+1)/(count+1); cxw=a[0]+(b[0]-a[0])*t; cyw=a[1]+(b[1]-a[1])*t
            if abs(a[1]-front_y)<.55 and abs(b[1]-front_y)<.55 and z<3.5 and abs(cxw-front_x)<5.0: continue
            add_window((cxw,cyw),z,angle=ang,outward=out)
mesh_obj('SK_Exterior_Windows',window_v,window_f,[glass,roofmat,trim],window_idx)

# North-facing centered entry portico. Positions and dimensions are interpretive.
port_v=[]; port_f=[]
# four square white columns
for xx in (front_x-3.2,front_x-1.1,front_x+1.1,front_x+3.2): add_box(port_v,port_f,(xx,front_y+1.7,2.65),(.42,.42,5.25))
# entablature and shallow gabled pediment
add_box(port_v,port_f,(front_x,front_y+1.7,5.32),(7.6,.52,.42))
# porch deck and entry steps
add_box(port_v,port_f,(front_x,front_y+1.8,.30),(8.1,3.7,.28))
add_box(port_v,port_f,(front_x,front_y+4.0,.14),(8.1,2.0,.20))
# Door frame and double wood door
add_box(port_v,port_f,(front_x,front_y+.12,1.43),(2.05,.18,2.76))
add_box(port_v,port_f,(front_x-.52,front_y+.20,1.38),(.98,.12,2.48))
add_box(port_v,port_f,(front_x+.52,front_y+.20,1.38),(.98,.12,2.48))
# light stone side plinths for columns
for xx in (front_x-4.0,front_x+4.0): add_box(port_v,port_f,(xx,front_y+1.7,.55),(.7,.75,.45))
# white pediment as a triangular prism in X-Z plane, attached to the portico front
base=len(port_v)
for yy in (front_y+.25,front_y+2.05):
    port_v.extend([(front_x-3.8,yy,5.55),(front_x+3.8,yy,5.55),(front_x,yy,7.2)])
port_f.extend([(base,base+2,base+1),(base+3,base+4,base+5),(base,base+3,base+5,base+2),(base+2,base+5,base+4,base+1),(base+1,base+4,base+3,base)])
mesh_obj('SK_Entry_Portico',port_v,port_f,[white,wood,stone])

# Main gable ridge runs across the wide (X) facade, with roof pitch along depth.
# Triangulation follows the concave GIS ring and does not bridge its notch.
ry0=y0; ry1=y1; ridge=(ry0+ry1)/2; eave=7.0; peak=12.2
roof_points=[Vector((x,y,0)) for x,y in pts]
triangles=tessellate_polygon([roof_points])
rv=[(x,y,eave+(peak-eave)*(1-abs(y-ridge)/max(ridge-ry0,ry1-ridge))) for x,y in pts]
rf=[]
for tri in triangles:
    face=tuple(tri)
    a,b,c=[Vector(rv[i]) for i in face]
    if (b-a).cross(c-a).z<0: face=tuple(reversed(face))
    rf.append(face)
roof=mesh_obj('SK_Main_Gabled_Roof',rv,rf,[roofmat]); roof['role']='Estimated pitched roof with ridge parallel to the wide facade, triangulated within the concave GIS ring; pitch/ridge not surveyed'
# Source illustration's two end gables and central projecting gable are shown
# as simple front-facing triangles; their sizes are visual estimates only.
gv=[]; gf=[]; gmi=[]
def add_front_gable(center,width,apex):
    z0=7.0; y=front_y+.08; zbase=len(gv)
    gv.extend([(center-width/2,y,z0),(center+width/2,y,z0),(center,y,apex)])
    gf.append((zbase,zbase+2,zbase+1)); gmi.append(0)
    # Dark timber outline strips as shallow prisms in the facade plane.
    def beam(p1,p2,t=.16):
        x1,z1=p1; x2,z2=p2; dx=x2-x1; dz=z2-z1; L=math.hypot(dx,dz)
        nx=-dz/L*t/2; nz=dx/L*t/2; y0=y-.035; y1=y+.055; s=len(gv)
        corners=[(x1+nx,y0,z1+nz),(x2+nx,y0,z2+nz),(x2-nx,y0,z2-nz),(x1-nx,y0,z1-nz),
                 (x1+nx,y1,z1+nz),(x2+nx,y1,z2+nz),(x2-nx,y1,z2-nz),(x1-nx,y1,z1-nz)]
        gv.extend(corners)
        gf.extend([(s,s+1,s+2,s+3),(s+4,s+7,s+6,s+5),(s,s+4,s+5,s+1),(s+1,s+5,s+6,s+2),(s+2,s+6,s+7,s+3),(s+3,s+7,s+4,s)])
        gmi.extend([1]*6)
    beam((center-width/2,z0),(center,apex),.20); beam((center,apex),(center+width/2,z0),.20)
    beam((center-width/2,z0),(center+width/2,z0),.17)
add_front_gable(front_x-8.0,5.0,10.2)
add_front_gable(front_x+8.0,5.0,10.2)
add_front_gable(front_x,8.7,12.0)
mesh_obj('SK_Front_Gable_Ends',gv,gf,[brick,wood],gmi)
# Centered attic glazing and legible chapter sign in the principal gable.
agv=[]; agf=[]; add_box(agv,agf,(front_x,front_y+.15,9.55),(1.55,.16,1.55))
mesh_obj('SK_Central_Gable_Window',agv,agf,[glass])
plv=[]; plf=[]; add_box(plv,plf,(front_x,front_y+.18,8.25),(4.8,.14,.52))
mesh_obj('SK_Central_Gable_Sign_Plaque',plv,plf,[white])
bpy.ops.object.text_add(location=(front_x,front_y+.28,8.1))
sign=bpy.context.object; sign.name='SK_Sigma_Kappa_Sign'; sign.rotation_euler=Matrix(((-1,0,0),(0,0,1),(0,1,0))).to_euler(); sign.data.body='SIGMA KAPPA'; sign.data.align_x='CENTER'; sign.data.size=.38; sign.data.extrude=.008
sign.data.materials.append(wood); sign['role']='Centered chapter sign; lettering is interpretive, not a measured historic sign'
bpy.ops.object.convert(target='MESH')
sign=bpy.context.object
for c in list(sign.users_collection): c.objects.unlink(sign)
root.objects.link(sign)
# Four dormers are spread across the north-facing roof slope, aligned to the facade.
def point_inside(px,py):
    inside=False
    for i,a in enumerate(pts):
        b=pts[(i+1)%n]
        if ((a[1]>py)!=(b[1]>py)) and px < (b[0]-a[0])*(py-a[1])/(b[1]-a[1])+a[0]: inside=not inside
    return inside
dv=[]; df=[]; dmi=[]
for xx in (front_x-8.0,front_x-2.7,front_x+2.7,front_x+8.0):
    yy=front_y-6.0
    basez=eave+(peak-eave)*(1-abs(yy-ridge)/max(ridge-ry0,ry1-ridge))+.12
    if not point_inside(xx,yy): continue
    add_box(dv,df,(xx,yy+.38,basez+.62),(1.75,1.15,1.25)); dmi.extend([0]*6)
    s=len(dv)
    dv.extend([(xx-.88,yy-.22,basez+1.23),(xx+.88,yy-.22,basez+1.23),(xx,yy-.22,basez+2.0),
               (xx-.88,yy+.98,basez+1.23),(xx+.88,yy+.98,basez+1.23),(xx,yy+.98,basez+2.0)])
    df.extend([(s,s+1,s+2),(s+3,s+5,s+4),(s,s+3,s+4,s+1),(s+1,s+4,s+5,s+2),(s+2,s+5,s+3,s)]); dmi.extend([0]*5)
    add_box(dv,df,(xx,yy-.24,basez+.68),(.95,.08,.88)); dmi.extend([1]*6)
    add_box(dv,df,(xx,yy-.30,basez+.68),(.09,.10,1.0)); dmi.extend([2]*6)
mesh_obj('SK_Roof_Dormers',dv,df,[trim,glass,white],dmi)
# Illustrative chimney is placed only if its estimated position lies inside the wall ring.
cv=[]; cf=[]; chimxy=(x1-2.5,y1-4.5)
if point_inside(*chimxy):
    chimz=eave+(peak-eave)*(1-abs(chimxy[1]-ridge)/max(ridge-ry0,ry1-ridge))
    add_box(cv,cf,(chimxy[0],chimxy[1],chimz+.7),(1.25,1.35,3.2))
    chimney=mesh_obj('SK_Chimney',cv,cf,[brick]); chimney['role']='Estimated chimney seen in secondary illustration; location is interpretive'

# The illustration shows two facade levels, while GIS NUM_LEVELS says one.
# Keep the upper story as an estimated exterior, but show only one explicitly
# schematic interior level because no as-built floor plan has been found.
floor_v=[]; floor_f=[]
start=len(floor_v); floor_v.extend([(x,y,.22) for x,y in pts]); floor_f.append(tuple(range(start,start+n)))
mesh_obj('SK_Interior_Floor_Plates',floor_v,floor_f,[interior])
# Cutaway boundary is a separate low schematic wall course around the GIS outline.
polyline_box('SK_Interior_Schematic_Boundary',pts,.57,.62,.16,wall)
# Low schematic partition inserts clipped to the polygon's interior. Room sizes
# and uses are not sourced.
def horizontal_spans(y):
    hits=[]
    for i,a in enumerate(pts):
        b=pts[(i+1)%n]
        if (a[1] <= y < b[1]) or (b[1] <= y < a[1]):
            t=(y-a[1])/(b[1]-a[1]); hits.append(a[0]+t*(b[0]-a[0]))
    hits.sort(); return [(hits[i],hits[i+1]) for i in range(0,len(hits)-1,2) if hits[i+1]-hits[i]>.8]
def vertical_spans(x):
    hits=[]
    for i,a in enumerate(pts):
        b=pts[(i+1)%n]
        if (a[0] <= x < b[0]) or (b[0] <= x < a[0]):
            t=(x-a[0])/(b[0]-a[0]); hits.append(a[1]+t*(b[1]-a[1]))
    hits.sort(); return [(hits[i],hits[i+1]) for i in range(0,len(hits)-1,2) if hits[i+1]-hits[i]>.8]
pv=[]; pf=[]
def partition_span(a,b,constant,axis):
    mid=(a+b)/2
    gap=1.15 if b-a>5.0 else 0.0
    for lo,hi in ((a,mid-gap/2),(mid+gap/2,b)):
        if hi-lo<.65: continue
        if axis=='x': add_box(pv,pf,((lo+hi)/2,constant,.96),(hi-lo,.24,1.55))
        else: add_box(pv,pf,(constant,(lo+hi)/2,.96),(.24,hi-lo,1.55))
for y in (y0+5,y0+12,y0+20,y0+28,y0+35):
    for a,b in horizontal_spans(y): partition_span(a,b,y,'x')
for x in (x0+6,x0+12,x0+18):
    for a,b in vertical_spans(x): partition_span(a,b,x,'y')
mesh_obj('SK_Interior_Schematic_Partitions',pv,pf,[wall])
# Distinct generic furniture silhouettes and a stair placeholder improve plan legibility;
# none are assigned real room uses or claimed to match an as-built layout.
fv=[]; ff=[]
stations=[(x0+19,y0+7,'table'),(x0+17,y0+15,'bed'),(x0+9,y0+21,'table'),
          (x0+18,y0+24,'sofa'),(x0+9,y0+31,'bed'),(x0+17,y0+33,'table')]
for tx,ty,kind in stations:
    if not point_inside(tx,ty): continue
    if kind=='table':
        add_box(fv,ff,(tx,ty,.36),(2.5,1.25,.18))
        for dx in (-1.65,1.65):
            for dy in (-.92,.92):
                if point_inside(tx+dx,ty+dy): add_box(fv,ff,(tx+dx,ty+dy,.38),(.55,.55,.52))
    elif kind=='bed':
        add_box(fv,ff,(tx,ty,.34),(1.45,2.5,.22)); add_box(fv,ff,(tx,ty+.87,.48),(1.15,.48,.18))
    else:
        add_box(fv,ff,(tx,ty,.34),(2.7,1.0,.26)); add_box(fv,ff,(tx,ty-.42,.50),(2.7,.16,.42))
# Stair run placeholder: parallel treads in a compact rectangle near the central circulation.
stx=x0+16.5; sty=y0+18.0
if point_inside(stx,sty):
    for i in range(8): add_box(fv,ff,(stx,sty+i*.25,.38),(2.0,.13,.12))
mesh_obj('SK_Interior_Schematic_Furniture',fv,ff,[furn])

# Render previews with temporary camera/context, then remove every preview object before saving.
def aim(ob,target): ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
camdata=bpy.data.cameras.new('SK_TemporaryPreviewCamera'); cam=bpy.data.objects.new('SK_TemporaryPreviewCamera',camdata); scene.collection.objects.link(cam); scene.camera=cam
cam.location=(cx-17,y1+48,26); aim(cam,(cx,cy,5.0)); camdata.lens=48
scene.render.engine='BLENDER_WORKBENCH'; scene.display.shading.light='FLAT'; scene.display.shading.color_type='MATERIAL'; scene.display.shading.show_shadows=False; scene.display.shading.show_cavity=False; scene.display.shading.background_type='VIEWPORT'; scene.display.shading.background_color=(.45,.49,.54); scene.display.shading.show_specular_highlight=False
scene.render.resolution_x=1500; scene.render.resolution_y=1125; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.render.filepath=os.path.abspath(OUT+'/exterior_preview.png')
interior_names={'SK_Interior_Floor_Plates','SK_Interior_Schematic_Boundary','SK_Interior_Schematic_Partitions','SK_Interior_Schematic_Furniture'}
for ob in scene.objects: ob.hide_render=ob.name in interior_names or ob==cam
bpy.ops.render.render(write_still=True)
cam.location=(cx,y1+62,20); aim(cam,(cx,y1-1,5.6)); camdata.type='ORTHO'; camdata.ortho_scale=max(x1-x0,30)*1.20
scene.render.filepath=os.path.abspath(OUT+'/front_elevation_preview.png'); bpy.ops.render.render(write_still=True)
# Cutaway plan preview hides the whole exterior envelope. It is one schematic level.
visible={'SK_Interior_Floor_Plates','SK_Interior_Schematic_Boundary','SK_Interior_Schematic_Partitions','SK_Interior_Schematic_Furniture'}
for ob in scene.objects: ob.hide_render=ob.name not in visible or ob==cam
cam.location=(cx,cy,58); aim(cam,(cx,cy,0)); camdata.type='ORTHO'; camdata.ortho_scale=max(x1-x0,(y1-y0)*scene.render.resolution_x/scene.render.resolution_y)*1.16
scene.render.filepath=os.path.abspath(OUT+'/interior_cutaway_preview.png'); bpy.ops.render.render(write_still=True)
for ob in list(scene.objects):
    if ob==cam: bpy.data.objects.remove(ob,do_unlink=True)
for ob in root.objects: ob.hide_render=False
scene.camera=None
if camdata.users==0: bpy.data.cameras.remove(camdata)
# Match the shared manifest's stable one-object collection contract.
parts=[ob for ob in root.objects if ob.type=='MESH' and ob!=house]
if parts:
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts: ob.select_set(True)
    house.select_set(True); bpy.context.view_layer.objects.active=house
    bpy.ops.object.join()
house.name='House_301840869'; house.data.name='Sigma_Kappa_Composite_Mesh'
house['interior_representation']='One-level schematic insert; no verified floor plan or room uses found.'
house['roof_uncertainty']='Roof geometry is estimated from a secondary custom illustration; not measured.'
house['front_orientation']='North-facing interpretation of the wide GIS edge; entrance elevation is unverified.'
# Keep a shaded material viewport for interactive opening; preview PNGs above use flat fill.
scene.display.shading.light='STUDIO'; scene.display.shading.studio_light='paint.sl'; scene.display.shading.color_type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('SAVED',BLEND,'FID',780,'GIS_VERTS',n,'BOUNDS',(x0,x1,y0,y1),'ASSET_OBJECTS',len(root.objects),'SCENE_OBJECTS',len(scene.objects),'GIS_AREA_M2',abs(signed_area))
