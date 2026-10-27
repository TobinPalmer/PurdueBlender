import bpy, json, math, os, sys, random
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
GIS=os.path.join(ROOT,'audit','brunner_farm_animal_hospital','sources','purdue_gis_feature_408.json')
OUT=os.path.join(ROOT,'modular','buildings')
EV=os.path.join(ROOT,'audit','brunner_farm_animal_hospital')
ORLAT,ORLON=40.4274,-86.9137
SX=111412.84*math.cos(math.radians(ORLAT)); SY=111040.0
DATA={
'BRFM':dict(id='david_and_bonnie_brunner_farm_animal_hospital',fid=408,name='David and Bonnie Brunner Farm Animal Hospital',mass='massing_david_and_bonnie_brunner_farm_animal_hospital_dada82b',stories=1,h=6.2,style='veterinary',brick=(.47,.19,.13),stone=(.73,.70,.63),glass=(.10,.24,.28),roof=(.18,.18,.17),accent=(.15,.16,.16),year='Separate 23,900-square-foot farm-animal hospital east of the Equine Hospital; low clinical wing, clear client/service entrances, restrained veterinary campus palette; height estimated',refs=[('Purdue Veterinary Medicine Farm Hospital virtual tour','https://vet.purdue.edu/hospital/virtual-tour/hospital.php?id=3','Official exterior/context tour and hospital organization.'),('Purdue BRFM emergency plan','https://www.purdue.edu/operations/emergency-preparedness/brfm/','Official address/building identity and exterior reference image.')]),
}

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


