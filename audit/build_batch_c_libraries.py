"""Build the nine assigned batch-C Purdue building libraries, source-only.

Run with Blender 5.2 background from the project root. Each invocation reads one
official GIS snapshot and writes only that building's library/evidence/preview.
The detailed silhouette follows the official footprint; facade and roof details
are explicitly documented as photo-informed or estimated.
"""
import bpy, bmesh, json, math, os, sys, datetime
from mathutils import Vector, geometry

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
CONFIGS={
 'lambert': dict(id='massing_lambert_ward_l_fieldhouse_and_gymnasium_1656862', slug='lambert_fieldhouse', name='Ward L. Lambert Fieldhouse and Gymnasium', abbr='LAMB', fid=261, levels=5, height=21.03, kind='fieldhouse', title='Lambert Fieldhouse', refs=['https://purduesports.com/facilities','https://www.google.com/maps/search/?api=1&query=Lambert+Fieldhouse+Purdue+University']),
 'life_science_plant_soils': dict(id='massing_life_science_plant_and_soils_laboratory_5963acd', slug='life_science_plant_and_soils_laboratory', name='Life Science Plant and Soils Laboratory', abbr='LSPS', fid=917, levels=4, height=10.97, kind='lab', title='Life Science Plant and Soils Laboratory', refs=['https://ag.purdue.edu/department/btny/extension/plantandpestdiagnosticlab.html','https://ag.purdue.edu/department/btny/ppdl/contact-us/parking-and-map.html','https://ag.purdue.edu/department/btny/lilly-greenhouse/index.html','https://www.google.com/maps/search/?api=1&query=Life+Science+Plant+and+Soils+Laboratory+Purdue']),
 'msee': dict(id='massing_materials_science_and_electrical_engineering_msee_003a4e2', slug='materials_and_electrical_engineering', name='Materials And Electrical Engineering', abbr='MSEE', fid=646, levels=4, height=10.97, kind='atrium', title='Materials and Electrical Engineering', refs=['https://engineering.purdue.edu/ECN/AboutUs/History/MSEE','https://engineering.purdue.edu/Imprints/fall-2018/materials-and-electrical-engineering-atrium-gets-a-major-upgrade','https://www.google.com/maps/search/?api=1&query=Materials+and+Electrical+Engineering+Purdue']),
 'morgan_center': dict(id='massing_morgan_center_for_entrepreneurship_mrgn_9ba681c', slug='burton_morgan_center', name='Burton D. Morgan Center For Entrepreneurship', abbr='MRGN', fid=80, levels=2, height=8.5, kind='morgan', title='Burton D. Morgan Center for Entrepreneurship', refs=['https://www.purdue.edu/uns/html3month/2006/060131.Blewett.bdmaward.html','https://schooldesigns.com/Projects/purdue-university-the-burton-d-morgan-center-for-entrepreneurship/','https://events.purdue.edu/burton_d_morgan_ctr_for_entrepreneurshp','https://www.google.com/maps/search/?api=1&query=Burton+D+Morgan+Center+Purdue']),
 'boilermaker_aquatic': dict(id='massing_morgan_j_burke_boilermaker_aquatic_center_2e6697f', slug='morgan_j_burke_boilermaker_aquatic_center', name='Morgan J. Burke Boilermaker Aquatic Center', abbr='AQUA', fid=896, levels=2, height=12.2, kind='aquatic', title='Morgan J. Burke Boilermaker Aquatic Center', refs=['https://purduesports.com/facilities/morgan-j.-burke-aquatic-center/12','https://www.purdue.edu/recwell/sports-and-programs/aquatics/index.php','https://www.google.com/maps/search/?api=1&query=Morgan+J+Burke+Boilermaker+Aquatic+Center']),
 'national_soil_erosion': dict(id='massing_national_soil_erosion_laboratory_soil_0a1864c', slug='national_soil_erosion_laboratory', name='National Soil Erosion Laboratory', abbr='SOIL', fid=242, levels=3, height=7.32, kind='soil', title='National Soil Erosion Research Laboratory', refs=['https://topsoil.nserl.purdue.edu/AgroEnviron2016/','https://topsoil.nserl.purdue.edu/AgroEnviron2016/index_files/image007.jpg','https://topsoil.nserl.purdue.edu/~flanagan/usle-landmark/booklet.htm','https://www.google.com/maps/search/?api=1&query=USDA+ARS+National+Soil+Erosion+Research+Laboratory+275+South+Russell+Street+Purdue']),
 'nacc': dict(id='massing_native_american_educational_and_cultural_center_nacc_faa0f59', slug='native_american_educational_and_cultural_center', name='Native American Educational and Cultural Center', abbr='NACC', fid=927, levels=1, height=5.49, kind='nacc', title='Native American Educational and Cultural Center', refs=['https://www.purdue.edu/operations/emergency-preparedness/nacc/','https://purdue.edu/naecc/','https://www.google.com/maps/search/?api=1&query=Native+American+Educational+and+Cultural+Center+903+5th+Street+Purdue']),
 'northwest_chiller': dict(id='massing_northwest_chiller_plant_nwcp_2b32fa6', slug='northwest_chiller_plant', name='Northwest Chiller Plant', abbr='NWCP', fid=74, levels=2, height=10.97, kind='chiller', title='Northwest Chiller Plant', refs=['https://www.purdue.edu/physicalfacilities/','https://www.google.com/maps/search/?api=1&query=Northwest+Chiller+Plant+Purdue']),
 'physics': dict(id='massing_physics_building_phys_3bf42f3', slug='physics_building', name='Physics Building', abbr='PHYS', fid=273, levels=8, height=25.60, kind='physics', title='Physics Building', refs=['https://www.purdue.edu/science/','https://www.google.com/maps/search/?api=1&query=Physics+Building+Purdue+525+Northwestern+Avenue'])
}
key=sys.argv[-1]
cfg=CONFIGS[key]
feature_path=os.path.join(ROOT,'audit',f"batchC_{key}_official_footprint.json")
with open(feature_path,encoding='utf-8-sig') as f: doc=json.load(f)
ftr=doc['features'][0]; attrs=ftr['attributes']; rings=ftr['geometry']['rings']
ORIG_LAT,ORIG_LON=40.4274,-86.9137
LON_M=111412.84*math.cos(math.radians(ORIG_LAT)); LAT_M=111040.
xy=[((p[0]-ORIG_LON)*LON_M,(p[1]-ORIG_LAT)*LAT_M) for p in rings[0][:-1]]
cx=(min(p[0] for p in xy)+max(p[0] for p in xy))/2; cy=(min(p[1] for p in xy)+max(p[1] for p in xy))/2
build_bbox_origin=[cx,cy]; local_origin_shift=[0.0,0.0,0.0]
if key=='nacc':
 # Match the established NACC manifest marker: the original detailed model
 # used the projected polygon area centroid. The current builder first makes
 # geometry around the GIS bbox center, so shift that completed asset by B-C.
 area2c=cxsum=cysum=0.0
 for (x,y),(u,v) in zip(xy,xy[1:]+xy[:1]):
  cross=x*v-u*y; area2c+=cross; cxsum+=(x+u)*cross; cysum+=(y+v)*cross
 centroid_x=cxsum/(3*area2c); centroid_y=cysum/(3*area2c)
 local_origin_shift=[cx-centroid_x,cy-centroid_y,0.0]
pts=[(x-cx,y-cy) for x,y in xy]; n=len(pts)
area2=sum(pts[i][0]*pts[(i+1)%n][1]-pts[(i+1)%n][0]*pts[i][1] for i in range(n))
if area2<0: pts.reverse(); n=len(pts)
xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys); w=maxx-minx; d=maxy-miny
h=cfg['height']; floors=cfg['levels']
# Lambert is a one-volume fieldhouse: GIS extrusion is used for the roof apex,
# while the low brick perimeter wall and clerestory form the gym's actual shell.
roof_peak=h
if cfg['kind']=='fieldhouse': h=11.2; floors=2
elif cfg['kind']=='aquatic': h=9.2; floors=1
elif cfg['kind']=='nacc': h=3.8; floors=1
floor_h=h/max(floors,1)

# A clean library contract: exactly one stable asset collection, with local origin centered on GIS bbox.
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
 if c.name!='Collection': bpy.data.collections.remove(c)
scene=bpy.context.scene
for c in list(scene.collection.children): scene.collection.children.unlink(c)
asset=bpy.data.collections.new('Asset_'+cfg['slug']); scene.collection.children.link(asset)
cols={}
for key2 in ('Structure','Facade','Roof','Interior','Site'):
 c=bpy.data.collections.new(cfg['abbr']+'_'+key2); asset.children.link(c); cols[key2]=c
rig=bpy.data.collections.new('Preview_Rig'); scene.collection.children.link(rig)

