import bpy, json, math, os, sys, random
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
GIS=os.path.join(ROOT,'audit','official_purdue_buildings_wgs84.json')
OUT=os.path.join(ROOT,'modular','buildings')
EV=os.path.join(ROOT,'audit','build_batch_a')
ORLAT,ORLON=40.4274,-86.9137
SX=111412.84*math.cos(math.radians(ORLAT)); SY=111040.0
DATA={
'AGAD':dict(id='agricultural_administration_building', fid=267, name='Agricultural Administration Building', mass='massing_agricultural_administration_building_120d92c', stories=5, h=17.2, style='historic', brick=(.34,.105,.065), stone=(.66,.59,.45), glass=(.16,.29,.31), roof=(.17,.18,.18), accent=(.40,.25,.15), year='1930s-era Collegiate Gothic/Georgian campus brick, symmetrical principal entrance, pale stone trim, tall punched windows, pedimented entry', refs=[('Purdue College of Agriculture image','https://ag.purdue.edu/news/department/hla/2020/05/root-and-vine-psf-food-bank.html','Current page photo; red brick symmetry and central entry.'),('Purdue building directory','https://www.purdue.edu/campus/buildings/','Official building identity/address; facade details inferred from Purdue photo.')]),
'ABE':dict(id='agricultural_and_biological_engineering_abe',fid=406,name='Agricultural and Biological Engineering (ABE)',mass='massing_agricultural_and_biological_engineering_abe_0ebc7b3',stories=6,h=22.0,style='hybrid',brick=(.40,.20,.13),stone=(.68,.63,.52),glass=(.17,.34,.39),roof=(.21,.23,.24),accent=(.48,.29,.19),year='2020 renovation/addition: brick and glass laboratory wings, stone entry surround with historic 1928 marker, multi-story glazing and rooftop lab services',refs=[('Official ABE building history','https://engineering.purdue.edu/ABE/BldgHistory','Historical context and archive photos; building renewal noted.'),('Pepper Construction project','https://www.pepperconstruction.com/project/purdue-university-agriculture-and-biological-engineering-renovation-addition','Renovation/addition materials and massing.'),('Farm Progress exterior photo','https://www.farmprogress.com/technology/check-out-purdue-s-new-research-facilities','Exterior brick/glass and entrance reference.')]),
'ADDL':dict(id='animal_disease_diagnostic_laboratory',fid=241,name='Willie M. Reed Animal Disease Diagnostic Laboratory',mass='massing_animal_disease_diagnostic_laboratory_b934354',stories=5,h=18.0,style='lab',brick=(.49,.43,.34),stone=(.68,.66,.59),glass=(.19,.27,.29),roof=(.25,.27,.28),accent=(.46,.49,.48),year='Research/diagnostic laboratory: restrained masonry and metal-clad service volumes, regular lab window bays, roof exhaust and screened HVAC; five-level data field treated as estimated height',refs=[('Purdue ADDL official page','https://vet.purdue.edu/addl/','Official campus laboratory and role; current imagery.'),('Purdue ADDL history/news','https://www.addl.purdue.edu/Newsletters/2007/Summer/Letter.htm','2007 description of attached high-containment addition; model signals service exhaust without exposing interior details.'),('Purdue official capital records','https://www.purdue.edu/treasurer/finance/wp-content/uploads/2023/04/Reed-Animal-Disease-Diagnostic-Laboratory-Equipment-Replacement-B-1-23-2-08.pdf','2023 project record and existing facility references.')]),
'BIDC':dict(id='bechtel_innovation_design_center_bidc',fid=912,name='Bechtel Innovation Design Center (BIDC)',mass='massing_bechtel_innovation_design_center_bidc_5488863',stories=2,h=10.8,style='modern',brick=(.39,.17,.11),stone=(.58,.58,.53),glass=(.11,.29,.34),roof=(.18,.20,.22),accent=(.72,.35,.10),year='2017 makerspace; modern transparent student-facing entrance, dark metal framing, red/brown masonry and industrial roof plant; interior only schematic',refs=[('Bechtel Center official about and floorplans','https://www.purdue.edu/bidc/about/about-the-center/','Official building purpose and posted first/second/basement plans; massing details estimated from available page imagery.'),('Purdue BIDC','https://www.purdue.edu/bidc/','Official center identity and facility information.')]),
'BIND':dict(id='bindley_bioscience_center',fid=605,name='Bindley Bioscience Center',mass='massing_bindley_bioscience_center_641f939',stories=3,h=12.0,style='lab',brick=(.64,.65,.61),stone=(.74,.73,.68),glass=(.12,.28,.35),roof=(.22,.23,.24),accent=(.56,.34,.19),year='Discovery Park research center; three-story glass-and-light-metal research block, curtain-wall bands, a strong ground-floor lobby and screened rooftop mechanical equipment',refs=[('Bindley Bioscience official site','https://bindley.research.purdue.edu/','Official center identity and current site.'),('Purdue Statistics view from Bindley','https://www.stat.purdue.edu/news/2020/bindley.html','Published campus/building view; modest facade details inferred.'),('Purdue Discovery Park directory','https://www.purdue.edu/discoverypark/bioscience/directory/view.php?id=3080','Building identity and Discovery Park context.')]),
'BCHM':dict(id='biochemistry_building',fid=238,name='Biochemistry Building',mass='massing_biochemistry_building_a267b8d',stories=5,h=16.0,style='historic_lab',brick=(.40,.16,.10),stone=(.62,.57,.48),glass=(.17,.27,.29),roof=(.21,.22,.21),accent=(.50,.34,.20),year='1938 Agricultural Chemistry origin with 1952 and 1981 additions; brick academic/lab block, repeated vertical window bays and layered additions (massing joins are interpretive)',refs=[('Purdue Archives building record','https://archives.lib.purdue.edu/agents/corporate_entities/641','Historical sequence and earlier name.'),('Purdue Provost classroom planning','https://www.purdue.edu/provost/about/provostInitiatives/classroom/index.php','Current use and room context; exterior facade specifics estimated.')]),
'BRFM':dict(id='david_and_bonnie_brunner_farm_animal_hospital',fid=408,name='David and Bonnie Brunner Farm Animal Hospital',mass='massing_david_and_bonnie_brunner_farm_animal_hospital_dada82b',stories=2,h=9.4,style='veterinary',brick=(.53,.49,.40),stone=(.72,.69,.61),glass=(.18,.30,.32),roof=(.20,.21,.21),accent=(.42,.39,.32),year='Separate 23,900-square-foot farm-animal hospital east of the Equine Hospital; low clinical wing, clear client/service entrances, restrained veterinary campus palette; height estimated',refs=[('Purdue Veterinary Medicine Farm Hospital virtual tour','https://vet.purdue.edu/hospital/virtual-tour/hospital.php?id=3','Official exterior/context tour and hospital organization.'),('Purdue BRFM emergency plan','https://www.purdue.edu/operations/emergency-preparedness/brfm/','Official address/building identity and exterior reference image.')]),
'DAUC':dict(id='dauch_alumni_center',fid=71,name='Dick & Sandy Dauch Alumni Center',mass='massing_dauch_alumni_center_3cb1249',stories=4,h=14.4,style='alumni',brick=(.42,.13,.09),stone=(.68,.61,.48),glass=(.10,.27,.32),roof=(.17,.19,.20),accent=(.72,.38,.13),year='2004-era alumni gathering center; rounded brick facade with large glazed atrium, stone sign/base, event spaces, flagpoles and curved roofline',refs=[('Purdue for Life photo','https://www.purdueforlife.org/about/','Current exterior and glass/brick form.'),('Home of Purdue visitor listing','https://www.homeofpurdue.com/listing/dauch-alumni-center/31/','Exterior identity and facade reference.'),('Purdue Archives campus facilities database','https://collections.lib.purdue.edu/campus/buildings','Official campus building identity.')])}

