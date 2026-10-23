import bpy,json,shutil,math
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/complete_potter';P=R/'modular/buildings/potter_engineering.blend'
if not (D/'before.blend').exists():shutil.copy2(P,D/'before.blend')
shutil.copy2(D/'before.blend',P)
bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];o=next(x for x in c.objects if 'Structural_Envelope' in x.name)
# Continuous thin wall replaces the completely filled placeholder volume.
z0=min(v.co.z for v in o.data.vertices);z1=max(v.co.z for v in o.data.vertices);pts=[v.co.copy() for v in o.data.vertices if abs(v.co.z-z0)<1e-4];n=len(pts)
def material(name,color,rough=.7):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;return m
brick=material('POTR_Meter_Brick',(0.23,.085,.045));nt=brick.node_tree;tex=nt.nodes.new('ShaderNodeTexBrick');tex.inputs['Color1'].default_value=(.25,.075,.035,1);tex.inputs['Color2'].default_value=(.12,.035,.018,1);tex.inputs['Mortar'].default_value=(.24,.22,.19,1);tex.inputs['Scale'].default_value=1;tex.inputs['Brick Width'].default_value=.203;tex.inputs['Row Height'].default_value=.067;tex.inputs['Mortar Size'].default_value=.007
coord=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');comb=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(coord.outputs['Object'],sep.inputs[0]);nt.links.new(sep.outputs['X'],comb.inputs['X']);nt.links.new(sep.outputs['Z'],comb.inputs['Y']);nt.links.new(comb.outputs[0],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.003;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],nt.nodes.get('Principled BSDF').inputs['Normal'])
# Select facade horizontal axis from the surface normal so brick courses retain meter size on both cardinal facades.
geom=nt.nodes.new('ShaderNodeNewGeometry');nsep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geom.outputs['Normal'],nsep.inputs[0]);absolute=nt.nodes.new('ShaderNodeMath');absolute.operation='ABSOLUTE';nt.links.new(nsep.outputs['X'],absolute.inputs[0]);mix=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(absolute.outputs[0],mix.inputs[0]);nt.links.new(sep.outputs['X'],mix.inputs[1]);nt.links.new(sep.outputs['Y'],mix.inputs[2]);nt.links.new(mix.outputs[0],comb.inputs['X'])
concrete=material('POTR_Precast_Concrete',(.48,.43,.35));floor=material('POTR_Terrazzo_Estimate',(.31,.28,.23));metal=material('POTR_Dark_Window_Frame',(.045,.04,.03),.32);glass=material('POTR_Recessed_Glass',(.045,.07,.075),.18)
# Existing architectural assessment describes 5ft4 panels, 1ft4 overhang and 4.5sf openings.
verts=[tuple(v.co) for v in o.data.vertices];faces=[tuple(p.vertices) for p in o.data.polygons if abs(p.normal.z)<.5];mesh=bpy.data.meshes.new('POTR_Hollow_Exterior');mesh.from_pydata(verts,[],faces);mesh.materials.append(brick);o.data=mesh;mod=o.modifiers.new('Inward_280mm_Wall','SOLIDIFY');mod.thickness=.28;mod.offset=-1
# Interior slabs use the exact cached source polygon triangulation from the roof, avoiding bounds rectangles.
roof=next(x for x in c.objects if 'Roof' in x.name)
for level,z in enumerate([-4.064,.6096,4.8768,9.144]):
 me=roof.data.copy();ob=bpy.data.objects.new('POTR_Interior_Slab_Level_%d_EstimatedElevation'%level,me);c.objects.link(ob);bottom=min(v.co.z for v in me.vertices)
 for v in me.vertices:v.co.z=z+(v.co.z-bottom)*.6
 me.materials.clear();me.materials.append(floor);ob['evidence']='2016 existing plans pages40-45; elevations estimated, not a current interior certification'
def box(name,loc,scale,mat):
 x,y,z=[v/2 for v in scale];verts=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)];faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(mat);b=bpy.data.objects.new(name,me);c.objects.link(b);b.location=loc;return b
# Only long nearly cardinal perimeter edges receive estimated precast recess rhythm.
for j,(a,b) in enumerate(zip(pts,pts[1:]+pts[:1])):
 d=b-a;L=d.xy.length
 if L<8:continue
 tangent=Vector((d.x/L,d.y/L,0));normal=Vector((tangent.y,-tangent.x,0));normal *= (1 if sum(u.x*v.y-v.x*u.y for u,v in zip(pts,pts[1:]+pts[:1]))>0 else -1);count=int(L/1.6256)
 for k in range(count):
  p=a+tangent*((k+.5)*L/count)
  for z in [6.1,10.3672]:
   q=p+normal*.045;ob=box('POTR_Precast_Panel_Estimated_%d_%d_%.1f'%(j,k,z),(q.x,q.y,z),(L/count-.025,.12,3.2),concrete);ob.rotation_euler.z=math.atan2(d.y,d.x)
   q=p+normal*.125;ob=box('POTR_Shaded_Window_Representation',(q.x,q.y,z+.12),(.71,.025,.7066),glass);ob.rotation_euler.z=math.atan2(d.y,d.x)
   q=p+normal*.25;ob=box('POTR_406mm_Shading_Overhang',(q.x,q.y,z+.57),(L/count-.025,.4064,.16),concrete);ob.rotation_euler.z=math.atan2(d.y,d.x)