def mat(name,color,rough=.7,metal=0,scale=5,bump=.04):
 m=bpy.data.materials.new(cfg['abbr']+' | '+name); m.diffuse_color=(*color,1); m.use_nodes=True
 nt=m.node_tree; bs=nt.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
 # A restrained emissive lift keeps large horizontal roof surfaces readable in
 # the small dark preview rig; it does not replace their physically lit shader.
 if 'Emission Color' in bs.inputs:
  bs.inputs['Emission Color'].default_value=(*color,1); bs.inputs['Emission Strength'].default_value=.24 if ('membrane' in name or 'shingle' in name) else .035
 tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=scale; tex.inputs['Detail'].default_value=3
 geo=nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(geo.outputs['Generated'],tex.inputs['Vector'])
 ramp=nt.nodes.new('ShaderNodeValToRGB'); lo=(*[v*.83 for v in color],1); hi=(*[min(1,v*1.16) for v in color],1); ramp.color_ramp.elements[0].color=lo; ramp.color_ramp.elements[1].color=hi; nt.links.new(tex.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
 b=nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value=bump; b.inputs['Distance'].default_value=.025; nt.links.new(tex.outputs['Fac'],b.inputs['Height']); nt.links.new(b.outputs['Normal'],bs.inputs['Normal'])
 return m
brick=mat('mottled Purdue red-brown brick',(.40,.15,.09),.84,0,24,.08)
stone=mat('warm gray limestone / precast',(.59,.56,.48),.72,0,9,.06)
concrete=mat('cast concrete',(.40,.42,.41),.86,0,11,.08)
metal=mat('charcoal anodized metal',(.10,.13,.15),.38,.55,16,.035)
roofmat=mat('weathered membrane / standing seam',(.52,.54,.56),.80,.01,22,.025)
glass=mat('blue gray reflective glazing',(.045,.15,.21),.2,.25,5,.012)
glassblock=mat('translucent cast glass block',(.46,.59,.62),.42,.05,8,.015)
greenhouse_glass=mat('translucent greenhouse glazing',(.31,.48,.48),.17,.18,3,.01)
dark=mat('deep shadow / reveals',(.035,.047,.05),.78,0,4,.02)
wood=mat('warm interior wood',(.37,.20,.10),.66,0,8,.035)
siding=mat('aged warm-white horizontal clapboard',(.68,.62,.50),.88,0,36,.075)
shingle=mat('weathered charcoal asphalt shingles',(.19,.20,.20),.92,0,65,.05)
roof_course=mat('asphalt shingle course edges',(.12,.13,.14),.92,0,28,.04)
water=mat('pool water',(.015,.70,.78),.12,.12,3,.01)
green=mat('plant foliage',(.075,.20,.095),.8,0,8,.06)
colors={'fieldhouse':(brick,concrete),'lab':(brick,stone),'atrium':(brick,stone),'morgan':(brick,stone),'aquatic':(concrete,brick),'soil':(brick,concrete),'nacc':(siding,stone),'chiller':(concrete,metal),'physics':(brick,stone)}
basewall,trim=colors[cfg['kind']]

def translucent_material(name,color,opacity=.52):
 m=bpy.data.materials.new(cfg['abbr']+' | '+name); m.use_nodes=True
 nt=m.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); bs=nt.nodes.new('ShaderNodeBsdfPrincipled'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=.2; bs.inputs['Metallic'].default_value=.12
 noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=7; tex=nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(tex.outputs['Generated'],noise.inputs['Vector'])
 bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.08; bump.inputs['Distance'].default_value=.018; nt.links.new(noise.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
 tr=nt.nodes.new('ShaderNodeBsdfTransparent'); mix=nt.nodes.new('ShaderNodeMixShader'); mix.inputs[0].default_value=1-opacity; nt.links.new(tr.outputs['BSDF'],mix.inputs[1]); nt.links.new(bs.outputs['BSDF'],mix.inputs[2]); nt.links.new(mix.outputs[0],out.inputs['Surface']); return m
pool_glass=translucent_material('natatorium clear-span glazing',(.30,.56,.62),.012) if cfg['kind']=='aquatic' else glass
fieldhouse_glass=translucent_material('glass-block facade with interior light transmission',(.46,.59,.62),.24) if cfg['kind']=='fieldhouse' else glassblock
if cfg['kind']=='lab':
 greenhouse_glass=translucent_material('greenhouse clear glazing',(.40,.62,.58),.28)
facade_glass=translucent_material('schematic clear facade glazing',(.26,.43,.50),.26) if cfg['kind'] in ('morgan','soil','nacc','lab') else glass

def mesh_obj(name,verts,faces,material,col,mat_indices=None):
 me=bpy.data.meshes.new(name+' | mesh'); me.from_pydata(verts,[],faces); me.materials.append(material)
 ob=bpy.data.objects.new(name,me); col.objects.link(ob)
 if me.polygons:
  bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
 if mat_indices:
  for mi in mat_indices: me.polygons[mi].material_index=1
 return ob
def cube(name,loc,scale,material,col,rot=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); ob=bpy.context.object; ob.name=name; ob.dimensions=scale; ob.rotation_euler[2]=rot; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(ob.users_collection): c.objects.unlink(ob)
 col.objects.link(ob); ob.data.materials.append(material); return ob
def cyl(name,loc,radius,depth,material,col,verts=16):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=radius,depth=depth,location=loc); ob=bpy.context.object; ob.name=name
 for c in list(ob.users_collection): c.objects.unlink(ob)
 col.objects.link(ob); ob.data.materials.append(material); return ob
def mesh_poly(name,poly,z0,z1,material,col):
 verts=[(x,y,z0) for x,y in poly]+[(x,y,z1) for x,y in poly]
 faces=[]
 for i in range(len(poly)): faces.append((i,(i+1)%len(poly),(i+1)%len(poly)+len(poly),i+len(poly)))
 # concave footprint top/bottom triangulated with Blender tessellator
 uv=[Vector((x,y,0)) for x,y in poly]
 tris=geometry.tessellate_polygon([uv])
 for t in tris:
  idx=list(t)
  faces.append(tuple(idx)); faces.append(tuple(i+len(poly) for i in reversed(idx)))
 return mesh_obj(name,verts,faces,material,col)

def add_gable_roof(label,eave,ridge,material,span_fraction=.94,long_fraction=.94,seams=8):
 axis_x=w>=d; span=min(w,d)*span_fraction; long=max(w,d)*long_fraction; half=span/2
 def point(s,u,z): return (s,u,z) if axis_x else (u,s,z)
 v=[]; f=[]
 for side in (-1,1):
  base=len(v); e_u=side*half
  v.extend([point(-long/2,e_u,eave),point(long/2,e_u,eave),point(long/2,0,ridge),point(-long/2,0,ridge)])
  f.append((base,base+1,base+2,base+3))
 roof=mesh_obj(label+' | pitched roof planes',v,f,material,cols['Roof'])
 # Raised standing seams help the clear-span pool roof; the house roof uses
 # shingle material without industrial metal ribs.
 if cfg['kind']!='nacc':
  seam_v=[]; seam_f=[]
  for side in (-1,1):
   for j in range(seams+1):
    s=-long/2+long*j/seams; base=len(seam_v)
    seam_v.extend([point(s-.025,side*half,eave+.03),point(s+.025,side*half,eave+.03),point(s+.025,0,ridge+.03),point(s-.025,0,ridge+.03)])
    seam_f.append((base,base+1,base+2,base+3))
  mesh_obj(label+' | standing seam roof ribs',seam_v,seam_f,metal,cols['Roof'])
 # Gable end lights: glass triangles in the high clear-span wall above eaves.
 for s in (-long/2,long/2):
  gv=[point(s,-half,eave),point(s,half,eave),point(s,0,ridge)]
  mesh_obj(label+' | gable end infill',gv,[(0,1,2)],pool_glass if cfg['kind']=='aquatic' else basewall,cols['Facade'])
 return roof

# For the six detailed target libraries, build actual facade openings instead
# of placing glazing over a solid GIS extrusion. This lets exported interior
# objects read through the windows. The wall surfaces follow each official
# footprint edge; opening dimensions remain schematic and follow facade bays.
OPEN_SHELL_KINDS={'fieldhouse','lab','morgan','soil','nacc'}
def mesh_walls_with_glazing_openings():
 wall_verts=[]; wall_faces=[]
 for i,p in enumerate(pts):
  q=pts[(i+1)%n]; dx=q[0]-p[0]; dy=q[1]-p[1]; length=math.hypot(dx,dy)
  bays=max(1,int(length/(6.0 if cfg['kind']=='fieldhouse' else 3.8)))
  ww=min(3.2 if cfg['kind']=='fieldhouse' else 1.52,length/bays*.72)
  openings=[]
  for floor in range(floors):
   if length<2.4: continue
   if cfg['kind']=='fieldhouse' and floor>0 and floor_h<4: continue
   z0=floor*floor_h+(0.32 if floor==0 else .24)
   wh=max(.75,min(2.8 if cfg['kind']=='fieldhouse' else 1.8,floor_h*.68))
   for j in range(bays):
    glazing=True
    if cfg['kind']=='fieldhouse': glazing=(j%2==0)
    if cfg['kind']=='soil': glazing=(j%2==0)
    if cfg['kind']=='nacc': glazing=(j%2==0)
    if cfg['kind']=='lab': glazing=(i%3==0)
    if not glazing: continue
    center=(j+.5)*length/bays
    # Slightly oversize the structural opening behind the separate glazed pane.
    half=ww*.5+.07
    opening=(max(0.0,center-half),min(length,center+half),max(0,z0-.06),min(h,z0+wh+.06))
    if opening[1]>opening[0] and opening[3]>opening[2]: openings.append(opening)
  # A small 2-D cell grid creates a true hole at each glazed opening.
  us=sorted({0.0,length,*[u for op in openings for u in op[:2]]})
  zs=sorted({0.0,h,*[z for op in openings for z in op[2:]]})
  nx=-dy/length; ny=dx/length
  edge_verts=[]; edge_faces=[]
  for ua,ub in zip(us,us[1:]):
   if ub-ua<1e-5: continue
   for za,zb in zip(zs,zs[1:]):
    if zb-za<1e-5: continue
    um=(ua+ub)*.5; zm=(za+zb)*.5
    if any(a<um<b and c<zm<d_ for a,b,c,d_ in openings): continue
    base=len(edge_verts)
    edge_verts.extend([(p[0]+dx*ua/length,p[1]+dy*ua/length,za),
                       (p[0]+dx*ub/length,p[1]+dy*ub/length,za),
                       (p[0]+dx*ub/length,p[1]+dy*ub/length,zb),
                       (p[0]+dx*ua/length,p[1]+dy*ua/length,zb)])
    edge_faces.append((base,base+1,base+2,base+3))
  offset=len(wall_verts); wall_verts.extend(edge_verts)
  wall_faces.extend(tuple(offset+v for v in face) for face in edge_faces)
 mesh_obj(cfg['title']+' | GIS perimeter wall panels with real glazing openings',wall_verts,wall_faces,basewall,cols['Structure'])

# Structural shell: official footprint, with the aquatics building treated as
# a glazed clear-span volume so its competition pool reads through the walls.
shellmat=pool_glass if cfg['kind']=='aquatic' else basewall
if cfg['kind']=='aquatic':
 mesh_poly(cfg['title']+' | official GIS footprint interior plinth',pts,0,.24,concrete,cols['Structure'])
elif cfg['kind'] in OPEN_SHELL_KINDS:
 mesh_poly(cfg['title']+' | official GIS footprint ground floor',pts,.02,.14,concrete,cols['Interior'])
 mesh_walls_with_glazing_openings()
else:
 mesh_poly(cfg['title']+' | official GIS footprint structural shell',pts,0,h,shellmat,cols['Structure'])
for floor in range(1,floors):
 z=floor*floor_h
 # thin projecting datum bands are deliberately restrained and follow every footprint edge
 for i,p in enumerate(pts):
  q=pts[(i+1)%n]; dx=q[0]-p[0]; dy=q[1]-p[1]; length=math.hypot(dx,dy)
  if length>1.7: cube(cfg['abbr']+f' | level {floor} horizontal datum',((p[0]+q[0])/2,(p[1]+q[1])/2,z),(length,.11,.10),trim,cols['Facade'],math.atan2(dy,dx))
 # interior plate follows GIS plan; simple triangulated surface and colored floor finishes.
 mesh_poly(cfg['abbr']+f' | level {floor} interior floor plate',pts,z-.08,z-.015,concrete,cols['Interior'])

# Facade module positions along each true GIS perimeter segment, not an axis-aligned substitute.
window_count=0
for i,p in enumerate(pts):
 q=pts[(i+1)%n]; dx=q[0]-p[0]; dy=q[1]-p[1]; length=math.hypot(dx,dy)
 if length<2.4: continue
 ang=math.atan2(dy,dx); nx=-dy/length; ny=dx/length
 # Avoid busy fenestration on very short angled facets; window bay spacing tracks elevation.
 bays=max(1,int(length/(6.0 if cfg['kind'] in ('fieldhouse','aquatic','chiller') else 3.8)))
 for floor in range(floors):
  if cfg['kind'] in ('fieldhouse','aquatic','chiller') and floor>0 and floor_h<4: continue
  z0=floor*floor_h + (0.32 if floor==0 else .24); wh=(h-.55 if cfg['kind']=='aquatic' else max(.75,min(2.8 if cfg['kind']=='fieldhouse' else 1.8,floor_h*.68))); ww=(min(6.0,length/bays*.92) if cfg['kind']=='aquatic' else min(3.2 if cfg['kind']=='fieldhouse' else 1.52,length/bays*.72))
  for j in range(bays):
   # Facade glazing sits just proud of the shell face, keeping the window frame
   # legible and leaving room for explicitly schematic room cues behind it.
   t=(j+.5)/bays; x=p[0]+dx*t-nx*.055; y=p[1]+dy*t-ny*.055
   # Choose feature glazing ratios by type and publicly documented architectural character.
   glazing=cfg['kind'] in ('atrium','morgan','aquatic','physics') or (cfg['kind']=='lab' and (i%3==0))
   if cfg['kind']=='chiller': glazing=(floor==0 and j%5==0)
   if cfg['kind']=='fieldhouse': glazing=(j%2==0)
   if cfg['kind']=='soil': glazing=(j%2==0)
   if cfg['kind']=='nacc': glazing=(j%2==0)
   winmat=fieldhouse_glass if cfg['kind']=='fieldhouse' else (pool_glass if cfg['kind']=='aquatic' else (facade_glass if cfg['kind'] in ('morgan','soil','nacc','lab') else glass))
   cube(cfg['abbr']+f' | facade bay {i}-{floor}-{j} '+('glazing' if glazing else 'recessed panel'),(x,y,z0+wh/2),(ww,.075,wh),winmat if glazing else trim,cols['Facade'],ang); window_count+=int(glazing)
   if glazing:
    # visible vertical mullion and sill/frame accents
    cube(cfg['abbr']+' | vertical glazing mullion',(x,y,z0+wh/2),(.055,.12,wh+.08),metal,cols['Facade'],ang)
    cube(cfg['abbr']+' | glazing sill',(x,y,z0),(ww+.12,.16,.09),trim,cols['Facade'],ang)

# Roof diaphragm plus a visible, building-specific roofline system.
if cfg['kind'] not in ('fieldhouse','aquatic','nacc'):
 mesh_poly(cfg['abbr']+' | structural flat roof',pts,h-.22,h,roofmat,cols['Roof'])
 for i,p in enumerate(pts):
  q=pts[(i+1)%n]; dx=q[0]-p[0]; dy=q[1]-p[1]; length=math.hypot(dx,dy)
  if length>1.5: cube(cfg['abbr']+' | roof parapet coping',((p[0]+q[0])/2,(p[1]+q[1])/2,h+.16),(length,.23,.32),trim,cols['Roof'],math.atan2(dy,dx))

# Recognizable signature features informed by building use and source photographs/descriptions.
if cfg['kind']=='fieldhouse':
 # High-volume arched gym roof represented by transverse steel ribs and a continuous segmented barrel canopy.
 axis_x=w>=d; span=min(w,d)*.95; long=max(w,d)*.91; r=span/2; run_count=max(8,int(long/6)); cross_steps=24
 rise=max(4.1,min(roof_peak-h,r*.145)); roof_verts=[]; roof_faces=[]
 # One continuous, correctly curved canopy. Transverse end ribs and longitudinal
 # standing seams are separate batched mesh objects, avoiding thousands of primitives.
 for k in range(run_count+1):
  s=-long/2+long*k/run_count
  for step in range(cross_steps+1):
   a=math.pi*step/cross_steps; u=-r*math.cos(a); z=h+rise*math.sin(a)
   roof_verts.append((s,u,z) if axis_x else (u,s,z))
 for k in range(run_count):
  for step in range(cross_steps):
   a=k*(cross_steps+1)+step; roof_faces.append((a,a+cross_steps+1,a+cross_steps+2,a+1))
 mesh_obj('LAMB | continuous arched fieldhouse roof canopy',roof_verts,roof_faces,roofmat,cols['Roof'])
 rib_verts=[]; rib_faces=[]
 for k in range(0,run_count+1,2):
  base=len(rib_verts); s=-long/2+long*k/run_count; r2=r+.08
  for step in range(cross_steps+1):
   a=math.pi*step/cross_steps; u=-r2*math.cos(a); z=h+rise*math.sin(a)
   rib_verts.extend([(s,u,z-.07) for s in ( -long/2+long*k/run_count-.11, -long/2+long*k/run_count+.11)] if axis_x else [(u,s,z-.07) for s in (-long/2+long*k/run_count-.11,-long/2+long*k/run_count+.11)])
  # Use a simple tube-like arch strip; recalc normals makes both sides render reliably.
  for step in range(cross_steps):
   a=base+step*2; rib_faces.append((a,a+1,a+3,a+2))
 mesh_obj('LAMB | repeated steel roof arch rib',rib_verts,rib_faces,metal,cols['Roof'])
 # Translucent monitor/clerestory strips run along the springing line.
 # Bright high clerestory band below a reduced roof rise leaves the masonry
 # facade exposed and makes the roof edge/profile easier to read.
 for side in (-1,1): cube(cfg['abbr']+' | translucent clerestory band',(0,side*(d/2-.15),h*.86),(long*.80,.20,1.25),fieldhouse_glass,cols['Facade']) if axis_x else cube(cfg['abbr']+' | translucent clerestory band',(side*(w/2-.15),0,h*.86),(.20,long*.80,1.25),fieldhouse_glass,cols['Facade'])
 # Historic street facade: tall glass-block bays between pronounced concrete piers.
 for i,p in enumerate(pts):
  q=pts[(i+1)%n]; dx=q[0]-p[0]; dy=q[1]-p[1]; length=math.hypot(dx,dy)
  if length<12: continue
  ang=math.atan2(dy,dx); nx=-dy/length; ny=dx/length
  for j in range(1,max(2,int(length/7))):
   t=j/max(2,int(length/7)); x=p[0]+dx*t+nx*.20; y=p[1]+dy*t+ny*.20
   cube('LAMB | pale concrete facade pier',(x,y,h*.50),(.42,.52,h*.94),concrete,cols['Facade'],ang)
 # Interior court cue, deliberately schematic: red track ring and small bleacher rows.
 track=mat('indoor track surface',(.43,.12,.075),.78,0,18,.025)
 floor=mat('fieldhouse sport floor',(.31,.28,.22),.84,0,7,.02)
 mesh_poly('LAMB | schematic interior arena floor',[(x*.78,y*.78) for x,y in pts],.08,.16,floor,cols['Interior'])
 rx=w*.31; ry=d*.27; verts=[]; faces=[]; segs=96
 for radx,rady in ((rx,ry),(rx*.86,ry*.84)):
  verts += [(radx*math.cos(2*math.pi*j/segs),rady*math.sin(2*math.pi*j/segs),.20) for j in range(segs)]
 faces=[(j,(j+1)%segs,(j+1)%segs+segs,j+segs) for j in range(segs)]
 mesh_obj('LAMB | schematic indoor oval running track',verts,faces,track,cols['Interior'])
 for row in range(4):
  cube('LAMB | schematic interior bleacher tier',(0,d*.34+row*.88,.50+row*.36),(w*.45,.78,.25),metal,cols['Interior'])
 # Six visible lane boundaries and a start/finish bar clarify the oval track
 # through the north clerestory and the true glass-block perimeter openings.
 for lane in range(1,7):
  rx_lane=rx*(.86+lane*.14/6); ry_lane=ry*(.84+lane*.16/6)
  line_v=[]; line_f=[]
  for j in range(segs):
   a=2*math.pi*j/segs; b=2*math.pi*(j+1)/segs
   base=len(line_v)
   line_v.extend([(rx_lane*math.cos(a),ry_lane*math.sin(a),.214),(rx_lane*math.cos(b),ry_lane*math.sin(b),.214),
                  ((rx_lane-.055)*math.cos(b),(ry_lane-.055)*math.sin(b),.214),((rx_lane-.055)*math.cos(a),(ry_lane-.055)*math.sin(a),.214)])
   line_f.append((base,base+1,base+2,base+3))
  mesh_obj('LAMB | track lane boundary '+str(lane),line_v,line_f,stone,cols['Interior'])
 cube('LAMB | track finish line',(0,-ry*.86,.22),(rx*1.72,.12,.025),stone,cols['Interior'])
elif cfg['kind']=='lab':
 # The adjoining Life Science Ranges are represented as a recognizable attached
 # greenhouse wing, with glazed panels, metal frames, growing benches and vents.
 # The official map confirms nearby greenhouse facilities but does not verify
 # an 8.2 m attachment to this GIS footprint. Keep the glazed lab bay inside
 # the recorded building envelope and describe it as an interpretive facade.
 gx=0; gw=min(w*.38,24); gd=min(8.2,d*.30); gy=miny+gd/2; gh=6.0
 cube('LSPS | greenhouse service wing floor',(gx,gy,.16),(gw,gd,.32),concrete,cols['Interior'])
 for y in (gy-gd/2+.05,gy+gd/2): cube('LSPS | greenhouse long glass wall',(gx,y,gh/2),(gw,.10,gh),greenhouse_glass,cols['Facade'])
 for x in (gx-gw/2,gx+gw/2): cube('LSPS | greenhouse end glazing',(x,gy,gh/2),(.10,gd,gh),greenhouse_glass,cols['Facade'])
 # Pitch glass canopy with visible rafters and perimeter mullions.
 roof_v=[(gx-gw/2,gy-gd/2,gh),(gx+gw/2,gy-gd/2,gh),(gx,gy-gd/2,gh+1.5),(gx-gw/2,gy+gd/2,gh),(gx+gw/2,gy+gd/2,gh),(gx,gy+gd/2,gh+1.5)]
 mesh_obj('LSPS | pitched greenhouse glass roof',roof_v,[(0,1,2),(3,5,4)],greenhouse_glass,cols['Roof'])
 for j in range(1,9): cube('LSPS | greenhouse vertical mullion',(gx-gw/2+gw*j/9,gy-gd/2+.09,gh/2),(.10,.18,gh),metal,cols['Facade'])
 for z in (1.8,3.6,5.4): cube('LSPS | greenhouse front horizontal transom',(gx,gy-gd/2+.09,z),(gw,.18,.10),metal,cols['Facade'])
 for j in range(1,6): cube('LSPS | greenhouse side mullion',(gx-gw/2-.13,gy-gd/2+gd*j/6,gh/2),(.18,.10,gh),metal,cols['Facade'])
 for x in (-gw*.30,0,gw*.30):
  cube('LSPS | greenhouse growing bench',(gx+x,gy,.88),(2.8,gd*.60,.12),wood,cols['Interior'])
  for j in range(6):
   cyl('LSPS | schematic potted test plant pot',(gx+x-1.1+j*.44,gy,.98),.12,.30,stone,cols['Interior'],10)
   cyl('LSPS | schematic crop canopy',(gx+x-1.1+j*.44,gy,1.28),.22,.38,green,cols['Interior'],12)
 # Repeated greenhouse rafters and suspended grow-light bars make the bay
 # read as working plant space. These are schematic contents, not surveyed fitout.
 for j in range(1,9):
  x=gx-gw/2+gw*j/9
  beam=cube('LSPS | greenhouse pitched roof rafter',(x,gy,gh+.58),(.09,gd*.98,1.18),metal,cols['Roof'])
  beam.rotation_euler[0]=math.atan2(1.5,gw/2) if j<=4 else -math.atan2(1.5,gw/2)
 for z in (2.2,3.8):
  cube('LSPS | schematic suspended horticulture grow-light',(gx,gy,z),(gw*.72,.16,.08),trim,cols['Interior'])
 for k in range(4): cube('LSPS | rooftop mechanical curb',(minx+w*(.45+.09*k),maxy-d*.15,h+.45),(1.8,1.4,.9),metal,cols['Roof'])
 cube('LSPS | schematic laboratory service/loading door',(minx+w*.70,miny+.08,2.1),(3.0,.16,4.0),metal,cols['Facade'])
 for z in [0.38+j*.34 for j in range(10)]: cube('LSPS | schematic loading door horizontal slat',(minx+w*.70,miny+.025,z),(2.75,.05,.035),trim,cols['Facade'])
 cube('LSPS | schematic service canopy within GIS footprint',(minx+w*.70,miny+.775,4.4),(4.4,1.55,.22),trim,cols['Facade'])
 cube('LSPS | schematic service identification panel',(minx+w*.70,miny+.07,5.05),(5.0,.14,.58),dark,cols['Facade'])
elif cfg['kind']=='atrium':
 # GIS is the compact MSEE polygon; a two-story glass atrium is a documented architectural hallmark.
 atr_w=min(w*.31,10); atr_d=min(d*.30,10); cube('MSEE | two-story Brown Atrium glazed volume',(maxx-atr_w/2,miny+atr_d/2,h*.40),(atr_w,atr_d,h*.78),glass,cols['Facade'])
 for z in (h*.28,h*.52): cube('MSEE | atrium floor slab glimpse',(maxx-atr_w/2,miny+atr_d/2,z),(atr_w*.95,atr_d*.92,.14),wood,cols['Interior'])
 # Atrium mullion grid
 for j in range(1,6): cube('MSEE | atrium curtain wall mullion',(maxx-atr_w/2-atr_w/2+j*atr_w/6,miny+.04,h*.4),(.10,.16,h*.76),metal,cols['Facade'])
elif cfg['kind']=='morgan':
 # Purdue's award image identifies a two-story brick, metal and glass building;
 # the full-width deep overhang, centered glazed entry and name band are legible.
 cube('Morgan | two-story transparent entry bay',(0,miny-.16,h*.36),(w*.40,.18,h*.68),facade_glass,cols['Facade'])
 for j in range(1,9): cube('Morgan | entry curtain-wall mullion',(minx+w*j/10,miny-.30,h*.36),(.10,.20,h*.67),metal,cols['Facade'])
 cube('Morgan | prominent entrance canopy',(0,miny-1.8,4.0),(min(w*.78,23),3.8,.72),trim,cols['Facade'])
 cube('Morgan | canopy dark underside',(0,miny-1.82,3.62),(min(w*.74,22.5),3.55,.10),dark,cols['Facade'])
 for x in (-min(w*.72,22)*.42,min(w*.72,22)*.42):
  cube('Morgan | canopy support column',(x,miny-3.2,1.9),(.24,.24,3.6),metal,cols['Facade'])
 for x in (-1.1,1.1): cube('Morgan | double entry door leaf',(x,miny-.33,1.55),(1.0,.10,3.0),metal,cols['Facade'])
 cube('Morgan | entry door glass inset',(0,miny-.39,1.65),(1.05,.06,2.55),glass,cols['Facade'])
 cube('Morgan | brick name panel',(0,miny-.18,h*.82),(w*.64,.20,.96),brick,cols['Facade'])
 # A two-level glazed lobby with an open stair and an 80-seat lecture-room
 # cue is documented at Purdue; seat layout and internal circulation are schematic.
 cube('Morgan | lobby floor slab',(0,miny+5.7,.18),(w*.54,11.4,.22),concrete,cols['Interior'])
 cube('Morgan | upper lobby bridge',(0,miny+6.7,4.28),(w*.38,5.2,.18),wood,cols['Interior'])
 cube('Morgan | stair lower landing',(-w*.18,miny+2.8,.38),(3.6,2.4,.22),trim,cols['Interior'])
 for step in range(11):
  cube('Morgan | lobby stair tread',(-w*.18,miny+3.1+step*.38,.50+step*.30),(2.7,.42,.14),wood,cols['Interior'])
 # Seminar seating and presentation wall, explicitly schematic furniture.
 cube('Morgan | lecture room presentation wall',(w*.20,miny+13.2,2.0),(w*.28,.20,3.5),dark,cols['Interior'])
 for row in range(5):
  for seat in range(8):
   sx=w*.04+seat*1.02; sy=miny+8.2+row*1.0
   cube('Morgan | schematic lecture chair seat',(sx,sy,.62),( .72,.68,.12),trim,cols['Interior'])
   cube('Morgan | schematic lecture chair back',(sx,sy+.28,1.02),(.72,.10,.78),wood,cols['Interior'])
 # Bright metal coping and the name-bearing brick band visible in Purdue's exterior photograph.
 cube('Morgan | silver metal roof edge',(0,0,h+.13),(w+.35,d+.35,.22),trim,cols['Roof'])
elif cfg['kind']=='aquatic':
 # Clear-span natatorium roof, glazed high-bay envelope and eight-lane pool.
 add_gable_roof('AQUA | clear-span natatorium',h,roof_peak,roofmat,.96,.97,12)
 axis_x=w>=d; span=min(w,d)*.96; long=max(w,d)*.96; half=span/2
 for i in range(0,7):
  s=-long/2+long*i/6
  # Simple visible steel roof trusses in the tall pool hall.
  points=[(s,-half,h),(s,0,roof_peak),(s,half,h)] if axis_x else [(-half,s,h),(0,s,roof_peak),(half,s,h)]
  for a,b in ((points[0],points[1]),(points[1],points[2]),(points[0],points[2])):
   va=Vector(a); vb=Vector(b); delta=vb-va
   bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.10,depth=delta.length,location=(va+vb)/2)
   beam=bpy.context.object; beam.name='AQUA | schematic clear-span roof truss'; beam.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
   for c in list(beam.users_collection): c.objects.unlink(beam)
   cols['Interior'].objects.link(beam); beam.data.materials.append(metal)
 # Concrete piers and a solid waterline plinth anchor the curtainwall.
 for i,p in enumerate(pts):
  q=pts[(i+1)%n]; dx=q[0]-p[0]; dy=q[1]-p[1]; length=math.hypot(dx,dy)
  if length<12: continue
  ang=math.atan2(dy,dx); nx=-dy/length; ny=dx/length
  for j in range(0,max(2,int(length/8))+1):
   t=j/max(2,int(length/8)); x=p[0]+dx*t+nx*.18; y=p[1]+dy*t+ny*.18
   cube('AQUA | exterior concrete clear-span pier',(x,y,h*.52),(.34,.45,h*.90),concrete,cols['Facade'],ang)
 pool_w=min(w*.62,25); pool_d=min(d*.76,50)
 # Continuous deck slab around the basin. 50 m pool length and eight lanes are
 # official facility facts; lane width/deck width and all fittings are schematic.
 mesh_poly('Aquatic | continuous pool deck',pts,.25,.34,concrete,cols['Interior'])
 cube('Aquatic | interior pool basin',(0,0,1.1),(pool_w,pool_d,1.9),concrete,cols['Interior'])
 cube('Aquatic | water surface',(0,0,2.08),(pool_w-.35,pool_d-.35,.06),water,cols['Interior'])
 lane_pitch=(pool_w-.7)/8
 for boundary in range(9):
  lx=-pool_w/2+.35+boundary*lane_pitch
  cube('Aquatic | eight-lane pool boundary marking',(lx,0,2.125),(.055,pool_d-.65,.025),stone,cols['Interior'])
  if boundary<8:
   # Dotted lane ropes remain visibly distinct from the pool floor markings.
   bead_count=36
   for bead in range(bead_count):
    yy=-pool_d*.46+(pool_d*.92)*(bead+.5)/bead_count
    cyl('Aquatic | schematic floating lane-rope bead',(lx,yy,2.20),.075,.055,trim if bead%6==0 else glassblock,cols['Interior'],8)
 for end_y in (-pool_d*.47,pool_d*.47):
  for lane in range(8):
   lx=-pool_w/2+.35+(lane+.5)*lane_pitch
   cube('Aquatic | schematic lane starting block',(lx,end_y,2.45),(.65,.85,.62),trim,cols['Interior'])
 cube('AQUA | Purdue gold sign fascia',(0,pool_d*.50,roof_peak-1.40),(min(w*.68,37),.34,1.55),brick,cols['Interior'])
 cube('AQUA | Purdue gold sign field',(0,pool_d*.50-.23,roof_peak-1.40),(min(w*.64,34),.16,1.30),trim,cols['Interior'])
 aqua_text=bpy.data.curves.new('AQUA | sign lettering','FONT'); aqua_text.body='PURDUE'; aqua_text.size=1.12; aqua_text.align_x='CENTER'; aqua_text.align_y='CENTER'; aqua_text.extrude=.012
 aqua_label=bpy.data.objects.new('AQUA | Purdue pool-hall sign lettering',aqua_text); cols['Interior'].objects.link(aqua_label); aqua_label.location=(0,pool_d*.50-.33,roof_peak-1.40); aqua_label.rotation_euler=(math.pi/2,0,0); aqua_text.materials.append(dark)
 # Raised bleacher tiers sit on one long wall; diving platforms are at the far end.
 for row in range(7):
  x=pool_w*.72+row*.52
  cube('AQUA | schematic spectator bleacher tier',(x,0,.62+row*.34),(3.0,pool_d*.58,.26),concrete,cols['Interior'])
  cube('AQUA | schematic spectator seat accent',(x-.20,0,.78+row*.34),(2.6,pool_d*.58,.10),trim,cols['Interior'])
 for level in range(5): cube('AQUA | schematic diving tower platform',(-pool_w*.65,-pool_d*.42+level*.65,3.0+level*1.35),(3.0,2.1,.20),trim,cols['Interior'])
 for x in (-pool_w*.62,pool_w*.62):
  cube('AQUA | end pool deck drainage channel',(x,0,.38),(.16,pool_d*.84,.08),dark,cols['Interior'])
