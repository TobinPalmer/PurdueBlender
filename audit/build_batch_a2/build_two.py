import bpy,json,math,os
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'));OUT=os.path.join(ROOT,'modular','buildings');EV=os.path.dirname(__file__)
SX=111412.84*math.cos(math.radians(40.4274));SY=111040.0
DATA={
'MSEE':dict(id='materials_science_and_electrical_engineering_msee',name='Materials Science and Electrical Engineering (MSEE)',stories=4,h=15.0,style='academic',facade=(.40,.19,.12),stone=(.68,.65,.57),glass=(.13,.29,.34),metal=(.20,.23,.24),roof=(.24,.25,.24)),
'NWCP':dict(id='northwest_chiller_plant',name='Northwest Chiller Plant',stories=2,h=10.5,style='industrial',facade=(.47,.48,.45),stone=(.57,.57,.53),glass=(.12,.22,.25),metal=(.30,.33,.33),roof=(.25,.27,.26))}

def mat(name,c,r=.65,m=0,scale=30,b=.08):
 x=bpy.data.materials.new(name);x.diffuse_color=(*c,1);x.use_nodes=True;n=x.node_tree.nodes;l=x.node_tree.links;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=r;p.inputs['Metallic'].default_value=m
 tc=n.new('ShaderNodeTexCoord');no=n.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=scale;no.inputs['Detail'].default_value=3;ra=n.new('ShaderNodeValToRGB');ra.color_ramp.elements[0].color=(*(v*.82 for v in c),1);ra.color_ramp.elements[1].color=(*(min(1,v*1.15) for v in c),1);l.new(tc.outputs['Generated'],no.inputs['Vector']);l.new(no.outputs['Fac'],ra.inputs['Fac']);l.new(ra.outputs['Color'],p.inputs['Base Color']);bu=n.new('ShaderNodeBump');bu.inputs['Strength'].default_value=b;bu.inputs['Distance'].default_value=.03;l.new(no.outputs['Fac'],bu.inputs['Height']);l.new(bu.outputs['Normal'],p.inputs['Normal']);return x

def box(name,loc,dims,ma,col,ang=0):
 x,y,z=loc;dx,dy,dz=[v*.5 for v in dims];c=math.cos(ang);s=math.sin(ang);v=[]
 for zz in (-dz,dz):
  for yy in (-dy,dy):
   for xx in (-dx,dx):v.append((x+c*xx-s*yy,y+s*xx+c*yy,z+zz))
 f=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
 me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(v,[],f);me.materials.append(ma);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);return o

def mesh(name,vs,fs,ma,col):
 me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(vs,[],fs);me.materials.append(ma);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);return o

def centroid(q):
 a=cx=cy=0
 for (x,y),(u,v) in zip(q,q[1:]+q[:1]):t=x*v-u*y;a+=t;cx+=(x+u)*t;cy+=(y+v)*t
 return (cx/(3*a),cy/(3*a)) if abs(a)>1e-8 else (sum(x for x,y in q)/len(q),sum(y for x,y in q)/len(q))

def camera_render(code,p,col,h,local,bounds):
 scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1050;scene.render.resolution_y=850;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
 scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.34,.39,.45,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
 minx,maxx,miny,maxy=bounds;wx=maxx-minx;wy=maxy-miny
 if code=='MSEE':camloc=(minx-wx*.85,miny-wy*.38,h*1.48)
 else:camloc=(maxx+wx*.72,miny-wy*1.0,h*2.05)
 bpy.ops.object.camera_add(location=camloc);cam=bpy.context.object;cam.name='PreviewCamera_'+p['id'];target=Vector((0,0,h*.43));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=56 if code=='MSEE' else 50;scene.camera=cam
 for k,(loc,power,size) in enumerate([((wx*.2,-wy*.55,h*2.6),max(18000,wx*wy*4),max(wx,wy)*.8),((-wx*.7,wy*.25,h*1.7),max(9000,wx*wy*2),max(wx,wy)*.65)]):
  bpy.ops.object.light_add(type='AREA',location=loc);li=bpy.context.object;li.name=f'PreviewLight_{k}_{p["id"]}';li.data.energy=power;li.data.shape='DISK';li.data.size=size;li.rotation_euler=(Vector((0,0,h*.4))-li.location).to_track_quat('-Z','Y').to_euler()
 scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.35 if code=='MSEE' else -.25

