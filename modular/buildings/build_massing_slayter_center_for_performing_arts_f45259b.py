import bpy,bmesh,json,math,os
from mathutils import Vector
EVIDENCE=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','audit','slayter_center_for_performing_arts'))
cfg=json.load(open(os.path.join(EVIDENCE,'build_config.json'),encoding='utf-8-sig'))
blend=bpy.data.filepath; obj=bpy.data.objects.get(cfg['object_name']); coll=bpy.data.collections.get(cfg['collection_name'])
if not blend or obj is None or coll is None or obj not in coll.objects[:] or len(coll.objects)!=1: raise RuntimeError('Slayter asset structure mismatch')
with open(os.path.join(EVIDENCE,cfg['source_feature_file']),encoding='utf-8-sig') as f: feature=json.load(f)
ring=feature['geometry']['rings'][0]; ring=ring[:-1] if ring[0]==ring[-1] else ring
lat0,lon0=40.4274,-86.9137
pts=[Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0)) for lon,lat in ring]
xs=[p.x for p in pts]; ys=[p.y for p in pts]; xmin,xmax=min(xs),max(xs); ymin,ymax=min(ys),max(ys); cx=(xmin+xmax)/2; cy=(ymin+ymax)/2
# The GIS record is the mapped venue envelope, not a surveyed structure boundary.
# The 2006 Commons photo's WGS84 position and compass heading point from the
# north-northwest audience approach toward the venue center; internal geometry
# follows that geotagged bearing (about 334 degrees from the stage toward camera).
front_axis=Vector((-0.432,0.902,0)); front_axis.normalize()
width_axis=Vector((front_axis.y,-front_axis.x,0)); width_axis.normalize()
stage_center=Vector((cx,cy,0))
def local(u,v,z=0): return stage_center+width_axis*u+front_axis*v+Vector((0,0,z))
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
stage_back_w=float(cfg['stage_back_width_ft'])*0.3048; stage_front_w=float(cfg['stage_front_width_ft'])*0.3048; stage_d=float(cfg['stage_depth_ft'])*0.3048
def prism_xy(outline,z0,z1,mi):
 bottom=[(x,y,z0) for x,y in outline]; top=[(x,y,z1) for x,y in outline]
 poly(list(reversed(bottom)),mi); poly(top,mi)
 for i in range(len(outline)): poly([bottom[i],bottom[(i+1)%len(outline)],top[(i+1)%len(outline)],top[i]],mi)
# The published stage flares from 34 ft at the rear to 56 ft at the north-facing front and is 46 ft deep.
stage_outline=[(local(-stage_back_w/2,-stage_d).x,local(-stage_back_w/2,-stage_d).y),
               (local(-stage_front_w/2,0).x,local(-stage_front_w/2,0).y),
               (local(stage_front_w/2,0).x,local(stage_front_w/2,0).y),
               (local(stage_back_w/2,-stage_d).x,local(stage_back_w/2,-stage_d).y)]
prism_xy(stage_outline,.24,.72,concrete)
# Backstage service block sits behind the stage; its footprint remains approximate.
box(local(0,-stage_d-.55,2.05),width_axis*5.6,front_axis*.9,3.2,dark)
# Eight seating tiers spread north from the stage and stay inside the mapped center envelope.
rows=int(cfg.get('audience_rows',8)); row_start=3.0; row_step=max(1.6,(ymax-cy-row_start-2.0)/max(rows,1))
for i in range(rows):
 dist=row_start+i*row_step; z=.28+i*.36; width=min((xmax-xmin)*.72,10.5+i*2.5)
 # Break the widening audience tiers into sections for aisles; rows face south toward the stage.
 for frac in (-.34,0,.34):
  seg=width*.27; c=local(width*frac,dist,z)
  box(c,width_axis*seg,front_axis*(row_step*.62),.36,seatmat)
  box(local(width*frac,dist,z+.34),width_axis*(seg*.9),front_axis*(row_step*.48),.14,concrete)
# Slender white acoustic reflector fins form the photographed stage backdrop.
for i in range(13):
 u=-8.0+i*(16.0/12); h=4.3+1.4*(1.0-abs(u)/8.0)
 box(local(u,-stage_d+.4,.72+h/2),width_axis*(.72 if i not in (0,12) else .9),front_axis*.34,h,canopy)
# A broad shallow concrete canopy hangs beneath the three steel tripod legs.
# Its roof edge is estimated from the photo; the stage dimensions remain source-published.
apex=15.5; canopy_center=local(0,-stage_d*.34,0); apex_pt=local(0,-stage_d*.34,apex)
for u,v in ((-12,-stage_d*.34),(12,-stage_d*.34),(0,-stage_d-7)):
 beam(local(u,v,.45),apex_pt,.48,steel)
segments=32; rx=10.8; ry=5.7; top=[]; bottom=[]
for i in range(segments):
 a=2*math.pi*i/segments; u=rx*math.cos(a); v=ry*math.sin(a)
 top.append(tuple(canopy_center+width_axis*u+front_axis*v+Vector((0,0,7.7))))
 bottom.append(tuple(canopy_center+width_axis*u+front_axis*v+Vector((0,0,7.15))))
poly(top,canopy); poly(bottom,canopy)
for i in range(segments): poly([bottom[i],bottom[(i+1)%segments],top[(i+1)%segments],top[i]],canopy)
# Steel suspension cables radiate from the tripod head to the canopy rim.
for i in range(16):
 a=2*math.pi*i/16; u=rx*.96*math.cos(a); v=ry*.96*math.sin(a)
 q=canopy_center+width_axis*u+front_axis*v+Vector((0,0,7.72))
 beam(apex_pt,q,.045,steel)
# Front apron steps descend away from the raised stage toward the audience.
for i in range(5): box(local(0,i*.42,.40-i*.07),width_axis*.48,front_axis*3.8,.16,concrete)
old=obj.data; oldname=old.name; mesh=bpy.data.meshes.new(oldname+'_amphitheater'); mesh.from_pydata(verts,[],faces)
for m in mats: mesh.materials.append(m)
mesh.update()
for p,mi in zip(mesh.polygons,mids): p.material_index=mi
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update(); obj.data=mesh
if old.users==0: bpy.data.meshes.remove(old)
mesh.name=oldname; obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
bpy.ops.wm.save_as_mainfile(filepath=blend)
print('BUILD_RESULT_JSON='+json.dumps({'asset_id':cfg['asset_id'],'source_fid':feature['attributes']['FID'],'mapped_envelope_xy_m':[[round(xmin,3),round(xmax,3)],[round(ymin,3),round(ymax,3)]],'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'tripod_apex_estimate_m':apex,'canopy_edge_estimate_m':7.7,'stage_dimensions_m':{'front_width':stage_front_w,'back_width':stage_back_w,'depth':stage_d},'audience_rows':rows,'collection_objects':len(coll.objects)}))
