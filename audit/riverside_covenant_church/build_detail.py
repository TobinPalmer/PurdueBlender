import bpy,bmesh,json,math,os
from mathutils import Vector
cfg=json.load(open(os.path.join(os.path.dirname(__file__),'build_config.json'),encoding='utf-8-sig'))
path=bpy.data.filepath; obj=bpy.data.objects.get(cfg['object_name']); coll=bpy.data.collections.get(cfg['collection_name'])
if not path or obj is None or coll is None or obj not in coll.objects[:] or len(coll.objects)!=1: raise RuntimeError('Assigned church collection mismatch')
# Original massing polygon is retained as the shell. Added windows and entrance are deliberately approximate.
mesh=obj.data; original_verts=[tuple(v.co) for v in mesh.vertices]; faces=[tuple(p.vertices) for p in mesh.polygons]; assignments=[]
wallc=(.36,.12,.075) if 'redeemer' in cfg['asset_id'] else (.43,.33,.23)
stonec=(.68,.59,.46) if 'redeemer' in cfg['asset_id'] else (.68,.63,.54)
glassc=(.025,.075,.10); roofc=(.14,.12,.10)
def mat(name,color,rough=.8,metal=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True; bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal; return m
mats=[mat(cfg['asset_id']+'_Masonry',wallc),mat(cfg['asset_id']+'_Limestone',stonec),mat(cfg['asset_id']+'_Glazing',glassc,.2,.06),mat(cfg['asset_id']+'_Roof',roofc)]
verts=list(original_verts); mat_ids=[]
world=obj.matrix_world.copy(); inv=world.inverted_safe();
def to_local(p): return tuple(inv@Vector(p))
def add_face(ids,mi): faces.append(tuple(ids)); mat_ids.append(mi)
def quad(ps,mi):
 k=len(verts); verts.extend(to_local(p) for p in ps); add_face((k,k+1,k+2,k+3),mi)
def box(c,t,n,w,d,h,mi):
 c=Vector(c); t=Vector((t.x,t.y,0)).normalized(); n=Vector((n.x,n.y,0)).normalized(); z=Vector((0,0,1)); hw=w/2;hd=d/2;hh=h/2
 o=[(-hw,-hd,-hh),(hw,-hd,-hh),(hw,hd,-hh),(-hw,hd,-hh),(-hw,-hd,hh),(hw,-hd,hh),(hw,hd,hh),(-hw,hd,hh)]; k=len(verts); verts.extend(to_local(c+t*a+n*b+z*v) for a,b,v in o)
 for f0 in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): add_face(tuple(k+i for i in f0),mi)
# Give original structural polygons stable masonry/roof material slots while preserving all original mesh geometry.
for p in mesh.polygons:
 n=world.to_3x3()@p.normal; mat_ids.append(3 if n.z>.82 else 0)
# Facade bays placed on long vertical faces based on polygon bounds; no exact openings inferred.
minz=min((world@v.co).z for v in mesh.vertices); maxz=max((world@v.co).z for v in mesh.vertices); h=maxz-minz; model_center=sum((world@v.co for v in mesh.vertices),Vector((0,0,0)))/max(1,len(mesh.vertices))
for p in list(mesh.polygons):
 if len(p.vertices)<4: continue
 coords=[world@mesh.vertices[i].co for i in p.vertices]; n=world.to_3x3()@p.normal
 face_center=sum(coords,Vector((0,0,0)))/len(coords)
 if n.dot(face_center-model_center)<0: n=-n
 if abs(n.z)>.2: continue
 lo=min(v.z for v in coords); hi=max(v.z for v in coords); bottoms=[v for v in coords if abs(v.z-lo)<1e-4];
 if hi-lo<3.5 or len(bottoms)<2: continue
 a,b=max(((bottoms[i],bottoms[j]) for i in range(len(bottoms)) for j in range(i+1,len(bottoms))),key=lambda ab:(ab[0]-ab[1]).length)
 delta=b-a; L=Vector((delta.x,delta.y,0)).length
 if L<5: continue
 t=Vector((delta.x,delta.y,0)).normalized(); n=Vector((n.x,n.y,0)).normalized(); count=max(1,int((L-2)//4.0)); spacing=L/(count+1); ww=min(1.65,spacing*.6); wh=1.35
 rows=[1.75,4.45,7.15] if h>9.0 else [1.7,4.3]
 for zoff in rows:
  z=minz+zoff
  if z+wh/2>hi-.35: continue
  for k in range(count):
   p0=a.lerp(b,(k+1)/(count+1)); c=Vector((p0.x,p0.y,z))+n*.075
   box(c,t,n,ww*.76,.06,wh,2); fc=c+n*.05; bw=.09
   box(fc+Vector((0,0,wh/2)),t,n,ww,.13,bw,1); box(fc-Vector((0,0,wh/2)),t,n,ww,.13,bw,1); box(fc-t*(ww/2-bw/2),t,n,bw,.13,wh,1); box(fc+t*(ww/2-bw/2),t,n,bw,.13,wh,1)
# West-facing entrance marker. Its exact position and style are not documented, so it remains explicitly approximate.
wall_faces=[]
for p in mesh.polygons:
 n=world.to_3x3()@p.normal
 if abs(n.z)>.2: continue
 coords=[world@mesh.vertices[i].co for i in p.vertices]
 if len(coords)>=4 and max(v.z for v in coords)-min(v.z for v in coords)>3:
  bottoms=[v for v in coords if v.z<min(c.z for c in coords)+.01]
  if len(bottoms)>=2: wall_faces.append((p,coords,n,bottoms))
entry=min(wall_faces,key=lambda x:x[2].x,default=None)
if entry:
 p0=min((v for v in entry[1]),key=lambda v:v.x); n=Vector((entry[2].x,entry[2].y,0)).normalized(); t=Vector((n.y,-n.x,0)).normalized(); center=Vector((sum(v.x for v in entry[1])/len(entry[1]),sum(v.y for v in entry[1])/len(entry[1]),minz+1.3))+n*.1
 box(center,t,n,2.1,.12,2.6,2)
# Rebuild the same mesh datablock and preserve all existing structural faces.
oldname=mesh.name; new=bpy.data.meshes.new(oldname+'_facade'); new.from_pydata(verts,[],faces); new.materials.clear()
for m in mats:new.materials.append(m)
new.update()
for p,mi in zip(new.polygons,mat_ids): p.material_index=mi
bm=bmesh.new();bm.from_mesh(new);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(new);bm.free();new.update();obj.data=new
if mesh.users==0:bpy.data.meshes.remove(mesh)
new.name=oldname
bpy.ops.wm.save_as_mainfile(filepath=path)
print('BUILD_RESULT_JSON='+json.dumps({'asset_id':cfg['asset_id'],'original_vertex_count':len(original_verts),'new_vertex_count':len(new.vertices),'new_face_count':len(new.polygons),'height_m':round(h,3),'position_footprint':'retained from original source mesh; not independently verified','collection_objects':len(coll.objects)}))