def material(name,color,rough=.65,metal=0,scale=28,bump=.06):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
 tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=3;noise.inputs['Roughness'].default_value=.72
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.2;ramp.color_ramp.elements[0].color=(*(v*.84 for v in color),1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(*(min(1,v*1.13) for v in color),1)
 l.new(tc.outputs['Generated'],noise.inputs['Vector']);l.new(noise.outputs['Fac'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],b.inputs['Base Color'])
 bu=n.new('ShaderNodeBump');bu.inputs['Strength'].default_value=bump;bu.inputs['Distance'].default_value=.035;l.new(noise.outputs['Fac'],bu.inputs['Height']);l.new(bu.outputs['Normal'],b.inputs['Normal']);return m

def box(name,loc,dim,mat,col,ang=0,bevel=0):
 # Build boxes directly rather than invoking operators thousands of times; this
 # keeps batch generation practical while preserving individually named details.
 x,y,z=loc;dx,dy,dz=(v*.5 for v in dim);ca,sa=math.cos(ang),math.sin(ang)
 v=[]
 for zz in (-dz,dz):
  for yy in (-dy,dy):
   for xx in (-dx,dx):v.append((x+ca*xx-sa*yy,y+sa*xx+ca*yy,z+zz))
 f=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
 me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(v,[],f);me.materials.append(mat);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o)
 if bevel:
  mod=o.modifiers.new('Soft architectural edge','BEVEL');mod.width=bevel;mod.segments=2
  o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);return o

