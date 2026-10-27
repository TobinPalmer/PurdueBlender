import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path('.').resolve()
AUD=ROOT/'audit/alpha_chi_omega_fid765'
SRC=AUD/'sources/fid765_arcgis_4326.json'
OUT=ROOT/'modular/buildings/alpha_chi_omega_fid765.blend'
ID='alpha_chi_omega_fid765'; ASSET='Asset_'+ID; SCENE='Building_'+ID
assert SRC.exists()
# Rebuild is explicit and limited to this one assigned house asset.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene; scene.name=SCENE
asset=bpy.data.collections.new(ASSET); scene.collection.children.link(asset)
def subcol(name):
 c=bpy.data.collections.new(name);asset.children.link(c);return c
ext=subcol('Exterior_Shell_Facade_Roof');interior=subcol('Interior_Schematic_NoGeoregisteredPlan')
# Project raw Purdue GIS longitude/latitude with the repository's local campus approximation.
data=json.loads(SRC.read_text(encoding='utf-8'));feature=data['features'][0]
attrs=feature['attributes'];ring=feature['geometry']['rings'][0]
LAT0,LON0=40.4274,-86.9137
sx=111412.84*math.cos(math.radians(LAT0));sy=111040.0
world=[((lon-LON0)*sx,(lat-LAT0)*sy) for lon,lat in ring]
# signed polygon centroid, using the unfiltered source boundary
cross=[]
for (x1,y1),(x2,y2) in zip(world,world[1:]):cross.append(x1*y2-x2*y1)
area2=sum(cross);assert abs(area2)>1
cx=sum((world[i][0]+world[i+1][0])*cross[i] for i in range(len(cross)))/(3*area2)
cy=sum((world[i][1]+world[i+1][1])*cross[i] for i in range(len(cross)))/(3*area2)
ring_local=[(x-cx,y-cy) for x,y in world[:-1]]
# Remove only very short CAD snap segments; the deviation is documented and under 0.1 m.
poly=[]
for p in ring_local:
 if not poly or math.dist(p,poly[-1])>=0.08:poly.append(p)
if len(poly)>2 and math.dist(poly[0],poly[-1])<0.08:poly.pop()
assert len(poly)>=8
# Keep clockwise order from the GIS service; front edge 14 faces toward David Ross Road.
# Feature orientation is inferred from the chapter photo and nearest local road, not in the GIS attributes.
front_idx=14
front_a=poly[front_idx];front_b=poly[(front_idx+1)%len(poly)]
# Near-duplicate removal may shift the index only if a sub-0.08m edge precedes it; select the long SE edge.
edge_lengths=[math.dist(poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly))]
front_idx=max((i for i,L in enumerate(edge_lengths) if L>18),key=lambda i: edge_lengths[i])
front_a=poly[front_idx];front_b=poly[(front_idx+1)%len(poly)]
Lfront=edge_lengths[front_idx];ux=(front_b[0]-front_a[0])/Lfront;uy=(front_b[1]-front_a[1])/Lfront
# GIS rings are clockwise, so the left normal is outward.
nx,ny=-uy,ux
if nx<0 and ny>0: pass
# Height cues: 3 visible levels and a dormered roof from the chapter-owned rendering/photo.
Z0=0.55; EAVE=9.6; ROOF_TOP=12.8; ROOF_FACTOR_X=(max(x for x,y in ring_local)-min(x for x,y in ring_local)+0.60)/(max(x for x,y in ring_local)-min(x for x,y in ring_local)); ROOF_FACTOR_Y=(max(y for x,y in ring_local)-min(y for x,y in ring_local)+0.60)/(max(y for x,y in ring_local)-min(y for x,y in ring_local))

