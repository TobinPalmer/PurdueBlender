import bpy, math, json, os
from mathutils import Vector
from math import radians, cos
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'zundo_family_dentistry_r2.blend')
OUT = os.path.dirname(__file__)
# OSM way 887558318 ring in raw snapshot; approximate project X east, Y north.
nodes=[(-86.9220566,40.4458794),(-86.9219389,40.4458793),(-86.9219391,40.4458211),(-86.9218772,40.4458211),(-86.9218774,40.4457310),(-86.9219378,40.4457311),(-86.9219380,40.4456574),(-86.9220571,40.4456576)]
lat0,lon0=40.4274,-86.9137
xy=[((lon-lon0)*111412.84*cos(radians(lat0)),(lat-lat0)*111040.0) for lon,lat in nodes]
cross=[xy[i][0]*xy[(i+1)%len(xy)][1]-xy[(i+1)%len(xy)][0]*xy[i][1] for i in range(len(xy))]
area2=sum(cross)
origin=(sum((xy[i][0]+xy[(i+1)%len(xy)][0])*cross[i] for i in range(len(xy)))/(3*area2),sum((xy[i][1]+xy[(i+1)%len(xy)][1])*cross[i] for i in range(len(xy)))/(3*area2))
poly=[(x-origin[0],y-origin[1]) for x,y in xy]
# Reset and make one self-contained building library scene.
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene; sc.name='Building_zundo_family_dentistry'
col=bpy.data.collections.new('Asset_massing_zundo_family_dentistry_f840e2b'); sc.collection.children.link(col)
def link(o):
 for c in list(o.users_collection): c.objects.unlink(o)
 col.objects.link(o); return o
def mat(name,color,rough=.65,metal=0,noise_scale=None,noise_strength=.12):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
 if noise_scale:
  nt=m.node_tree; tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=noise_scale; tex.inputs['Detail'].default_value=3
  coord=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(coord.outputs['Generated'],tex.inputs['Vector'])
  bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=noise_strength; bump.inputs['Distance'].default_value=.035; nt.links.new(tex.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
  ramp=nt.nodes.new('ShaderNodeValToRGB'); base=Vector(color);ramp.color_ramp.elements[0].position=.22;ramp.color_ramp.elements[0].color=(*(base*.88),1);ramp.color_ramp.elements[1].position=.78;ramp.color_ramp.elements[1].color=(*(base*1.08),1);nt.links.new(tex.outputs['Fac'],ramp.inputs['Fac']);nt.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
  p.inputs['Roughness'].default_value=rough
 return m
wall=mat('Pale warm painted exterior with subtle stipple (inferred)',(.78,.76,.70),.82,noise_scale=13,noise_strength=.14)
trim=mat('Soft white fascia and trim',(.88,.86,.80),.64)
roof=mat('Dark charcoal low-slope membrane with fine granule texture (inferred)',(.16,.17,.18),.84,noise_scale=28,noise_strength=.17)
concrete=mat('Warm gray broom-finished concrete with aggregate variation',(.50,.51,.49),.88,noise_scale=34,noise_strength=.20)
glass=mat('Readable blue-gray reflective safety glazing',(.19,.34,.40),.19,.18,noise_scale=5,noise_strength=.025)
frame=mat('Graphite bronze window frames',(.16,.19,.19),.30,.50)
wood=mat('Warm wood interior cabinetry',(.38,.23,.13),.56)
interior=mat('Warm off-white interior partitions',(.86,.84,.77),.86,noise_scale=8,noise_strength=.045)
seat=mat('Muted deep teal dental upholstery',(.08,.32,.32),.48)
steel=mat('Brushed stainless equipment',(.60,.65,.67),.26,.72)
plantmat=mat('Landscape evergreen',(.10,.22,.12),.92,noise_scale=9,noise_strength=.2)
accent=mat('Deep bronze sign lettering',(.12,.16,.16),.34,.35)
ledmat=mat('Soft warm task light diffuser',(.95,.88,.68),.3)
ledp=ledmat.node_tree.nodes.get('Principled BSDF');ledp.inputs['Emission Color'].default_value=(1.0,.72,.36,1);ledp.inputs['Emission Strength'].default_value=1.3
def cube(name,loc,scale,ma,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=link(bpy.context.object); o.name=name; o.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(ma)
 if bevel:
  b=o.modifiers.new('Small softened edges','BEVEL'); b.width=bevel;b.segments=2
  o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o
def cyl(name,loc,r,depth,ma,vertices=20):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=r, depth=depth, location=loc); o=link(bpy.context.object);o.name=name;o.data.materials.append(ma); return o
def mesh(name,verts,faces,ma):
 me=bpy.data.meshes.new(name+'Mesh'); me.from_pydata(verts,[],faces); me.materials.append(ma); me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);return o