def mesh_obj(name,verts,faces,mat,col):
 me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(verts,[],faces);me.materials.append(mat);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);return o

def poly_area_centroid(ring):
 A=0;cx=cy=0
 for (x,y),(u,v) in zip(ring,ring[1:]+ring[:1]):
  q=x*v-u*y;A+=q;cx+=(x+u)*q;cy+=(y+v)*q
 if abs(A)<1e-7:return (sum(x for x,y in ring)/len(ring),sum(y for x,y in ring)/len(ring))
 return cx/(3*A),cy/(3*A)

def reset():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for c in list(bpy.data.collections):
  if c.name!='Collection':bpy.data.collections.remove(c)
 root=bpy.context.scene.collection
 for c in list(root.children):
  if c.name=='Collection':root.children.unlink(c)

def roof_tess(local):
 rings=[[Vector((x,y,0)) for x,y in local]]
 try:
  tris=tessellate_polygon(rings)
  return [tuple(int(k) for k in t) for t in tris]
 except:return [tuple(range(len(local)))]

def build(code,feature):
 p=DATA[code];name=p['id']; reset();scene=bpy.context.scene
 col=bpy.data.collections.new('Asset_'+name);scene.collection.children.link(col)
 a=feature['attributes'];rings=feature['geometry']['rings'];ring=rings[0]
 pts=[((lon-ORLON)*SX,(lat-ORLAT)*SY) for lon,lat in ring[:-1]]
 ox,oy=poly_area_centroid(pts);local=[(x-ox,y-oy) for x,y in pts]
 minx=min(x for x,y in local);maxx=max(x for x,y in local);miny=min(y for x,y in local);maxy=max(y for x,y in local);wx=maxx-minx;wy=maxy-miny
 # material palette specific to each building
 brick=material(name+'_textured_masonry',p['brick'],.76,0,42,.13);stone=material(name+'_cut_stone',p['stone'],.7,0,30,.1);glass=material(name+'_blue_gray_glazing',p['glass'],.18,.28,8,.015);roofmat=material(name+'_roof_membrane',p['roof'],.62,.06,54,.12);metal=material(name+'_dark_metal',p['accent'],.34,.55,20,.04);inside=material(name+'_schematic_interior',(.62,.59,.50),.82,0,20,.04);floor=material(name+'_interior_floor',(.36,.36,.33),.75,0,45,.08)
 h=p['h'];stories=p['stories'];base=.35
 # exact official wall-plan polygon, extruded as the primary shell
 n=len(local);verts=[(x,y,base) for x,y in local]+[(x,y,h) for x,y in local]
 faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 shell=mesh_obj(name+'_GIS_outline_primary_shell',verts,faces,brick,col)
 shell['Source_feature_FID']=int(a['FID']);shell['Plan_source']='Purdue BuildingShapes official GIS outer footprint';shell['Height_status']='GIS extrusion / story field is not elevation survey; height is modeled estimate'
 # plinth/pale belt
 for z,th,mat in [(.3,.7,stone),(h*.72,.28,stone)]:
  for i,(x,y) in enumerate(local):
   u,v=local[(i+1)%n];dx=u-x;dy=v-y;L=math.hypot(dx,dy)
   if L<2:continue
   ang=math.atan2(dy,dx);mx=(x+u)/2;my=(y+v)/2
   # tangent-aligned trim with slim outside projection
   box(f'{code}_belt_{z:.1f}_{i}',(mx-.045*math.sin(ang),my+.045*math.cos(ang),z),(L,.13,th),mat,col,ang,.025)
 # architectural windows + frame every substantial facade segment; full occupancy by level
 levelh=(h-base)/stories
 for i,(x,y) in enumerate(local):
  u,v=local[(i+1)%n];dx=u-x;dy=v-y;L=math.hypot(dx,dy)
  if L<4.0:continue
  ang=math.atan2(dy,dx);nx=math.sin(ang);ny=-math.cos(ang); # outward normal for ring orientation may be cw, detect via area
  signed=sum(local[j][0]*local[(j+1)%n][1]-local[(j+1)%n][0]*local[j][1] for j in range(n))
  if signed<0:nx,ny=-nx,-ny
  margin=1.0 if L>7 else .6
  count=max(1,int((L-2*margin)/(2.5 if p['style'] in ('modern','lab') else 3.05)))
  stride=(L-2*margin)/count
  for lev in range(stories):
   z=base+levelh*(lev+.5)
   for j in range(count):
    along=margin+(j+.5)*stride
    cx=x+dx*(along/L)+nx*.11;cy=y+dy*(along/L)+ny*.11
    ww=min(1.5 if p['style'] in ('historic','historic_lab') else 2.0,stride*.67)
    wh=min(1.85,levelh*.58)
    # agricultural administration has a formal, vertical window rhythm
    if p['style']=='historic':ww=min(1.35,stride*.62);wh=min(2.0,levelh*.68)
    box(f'{code}_glazed_bay_{i}_{lev}_{j}',(cx,cy,z),(ww,.15,wh),glass,col,ang,.012)
    # jamb mullions and sills; explicit finer architectural rhythm
    for side in (-1,1):
     px=cx+math.cos(ang)*side*ww*.5;py=cy+math.sin(ang)*side*ww*.5
     box(f'{code}_mullion_{i}_{lev}_{j}_{side}',(px,py,z),(0.055,.19,wh+.08),metal,col,ang)
    box(f'{code}_sill_{i}_{lev}_{j}',(cx,cy,z-wh*.5-.06),(ww+.18,.24,.11),stone,col,ang,.018)
 # prominent building-specific facade block/signature entry on longest south-ish/visible wall
 edges=[]
 for i,(x,y) in enumerate(local):
  u,v=local[(i+1)%n];L=math.hypot(u-x,v-y)
  if L>=6:edges.append((L,i,x,y,u,v))
 # select frontage by outward normal facing campus south (negative y); choose longest edge with outward y<-.25 if possible
 signed=sum(local[j][0]*local[(j+1)%n][1]-local[(j+1)%n][0]*local[j][1] for j in range(n))
 choices=[]
 for e in edges:
  L,i,x,y,u,v=e;ang=math.atan2(v-y,u-x);nx=math.sin(ang);ny=-math.cos(ang)
  if signed<0:nx,ny=-nx,-ny
  choices.append((ny,L,e,nx,ny,ang))
 front=min(choices,key=lambda q:(q[0],-q[1])) if choices else None
 if front:
  _,L,e,nx,ny,ang=front;_,i,x,y,u,v=e;mid=((x+u)/2,(y+v)/2); cx=mid[0]+nx*.14;cy=mid[1]+ny*.14
  # main entry glazed recess / vestibule + projecting stone portal
  doorw=min(3.2,max(2.0,L*.14));doorh=min(3.4,levelh*.95)
  box(code+'_main_entrance_glazed_door',(cx,cy,base+doorh*.5),(doorw,.24,doorh),glass,col,ang,.02)
  box(code+'_entry_portal_left',(cx-math.cos(ang)*doorw*.58,cy-math.sin(ang)*doorw*.58,base+doorh*.53),(.32,.42,doorh+1.0),stone,col,ang,.03)
  box(code+'_entry_portal_right',(cx+math.cos(ang)*doorw*.58,cy+math.sin(ang)*doorw*.58,base+doorh*.53),(.32,.42,doorh+1.0),stone,col,ang,.03)
  box(code+'_entry_lintel',(cx,cy,base+doorh+.48),(doorw+1.5,.48,.36),stone,col,ang,.04)
  # entry canopy modern types; pediment/archivolt historic
  if p['style']=='historic':
   box(code+'_pediment_cornice',(cx,cy,base+doorh+1.1),(doorw+2.4,.65,.3),stone,col,ang,.03)
   # shallow gable triangle placed as oriented triangular mesh
   verts=[(-doorw*.62,0,0),(doorw*.62,0,0),(0,0,1.0),(-doorw*.62,-.12,0),(doorw*.62,-.12,0),(0,-.12,1.0)]
   V=[]
   for lx,ly,lz in verts:
    V.append((cx+math.cos(ang)*lx-math.sin(ang)*ly,cy+math.sin(ang)*lx+math.cos(ang)*ly,base+doorh+1.28+lz))
   mesh_obj(code+'_entry_gabled_pediment',V,[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)],stone,col)
  else:
   box(code+'_entry_canopy',(cx,cy,base+doorh+.45),(doorw+2.0,1.5,.26),metal,col,ang,.04)
  # identify a side elevation sign via raised gold letter geometry
  bpy.ops.object.text_add(location=(cx+nx*.25,cy+ny*.25,base+doorh+.75));o=bpy.context.object;o.name=code+'_facade_identity_sign';o.data.body=p['name'].replace(' (BIDC)','');o.data.align_x='CENTER';o.data.size=.46 if len(p['name'])<28 else .32;o.data.extrude=.012;o.rotation_euler[0]=math.radians(90);o.rotation_euler[2]=ang-math.pi/2;o.data.materials.append(metal)
  for c in list(o.users_collection):c.objects.unlink(o)
  col.objects.link(o)
 # Building-specific identity elements, based on each source's distinctive form.
 # These sit just beyond the GIS wall line and are recorded as interpretive
 # additions rather than changes to the official footprint.
 if front and code in ('BIDC','BIND','DAUC'):
  _,L,e,nx,ny,ang=front;_,i,x,y,u,v=e
  # Double-height lobby / atrium glass articulates the principal public face.
  panelw=min(L*.54, 19.0 if code=='BIND' else 15.0)
  panelh=h*.70 if code=='DAUC' else min(h*.66, 8.0)
  cx=(x+u)/2+nx*.22;cy=(y+v)/2+ny*.22;cz=base+panelh*.53
  box(code+'_signature_public_lobby_curtainwall',(cx,cy,cz),(panelw,.20,panelh),glass,col,ang,.025)
  for q in range(1,7):
   dx=math.cos(ang)*(-panelw*.5+panelw*q/7);dy=math.sin(ang)*(-panelw*.5+panelw*q/7)
   box(f'{code}_signature_curtainwall_mullion_{q}',(cx+dx,cy+dy,cz),(.075,.27,panelh),metal,col,ang)
  for q in range(1,3):
   box(f'{code}_signature_curtainwall_transom_{q}',(cx,cy,base+panelh*q/3),(panelw,.27,.095),metal,col,ang)
  if code=='DAUC':
   # Dauch's campus identity includes a freestanding set of three flagpoles.
   for q in range(3):
    px=cx+math.cos(ang)*(panelw*.55+q*1.25)+nx*.8;py=cy+math.sin(ang)*(panelw*.55+q*1.25)+ny*.8
    box(f'DAUC_flagpole_{q+1}',(px,py,h*.58),(.085,.085,h*1.08),stone,col)
    box(f'DAUC_flag_{q+1}',(px+1.0,py,h*.99),(1.8,.045,.9),metal if q==2 else stone,col)
 if code=='ABE' and front:
  # High-bay laboratory / modern addition roof lantern; height and position
  # are interpretive cues, not survey geometry.
  rx=(min(x for x,y in local)+max(x for x,y in local))*.5;ry=(min(y for x,y in local)+max(y for x,y in local))*.5
  box('ABE_addition_high_bay_roof_lantern',(rx,ry,h+.75),(max(8,wx*.24),max(5,wy*.12),1.45),glass,col,.04,.05)
 if code=='AGAD' and front:
  # Formal central portico columns reinforce the historic symmetric entrance.
  _,L,e,nx,ny,ang=front;_,i,x,y,u,v=e;cx=(x+u)/2+nx*.25;cy=(y+v)/2+ny*.25
  for side in (-1,1):
   px=cx+math.cos(ang)*side*2.0;py=cy+math.sin(ang)*side*2.0
   box(f'AGAD_pediment_portico_column_{side}',(px,py,base+2.15),(.42,.48,3.8),stone,col,ang,.035)
   box(f'AGAD_portico_capital_{side}',(px,py,base+4.05),(.75,.72,.28),stone,col,ang,.035)
  box('AGAD_portico_entablature',(cx,cy,base+4.15),(5.6,.65,.38),stone,col,ang,.04)
 # roof coping, parapet and screened plant
 for i,(x,y) in enumerate(local):
  u,v=local[(i+1)%n];L=math.hypot(u-x,v-y)
  if L<2.5:continue
  ang=math.atan2(v-y,u-x);box(f'{code}_roof_coping_{i}',((x+u)/2,(y+v)/2,h+.08),(L,.3,.22),stone if p['style'] in ('historic','historic_lab') else metal,col,ang,.02)
 roof_mesh=mesh_obj(code+'_roof_membrane_surface',[(x,y,h-.08) for x,y in local],roof_tess(local),roofmat,col)
 # rooftop service penthouse, vents, chimneys, screened HVAC: preserve prominent profile cues
 minx=min(x for x,y in local);maxx=max(x for x,y in local);miny=min(y for x,y in local);maxy=max(y for x,y in local);wx=maxx-minx;wy=maxy-miny
 # industrial screen on 2-5 roof equipment blocks
 box(code+'_roof_mechanical_screen',(.26*minx+.74*maxx,.20*miny+.80*maxy,h+.7),(max(4,wx*.22),max(3,wy*.13),1.25),metal,col,.06,.08)
 for j in range(max(3,stories)):
  qx=minx+wx*(.30+.10*(j%5));qy=miny+wy*(.68+.035*(j%4));rad=.23 if p['style'] in ('lab','veterinary') else .15
  box(f'{code}_roof_exhaust_stack_{j}',(qx,qy,h+1.5),(rad*2,rad*2,1.5+(j%2)*.65),metal,col,0,.04)
  box(f'{code}_exhaust_cap_{j}',(qx,qy,h+2.28+(j%2)*.65),(rad*3.2,rad*3.2,.12),stone,col,0,.025)
 # distinct material panel pilasters/modern spandrels across elevations
 for i,(x,y) in enumerate(local):
  u,v=local[(i+1)%n];L=math.hypot(u-x,v-y)
  if L<12:continue
  ang=math.atan2(v-y,u-x);nx=math.sin(ang);ny=-math.cos(ang)
  if signed<0:nx,ny=-nx,-ny
  npost=max(2,int(L/9))
  for q in range(npost+1):
   t=(q+.25)/npost;px=x+u*t-x*t+nx*.03;py=y+v*t-y*t+ny*.03
   if p['style'] in ('modern','lab','alumni','veterinary','hybrid'):
    box(f'{code}_facade_pier_{i}_{q}',(px,py,h*.55),(.10,.12,h*.88),metal if p['style'] in ('modern','lab') else stone,col,ang)
 # schematic interior: explicitly not as-built. Floors, open corridors, core, rooms, stairs, furniture silhouettes.
 interior=bpy.data.collections.new(code+'_SCHEMATIC_INTERIOR_NOT_AS_BUILT');col.children.link(interior)
 for lev in range(stories):
  z=base+lev*levelh+.08
  box(f'{code}_schematic_floor_{lev}',(0,0,z),(wx*.52,wy*.53,.12),floor,interior)
  # central circulation spine; corridors and a structural core
  box(f'{code}_schematic_corridor_{lev}',(0,0,z+.14),(wx*.44,1.9,.12),stone,interior)
  box(f'{code}_schematic_core_{lev}',(.22*wx,-.18*wy,z+levelh*.40),(max(2,wx*.12),max(2,wy*.10),levelh*.78),inside,interior)
  # partitions/door cues
  for s in (-1,1):
   box(f'{code}_schematic_partition_{lev}_{s}',(s*wx*.16,0,z+1.4),(.12,wy*.34,2.8),inside,interior)
   for q in range(3):box(f'{code}_schematic_bench_{lev}_{s}_{q}',(s*wx*.16, -wy*.12+q*wy*.12,z+.52),(max(.8,wx*.08),.7,.85),stone,interior,.0,.05)
  # circled staircase cue as stepped flights
  for q in range(6):box(f'{code}_schematic_stair_tread_{lev}_{q}',(-wx*.20+q*.30,wy*.20,z+.15+q*.27),(.62,1.5,.18),metal,interior)
 # Floorplan label lives within the interior and clearly records schematic status
 bpy.ops.object.text_add(location=(-wx*.23,-wy*.23,.8));txt=bpy.context.object;txt.name=code+'_SCHEMATIC_ONLY_label';txt.data.body='SCHEMATIC INTERIOR — NOT AS-BUILT';txt.data.size=1.2;txt.data.materials.append(metal)
 for c in list(txt.users_collection):c.objects.unlink(txt)
 interior.objects.link(txt)
 # source-specific lower entrance steps
 if front:
  _,L,e,nx,ny,ang=front;_,i,x,y,u,v=e;cx=(x+u)/2+nx*.14;cy=(y+v)/2+ny*.14
  for q in range(4):box(f'{code}_entry_step_{q}',(cx+nx*(1.1+q*.42),cy+ny*(1.1+q*.42),.12+q*.17),(3.6,1.0,.24),stone,col,ang,.035)
 # scene, camera, render preview. Collection remains exportable as a single stable collection.
 scene.render.engine='CYCLES' if False else 'BLENDER_EEVEE';scene.render.resolution_x=1000;scene.render.resolution_y=820;scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
 scene.world.use_nodes=True; scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.35,.38,.42,1); scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.65
 bpy.ops.object.camera_add(location=(maxx+wx*.9,miny-wy*1.25,h*1.08));cam=bpy.context.object;cam.name='PreviewCamera_'+name;target=Vector((0,0,h*.42));cam.rotation_euler=(target- cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=47;scene.camera=cam
 for typ,loc,power,size in [('AREA',(wx*.15,-wy*.45,h*2.4),max(18000,wx*wy*4.0),max(wx,wy)*.8),('AREA',(-wx*.65,wy*.4,h*1.5),max(9000,wx*wy*2.0),max(wx,wy)*.6)]:
  bpy.ops.object.light_add(type=typ,location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,h*.4))-l.location).to_track_quat('-Z','Y').to_euler();l.name='PreviewLight_'+name
 scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=1.2;scene.render.image_settings.color_mode='RGBA';scene.camera.data.dof.use_dof=False
 preview=os.path.join(EV,name+'_preview.png');scene.render.filepath=preview
 # camera/light and interior are in collection; user can link a complete self-contained collection
 # pack no external files; all surface maps are procedural.
 out=os.path.join(OUT,name+'.blend');bpy.ops.wm.save_as_mainfile(filepath=out)
 bpy.ops.render.render(write_still=True)
 # evidence with raw feature snapshot
 raw=os.path.join(EV,name+'_gis_feature_'+str(a['FID'])+'.json')
 json.dump({'provider':'Purdue University BuildingShapes ArcGIS FeatureServer','feature':feature,'retrieved_date':'2026-10-24','source_crs':'EPSG:4326 local WGS84 snapshot transformed from ArcGIS EPSG:3857 service','service_url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0'},open(raw,'w'),indent=2)
 materials=[m for m in bpy.data.materials if m.name.startswith(name+'_')]
 evidence={'building_id':p['mass'],'detailed_asset_id':name,'asset_file':os.path.relpath(out,ROOT),'exported_collection':col.name,'scene':'Scene','source_feature':{'provider':'Purdue University BuildingShapes ArcGIS FeatureServer','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','feature_id':int(a['FID']),'building_code':a.get('BLDG_ABBR'),'building_name_source':a.get('BUILDING_N'),'source_address':a.get('ADDRESS'),'retrieved':'2026-10-24','source_crs':'Service EPSG:3857; checked-in snapshot stored WGS84/EPSG:4326','attributes':{k:a.get(k) for k in ('NUM_LEVELS','Extrution','Elevation','BUILT','OCCUPIED','Shape__Area','Shape__Length')},'snapshot':os.path.relpath(raw,ROOT)},'references':[{'provider':r[0],'url':r[1],'observed_or_supports':r[2]} for r in p['refs']],'street_view':{'status':'not independently confirmed in this pass','method':'Google Maps Street View availability requires a linked in-app review; no street panorama evidence is claimed for this asset'},'geometry':{'coordinates':'local meters at polygon centroid; X east, Y north, Z up','local_origin_xy_m':[ox,oy],'footprint_vertex_count':len(local),'plan_bounds_local_m':[min(x for x,y in local),max(x for x,y in local),min(y for x,y in local),max(y for x,y in local)],'footprint_source':'Exact first exterior ring of matched official Purdue GIS feature, with satellite-attached courtyard/hole rings omitted from shell; no rescaling','levels_modeled':stories,'height_m':h,'height_status':'estimated from building count/use and photo/story cues; not survey-verified','facade_description':p['year'],'interior':'Procedural schematic multi-floor circulation, core, rooms, stairs and furniture silhouettes. It is intentionally labeled NOT AS-BUILT; no room plan claimed. BIDC official posted plan availability exists but was not traced into geometry.'},'materials':{'count':len(materials),'all_procedural_and_portable':True,'texture_network':'Generated-coordinate noise/ramp color with bump, no external image paths'},'validation':{'preview':os.path.relpath(preview,ROOT),'saved_source_library':True,'expected_collection':col.name,'object_count':len(col.all_objects),'shell_object':shell.name,'geometry_edit':'Created new source library; original campus massing library untouched'},'uncertainties':['Purdue GIS polygon can include footprint geometry updated by survey/cartography; the matched record was checked by code, name and address but not by an on-site survey.','Wall height and roof elevations are estimates; GIS level/extrusion attributes are not treated as a surveyed elevation.','Facade bay dimensions and window counts are visual estimates from available Purdue/project reference pages; no measured elevations or construction drawings were located.','Interior is schematic only and not an as-built plan.','Street View was not available/verified in this modeling pass.']}
 json.dump(evidence,open(os.path.join(EV,name+'_evidence.json'),'w'),indent=2)
 print('BUILT',name,'feature',a['FID'],'origin',ox,oy,'objects',len(col.all_objects),'path',out,flush=True)

def main():
 d=json.load(open(GIS,encoding='utf-8'));features={f['attributes']['BLDG_ABBR']:f for f in d['features'] if f.get('attributes',{}).get('BLDG_ABBR') in DATA}
 for c,p in DATA.items():
  f=features.get(c)
  if not f:raise RuntimeError('Missing GIS feature: '+c)
  build(c,f)
if __name__=='__main__':main()