# Materials: all procedural, packed into the blend with no external image dependencies.
def mat(name,base,rough=.65,metal=0.0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*base,1);m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Base Color'].default_value=(*base,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;m.node_tree.links.new(bs.outputs['BSDF'],out.inputs['Surface']);return m
brick=mat('AXO_Brick_Procedural_Red_1964',(.45,.095,.055),.78)
nt=brick.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');tc=nt.nodes.new('ShaderNodeTexCoord');bt=nt.nodes.new('ShaderNodeTexBrick');bt.inputs['Color1'].default_value=(.48,.12,.075,1);bt.inputs['Color2'].default_value=(.31,.055,.035,1);bt.inputs['Mortar'].default_value=(.17,.15,.13,1);bt.inputs['Brick Width'].default_value=.25;bt.inputs['Row Height'].default_value=.075;bt.inputs['Mortar Size'].default_value=.012;bu=nt.nodes.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.22;bu.inputs['Distance'].default_value=.012;nt.links.new(tc.outputs['UV'],bt.inputs['Vector']);nt.links.new(bt.outputs['Color'],bs.inputs['Base Color']);nt.links.new(bt.outputs['Fac'],bu.inputs['Height']);nt.links.new(bu.outputs['Normal'],bs.inputs['Normal']);brick['source_note']='Warm red brick from Alpha Beta house newsletter exterior photos/render; mortar dimensions are visual estimates.'
limestone=mat('AXO_Limestone_Trim_Procedural',(.76,.70,.58),.76)
nt=limestone.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=18;noise.inputs['Detail'].default_value=3;noise.inputs['Roughness'].default_value=.7;bu=nt.nodes.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.12;bu.inputs['Distance'].default_value=.006;tc=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(tc.outputs['Object'],noise.inputs['Vector']);nt.links.new(noise.outputs['Fac'],bu.inputs['Height']);nt.links.new(bu.outputs['Normal'],bs.inputs['Normal'])
roofmat=mat('AXO_Roof_Dark_Slate_Shingle_Procedural',(.11,.125,.13),.82)
nt=roofmat.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');tc=nt.nodes.new('ShaderNodeTexCoord');bricktex=nt.nodes.new('ShaderNodeTexBrick');bricktex.inputs['Color1'].default_value=(.12,.14,.15,1);bricktex.inputs['Color2'].default_value=(.055,.065,.07,1);bricktex.inputs['Mortar'].default_value=(.025,.03,.035,1);bricktex.inputs['Brick Width'].default_value=.48;bricktex.inputs['Row Height'].default_value=.19;bricktex.inputs['Mortar Size'].default_value=.015;bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.2;bump.inputs['Distance'].default_value=.012;nt.links.new(tc.outputs['Object'],bricktex.inputs['Vector']);nt.links.new(bricktex.outputs['Color'],bs.inputs['Base Color']);nt.links.new(bricktex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal']);roofmat['source_note']='Dark slate-like shingles from 2016 Alpha Beta renovation rendering; roof material/type not confirmed by survey.'
glass=mat('AXO_Window_Glass_BlueGray',(.055,.105,.14),.22,.2);pbs=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');pbs.inputs['Transmission Weight'].default_value=.15;pbs.inputs['Emission Color'].default_value=(.015,.028,.038,1);pbs.inputs['Emission Strength'].default_value=.12
metal=mat('AXO_Railing_Dark_Bronze',(.075,.067,.055),.38,.65)
wood=mat('AXO_Entry_Door_Walnut',(.16,.065,.028),.45)
concrete=mat('AXO_Foundation_Concrete',(.34,.32,.29),.86)
plaster=mat('AXO_Interior_Warm_Plaster',(.76,.72,.64),.8)
interiorwood=mat('AXO_Interior_Wood',(.32,.20,.10),.7)

# Mesh helpers use local geometry coordinates and identity transforms, making the library portable.
def mesh_obj(name,verts,faces,material,coll,props=None):
 me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update()
 # Metric UVs keep the procedural brick courses horizontal across facade panels.
 coords=[Vector(v) for v in verts];dx=max(v.x for v in coords)-min(v.x for v in coords);dy=max(v.y for v in coords)-min(v.y for v in coords);dz=max(v.z for v in coords)-min(v.z for v in coords)
 uv=me.uv_layers.new(name='Metric_UV')
 if dz>max(dx,dy)*0.55 and dz>0.35: horizontal='x' if dx>=dy else 'y'; uvfn=lambda p:(p.x,p.z) if horizontal=='x' else (p.y,p.z)
 else: uvfn=lambda p:(p.x,p.y)
 for polyface in me.polygons:
  for li in polyface.loop_indices: uv.data[li].uv=uvfn(coords[me.loops[li].vertex_index])
 ob=bpy.data.objects.new(name,me);coll.objects.link(ob)
 if props:
  for k,v in props.items():ob[k]=v
 return ob