# OSM footprint-derived shell, local origin at polygon centroid.
n=len(poly); verts=[(x,y,z) for z in (0,3.45) for x,y in poly]; faces=[tuple(range(n-1,-1,-1))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
shell=mesh('Continuous footprint-derived exterior shell',verts,faces,wall)
# Concrete plinth/ribbon follows each edge; shallow roof slab and coping.
for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
 dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy); ang=math.atan2(dy,dx); mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
 cube('Foundation edge %02d'%i,(mid[0],mid[1],.12),(L+.04,.12,.24),concrete,.02).rotation_euler[2]=ang
 cube('Fascia edge %02d'%i,(mid[0],mid[1],3.52),(L+.35,.24,.34),trim,.025).rotation_euler[2]=ang
# membrane roof shaped to exact footprint; shallow overhanging apron as slight larger approximate slab
roofverts=[(x,y,3.68) for x,y in poly]
mesh('Low parapet flat roof plane (form inferred from low profile)',roofverts,[tuple(range(n))],roof)
# Low parapet panels, with slightly raised roof lip.
for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
 dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy); ang=math.atan2(dy,dx); mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
 cube('Parapet coping %02d'%i,(mid[0],mid[1],3.85),(L,.16,.18),trim,.015).rotation_euler[2]=ang
# Windows set in dark thin-framed rectangles on perimeter; intentionally schematic due no measured elevations.
def facade_panel(name,edge_index,t,width,z=1.65,height=1.25):
 a,b=poly[edge_index],poly[(edge_index+1)%n]; dx,dy=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dy); ang=math.atan2(dy,dx); px=a[0]+dx*t; py=a[1]+dy*t; nx=-dy/L; ny=dx/L
 # outward offset slightly from wall
 loc=(px+nx*.04,py+ny*.04,z)
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=link(bpy.context.object);o.name=name;o.dimensions=(width,.07,height);o.rotation_euler[2]=ang;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(glass)
 bevel=o.modifiers.new('Glazing edge bevel','BEVEL');bevel.width=.035;bevel.segments=2
 # perimeter frame as four bars in local façade axes, represented by thin trim bars
 for label,offset,dims in [('jambL',(-width/2-.045,0),( .08,.10,height+.10)),('jambR',(width/2+.045,0),(.08,.10,height+.10)),('head',(0,height/2+.04),(width+.16,.10,.08)),('sill',(0,-height/2-.04),(width+.16,.15,.10))]:
  xx=px+nx*.08+math.cos(ang)*offset[0]; yy=py+ny*.08+math.sin(ang)*offset[0]
  cube(name+' '+label,(xx,yy,z+offset[1]),dims,frame,.012).rotation_euler[2]=ang
 # central vertical mullion
 xx=px+nx*.09; yy=py+ny*.09
 cube(name+' mullion',(xx,yy,z),(.035,.11,height),frame,.008).rotation_euler[2]=ang
# Put irregular, light-reflective window groups on visible elevations; arrangement is inferred without a measured facade survey.
for edge,t,width in [(0,.32,1.35),(0,.68,1.35),(2,.33,1.2),(2,.70,1.2),(4,.30,1.25),(4,.68,1.25),(6,.35,1.35),(6,.70,1.35),(1,.55,1.0),(5,.52,1.0),(3,.16,1.55),(3,.83,1.30)]:
 facade_panel('Schematic exterior window',edge,t,width)
# Entrance on eastmost road-facing wall; inferred location. Existing public street preview supports a low light-colored profile but does not reveal the exact door/window pattern.
front_i=max(range(n),key=lambda i:(poly[i][0]+poly[(i+1)%n][0])/2)
a,b=poly[front_i],poly[(front_i+1)%n]; dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy); ang=math.atan2(dy,dx); nx,ny=-dy/L,dx/L; px,py=(a[0]+b[0])/2,(a[1]+b[1])/2
# A recessed-looking glazed door is framed by a clear projecting portal and canopy (inferred, not plan/photo measured).
facade_panel('Street entry glazed door',front_i,.51,1.18,z=1.23,height=2.38)
# portal frame, offset onto street side; horizontal dimensions follow facade edge
for label,offset in [('left',-.82),('right',.82)]:
 xx=px+nx*.16+math.cos(ang)*offset; yy=py+ny*.16+math.sin(ang)*offset
 cube('Entry portal '+label,(xx,yy,1.48),(.17,.18,2.95),trim,.025).rotation_euler[2]=ang
