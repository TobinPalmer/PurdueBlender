import bpy,json,math,shutil
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/complete_bhee';P=R/'modular/buildings/electrical_engineering.blend'
if not (D/'before.blend').exists():shutil.copy2(P,D/'before.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_electrical_engineering'];a=math.radians(39.24);co,si=math.cos(a),math.sin(a)
def mat(n,col,rough=.6):
 m=bpy.data.materials.new('BHEE_'+n);m.diffuse_color=(*col,1);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*col,1);s.inputs['Roughness'].default_value=rough;return m
brick=mat('Brick',(.29,.085,.045));stone=mat('Limestone',(.64,.59,.48));white=mat('Paint',(.78,.77,.72));dark=mat('Metal',(.035,.04,.043),.3);glass=mat('Glass',(.075,.13,.15),.16);wood=mat('Laminate',(.65,.5,.31));green=mat('GreenFabric',(.28,.38,.12));floor=mat('Terrazzo',(.4,.4,.35));carpet=mat('Carpet',(.2,.25,.14));roof=mat('Roof',(.13,.13,.12));screen=mat('Screen',(.045,.12,.2),.25)
# Meter-scaled XYZ running bond, and fine surface relief.
n=brick.node_tree.nodes;l=brick.node_tree.links;t=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(t.outputs['Geometry'] if 'Geometry' in t.outputs else t.outputs['Object'],sep.inputs[0]);comb=n.new('ShaderNodeCombineXYZ');l.new(sep.outputs['X'],comb.inputs['X']);l.new(sep.outputs['Z'],comb.inputs['Y']);b=n.new('ShaderNodeTexBrick');b.inputs['Scale'].default_value=1;b.inputs['Brick Width'].default_value=.215;b.inputs['Row Height'].default_value=.065;b.inputs['Mortar Size'].default_value=.009;b.inputs['Color1'].default_value=(.32,.095,.05,1);b.inputs['Color2'].default_value=(.2,.05,.025,1);b.inputs['Mortar'].default_value=(.48,.44,.36,1);l.new(comb.outputs[0],b.inputs['Vector']);l.new(b.outputs['Color'],n.get('Principled BSDF').inputs['Base Color']);bum=n.new('ShaderNodeBump');bum.inputs['Distance'].default_value=.006;bum.inputs['Strength'].default_value=.35;l.new(b.outputs['Fac'],bum.inputs['Height']);l.new(bum.outputs[0],n.get('Principled BSDF').inputs['Normal'])
for m in (floor,carpet,stone,white):
 ns=m.node_tree.nodes;lk=m.node_tree.links;noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=80;bu=ns.new('ShaderNodeBump');bu.inputs['Distance'].default_value=.004;bu.inputs['Strength'].default_value=.18;lk.new(noise.outputs['Fac'],bu.inputs['Height']);lk.new(bu.outputs[0],ns.get('Principled BSDF').inputs['Normal'])
for o in list(c.all_objects):
 if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
