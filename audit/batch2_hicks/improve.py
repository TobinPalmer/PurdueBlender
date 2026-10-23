import bpy,math,json
from mathutils import Vector
P='audit/batch2_hicks/'
c=bpy.data.collections['Asset_hicks_library']; root=bpy.data.objects.get('AssetRoot_hicks_library')
sub=bpy.data.collections.new('HIKS_2013_Study_Furnishing_Interpretation');c.children.link(sub)
def mat(n,col,r=.6):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Roughness'].default_value=r;return m
wood=mat('HIKS_Study_Light_Maple',(.48,.34,.18));white=mat('HIKS_Study_OffWhite',(.72,.70,.63));green=mat('HIKS_Study_Green_Upholstery',(.21,.32,.055));red=mat('HIKS_Study_Rust_Upholstery',(.39,.095,.035));steel=mat('HIKS_Study_Satin_Metal',(.23,.25,.26),.32);black=mat('HIKS_Study_Dark_Equipment',(.025,.03,.033));carpet=mat('HIKS_Study_Terracotta_Carpet',(.24,.105,.055))
# Meter-coordinate physical grain independent of mesh UV.
for m,scale,strength in [(wood,6,.08),(carpet,95,.22),(green,130,.12),(red,130,.12)]:
 n=m.node_tree.nodes;l=m.node_tree.links;t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=scale;co=n.new('ShaderNodeTexCoord');l.new(co.outputs['Object'],t.inputs['Vector']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=strength;b.inputs['Distance'].default_value=.003;l.new(t.outputs['Fac'],b.inputs['Height']);l.new(b.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
def box(n,loc,dims,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name='HIKS_Study_'+n;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for cc in list(o.users_collection):cc.objects.unlink(o)
 sub.objects.link(o);o.data.materials.append(m);o['evidence']='2013 renovation photo-supported furniture type; approximate position/dimensions';be=o.modifiers.new('Soft furniture edges','BEVEL');be.width=.018;be.segments=2;return o
def table(x,y,h=.74):
 box('TableTop',(x,y,-5.304+h),(1.7,.8,.055),white)
 for dx in [-.66,.66]:
  for dy in [-.27,.27]:box('TableLeg',(x+dx,y+dy,-5.304+h/2),(.045,.045,h),steel)
def chair(x,y,color=green,h=.45):
 z=-5.304;box('Seat',(x,y,z+h),(.48,.48,.10),color);box('Back',(x,y+.22,z+h+.26),(.48,.065,.46),color)
 for dx in [-.18,.18]:
  for dy in [-.17,.17]:box('ChairLeg',(x+dx,y+dy,z+h/2),(.025,.025,h),steel)
# Keep atrium, column grid and lightwell strip clear. Furnishing zones are interpretations, not surveyed room layouts.
for x in [-8.5,8.5]:
 for y in [-3,1.5]:
  table(x,y);chair(x-.45,y-.62);chair(x+.45,y-.62);chair(x-.45,y+.62);chair(x+.45,y+.62)
# Raised bistro / power bar, matching documented renovation furniture.
box('PowerBarTop',(8.6,5.9,-4.254),(6,.65,.08),white)
for x in [6.2,8.6,11]:box('PowerBarSupport',(x,5.9,-4.78),(.08,.45,1.05),steel);chair(x,5.15,green,.72)
# Paired computer consoles with timber vertical supports and monitors.
for x in [-10.5,-8.7,-6.9]:
 box('ComputerDesk',(x,5.8,-4.55),(1.5,.75,.06),wood)
 box('ComputerPost',(x,6.05,-3.55),(.12,.12,3.4),wood)
 box('Monitor',(x,5.95,-4.04),(.55,.065,.34),black);box('MonitorStand',(x,5.95,-4.38),(.05,.05,.30),steel)
 box('Keyboard',(x,5.55,-4.505),(.42,.15,.025),black);chair(x,4.95)
# Red lounge chairs and low tables visible in photo b.
for x in [-9,-6.5]:
 chair(x,-6,red);box('LoungeSideTable',(x+1,-6,-4.80),(.6,.6,.06),wood);box('LoungeTablePedestal',(x+1,-6,-5.04),(.08,.08,.5),steel)
# Carpet mats occupy only furnishing patches, not atrium void.
for x in [-8.5,8.5]:box('CarpetZone',(x,-.75,-5.296),(5,9,.012),carpet)
# Correct brick node default scale (5 turns intended220mm bricks into44mm).
m=bpy.data.materials['Mat_HIKS_Purdue_Red_Brick'];brick=next(n for n in m.node_tree.nodes if n.type=='TEX_BRICK');brick.inputs['Scale'].default_value=1;brick.inputs['Mortar Size'].default_value=.004;brick.inputs['Mortar Smooth'].default_value=.001
m['physical_module_m']='0.22 x 0.075; 4mm mortar, UV units meters'
for m in bpy.data.materials:
 if m.use_nodes:
  bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if bs and not bs.inputs['Base Color'].is_linked:m.diffuse_color=bs.inputs['Base Color'].default_value
bpy.context.scene['interior_status']='Photo-supported 2013 furnishing types; approximate layout and sizes; no complete surveyed room plan. Existing subterranean structure remains unverified.'
# Camera and lighting in a nonexport review collection.
sc=bpy.context.scene
for o in list(sc.objects):
 if o.type=='LIGHT':o.hide_render=True
sc.world=bpy.data.worlds.new('Hicks_Review_World');sc.world.color=(.4,.4,.4)
for x in [-9,9]:
 for y in [-4,4]:
  ld=bpy.data.lights.new('ReviewArea','AREA');ld.energy=850;ld.shape='DISK';ld.size=6;o=bpy.data.objects.new('ReviewArea',ld);sc.collection.objects.link(o);o.location=(x,y,-1.5)
camd=bpy.data.cameras.new('Review_Hicks_Interior');cam=bpy.data.objects.new('Review_Hicks_Interior',camd);sc.collection.objects.link(cam);cam.location=(-13,-7,-2.9);cam.rotation_euler=(Vector((7,2,-4.4))-cam.location).to_track_quat('-Z','Y').to_euler();camd.lens=22;sc.camera=cam
sc.render.engine='CYCLES';sc.cycles.samples=20;sc.render.resolution_x=1000;sc.render.resolution_y=700;sc.render.resolution_percentage=100
sc.render.filepath=P+'interior.png'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('HICKS_SAVED',len(c.all_objects))
bpy.ops.render.render(write_still=True)

