import bpy, math, json
from mathutils import Vector, Matrix
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.name='Building_bell_tower'
asset=bpy.data.collections.new('Asset_bell_tower');scene.collection.children.link(asset)
ref=json.loads((ROOT/'audit/official_building_references.json').read_text())
def find(d):
 if isinstance(d,dict):
  if d.get('code')=='BELL':return d
  for v in d.values():
   r=find(v)
   if r:return r
 if isinstance(d,list):
  for v in d:
   r=find(v)
   if r:return r
r=find(ref); (P/'official_BELL_reference.json').write_text(json.dumps(r,indent=2))
cx,cy=r['official_polygon_center_xy_m'];angle=math.radians(r['minimum_rotated_rectangle']['angle_degrees_east_ccw']-90)
W=(r['minimum_rotated_rectangle']['width_m']+r['minimum_rotated_rectangle']['depth_m'])/2
R=Matrix.Rotation(angle,4,'Z')
def mat(n,c,metal=0,rough=.65):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 return m
brick=mat('Bell_Red_Brick',(.30,.085,.043));stone=mat('Bell_Indiana_Limestone',(.65,.61,.50));black=mat('Bell_Clock_Black',(.009,.012,.014),.25,.35);dial=mat('Bell_Clock_Ivory',(.87,.82,.65));roof=mat('Bell_Dark_Metal_Roof',(.065,.06,.055),.75,.35);bronze=mat('Bell_Aged_Bronze',(.20,.13,.06),.72,.42);steel=mat('Bell_Internal_Steel',(.10,.11,.10),.75,.4)
# World-coordinate brick pattern: physically scaled courses, with three planar projections.
n=brick.node_tree.nodes;l=brick.node_tree.links;bs=n.get('Principled BSDF');tex=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(tex.outputs['Object'],sep.inputs[0])
geom=n.new('ShaderNodeNewGeometry');ns=n.new('ShaderNodeSeparateXYZ');l.new(geom.outputs['Normal'],ns.inputs[0]);ab=n.new('ShaderNodeMath');ab.operation='ABSOLUTE';l.new(ns.outputs['X'],ab.inputs[0])
mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';l.new(ab.outputs[0],mix.inputs[0]);a=n.new('ShaderNodeCombineXYZ');b=n.new('ShaderNodeCombineXYZ')
for node,key in [(a,'X'),(b,'Y')]:l.new(sep.outputs[key],node.inputs['X']);l.new(sep.outputs['Z'],node.inputs['Y'])
l.new(a.outputs[0],mix.inputs[1]);l.new(b.outputs[0],mix.inputs[2]);bt=n.new('ShaderNodeTexBrick');l.new(mix.outputs[0],bt.inputs['Vector']);bt.inputs['Scale'].default_value=1;bt.inputs['Brick Width'].default_value=.215;bt.inputs['Row Height'].default_value=.075;bt.inputs['Mortar Size'].default_value=.004;bt.inputs['Mortar Smooth'].default_value=.001;bt.inputs['Color1'].default_value=(.32,.085,.045,1);bt.inputs['Color2'].default_value=(.14,.035,.019,1);bt.inputs['Mortar'].default_value=(.24,.20,.15,1);l.new(bt.outputs['Color'],bs.inputs['Base Color']);bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.009;bump.inputs['Strength'].default_value=.45;l.new(bt.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
noise=stone.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=24;bump=stone.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.006;bump.inputs['Strength'].default_value=.2;stone.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);stone.node_tree.links.new(bump.outputs[0],stone.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
def adopt(o,name,material):
 o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 asset.objects.link(o)
 if material:o.data.materials.append(material)
 return o
def cube(n,loc,dim,m,bev=.018):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=adopt(bpy.context.object,n,m);o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bev:mo=o.modifiers.new('Small real edge rounding','BEVEL');mo.width=bev;mo.segments=2
 return o
def mesh(n,verts,faces,m):
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);asset.objects.link(o);o.data.materials.append(m);return o
def cyl(n,loc,rad,depth,m):
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=rad,depth=depth,location=loc);return adopt(bpy.context.object,n,m)
def rod(n,p1,p2,r,m):
 d=Vector(p2)-Vector(p1);o=cyl(n,(Vector(p1)+Vector(p2))/2,r,d.length,m);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def arch(n,width,spring,top,depth,m):
 # Solid spandrel above a semicircular, open arch, extruded in local Y.
 rad=width/2;pts=[(-rad,top),(rad,top),(rad,spring)]
 for k in range(1,33):
  t=math.pi*k/32;pts.append((rad*math.cos(t),spring+rad*math.sin(t)))
 N=len(pts);v=[(x,y,z) for y in [-depth/2,depth/2] for x,z in pts];f=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
 for i in range(N):j=(i+1)%N;f.append((i,j,N+j,N+i))
 return mesh(n,v,f,m)