elif cfg['kind']=='soil':
 # Low brick research lab: ribbon glazing, receiving/loading door, dated roof plant and identity plaque.
 cube('Soil Lab | research ribbon window',(0,miny-.12,h*.53),(w*.67,.18,1.15),glass,cols['Facade'])
 cube('Soil Lab | loading / equipment door',(minx+w*.54,miny-.08,1.5),(1.9,.15,3),metal,cols['Facade'])
 for k in range(4):
  x=minx+5+k*5.2; cube('Soil Lab | rooftop exhaust plenum',(x,maxy-d*.17,h+.65),(2.5,2.2,1.25),concrete,cols['Roof'])
  cube('Soil Lab | rooftop equipment cap',(x,maxy-d*.17,h+1.31),(2.0,1.7,.12),metal,cols['Roof'])
 # Roof service access, vent stacks, and large louvered utility bays.
 for k in range(3):
  x=minx+w*(.22+.27*k)
  cube('Soil Lab | roof fan curb',(x,maxy-d*.42,h+.22),(2.4,2.0,.42),metal,cols['Roof'])
  cyl('Soil Lab | roof exhaust fan',(x,maxy-d*.42,h+.66),.72,.38,concrete,cols['Roof'],24)
  cyl('Soil Lab | exhaust fan hub',(x,maxy-d*.42,h+.87),.18,.12,metal,cols['Roof'],16)
 # One official exterior photograph verifies the identity plaque and brick
 # research-lab character. The loading-side door/shutters remain schematic.
 for x in (-w*.26,0,w*.26):
  cube('Soil Lab | schematic service-side shutter',(x,miny-.16,2.0),(2.4,.12,2.7),metal,cols['Facade'])
  for z in [1.0+j*.18 for j in range(12)]: cube('Soil Lab | schematic service shutter louver',(x,miny-.24,z),(2.22,.045,.035),trim,cols['Facade'])
 cube('Soil Lab | USDA laboratory sign panel',(0,miny-.18,h*.86),(min(w*.78,25),.16,.88),dark,cols['Facade'])
 # Schematic interior soil-testing stations: sieve stand, sample carts and work tables.
 for row in range(2):
  yy=miny+4.2+row*5.0
  cube('Soil Lab | interior sample-prep worktable',(0,yy,.94),(w*.44,1.35,.18),wood,cols['Interior'])
  for j in range(6):
   xx=-w*.19+j*w*.076
   cube('Soil Lab | labeled sample tray',(xx,yy,1.24),(1.0,.72,.42),stone,cols['Interior'])
 for x in (-w*.3,w*.3):
  cube('Soil Lab | interior equipment rack',(x,miny+12.5,1.8),(2.8,.75,3.3),metal,cols['Interior'])
  for shelf in range(4): cube('Soil Lab | equipment rack shelf',(x,miny+12.5,.65+shelf*.78),(2.7,.88,.12),trim,cols['Interior'])
