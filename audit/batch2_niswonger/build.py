import bpy,bmesh,math,json,shutil
from mathutils import Vector
from pathlib import Path
P=Path('audit/batch2_niswonger');path=Path(bpy.data.filepath)
if not (P/'before.blend').exists():shutil.copy2(path,P/'before.blend')
c=bpy.data.collections['Asset_niswonger_aviation_tech'];ref=bpy.data.collections.new('NISW_Previous_Unverified_Reference');bpy.context.scene.collection.children.link(ref);ref.hide_render=True;ref.hide_viewport=True
removed=[]
for o in list(c.all_objects):
 if o.name.startswith(('NISW_Interior_Shell_Unverified','NISW_RTU','NISW_Chiller','NISW_Rooftop','NISW_Roof_Access','NISW_Official_Footprint')):
  for co in list(o.users_collection):co.objects.unlink(o)
  ref.objects.link(o);removed.append(o.name)
# Photographic relative heights indicate single-story classrooms and a raised clerestory, not four stories.
for o in c.all_objects:
 if o.type=='MESH':
  for v in o.data.vertices:v.co.z*=.50
 elif o.type=='FONT':o.location.z*=.50
# Original curved roof unsupported; retain in reference, replace by single sloping metal profile photographed by architect.
o=bpy.data.objects.get('NISW_Aerodynamic_Curved_Roof')
for co in list(o.users_collection):co.objects.unlink(o)
ref.objects.link(o)
def mat(n,col,rough=.6,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
white=mat('NISW_Photographic_Offwhite_Plaster',(.72,.69,.61));orange=mat('NISW_Photographic_Terracotta_Panels',(.40,.12,.045));black=mat('NISW_Seat_Upholstery',(.025,.029,.035));desk=mat('NISW_Lecture_Desk_Laminate',(.65,.62,.53));metal=mat('NISW_Satin_Metal',(.38,.42,.43),.28,.7)
floor=mat('NISW_Terrazzo_Tile_MetreScale',(.27,.25,.22),.32)
n=floor.node_tree.nodes;l=floor.node_tree.links;t=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=85;l.new(t.outputs['Object'],noise.inputs['Vector']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.003;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
brick=bpy.data.materials['NISW_Purdue_Red_Brick'];brick.diffuse_color=(.36,.09,.035,1)
# Brick coordinates projected by face normal so mortar courses stay horizontal on every facade.
n=brick.node_tree.nodes;l=brick.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.72;l.new(bs.outputs[0],out.inputs['Surface']);tc=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['Object'],sep.inputs[0]);geom=n.new('ShaderNodeNewGeometry');sn=n.new('ShaderNodeSeparateXYZ');l.new(geom.outputs['Normal'],sn.inputs[0]);ab=n.new('ShaderNodeMath');ab.operation='ABSOLUTE';l.new(sn.outputs['X'],ab.inputs[0]);mix=n.new('ShaderNodeMixRGB');l.new(ab.outputs[0],mix.inputs[0]);l.new(sep.outputs['X'],mix.inputs[1]);l.new(sep.outputs['Y'],mix.inputs[2]);comb=n.new('ShaderNodeCombineXYZ');l.new(mix.outputs[0],comb.inputs['X']);l.new(sep.outputs['Z'],comb.inputs['Y']);bt=n.new('ShaderNodeTexBrick');bt.inputs['Scale'].default_value=1;bt.inputs['Brick Width'].default_value=.203;bt.inputs['Row Height'].default_value=.067;bt.inputs['Mortar Size'].default_value=.008;bt.inputs['Color1'].default_value=(.38,.085,.035,1);bt.inputs['Color2'].default_value=(.15,.035,.018,1);bt.inputs['Mortar'].default_value=(.46,.42,.34,1);l.new(comb.outputs[0],bt.inputs['Vector']);l.new(bt.outputs['Color'],bs.inputs['Base Color']);bp=n.new('ShaderNodeBump');bp.inputs['Distance'].default_value=.003;bp.inputs['Strength'].default_value=.4;l.new(bt.outputs['Fac'],bp.inputs['Height']);l.new(bp.outputs[0],bs.inputs['Normal'])
# Material from exterior photographs: predominantly brick, pale metal fascia, bluegrey window framing.
bpy.data.objects['NISW_Walls_Composite_Panel'].data.materials.clear();bpy.data.objects['NISW_Walls_Composite_Panel'].data.materials.append(brick)
for m in bpy.data.materials:
 if 'Mullion' in m.name:m.diffuse_color=(.12,.16,.17,1)
def box(n,loc,dim,m,angle=0):
 bm=bmesh.new();bmesh.ops.create_cube(bm,size=1)
 for v in bm.verts:v.co.x*=dim[0];v.co.y*=dim[1];v.co.z*=dim[2]
 me=bpy.data.meshes.new(n);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(n,me);c.objects.link(o);o.location=loc;o.rotation_euler.z=angle;o.data.materials.append(m);o['accuracy_status']='2016 plan registration / photograph reconstruction; estimated vertical dimensions';return o
# single sloping roof over north teaching/atrium zone, preserves XY of inherited roof
vs=[(-24,7.5,7.6),(20.5,7.5,9.4),(20.5,43.5,9.4),(-24,43.5,7.6)];me=bpy.data.meshes.new('NISW_SingleSlope_Roof');me.from_pydata(vs,[],[(0,1,2,3)]);o=bpy.data.objects.new('NISW_Photographic_Sloping_Roof',me);c.objects.link(o);me.materials.append(metal);s=o.modifiers.new('Metal roof thickness','SOLIDIFY');s.thickness=.15
# ground floor only: unsupported multistory slabs archived
box('NISW_GroundFloor_North',(-6,25,-.10),(42,34,.20),floor);box('NISW_GroundFloor_Hangar',(-3,-10,-.1),(38,32,.2),floor)
rooms=[('149',-14.3,22.4,13.4112,12.192,-13,72),('157',-27.3,25,10.0584,13.4112,-13,60),('187',.5,27.2,10.3632,9.144,0,46),('184',-8,37.6,9.4488,8.8392,0,40)]
record=[]
for rn,cx,cy,w,d,ang,cap in rooms:
 a=math.radians(ang)
 def pos(x,y,z):return(cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a),z)
 def rb(n,x,y,z,di,ma):return box('NISW_Room'+rn+'_'+n,pos(x,y,z),di,ma,a)
 rb('Carpet',0,0,.015,(w,d,.03),floor)
 # actual door opening on back wall; 1.1m leaf, jambs, transom. Interior clear height estimated3.5m.
 for x,wi in [(-w/4-.3,w/2-.6),(w/4+.3,w/2-.6)]:rb('BackWall',x,d/2,1.75,(wi,.16,3.5),orange)
 rb('DoorHeader',0,d/2,2.85,(1.2,.16,1.3),orange);rb('DoorLeaf_Open',.55,d/2+.45,1.05,(.06,.9,2.1),desk)
 rb('FrontWall',0,-d/2,1.75,(w,.16,3.5),white)
 for x in [-w/2,w/2]:rb('SideWall',x,0,1.75,(.16,d,3.5),orange)
 rb('Chalkboard',0,-d/2+.1,1.5,(w*.60,.06,1.0),black);rb('ProjectionScreen',0,-d/2+.15,2.65,(w*.60,.05,1.1),white)
 rows=6;cols=math.ceil(cap/rows);count=0
 for row in range(rows):
  yy=-d/2+2.5+row*(d-3.5)/6
  # tiered desk and paired supports, black upholstered chair with actual back/seat
  rb('Tier'+str(row),0,yy+.25,.06+row*.09,(w-1.8,(d-3.5)/6,.12+row*.18),floor)
  for col in range(cols):
   if count>=cap:break
   xx=(col-(cols-1)/2)*(w-2)/cols;z=row*.18
   rb(f'Desk_{count}',xx,yy,z+.75,((w-2)/cols-.05,.45,.055),desk)
   rb(f'DeskSupport_{count}',xx,yy,z+.38,(.045,.045,.72),metal)
   rb(f'Seat_{count}',xx,yy+.65,z+.47,(.43,.43,.07),black);rb(f'ChairBack_{count}',xx,yy+.86,z+.77,(.43,.065,.55),black)
   count+=1
 for x in [-w*.28,w*.28]:
  for y in [-d*.24,d*.24]:
   rb('CeilingPanel',x,y,3.42,(2,.55,.06),white)
   ld=bpy.data.lights.new('NISW_Classroom'+rn,'AREA');ld.energy=110;ld.shape='RECTANGLE';ld.size=2;lo=bpy.data.objects.new(ld.name,ld);c.objects.link(lo);lo.location=pos(x,y,3.3)
 record.append(dict(room=rn,center=[cx,cy],width_m=w,depth_m=d,capacity_2016=cap,modeled_seats=count,orientation_deg=ang,registration_uncertainty_m=1.5))