def add_box(name, center, dims, mat, rotation=0.0, bevel=0.0):
    x,y,z=center; dx,dy,dz=(v*.5 for v in dims); c,s=math.cos(rotation),math.sin(rotation)
    verts=[]
    for zz in (-dz,dz):
        for yy in (-dy,dy):
            for xx in (-dx,dx): verts.append((x+c*xx-s*yy,y+s*xx+c*yy,z+zz))
    faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    mesh=bpy.data.meshes.new(name+'Mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(mat); mesh.update()
    obj=bpy.data.objects.new(name,mesh); col=bpy.data.collections.get('Asset_david_and_bonnie_brunner_farm_animal_hospital'); col.objects.link(obj)
    if bevel:
        mod=obj.modifiers.new('Soft edge','BEVEL'); mod.width=bevel; mod.segments=2
        obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return obj

def simple_material(name,color,metallic=0.0,roughness=.6):
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color=(*color,1); mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF'); bsdf.inputs['Base Color'].default_value=(*color,1); bsdf.inputs['Metallic'].default_value=metallic; bsdf.inputs['Roughness'].default_value=roughness
    return mat

def brunner_finish():
    global col
    name='david_and_bonnie_brunner_farm_animal_hospital'; col=bpy.data.collections.get('Asset_'+name); scene=bpy.context.scene
    shell=bpy.data.objects.get(name+'_GIS_outline_primary_shell'); assert shell is not None
    # The isolated official BEP image shows the actual one-story brick hospital:
    # a low flat-roof clinical/service wing, a small clay-tile lobby roof, a
    # glazed client entrance, a personnel door and a large vehicle opening. Details below
    # are scale cues; their exact positions/dimensions are not measured.
    bounds=shell.bound_box
    points=[shell.matrix_world @ Vector(v) for v in bounds]
    bbmin=[min(p[i] for p in points) for i in range(3)]; bbmax=[max(p[i] for p in points) for i in range(3)]
    # Source footprint vertex order/orientation is retained from the GIS shell.
    ring=[]
    # The shell stores the source ring twice: bottom vertices then top vertices.
    for v in shell.data.vertices[:len(shell.data.vertices)//2]:
        ring.append((v.co.x,v.co.y))
    n=len(ring); signed=sum(ring[i][0]*ring[(i+1)%n][1]-ring[(i+1)%n][0]*ring[i][1] for i in range(n))
    candidate=[]
    for i,(x,y) in enumerate(ring):
        u,v=ring[(i+1)%n]; dx=u-x; dy=v-y; length=math.hypot(dx,dy)
        if length<12: continue
        nx,ny=math.sin(math.atan2(dy,dx)),-math.cos(math.atan2(dy,dx))
        if signed<0: nx,ny=-nx,-ny
        # Public/client frontage faces south per construction context and faces the road edge.
        candidate.append((ny,length,i,x,y,u,v,nx,ny,math.atan2(dy,dx)))
    south_edges=[q for q in candidate if q[0]<-.75]
    front=max(south_edges,key=lambda q:q[1]) if south_edges else min(candidate,key=lambda q:(q[0],-q[1]))
    _,length,front_index,x,y,u,v,nx,ny,angle=front
    dx=u-x; dy=v-y; ux=dx/length; uy=dy/length
    def p(t, inward=0.0): return (x+dx*t-nx*inward, y+dy*t-ny*inward)
    base=.35; walltop=6.2
    brick=simple_material(name+'_photo_brick',(.48,.17,.105),0,.82)
    stone=simple_material(name+'_photo_limestone',(.72,.68,.59),0,.72)
    dark=simple_material(name+'_photo_dark_metal',(.10,.12,.12),.55,.42)
    glass=simple_material(name+'_photo_glazing',(.12,.25,.29),.25,.24)
    door=simple_material(name+'_service_door_gray',(.29,.31,.30),.25,.52)
    tile=simple_material(name+'_clay_roof_tile',(.42,.105,.065),.08,.78)
    # More realistic standing seam/parapet cap on the clinic wing.
    for edge_i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
        L=math.dist(a,b)
        if L<3: continue
        ang=math.atan2(b[1]-a[1],b[0]-a[0]); mx=(a[0]+b[0])*.5; my=(a[1]+b[1])*.5
        add_box(f'BRFM_photo_roof_edge_{edge_i}',(mx,my,walltop+.08),(L,.26,.18),dark,ang)
    # The source photo shows a raised brick reception wing at the southwest
    # footprint return, a narrow window row on its west wall, and a recessed
    # entrance on its south wall. Use the two official GIS edges for placement.
    rec_i=10; rx,ry=ring[rec_i]; rux,ruy=ring[(rec_i+1)%n]
    rdx,rdy=rux-rx,ruy-ry; rlen=math.hypot(rdx,rdy); rangle=math.atan2(rdy,rdx)
    rnx,rny=math.sin(rangle),-math.cos(rangle)
    if signed<0: rnx,rny=-rnx,-rny
    def rp(t,outward=0.0): return (rx+rdx*t+rnx*outward,ry+rdy*t+rny*outward)
    # Raised masonry reception volume over the GIS-defined west/south wing.
    roof_len=rlen+.45; roof_depth=14.8; eave_z=7.12; ridge_z=8.48
    volume_x,volume_y=rp(.5,-roof_depth/2)
    add_box('BRFM_raised_reception_brick_volume',(volume_x,volume_y,6.66),(rlen+.12,roof_depth-.4,.92),brick,rangle)
    rcx,rcy=rp(.5,.15)  # front eave line, with a small exterior overhang
    # Recessed glazed portal near the main-clinic junction; dark reveal is set
    # outside the glazing and the leaves sit behind the exterior brick plane.
    lobby_t=.14; lx,ly=rp(lobby_t,0)
    add_box('BRFM_public_entry_recess',(lx-rnx*.05,ly-rny*.05,2.05),(3.55,.12,3.2),dark,rangle)
    entry_glass=simple_material(name+'_entry_glass',(.07,.32,.40),.12,.22)
    add_box('BRFM_public_entry_glass',(lx+rnx*.07,ly+rny*.07,2.05),(3.35,.07,3.0),entry_glass,rangle,.02)
    for side in (-1,1):
        add_box(f'BRFM_public_entry_door_leaf_{side}',(lx+rdx/rlen*side*.54+rnx*.11,ly+rdy/rlen*side*.54+rny*.11,1.6),(1.0,.06,2.45),dark,rangle,.012)
    for side in (-1,1):
        add_box(f'BRFM_entry_brick_jamb_{side}',(lx+rdx/rlen*side*2.08+rnx*.06,ly+rdy/rlen*side*2.08+rny*.06,2.1),(.34,.24,3.85),brick,rangle)
    add_box('BRFM_entry_brick_header',(lx+rnx*.06,ly+rny*.06,4.06),(4.55,.24,.34),brick,rangle)
    # Four-sided hip roof: two trapezoid slopes and two triangular end hips.
    half=roof_len/2; depth=roof_depth; ridge_half=2.15
    def roof_point(t,d,z): return (rcx+rdx/rlen*t-rnx*d,rcy+rdy/rlen*t-rny*d,z)
    verts=[roof_point(-half,0,eave_z),roof_point(half,0,eave_z),roof_point(half,depth,eave_z),roof_point(-half,depth,eave_z),roof_point(-ridge_half,depth/2,ridge_z),roof_point(ridge_half,depth/2,ridge_z)]
    faces=[(0,1,5,4),(3,4,5,2),(0,4,3),(1,2,5)]
    roofmesh=bpy.data.meshes.new('BRFM_reception_hip_roofMesh'); roofmesh.from_pydata(verts,[],faces); roofmesh.materials.append(tile); roofmesh.update()
    roofobj=bpy.data.objects.new('BRFM_entry_clay_tile_hip_roof_estimated',roofmesh); col.objects.link(roofobj)
    # Fine tile courses follow each of the four roof planes without changing
    # the source-visible hip silhouette.
    for k in range(1,8):
        frac=k/8; d=depth/2*frac; z=eave_z+(ridge_z-eave_z)*frac
        for side in (-1,1):
            t0=-half+(half-ridge_half)*frac if side<0 else ridge_half+(half-ridge_half)*frac
            t1=-t0
            a=roof_point(t0,d,z); b=roof_point(t1,d,z)
            mesh_obj(f'BRFM_tile_course_front_{side}_{k}',[a,b,(b[0],b[1],b[2]+.025),(a[0],a[1],a[2]+.025)],[(0,1,2,3)],tile,col)
    # Seven slim windows are visible on the left-hand reception frontage in
    # the source pixels, before the recessed portal. Their dimensions are estimates.
    for j in range(7):
        wt=.37+j*.085; cx,cy=rp(wt,.08)
        add_box(f'BRFM_reception_window_reveal_{j+1}',(cx,cy,2.72),(.78,.16,2.35),dark,rangle)
        add_box(f'BRFM_reception_narrow_window_{j+1}',(cx+rnx*.10,cy+rny*.10,2.72),(.56,.08,2.05),glass,rangle)
    # The reference photo shows a conventional service door and one larger
    # vehicle opening; dimensions remain estimated from the perspective image.
    px,py=p(.74,-.20)
    add_box('BRFM_service_personnel_door_recess',(px+nx*.10,py+ny*.10,1.95),(2.0,.14,3.35),dark,angle)
    add_box('BRFM_service_personnel_door',(px+nx*.26,py+ny*.26,1.95),(1.65,.16,3.05),door,angle)
    px,py=p(.39,-.20)
    add_box('BRFM_service_bay_dark_recess',(px+nx*.10,py+ny*.10,2.38),(7.0,.14,4.15),dark,angle)
    add_box('BRFM_service_bay_overhead_door_1',(px+nx*.26,py+ny*.26,2.3),(6.2,.16,3.75),door,angle)
    for k in range(1,9):
        zz=.48+k*.42
        add_box(f'BRFM_service_door_rib_1_{k}',(px+nx*.36,py+ny*.36,zz),(6.05,.07,.035),stone,angle)
    for side in (-1,1):
        add_box(f'BRFM_service_bay_jamb_1_{side}',(px+ux*side*3.63,py+uy*side*3.63,2.45),(.25,.38,4.35),stone,angle)
    add_box('BRFM_service_bay_header_1',(px+nx*.15,py+ny*.15,4.7),(7.4,.4,.28),stone,angle)
    # The source photo shows a horizontal louver on the short right-side return.
    lou_i=5; qx,qy=ring[lou_i]; qex,qey=ring[(lou_i+1)%n]
    qdx,qdy=qex-qx,qey-qy; qlen=math.hypot(qdx,qdy); qa=math.atan2(qdy,qdx)
    qnx,qny=math.sin(qa),-math.cos(qa)
    if signed<0: qnx,qny=-qnx,-qny
    lt=.83; lxv=qx+qdx*lt+qnx*.10; lyv=qy+qdy*lt+qny*.10
    add_box('BRFM_right_return_louver_recess',(lxv,lyv,2.85),(2.25,.18,2.35),dark,qa)
    for k in range(8):
        add_box(f'BRFM_right_return_louver_slats_{k+1}',(lxv+qnx*.12,lyv+qny*.12,1.92+k*.26),(2.0,.08,.09),stone,qa)
    # Low pale roof-mounted units: presence is supported by Pepper's aerial; exact count/location are estimates.
    rooftop=simple_material(name+'_roof_equipment_light',(.70,.72,.70),.18,.56)
    for j,(t,d) in enumerate(((.48,16),(.82,12)),1):
        px,py=p(t,d)
        add_box(f'BRFM_roof_hvac_unit_{j}',(px,py,6.95),(3.2,2.2,1.35),rooftop,angle,.08)
        add_box(f'BRFM_roof_hvac_louver_{j}',(px,py-ny*1.12,6.95), (2.5,.06,.65),dark,angle)
    # Correct palette of the generic generator based on the building-specific
    # emergency plan photograph; maintain source-backed but estimated detail.
    for mat in bpy.data.materials:
        if mat.name.startswith(name+'_textured_masonry'):
            mat.diffuse_color=(.40,.11,.065,1)
            mat.use_nodes=True; nt=mat.node_tree; bsdf=nt.nodes.get('Principled BSDF')
            if bsdf:
                bsdf.inputs['Roughness'].default_value=.82
                # Keep the material's subtle procedural color variation; the
                # brick courses are represented by the source-backed belts,
                # avoiding a projection that rotates across shell faces.
                bsdf.inputs['Base Color'].default_value=(.40,.11,.065,1)
        elif mat.name.startswith(name+'_cut_stone'):
            mat.diffuse_color=(.72,.68,.59,1)
    # Keep the source-visible reception window row modeled above. Remove generic
    # windows, pale vertical piers, and unsupported tall roof stacks/screens.
    for obj in list(col.objects):
        object_name=obj.name
        if object_name.startswith(('BRFM_glazed_bay_','BRFM_mullion_','BRFM_sill_','BRFM_facade_pier_','BRFM_roof_exhaust_stack_','BRFM_roof_mechanical_screen','BRFM_roof_hvac_louver_')):
            bpy.data.objects.remove(obj,do_unlink=True)
    # Replace generic full-name sign with a compact source-identity sign.
    generic_entry_prefixes=('BRFM_main_entrance_glazed_door','BRFM_entry_portal_','BRFM_entry_lintel','BRFM_entry_canopy','BRFM_facade_identity_sign','BRFM_entry_step_')
    for obj in list(col.objects):
        if obj.name.startswith(generic_entry_prefixes): bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.object.text_add(location=(lx+rnx*.16,ly+rny*.16,4.05)); sign=bpy.context.object; sign.name='BRFM_facility_identity_sign'; sign.data.body='ENTRANCE'; sign.data.size=.36; sign.data.extrude=.012; sign.data.align_x='CENTER'; sign.data.materials.append(stone); sign.rotation_euler=(math.radians(90),0,0)
    for c in list(sign.users_collection): c.objects.unlink(sign)
    col.objects.link(sign)
    roof_material=bpy.data.materials.get(name+'_roof_membrane')
    if roof_material and len(shell.data.polygons)>1:
        if roof_material.name not in shell.data.materials: shell.data.materials.append(roof_material)
        roof_index=list(shell.data.materials).index(roof_material)
        shell.data.polygons[1].material_index=roof_index
    # Reopen validation and final renderer are separate post-save steps in the
    # validator script; this pass makes the asset deterministic and evidence-rich.
    scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1400; scene.render.resolution_y=920; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(EV,name+'_overview.png')
    scene.view_settings.exposure=.45
    scene.camera.location=(bbmax[0]+77,bbmin[1]-84,66)
    target=Vector(((bbmin[0]+bbmax[0])*.5,(bbmin[1]+bbmax[1])*.5,3.2))
    scene.camera.rotation_euler=(target-Vector(scene.camera.location)).to_track_quat('-Z','Y').to_euler(); scene.camera.data.lens=42
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,name+'.blend'))
    bpy.ops.render.render(write_still=True)
    # Re-aim the same camera to document the recognizable client/service facade.
    scene.render.filepath=os.path.join(EV,name+'_facade_detail.png')
    front_mid=Vector(((x+u)*.5,(y+v)*.5,3.6))
    scene.camera.location=(front_mid.x+nx*92,front_mid.y+ny*92,24.0); scene.camera.data.lens=42
    target=front_mid; scene.camera.rotation_euler=(target-Vector(scene.camera.location)).to_track_quat('-Z','Y').to_euler()
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,name+'.blend'))
    evidence_path=os.path.join(EV,name+'_evidence.json')
    with open(evidence_path,encoding='utf-8') as f: evidence=json.load(f)
    evidence.setdefault('revision_history',[]).append({
        'date':'2026-10-27',
        'review_request':'Restore missing detailed library as a dedicated reproducible asset; replace generic two-story massing cues with current building-specific source evidence.',
        'geometry_edits':['Kept the estimated 6.2 m one-story service shell and the official GIS FID 408 footprint/origin.','Added the photo-visible reception-frontage window row, a recessed entry, a raised brick reception volume, and a four-sided tile hip roof over the reception wing.','Removed unsupported generic facade piers and tall rooftop stacks/screens, and added the source-visible right-return louver. Service-door and architectural dimensions remain estimates.'],
        'source_interpretation':'Purdue BEP photo pixels directly support the reception window row, raised brick entry wing, four-sided clay-tile hip, recessed double-door portal, service bay and right-return louver. Rooftop detail remains restrained because the Farm Animal Hospital is mostly cropped in the available aerial.',
        'footprint_and_origin':'Official GIS shell and manifest local origin retained.'})
    evidence.setdefault('validation',{}).update({
        'overview_preview':os.path.relpath(os.path.join(EV,name+'_overview.png'),ROOT).replace('/','\\'),
        'facade_detail_preview':os.path.relpath(os.path.join(EV,name+'_facade_detail.png'),ROOT).replace('/','\\'),
        'saved_source_library':True,
        'final_object_count':len(col.all_objects),
        'estimated_wall_height_m':walltop,
        'modeled_principal_levels':1})
    with open(evidence_path,'w',encoding='utf-8') as f: json.dump(evidence,f,indent=2)
    print('BRUNNER_FINAL',len(col.all_objects),bbmin,bbmax,flush=True)

def main():
    d=json.load(open(GIS,encoding='utf-8'))
    feature=d['feature'] if 'feature' in d else next(f for f in d['features'] if f.get('attributes',{}).get('BLDG_ABBR')=='BRFM')
    build('BRFM',feature)
    brunner_finish()

if __name__=='__main__': main()