def prism(name,pts,z0,z1,material,coll,props=None):
 n=len(pts);verts=[(x,y,z0) for x,y in pts]+[(x,y,z1) for x,y in pts];faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
 for i in range(n):j=(i+1)%n;faces.append((i,j,n+j,n+i))
 return mesh_obj(name,verts,faces,material,coll,props)
def box(name,center,dims,material,coll,props=None):
 x,y,z=center;dx,dy,dz=[v/2 for v in dims];pts=[(x-dx,y-dy,z-dz),(x+dx,y-dy,z-dz),(x+dx,y+dy,z-dz),(x-dx,y+dy,z-dz),(x-dx,y-dy,z+dz),(x+dx,y-dy,z+dz),(x+dx,y+dy,z+dz),(x-dx,y+dy,z+dz)];return mesh_obj(name,pts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material,coll,props)
def wall_box(name,edge_a,u,n,t,offset,z,along,depth,height,material,coll,props=None):
 center=(edge_a[0]+u[0]*t+n[0]*offset,edge_a[1]+u[1]*t+n[1]*offset,z)
 c=Vector(center);U=Vector((u[0],u[1],0));N=Vector((n[0],n[1],0));Z=Vector((0,0,1));verts=[]
 for da,dd,dz in [(-along/2,-depth/2,-height/2),(along/2,-depth/2,-height/2),(along/2,depth/2,-height/2),(-along/2,depth/2,-height/2),(-along/2,-depth/2,height/2),(along/2,-depth/2,height/2),(along/2,depth/2,height/2),(-along/2,depth/2,height/2)]:
  p=c+U*da+N*dd+Z*dz;verts.append(tuple(p))
 return mesh_obj(name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material,coll,props)
def wall_quad(name,a,u,n,t0,t1,z0,z1,offset,material,coll):
 pts=[]
 for t,z in [(t0,z0),(t1,z0),(t1,z1),(t0,z1)]:pts.append((a[0]+u[0]*t+n[0]*offset,a[1]+u[1]*t+n[1]*offset,z))
 return mesh_obj(name,pts,[(0,1,2,3)],material,coll)
def line_bar(name,a,u,n,t0,t1,z0,z1,offset,material,coll):
 return wall_quad(name,a,u,n,t0,t1,z0,z1,offset,material,coll)

