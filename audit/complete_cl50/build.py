import bpy,math,json,shutil
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=P/'audit/complete_cl50';f=P/'modular/buildings/class_of_1950.blend'
if not (D/'before.blend').exists():shutil.copy2(f,D/'before.blend')
c=bpy.data.collections['Asset_class_of_1950'];ref=bpy.data.collections.new('CL50_PreCompletion_Interior');bpy.context.scene.collection.children.link(ref);ref.hide_render=True;ref.hide_viewport=True
keep=['GIS','Penthouse','Root','Seward','Sculpt','Plaque','Lantern']
for o in list(c.all_objects):
 if o.type=='MESH' and not any(t in o.name for t in keep):
  for q in list(o.users_collection):q.objects.unlink(o)
  ref.objects.link(o)
def mat(n,col,rough=.65):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*col,1);s.inputs['Roughness'].default_value=rough;return m
cream=mat('CL50_Photographic_Cream_Textured_Masonry',(.66,.62,.49));wood=mat('CL50_Photographic_Brown_Wood',(.19,.085,.028),.45);seat=mat('CL50_Photographic_Dark_Seats',(.025,.028,.024));floor=mat('CL50_Pale_Terrazzo',(.48,.46,.39));white=mat('CL50_Acoustic_Ceiling',(.8,.8,.75));black=mat('CL50_Speaker_Black',(.01,.01,.012));glass=mat('CL50_Entrance_Glass',(.13,.21,.23),.16);metal=mat('CL50_Bronze_Frame',(.11,.065,.025),.3)
for m,scale,strength in [(cream,35,.16),(floor,120,.07),(wood,7,.06)]:
 t=m.node_tree;n=t.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;b=t.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=strength;b.inputs['Distance'].default_value=.025;t.links.new(n.outputs['Fac'],b.inputs['Height']);t.links.new(b.outputs['Normal'],t.nodes.get('Principled BSDF').inputs['Normal'])
def xy(u,v):return ((v-287)/732*43.3-30.3,18.975-(u-60)/540*37.35)
def cube(n,p,d,m):
 vs=[(i*d[0]/2,j*d[1]/2,k*d[2]/2) for i,j,k in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]);me.update();o=bpy.data.objects.new('CL50_New_'+n,me);c.objects.link(o);o.location=p;me.materials.append(m);return o

def wall(n,a,b,z=1.9,h=3,t=.15,m=cream):
 dx=b[0]-a[0];dy=b[1]-a[1];o=cube(n,((a[0]+b[0])/2,(a[1]+b[1])/2,z),(math.hypot(dx,dy),t,h),m);o.rotation_euler.z=math.atan2(dy,dx);return o
def poly(n,pts,z,m):
 me=bpy.data.meshes.new(n);me.from_pydata([(x,y,z) for x,y in pts],[],[tuple(range(len(pts)))]);me.update();o=bpy.data.objects.new('CL50_New_'+n,me);c.objects.link(o);me.materials.append(m);return o
# Register official conference plan to GIS overall dimensions; room walls approximate, not surveyed.
aud=[xy(u,v) for u,v in [(120,502),(145,502),(346,398),(380,398),(415,410),(443,450),(443,860),(430,892),(400,914),(346,914),(145,810),(120,810)]]
poly('Auditorium224_Floor',aud,.42,floor)
for i,(a,b) in enumerate(zip(aud,aud[1:]+aud[:1])):wall('Auditorium224_Partition'+str(i),a,b,4.4,8)
# Stage follows plan west side (image left); auditorium seating faces local north.
st=xy(154,656);cube('Stage',(st[0],st[1],.7),(17,3,.55),wood);cube('Single_Projection_Screen',(st[0],st[1]+1.4,4.3),(11,.08,4),white)
for s in [-1,1]:cube('Speaker',(st[0]+s*7,st[1]+1.3,4),( .38,.15,3.2),black)
cube('Lectern',(st[0]+5,st[1]-.8,1.35),(.8,.65,1.1),wood)
# Twenty curved desk rows with central stepped aisle; approximate500seat capacity layout supported by archive.
for row in range(20):
 y=st[1]-2.8-row*.8;z=.5+row*.16;half=8.5+min(row,10)*.30
 for side in [-1,1]:
  for j in range(12):
   x=st[0]+side*(1.0+j*(half-1)/12);cy=y+.007*(x-st[0])**2
   cube('Seat_%02d_%s_%02d'%(row,side,j),(x,cy,z+.43),(.46,.43,.09),seat);cube('Back_%02d_%s_%02d'%(row,side,j),(x,cy-.18,z+.72),(.46,.09,.5),seat)
  # Thin desk sections follow shallow curve, separated by central aisle.
  for j in range(6):
   a=st[0]+side*(.8+j*(half-.8)/6);b=st[0]+side*(.8+(j+1)*(half-.8)/6)
   wall('CurvedWoodDesk',(a,y+.007*(a-st[0])**2+.4),(b,y+.007*(b-st[0])**2+.4),z+.77,.075,.36,wood)
 cube('Central_Aisle_Step',(st[0],y,z-.06),(1.3,.8,.16),floor)