def build(code,f,rawpath,refs):
 p=DATA[code];name=p['id'];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for c in list(bpy.data.collections):
  if c.name!='Collection':bpy.data.collections.remove(c)
 root=bpy.context.scene.collection
 for c in list(root.children):
  if c.name=='Collection':root.children.unlink(c)
 col=bpy.data.collections.new('Asset_'+name);root.children.link(col);a=f['attributes'];ring=f['geometry']['rings'][0];geo=[((x+86.9137)*SX,(y-40.4274)*SY) for x,y in ring[:-1]];ox,oy=centroid(geo);q=[(x-ox,y-oy) for x,y in geo];n=len(q);signed=sum(q[i][0]*q[(i+1)%n][1]-q[(i+1)%n][0]*q[i][1] for i in range(n));minx=min(x for x,y in q);maxx=max(x for x,y in q);miny=min(y for x,y in q);maxy=max(y for x,y in q);wx=maxx-minx;wy=maxy-miny
 facade=mat(name+'_facade',p['facade'],.75,0,36,.12);stone=mat(name+'_cast_stone',p['stone'],.68,0,30,.08);glass=mat(name+'_glazing',p['glass'],.16,.24,8,.02);metal=mat(name+'_painted_metal',p['metal'],.4,.55,22,.04);roof=mat(name+'_roofing',p['roof'],.63,.1,44,.1);inside=mat(name+'_schematic_interior',(.63,.61,.55),.82,0,22,.04);floor=mat(name+'_interior_floor',(.33,.35,.34),.75,0,40,.06)
 h=p['h'];z0=.3;lh=(h-z0)/p['stories'];v=[(x,y,z0) for x,y in q]+[(x,y,h) for x,y in q];faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];shell=mesh(name+'_official_GIS_shell',v,faces,facade,col);shell['GIS_FID']=a['FID'];shell['height']='estimated; GIS story count and published descriptions are not elevation survey'
 # Perimeter trim and fenestration; MSEE is brick with punched windows and metal accents.
 for i,(x,y) in enumerate(q):
  u,v=q[(i+1)%n];dx=u-x;dy=v-y;L=math.hypot(dx,dy)
  if L<3.8:continue
  ang=math.atan2(dy,dx);nx=math.sin(ang);ny=-math.cos(ang)
  if signed<0:nx,ny=-nx,-ny
  if L>6:
   box(f'{code}_stringcourse_{i}',((x+u)/2,(y+v)/2,h*.68),(L,.14,.24),stone,col,ang)
  count=max(1,int((L-2)/(2.6 if code=='MSEE' else 4.2)));stride=(L-2)/count
  if code=='MSEE':
   for lev in range(p['stories']):
    for j in range(count):
     t=1+(j+.5)*stride;cx=x+dx*t/L+nx*.10;cy=y+dy*t/L+ny*.10;ww=min(1.9,stride*.62);wh=min(1.95,lh*.6);cz=z0+lh*(lev+.5)
     box(f'MSEE_window_{i}_{lev}_{j}',(cx,cy,cz),(ww,.17,wh),glass,col,ang)
     for sd in (-1,1):box(f'MSEE_mullion_{i}_{lev}_{j}_{sd}',(cx+math.cos(ang)*sd*ww*.5,cy+math.sin(ang)*sd*ww*.5,cz),(.06,.22,wh+.08),metal,col,ang)
     box(f'MSEE_sill_{i}_{lev}_{j}',(cx,cy,cz-wh*.5-.08),(ww+.16,.23,.12),stone,col,ang)
  else:
   # Chiller plant's lower walls are predominantly louver panels, not office glazing.
   for j in range(count):
    t=1+(j+.5)*stride;cx=x+dx*t/L+nx*.13;cy=y+dy*t/L+ny*.13
    ww=min(3.0,stride*.74);wh=max(2.0,h*.39)
    box(f'NWCP_acoustic_louver_bank_{i}_{j}',(cx,cy,z0+wh*.52),(ww,.22,wh),metal,col,ang)
    for k in range(1,8):box(f'NWCP_louver_blade_{i}_{j}_{k}',(cx,cy,z0+wh*k/8),(ww,.27,.075),stone,col,ang)
 # Main public entrance on MSEE west-facing Northwestern Ave frontage, south-facing service access at utility plant.
 edges=[]
 for i,(x,y) in enumerate(q):
  u,v=q[(i+1)%n];L=math.hypot(u-x,v-y);ang=math.atan2(v-y,u-x);nx=math.sin(ang);ny=-math.cos(ang)
  if signed<0:nx,ny=-nx,-ny
  if L>6:edges.append((nx,ny,L,i,x,y,u,v,ang))
 front=min(edges,key=lambda z:(z[0] if code=='MSEE' else z[1],-z[2])) if edges else None
 if front:
  nx,ny,L,i,x,y,u,v,ang=front;cx=(x+u)/2+nx*.18;cy=(y+v)/2+ny*.18
  if code=='MSEE':
   # The documented two-storey Max W. Brown Atrium: glazed full-height bays, roof skylight, and public entry.
   atrw=min(L*.58,22);atrh=min(h*.74,8.2);acz=z0+atrh*.52
   box('MSEE_Max_W_Brown_two_story_glazed_atrium',(cx,cy,acz),(atrw,.22,atrh),glass,col,ang)
   for k in range(1,9):box(f'MSEE_atrium_mullion_{k}',(cx+math.cos(ang)*(-atrw/2+atrw*k/9),cy+math.sin(ang)*(-atrw/2+atrw*k/9),acz),(.08,.28,atrh),metal,col,ang)
   for z in (z0+atrh*.36,z0+atrh*.68):box(f'MSEE_atrium_transom_{z:.1f}',(cx,cy,z),(atrw,.28,.09),metal,col,ang)
   box('MSEE_atrium_roof_skylight',(cx,cy+ny*1.5,z0+atrh),(atrw*.78,3.0,.16),glass,col,ang)
   # doors and stone header below atrium
   box('MSEE_primary_glazed_doors',(cx,cy,z0+1.55),(4.0,.22,3.1),glass,col,ang)
   box('MSEE_entry_stone_header',(cx,cy,z0+3.3),(5.3,.48,.26),stone,col,ang)
  else:
   box('NWCP_service_double_door',(cx,cy,z0+1.6),(3.0,.22,3.2),glass,col,ang)
   box('NWCP_service_canopy',(cx,cy,z0+3.5),(4.4,1.1,.2),metal,col,ang)
 # Perimeter flat roof parapet
 for i,(x,y) in enumerate(q):
  u,v=q[(i+1)%n];L=math.hypot(u-x,v-y)
  if L>2:box(f'{code}_parapet_cap_{i}',((x+u)/2,(y+v)/2,h+.10),(L,.32,.22),stone,col,math.atan2(v-y,u-x))
 tris=tessellate_polygon([[Vector((x,y,0)) for x,y in q]])
 mesh(name+'_flat_roof_surface',[(x,y,h-.1) for x,y in q],[tuple(map(int,t)) for t in tris],roof,col)
 if code=='MSEE':
  # Raised, low roof monitor ties the atrium to its tall east-facing glazing.
  box('MSEE_atrium_roof_monitor',(0,wy*.20,h+.85),(wx*.3,2.8,1.45),glass,col,.02)
  for lev in range(p['stories']):
   zz=z0+lev*lh+.12;box(f'MSEE_schematic_floor_{lev}',(0,0,zz),(wx*.5,wy*.52,.13),floor,col)
   box(f'MSEE_schematic_atrium_void_edge_{lev}',(0,wy*.13,zz+lh*.47),(wx*.12,wy*.16,.12),stone,col)
   box(f'MSEE_schematic_lab_zone_{lev}',(-wx*.18,-wy*.15,zz+1.2),(wx*.16,wy*.12,2.4),inside,col)
  # Short glazed connector stubs are omitted because their attachment endpoints were not survey-checked.
  note='Documented open two-storey atrium, lab wings and two skyways. Local atrium and interior zones are interpretive; skyway endpoints omitted pending exact geometry.'
 else:
  # Mechanical yard and rooftop equipment: package plant, rooftop fans, headers and safety rails.
  box('NWCP_roof_equipment_screen',(.20*wx,.10*wy,h+.55),(wx*.55,wy*.32,1.05),metal,col)
  for i in range(5):
   x=minx+wx*(.22+.12*i);y=miny+wy*.18
   # cooling cells / fan housings
   box(f'NWCP_roof_cooling_cell_{i+1}',(x,y,h+1.72),(max(2,wx*.1),max(2,wy*.13),2.3),stone,col)
   box(f'NWCP_roof_fan_grille_{i+1}',(x,y,h+2.90),(max(1.6,wx*.075),max(1.6,wy*.09),.12),metal,col)
   # concentric fan hub and radial blades as high-contrast top plate
   box(f'NWCP_fan_hub_{i+1}',(x,y,h+3.0),(.45,.45,.2),glass,col)
  # exposed insulated headers and branch pipes; deliberately separate pipe-like mesh boxes.
  for k in range(3):
   box(f'NWCP_roof_chilled_water_header_{k}',(0,miny+wy*(.72+k*.055),h+1.3), (wx*.70,.35,.35),glass,col)
  for k in range(4):
   xx=minx+wx*(.28+k*.12);box(f'NWCP_vertical_pipe_riser_{k}',(xx,miny+wy*.65,h*.56),(.27,.27,h*.92),glass,col)
  # schematic machine-room interior (explicitly not an as-built room layout)
  interior=bpy.data.collections.new('NWCP_SCHEMATIC_INTERIOR_NOT_AS_BUILT');col.children.link(interior)
  for i in range(2):
   box(f'NWCP_schematic_floor_{i}',(0,0,z0+i*5.0),(wx*.54,wy*.54,.16),floor,interior)
   for j in range(3):
    xx=-wx*.18+j*wx*.18;box(f'NWCP_schematic_chiller_{i}_{j}',(xx,0,z0+i*5+1.5),(wx*.12,wy*.14,2.7),inside,interior)
    box(f'NWCP_schematic_chiller_pipe_{i}_{j}',(xx,wy*.12,z0+i*5+2.65),(wx*.14,.18,.22),glass,interior)
  note='Industrial rooftop plant equipment is a typology-based reconstruction; exact chiller cell count, pipe routing, and interior layout remain unverified.'
  # service-yard safety bollards and fence panels
  for j in range(5):
   xx=minx+wx*(.20+.12*j);yy=miny-.8
   box(f'NWCP_bollard_{j}',(xx,yy,.65),(.20,.20,1.3),stone,col)
 # all buildings get a marked schematic interior partition/core, never presented as surveyed
 if code=='MSEE':
  interior=bpy.data.collections.new('MSEE_SCHEMATIC_INTERIOR_NOT_AS_BUILT');col.children.link(interior)
  for lev in range(p['stories']):
   box(f'MSEE_interior_floor_{lev}',(0,0,z0+lev*lh+.08),(wx*.52,wy*.52,.14),floor,interior)
   box(f'MSEE_interior_core_{lev}',(wx*.18,-wy*.12,z0+lev*lh+1.3),(wx*.1,wy*.1,2.6),inside,interior)
   box(f'MSEE_interior_studio_partition_{lev}',(-wx*.16,0,z0+lev*lh+1.3),(.12,wy*.27,2.6),inside,interior)
  note='Schematic floor slabs, atrium void cue, lab and student-collaboration zones; not an as-built plan. Official archive supports an open two-storey atrium, laboratories and skyways.'
 # sign, explicit building identity
 if front:
  nx,ny,L,i,x,y,u,v,ang=front;cx=(x+u)/2+nx*.25;cy=(y+v)/2+ny*.25
  bpy.ops.object.text_add(location=(cx,cy,z0+3.8));t=bpy.context.object;t.name=code+'_building_identity_label';t.data.body='MSEE | Materials & Electrical Engineering' if code=='MSEE' else 'NORTHWEST CHILLER PLANT';t.data.size=.55;t.data.extrude=.008;t.rotation_euler=(math.pi/2,0,ang-math.pi/2);t.data.materials.append(metal)
  for c in list(t.users_collection):c.objects.unlink(t)
  col.objects.link(t)
 else:note='No dominant frontage selected; entry facade location is unverified.'
 bounds=[minx,maxx,miny,maxy];camera_render(code,p,col,h,q,bounds);preview=os.path.join(EV,name+'_preview.png');bpy.context.scene.render.filepath=preview;out=os.path.join(OUT,name+'.blend');bpy.ops.wm.save_as_mainfile(filepath=out);bpy.ops.render.render(write_still=True)
 # Save the exact upstream GIS record alongside a complete provenance note.
 json.dump(f,open(rawpath,'w'),indent=2)
 ev={'building_id':name,'replaces_massing_id':'massing_materials_science_and_electrical_engineering_msee_003a4e2' if code=='MSEE' else 'massing_northwest_chiller_plant_nwcp_2b32fa6','library':os.path.relpath(out,ROOT),'collection':col.name,'retrieved_date':'2026-10-24','gis_source':{'provider':'Purdue BuildingShapes ArcGIS FeatureServer, layer 0','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','feature_id':a['FID'],'building_code':a.get('BLDG_ABBR'),'official_name':a.get('BUILDING_N'),'address':a.get('ADDRESS'),'crs':'Feature snapshot EPSG:4326; campus local axes derive from project approximate tangent-plane conversion, not surveyed coordinates','attributes':{k:a.get(k) for k in ('NUM_LEVELS','Extrution','Elevation','Shape__Area','Shape__Length')},'original_snapshot':os.path.relpath(rawpath,ROOT)},'references':refs,'street_view':'Not independently inspected in this pass; availability/location not confirmed.','geometry':{'origin_local_m':[ox,oy],'axes':'X east, Y north, Z up; meters','footprint_vertices':len(q),'footprint_bounds_local_m':bounds,'height_m':h,'height_status':'estimated from GIS floor count plus official descriptions; not an elevation survey','detailed_features':note,'exterior_materials':'procedural noise/color-ramp/bump networks; no external image dependencies','interior':'schematic only, explicitly named NOT_AS_BUILT; no construction plans used.'},'validation':{'preview':os.path.relpath(preview,ROOT),'object_count':len(col.all_objects),'collection':col.name,'library_saved':True},'uncertainties':['Interior plans and precise facade dimensions are not available from the referenced sources.','Street View has not been independently checked.','GIS footprint/address/code matched, but no field survey performed.']}
 json.dump(ev,open(os.path.join(EV,name+'_evidence.json'),'w'),indent=2);print('SAVED',name,'fid',a['FID'],'origin',ox,oy,'objects',len(col.all_objects),flush=True)

