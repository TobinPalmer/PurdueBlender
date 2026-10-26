import bpy, math, json, os
from mathutils import Vector
from math import radians, cos
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'zundo_family_dentistry.blend')
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
  nt=m.node_tree; tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=noise_scale; tex.inputs['Detail'].default_value=3; bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=noise_strength; bump.inputs['Distance'].default_value=.06; nt.links.new(tex.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 return m
wall=mat('Warm white painted fiber-cement / stucco (inferred)',(.72,.70,.64),.83,noise_scale=38,noise_strength=.09)
trim=mat('Soft white fascia and trim',(.88,.86,.80),.64)
roof=mat('Charcoal low-slope membrane roof (inferred)',(.13,.15,.16),.88,noise_scale=52,noise_strength=.10)
concrete=mat('Broom-finished concrete',(.43,.44,.42),.9,noise_scale=70,noise_strength=.16)
glass=mat('Reflective blue-gray glazing',(.055,.12,.16),.2,.34)
frame=mat('Dark bronze window frames',(.12,.14,.14),.32,.65)
wood=mat('Warm wood interior cabinetry',(.38,.23,.13),.56)
interior=mat('Warm off-white interior partitions',(.82,.79,.71),.9)
seat=mat('Muted teal upholstery',(.035,.25,.25),.55)
steel=mat('Brushed stainless equipment',(.48,.54,.56),.28,.75)
plantmat=mat('Landscape evergreen',(.10,.22,.12),.92,noise_scale=9,noise_strength=.2)
accent=mat('Quiet dental office sign bronze',(.22,.25,.25),.35,.45)
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
# Put glazing on several wall spans; pattern sparse/office-like.
for edge,t,width in [(0,.32,1.35),(0,.68,1.35),(2,.33,1.2),(2,.70,1.2),(4,.30,1.25),(4,.68,1.25),(6,.35,1.35),(6,.70,1.35),(1,.55,1.0),(5,.52,1.0)]:
 facade_panel('Schematic exterior window',edge,t,width)
# Entrance on eastmost long wall; glazing pair and accessibility landing. Identify edge at most positive x.
front_i=max(range(n),key=lambda i:(poly[i][0]+poly[(i+1)%n][0])/2)
a,b=poly[front_i],poly[(front_i+1)%n]; dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy); ang=math.atan2(dy,dx); nx,ny=dy/L,-dx/L; px,py=(a[0]+b[0])/2,(a[1]+b[1])/2
# Entry glazing bay
facade_panel('Main entry glazed door panel',front_i,.51,1.55,z=1.45,height=2.45)
# simple door pull and address plaque on approach-facing side
ex,ey=px+nx*.15,py+ny*.15
cube('Door pull',(ex+math.cos(ang)*.42,ey+math.sin(ang)*.42,1.4),(.045,.06,.75),steel,.015).rotation_euler[2]=ang
cube('Address plaque backing',(ex+math.cos(ang)*1.05,ey+math.sin(ang)*1.05,2.25),(.72,.08,.30),accent,.025).rotation_euler[2]=ang
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
# Interior partition layout leaves patient reception toward east/street-facing front.
cube('Schematic corridor separation partition',(-.25,0,1.48),(.12,19.0,2.9),interior,.02)
cube('Schematic reception privacy wall',(5.35,0,1.48),(.12,6.0,2.9),interior,.02)
for yy in (-5.8,.1,6.0): cube('Schematic operatory partition',(-3.5,yy,1.48),(4.2,.12,2.9),interior,.02)
# Waiting room seating at reception
for yy in (-2.0,.4,2.8):
 cube('Reception waiting seat cushion',(5.7,yy,.50),(1.65,.68,.32),seat,.11)
 for xoff in (.12,1.42): cube('Waiting seat leg',(5.7+xoff,yy,.25),(.08,.08,.5),steel,.02)
# Reception counter, monitor, and shelves
cube('Reception counter base',(5.2,0,.56),(2.1,.72,1.05),wood,.08)
cube('Reception counter stone top',(5.2,0,1.12),(2.22,.82,.12),trim,.025)
cube('Reception monitor',(5.2,.3,1.62),(.55,.12,.38),frame,.02)
# Four schematic treatment bays with chair, base, head rest, task lamp and instrument cart
for idx,(cx,cy) in enumerate([(-3.6,-8.8),(-3.6,-2.8),(-3.6,3.2),(-3.6,9.2)]):
 cube('Dental chair upholstered seat %d'%idx,(cx,cy,.65),(1.0,1.35,.34),seat,.15)
 cube('Dental chair back %d'%idx,(cx,cy-.58,1.12),(.92,.28,1.05),seat,.12).rotation_euler[0]=radians(-14)
 cyl('Dental chair pedestal %d'%idx,(cx,cy,.34),.22,.45,steel)
 cube('Dental equipment trolley %d'%idx,(cx-.95,cy+.3,.60),(.42,.45,.76),trim,.06)
 cyl('Task lamp arm base %d'%idx,(cx+.72,cy+.5,1.8),.05,.1,steel)
 cube('Dental operating lamp %d'%idx,(cx+.72,cy+.5,2.0),(.32,.32,.09),trim,.03)