# Iteration: construct real wall apertures directly, retaining the source XY perimeter.
for ob in list(c.objects):
 if ob.name.startswith(('POTR_Precast_Panel','POTR_Shaded_Window','POTR_406mm')):bpy.data.objects.remove(ob,do_unlink=True)
vs=[];fs=[];mis=[]
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=1
for j,(a,b) in enumerate(zip(pts,pts[1:]+pts[:1])):
 d=b-a;L=d.xy.length
 if L<.001:continue
 tangent=Vector((d.x/L,d.y/L,0));normal=Vector((tangent.y,-tangent.x,0));normal *= (1 if sum(u.x*v.y-v.x*u.y for u,v in zip(pts,pts[1:]+pts[:1]))>0 else -1)
 holes=[]
 if L>1.65:
  for k in range(max(1,int(L/1.6256))):
   u=(k+.5)*L/max(1,int(L/1.6256))
   for z in [6.1,10.3672]:holes.append((u-.355,u+.355,z-.3533,z+.3533))
 us=sorted(set([0,L]+[u for h in holes for u in h[:2]]));zs=sorted(set([-.0,4.4,13.5,z1]+[z for h in holes for z in h[2:]]))
 for u0,u1 in zip(us,us[1:]):
  for low,high in zip(zs,zs[1:]):
   if any(h[0]<(u0+u1)/2<h[1] and h[2]<(low+high)/2<h[3] for h in holes):continue
   base=len(vs)
   for u,z in [(u0,low),(u1,low),(u1,high),(u0,high)]:
    q=a+tangent*u;vs.append((q.x,q.y,z))
   fs.append((base,base+1,base+2,base+3));mis.append(int(L>1.65 and 4.4<=(low+high)/2<13.5))
 for h in holes:
  u=(h[0]+h[1])/2;z=(h[2]+h[3])/2;q=a+tangent*u-normal*.1
  ob=box('POTR_RealOpening_Glazing',(q.x,q.y,z),(.71,.025,.7066),glass);ob.rotation_euler.z=math.atan2(d.y,d.x)
  q=a+tangent*u+normal*.2032;ob=box('POTR_Precast_406mm_Overhang',(q.x,q.y,h[3]+.1),(.95,.4064,.16),concrete);ob.rotation_euler.z=math.atan2(d.y,d.x)
me=bpy.data.meshes.new('POTR_Perimeter_With_Real_Window_Openings');me.from_pydata(vs,[],fs);me.materials.append(brick);me.materials.append(concrete)
for face,mi in zip(me.polygons,mis):face.material_index=mi
o.data=me
# Date-labelled historical interior tracing, with registration uncertainty retained.
white=material('POTR_Historic2016_Partition_Paint',(.7,.68,.61))
trace=json.loads((D/'historic_walls.json').read_text())
for page,base in [(51,-4.064),(53,.6096),(54,4.8768),(55,9.144)]:
 for idx,line in enumerate(trace[str(page)]['lines']):
  a=Vector((*line[0],0));b=Vector((*line[-1],0));d=b-a;L=d.length
  ob=box('POTR_Historic2016_Plan%d_Wall_%d'%(page,idx),((a.x+b.x)/2,(a.y+b.y)/2,base+1.35),(L,.12,2.7),white);ob.rotation_euler.z=math.atan2(d.y,d.x);ob['evidence']='Raster-traced existing 2016 plan; approximate affine registration, room layout may have changed';ob['registration_iou']=trace[str(page)]['registration_iou']
# Full basement perimeter documented by the existing structural assessment.
vs=[];fs=[]
for a,b in zip(pts,pts[1:]+pts[:1]):
 start=len(vs);vs.extend([(a.x,a.y,-4.064),(b.x,b.y,-4.064),(b.x,b.y,.6096),(a.x,a.y,.6096)]);fs.append((start,start+1,start+2,start+3))
me=bpy.data.meshes.new('POTR_Basement_Perimeter');me.from_pydata(vs,[],fs);me.materials.append(concrete);ob=bpy.data.objects.new('POTR_Full_Basement_Walls',me);c.objects.link(ob);m=ob.modifiers.new('Inward_Basement_280mm','SOLIDIFY');m.thickness=.28;m.offset=-1
# Save portable node textures; no dependencies.
bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];s=bpy.context.scene
roof=next(x for x in c.objects if 'Roof' in x.name);camd=bpy.data.cameras.new('Evidence');cam=bpy.data.objects.new('Evidence',camd);s.collection.objects.link(cam);cam.location=(110,-140,100);target=sum((roof.matrix_world@Vector(v) for v in roof.bound_box),Vector())/8;cam.location=target+Vector((100,-125,90));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=110;s.camera=cam;s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='MATERIAL';s.render.resolution_x=1100;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.filepath=str(D/'after.png');bpy.ops.render.render(write_still=True)
(D/'checks.json').write_text(json.dumps({'reopened':True,'objects':len(c.all_objects),'images_missing':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file],'height_estimated':True,'interior_complete':False,'panel_positions_estimated':True},indent=2))