def main():
 for code,filename,refs in [
 ('MSEE','batchC_msee_official_footprint.json',[{'provider':'Purdue Archives and Special Collections','url':'https://archives.lib.purdue.edu/agents/corporate_entities/703','detail':'1988 facility; open two-storey glass atrium, laboratories, and two pedestrian skyways.'},{'provider':'Purdue Engineering Imprints','url':'https://engineering.purdue.edu/Imprints/fall-2018/materials-and-electrical-engineering-atrium-gets-a-major-upgrade','detail':'2017-2020 student-centered Max W. Brown Atrium renovation and new public front door.'},{'provider':'Purdue Engineering Space Master Plan','url':'https://engineering.purdue.edu/Engr/AboutUs/MeetDean/Vision-2030/space-master-plan','detail':'Modern student-centered program within MSEE.'}]),
 ('NWCP','batchC_northwest_chiller_official_footprint.json',[{'provider':'Purdue Engineering Research Expo handout','url':'https://engineering.purdue.edu/Herrick/information/2013%20Research%20Expo%20handout.pdf','detail':'Identifies Northwest Chiller Plant as a campus cooling-capacity facility.'},{'provider':'Purdue Board of Trustees capital project record','url':'https://www.purdue.edu/treasurer/finance/wp-content/uploads/2023/04/Northwest-Chiller-Plant-System-Improvements-B-1-23-2-04.pdf','detail':'2023 system-improvement project confirms operating utility function; precise exterior geometry not depicted in this record.'}])]:
  d=json.load(open(os.path.join(ROOT,'audit',filename),encoding='utf-8'));f=next(x for x in d['features'] if x.get('attributes',{}).get('BLDG_ABBR')==code);raw=os.path.join(EV,DATA[code]['id']+'_gis_feature.json');build(code,f,raw,refs)
if __name__=='__main__':main()