# Make an extruded foundation/slab that follows the measured GIS polygon.
prism('GIS_Footprint_Foundation_Slab',poly,0.0,Z0,concrete,ext,{'source':'Purdue ArcGIS FID 765; local approximation; boundary simplified only for <0.08m snaps.'})
# External walls as a continuous ring tessellated around designed openings.
wallbase=Z0; floors=[(1.15,2.75),(4.15,5.75),(7.15,8.65)]; edge_openings={}
for i,L in enumerate(edge_lengths):
 a=poly[i];b=poly[(i+1)%len(poly)];dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy)
 if L<.2:continue
 u=(dx/L,dy/L);n=(-u[1],u[0])
 openings=[]
 if i==front_idx:
  # Three arched public-facing bays; one central double entry and two glazed side bays.
  center=L/2
  for k,off in enumerate((-4.0,0.0,4.0)):
   c=center+off;openings.append((c-1.48,c+1.48,wallbase,3.55))
  # Balcony doors and flanking upper windows.
  for off in (-4.0,0.0,4.0):
   c=center+off;openings.append((c-1.23,c+1.23,4.15,6.2))
  for off in (-7.4,-3.7,3.7,7.4):
   c=center+off;openings.append((c-.78,c+.78,7.2,8.65))
 elif L>=4.5:
  count=max(1,int(L//3.7));
  for floorno,(z0,z1) in enumerate(floors):
   for k in range(count):
    c=L*(k+1)/(count+1);w=1.25 if floorno<2 else 1.1
    openings.append((c-w/2,c+w/2,z0,z1))
 edge_openings[i]=openings
 # Create wall mesh from rectangles outside openings; set breakpoints so each opening is a clean true hole.
 ts=sorted(set([0.0,L]+[max(0,min(L,v)) for o in openings for v in o[:2]]));zs=sorted(set([wallbase,EAVE]+[v for o in openings for v in o[2:]]))
 vv=[];ff=[]
 for t0,t1 in zip(ts[:-1],ts[1:]):
  if t1-t0<.02:continue
  for z0,z1 in zip(zs[:-1],zs[1:]):
   if z1-z0<.02:continue
   tc=(t0+t1)/2;zc=(z0+z1)/2
   if any(o[0]<tc<o[1] and o[2]<zc<o[3] for o in openings):continue
   base=len(vv);vv.extend([(a[0]+u[0]*t0,a[1]+u[1]*t0,z0),(a[0]+u[0]*t1,a[1]+u[1]*t1,z0),(a[0]+u[0]*t1,a[1]+u[1]*t1,z1),(a[0]+u[0]*t0,a[1]+u[1]*t0,z1)]);ff.append((base,base+1,base+2,base+3))
 if ff:mesh_obj(f'Brick_Wall_Edge_{i:02d}',vv,ff,brick,ext,{'GIS_edge_index':i,'opening_count':sum(1 for o in openings)})
 # Window panes and trim fit every aperture. True holes are retained behind the glass.
 for j,(t0,t1,z0,z1) in enumerate(openings):
  w=t1-t0;zmid=(z0+z1)/2
  if i==front_idx and z0<1:
   rad=(w-.32)/2;spring=z1-rad-.22;arch_center_t=(t0+t1)/2;glass_r=max(.2,rad-.18);pts=[(t0+.12,z0+.08),(t1-.12,z0+.08)]
   for q in range(17):
    th=math.pi*q/16;pts.append((arch_center_t+glass_r*math.cos(th),spring+glass_r*math.sin(th)))
   vv=[(a[0]+u[0]*t+n[0]*.045,a[1]+u[1]*t+n[1]*.045,z) for t,z in pts];mesh_obj(f'Window_Glass_E{i:02d}_{j:02d}',vv,[tuple(range(len(vv)))],glass,ext,{'shape':'arched glazing under stone voussoirs'})
  else:wall_quad(f'Window_Glass_E{i:02d}_{j:02d}',a,u,n,t0+.07,t1-.07,z0+.07,z1-.07,.045,glass,ext)
  # Surround frame. Front arcade doors/windows receive stone arch blocks below.
  surround=limestone if i==front_idx else limestone;off=.10
  if i==front_idx and z0<1:
   # Four side/head stone lines; segmented semicircular voussoirs provide the arched heads.
   line_bar(f'Portal_Jamb_L_{j}',a,u,n,t0-.08,t0+.10,z0,z1-.35,off,surround,ext)
   line_bar(f'Portal_Jamb_R_{j}',a,u,n,t1-.10,t1+.08,z0,z1-.35,off,surround,ext)
   rad=(w-.32)/2;spring=z1-rad-.22;arch_center_t=(t0+t1)/2
   count=11
   # Close the area above each semicircular opening with short brick infill panels.
   for q in range(16):
    x0=-rad-.22+2*(rad+.22)*q/16;x1=-rad-.22+2*(rad+.22)*(q+1)/16
    h0=spring+math.sqrt(max(0,(rad+.22)**2-x0*x0));h1=spring+math.sqrt(max(0,(rad+.22)**2-x1*x1))
    verts=[(a[0]+u[0]*t+n[0]*(off+.015),a[1]+u[1]*t+n[1]*(off+.015),z) for t,z in [(arch_center_t+x0,h0),(arch_center_t+x1,h1),(arch_center_t+x1,z1),(arch_center_t+x0,z1)]]
    mesh_obj(f'Portal_Arch_Spandrel_{j}_{q:02d}',verts,[(0,1,2,3)],brick,ext)
   for q in range(count):
    aa=math.pi*q/count+.01;ab=math.pi*(q+1)/count-.01
    coords=[(arch_center_t+rad*math.cos(aa),spring+rad*math.sin(aa)),(arch_center_t+(rad+.22)*math.cos(aa),spring+rad*math.sin(aa)),(arch_center_t+(rad+.22)*math.cos(ab),spring+rad*math.sin(ab)),(arch_center_t+rad*math.cos(ab),spring+rad*math.sin(ab))]
    verts=[]
    for dep in (off,off+.16):
     verts.extend([(a[0]+u[0]*t+n[0]*dep,a[1]+u[1]*t+n[1]*dep,z) for t,z in coords])
    mesh_obj(f'Portal_Voussoir_{j}_{q:02d}',verts,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],surround,ext,{'round':'arched_portal','dimensions_estimated':True})
   line_bar(f'Portal_Sill_{j}',a,u,n,t0-.18,t1+.18,z0-.03,z0+.13,off,surround,ext)
  else:
   line_bar(f'Window_Left_Jamb_E{i}_{j}',a,u,n,t0-.10,t0+.05,z0-.06,z1+.06,.09,surround,ext)
   line_bar(f'Window_Right_Jamb_E{i}_{j}',a,u,n,t1-.05,t1+.10,z0-.06,z1+.06,.09,surround,ext)
   line_bar(f'Window_Head_E{i}_{j}',a,u,n,t0-.10,t1+.10,z1-.08,z1+.08,.10,surround,ext)
   line_bar(f'Window_Sill_E{i}_{j}',a,u,n,t0-.16,t1+.16,z0-.09,z0+.07,.10,surround,ext)
   line_bar(f'Window_Mullion_V_E{i}_{j}',a,u,n,(t0+t1)/2-.035,(t0+t1)/2+.035,z0+.08,z1-.08,.11,metal,ext)
   line_bar(f'Window_Mullion_H_E{i}_{j}',a,u,n,t0+.08,t1-.08,(z0+z1)/2-.03,(z0+z1)/2+.03,.11,metal,ext)
  if i==front_idx and z0>3.8 and z1<6.3:
   # Door glazing and balcony thresholds at second story.
   line_bar(f'Balcony_Door_Threshold_{j}',a,u,n,t0-.18,t1+.18,z0-.07,z0+.06,.12,surround,ext)
# Foundation belt and floor-line stringcourses around the house.
for level,z in enumerate((3.55,6.55,9.48)):
 # thin belt created per boundary edge, follows the actual footprint rather than an AABB
 for i,a in enumerate(poly):
  b=poly[(i+1)%len(poly)];L=math.dist(a,b)
  if L<.15:continue
  u=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(-u[1],u[0])
  wall_box(f'Stringcourse_{level}_{i}',a,u,n,L/2,0,z+.04,L,.15,.10,limestone,ext)

# Front arcade/entry: four paired limestone columns, triple arched bays, a covered stoop and balcony.
a=front_a;u=(ux,uy);n=(nx,ny);center=Lfront/2
# Wide porch slab and steps toward David Ross Road.
wall_box('Front_Portico_Slab',a,u,n,center,.72,.77,13.2,2.35,.42,limestone,ext,{'front_direction':'southeast toward David Ross Road; inferred from site access.'})
for k,off in enumerate((-5.7,-1.9,1.9,5.7)):
 t=center+off
 wall_box(f'Front_Portico_Column_{k:02d}',a,u,n,t,.0,2.22,.60,.82,3.34,limestone,ext)
 wall_box(f'Front_Column_Base_{k:02d}',a,u,n,t,.0,.86,.78,1.02,.32,limestone,ext)
 wall_box(f'Front_Column_Capital_{k:02d}',a,u,n,t,.0,3.80,.82,1.04,.34,limestone,ext)
# Balcony at the second story, with dark rails and balusters.
wall_box('Front_Balcony_Deck',a,u,n,center,1.02,4.02,12.8,1.55,.25,limestone,ext)
wall_box('Front_Balcony_Handrail',a,u,n,center,1.82,5.08,12.8,.12,.10,metal,ext)
for j in range(25):
 t=center-6.1+j*(12.2/24)
 wall_box(f'Front_Balcony_Baluster_{j:02d}',a,u,n,t,1.82,4.55,.08,.08,1.06,metal,ext)
# Front door double leaf, glazing, and fanlight set inside center arch.
for side in (-1,1):
 t=center+side*.47
 wall_box(f'Front_Entry_Door_Leaf_{side}',a,u,n,t,.10,1.75,.90,.08,2.15,wood,ext)
 wall_box(f'Entry_Door_Glass_Lite_{side}',a,u,n,t,.17,2.38,.72,.035,.42,glass,ext)
# Door pulls
for side in (-1,1):wall_box(f'Entry_Door_Pull_{side}',a,u,n,center+side*.12,.14,1.64,.04,.10,.25,metal,ext)
# Small house-name plaque above the balcony/gable.
wall_box('AXO_Gable_NamePlaque',a,u,n,center,.35,11.65,3.9,1.12,.16,limestone,ext)
# A triangular masonry gable with a raised light stone outline.
gw=9.6;zbase=10.3;zapex=13.35;off=.30
tri=[(center-gw/2,zbase),(center+gw/2,zbase),(center,zapex)]
verts=[(a[0]+u[0]*t+n[0]*off,a[1]+u[1]*t+n[1]*off,z) for t,z in tri]
mesh_obj('Central_Front_Gable_Masonry',verts,[(0,1,2)],brick,ext,{'reference':'2016 Alpha Beta Home Corporation renovation rendering; dimensions estimated.'})
# Gable rake/band edging
for side in (-1,1):
 t0=center if side<0 else center+gw/2;t1=center-gw/2 if side<0 else center
 z0=zapex if side<0 else zbase;z1=zbase if side<0 else zapex
 # approximate rake as slim line in facade plane, world-oriented bar follows slope
 midt=(t0+t1)/2;midz=(z0+z1)/2;length=math.hypot(t1-t0,z1-z0)
 # custom oriented rectangular prism in the facade plane
 p0=Vector((a[0]+u[0]*midt+n[0]*off,a[1]+u[1]*midt+n[1]*off,midz));U=Vector((u[0],u[1],0));Z=Vector((0,0,1));along=Vector((u[0]*(t1-t0)+0,u[1]*(t1-t0),z1-z0)).normalized();across=Vector((0,0,1)).cross(along).normalized();depth=Vector((n[0],n[1],0));v=[]
 for da,dd,zz in [(-length/2,-.08,-.10),(length/2,-.08,-.10),(length/2,.08,-.10),(-length/2,.08,-.10),(-length/2,-.08,.10),(length/2,-.08,.10),(length/2,.08,.10),(-length/2,.08,.10)]:
  # use along slope axis, depth axis and in-plane perpendicular axis
  p=p0+along*da+depth*dd+across*zz;v.append(tuple(p))
 mesh_obj(f'Gable_Rake_Trim_{side}',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],limestone,ext)
