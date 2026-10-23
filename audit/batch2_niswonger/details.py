import bpy,math,json
from mathutils import Vector
from pathlib import Path
c=bpy.data.collections['Asset_niswonger_aviation_tech']
def mat(n):return bpy.data.materials[n]
white=mat('NISW_Photographic_Offwhite_Plaster');orange=mat('NISW_Photographic_Terracotta_Panels');metal=mat('NISW_Satin_Metal');black=mat('NISW_Seat_Upholstery');desk=mat('NISW_Lecture_Desk_Laminate');floor=mat('NISW_Terrazzo_Tile_MetreScale')
def box(n,p,d,m,a=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.rotation_euler.z=a
 for co in list(o.users_collection):co.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(m);return o
# Add tile joints with metre-based mapping plus fine terrazzo aggregate.
n=floor.node_tree.nodes;l=floor.node_tree.links;tc=next(x for x in n if x.bl_idname=='ShaderNodeTexCoord');bt=n.new('ShaderNodeTexBrick');bt.offset=0;bt.inputs['Scale'].default_value=1;bt.inputs['Brick Width'].default_value=.60;bt.inputs['Row Height'].default_value=.60;bt.inputs['Mortar Size'].default_value=.003;bt.inputs['Color1'].default_value=(.28,.25,.21,1);bt.inputs['Color2'].default_value=(.32,.29,.25,1);bt.inputs['Mortar'].default_value=(.16,.14,.12,1)
# object XY become brick XY for floors
l.new(tc.outputs['Object'],bt.inputs['Vector']);l.new(bt.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
for m in bpy.data.materials:
 if 'Mullion' in m.name and m.use_nodes:m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.12,.16,.17,1)
# Close roof edges with teal clerestory glass between inherited wallhead and revised single slope.
glass=mat('NISW_CurtainWall_Glass');glass.diffuse_color=(.12,.34,.37,1)
for m in [glass]:
 b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.12,.34,.37,1);b.inputs['Roughness'].default_value=.15
ring=[(-24,7.5,7.6),(20.5,7.5,9.4),(20.5,43.5,9.4),(-24,43.5,7.6)]
for i in range(4):
 a=ring[i];b=ring[(i+1)%4];me=bpy.data.meshes.new('NISW_ClerestoryClosure');me.from_pydata([(a[0],a[1],7.35),(b[0],b[1],7.35),b,a],[],[(0,1,2,3)]);o=bpy.data.objects.new('NISW_ClerestoryClosure',me);c.objects.link(o);me.materials.append(glass)
 # beam roof perimeter; orientation3D
 delta=Vector(b)-Vector(a);ob=box('NISW_PaleMetal_RoofFascia',(Vector(a)+Vector(b))/2,(delta.length,.16,.25),metal);ob.rotation_euler=delta.to_track_quat('X','Z').to_euler()
r=json.load(open('audit/batch2_niswonger/changes.json'))['rooms']
for rr in r:
 rn=rr['room'];cx,cy=rr['center'];w,d=rr['width_m'],rr['depth_m'];a=math.radians(rr['orientation_deg'])
 def pos(x,y,z):return(cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a),z)
 def rb(n,x,y,z,di,ma):return box('NISW_Room'+rn+'_'+n,pos(x,y,z),di,ma,a)
 rb('SuspendedCeiling',0,0,3.55,(w,d,.08),white)
 rb('Lectern',w*.30,-d/2+1.0,.53,(.7,.6,1.05),desk)
 rb('LecternMonitor',w*.30,-d/2+1.0,1.2,(.45,.08,.30),black)
 for x in [-w/2+.2,w/2-.2]:
  for yy in [-d*.3,0,d*.3]:
   rb('Sconce',x,yy,2.1,(.12,.40,.20),white)
  rb('TierHandrail',x,0,.95,(.045,d*.62,.045),metal)
 for o in list(c.all_objects):
  if o.name.startswith('NISW_Room'+rn+'_Seat_'):
   no=o.name.split('_')[-1];p=o.location.copy();p.z-=.25;ob=box('NISW_Room'+rn+'_ChairPedestal_'+no,p,(.06,.06,.45),metal)
   p.z-=.20;box('NISW_Room'+rn+'_ChairBase_'+no,p,(.35,.35,.04),metal)
# connector photographed transverse roof beams and metal decking underside
for y in [10,15,20,25,30,35,40]:
 box('NISW_Atrium_Steel_Crossbeam',(12,y,7.9),(12,.15,.25),metal)
 for z in [3.5,5,6.5,7.5]:box('NISW_Atrium_GlazingRail',(18,y,z),(.09,4.9,.09),metal)
 for z in [.8,1.8,2.8]:box('NISW_Atrium_PanelJoint',(5.08,y,z),(.018,4.7,.018),metal)
# contrasting dark floor border in glazed connector
for x in [6.2,17.2]:box('NISW_Atrium_TileBorder',(x,25,.007),(.15,34,.012),black)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