canopy=cube('Projecting entry canopy, inferred',(px+nx*.72,py+ny*.72,2.90),(2.25,1.05,.16),accent,.04);canopy.rotation_euler[2]=ang
for side in (-.88,.88):
 xx=px+nx*.84+math.cos(ang)*side; yy=py+ny*.84+math.sin(ang)*side
 cube('Canopy support post',(xx,yy,1.42),(.11,.11,2.82),trim,.02)
# metal pull and two engraved-looking sign panels are aligned to the street-facing wall
ex,ey=px+nx*.18,py+ny*.18
cube('Door vertical pull',(ex+math.cos(ang)*.40,ey+math.sin(ang)*.40,1.25),(.045,.055,.72),steel,.012).rotation_euler[2]=ang
# Small address plaque at eye level
plaque=cube('Address plaque 1827',(px+nx*.12+math.cos(ang)*1.45,py+ny*.12+math.sin(ang)*1.45,2.25),(.72,.09,.28),accent,.02);plaque.rotation_euler[2]=ang
num=bpy.data.curves.new('Street number lettering','FONT');num.body='1827';num.size=.17;num.align_x='CENTER';num.align_y='CENTER';num.extrude=.001
no=bpy.data.objects.new('Address lettering 1827',num);col.objects.link(no);no.location=(px+nx*.18+math.cos(ang)*1.45,py+ny*.18+math.sin(ang)*1.45,2.25);no.rotation_euler=(radians(90),0,ang+math.pi);no.data.materials.append(trim)
# Wall-mounted practice sign above/beside entry: legible from street camera, branding text verified by official site.
board=cube('Practice sign panel',(px+nx*.25+math.cos(ang)*2.7,py+ny*.25+math.sin(ang)*2.7,3.16),(4.25,.12,.44),trim,.025);board.rotation_euler[2]=ang
cu=bpy.data.curves.new('Practice sign lettering','FONT');cu.body='ZUNDO FAMILY DENTISTRY';cu.size=.29;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=.002
text=bpy.data.objects.new('Zundo Family Dentistry sign lettering',cu);col.objects.link(text);text.location=(px+nx*.325+math.cos(ang)*2.7,py+ny*.325+math.sin(ang)*2.7,3.16);text.rotation_euler=(radians(90),0,ang+math.pi);text.data.materials.append(accent)
# Corner piers and fine reveal bands articulate the office elevations; exact cladding joints are inferred.
for edge,(aa,bb) in enumerate(zip(poly,poly[1:]+poly[:1])):
 ddx,ddy=bb[0]-aa[0],bb[1]-aa[1]; ll=math.hypot(ddx,ddy); theta=math.atan2(ddy,ddx)
 if ll>5.0:
  for tt in (.025,.975):
   qx=aa[0]+ddx*tt; qy=aa[1]+ddy*tt
   pil=cube('Subtle facade corner pier %02d'%edge,(qx,qy,1.72),(.20,.22,3.35),trim,.025);pil.rotation_euler[2]=theta
  for zz in (.55,2.72):
   band=cube('Fine horizontal wall reveal %02d'%edge,((aa[0]+bb[0])/2,(aa[1]+bb[1])/2,zz),(ll,.04,.035),trim,.008);band.rotation_euler[2]=theta