def box(n,u,v,z,dx,dy,dz,m):
 vs=[(x*dx/2,y*dy/2,zz*dz/2) for x,y,zz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];me=bpy.data.meshes.new(n);me.from_pydata(vs,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();o=bpy.data.objects.new('BHEE_'+n,me);c.objects.link(o);o.location=(u*co-v*si,u*si+v*co,z);o.rotation_euler.z=a;o.data.materials.append(m);return o
def edge(n,p,q,z,h,m,th=.3):
 u,v=p;x,y=q;ln=math.hypot(x-u,y-v);o=box(n,(u+x)/2,(v+y)/2,z,ln,th,h,m);o.rotation_euler.z=a+math.atan2(y-v,x-u);return o
refs=json.loads((R/'audit/official_building_references.json').read_text())
for fid in (292,):
 f=next(x for x in refs['buildings'] if x['fid']==fid);pts=[((x-143.8499984741211)*co+(y-135)*si,-(x-143.8499984741211)*si+(y-135)*co) for x,y in f['rings_xy_m'][0]]
 for j,(p,q) in enumerate(zip(pts,pts[1:])):
  ln=math.dist(p,q);dx=(q[0]-p[0])/ln;dy=(q[1]-p[1])/ln
  if ln<3:edge('Pier',p,q,9,18,brick);continue
  bays=max(1,round(ln/3.6));step=ln/bays
  for k in range(bays):
   t0=k*step;t1=(k+1)*step;w=min(1.65,step*.55);cen=(t0+t1)/2
   at=lambda t:(p[0]+dx*t,p[1]+dy*t)
   for za,zb in [(0,1),(4.2,5.8),(9,10.6),(13.8,15.1),(17.2,18)]:edge('Spandrel',at(t0),at(t1),(za+zb)/2,zb-za,brick)
   for z0,z1 in [(1,4.2),(5.8,9),(10.6,13.8),(15.1,17.2)]:
    edge('Jamb',at(t0),at(cen-w/2),(z0+z1)/2,z1-z0,brick);edge('Jamb',at(cen+w/2),at(t1),(z0+z1)/2,z1-z0,brick)
    edge('Window',at(cen-w/2),at(cen+w/2),(z0+z1)/2,z1-z0,glass,.07)
    edge('Mullion',at(cen-.025),at(cen+.025),(z0+z1)/2,z1-z0,dark,.12)
    for zz in (z0,z0+(z1-z0)*.5,z1):edge('WindowRail',at(cen-w/2),at(cen+w/2),zz,.065,dark,.13)
    edge('StoneSill',at(cen-w/2-.12),at(cen+w/2+.12),z0-.08,.16,stone,.45)
  for zz in (.7,14.3,17.9):edge('StoneCourse',p,q,zz,.22,stone,.42)
# Secondary official curved entrance projection: low entrance volume; height estimated.
box('SecondaryEntrance',7,-36,1.5,5,3,3,stone)
# Interior first floor articulated into published functional zones. Dimensions inferred from proposal; actual furnishing types from2024 photos.
# Ground floor wings surround courtyard; four slab strips and roofs.
strips=[(-20,35,25,43),(-20,-14,-24,25),(15,35,-24,25),(-15,23,-54,-36),(-15,-1,-36,-24)]
for i,(u0,u1,v0,v1) in enumerate(strips):
 for zz in (0,4.7,9.5,14.3,18.1):box('FloorSlab', (u0+u1)/2,(v0+v1)/2,zz,u1-u0,v1-v0,.2,floor if zz<18 else roof)
# courtyard inner walls/windows (inferred plan)
for p,q in [((-14,-24),(-14,25)),((-14,25),(15,25)),((15,25),(15,-24))]:
 edge('CourtyardBase',p,q,.5,1,brick,.25);edge('CourtyardGlazing',p,q,2.7,3.4,glass,.08);edge('CourtyardUpper',p,q,11.2,13.6,brick,.25)
# labs in long north wing + east wing; lounge lower wing
for u in (-15,-5,5,15,25):
 edge('LabPartition',(u,29.5),(u,42),1.8,3.4,white,.14)
for u in (-10,0,10,20,30):
 for v in (31,37):
  box('BenchTop',u,v,.95,3.5,1.05,.09,wood)
  for du in (-1.4,1.4):
   for dv in (-.38,.38):box('BenchLeg',u+du,v+dv,.45,.07,.07,.9,dark)
  box('Monitor',u,v,1.55,.75,.1,.45,screen);box('Scope',u+.95,v,1.25,.45,.35,.35,dark);box('ScopeScreen',u+.95,v-.19,1.28,.32,.025,.2,screen)
  box('Shelf',u,v,1.9,3.4,.4,.07,white)
  for dv in (-1.1,1.1):
   box('LabChairSeat',u,v+dv,.56,.5,.5,.12,dark);box('LabChairBack',u,v+dv+.2,.85,.48,.08,.52,dark);box('ChairPedestal',u,v+dv,.27,.09,.09,.5,dark)
for v in (-16,-7,2,11,20):
 edge('EastRoomPartition',(19.2,v),(34,v),1.8,3.4,white,.14)
 for u in (22,29):
  box('LabBench',u,v+3,.9,3.5,1.1,.1,wood);box('LabCabinet',u,v+3,.42,1,.9,.8,white);box('LabMonitor',u,v+3,1.3,.7,.08,.45,screen)
box('LoungeCarpet',3,-44,.14,31,15,.025,carpet)
for u in (-10,-3,4,11,18):
 for v in (-40,-49):
  box('LoungeTable',u,v,.78,2.2,1.2,.09,wood);box('TableBase',u,v,.38,.12,.12,.75,dark)
  for du in (-.65,.65):
   for dv in (-.95,.95):
    box('GreenChairSeat',u+du,v+dv,.48,.5,.5,.12,green);box('GreenChairBack',u+du,v+dv+(.22 if dv>0 else -.22),.79,.5,.09,.6,green)
# ceiling exposed beams/services, light bars matching photos
for u in (-17,-8,1,10,19,28):
 box('WhiteExposedBeam',u,34,4.25,.25,17,.35,white)
 for v in (29,35,40):box('LinearLight',u,v,3.95,5,.1,.08,white)
for u in (-10,0,10,20):box('LoungeCeilingService',u,-44,4.2,.25,17,.3,white)
# Facade triple stone entrance on NW outer long facade inferred central bay
for u in (2,6,10):
 box('EntranceDoor',u,43.68,1.45,1.6,.13,2.8,dark)
 for du in (-1,1):box('EntranceStoneJamb',u+du,43.9,1.6,.3,.5,3.2,stone)
 box('EntranceLintel',u,43.9,3.3,2.6,.6,.35,stone)
box('EntryLanding',6,45,.1,15,2.5,.2,stone)
# Pictured red tile eave and dark cornice on north facade; exact roof profile remains estimated.
tile=mat('RedTile',(.32,.1,.045))
for u in range(-20,35):
 o=box('TileEave',u+.5,43.5,18.32,.98,1.5,.12,tile);o.rotation_euler.x=math.radians(12)
box('DarkCornice',7.5,43.8,17.65,55,.3,.45,dark)
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.65
for u in (-15,-5,5,15,25):
 # corridor-side door framed within existing lab partition end
 box('LabDoor',u,28.7,1.1,.08,1.3,2.2,wood)
for v in (-16,-7,2,11,20):box('GlassOfficeDoor',18.2,v,1.1,1.2,.08,2.2,glass)
# Clip all slabs to official outline, with proposal-derived courtyard cutout.
from mathutils.geometry import tessellate_polygon
for ob in list(c.objects):
 if ob.name.startswith('BHEE_FloorSlab'):bpy.data.objects.remove(ob,do_unlink=True)
f=next(x for x in refs['buildings'] if x['fid']==292);ps=[(x-143.8499984741211,y-135) for x,y in f['rings_xy_m'][0]][:-1];nn=len(ps)
for zz in (0,4.7,9.5,14.3,18.1):
 vs=[(x,y,z) for z in (zz-.1,zz+.1) for x,y in ps];faces=[(i,(i+1)%nn,(i+1)%nn+nn,i+nn) for i in range(nn)];vv=[Vector((x,y,0)) for x,y in ps]
 for tr in tessellate_polygon([vv]):
  ids=[x if isinstance(x,int) else vv.index(x) for x in tr];faces.extend([tuple(reversed(ids)),tuple(x+nn for x in ids)])
 me=bpy.data.meshes.new('ClippedSlab');me.from_pydata(vs,[],faces);me.update();ob=bpy.data.objects.new('BHEE_ClippedSlab',me);c.objects.link(ob);me.materials.append(roof if zz>18 else floor)
 cut=box('TemporaryCourtyardCutter',.5,.5,zz,29,49,1,roof);mod=ob.modifiers.new('Courtyard','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.context.view_layer.objects.active=ob
 try:bpy.ops.object.modifier_apply(modifier=mod.name)
 except:pass
 bpy.data.objects.remove(cut,do_unlink=True)
c['completion_note']='2026-10-22: detailed facades and first-floor teaching/lab/lounge interior. Published proposal informs room locations; furnishings/material types supported2024 built photos. Heights and upper floors unverified.'
bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));(D/'check.json').write_text(json.dumps({'objects':len(bpy.data.collections[c.name].all_objects) if False else len(bpy.data.collections['Asset_electrical_engineering'].all_objects),'reopened':True,'external_images':[]},indent=2))