# Three small teaching rooms along the curved south face; map positions121125129.
for label,v1,v2 in [('129',435,576),('125',576,733),('121',733,872)]:
 a,b=xy(492,v1),xy(492,v2);cc=xy(535,(v1+v2)/2);poly('Room'+label+'_Floor',[xy(492,v1),xy(560,v1),xy(560,v2),xy(492,v2)],.43,floor)
 wall('Room'+label+'_North',a,b,2,3.2)
 for vv in [v1,v2]:wall('Room'+label+'_Partition',xy(492,vv),xy(560,vv),2,3.2)
 cube('Room'+label+'_TeachingBoard',(cc[0],a[1]+.1,2),(4,.07,1.3),white)
 for rr in range(4):
  for jj in range(5):cube('Room'+label+'_Table',(cc[0]+(jj-2)*1.1,cc[1]+(rr-1.5)*.8,1.15),(.85,.48,.06),wood)
# Lobby perimeter circulation / acoustic ceiling grid visible from interior.
for u in range(65,480,24):
 for v in range(300,1000,24):
  p=xy(u,v)
  if -28<p[0]<11 and -11<p[1]<18:cube('AcousticTile',(p[0],p[1],8.2),(1.36,1.58,.045),white)
# Round columns along the curved frontage, pale stone capitals supported by source photo.
ring=[(-30.317,-13.17),(-25,-15.5),(-18,-17.5),(-9,-18.3),(0,-17.3),(8,-14.7),(12.9,-13.25)]
for i,p in enumerate(ring):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.40,depth=5.5,location=(*p,2.9));o=bpy.context.object;o.name='CL50_New_RoundBrickColumn'+str(i)
 for q in list(o.users_collection):q.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(bpy.data.materials.get('CL50_Finish_Brick') or cream);cube('ColumnCapital'+str(i),(*p,5.75),(1,1,.32),cream)
# Meter-scaled facade brick UVs, vertically aligned mortar courses.
w=bpy.data.objects['CL50_Corrected_GIS_Wall_Envelope'];uv=w.data.uv_layers.new(name='Meters_AlongWall_Height')
for face in w.data.polygons:
 vv=[w.data.vertices[i].co for i in face.vertices];a=vv[0];b=next((v for v in vv[1:] if (Vector((v.x-a.x,v.y-a.y))).length>.01),a);direction=Vector((b.x-a.x,b.y-a.y));direction.normalize()
 for li in face.loop_indices:
  v=w.data.vertices[w.data.loops[li].vertex_index].co;uv.data[li].uv=((v.x-a.x)*direction.x+(v.y-a.y)*direction.y,v.z)
brick=bpy.data.materials.get('CL50_Finish_Brick')
if brick:
 t=brick.node_tree;n=t.nodes.new('ShaderNodeTexBrick');n.inputs['Scale'].default_value=1;n.inputs['Brick Width'].default_value=.215;n.inputs['Row Height'].default_value=.075;n.inputs['Mortar Size'].default_value=.007;n.inputs['Color1'].default_value=(.24,.065,.025,1);n.inputs['Color2'].default_value=(.39,.14,.055,1);n.inputs['Mortar'].default_value=(.42,.37,.27,1);co=t.nodes.new('ShaderNodeTexCoord');t.links.new(co.outputs['UV'],n.inputs['Vector']);t.links.new(n.outputs['Color'],t.nodes.get('Principled BSDF').inputs['Base Color']);b=t.nodes.new('ShaderNodeBump');b.inputs['Distance'].default_value=.008;b.inputs['Strength'].default_value=.25;t.links.new(n.outputs['Fac'],b.inputs['Height']);t.links.new(b.outputs['Normal'],t.nodes.get('Principled BSDF').inputs['Normal'])
c['completion_evidence']='2024 Purdue RoadSchool plan + GoogleMaps JinchuLiu historical interior photo; registered floorplan approximate. No measured vertical survey.'
bpy.ops.wm.save_as_mainfile(filepath=str(f))
(D/'changes.json').write_text(json.dumps({'objects':len(c.all_objects),'archived_objects':len(ref.all_objects),'room_plan':'2024 Purdue RoadSchool PDF','interior':'GoogleMaps historical JinchuLiu photo; parent verification','estimated':'all vertical dimensions, precise seating spacing, room registration','seats':480,'placement_changed':False},indent=2))
print('SAVED',len(c.all_objects))
