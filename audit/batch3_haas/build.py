import bpy,json,shutil,math
from pathlib import Path
from mathutils import Vector
D=Path('audit/batch3_haas');fp=Path(bpy.data.filepath);shutil.copy2(fp,D/'before.blend');c=bpy.data.collections['Asset_felix_haas_hall'];ref=bpy.data.collections.new('HAAS_Batch3_Unverified_Interior_Archive');bpy.context.scene.collection.children.link(ref);ref.hide_render=True;ref.hide_viewport=True
start=False;arch=[]
for o in list(c.all_objects):
 if o.name=='HAAS_Rotunda_Terrazzo_Floor':start=True
 if start and not o.name.startswith(('HAAS_Corrected','AssetRoot')):
  if o.type=='MESH':
   for col in list(o.users_collection):col.objects.unlink(o)
   ref.objects.link(o);arch.append(o.name)
def mat(n,col,rough=.65):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;return m
wall=mat('HAAS_Plan_Painted_Plaster_estimated',(.64,.60,.51));wood=mat('HAAS_Plan_Laminate_estimated',(.27,.15,.065));metal=mat('HAAS_Plan_Charcoal_estimated',(.045,.05,.055));fabric=mat('HAAS_Plan_Upholstery_estimated',(.08,.12,.16));floor=mat('HAAS_Plan_Resilient_Floor_estimated',(.35,.33,.28));porcelain=mat('HAAS_Plan_Porcelain_estimated',(.8,.8,.77));added=[]
def cube(n,loc,sz,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name='HAAS_Plan_'+n;o.dimensions=sz;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for col in list(o.users_collection):col.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(m);o['evidence']='Purdue CS HAAS_first.pdf; approximate diagram registration; furniture and heights estimated';added.append(o.name);return o
def xy(u,v):return (-26+(v-97)*28.1/713,26.5-(u-48)*52.5/1417)
def slab(n,r,z,h,m):
 a=xy(r[0],r[1]);b=xy(r[2],r[3]);return cube(n,((a[0]+b[0])/2,(a[1]+b[1])/2,z+h/2),(abs(b[0]-a[0]),abs(b[1]-a[1]),h),m)
slab('Ground_Main',(52,101,1461,806),.3,.12,floor);slab('Ground_Entrance',(472,810,1060,1120),.3,.12,floor)
# Rectangles traced from published schematic, not construction drawings.
rooms=[]
def room(num,r,kind='office'):rooms.append((str(num),r,kind))
for i,(num,a,b) in enumerate([(156,212,315),(154,315,410),(152,410,527),(150,527,623),(148,623,739),(146,739,842),(144,842,953),(142,953,1057),(140,1057,1150),(132,1245,1380)]):room(num,(a,98,b,208 if num!=132 else 185),'printer' if num==140 else 'office')
for num,a,b in [(164,156,257),(170,257,370),(172,370,485),(174,485,605),(176,605,707),(110,804,900),(112,900,990),(114,990,1084),(116,1084,1180),(118,1180,1284),(120,1284,1380)]:room(num,(a,712,b,810))
for num,r,kind in [('156A',(49,98,210,195),'office'),('156B',(49,195,150,321),'office'),('164A',(49,429,155,554),'office'),('164B',(49,554,155,645),'printer'),('164C',(49,645,155,810),'office'),('162',(155,429,257,505),'storage'),('164',(155,505,257,712),'reception'),('130',(1380,98,1465,339),'office'),('128',(1355,339,1465,446),'office'),('126',(1355,446,1465,539),'office'),('124',(1355,539,1465,660),'office'),('122',(1380,660,1465,810),'office'),('151',(310,264,597,446),'ta'),('145',(597,264,886,446),'ta'),('143',(886,264,1074,446),'student'),('175',(310,446,597,627),'ta'),('111',(597,446,886,627),'conference'),('115',(886,446,1074,627),'student'),('117',(1074,446,1168,627),'toilet'),('119',(1197,435,1290,627),'toilet'),('135',(1074,357,1197,446),'storage'),('1U01',(1197,357,1290,435),'storage'),('101',(470,933,655,1125),'conference'),('102',(920,933,1063,1027),'office'),('104',(920,1027,1063,1125),'office'),('106',(825,1027,920,1125),'storage')]:room(num,r,kind)
# Room walls with real openings on one edge; shared edges remain joined but no overlapping copies.
segments=set()
for num,r,kind in rooms:
 u0,v0,u1,v1=r
 # door centered on lower schematic edge; plan does not show door swing, recorded approximate
 edges=[((u0,v0),(u1,v0)),((u0,v0),(u0,v1)),((u1,v0),(u1,v1))]
 mid=(u0+u1)/2;gap=14
 edges += [((u0,v1),(mid-gap,v1)),((mid+gap,v1),(u1,v1))]
 for aa,bb in edges:
  key=tuple(sorted((aa,bb)))
  if key in segments:continue
  segments.add(key);a=xy(*aa);b=xy(*bb);cube('Partition_'+num+'_'+str(len(segments)),((a[0]+b[0])/2,(a[1]+b[1])/2,1.92),(max(abs(a[0]-b[0]),.12),max(abs(a[1]-b[1]),.12),3),wall)
 a=xy(u0,v0);b=xy(u1,v1);x=(a[0]+b[0])/2;y=(a[1]+b[1])/2
 if kind not in ['storage','toilet']:
  count=4 if kind=='ta' else 1
  for k in range(count):
   yy=y+(k-(count-1)/2)*1.3;cube('Desk_'+num+'_'+str(k),(x,yy,1.15),(1.45,.7,.07),wood);cube('DeskPedestal_'+num+'_'+str(k),(x+.5,yy,.78),(.35,.6,.7),metal);cube('ChairSeat_'+num+'_'+str(k),(x-.1,yy+.7,.86),(.5,.5,.1),fabric);cube('ChairBack_'+num+'_'+str(k),(x-.1,yy+.93,1.16),(.5,.08,.55),fabric);cube('ChairStem_'+num+'_'+str(k),(x-.1,yy+.7,.63),(.07,.07,.4),metal)
  if kind=='conference':
   cube('ConferenceTable_'+num,(x, y,1.15),(2.8,1.2,.1),wood)
 if kind=='toilet':
  for k in range(3):cube('WC_'+num+'_'+str(k),(x,y+(k-1)*1.1,.65),(.5,.65,.45),porcelain)
# Historical plan places stairs at west corner, northeast and entrance.
for tag,r in [('West',(50,321,249,429)),('Northeast',(1150,99,1245,282)),('Entrance',(545,810,693,933))]:
 for k in range(18):
  u0,v0,u1,v1=r;h=(k+1)*.18;slab('Stair_'+tag+'_'+str(k),(u0+(u1-u0)*k/18,v0,u0+(u1-u0)*(k+1)/18,v1),.42,h,wall)
slab('Lift_Core',(1304,187,1357,282),.42,3,metal)
# metric noise on estimated floor, avoids unscaled Generated coordinates
nt=floor.node_tree;n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=35;t=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(t.outputs['Object'],n.inputs['Vector']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.08;bump.inputs['Distance'].default_value=.003;nt.links.new(n.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])
bpy.ops.wm.save_as_mainfile(filepath=str(fp));bpy.ops.wm.open_mainfile(filepath=str(fp));c=bpy.data.collections['Asset_felix_haas_hall'];(D/'changes.json').write_text(json.dumps({'archived':arch,'added':added,'rooms':rooms,'count':len(c.all_objects),'reopened':True,'limitations':'Only published schematic first floor. Door locations furniture heights finishes estimated. Upper floor remains unmodeled; old fictional rotunda and roof-piercing seminar archived.'},indent=2))

