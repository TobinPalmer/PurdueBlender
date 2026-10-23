import bpy,math,json,pathlib
from mathutils import Vector
p=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');d=p/'audit/batch3_elliott';f=p/'modular/buildings/elliott_hall_of_music.blend'
import shutil;shutil.copy2(d/'before.blend',f)
bpy.ops.wm.open_mainfile(filepath=str(f));c=bpy.data.collections['Asset_elliott_hall_of_music'];walls=bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls'];poly=[(v.co.x,v.co.y) for v in walls.data.vertices if abs(v.co.z)<.01]
def inside(x,y):
 q=False
 for i,(a,b) in enumerate(poly):
  u,v=poly[i-1]
  if (b>y)!=(v>y) and x<(u-a)*(y-b)/(v-b)+a:q=not q
 return q
def mat(name,col,rough=.7):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;n=m.node_tree.nodes;bs=n.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Roughness'].default_value=rough
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=65;b=n.new('ShaderNodeBump');b.inputs['Distance'].default_value=.001;b.inputs['Strength'].default_value=.14;m.node_tree.links.new(noise.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],bs.inputs['Normal']);return m
seat=mat('ELLT_Photo_Tan_Upholstery',(.32,.19,.10));wood=mat('ELLT_Stage_Timber',(.22,.12,.055));con=mat('ELLT_Interior_Pale_Plaster',(.64,.58,.45));red=mat('ELLT_Stage_Red_Velour',(.22,.012,.018));metal=mat('ELLT_Dark_Seat_Frame',(.025,.025,.025));floor=mat('ELLT_Carpet',(.20,.20,.19));black=mat('ELLT_Black_Stage_Drape',(.009,.009,.012));teal=mat('ELLT_Balcony_Teal',(.025,.10,.105))
batches={}
def box(n,loc,dim,m):
 verts=[(loc[0]+i*dim[0]/2,loc[1]+j*dim[1]/2,loc[2]+k*dim[2]/2) for i,j,k in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 theta=math.radians(-129.36);verts=[(x*math.cos(theta)-y*math.sin(theta),x*math.sin(theta)+y*math.cos(theta),z) for x,y,z in verts]
 vs,fs=batches.setdefault(m.name,([],[]));base=len(vs);vs.extend(verts);fs.extend([tuple(base+i for i in face) for face in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]])

# Local main-axis orientation is an estimate pending measured plan. Keep all new structure inside source perimeter.
(d/'polygon.json').write_text(json.dumps(poly))
box('House_Floor',(0,0,-.2),(64,43,.25),floor)
for side in [-1,1]:
 box('Interior_Pale_Wall_%s'%side,(2,side*21.2,9),(43,.3,18),con)
 for k in range(12):box('Wall_Pilaster_%s_%s'%(side,k),(-17+k*3.6,side*20.9,9),(.36,.35,18),con)
box('Stage',(-22,0,1.0),(11,34,1.2),wood)
box('Proscenium_Left',(-17,-18,7),(.6,2,12),con);box('Proscenium_Right',(-17,18,7),(.6,2,12),con);box('Proscenium_Header',(-17,0,13),(.6,38,2),con)
for j in range(48):box('Curtain_%02d'%j,(-25.9,-16+j*.68,6.5),(.35,.62,10),red if j<7 or j>40 else black)
count=0
for level,rows,start,z0 in [(0,27,-13,.3),(1,13,8,7),(2,13,10,12)]:
 for r in range(rows):
  x=start+r*.92;z=z0+r*(.12 if level==0 else .28);half=15+min(r*.16,3)
  for segment in range(-int(half),int(half)):
   yy=segment+.5;box('Tier_%s_%s_%s'%(level,r,segment),(x+.007*yy*yy,yy,z-.12),(.95,1,.22),floor)
  for j in range(-int(half/.57),int(half/.57)+1):
   y=j*.57
   if any(abs(y-a)<.8 for a in [-11,-4,4,11]):continue
   theta=math.radians(-129.36)
   if not all(inside((x+.007*y*y+dx)*math.cos(theta)-(y+dy)*math.sin(theta),(x+.007*y*y+dx)*math.sin(theta)+(y+dy)*math.cos(theta)) for dx in [-.45,.45] for dy in [-.3,.3]):continue
   box('Seat_%s_%s_%s'%(level,r,j),(x+.007*y*y,y,z+.43),(.43,.49,.12),seat);box('Back_%s_%s_%s'%(level,r,j),(x+.23+.007*y*y,y,z+.75),(.10,.49,.64),seat);box('Frame_%s_%s_%s'%(level,r,j),(x+.007*y*y,y,z+.20),(.12,.32,.4),metal);count+=1
 if level:
  box('Front_Balcony_%s'%level,(start-.4,0,z0+.5),(.16,30,1),teal)
 for y in [-19,19]:box('Balcony_Rail_%s_%s'%(level,y),(start+rows*.46,y,z0+1),(rows*.92,.09,1),metal)
for name,(verts,faces) in batches.items():
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('ELLT_B3_'+name,me);c.objects.link(o);me.materials.append(bpy.data.materials[name]);o['evidence_status']='Photo/chart informed, estimated dimensions; northeast stage orientation inferred from official plan outline'
# No guessed backstage/practice rooms.

bpy.ops.wm.save_as_mainfile(filepath=str(f));bpy.ops.wm.open_mainfile(filepath=str(f));c=bpy.data.collections['Asset_elliott_hall_of_music'];(d/'result.json').write_text(json.dumps({'export_objects':len(c.all_objects),'estimated_seats':count,'footprint_unchanged':True,'save_reopen':True,'limitations':'Seat pitch/row placement/room orientation inferred; not exact capacity or surveyed interior'},indent=2))
s=bpy.context.scene
names={q.name for q in c.all_objects}
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render=o.name not in names
for o in c.all_objects:
 if 'Roof' in o.name:o.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=12;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Review');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.7,.7,.7,1)
cd=bpy.data.cameras.new('Review');cam=bpy.data.objects.new('Review',cd);s.collection.objects.link(cam);s.camera=cam;cam.location=(-23,-28,16);target=Vector((14,17,5));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=21;s.render.filepath=str(d/'interior.png');bpy.ops.render.render(write_still=True)