# Ground / entry walk as compact apron; orient normal to street-facing façade.
walkloc=(px+nx*2.25,py+ny*2.25,.025)
cube('Concrete accessible entry walk',walkloc,(2.8,5.2,.09),concrete,.03).rotation_euler[2]=ang+math.pi/2
cube('Entry landing',(px+nx*.9,py+ny*.9,.07),(2.3,2.2,.14),concrete,.04).rotation_euler[2]=ang+math.pi/2
# Interior floor and simple reception / corridor / operatories, schematic layout inside uncertain shell.
# Place partitions approximately along long-axis direction; no clinical plan source exists.
mesh('Interior continuous light floor',[(x,y,.035) for x,y in poly],[tuple(range(n))],mat('Interior resilient floor',(.58,.56,.50),.78,noise_scale=46,noise_strength=.06))
# partition walls as precise simple aligned slabs
# Simple room zoning laid out in XY axis-aligned local extent; labeled in object names for clarity.
minx,maxx=min(p[0] for p in poly),max(p[0] for p in poly); miny,maxy=min(p[1] for p in poly),max(p[1] for p in poly)
# Schematic reception / corridor / four operatories; partition heights and organization are not from a floor plan.
# Corridor divider is interrupted for an opening; door leaf, head and jambs make the passage readable.
for cy in (-5.1,5.1): cube('Schematic corridor divider wall',(-.25,cy,1.48),(.12,8.8,2.9),interior,.025)
for xx in (-.25,.25): cube('Reception opening jamb',(xx,0,1.48),(.12,.12,2.9),trim,.015)
cube('Reception opening head',(-.25,0,2.68),(.12,1.0,.18),trim,.015)
door=cube('Reception corridor door leaf',(-.25,-.02,1.04),(.07,.82,2.08),wood,.025)
cube('Reception door vision lite',(-.20,-.02,1.58),(.025,.46,.48),glass,.01)
cyl('Reception door lever',(-.16,.24,1.02),.035,.12,steel,12).rotation_euler[0]=radians(90)
# Reception privacy return wall on the east wing with a doorway gap.
cube('Schematic reception privacy return',(5.35,-2.15,1.48),(.12,1.7,2.9),interior,.025)
cube('Schematic reception privacy return',(5.35,2.15,1.48),(.12,1.7,2.9),interior,.025)
# Three cross walls divide the western treatment rooms; door gaps are left beside corridor.
for yy in (-5.8,.1,6.0):
 cube('Schematic operatory partition',(-4.00,yy,1.48),(3.2,.12,2.9),interior,.025)
 # hinged door leaf, door casing, kick plate at the east end near circulation
 cube('Operatory door casing',( -1.97,yy,1.48),(.12,.13,2.35),trim,.02)
 leaf=cube('Operatory door leaf',(-1.90,yy,1.05),(.90,.075,2.08),wood,.025)
 cube('Operatory door vision lite',(-1.90,yy-.01,1.60),(.53,.025,.45),glass,.012)
 cyl('Operatory door lever',(-1.54,yy-.06,1.00),.03,.10,steel,12).rotation_euler[0]=radians(90)
# Waiting room seating at reception
for yy in (-1.45,1.45):
 cube('Waiting bench upholstered cushion',(6.65,yy,.56),(1.05,.72,.27),seat,.11)
 cube('Waiting bench back',(6.97,yy,1.02),(.22,.72,.72),seat,.10)
 for xoff in (-.38,.38): cube('Waiting bench leg',(6.65+xoff,yy,.28),(.08,.09,.50),steel,.02)
