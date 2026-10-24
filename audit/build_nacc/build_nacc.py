import bpy,json,math,os
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'));OUT=os.path.join(ROOT,'modular','buildings');EV=os.path.dirname(__file__)
SRC=os.path.join(ROOT,'audit','batchC_nacc_official_footprint.json')
SX=111412.84*math.cos(math.radians(40.4274));SY=111040.0

def material(name,color,rough=.72,metal=0,scale=32,bump=.1):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 tc=n.new('ShaderNodeTexCoord');no=n.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=scale;no.inputs['Detail'].default_value=3;ra=n.new('ShaderNodeValToRGB');ra.color_ramp.elements[0].color=(*(v*.83 for v in color),1);ra.color_ramp.elements[1].color=(*(min(1,v*1.13) for v in color),1);l.new(tc.outputs['Generated'],no.inputs['Vector']);l.new(no.outputs['Fac'],ra.inputs['Fac']);l.new(ra.outputs['Color'],p.inputs['Base Color']);bu=n.new('ShaderNodeBump');bu.inputs['Strength'].default_value=bump;bu.inputs['Distance'].default_value=.03;l.new(no.outputs['Fac'],bu.inputs['Height']);l.new(bu.outputs['Normal'],p.inputs['Normal']);return m

def box(name,loc,dims,ma,col,ang=0):
 x,y,z=loc;dx,dy,dz=(q*.5 for q in dims);c=math.cos(ang);s=math.sin(ang);v=[]
 for zz in (-dz,dz):
  for yy in (-dy,dy):
   for xx in (-dx,dx):v.append((x+c*xx-s*yy,y+s*xx+c*yy,z+zz))
 fs=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)];me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(v,[],fs);me.materials.append(ma);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);return o

def mesh(name,v,f,ma,col):
 me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(v,[],f);me.materials.append(ma);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);return o

def centroid(q):
 area=cx=cy=0
 for (x,y),(u,v) in zip(q,q[1:]+q[:1]):t=x*v-u*y;area+=t;cx+=(x+u)*t;cy+=(y+v)*t
 return (cx/(3*area),cy/(3*area)) if abs(area)>1e-8 else (sum(x for x,y in q)/len(q),sum(y for x,y in q)/len(q))

def text(name,body,loc,size,ma,col,rot=0):
 bpy.ops.object.text_add(location=loc);o=bpy.context.object;o.name=name;o.data.body=body;o.data.size=size;o.data.extrude=.008;o.rotation_euler=(math.pi/2,0,rot-math.pi/2);o.data.materials.append(ma)
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);return o