elif cfg['kind']=='nacc':
 # Former single-family house: one-storey clapboard bungalow massing, pitched shingle roof,
 # front porch, sash windows and a small attached garage/service door.
 add_gable_roof('NACC | small-house gable roof',h,roof_peak,shingle,.98,.98,10)
 # Shingle courses follow the two sloped roof planes, keeping the modest house roof
 # visibly asphalt-shingled rather than industrial standing-seam metal.
 axis_x=w>=d; roof_span=min(w,d)*.98; roof_long=max(w,d)*.98; half=roof_span/2; eave=h; ridge=roof_peak
 roof_line_v=[]; roof_line_f=[]; course_gap=.42
 for side in (-1,1):
  for row in range(1,max(3,int(half/course_gap))):
   frac=row/max(3,int(half/course_gap)); u=side*half*(1-frac); z=eave+(ridge-eave)*frac+.035; base=len(roof_line_v)
   if axis_x: roof_line_v.extend([(-roof_long/2,u,z),(roof_long/2,u,z),(roof_long/2,u,z+.035),(-roof_long/2,u,z+.035)])
   else: roof_line_v.extend([(u,-roof_long/2,z),(u,roof_long/2,z),(u,roof_long/2,z+.035),(u,-roof_long/2,z+.035)])
   roof_line_f.append((base,base+1,base+2,base+3))
 mesh_obj('NACC | schematic asphalt shingle courses',roof_line_v,roof_line_f,roof_course,cols['Roof'])
 # Real horizontal lap boards are modeled as narrow continuous seams around the GIS shell.
 board_v=[]; board_f=[]
 for i,p in enumerate(pts):
  q=pts[(i+1)%n]; dx=q[0]-p[0]; dy=q[1]-p[1]; length=math.hypot(dx,dy)
  if length<1.2: continue
  nx=-dy/length; ny=dx/length; z=.22
  while z<h-.08:
   a=len(board_v); zline=z
   board_v.extend([(p[0]+nx*.065,p[1]+ny*.065,zline),(q[0]+nx*.065,q[1]+ny*.065,zline),(q[0]+nx*.065,q[1]+ny*.065,zline+.045),(p[0]+nx*.065,p[1]+ny*.065,zline+.045)])
   board_f.append((a,a+1,a+2,a+3)); z+=.25
 mesh_obj('NACC | aged horizontal clapboard lap courses',board_v,board_f,siding,cols['Facade'])
 # Porch aligns with the street-facing south footprint notch; posts and balustrade make it read as a house.
 porch_x=minx+w*.54; porch_y=miny-1.0; porch_w=min(w*.55,9.0)
 cube('NACC | front porch floor',(porch_x,porch_y,.30),(porch_w,2.5,.28),stone,cols['Site'])
 cube('NACC | covered front porch roof',(porch_x,porch_y,3.38),(porch_w+1.0,3.0,.22),siding,cols['Facade'])
 for dx in (-porch_w*.45,porch_w*.45): cube('NACC | porch column',(porch_x+dx,porch_y-.7,1.85),(.18,.18,2.9),stone,cols['Facade'])
 cube('NACC | centered community front door',(porch_x,miny-.11,1.55),(1.05,.12,2.65),wood,cols['Facade'])
 cube('NACC | storm door glass',(porch_x,miny-.19,1.72),(.72,.05,1.55),glass,cols['Facade'])
 # Attached garage/service bay follows the small rectangular footprint projection on the west side.
 gx=minx+2.1
 cube('NACC | attached garage door',(gx,miny-.10,1.42),(2.6,.14,2.55),metal,cols['Facade'])
 for z in [0.40+j*.23 for j in range(9)]: cube('NACC | garage door panel seam',(gx,miny-.19,z),(2.42,.04,.035),stone,cols['Facade'])
 cube('NACC | garage eave fascia',(gx,miny-.25,2.80),(3.2,.35,.18),trim,cols['Facade'])
 # Schematic interior gathering inset; no specific room layout is claimed.
 cyl('NACC | schematic circular gathering floor inset',(0,0,.06),min(w,d)*.12,.08,wood,cols['Interior'],48)