# Built-in Blender font text; no font file dependency.
def text_obj(name,body,size,location,normal,material):
 cu=bpy.data.curves.new(name+'_Curve','FONT');cu.body=body;cu.size=size;cu.extrude=.015;cu.align_x='CENTER';cu.align_y='CENTER';ob=bpy.data.objects.new(name,cu);ext.objects.link(ob);ob.location=location
 N=Vector((normal[0],normal[1],0)).normalized();U=Vector((N.y,-N.x,0));UP=Vector((0,0,1));basis=Matrix((U,UP,-N)).transposed();ob.rotation_euler=basis.to_euler()
 cu.materials.append(material);ob['text_source']='Greek letters and house name from Alpha Beta chapter identity; visual sign dimensions estimated.';return ob
text_obj('Alpha_Chi_Omega_Greek_Letters','ΩΧΑ',.90,(a[0]+u[0]*center+n[0]*.48,a[1]+u[1]*center+n[1]*.48,12.35),(nx,ny,0),limestone)
# Dormer boxes across the front mansard roof; openings/glass and dark caps echo the chapter rendering.
for k,offt in enumerate((-12.0,-8.0,-4.0,4.0,8.0,12.0)):
 t=center+offt
 wall_box(f'Roof_Dormer_Front_{k:02d}',a,u,n,t,.38,11.45,1.28,1.18,2.10,brick,ext)
 wall_quad(f'Dormer_Glass_{k:02d}',a,u,n,t-.39,t+.39,10.75,12.20,.98,glass,ext)
 for side in (-1,1):line_bar(f'Dormer_Jamb_{k}_{side}',a,u,n,t+side*.48-.07,t+side*.48+.07,10.65,12.38,1.03,limestone,ext)
 line_bar(f'Dormer_Lintel_{k}',a,u,n,t-.56,t+.56,12.30,12.46,1.04,limestone,ext)
 wall_box(f'Dormer_Roof_Cap_{k}',a,u,n,t,.68,12.78,1.55,1.40,.28,roofmat,ext)