# Reception counter, monitor, and shelves
cube('Reception counter base',(6.25,0,.54),(2.1,.72,1.02),wood,.08)
cube('Reception counter stone top',(6.25,0,1.10),(2.25,.84,.12),trim,.025)
for yy in (-.24,0,.24): cube('Reception counter drawer reveal',(6.25,-.371,.55+yy),(.72,.022,.13),accent,.01)
cube('Reception monitor',(6.25,.32,1.59),(.62,.12,.36),frame,.02)
cube('Reception keyboard',(6.25,.18,1.31),(.42,.24,.035),steel,.01)
cube('Reception credenza',(7.35,3.7,.54),(1.35,.48,1.02),wood,.06)
cube('Reception credenza worktop',(7.35,3.7,1.09),(1.42,.55,.10),trim,.02)
# Four schematic treatment bays with chair, base, head rest, task lamp and instrument cart
for idx,(cx,cy) in enumerate([(-3.6,-8.8),(-3.6,-2.8),(-3.6,3.2),(-3.6,9.2)]):
 cube('Dental chair upholstered seat %d'%idx,(cx,cy,.65),(1.0,1.35,.34),seat,.15)
 cube('Dental chair back %d'%idx,(cx,cy-.58,1.12),(.92,.28,1.05),seat,.12).rotation_euler[0]=radians(-14)
 cyl('Dental chair pedestal %d'%idx,(cx,cy,.34),.22,.45,steel)
 cube('Dental equipment trolley %d'%idx,(cx-.95,cy+.3,.60),(.42,.45,.76),trim,.06)
 cyl('Task lamp arm base %d'%idx,(cx+.72,cy+.5,1.8),.05,.1,steel)
 cube('Dental operating lamp %d'%idx,(cx+.72,cy+.5,2.0),(.38,.38,.10),trim,.035)
 # paired upholstered arm pads, angled leg support, footrest, and fine task-light arm
 for side in (-.60,.60):
  cube('Dental chair arm support %d'%idx,(cx+side,cy+.03,.83),(.13,.62,.12),steel,.035)
  cube('Dental chair arm pad %d'%idx,(cx+side,cy+.03,.92),(.18,.65,.11),seat,.04)
 cube('Dental chair leg support %d'%idx,(cx,cy+.62,.54),(.65,.64,.18),seat,.08)
 cube('Dental chair head cushion %d'%idx,(cx,cy-.99,1.63),(.50,.23,.38),seat,.09)
 cyl('Dental chair lower base %d'%idx,(cx,cy,.12),.42,.12,steel,24)
 cube('Dental chair task-light arm %d'%idx,(cx+.82,cy+.50,1.86),(.045,.045,.55),steel,.015).rotation_euler[0]=radians(25)
 # operatory wall cabinet and basin, all furnishings deliberately schematic
 cube('Operatory base cabinet %d'%idx,(-5.25,cy+1.55,.54),(1.7,.52,1.02),wood,.06)
 cube('Operatory countertop %d'%idx,(-5.25,cy+1.55,1.08),(1.82,.62,.12),trim,.02)
 cube('Operatory upper cabinet %d'%idx,(-5.25,cy+1.60,2.45),(1.62,.38,.72),wood,.05)
 cyl('Operatory sink basin %d'%idx,(-5.25,cy+1.50,1.16),.22,.06,steel,24)
 cyl('Operatory sink faucet %d'%idx,(-5.25,cy+1.27,1.32),.035,.27,steel,12)
 # low-profile ceiling task-light panel and warm emission visible in bright roof-off view
 cube('Operatory ceiling task panel %d'%idx,(cx,cy,3.12),(.70,.48,.06),ledmat,.02)

# Decorative evergreen pot cluster near entry without claiming exact planting species
for j,offset in enumerate((-.9,1.15)):
 xx=px+nx*1.15+math.cos(ang)*offset; yy=py+ny*1.15+math.sin(ang)*offset
 cyl('Entry planter pot %d'%j,(xx,yy,.28),.34,.52,concrete,16)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.58,location=(xx,yy,.95));o=link(bpy.context.object);o.name='Low ornamental shrub %d'%j;o.scale=(.75,.75,1.15);o.data.materials.append(plantmat)
# The wall-mounted practice/address signs above are the evidence-backed identity elements.
# Presentation-only ground and neighborhood trees; kept outside export asset collection.
pres=bpy.data.collections.new('Preview_only_site_context_exclude_from_master');sc.collection.children.link(pres)
def preview_cube(name,loc,scale,ma):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object
 for c in list(o.users_collection):c.objects.unlink(o)
 pres.objects.link(o);o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma);return o
grass=mat('Preview grass',(.16,.22,.13),.95,noise_scale=18,noise_strength=.22)
preview_cube('Preview grass only',(0,0,-.17),(42,46,.18),grass)
# a few simple mature deciduous trees frame the modest single-storey office in the render only
for k,(tx,ty) in enumerate([(-15,-14),(-15,14),(15,14)]):
 bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.22,depth=4.4,location=(tx,ty,2.2)); trunk=bpy.context.object
 for c in list(trunk.users_collection):c.objects.unlink(trunk)
 pres.objects.link(trunk);trunk.name='Preview tree trunk %d'%k;trunk.data.materials.append(wood)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,radius=1,location=(tx,ty,5.4));o=bpy.context.object
 for c in list(o.users_collection):c.objects.unlink(o)
 pres.objects.link(o);o.name='Preview tree crown %d'%k;o.scale=(2.4,2.3,2.7);o.data.materials.append(plantmat)
# Multi-angle evidence views. Trees and site context stay outside the stable export collection.
world=bpy.data.worlds.new('Bright soft overcast documentation world');sc.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.64,.70,.78,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.72
ld=bpy.data.lights.new('Large soft key daylight','AREA');lo=bpy.data.objects.new('Large soft key daylight',ld);sc.collection.objects.link(lo);lo.location=(17,-14,24);ld.energy=3200;ld.shape='DISK';ld.size=16
filld=bpy.data.lights.new('Soft frontal fill','AREA');fill=bpy.data.objects.new('Soft frontal fill',filld);sc.collection.objects.link(fill);fill.location=(20,8,12);filld.energy=1700;filld.shape='DISK';filld.size=12
camd=bpy.data.cameras.new('Documentation camera');cam=bpy.data.objects.new('Documentation camera',camd);sc.collection.objects.link(cam);sc.camera=cam
camd.type='ORTHO';camd.lens=50
sc.render.engine='CYCLES';sc.cycles.samples=32
sc.render.resolution_x=1400;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG'
def aim_camera(loc,target=(0,0,1.45),scale=34):
 cam.location=loc;direction=Vector(target)-Vector(loc);cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();camd.ortho_scale=scale