elif cfg['kind']=='chiller':
 # Industrial chiller plant: solid utility envelope, louvers, exhaust stacks and pipework.
 for i in range(max(3,int(w/5))): cube('NWCP | intake louver bank',(minx+(i+.5)*w/max(3,int(w/5)),miny-.12,h*.43),(1.1,.16,h*.46),metal,cols['Facade'])
 for k in range(3):
  x=minx+w*(.25+.25*k); cube('NWCP | rooftop chiller unit',(x,0,h+.8),(w*.16,d*.34,1.5),concrete,cols['Roof'])
  for j in range(4): cyl('NWCP | chiller fan housing',(x-w*.045+j*w*.03,0,h+1.58),.28,.08,metal,cols['Roof'],24)
 for x in (minx+w*.32,minx+w*.68):
  cyl('NWCP | cooling exhaust stack',(x,maxy-1,h+2.1),.38,4.2,metal,cols['Roof'],24)
elif cfg['kind']=='physics':
 # Mid-century science tower: repeated vertical brick piers, bands, observatory/service rooftop elements.
 for j in range(1,9):
  x=minx+w*j/9; cube('Physics | vertical facade pier',(x,miny-.09,h*.50),(.34,.20,h*.96),trim,cols['Facade'])
 for z in (h*.25,h*.50,h*.75): cube('Physics | continuous horizontal spandrel',(0,miny-.12,z),(w,.18,.24),concrete,cols['Facade'])
 cube('Physics | roof penthouse',(0,0,h+.8),(w*.38,d*.34,1.6),concrete,cols['Roof'])
 # Interior two-storey lobby cue at entrance
 cube('Physics | lobby floor glimpse',(0,miny+d*.14,1.5),(w*.35,d*.22,.12),wood,cols['Interior'])