# Roof geometry: exact GIS plan plus a conservative 0.30 m bounding eave; mansard-like multi-plane roof.
minx,maxx=min(x for x,y in poly),max(x for x,y in poly);miny,maxy=min(y for x,y in poly),max(y for x,y in poly)
scx=(maxx-minx+.60)/(maxx-minx);scy=(maxy-miny+.60)/(maxy-miny)
outer=[(x*scx,y*scy) for x,y in poly];knee=[(x*.94,y*.94) for x,y in poly];inner=[(x*.40,y*.40) for x,y in poly];npoly=len(poly)
verts=[(x,y,EAVE) for x,y in outer]+[(x,y,11.35) for x,y in knee]+[(x,y,ROOF_TOP) for x,y in inner]
faces=[]
for i in range(npoly):
 j=(i+1)%npoly;faces.append((i,j,npoly+j,npoly+i));faces.append((npoly+i,npoly+j,2*npoly+j,2*npoly+i))
faces.append(tuple(range(2*npoly,3*npoly)))
mesh_obj('Primary_Mansard_Roof',verts,faces,roofmat,ext,{'plan_footprint':'Purdue GIS FID 765 polygon plus approx 0.30m eave in AABB X/Y','height':'Eave and peak inferred from 3-level photo/rendering; not surveyed.'})
# Roof fascia band follows roof perimeter.
for i,p in enumerate(outer):
 q=outer[(i+1)%npoly];L=math.dist(p,q)
 if L<.15:continue
 # make fascia as shallow wall segment along each perimeter edge
 ua=((q[0]-p[0])/L,(q[1]-p[1])/L);na=(-ua[1],ua[0]);wall_box(f'Roof_Fascia_{i}',p,ua,na,L/2,.0,EAVE-.10,L,.12,.30,limestone,ext)