preview_objs=list(pres.objects)
# Clear entry view of any preview tree; keep lawn only.
for o in preview_objs:
 if o.name.startswith('Preview tree'):o.hide_render=True
# Street-facing front view: eye-level, straight toward the eastern frontage and sign.
aim_camera((34,0,9.5),scale=34);sc.render.filepath=os.path.join(OUT,'zundo_r2_front.png');bpy.ops.render.render(write_still=True)
# Side/rear view, also unobstructed; east road front shifts behind the camera.
for o in preview_objs:
 if o.name.startswith('Preview tree'):o.hide_render=False
# keep trees far from the south-west rear camera's sightline by hiding those on the building perimeter
for o in preview_objs:
 if o.name.startswith('Preview tree'):o.hide_render=True
aim_camera((-29,-29,15),scale=37);sc.render.filepath=os.path.join(OUT,'zundo_r2_side_rear.png');bpy.ops.render.render(write_still=True)
# Bright roof-off schematic interior: top-down with ground/trees suppressed for an unobstructed plan read.
for o in preview_objs:o.hide_render=True
roof_objs=[o for o in col.objects if ('roof' in o.name.lower() or 'parapet coping' in o.name.lower())]
for o in roof_objs:o.hide_render=True
world.node_tree.nodes['Background'].inputs['Strength'].default_value=1.0
for light in (ld,filld):light.energy*=1.35
# softer fill from overhead reduces hard partitions' shadows
insd=bpy.data.lights.new('Interior roof-off fill','AREA');ins=bpy.data.objects.new('Interior roof-off fill',insd);sc.collection.objects.link(ins);ins.location=(0,0,22);insd.energy=2500;insd.shape='DISK';insd.size=24
aim_camera((0,0,36),(0,0,0),34);sc.render.filepath=os.path.join(OUT,'zundo_r2_roof_off.png');bpy.ops.render.render(write_still=True)
# restore exterior camera/roof, keep preview trees non-obstructive in delivered scene and save R2
for o in roof_objs:o.hide_render=False
for o in preview_objs:
 if o.name.startswith('Preview tree'):o.hide_render=True
cam.location=(34,0,9.5);aim_camera((34,0,9.5),scale=34)
sc.render.filepath=os.path.join(OUT,'zundo_r2_front.png')
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
# Count and report local bounds of mesh-like geometry
from mathutils import Vector
objs=[o for o in col.objects if o.type in {'MESH','CURVE'}]
pts=[]
for o in objs:
 if o.type=='MESH': pts += [o.matrix_world @ v.co for v in o.data.vertices]
 else:
  for bb in o.bound_box: pts.append(o.matrix_world @ Vector(bb))
mins=[min(p[i] for p in pts) for i in range(3)]; maxs=[max(p[i] for p in pts) for i in range(3)]
report={'asset':os.path.relpath(ASSET,ROOT).replace('\\','/'),'scene':sc.name,'collection':col.name,'local_placement_origin_xy_m':[round(origin[0],6),round(origin[1],6)],'local_bounds_m':[[round(mins[0],4),round(maxs[0],4)],[round(mins[1],4),round(maxs[1],4)],[round(mins[2],4),round(maxs[2],4)]],'mesh_object_count':sum(o.type=='MESH' for o in col.objects),'curve_object_count':sum(o.type=='CURVE' for o in col.objects),'object_count':len(col.objects),'material_count':len([m for m in bpy.data.materials if m.users>0]),'footprint_source':'OSM way 887558318; exact eight-node ring transformed through project local approximation','placement_origin_description':'OSM polygon shoelace centroid projected from geographic vertices using modular/AGENTS.md local transform; the master Placement marker must use these campus XY meters when replacing massing.'}
with open(os.path.join(OUT,'build_metrics_r2.json'),'w') as f:json.dump(report,f,indent=2)
print('ZUNDO_METRICS',json.dumps(report))