# Restrained, explicitly schematic first-room furnishings make interiors readable
# through an entrance/window without implying a measured floor plan.
if cfg['kind']=='lab':
 for x in (-w*.19,0,w*.19):
  cube('LSPS | schematic visible lab bench',(x,miny+.48,1.10),(4.4,.82,.14),wood,cols['Interior'])
  for j in range(3): cyl('LSPS | schematic lab vessel',(x-1.1+j*1.1,miny+.48,1.62),.17,.82,greenhouse_glass,cols['Interior'],16)
 # No unverified apron/extension is added outside the official polygon.
elif cfg['kind']=='fieldhouse':
 cube('LAMB | schematic illuminated entry vestibule',(0,miny-.13,1.75),(9.2,.08,2.9),glassblock,cols['Facade'])
 for x in (-4.5,0,4.5): cube('LAMB | vestibule door mullion',(x,miny-.20,1.75),(.12,.12,2.95),metal,cols['Facade'])
 cube('LAMB | immediate entry walk',(0,miny-3.0,.04),(15.0,5.0,.08),concrete,cols['Site'])
elif cfg['kind']=='morgan':
 cube('Morgan | schematic lobby welcome desk',(0,miny-.015,1.12),(4.4,.38,.9),wood,cols['Interior'])
 for x in (-4.2,4.2): cube('Morgan | schematic lobby bench',(x,miny+2.2,.62),(2.6,.75,.22),trim,cols['Interior'])
 for x in (-8,8):
  cube('Morgan | entry planter',(x,miny-2.2,.55),(1.3,1.2,.95),stone,cols['Site'])
  for j in range(3): cyl('Morgan | schematic planter shrub',(x-.35+j*.35,miny-2.2,1.25),.23,.8,green,cols['Site'],12)
elif cfg['kind']=='soil':
 for x in (-w*.20,0,w*.20):
  cube('Soil Lab | schematic visible research workbench',(x,miny-.015,1.1),(4.4,.32,.14),wood,cols['Interior'])
  for j in range(3): cube('Soil Lab | schematic sample tray',(x-1.2+j*1.2,miny-.015,1.42),(.54,.24,.42),stone,cols['Interior'])
 cube('Soil Lab | immediate receiving apron',(minx+w*.54,miny-2.2,.04),(7.0,3.0,.08),concrete,cols['Site'])