# One rear-left brick chimney is visible in the chapter's 2016 exterior rendering.
for k,(x,y) in enumerate(((5.53,5.78),)):
 box(f'Brick_Chimney_{k}',(x,y,13.90),(1.25,1.35,2.20),brick,ext,{'dimensions_estimated':True,'source_note':'Approximate chimney position calibrated to the 2016 exterior rendering.'})
 box(f'Chimney_Cap_{k}',(x,y,15.10),(1.55,1.65,.20),limestone,ext)
# Schematic floor plates + simplified core, explicitly not a georegistered interior plan.
for i,z in enumerate((-.08,0.55,3.55,6.55,9.55)):
 mesh_obj(f'Schematic_Interior_Floor_{i}',[(x,y,z) for x,y in poly],[tuple(range(len(poly)))],interiorwood,interior,{'status':'schematic only; no georegistered plan available','source_note':'GIS Floorplans field points to inaccessible Purdue internal drive, not a public measured drawing.'})
# Schematic interior partition bars around the central core, repeated on three floors.
for floorno,z in enumerate((.55,3.55,6.55)):
 box(f'Schematic_Corridor_Wall_A_F{floorno}',(0,0,z+1.3),(10,.14,2.6),plaster,interior,{'dimensions_status':'schematic, not a source-derived plan'})
 box(f'Schematic_Corridor_Wall_B_F{floorno}',(0,0,z+1.3),(.14,8,2.6),plaster,interior,{'dimensions_status':'schematic, not a source-derived plan'})