def main():
 d=json.load(open(SRC,encoding='utf-8'));f=next(x for x in d['features'] if x['attributes'].get('BLDG_ABBR')=='NACC');a=f['attributes'];name='native_american_educational_and_cultural_center_nacc';bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for c in list(bpy.data.collections):
  if c.name!='Collection':bpy.data.collections.remove(c)
 root=bpy.context.scene.collection
 for c in list(root.children):
  if c.name=='Collection':root.children.unlink(c)
 col=bpy.data.collections.new('Asset_'+name);root.children.link(col);geo=[((x+86.9137)*SX,(y-40.4274)*SY) for x,y in f['geometry']['rings'][0][:-1]];ox,oy=centroid(geo);q=[(x-ox,y-oy) for x,y in geo];n=len(q);signed=sum(q[i][0]*q[(i+1)%n][1]-q[(i+1)%n][0]*q[i][1] for i in range(n));mnx=min(x for x,y in q);mxx=max(x for x,y in q);mny=min(y for x,y in q);mxy=max(y for x,y in q);wx=mxx-mnx;wy=mxy-mny
 siding=material(name+'_white_weathered_wood_siding',(.79,.79,.73),.78,0,26,.12);trim=material(name+'_white_trim',(.91,.89,.82),.65,0,25,.06);shingle=material(name+'_charcoal_composition_shingle',(.20,.22,.22),.83,0,60,.16);glass=material(name+'_residential_window_glass',(.15,.27,.31),.18,.13,9,.015);foundation=material(name+'_painted_foundation',(.30,.31,.30),.8,0,40,.1);door=material(name+'_wood_door',(.30,.22,.15),.62,0,30,.1);interior=material(name+'_schematic_room',(.72,.69,.59),.86,0,22,.05);ifloor=material(name+'_schematic_floor',(.39,.37,.33),.8,0,35,.06);landscape=material(name+'_gravel_drive',(.43,.43,.40),.95,0,50,.16);garageMat=material(name+'_garage_siding',(.72,.72,.67),.83,0,28,.1)
 z0=.32;eave=6.55;ridge=9.2;story=2.85;# GIS wall outline is retained exactly; upper wood frame and lower foundation
 verts=[(x,y,-2.35) for x,y in q]+[(x,y,eave) for x,y in q];fs=[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];shell=mesh(name+'_official_GIS_wall_shell',verts,fs,siding,col);shell['GIS_FID']=a['FID'];shell['height_status']='two stories per Purdue Building Emergency Plan; roof form/height modeled estimate'
 # visible foundation skirt under wall perimeter
 for i,(x,y) in enumerate(q):
  u,v=q[(i+1)%n];dx=u-x;dy=v-y;L=math.hypot(dx,dy)
  if L<.5:continue
  ang=math.atan2(dy,dx);box(f'NACC_foundation_face_{i}',((x+u)/2,(y+v)/2,.08),(L,.16,.55),foundation,col,ang)
  # Horizontal wood clapboard runs, a restrained repeating lap-siding detail.
  nx=math.sin(ang);ny=-math.cos(ang)
  if signed<0:nx,ny=-nx,-ny
  for row in range(1,26):
   z=.45+row*.24
   box(f'NACC_clapboard_{i}_{row}',((x+u)/2+nx*.10,(y+v)/2+ny*.10,z),(L,.055,.035),trim,col,ang)
 # Roof gable: main ridge follows long building dimension; two sloped planes with overhang.
 cx=(mnx+mxx)/2;cy=(mny+mxy)/2;halfX=wx*.5+.45;edgeY=wy*.5+.45
 # Broad roof surfaces slope from ridge to eaves. Separate planes preserve crisp gable.
 mesh('NACC_roof_south_slope',[(cx-halfX,cy, ridge),(cx+halfX,cy,ridge),(cx+halfX,cy-edgeY,eave-.15),(cx-halfX,cy-edgeY,eave-.15)],[(0,1,2,3)],shingle,col)
 mesh('NACC_roof_north_slope',[(cx+halfX,cy,ridge),(cx-halfX,cy,ridge),(cx-halfX,cy+edgeY,eave-.15),(cx+halfX,cy+edgeY,eave-.15)],[(0,1,2,3)],shingle,col)
 box('NACC_ridge_cap',(cx,cy,ridge+.04),(2*halfX,.35,.22),trim,col)
 # Gable end infill triangular panels at west/east ends.
 for sgn in (-1,1):
  x=cx+sgn*halfX
  vtx=[(x,cy-edgeY,eave-.18),(x,cy+edgeY,eave-.18),(x,cy,ridge-.12),(x+sgn*.10,cy-edgeY,eave-.18),(x+sgn*.10,cy+edgeY,eave-.18),(x+sgn*.10,cy,ridge-.12)]
  mesh(f'NACC_gable_end_{sgn}',vtx,[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)],siding,col)
 # contrasting fascia/eaves
 box('NACC_east_fascia',(mxx+.35,cy,eave-.03),(.22,wy+.9,.28),trim,col);box('NACC_west_fascia',(mnx-.35,cy,eave-.03),(.22,wy+.9,.28),trim,col)
 # Principal direction: east face (toward Fifth Street) is the verified front; rear door faces alley.
 front_angle=0.0
 # Residential six-over-six double-hung windows with trim and shutters, separated by floors.
 for i,(x,y) in enumerate(q):
  u,v=q[(i+1)%n];dx=u-x;dy=v-y;L=math.hypot(dx,dy)
  if L<2.3:continue
  ang=math.atan2(dy,dx);nx=math.sin(ang);ny=-math.cos(ang)
  if signed<0:nx,ny=-nx,-ny
  # avoid overfilling small angled porch/bay edges
  count=max(1,int((L-1.0)/2.5));stride=(L-1.0)/count
  for lev in range(2):
   z=z0+lev*story+1.45
   for j in range(count):
    t=.5+(j+.5)*stride;wx0=min(1.25,stride*.52);cx0=x+dx*t/L+nx*.14;cy0=y+dy*t/L+ny*.14
    box(f'NACC_double_hung_sash_{i}_{lev}_{j}',(cx0,cy0,z),(wx0,.15,1.38),glass,col,ang)
    # Thick white surround, sill, header, center rail and a 2x2 divided-light grid.
    for side in (-1,1):
     px=cx0+math.cos(ang)*side*(wx0*.5+.09);py=cy0+math.sin(ang)*side*(wx0*.5+.09)
     box(f'NACC_window_casing_{i}_{lev}_{j}_{side}',(px,py,z),(.12,.21,1.58),trim,col,ang)
     box(f'NACC_window_shutter_{i}_{lev}_{j}_{side}',(px+math.cos(ang)*side*.18,py+math.sin(ang)*side*.18,z),(.18,.11,1.5),door,col,ang)
    box(f'NACC_window_head_{i}_{lev}_{j}',(cx0,cy0,z+.79),(wx0+.32,.22,.14),trim,col,ang)
    box(f'NACC_window_sill_{i}_{lev}_{j}',(cx0,cy0,z-.79),(wx0+.38,.28,.17),trim,col,ang)
    box(f'NACC_window_muntin_vertical_{i}_{lev}_{j}',(cx0,cy0-.10,z),(.045,.20,1.30),trim,col,ang)
    box(f'NACC_window_muntin_horizontal_{i}_{lev}_{j}',(cx0,cy0-.11,z),(wx0-.12,.20,.045),trim,col,ang)
 # small white porch on Fifth Street/east elevation and main front door
 px=mxx+.35;py=cy-wy*.10
 box('NACC_fifth_street_front_door',(px,py,z0+1.05),(.18,1.05,2.12),door,col)
 box('NACC_front_door_trim_left',(px+.15,py-.62,z0+1.05),(.28,.14,2.34),trim,col);box('NACC_front_door_trim_right',(px+.15,py+.62,z0+1.05),(.28,.14,2.34),trim,col);box('NACC_front_door_header',(px+.15,py,z0+2.22),(.28,1.38,.16),trim,col)
 # covered entry stoop/porch, two light posts and handrail
 box('NACC_front_porch_deck',(px+1.5,py,z0+.18),(2.8,2.8,.3),trim,col)
 for j,dy in enumerate((-1.18,1.18)):
  box(f'NACC_porch_column_{j}',(px+2.4,py+dy,z0+1.55),(.20,.20,2.75),trim,col)
 box('NACC_front_porch_roof',(px+2.25,py,z0+3.15),(1.65,3.15,.22),shingle,col)
 box('NACC_front_porch_fascia',(px+2.25,py,z0+3.02),(1.72,3.22,.18),trim,col)
 # official accessibility door/ramp on front toward parking lot, located on southern side (position estimated)
 box('NACC_parking_lot_access_door',(cx, mny-.12,z0+1.05),(1.05,.18,2.12),door,col)
 rampLen=5.2
 box('NACC_accessibility_ramp',(cx,mny-2.65,.34),(1.45,rampLen,.16),foundation,col)
 box('NACC_accessibility_entry_landing',(cx,mny-.25,.43),(2.15,1.25,.16),trim,col)
 for side in (-1,1):
  for j in range(4):box(f'NACC_ramp_handrail_post_{side}_{j}',(cx+side*.78,mny-4.9+j*1.4,.66),(.08,.08,.82),trim,col)
  box(f'NACC_ramp_handrail_{side}',(cx+side*.78,mny-2.65,.96),(.08,rampLen,.08),trim,col)
 # alley-facing rear door at kitchen, explicitly separate from main 5th Street entrance.
 box('NACC_alley_rear_kitchen_door',(mnx-.15,cy+.85,z0+1.02),(.18,1.0,2.05),door,col)
 box('NACC_alley_rear_door_casing',(mnx-.27,cy+.85,z0+2.12),(.25,1.34,.16),trim,col)
 # engraved-looking center plaque: institutional identifier, not a new cultural motif.
 box('NACC_name_plaque',(px+.24,py,z0+2.52),(.08,1.5,.45),foundation,col)
 # Detached, single-car storage garage in the rear yard; exact setback/azimuth is unverified.
 gx=mnx-5.4;gy=cy-2.4;gw=4.4;gd=3.5;ge=2.6;gr=3.55
 box('NACC_detached_single_car_storage_garage',(gx,gy,ge*.5),(gw,gd,ge),garageMat,col)
 box('NACC_garage_rollup_storage_door',(gx-gw*.5-.08,gy,1.35),(.12,2.7,2.1),foundation,col)
 # gable roof panels on the garage
 mesh('NACC_garage_roof_south',[(gx-gw*.6,gy,gr),(gx+gw*.6,gy,gr),(gx+gw*.6,gy-gd*.6,ge),(gx-gw*.6,gy-gd*.6,ge)],[(0,1,2,3)],shingle,col)
 mesh('NACC_garage_roof_north',[(gx+gw*.6,gy,gr),(gx-gw*.6,gy,gr),(gx-gw*.6,gy+gd*.6,ge),(gx+gw*.6,gy+gd*.6,ge)],[(0,1,2,3)],shingle,col)
 # A small gravel parking apron is a contextual hint; exact material extent omitted.
 box('NACC_gravel_parking_apron',(cx+4,mny-5,.04),(10,9,.08),landscape,col)
 # Realistic schematic interior zones derived from official room list, not surveyed plans.
 interiorcol=bpy.data.collections.new('NACC_SCHEMATIC_INTERIOR_NOT_AS_BUILT');col.children.link(interiorcol)
 for lev,z in [('basement',-2.25),('first_floor',.38),('second_floor',3.23)]:
  box('NACC_'+lev+'_floor_schematic',(cx,cy,z),(wx*.78,wy*.78,.13),ifloor,interiorcol)
 # basement furnace/main room + two smaller service rooms
 for nm,x,y,dx,dy,z in [('furnace_main',cx-.9,cy,wx*.3,wy*.55,-.85),('basement_small',cx+wx*.25,cy+wy*.12,wx*.18,wy*.22,-.8),('basement_large',cx+wx*.22,cy-wy*.2,wx*.24,wy*.24,-.8)]:box('NACC_schematic_'+nm,(x,y,z),(dx,.10,2.6),interior,interiorcol)
 # first floor living/welcome/map room front, kitchen at rear and restroom/core; partitions
 for nm,x,y,dx,dy in [('living_welcome_map',cx+wx*.22,cy,wx*.30,wy*.75),('kitchen',cx-wx*.22,cy-wy*.26,wx*.32,wy*.34),('restroom',cx-wx*.2,cy+wy*.27,wx*.24,wy*.19)]:box('NACC_first_floor_schematic_partition_'+nm,(x,y,1.75),(dx,.12,2.7),interior,interiorcol)
 # Second-floor computer lab/library/conference/offices/restroom partitions
 for nm,x,y,dx,dy in [('computer_lab',cx+wx*.2,cy+wy*.2,wx*.3,wy*.3),('library',cx-wx*.2,cy+wy*.2,wx*.3,wy*.28),('conference',cx+wx*.2,cy-wy*.2,wx*.3,wy*.30),('office',cx-wx*.2,cy-wy*.2,wx*.3,wy*.28),('restroom',cx,cy,wx*.14,wy*.14)]:box('NACC_second_floor_schematic_partition_'+nm,(x,y,4.65),(dx,.12,2.7),interior,interiorcol)
 # object metadata emphasizes interpretive limits and rooms corroborated by official BEP.
 shell['interior_status']='Schematic partitions from official room names; layout not as-built.';shell['garage_status']='Official Purdue plan confirms one-car storage garage; exact location/size estimated.'
 # camera/render, all preview-only objects remain outside the exported asset collection
 scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1100;scene.render.resolution_y=850;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.35,.41,.48,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
 camloc=(mxx+wx*1.0,mny-wy*1.15,10.2);bpy.ops.object.camera_add(location=camloc);cam=bpy.context.object;cam.name='PreviewCamera_NACC';target=Vector((0,0,3.3));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=48;scene.camera=cam
 for loc,power,size in [((wx*.2,-wy*.5,17),6000,18),((-wx*.7,wy*.3,12),3500,13)]:
  bpy.ops.object.light_add(type='AREA',location=loc);li=bpy.context.object;li.data.energy=power;li.data.shape='DISK';li.data.size=size;li.rotation_euler=(Vector((0,0,3))-li.location).to_track_quat('-Z','Y').to_euler()
 scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.4;preview=os.path.join(EV,name+'_preview.png');scene.render.filepath=preview;out=os.path.join(OUT,name+'.blend');bpy.ops.wm.save_as_mainfile(filepath=out);bpy.ops.render.render(write_still=True)
 raw=os.path.join(EV,name+'_gis_feature_927.json');json.dump({'provider':'Purdue University BuildingShapes ArcGIS FeatureServer','service_url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','retrieved_date':'2026-10-24','spatial_reference':d['spatialReference'],'feature':f},open(raw,'w'),indent=2)
 ev={'building_id':'massing_native_american_educational_and_cultural_center_nacc_faa0f59','detailed_asset_id':name,'file':os.path.relpath(out,ROOT),'collection':col.name,'scene':'Scene','retrieved_date':'2026-10-24','sources':[{'provider':'Purdue Office of Emergency Preparedness, NACC Building Emergency Plan','url':'https://www.purdue.edu/operations/emergency-preparedness/nacc/','observed':'former single-family white wood-frame house; two stories and basement; 3 entry/exit doors; east/front door to Fifth Street, accessible entrance/ramp toward parking, rear kitchen door toward alley; separate one-car storage garage; room names by floor; revised 2026-03-17.'},{'provider':'Purdue Native American Educational and Cultural Center','url':'https://purdue.edu/naecc/','observed':'official center identity/address at 903 Fifth Street; current page confirms facility name and use.'},{'provider':'Purdue BuildingShapes ArcGIS FeatureServer','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','feature_id':a['FID'],'building_code':a.get('BLDG_ABBR'),'address':a.get('ADDRESS'),'crs_service':'EPSG:4326 as recorded in checked-in snapshot; campus local coordinates are approximate local tangent-plane formula, not surveyed coordinates','attributes':{k:a.get(k) for k in ('NUM_LEVELS','Extrution','Elevation','Shape__Area','Shape__Length')},'raw_snapshot':os.path.relpath(raw,ROOT)}],'geometry':{'origin_local_xy_m':[ox,oy],'axes':'X east, Y north, Z up; meters','footprint_vertices':len(q),'footprint_local_bounds_m':[mnx,mxx,mny,mxy],'official_footprint_shell':'Matched FID 927 / NACC / 903 5th Street. GIS shell retained as footprint outline; first story count field conflicts with Purdue 2-story emergency plan, so official written description is used.','stories':'2 above grade plus basement per Purdue BEP','modeled_eaves_ridge_m':[eave,ridge],'height_status':'estimated; no measured elevation data located','exterior_details':'white painted weathered wood clapboard, contrasting trim, divided-light sash, porch, dark composition gable roof, three functional entry cues, accessible ramp and separately modeled storage garage. Architectural details beyond official plan are estimated, not field-measured.','garage':'Purdue confirms detached one-car storage garage; size and setback estimated.','interior':'Schematic living/welcome/map room, kitchen, restrooms, second-floor computer lab/library/conference/office zones, and basement furnace rooms based on official room list. Clearly separated in NACC_SCHEMATIC_INTERIOR_NOT_AS_BUILT; partitions are not an as-built floor plan.'},'materials':{'all_procedural_portable':True,'count':9,'texture_network':'Procedural noise/color ramp/bump; no image paths.'},'street_view':{'status':'not independently verified in this pass','note':'Official BEP contains address-linked Google Earth and describes doors/faces; no Street View panorama capture date is claimed.'},'validation':{'saved':True,'preview':os.path.relpath(preview,ROOT),'collection':col.name,'object_count':len(col.all_objects)},'uncertainties':['Roof pitch, exact window count and historic house style are estimates; no measured elevations or historic house photographs were found in the consulted sources.','The GIS level field reports 1 while Purdue emergency plan explicitly states two stories and basement; modeling follows the dated Purdue written description.','Garage footprint/setback and ramp geometry are estimated from the official text description.','Interior partitions are schematic, derived from room names only.']}
 json.dump(ev,open(os.path.join(EV,name+'_evidence.json'),'w'),indent=2);print('SAVED',out,'collection',col.name,'origin',ox,oy,'objects',len(col.all_objects),flush=True)
if __name__=='__main__':main()