elif cfg['kind']=='nacc':
 cube('NACC | schematic warm community-room glimpse through storm door',(porch_x,miny-.135,1.55),(.78,.045,2.25),wood,cols['Interior'])
 cube('NACC | schematic entry room floor glimpse',(porch_x,miny-.135,.34),(1.3,.18,.10),trim,cols['Interior'])
 for x in (porch_x-porch_w*.40,porch_x+porch_w*.40):
  cube('NACC | porch planter',(x,porch_y-1.4,.40),(1.0,.8,.72),stone,cols['Site'])
  cyl('NACC | schematic porch planting',(x,porch_y-1.4,.95),.34,.64,green,cols['Site'],12)
 # An accessible approach ramp is drawn as site geometry and remains an
 # approximate design cue; no verified as-built ramp measurements were found.
 ramp_len=4.8; ramp_w=1.55; ramp_cy=porch_y-3.55
 ramp=cube('NACC | schematic accessible entry ramp',(porch_x,ramp_cy,.15),(ramp_w,ramp_len,.24),concrete,cols['Site'])
 ramp.rotation_euler[0]=-math.atan2(.30,ramp_len)
 for side in (-1,1):
  rail=cube('NACC | schematic ramp handrail',(porch_x+side*(ramp_w*.58),ramp_cy,1.02),( .08,ramp_len,.08),metal,cols['Site'])
  rail.rotation_euler[0]=-math.atan2(.30,ramp_len)
  for post in range(5):
   yy=ramp_cy-ramp_len*.45+post*ramp_len*.225
   z=.55+(ramp_len*.45-post*ramp_len*.225)*(.30/ramp_len)
   cube('NACC | schematic ramp rail post',(porch_x+side*(ramp_w*.58),yy,z),(.08,.08,.95),metal,cols['Site'])
 # Schematic community lounge furniture placed in the exported interior collection.
 cube('NACC | community gathering table',(porch_x,miny+4.1,.82),(2.0,1.1,.16),wood,cols['Interior'])
 for chair in range(6):
  a=math.tau*chair/6; xx=porch_x+1.65*math.cos(a); yy=miny+4.1+1.65*math.sin(a)
  cube('NACC | schematic community chair',(xx,yy,.50),(.55,.58,.12),trim,cols['Interior'])
  cube('NACC | schematic community chair back',(xx,yy+.20,.90),(.55,.10,.72),wood,cols['Interior'])

# Grounded entry threshold, entrance nameplate and minimal schematic circulation cue.
front_y=miny+(.5 if cfg['kind']=='lab' else -.4)
front_x=porch_x if cfg['kind']=='nacc' else 0.0
cube(cfg['abbr']+' | entrance threshold',(front_x,front_y,.12),(max(3,min(w*.26,10)),1.0,.24),trim,cols['Site'])
panel_z=3.22 if cfg['kind']=='nacc' else min(3.3,h*.36)
cube(cfg['abbr']+' | dark entrance name panel',(front_x,front_y-.12,panel_z),(min(w*.48,10),.12,.48),dark,cols['Facade'])
def add_text(body,loc,size):
 cu=bpy.data.curves.new(cfg['abbr']+' | lettering','FONT'); cu.body=body; cu.size=size; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=.003
 ob=bpy.data.objects.new(cfg['abbr']+' | facade identification lettering',cu); cols['Facade'].objects.link(ob); ob.location=loc; ob.rotation_euler=(math.pi/2,0,0); cu.materials.append(trim)
if cfg['kind']=='nacc': add_text('NATIVE AMERICAN',(front_x,front_y-.20,panel_z),.20)
elif cfg['kind']=='morgan':
 add_text('MRGN',(0,front_y-.20,min(3.3,h*.36)),.28)
 add_text('BURTON D. MORGAN',(0,miny-.26,h*.82),.34)
elif cfg['kind']=='soil':
 add_text('SOIL EROSION LAB',(0,front_y-.20,min(3.3,h*.36)),.28)
 add_text('NATIONAL SOIL EROSION RESEARCH LABORATORY',(0,miny-.22,h*.86),.24)
elif cfg['kind']=='lab':
 add_text('PLANT & SOILS',(0,front_y-.20,min(3.3,h*.36)),.28)
 add_text('PLANT AND SOILS LAB',(0,miny-.20,h*.84),.30)
elif cfg['kind']=='fieldhouse':
 add_text('LAMBERT FIELDHOUSE',(0,front_y-.20,min(3.3,h*.36)),.30)
else: add_text(cfg['abbr'],(front_x,front_y-.20,panel_z),.28)

# NACC's established master marker is the source GIS polygon centroid. The
# model is constructed about the bbox center, so translate every exported
# object by B-C to preserve the GIS outline at that manifest marker.
if key=='nacc' and any(abs(v)>1e-9 for v in local_origin_shift):
 stack=list(asset.children)
 while stack:
  c=stack.pop(); stack.extend(list(c.children))
  for ob in c.objects:
   ob.location.x += local_origin_shift[0]
   ob.location.y += local_origin_shift[1]
if key=='life_science_plant_soils':
 # Keep all LSPS asset geometry within the recorded footprint. Small facade
 # attachments, entry details and the interior greenhouse inset are nudged
 # inward when their object bounds cross the GIS bbox; no site apron remains.
 stack=list(asset.children)
 while stack:
  c=stack.pop(); stack.extend(list(c.children))
  for ob in c.objects:
   if ob.type!='MESH': continue
   bounds=[ob.matrix_world@Vector(v) for v in ob.bound_box]
   obminx=min(v.x for v in bounds); obmaxx=max(v.x for v in bounds)
   obminy=min(v.y for v in bounds); obmaxy=max(v.y for v in bounds)
   dx=max(0.0,minx-obminx)-max(0.0,obmaxx-maxx)
   dy=max(0.0,miny-obminy)-max(0.0,obmaxy-maxy)
   ob.location.x+=dx; ob.location.y+=dy
asset['source_feature_id']=cfg['fid']
asset['gis_placement_origin_xy_m']=[round(cx-local_origin_shift[0],9),round(cy-local_origin_shift[1],9)]
asset['build_bbox_origin_xy_m']=[round(build_bbox_origin[0],9),round(build_bbox_origin[1],9)]
asset['local_geometry_shift_m']=list(local_origin_shift)
asset['local_origin_convention']='GIS polygon area centroid; all exported objects shifted from bbox-centered build frame' if key=='nacc' else 'GIS footprint bbox midpoint'