def face_coords(side,u,d,z):
 t=side*math.pi/2;return (math.cos(t)*u-math.sin(t)*d,math.sin(t)*u+math.cos(t)*d,z)
def face_cube(n,side,u,d,z,w,th,h,m):
 o=cube(n,face_coords(side,u,d,z),(w,th,h),m);o.rotation_euler.z=side*math.pi/2;return o
def face_arch(n,side,d,width,spring,top,depth,m):
 o=arch(n,width,spring,top,depth,m);o.location=face_coords(side,0,d,0);o.rotation_euler.z=side*math.pi/2;return o
# Four open base passages; masonry frame rather than an invented enclosed interior.
for x in [-1,1]:
 for y in [-1,1]:
  cube(f'Ground_Limestone_Foot_{x}_{y}',(x*1.99,y*1.99,.55),(1.51,1.51,1.1),stone)
  cube(f'Ground_Limestone_Pier_{x}_{y}',(x*1.99,y*1.99,3.60),(1.45,1.45,5.0),stone)
  for zz in [1.35,3.45]:cube(f'Pier_Projecting_Capital_{x}_{y}_{zz}',(x*1.99,y*1.99,zz),(1.60,1.60,.22),stone)
for s in range(4):
 face_arch(f'Base_Arch_Spandrel_{s}',s,2.13,2.50,3.5,6.1,1.22,stone)
 vv=[face_coords(s,u,d,z) for d in [2.72,2.80] for u,z in [(-.17,4.59),(.17,4.59),(.28,6.03),(-.28,6.03)]]
 mesh(f'Base_Arch_Tapered_Keystone_{s}',vv,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],stone)
cube('Shaft_Structural_Envelope',(0,0,(6.1+30.45)/2),(W,W,30.45-6.1),brick)
# Central raised brick pier visible in official Purdue photograph. No stone quoins.
for s in range(4):
 face_cube(f'Brick_Central_Pilaster_{s}',s,0,W/2+.045,18.25,1.20,.09,24.3,brick)
 for zz in [14.0,22.1,30.25]:face_cube(f'Pilaster_Stone_Cap_{s}_{zz}',s,0,W/2+.055,zz,1.27,.11,.15,stone)
for z in [6.1,14.2,22.3,30.50]:
 cube(f'Limestone_String_Course_{z}',(0,0,z),(W+.25,W+.25,.20),stone)
 cube(f'String_Course_Shadow_{z}',(0,0,z-.15),(W+.11,W+.11,.10),stone)
for z,w,h in [(30.72,W+.60,.23),(30.93,W+.37,.19)]:cube(f'Clock_Base_Cornice_{z}',(0,0,z),(w,w,h),stone)
# Limestone clock drum, clad joints and architectural louvers below clock faces.
cube('Clock_Chamber',(0,0,33.12),(5.10,5.10,4.20),stone)
for s in range(4):
 for u in [-2.15,2.15]:face_cube(f'Clock_Jamb_Joint_{s}_{u}',s,u,2.557,33.13,.014,.014,4.05,black)
 for z in [31.20,32.0,34.7]:face_cube(f'Clock_Horizontal_Joint_{s}_{z}',s,0,2.558,z,5.06,.012,.012,black)
 face_cube(f'Clock_Lower_Panel_Shadow_{s}',s,0,2.565,31.70,1.60,.025,.42,black)
 face_cube(f'Clock_Lower_Panel_{s}',s,0,2.59,31.70,1.45,.025,.29,stone)
 for u in [-.79,.79]:face_cube(f'Clock_Panel_Frame_Jamb_{s}_{u}',s,u,2.62,31.70,.065,.065,.48,stone)
 for zz in [31.47,31.93]:face_cube(f'Clock_Panel_Frame_Rail_{s}_{zz}',s,0,2.62,zz,1.65,.065,.065,stone)
 vv=[face_coords(s,u,d,z) for u in [-.86,.86] for d,z in [(2.56,31.11),(3.16,31.11),(3.16,31.28),(2.56,31.55)]]
 mesh(f'Clock_Projected_Wedge_Hood_{s}',vv,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stone)
 # Dial plane basis: local X right, local Y up, normal outward (local +Z).
 t=s*math.pi/2;right=Vector((-math.cos(t),-math.sin(t),0));out=Vector((-math.sin(t),math.cos(t),0));up=Vector((0,0,1));basis=Matrix((right,up,out)).transposed().to_4x4();center=Vector(face_coords(s,0,2.60,33.36))
 def dial_object(o,extra=0):
  bpy.context.view_layer.update()
  o.matrix_world=Matrix.Translation(center+out*extra)@basis@o.matrix_world
  return o
 dial_object(cyl(f'Clock_{s}_Black_Rim',(0,0,0),1.16,.085,black))
 dial_object(cyl(f'Clock_{s}_Ivory_Dial',(0,0,0),1.105,.014,dial),.053)
 for radius in [.71,1.015]:
  bpy.ops.mesh.primitive_torus_add(major_radius=radius,minor_radius=.009,major_segments=96,minor_segments=6);dial_object(adopt(bpy.context.object,f'Clock_{s}_Chapter_Ring_{radius}',black),.067)
 for k in range(60):
  a=2*math.pi*k/60;o=cube(f'Clock_{s}_Minute_Tick_{k}',(1.065*math.sin(a),1.065*math.cos(a),0),(.020,.035,.009),black,0);o.rotation_euler.z=-a;dial_object(o,.069)
 nums=['XII','I','II','III','IIII','V','VI','VII','VIII','IX','X','XI']
 for k,txt in enumerate(nums):
  a=2*math.pi*k/12;cu=bpy.data.curves.new(f'Roman_{s}_{k}','FONT');cu.body=txt;cu.align_x='CENTER';cu.align_y='CENTER';cu.size=.245;cu.extrude=.002;ob=bpy.data.objects.new(f'Clock_{s}_Roman_{txt}',cu);asset.objects.link(ob);cu.materials.append(black);ob.location=(.865*math.sin(a),.865*math.cos(a),0);ob.rotation_euler.z=-a;dial_object(ob,.071)
 for label,a,length,w in [('Minute',math.radians(60),.92,.037),('Hour',math.radians(-60),.61,.065)]:
  vs=[(-w,0,0),(-w,length*.58,0),(-w*1.5,length*.69,0),(0,length,0),(w*1.5,length*.69,0),(w,length*.58,0),(w,0,0)]
  ob=mesh(f'Clock_{s}_{label}_Hand',vs,[tuple(range(7))],black);ob.rotation_euler.z=-a;dial_object(ob,.094)
 dial_object(cyl(f'Clock_{s}_Hub',(0,0,0),.085,.035,black),.10)
