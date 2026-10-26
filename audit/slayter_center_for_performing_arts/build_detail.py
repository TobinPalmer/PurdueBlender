import bpy,bmesh,json,math,os
from mathutils import Vector
cfg=json.load(open(os.path.join(os.path.dirname(__file__),'build_config.json'),encoding='utf-8-sig'))
blend=bpy.data.filepath; obj=bpy.data.objects.get(cfg['object_name']); coll=bpy.data.collections.get(cfg['collection_name'])
if not blend or obj is None or coll is None or obj not in coll.objects[:] or len(coll.objects)!=1: raise RuntimeError('Slayter asset structure mismatch')
with open(os.path.join(os.path.dirname(__file__),cfg['source_feature_file']),encoding='utf-8-sig') as f: feature=json.load(f)
ring=feature['geometry']['rings'][0]; ring=ring[:-1] if ring[0]==ring[-1] else ring
lat0,lon0=40.4274,-86.9137
pts=[Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0)) for lon,lat in ring]
xs=[p.x for p in pts]; ys=[p.y for p in pts]; xmin,xmax=min(xs),max(xs); ymin,ymax=min(ys),max(ys); cx=(xmin+xmax)/2; cy=(ymin+ymax)/2
# This GIS record is the mapped center boundary, not a surveyed wall perimeter; all stage and seat locations are approximate within it.
span=min(xmax-xmin,ymax-ymin); stage_x=xmin+span*0.25; stage_y=cy
mats=[]
def mat(name,color,rough=.8,metal=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True; bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal; mats.append(m); return len(mats)-1
concrete=mat('Slayter_Stage_Concrete',(0.48,.48,.45)); seatmat=mat('Slayter_Seating_Concrete',(.34,.36,.35)); steel=mat('Slayter_Support_Steel',(.17,.19,.20),.4,.7); canopy=mat('Slayter_Canopy_Concrete',(.69,.68,.63)); dark=mat('Slayter_Backstage',(.16,.17,.16));
verts=[]; faces=[]; mids=[]
def poly(v,mi):
 k=len(verts); verts.extend(tuple(Vector(p)) for p in v); faces.append(tuple(range(k,k+len(v)))); mids.append(mi)
def box(c,dx,dy,dz,mat_id):
 c=Vector(c); ex=Vector(dx)*.5; ey=Vector(dy)*.5; ez=Vector((0,0,dz*.5)); lo=c-ez; hi=c+ez; p=[lo-ex-ey,lo+ex-ey,lo+ex+ey,lo-ex+ey,hi-ex-ey,hi+ex-ey,hi+ex+ey,hi-ex+ey]
 for q,m in [((0,3,2,1),mat_id),((4,5,6,7),mat_id),((0,1,5,4),mat_id),((1,2,6,5),mat_id),((2,3,7,6),mat_id),((3,0,4,7),mat_id)]: poly([p[i] for i in q],m)
def beam(a,b,w,mi):
 a=Vector(a); b=Vector(b); d=b-a; axis=d.normalized(); ref=Vector((0,1,0)) if abs(axis.dot(Vector((0,1,0))))<.92 else Vector((1,0,0)); side=axis.cross(ref).normalized()*w/2; up=axis.cross(side).normalized()*w/2
 p=[a-side-up,a+side-up,a+side+up,a-side+up,b-side-up,b+side-up,b+side+up,b-side+up]
 for q in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): poly([p[i] for i in q],mi)
# Raised stage apron and low backstage block.
stage_w=13.5; stage_d=7.5
box((stage_x+stage_d*.5,stage_y,.48),(stage_d,0,0),(0,stage_w,0),.48,concrete)
box((stage_x+stage_d*.88,stage_y,2.25),(0,5.6,0),(.8,0,0),3.5,dark)
# A radial fan of eight rising seating tiers faces the stage. Rows are kept within the mapped center envelope.
rows=int(cfg.get('audience_rows',8)); row_start=stage_x+stage_d+3.0; row_step=max(1.6,(xmax-row_start-2.0)/max(rows,1))
for i in range(rows):
 x=row_start+i*row_step; z=.28+i*.36; width=min((ymax-ymin)*.72,10.5+i*2.5)
 # Break each bench into sections for stairs and circulation aisles.
 for yc in (-width*.35,0,width*.35):
  seg=width*.27; box((x,stage_y+yc,z),(row_step*.62,0,0),(0,seg,0),.36,seatmat)
  box((x,stage_y+yc,z+.34),(row_step*.48,0,0),(0,seg*.9,0),.14,concrete)
# Concrete tripodal roof canopy and steel support legs, kept separate from the seating envelope.
apex=9.0; roofx=stage_x+2.4; roofy=stage_y
for p in ((stage_x-1.6,stage_y-6.8,.4),(stage_x-1.6,stage_y+6.8,.4),(stage_x+7.4,stage_y,.4)):
 beam(p,(roofx,roofy,apex),.32,steel)
# Four faceted concrete panels approximate the suspended, folded canopy; its exact geometry is unverified.
corners=[(stage_x-3,stage_y-8,6.4),(stage_x+8,stage_y-8,7.6),(stage_x+8,stage_y+8,7.6),(stage_x-3,stage_y+8,6.4)]
poly(corners,canopy); poly([corners[0],corners[1],(roofx,roofy,apex)],canopy); poly([corners[1],corners[2],(roofx,roofy,apex)],canopy); poly([corners[2],corners[3],(roofx,roofy,apex)],canopy); poly([corners[3],corners[0],(roofx,roofy,apex)],canopy)
# Small front apron and stairs.
for i in range(5): box((stage_x+stage_d+0.4+i*.45,stage_y,0.12+i*.10),(.55,0,0),(0,3.2,0),.20,concrete)
old=obj.data; oldname=old.name; mesh=bpy.data.meshes.new(oldname+'_amphitheater'); mesh.from_pydata(verts,[],faces)
for m in mats: mesh.materials.append(m)
mesh.update()
for p,mi in zip(mesh.polygons,mids): p.material_index=mi
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update(); obj.data=mesh
if old.users==0: bpy.data.meshes.remove(old)
mesh.name=oldname; obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
bpy.ops.wm.save_as_mainfile(filepath=blend)
print('BUILD_RESULT_JSON='+json.dumps({'asset_id':cfg['asset_id'],'source_fid':feature['attributes']['FID'],'mapped_envelope_xy_m':[[round(xmin,3),round(xmax,3)],[round(ymin,3),round(ymax,3)]],'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'stage_apex_estimate_m':apex,'seating_rows':rows,'collection_objects':len(coll.objects)}))