# Preview studio outside the exported asset collection.
world=bpy.data.worlds.new(cfg['abbr']+' | preview world'); scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(.20,.26,.34,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.68
def area(name,loc,power,color,target,size):
 bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=cfg['abbr']+' Preview '+name; o.data.energy=power; o.data.color=color; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 for c in list(o.users_collection): c.objects.unlink(o)
 rig.objects.link(o)
extent=max(w,d,h,12)
area('key',(-extent,-extent*1.45,extent*1.35),max(900,extent*extent*3),(1.0,.78,.58),(0,0,h*.4),extent*.9)
area('fill',(extent*1.3,-extent*.4,extent*.85),max(600,extent*extent*1.3),(.58,.73,1),(0,0,h*.4),extent*.8)
area('rim',(0,extent*1.4,extent*1.2),max(800,extent*extent*2),(1,.52,.28),(0,0,h*.42),extent*.75)
area('top softbox',(0,0,extent*2.15),max(900,extent*extent*2.6),(.86,.91,1.0),(0,0,h*.35),extent*1.7)
if cfg['kind']=='aquatic': area('natatorium interior softbox',(0,0,h*.82),18000,(.83,.92,1.0),(0,0,2.0),min(w,d)*.72)
if cfg['kind']=='fieldhouse': area('gym interior softbox',(0,0,h*.78),15000,(1.0,.72,.53),(0,0,2.0),min(w,d)*.72)
camera_height=.16 if cfg['kind']=='aquatic' else (.46 if cfg['kind'] in ('fieldhouse','nacc','soil','lab','morgan') else .85)
camera_loc=(extent*1.2,-extent*1.65,extent*camera_height)
if cfg['kind']=='aquatic': camera_loc=(extent*.50,-extent*1.55,h*.82)
elif cfg['kind'] in ('morgan','nacc','soil','lab'): camera_loc=(extent*.82,-extent*1.65,max(6.0,h*1.05))
bpy.ops.object.camera_add(location=camera_loc); cam=bpy.context.object; cam.name=cfg['abbr']+' | three-quarter preview camera'; cam.rotation_euler=(Vector((0,0,h*.43))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=50
for c in list(cam.users_collection): c.objects.unlink(cam)
rig.objects.link(cam); scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=16; scene.render.resolution_x=800; scene.render.resolution_y=600; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
out=os.path.join(ROOT,'modular','buildings',cfg['slug']+'.blend'); preview=os.path.join(ROOT,'audit','batchC_'+key+'_preview.png')
scene.render.image_settings.file_format='PNG'; scene.render.filepath=preview
bpy.context.view_layer.objects.active=None
bpy.ops.wm.save_as_mainfile(filepath=out)
bpy.ops.render.render(write_still=True)

# A second, purposefully close interior render makes documented use cues
# inspectable even where the source exterior is opaque or highly glazed.
interior_preview=os.path.join(ROOT,'audit','batchC_'+key+'_interior_preview.png')
if key in ('boilermaker_aquatic','lambert','life_science_plant_soils','morgan_center','national_soil_erosion','nacc'):
 # Make the detail view an explicit cutaway so the simple shell does not
 # occlude the schematic interior furniture/competition fit-out. This is a
 # render-only visibility change: the saved library remains a complete asset.
 for group in ('Structure','Facade','Roof'):
  for ob in cols[group].objects: ob.hide_render=True
 for ob in cols['Interior'].objects:
  if 'interior floor plate' in ob.name.lower() or 'interior arena floor' in ob.name.lower(): ob.hide_render=True
 # Elevated oblique cutaway camera captures a useful floor/interior overview
 # instead of looking into the solid external wall from room height.
 iloc=(extent*.58,-extent*.75,extent*1.05); itarget=(0,0,.25); ilens=42
 bpy.ops.object.camera_add(location=iloc); icam=bpy.context.object; icam.name=cfg['abbr']+' | schematic interior detail preview camera'; icam.data.lens=ilens
 icam.data.type='ORTHO'; icam.data.ortho_scale=extent*1.28
 icam.rotation_euler=(Vector(itarget)-icam.location).to_track_quat('-Z','Y').to_euler()
 for c in list(icam.users_collection): c.objects.unlink(icam)
 rig.objects.link(icam); scene.camera=icam
 scene.cycles.samples=10; scene.render.resolution_x=720; scene.render.resolution_y=480; scene.render.filepath=interior_preview
 bpy.ops.render.render(write_still=True)

# Reopen via the separate validation pass (performed by the parent workflow); record source provenance now.
origin=[round(cx-local_origin_shift[0],6 if key=='nacc' else 3),round(cy-local_origin_shift[1],6 if key=='nacc' else 3)]
aligned_minx=minx+local_origin_shift[0]; aligned_maxx=maxx+local_origin_shift[0]
aligned_miny=miny+local_origin_shift[1]; aligned_maxy=maxy+local_origin_shift[1]
objects=[o for c in asset.children for o in c.objects]
evidence={
 'building_id':cfg['id'],'name':cfg['name'],'asset_file':'modular/buildings/'+cfg['slug']+'.blend','export_collection':asset.name,
 'source_feature':{'provider':'Purdue University ArcGIS BuildingShapesZip4 FeatureServer layer 0','feature_id':cfg['fid'],'matched_name':attrs.get('BUILDING_N'),'abbreviation':attrs.get('BLDG_ABBR'),'url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','query_url':f"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D{cfg['fid']}&outFields=*&returnGeometry=true&outSR=4326&f=json",'native_crs':'EPSG:3857 / ESRI WKID 102100; query geometry requested as EPSG:4326','retrieval_date':'2026-10-24','snapshot':'audit/batchC_'+key+'_official_footprint.json','official_levels':attrs.get('NUM_LEVELS'),'GIS_extrusion_field':attrs.get('Extrution'),'GIS_address':attrs.get('ADDRESS')},
 'coordinate_method':{'source_crs':'WGS 84 geographic coordinates returned by ArcGIS outSR=4326','project_transform':'X=(longitude + 86.9137)*111412.84*cos(radians(40.4274)); Y=(latitude - 40.4274)*111040.0','local_origin':'GIS polygon area centroid' if key=='nacc' else 'midpoint of transformed GIS footprint bounding box','build_bbox_origin_xy_m':[round(build_bbox_origin[0],6),round(build_bbox_origin[1],6)],'local_geometry_shift_from_bbox_m':local_origin_shift,'recommended_master_marker_xy_m':origin,'note':'Project approximation is not a surveyed CRS. For NACC the saved geometry is translated from the bbox-centered build frame to the established GIS polygon centroid marker; the manifest centroid is [-278.927997,190.076894].' if key=='nacc' else 'Project approximation is not a surveyed CRS. Footprint was centered for source-library geometry.'},
 'footprint':{'vertices':n,'bbox_local_m':[[round(aligned_minx,3),round(aligned_miny,3)],[round(aligned_maxx,3),round(aligned_maxy,3)]],'dimensions_m':[round(w,3),round(d,3)],'approx_plan_area_m2':round(abs(area2)/2,2),'measurement':'official GIS ring transformed to project-local approximation; structural wall panels preserve the perimeter and omit modeled facade openings where glazing is present' if key in OPEN_SHELL_KINDS else 'official GIS ring transformed to project-local approximation; extruded as continuous shell','interior_rings':'none in selected feature'},
 'vertical_geometry':{'model_height_m':roof_peak,'main_wall_height_m':h,'modeled_floor_count':floors,'status':'estimated from GIS Extrution field interpreted as feet; not a measured elevation','official_num_levels':attrs.get('NUM_LEVELS'),'note':'Roof elements add height beyond main envelope; verify against current imagery/plans if elevations become available. For Burton Morgan, official Purdue imagery text identifies a two-story building while the GIS record codes five levels; the model follows the photo-supported two-story description and records the GIS conflict.' if key=='morgan_center' else 'Roof elements add height beyond main envelope; verify against current imagery/plans if elevations become available.'},
 'references':[{'provider':'Purdue University / official ArcGIS building GIS','url':f"https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D{cfg['fid']}&outFields=*&returnGeometry=true&outSR=4326&f=json",'accessed':'2026-10-24','use':'footprint outline, official building identity, levels and extrusion attribute'}]+[{'provider':('USDA-ARS / Purdue NSERL' if 'topsoil.nserl.purdue.edu' in u else ('Google Maps' if 'google.com/maps' in u else ('Purdue University' if 'purdue.edu' in u else 'Published architectural / facility source'))),'url':u,'accessed':'2026-10-24','use':('exterior building photograph / landmark identification' if 'image007.jpg' in u else ('historic facility identity and construction context' if 'booklet.htm' in u else ('campus address / street context' if 'google.com/maps' in u else 'building identity, architectural features, or public context')))} for u in cfg['refs']],
 'modeled_features':['official GIS footprint shell/perimeter preserved','repeated facade bays and horizontal datums','procedural connected materials: brick, precast/concrete, glazing, metal and roof','building-specific roof/entry features described in source script','building-specific interior geometry is stored in the exported Interior collection, not only in the render setup','preview lighting/camera excluded from exported asset collection'],
 'specific_evidence_boundary':(
  'The 8-lane 50 m pool, diving use, high clear-span interior and spectator viewing are supported by official Purdue facility pages/photos; exterior roof profile and exact window/seat layout remain schematic estimates.' if key=='boilermaker_aquatic' else
  'The official PPDL map confirms nearby greenhouse facilities but does not verify an attached wing. The glazed growing bay is a schematic facade inset fully inside the selected GIS footprint; the unverified outside service apron was removed and all facade/site mesh bounds are contained within the GIS bbox.' if key=='life_science_plant_soils' else
  'Brick, concrete piers, glass-block facade, and indoor track use are photo/facility-informed; roof edge profile, exact clerestory placement, track geometry and bleacher locations are schematic estimates.' if key=='lambert' else
  'Two-storey brick/metal/glass profile and large entry overhang are supported by the Purdue award photograph/text. Interior desk, planters and exact glazing layout are schematic.' if key=='morgan_center' else
  'The official USDA/Purdue exterior photo verifies brick facade character and the laboratory name sign. Service shutters, receiving door and loading-side fenestration are schematic pending a verified loading-side reference.' if key=='national_soil_erosion' else
  'Official Purdue sources verify the current address and adaptive reuse of a former single-family house. The porch, garage/service door, window pattern and room glimpse are visibly interpretive schematic details; no archival photo is claimed.' if key=='nacc' else
  'All building-specific facade and roof details beyond the GIS footprint are interpretive estimates.'),
 'validation':{'saved':True,'render_preview':'audit/batchC_'+key+'_preview.png','interior_detail_preview':'audit/batchC_'+key+'_interior_preview.png','generated_at_local':datetime.datetime.now().astimezone().isoformat(timespec='seconds'),'asset_object_count':len(objects),'mesh_object_count':sum(o.type=='MESH' for o in objects),'interior_collection':'Interior','interior_object_count':len(cols['Interior'].objects),'interior_mesh_count':sum(o.type=='MESH' for o in cols['Interior'].objects),'interior_geometry_exported':True,'window_glazing_bays':window_count,'materials':len({m.name for o in objects if o.type=='MESH' for m in o.data.materials if m}),'material_nodes_connected':True,'source_collection_objects_only':True,'master_or_manifest_edited':False},
 'uncertainties':['GIS horizontal footprint is a good source for the plan but does not verify wall height, facade bay locations, or roof equipment.','Heights are interpreted from the GIS extrusion attribute and remain estimates.','Facade imagery is referenced through official pages and map links; current Street View imagery was not independently captured or date-verified in this build pass.','Interior circulation and finishes are schematic cues, not measured architectural plans.']}
with open(os.path.join(ROOT,'audit','batchC_'+key+'_evidence.json'),'w',encoding='utf-8') as f: json.dump(evidence,f,indent=2)
print(json.dumps({'asset':out,'preview':preview,'collection':asset.name,'objects':len(objects),'mesh_objects':sum(o.type=='MESH' for o in objects),'materials':len({m.name for o in objects if o.type=='MESH' for m in o.data.materials if m}),'origin_xy':origin,'local_dimensions_m':[round(w,2),round(d,2),round(h,2)],'window_glazing_bays':window_count},indent=2))