# Open belfry: corner columns, genuine open arches and cross rails.
cube('Belfry_Bottom_Sill',(0,0,35.36),(5.35,5.35,.34),stone)
for x in [-2.17,2.17]:
 for y in [-2.17,2.17]:
  cube(f'Belfry_Column_{x}_{y}',(x,y,38.55),(.67,.67,6.1),stone)
  for z in [35.65,40.2]:cube(f'Column_Capital_{x}_{y}_{z}',(x,y,z),(.85,.85,.28),stone)
  for z,w,hc in [(39.98,.74,.10),(40.34,.79,.08),(35.87,.73,.10)]:cube(f'Column_Capital_Layer_{x}_{y}_{z}',(x,y,z),(w,w,hc),stone)
  for off in [-.265,.265]:
   cube(f'Column_Recess_Rail_X_{x}_{y}_{off}',(x+off,y+math.copysign(.355,y),37.88),(.105,.045,4.0),stone,.009)
   cube(f'Column_Recess_Rail_Y_{x}_{y}_{off}',(x+math.copysign(.355,x),y+off,37.88),(.045,.105,4.0),stone,.009)
for s in range(4):
 face_arch(f'Belfry_Open_Arch_{s}',s,2.17,3.67,40.05,42.25,.68,stone)
 face_cube(f'Belfry_Cross_Rail_{s}',s,0,2.17,39.20,4.2,.35,.25,stone)
 for u in [-1.87,1.87]:face_cube(f'Belfry_Slender_Post_{s}_{u}',s,u,2.19,37.55,.14,.16,3.8,stone)
for z,w,h in [(42.18,5.55,.30),(42.46,5.86,.26),(42.68,5.96,.18)]:cube(f'Roof_Cornice_{z}',(0,0,z),(w,w,h),stone)
# Four profiled, hollow bells with flared skirts and clappers. Sizes are inferred, not surveyed.
profile=[(.0,.88),(.21,.84),(.25,.69),(.29,.44),(.37,.15),(.50,-.14),(.65,-.35),(.72,-.39),(.73,-.48),(.62,-.50),(.53,-.36),(.42,-.10),(.30,.18),(.23,.43),(.17,.65),(.0,.67)]
for i,(x,y,z,scale) in enumerate([(-.8,-.65,37.6,1.0),(.85,.6,38.3,.79),(-.75,.8,39.0,.60),(.8,-.7,39.7,.48)]):
 N=64;v=[(x+rad*scale*math.cos(k*2*math.pi/N),y+rad*scale*math.sin(k*2*math.pi/N),z+zz*scale) for rad,zz in profile for k in range(N)];f=[]
 for j in range(len(profile)-1):
  for k in range(N):a=j*N+k;b=j*N+(k+1)%N;f.append((a,b,b+N,a+N))
 ob=mesh(f'Historic_Bell_{i+1}',v,f,bronze)
 for poly in ob.data.polygons:poly.use_smooth=True
 rod(f'Bell_{i+1}_Clapper',(x,y,z+.2*scale),(x,y,z-.57*scale),.04*scale,steel)
 rod(f'Bell_{i+1}_Suspension',(x,y,z+.8*scale),(x,y,40.6),.035,steel)
