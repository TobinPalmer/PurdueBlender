import bpy,os,math
from mathutils import Vector
import bmesh
p=os.path.abspath('modular/buildings/krannert_building.blend');bpy.ops.wm.open_mainfile(filepath=p)
C=bpy.data.collections['Asset_krannert_building'];root=bpy.data.objects['AssetRoot_krannert_building']
# R2 can be repeated: clear only R2 objects, leaving the R1 asset and source geometry intact.
for o in list(C.objects):
 if o.name.startswith('KRAN_R2_'):bpy.data.objects.remove(o,do_unlink=True)

# Convert the lower-right open-table bay to an upholstered lounge zone, matching
# the Drawing Room's documented mixture of lounge and work settings. The old
# table/chairs in this bounded bay are removed so the new seating does not overlap.
for o in list(C.objects):
 if o.name.startswith(('KRAN_New_', 'KRAN_R1_DrawingRoom_Divider_')) and -13.0 < o.location.x < -9.0 and -7.6 < o.location.y < -4.0 and o.location.z < 6.0:
  bpy.data.objects.remove(o, do_unlink=True)

def material(name,color,rough=.7,metal=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 return m
# Fine procedural grain and upholstery weave keep these additions portable and avoid exaggerated bump.
def texture(m,scale=100,contrast=None,bumpdist=.0006):
 nt=m.node_tree;ns=nt.nodes;ls=nt.links;bs=ns.get('Principled BSDF')
 tex=next((n for n in ns if n.type=='TEX_COORD'),None) or ns.new('ShaderNodeTexCoord')
 noise=next((n for n in ns if n.label=='R2 subtle material texture'),None)
 if noise is None:
  noise=ns.new('ShaderNodeTexNoise');noise.label='R2 subtle material texture';noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.72;ls.new(tex.outputs['Object'],noise.inputs['Vector'])
 else:noise.inputs['Scale'].default_value=scale
 bump=next((n for n in ns if n.label=='R2 microtexture'),None)
 if bump is None:
  bump=ns.new('ShaderNodeBump');bump.label='R2 microtexture';bump.inputs['Distance'].default_value=bumpdist;bump.inputs['Strength'].default_value=.22;ls.new(noise.outputs['Fac'],bump.inputs['Height']);ls.new(bump.outputs['Normal'],bs.inputs['Normal'])
 ramp=next((n for n in ns if n.label=='R2 finish variation'),None)
 if contrast and ramp is None:
  ramp=ns.new('ShaderNodeValToRGB');ramp.label='R2 finish variation';ramp.color_ramp.elements[0].position=.22;ramp.color_ramp.elements[0].color=(*contrast[0],1);ramp.color_ramp.elements[1].position=.78;ramp.color_ramp.elements[1].color=(*contrast[1],1);ls.new(noise.outputs['Fac'],ramp.inputs[0]);ls.new(ramp.outputs['Color'],bs.inputs['Base Color'])
 return m
bluefabric=bpy.data.materials['KRAN_DrawingRoom_BlueFabric'];limefabric=bpy.data.materials['KRAN_DrawingRoom_LimeFabric'];oak=bpy.data.materials['KRAN_Photo_Oak']
for m in [bluefabric,limefabric]:texture(m,180,None,.00045)
lightoak=material('KRAN_R2_Parrish_Light_Oak',(.48,.30,.14),.48);texture(lightoak,5,((.34,.18,.07),(.60,.40,.22)),.0004)
softblue=material('KRAN_R2_DrawingRoom_Modular_Blue',(.08,.22,.36),.84);texture(softblue,145,((.035,.12,.24),(.18,.34,.47)),.00035)
pattern=material('KRAN_R2_DrawingRoom_Patterned_Upholstery',(.12,.22,.32),.87);texture(pattern,48,((.08,.15,.22),(.24,.32,.38)),.0003)
carpet=material('KRAN_R2_Area_Carpet',(.20,.22,.23),.96);texture(carpet,135,((.15,.17,.18),(.24,.26,.27)),.0008)
metal=material('KRAN_R2_Furniture_Metal',(.28,.30,.31),.3,.68)
glass=material('KRAN_R2_Conference_Glass',(.38,.60,.67),.16,.12)
gp=glass.node_tree.nodes.get('Principled BSDF');gp.inputs['Transmission Weight'].default_value=.72;gp.inputs['Alpha'].default_value=.28
try: glass.surface_render_method='DITHERED'
except Exception: pass
frame=material('KRAN_R2_Conference_Frame',(.42,.44,.43),.28,.6)
monitor=material('KRAN_R2_Monitor_Black',(.009,.016,.021),.22,.18)
white=material('KRAN_R2_Table_Light_Laminate',(.70,.69,.63),.42)

def box(name,loc,dim,mat,bevel=.02,rot=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name='KRAN_R2_'+name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.rotation_euler[2]=rot
 for cc in list(o.users_collection):cc.objects.unlink(o)
 C.objects.link(o);o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted();o.data.materials.append(mat)
 if bevel:
  b=o.modifiers.new('Rounded product edge','BEVEL');b.width=bevel;b.segments=4;o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 o['layout_status']='Photo-supported furniture or room element; exact coordinates, counts, sizes, and circulation remain estimated without a measured interior plan.'
 return o

def cyl(name,loc,r,depth,mat,verts=20):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name='KRAN_R2_'+name
 for cc in list(o.users_collection):cc.objects.unlink(o)
 C.objects.link(o);o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted();o.data.materials.append(mat);b=o.modifiers.new('Soft machined edge','BEVEL');b.width=.012;b.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');o['layout_status']='Photo-supported furniture detail; approximate local placement and dimensions.'
 return o

def annular_arc(name,cx,cy,z0,z1,r0,r1,a0,a1,mat,steps=60):
 verts=[]
 for k in range(steps+1):
  a=math.radians(a0+(a1-a0)*k/steps)
  for z in (z0,z1):
   for r in (r0,r1):verts.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
 faces=[]
 for k in range(steps):
  b=4*k;n=b+4
  faces.extend([(b,n,n+2,b+2),(b+1,b+3,n+3,n+1),(b+2,n+2,n+3,b+3),(b,b+1,n+1,n)])
 faces.extend([(0,2,3,1),(4*steps,4*steps+1,4*steps+3,4*steps+2)])
 me=bpy.data.meshes.new('R2 curved front counter solid');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new('KRAN_R2_'+name,me);C.objects.link(ob);ob.parent=root;ob.matrix_parent_inverse=root.matrix_world.inverted();ob.data.materials.append(mat)
 bev=ob.modifiers.new('Soft finished counter edges','BEVEL');bev.width=.018;bev.segments=3;ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL');ob['layout_status']='Curved library desk supported as a room type by Purdue 2026 facility-refresh photo; exact local placement and dimensions are estimates.'
 return ob

# Update the old straight library counter to a curved front desk shown in Purdue Libraries' June 2026 refresh imagery.
for o in list(C.objects):
 if o.name.startswith('KRAN_R1_Parrish_Counter_'):bpy.data.objects.remove(o,do_unlink=True)
cx,cy=-14.5,3.8
annular_arc('Parrish_Curved_Desk_Base',cx,cy,8.56,9.57,2.96,3.24,205,335,lightoak)
annular_arc('Parrish_Curved_Desk_Worktop',cx,cy,9.57,9.69,2.90,3.33,205,335,white)
annular_arc('Parrish_Curved_Desk_Wood_Lip',cx,cy,9.68,9.76,2.89,3.35,205,335,lightoak)
# Fine vertical oak divisions lend scale to the front desk; they follow the documented curved face.
for k in range(33):
 a=math.radians(207+k*128/32);r=3.25
 ob=box('Parrish_Desk_Front_Slat',(cx+r*math.cos(a),cy+r*math.sin(a),9.06),(.028,.035,.92),material('KRAN_R2_Desk_Slat',(.53,.35,.18),.48),.006,a+math.pi/2)
# Lightly sinuous collaborative table, consistent with the official library-refresh description; local path is illustrative.
N=48;verts=[];faces=[];pathpoints=[]
for i in range(N+1):
 t=i/N;x=-19.3+10.0*t;y=-2.25+.68*math.sin(2*math.pi*t);dx=10.0;dy=.68*2*math.pi*math.cos(2*math.pi*t);ln=math.hypot(dx,dy);nx=-dy/ln;ny=dx/ln
 pathpoints.append((x,y));
 for side in [-.62,.62]:verts.append((x+nx*side,y+ny*side,9.33))
for i in range(N):faces.append((2*i,2*i+1,2*i+3,2*i+2))
me=bpy.data.meshes.new('R2 winding shared table top');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
table=bpy.data.objects.new('KRAN_R2_Parrish_Winding_Study_Table',me);C.objects.link(table);table.parent=root;table.matrix_parent_inverse=root.matrix_world.inverted();table.data.materials.append(white);sol=table.modifiers.new('Solid oak/laminate tabletop','SOLIDIFY');sol.thickness=.07;sol.offset=-1;bev=table.modifiers.new('Rounded continuous edge','BEVEL');bev.width=.045;bev.segments=4;table['layout_status']='Purdue Libraries June 2026 refresh article labels a long winding Parrish study table; this spline and exact local placement/dimensions are illustrative estimates.'
# Six metal column pedestals below the continuous table at measured-looking but explicitly inferred intervals.
for i in [4,12,20,28,36,44]:
 x,y=pathpoints[i];cyl('Parrish_Table_Pedestal',(x,y,8.94),.055,.72,metal);box('Parrish_Table_Foot',(x,y,8.58),(.54,.42,.05),metal,.02)
# Four workstations with subdued dark monitors and small keyboards confirm the current public-computer function.
for i in [8,19,30,41]:
 x,y=pathpoints[i];cxm=x; cym=y-.07
 box('Parrish_Monitor_Screen',(cxm,cym,9.89),(.60,.055,.38),monitor,.035)
 box('Parrish_Monitor_Bezel',(cxm,cym-.035,9.89),(.66,.025,.43),frame,.035)
 cyl('Parrish_Monitor_Stand',(cxm,cym,9.57),.035,.28,metal,12)
 box('Parrish_Monitor_Foot',(cxm,cym,9.47),(.28,.20,.025),metal,.01)
 box('Parrish_Keyboard',(cxm,y-.34,9.39),(.34,.12,.025),monitor,.012)
# A few rolling-style study chairs with clearly rounded upholstery, arms and star bases.
for i in [9,18,31,40]:
 x,y=pathpoints[i]; yy=y+1.0
 cyl('Parrish_Chair_Base',(x,yy,8.67),.30,.06,metal,24);cyl('Parrish_Chair_Post',(x,yy,8.91),.04,.46,metal,16)
 box('Parrish_Chair_Seat',(x,yy,9.12),(.66,.62,.16),softblue,.10)
 box('Parrish_Chair_Back',(x,yy+.26,9.56),(.62,.14,.78),softblue,.13)
 for side in [-1,1]:box('Parrish_Chair_Arm',(x+side*.34,yy,9.31),(.09,.48,.10),metal,.035)
# Round-2 Drawing Room enhancement: a compact glass-walled group room is explicitly supported by the designer's write-up.
# Its bounds stay within the modeled room; the south-side door opens to a clear approach aisle.
zbase=3.90;top=zbase+2.45;roomxmin,roomxmax=-12.2,-7.8;ymin,ymax=-.15,3.55
for x in [roomxmin,roomxmax]:
 box('DrawingRoom_Glass_Panel',(x,(ymin+ymax)/2,(zbase+top)/2),(.055,ymax-ymin,top-zbase),glass,.008)
 for yy in [ymin,(ymin+ymax)/2,ymax]:box('DrawingRoom_Glass_Mullion',(x,yy,(zbase+top)/2),(.075,.045,top-zbase),frame,.008)
for yy in [ymax]:
 box('DrawingRoom_Glass_Panel',((roomxmin+roomxmax)/2,yy,(zbase+top)/2),(roomxmax-roomxmin,.055,top-zbase),glass,.008)
 for xx in [roomxmin,(roomxmin+roomxmax)/2,roomxmax]:box('DrawingRoom_Glass_Mullion',(xx,yy,(zbase+top)/2),(.045,.075,top-zbase),frame,.008)
# South/front wall leaves a 1m doorway in the middle.
for x in [-11.55,-8.45]:
 box('DrawingRoom_Glass_Panel',(x,ymin,(zbase+top)/2),(1.30,.055,top-zbase),glass,.008)
for x in [roomxmin,-11.55,-8.45,roomxmax]:box('DrawingRoom_Glass_Mullion',(x,ymin,(zbase+top)/2),(.045,.075,top-zbase),frame,.008)
box('DrawingRoom_Glass_Door',(-10.0,ymin-.015,zbase+1.05),(.90,.045,2.1),glass,.008)
box('DrawingRoom_Door_Pull',(-9.66,ymin-.06,zbase+1.05),(.025,.06,.55),metal,.01)
# Conference room kit: modest elliptical-ended table, task seats, tabletop screen and chair backs.
box('DrawingRoom_Conference_Table',(-10.0,2.02,4.78),(2.8,.95,.10),oak,.06)
for x in [-11.0,-10.0,-9.0]:
 for y in [1.48,2.55]:
  cyl('Conference_Table_Leg',(x,y,4.32),.045,.84,metal,16)
for x,y in [(-11.0,.90),(-10.0,.90),(-9.0,.90),(-11.0,3.00),(-10.0,3.00),(-9.0,3.00)]:
 box('Conference_Chair_Seat',(x,y,4.42),(.52,.54,.12),pattern,.08)
 box('Conference_Chair_Back',(x,y+.23,4.79),(.52,.12,.62),pattern,.09)
 for dx in [-.19,.19]:
  for dy in [-.19,.19]:box('Conference_Chair_Leg',(x+dx,y+dy,4.17),(.025,.025,.42),metal,.008)
# Textile drape and softened shapes on existing block chairs and acoustic screens.
for o in list(C.objects):
 if o.type!='MESH':continue
 if o.name.startswith(('KRAN_New_Seat','KRAN_New_Back')):
  for m in o.modifiers:
   if m.type=='BEVEL' and m.name=='Photo-supported eased edges':m.width=.075 if o.name.startswith('KRAN_New_Seat') else .065;m.segments=4
 if o.name.startswith('KRAN_New_AcousticBlueDivider'):
  for m in o.modifiers:
   if m.type=='BEVEL' and m.name=='Photo-supported eased edges':m.width=.045;m.segments=4
# Two modular soft-seating groups: rounded segmented backs/cushions, evidence-backed by OfficeWorks' photo/write-up.
def sofa(cx,cy,z,label,angle=0):
 for j,off in enumerate([-1,0,1]):
  rad=math.radians(angle);xx=cx+off*.78*math.cos(rad);yy=cy+off*.78*math.sin(rad)
  box(label+'_Seat',(xx,yy,z+.40),(.82,.78,.25),softblue,.12,rad)
  box(label+'_Back',(xx-.10*math.sin(rad),yy+.33*math.cos(rad),z+.88),(.82,.22,.82),softblue,.14,rad)
 for side in [-1,1]:
  rad=math.radians(angle);xx=cx+side*1.27*math.cos(rad);yy=cy+side*1.27*math.sin(rad)
  box(label+'_Arm',(xx,yy,z+.67),(.30,.85,.60),pattern,.12,rad)
 box(label+'_Plinth',(cx,cy,z+.17),(2.4,.72,.18),lightoak,.04,math.radians(angle))
sofa(-11.0,-6.0,3.9,'DrawingRoom_Modular_Lounge_A',-4)
# A paired low lounge bench and coffee table create a second seating type while
# preserving the main east-west route through the remaining open floor.
box('DrawingRoom_Lounge_Bench_Base',(-16.2,-6.7,4.08),(2.25,.74,.22),lightoak,.08)
box('DrawingRoom_Lounge_Bench_Cushion',(-16.2,-6.7,4.24),(2.18,.70,.16),softblue,.10)
box('DrawingRoom_Lounge_Bench_Back',(-16.2,-6.32,4.72),(2.20,.18,.78),pattern,.12)
box('DrawingRoom_Lounge_CoffeeTable',(-16.2,-5.45,4.42),(1.45,.55,.08),white,.06)
for x in [-16.75,-15.65]:cyl('Lounge_CoffeeTable_Pedestal',(x,-5.45,4.17),.035,.46,metal,16)
# Side tables with visible round edges add varied small-scale furnishings without crowding the main route.
for x,y in [(-18.4,-6.7),(-8.4,-6.0)]:
 cyl('DrawingRoom_Round_SideTable_Top',(x,y,4.44),.38,.06,oak,48);cyl('DrawingRoom_Round_SideTable_Pedestal',(x,y,4.16),.05,.50,metal,18);cyl('DrawingRoom_Round_SideTable_Foot',(x,y,3.91),.27,.05,metal,32)

# Give remaining source-model chair seats a separate rounded upholstery pad and
# visible cushion seam. Seat positions vary by story, so use each saved seat's
# own bounds rather than imposing a single floor plan.
for chair in [o for o in list(C.objects) if o.name.startswith('KRAN_New_Seat') and o.type=='MESH']:
 bb=[chair.matrix_world @ Vector(c) for c in chair.bound_box]
 lo=Vector((min(v.x for v in bb),min(v.y for v in bb),min(v.z for v in bb)));hi=Vector((max(v.x for v in bb),max(v.y for v in bb),max(v.z for v in bb)))
 cx0,cy0,cz0=(lo+hi)*.5; dims=hi-lo
 # Small eased cushion top is a visible upholstery layer, not a replacement seat.
 pad=box('Chair_Upholstery_Pad',(cx0,cy0,hi.z+.028),(max(.24,dims.x*.84),max(.24,dims.y*.84),.045),softblue,.035)
 pad['layout_status']='Added upholstery layer over a source-model chair; estimated thickness and material finish.'

# Two window-side high tables and stools are explicitly identified in the
# Drawing Room case study and diversify the work settings without filling aisles.
for idx,x in enumerate([-18.2,-15.6]):
 box('DrawingRoom_Window_HighTop',(x,2.10,4.97),(.95,.72,.08),lightoak,.045)
 cyl('DrawingRoom_HighTop_Pedestal',(x,2.10,4.43),.055,.98,metal,20)
 cyl('DrawingRoom_HighTop_Foot',(x,2.10,3.94),.32,.06,metal,24)
 for dx in [-.48,.48]:
  box('DrawingRoom_HighStool_Seat',(x+dx,2.10,4.62),(.40,.40,.10),pattern,.06)
  cyl('DrawingRoom_HighStool_Pedestal',(x+dx,2.10,4.26),.035,.67,metal,16)
  cyl('DrawingRoom_HighStool_Foot',(x+dx,2.10,3.94),.22,.06,metal,20)
  bpy.ops.mesh.primitive_torus_add(major_radius=.15,minor_radius=.014,major_segments=24,minor_segments=8,location=(x+dx,2.10,4.18))
  ring=bpy.context.object;ring.name='KRAN_R2_DrawingRoom_HighStool_FootRing'
  for cc in list(ring.users_collection):cc.objects.unlink(ring)
  C.objects.link(ring);ring.parent=root;ring.matrix_parent_inverse=root.matrix_world.inverted();ring.data.materials.append(metal);ring['layout_status']='Estimated bar-stool foot ring for the photo-supported high-top seating type.'
# Add evidence/status labels without claiming a surveyed layout.
s=bpy.context.scene
s['krannert_round2_sources']='Purdue Libraries 2026 Parrish refresh (https://blogs.lib.purdue.edu/news/2026/06/08/parrish-library-undergoing-renovations-and-facility-improvements/): curved front desk, winding study table, new carpet/furniture and computers in public areas; OfficeWorks Drawing Room case study (https://officeworks.net/projects/purdue-universitys-krannert-school-of-management-drawing-room): glass-walled conference rooms, varied lounges/booths/high-top tables and stools.'
s['krannert_round2_uncertainty']='Post-refresh as-built floor plans were not located. Room XY, sizes, counts, partition position, furniture arrangement, and computer placement are visual/functional estimates. The 2026 Parrish article includes refresh previews and describes renovation underway; it does not establish as-built measurements.'
s['interiors_status']='Drawing Room and Parrish Library furnished with photo-supported room types; room arrangement remains schematic. Other rooms and floors are not reconstructed.'
bpy.ops.wm.save_as_mainfile(filepath=p)
print('Saved round2 source',len(C.objects),'objects; added R2',sum(o.name.startswith('KRAN_R2_') for o in C.objects))