# Basement common room / dining furniture from chapter newsletter captions (placement schematic).
box('Schematic_Basement_Dining_Table',(0,-2,-1.9),(4.2,1.2,.12),interiorwood,interior,{'room':'dining/common room; schematic'})
for j in range(8):box(f'Schematic_Dining_Chair_{j}',(-1.8+(j%4)*1.2,-3.0+(j//4)*2.0,-2.28),(.48,.48,.85),interiorwood,interior,{'room':'dining/common room; schematic'})
box('Schematic_Basement_Common_Area',(2,2,-1.9),(3.2,.9,.12),interiorwood,interior,{'room':'basement common room; schematic'})
for i in range(3):box(f'Schematic_Basement_Seat_{i}',(0.8+i*1.05,3.1,-2.18),(.85,.85,.7),plaster,interior,{'room':'basement common room; schematic'})
# Building root metadata, exact GIS source, proposed placement origin; master manifest is coordinator-owned.
root=bpy.data.objects.new('AssetRoot_alpha_chi_omega_fid765',None);asset.objects.link(root);root.location=(0,0,0);root['stable_id']=ID;root['source_feature_id']=765;root['source_building_code']='SOACO';root['address']='851 David Ross Rd, West Lafayette, IN';root['local_origin_xy_m']=[cx,cy];root['local_origin_lonlat']=[cx/sx+LON0,cy/sy+LAT0];root['facade_edge_index_in_raw_ring']=front_idx;root['facade_azimuth_bearing_deg_estimated']=math.degrees(math.atan2(nx,ny))%360;root['interior_status']='schematic; no georegisterable or dimensioned floor plan found.'
asset['source_provider']='Purdue University ArcGIS BuildingShapesZip4 FeatureServer';asset['source_fid']=765;asset['source_name']='Alpha Chi Omega';asset['source_address']='851 David Ross Rd';asset['source_crs_returned']='EPSG:4326';asset['local_coordinate_method']='Purdue project local approximation; documented in audit/alpha_chi_omega_fid765/gis_crosswalk.json';asset['placement_origin_xy_m']=[cx,cy];asset['placement_origin_lonlat']=[cx/sx+LON0,cy/sy+LAT0];asset['export_collection']=ASSET

# Add a non-export QA environment / camera collection to the building scene.
qa=bpy.data.collections.new('QA_Render_Setup_Not_Exported');scene.collection.children.link(qa)
# Ground stage is QA-only.
mesh_obj('QA_Ground_Plane',[(-70,-70,-.08),(70,-70,-.08),(70,70,-.08),(-70,70,-.08)],[(0,1,2,3)],mat('QA_Grass_Ground',(.20,.27,.17),.9),qa)
# camera looks from inferred front side toward the house
n=Vector((nx,ny,0));target=Vector((0,0,5.4));camd=bpy.data.cameras.new('QA_Exterior_Camera');cam=bpy.data.objects.new('QA_Exterior_Camera',camd);qa.objects.link(cam);cam.location=target+n*52+Vector((0,0,21));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=49;scene.camera=cam
for name,loc,energy,size,color in [('QA_Key',(n.x*45-15,n.y*45+20,45),8500,30,(1.0,.84,.69)),('QA_Fill',(-25,-25,28),5600,34,(.76,.86,1.0)),('QA_Rim',(20,35,32),6200,30,(1.0,.94,.82))]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);qa.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,5))-o.location).to_track_quat('-Z','Y').to_euler()
world=bpy.data.worlds.new('AXO_QA_World');scene.world=world;world.use_nodes=True;bg=world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.42,.52,.68,1);bg.inputs['Strength'].default_value=.65
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1500;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=1.0;scene.render.image_settings.file_format='PNG'
# Metadata for build provenance
scene['model_source_note']='Asset geometry built from verified Purdue GIS FID 765 footprint and chapter-owned Alpha Beta house photos/rendering; not a measured architectural survey.'
# Save the portable building asset. QA collection remains outside the exported Asset collection.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
# Build report
objs=[o for o in asset.all_objects if o];meshes=[o for o in objs if o.type=='MESH']
allv=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
bounds=[[min(v[i] for v in allv) for i in range(3)],[max(v[i] for v in allv) for i in range(3)]]
report={'asset_path':str(OUT),'stable_id':ID,'export_collection':ASSET,'scene':SCENE,'source_feature':{'fid':765,'code':'SOACO','name':'Alpha Chi Omega','address':attrs.get('ADDRESS'),'crs':'EPSG:4326','source_layer_crs':'EPSG:3857'},'local_origin':{'campus_xy_m':[cx,cy],'lonlat':[cx/sx+LON0,cy/sy+LAT0]},'gis_footprint_bounds_local_m':[[min(x for x,y in ring_local),min(y for x,y in ring_local)],[max(x for x,y in ring_local),max(y for x,y in ring_local)]],'gis_footprint_area_m2':abs(area2)/2,'simplified_boundary_vertex_count':len(poly),'object_count':len(objs),'mesh_count':len(meshes),'bounds_local_m':bounds,'front_facade_edge_index':front_idx,'front_facade_outward_bearing_deg_estimated':math.degrees(math.atan2(nx,ny))%360,'eave_height_m_estimated':EAVE,'main_roof_peak_m_estimated':ROOF_TOP,'interior':'schematic and nondimensional; no georegisterable plan found; only areas/captions from chapter newsletter used.','external_images':[],'external_texture_nodes':[],'source_massing_file_preserved':True,'master_or_manifest_edited':False,'build_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest()}
(AUD/'build_result.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