# Decorative evergreen pot cluster near entry without claiming exact planting species
for j,offset in enumerate((-.9,1.15)):
 xx=px+nx*1.15+math.cos(ang)*offset; yy=py+ny*1.15+math.sin(ang)*offset
 cyl('Entry planter pot %d'%j,(xx,yy,.28),.34,.52,concrete,16)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.58,location=(xx,yy,.95));o=link(bpy.context.object);o.name='Low ornamental shrub %d'%j;o.scale=(.75,.75,1.15);o.data.materials.append(plantmat)
# Sign set parallel to entry with non-assertive practice lettering
cube('Practice sign panel',(px+nx*3.8,py+ny*3.8,1.25),(1.5,.16,1.0),trim,.06)
# text facing roughly street side (text plane local XY; text default lies local XY, orient vertical)
cu=bpy.data.curves.new('Zundo office lettering','FONT');cu.body='ZUNDO\nFAMILY DENTISTRY';cu.size=.16;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=.002
text=bpy.data.objects.new('Zundo Family Dentistry lettering',cu);col.objects.link(text);text.location=(px+nx*3.8,py+ny*3.8-.095,1.25);text.rotation_euler=(radians(90),0,ang);text.data.materials.append(accent)
# Presentation-only ground and neighborhood trees; kept outside export asset collection.
pres=bpy.data.collections.new('Preview_only_site_context_exclude_from_master');sc.collection.children.link(pres)
def preview_cube(name,loc,scale,ma):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object
 for c in list(o.users_collection):c.objects.unlink(o)
 pres.objects.link(o);o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma);return o
grass=mat('Preview grass',(.16,.22,.13),.95,noise_scale=18,noise_strength=.22)
preview_cube('Preview grass only',(0,0,-.17),(42,46,.18),grass)
# a few simple mature deciduous trees frame the modest single-storey office in the render only
for k,(tx,ty) in enumerate([(-12,-9),(12,9),(-11,12),(12,-12)]):
 cyl('Preview tree trunk %d'%k,(tx,ty,2.2),.22,4.4,wood,12)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,radius=1,location=(tx,ty,5.4));o=bpy.context.object
 for c in list(o.users_collection):c.objects.unlink(o)
 pres.objects.link(o);o.name='Preview tree crown %d'%k;o.scale=(2.4,2.3,2.7);o.data.materials.append(plantmat)
# Lighting and render for inspection
world=bpy.data.worlds.new('Soft overcast studio world');sc.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.55,.62,.72,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
ld=bpy.data.lights.new('Large soft daylight','AREA');lo=bpy.data.objects.new('Large soft daylight',ld);sc.collection.objects.link(lo);lo.location=(15,-18,27);ld.energy=2600;ld.shape='DISK';ld.size=18
camd=bpy.data.cameras.new('Exterior documentation camera');cam=bpy.data.objects.new('Exterior documentation camera',camd);sc.collection.objects.link(cam);sc.camera=cam
cam.location=(31,-35,24);target=Vector((0,0,1.25)); direction=target-Vector(cam.location);cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=40;camd.lens=50
sc.render.engine='CYCLES';sc.cycles.samples=24
sc.render.resolution_x=1200;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.render.image_settings.file_format='PNG';sc.render.filepath=os.path.join(OUT,'zundo_exterior_candidate.png')
# Save file with all render dependencies procedural/local, then render & save.
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.render.render(write_still=True)
# Additional schematic interior cutaway image; roof hidden only for this review render and restored before save/reopen validation.
roof_objs=[o for o in col.objects if ('roof' in o.name.lower() or 'parapet coping' in o.name.lower())]
for o in roof_objs:o.hide_render=True
saved_cam_loc=cam.location.copy();saved_cam_rot=cam.rotation_euler.copy(); saved_scale=camd.ortho_scale
cam.location=(0,0,34);cam.rotation_euler=(0,0,0);camd.ortho_scale=34
sc.render.filepath=os.path.join(OUT,'zundo_interior_schematic.png');bpy.ops.render.render(write_still=True)
for o in roof_objs:o.hide_render=False
cam.location=saved_cam_loc;cam.rotation_euler=saved_cam_rot;camd.ortho_scale=saved_scale;sc.render.filepath=os.path.join(OUT,'zundo_exterior_candidate.png')
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
with open(os.path.join(OUT,'build_metrics.json'),'w') as f:json.dump(report,f,indent=2)
print('ZUNDO_METRICS',json.dumps(report))