for y in [-.7,.7]:cube(f'Bell_Support_Beam_{y}',(0,y,40.6),(3.7,.13,.20),steel)
# Four-sided standing seam roof and thin finial, ending at published 160 ft.
h=47.35;z=42.77;a=2.92
mesh('Pyramidal_Metal_Roof',[(-a,-a,z),(a,-a,z),(a,a,z),(-a,a,z),(0,0,h)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)],roof)
for s in range(4):
 for u in [-a,-a*.66,-a*.33,0,a*.33,a*.66,a]:rod(f'Roof_Standing_Seam_{s}_{u}',face_coords(s,u,a,z+.02),(0,0,h+.01),.018,stone)
rod('Finial_Lower',(0,0,h),(0,0,48.15),.045,stone);rod('Finial_Tip',(0,0,48.15),(0,0,48.768),.018,stone)
for z in [47.65,47.9,48.13]:cyl(f'Finial_Collar_{z}',(0,0,z),.075,.045,stone)
cyl('Under_Tower_Memorial_Plaque',(0,0,.03),.85,.045,bronze)
for i in range(48):
 a=2*math.pi*i/48;o=cube(f'Plaque_Perimeter_Marker_{i}',(.78*math.sin(a),.78*math.cos(a),.057),(.06,.08,.008),stone,0);o.rotation_euler.z=-a
for text,zz,sz in [('PURDUE BELL TOWER',.28,.095),('DEDICATED OCTOBER 14, 1995',-.14,.052),('CLASS OF 1948',-.28,.065),('TIME CAPSULE 2095',-.42,.052)]:
 cu=bpy.data.curves.new('Plaque_Inscription','FONT');cu.body=text;cu.align_x='CENTER';cu.align_y='CENTER';cu.size=sz;cu.extrude=.001;ob=bpy.data.objects.new(text,cu);asset.objects.link(ob);cu.materials.append(stone);ob.location=(0,zz,.062)
asset['source_status']='Official GIS horizontal envelope; Purdue published height; photographic architectural reconstruction. Not surveyed.'
asset['height_m']=48.768;asset['official_feature']='BELL / FID 290';asset['orientation_degrees']=math.degrees(angle);asset['plan_width_m']=W
bpy.context.view_layer.update()
for ob in asset.all_objects:
 ob.matrix_world=Matrix.Translation((cx,cy,0))@R@ob.matrix_world
 ob['asset_id']='bell_tower'
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
# Preview staging belongs outside exported collection.
preview=bpy.data.collections.new('Bell_Tower_Preview_Only');scene.collection.children.link(preview)
def staging(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 preview.objects.link(o);return o
bpy.ops.mesh.primitive_plane_add(size=200,location=(cx,cy,-.035));ground=staging(bpy.context.object);ground.name='Preview_Ground';ground.data.materials.append(mat('Preview_Warm_Gray',(.23,.25,.23)))
world=bpy.data.worlds.new('Bell_Preview_Sky');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.45,.58,.72,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6
bpy.ops.object.light_add(type='SUN',location=(cx-30,cy-20,65));sun=staging(bpy.context.object);sun.rotation_euler=(.4,-.5,-.6);sun.data.energy=3;sun.data.angle=.15
bpy.ops.object.camera_add();cam=staging(bpy.context.object);scene.camera=cam
def view(name,offset,target,scale):
 cam.location=Vector((cx,cy,0))+Vector(offset);direction=Vector((cx,cy,target))-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale;scene.render.filepath=str(P/name)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=800;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
view('after_full.png',(85,-42,49),24,56)
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':area.spaces.active.region_3d.view_distance=65;area.spaces.active.region_3d.view_location=(cx,cy,24)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'modular/buildings/bell_tower.blend'))
bpy.ops.render.render(write_still=True)
view('after_belfry.png',(34,-17,42),38.8,18);bpy.ops.render.render(write_still=True)
view('after_base.png',(20,-28,11),3.1,10);bpy.ops.render.render(write_still=True)
(P/'build_result.json').write_text(json.dumps({'objects':len(asset.all_objects),'center':[cx,cy],'angle_deg':math.degrees(angle),'width_m':W,'height_m':48.768,'estimated_architecture':True},indent=2))