# glazed connector photographed by architect, continuous circulation, orange wall panels and benches
for y in [10,15,20,25,30,35,40]:
 box('NISW_Atrium_Steel_Column',(8,y,3.8),(.18,.18,7.6),metal)
 box('NISW_Atrium_TerracottaPanel',(5,y,1.75),(.13,4.8,3.5),orange)
 box('NISW_Atrium_Bench',(5.5,y,.45),(.6,2.8,.12),desk)
# cafe/reception documented architect image; approximate registration in northeast entrance space
for y in [34,38]:
 for x in [12,16]:
  box('NISW_Cafe_Table',(x,y,.75),(1.2,1.2,.06),desk)
  for dx,dy in [(0,.8),(0,-.8)]:
   box('NISW_Cafe_Chair',(x+dx,y+dy,.45),(.45,.45,.06),black);box('NISW_Cafe_ChairBack',(x+dx,y+dy+.2,.75),(.45,.05,.55),black)
# Store explicit claims rather than certify unknown current interior.
c['review_status']='Partial reconstruction from 2016 plan and architect photos. Current interior unverified.';c['height_status']='Estimated photographic scale: previous19.19m reduced to9.60m; no surveyed height.'
json.dump({'rooms':record,'archived':removed,'height_before_m':19.1939,'height_after_estimated_m':9.59695,'source_plan':'manual.pdf page33 (printed3-3), Revision12 06/01/2016','registration':'Plan rotated180deg; linear approximate fit to official FID870 north/south wings; room dimensions from printed page3-1; +-1.5m plan location uncertainty','master_edits':False},open(P/'changes.json','w'),indent=2)
bpy.ops.wm.save_as_mainfile(filepath=str(path))
