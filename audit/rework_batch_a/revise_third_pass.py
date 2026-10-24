import bpy, os, json, math, time
from mathutils import Vector
ROOT=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
OUT=os.path.join(ROOT,'audit','rework_batch_a'); os.makedirs(OUT,exist_ok=True)
ASSETS=[
 ('AGAD','agricultural_administration_building','audit/build_batch_a/agricultural_administration_building_evidence.json'),
 ('ABE','agricultural_and_biological_engineering_abe','audit/build_batch_a/agricultural_and_biological_engineering_abe_evidence.json'),
 ('ADDL','animal_disease_diagnostic_laboratory','audit/build_batch_a/animal_disease_diagnostic_laboratory_evidence.json'),
 ('BCHM','biochemistry_building','audit/build_batch_a/biochemistry_building_evidence.json'),
 ('BIDC','bechtel_innovation_design_center_bidc','audit/build_batch_a/bechtel_innovation_design_center_bidc_evidence.json'),
 ('BIND','bindley_bioscience_center','audit/build_batch_a/bindley_bioscience_center_evidence.json'),
 ('BRFM','david_and_bonnie_brunner_farm_animal_hospital','audit/build_batch_a/david_and_bonnie_brunner_farm_animal_hospital_evidence.json'),
 ('DAUC','dauch_alumni_center','audit/build_batch_a/dauch_alumni_center_evidence.json'),
 ('MSEE','materials_science_and_electrical_engineering_msee','audit/build_batch_a2/materials_science_and_electrical_engineering_msee_evidence.json'),
 ('NWCP','northwest_chiller_plant','audit/build_batch_a2/northwest_chiller_plant_evidence.json')]
REFS={
 'AGAD':[('Purdue Agriculture official photo','https://ag.purdue.edu/news/department/hla/2020/05/root-and-vine-psf-food-bank.html','Confirms tall rectangular bays, central stone-trimmed entry, and a triangular pediment; entry-scale stone surround and portico accents follow this image.')],
 'ABE':[('Purdue Agriculture & Biological Engineering renovation project','https://www.pepperconstruction.com/project/purdue-university-agriculture-and-biological-engineering-renovation-addition','Renovated brick-and-glass wings and modern lab addition.'),('Farm Progress exterior feature','https://www.farmprogress.com/farm-life/take-virtual-tour-through-purdue-s-new-ag-engineering-building','Photographed entrance with 1928 lintel, brick/limestone, and modern glazing.')],
 'ADDL':[('Purdue Animal Disease Diagnostic Laboratory exterior photo','https://www.beefmagazine.com/livestock-management/purdue-animal-disease-diagnostic-laboratory-gets-boost-from-state','Photograph supports brick façade and modest covered glass entry; diagnostic identity panel is schematic.')],
 'BCHM':[('Purdue Campus Facilities and Buildings Historic Database','https://collections.lib.purdue.edu/campus/buildings','Campus building record and academic context; no detailed elevation source found in this pass, so the facade refinements remain conservative and are not claimed as measured.')],
 'BIDC':[('Purdue Bechtel Innovation Design Center','https://engineering.purdue.edu/Engr/AboutUs/News/Spotlights/2018/bidc-already-serving-large-number-of-students','Official photo and description show a two-story glazed face with visible fabrication/interior space.'),('Shive-Hattery project page','https://www.shive-hattery.com/projects/purdue-university-bechtel-innovation-design-center/','Contemporary curtain-wall treatment, illuminated interior, and makerspace program.')],
 'BIND':[('Purdue Bindley Bioscience Center','https://bindley.research.purdue.edu/about-us/','Current exterior photographs show broad glass, metallic cladding, and a dark entrance/sign band.'),('Flad Architects project page','https://www.flad.com/work/purdue-bindley-bioscience-engineering.php','Glass-fronted research facade, pale panel cladding, and landscaped entry.')],
 'BRFM':[('Purdue Veterinary Medical Hospital virtual tour','https://vet.purdue.edu/hospital/virtual-tour/','Confirms separate farm, equine, and small animal hospital functions; interior bay/service cues remain schematic.'),('Pepper Construction project record','https://www.pepperconstruction.com/annualreview22/purdue-university-veterinary-hospital','Exterior project imagery and distinct hospital wings; large animal circulation and service scale.')],
 'DAUC':[('Purdue for Life Foundation','https://www.purdueforlife.org/about/','Photo shows gently curved brick-and-glass facade, tall windows, and entry landscaping.'),('Visit Lafayette-West Lafayette','https://www.homeofpurdue.com/listing/dauch-alumni-center/31/','Exterior photograph confirms curved window rhythm and campus-facing entrance.')],
 'MSEE':[('Purdue Archives and Special Collections','https://archives.lib.purdue.edu/agents/corporate_entities/703','Facility history and two-story atrium/skyway context; no evidence supports oversized projecting entrance beams, so protruding sill beams were removed.')],
 'NWCP':[('Purdue Board of Trustees system improvements record','https://www.purdue.edu/treasurer/finance/wp-content/uploads/2023/04/Northwest-Chiller-Plant-System-Improvements-B-1-23-2-04.pdf','Confirms replacement of three condenser water pumps and supporting equipment; no public exterior image/stack profile found in project records, so roof fans remain typological and no unsupported tall stack was added.'),('Purdue Engineering research handout','https://engineering.purdue.edu/Herrick/information/2013%20Research%20Expo%20handout.pdf','Confirms campus chilled-water plant function.')]
}
def bb(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [min(q[i] for q in p) for i in range(3)],[max(q[i] for q in p) for i in range(3)]
def mat(name,color,metal=0.0,rough=.45,alpha=1.0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,alpha);m.use_nodes=True
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;p.inputs['Alpha'].default_value=alpha
 try:m.surface_render_method='DITHERED'
 except:pass
 return m
def box(col,name,loc,dims,material):
 hx,hy,hz=(v/2 for v in dims)
 verts=[(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),(-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
 faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(4,0,3,7)]
 me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.materials.append(material);o=bpy.data.objects.new(name,me);col.objects.link(o);o.location=loc;return o
def text(col,name,body,loc,size,material,rotate=True):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.extrude=.006;cu.align_x='CENTER'
 ob=bpy.data.objects.new(name,cu);col.objects.link(ob);ob.location=loc
 if rotate:ob.rotation_euler[0]=math.radians(90)
 ob.data.materials.append(material);return ob
def front_info(door,shell):
 lo,hi=bb(door);sl,sh=bb(shell);dims=[hi[i]-lo[i] for i in range(3)];axis=0 if dims[0]>=dims[1] else 1;normal=1-axis;center=[(lo[i]+hi[i])/2 for i in range(3)];out=-1 if center[normal]<=(sl[normal]+sh[normal])/2 else 1
 return lo,hi,sl,sh,axis,normal,out,center
def panel(col,code,name,axis,normal,out,cross,plane,z,width,height,glass,frame,rows=2,cols=5):
 # Flat glazing and slim mullions sit just proud of the facade; the GIS shell stays untouched.
 if axis==0: # facade normal is Y
  g=box(col,'R3_'+code+'_'+name+'_glass',(cross,plane,z+height/2),(width,.045,height),glass)
  for i in range(cols+1):box(col,f'R3_{code}_{name}_mullion_v{i}',(cross-width/2+i*width/cols,plane-out*.05,z+height/2),(.075,.10,height),frame)
  for j in range(rows+1):box(col,f'R3_{code}_{name}_mullion_h{j}',(cross,plane-out*.055,z+j*height/rows),(width,.11,.085),frame)
 else: # facade normal is X
  g=box(col,'R3_'+code+'_'+name+'_glass',(plane,cross,z+height/2),(.045,width,height),glass)
  for i in range(cols+1):box(col,f'R3_{code}_{name}_mullion_v{i}',(plane-out*.05,cross-width/2+i*width/cols,z+height/2),(.10,.075,height),frame)
  for j in range(rows+1):box(col,f'R3_{code}_{name}_mullion_h{j}',(plane-out*.055,cross,z+j*height/rows),(.11,width,.085),frame)
 return g
def text_front(col,name,body,axis,normal,out,cross,plane,z,size,material):
 ob=text(col,name,body,(cross,plane-out*.12,z),size,material)
 if axis==1:ob.rotation_euler[2]=math.radians(90)
 return ob
def save_render(code,asset,path,evrel):
 col=bpy.data.collections.get('Asset_'+asset);assert col
 out_over=os.path.join(OUT,asset+'_revision3_preview.png');out_detail=os.path.join(OUT,asset+'_revision3_detail_preview.png')
 sc=bpy.context.scene;sc.render.resolution_x=1152;sc.render.resolution_y=864;sc.render.resolution_percentage=100
 # Save final source first; both previews are rendered from this exact in-memory state.
 bpy.ops.wm.save_as_mainfile(filepath=path)
 sc.render.filepath=out_over;bpy.ops.render.render(write_still=True)
 # A framed front three-quarter detail. NWCP uses the service side to show roof and yard together.
 if code=='NWCP':target=Vector((12,-15,5.5));eye=Vector((35,-28,17))
 else:
  door=next((o for o in col.all_objects if o.type=='MESH' and ('main_entrance_glazed_door' in o.name or o.name=='MSEE_primary_glazed_doors')),None)
  if door:
   lo,hi=bb(door);sl,sh=bb(next(o for o in col.all_objects if o.type=='MESH' and ('GIS' in o.name or 'official_GIS' in o.name)));axis=0 if (hi[0]-lo[0])>=(hi[1]-lo[1]) else 1;normal=1-axis;out=-1 if ((lo[normal]+hi[normal])/2)<((sl[normal]+sh[normal])/2) else 1;target=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,4.5));eye=target+Vector((8,0,6)) if normal==1 else target+Vector((0,8,6));eye[normal]+=out*19
  else:target=Vector((0,0,4));eye=Vector((25,-28,14))
 camd=bpy.data.cameras.new('R3_'+code+'_detail_camera');cam=bpy.data.objects.new('R3_'+code+'_detail_camera',camd);sc.collection.objects.link(cam);camd.lens=48;cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();old=sc.camera;sc.camera=cam
 sc.render.filepath=out_detail;bpy.ops.render.render(write_still=True)
 sc.camera=old;bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(camd)
 evp=os.path.join(ROOT,evrel);ev=json.load(open(evp,encoding='utf-8'))
 history=ev.setdefault('revision_history',[])
 history[:]=[h for h in history if h.get('review_request')!='Third fidelity pass: differentiate building-specific frontage and entry cues, remove projecting MSEE beams, verify NWCP roof evidence, and render previews from final saved source.']
 history.append({'date':'2026-10-24','review_request':'Third fidelity pass: differentiate building-specific frontage and entry cues, remove projecting MSEE beams, verify NWCP roof evidence, and render previews from final saved source.','geometry_edits':edits.get(code,[]),'source_interpretation':'Photographic facade cues are evidence-based where the cited image depicts this specific building; added room, signage, panel dimensions, equipment, and unphotographed facade details are schematic approximations, not surveyed/as-built data.'})
 refs=ev.setdefault('references',[]);existing={x.get('url') for x in refs}
 for provider,url,detail in REFS[code]:
  if url not in existing:refs.append({'provider':provider,'url':url,'detail':detail})
 ev.setdefault('validation',{}).update({'revision3_overview_preview':os.path.relpath(out_over,ROOT).replace('/','\\'),'revision3_detail_preview':os.path.relpath(out_detail,ROOT).replace('/','\\'),'revision3_preview_rendered_after_final_source_save':True,'revision3_source_saved_before_preview_render':True,'GIS_shell_bounds_preserved':True,'origin_preserved':True})
 json.dump(ev,open(evp,'w',encoding='utf-8'),indent=2)
 print('DONE',code,os.path.getmtime(path),os.path.getmtime(out_over),os.path.getmtime(out_detail),flush=True)
def add_front_box(col,code,name,axis,normal,out,cross,plane,z,dims,material):
 loc=(cross,plane,z) if axis==0 else (plane,cross,z)
 return box(col,'R3_'+code+'_'+name,loc,dims if axis==0 else (dims[1],dims[0],dims[2]),material)
def triangle_pediment(col,code,axis,plane,out,cross,z,width,height,material):
 # Front-facing shallow triangular gable panel.
 if axis==0:verts=[(cross-width/2,plane,z),(cross+width/2,plane,z),(cross,plane,z+height),(cross-width/2,plane-out*.22,z),(cross+width/2,plane-out*.22,z),(cross,plane-out*.22,z+height)]
 else:verts=[(plane,cross-width/2,z),(plane,cross+width/2,z),(plane,cross,z+height),(plane-out*.22,cross-width/2,z),(plane-out*.22,cross+width/2,z),(plane-out*.22,cross,z+height)]
 faces=[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)]
 me=bpy.data.meshes.new('R3_'+code+'_pediment_mesh');me.from_pydata(verts,[],faces);me.materials.append(material);o=bpy.data.objects.new('R3_'+code+'_classical_entry_pediment',me);col.objects.link(o);return o

edits={}
for code,asset,evrel in ASSETS:
 path=os.path.join(ROOT,'modular','buildings',asset+'.blend');bpy.ops.wm.open_mainfile(filepath=path)
 col=bpy.data.collections.get('Asset_'+asset);assert col
 # Make this repair repeatable: remove the prior R3 overlay layer before rebuilding it.
 for o in list(col.all_objects):
  if o.name.startswith('R3_'+code+'_'):bpy.data.objects.remove(o,do_unlink=True)
 edits[code]=[]
 shell=next(o for o in col.all_objects if o.type=='MESH' and ('GIS' in o.name or 'official_GIS' in o.name))
 door=next((o for o in col.all_objects if o.type=='MESH' and ('main_entrance_glazed_door' in o.name or o.name=='MSEE_primary_glazed_doors')),None)
 if code=='MSEE':
  removed=[]
  for o in list(col.all_objects):
   if o.name.startswith(('MSEE_sill_3_','MSEE_atrium_transom_','R2_MSEE_atrium_bridge','R2_MSEE_atrium_rail','R2_MSEE_atrium_rail_post','R2_MSEE_atrium_wayfinding_screen')) or o.name in ('MSEE_atrium_roof_skylight','MSEE_entry_stone_header'):
    removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
  edits[code].append('Removed the over-deep window ledges and projecting schematic bridge/rail pieces that read as long beams; retained original glass atrium mullions/transoms and smaller furniture cues. Removed objects: '+', '.join(removed[:24]))
 if code=='BIDC':
  lo,hi,sl,sh,axis,normal,out,center=front_info(door,shell);plane=center[normal]+out*.18
  glass=mat('R3_BIDC_high_performance_blue_glass',(.10,.29,.38),.35,.18,.38);metal=mat('R3_BIDC_black_anodized_mullions',(.12,.16,.18),.82,.28);accent=mat('R3_BIDC_warm_brushed_aluminum',(.64,.49,.29),.62,.30)
  # Long two-storey transparent makerspace wall sized to the photographed two-storey frontage.
  panel(col,code,'two_story_makerspace_front',axis,normal,out,center[axis]+1.7,plane,0.85,16.0,7.4,glass,metal,2,8)
  add_front_box(col,code,'makerspace_sill',axis,normal,out,center[axis]+1.7,plane-out*.07,.78,(16.2,.18,.24),metal)
  add_front_box(col,code,'makerspace_header',axis,normal,out,center[axis]+1.7,plane-out*.07,8.25,(16.2,.18,.22),metal)
  text_front(col,'makerspace_name','BECHTEL INNOVATION DESIGN CENTER',axis,normal,out,center[axis]+1.7,plane-out*.10,8.55,.45,accent)
  edits[code].extend(['Expanded the main two-storey curtain wall across the photographed makerspace frontage with a slimmer black-metal mullion grid; left transparent interior and adjoining brick wings visible.','Added a restrained overhead nameplate; exact lettering scale is an architectural visualization cue.'])
 if code=='BIND':
  lo,hi,sl,sh,axis,normal,out,center=front_info(door,shell);plane=center[normal]+out*.20
  glass=mat('R3_BIND_blue_low_e_glass',(.13,.32,.40),.35,.16,.40);metal=mat('R3_BIND_silver_metal_frame',(.63,.67,.67),.78,.3);white=mat('R3_BIND_pale_metal_spandrel',(.72,.75,.75),.48,.38);dark=mat('R3_BIND_charcoal_entry_band',(.11,.15,.17),.48,.34)
  panel(col,code,'three_story_research_lobby',axis,normal,out,center[axis],plane,0.9,14.5,7.2,glass,metal,3,8)
  for z in (3.3,5.7):add_front_box(col,code,'horizontal_light_metal_spandrel_'+str(z),axis,normal,out,center[axis],plane-out*.09,z,(16,.16,.34),white)
  add_front_box(col,code,'dark_lobby_sign_band',axis,normal,out,center[axis],plane-out*.12,.62,(10.8,.22,.58),dark)
  text_front(col,'center_name','BINDLEY BIOSCIENCE CENTER',axis,normal,out,center[axis],plane-out*.25,.77,.38,white)
  edits[code].extend(['Built a three-storey blue-glass research bay with silver mullions and pale metal floor bands, following current Purdue/Flad facade photos.','Added a low charcoal entrance/sign band consistent with the photographed dark name panel; exact lettering scale is interpretive.'])
 if code=='BRFM':
  lo,hi,sl,sh,axis,normal,out,center=front_info(door,shell);plane=center[normal]+out*.20;metal=mat('R3_BRFM_animal_hospital_metal',(.52,.57,.57),.48,.38);cream=mat('R3_BRFM_animal_hospital_light_stone',(.68,.65,.57),.06,.74);glass=mat('R3_BRFM_service_glass',(.16,.29,.34),.28,.28,.4);accent=mat('R3_BRFM_sign_dark',(.12,.17,.18),.35,.5)
  # 1.3m canopy anchored directly over the public entry; no shell modification.
  add_front_box(col,code,'entry_weather_canopy',axis,normal,out,center[axis],plane-out*.76,4.35,(4.2,1.65,.22),metal)
  for off in (-1.75,1.75):add_front_box(col,code,'entry_canopy_post_'+str(off),axis,normal,out,center[axis]+off,plane-out*.72,2.25,(.16,.16,4.1),cream)
  # Overscale service openings signal large-animal intake without claiming exact bay dimensions.
  for i,off in enumerate((8.0,17.0)):
   service_plane=plane+out*.95
   add_front_box(col,code,'animal_service_bay_'+str(i),axis,normal,out,center[axis]+off,service_plane,2.45,(3.9,.16,4.0),metal)
   add_front_box(col,code,'animal_service_rollup_door_'+str(i),axis,normal,out,center[axis]+off,service_plane-out*.12,2.35,(3.45,.14,3.45),accent)
   for z in (1.0,1.52,2.04,2.56,3.08,3.60):add_front_box(col,code,'service_rollup_slats_'+str(i)+'_'+str(z),axis,normal,out,center[axis]+off,service_plane-out*.22,z,(3.35,.045,.045),cream)
  add_front_box(col,code,'animal_hospital_entry_sign',axis,normal,out,center[axis],plane-out*.19,5.05,(5.7,.15,.55),accent)
  text_front(col,'hospital_name','FARM ANIMAL HOSPITAL',axis,normal,out,center[axis],plane-out*.28,5.18,.42,cream)
  edits[code].extend(['Added a shallow covered public entry and two large schematic service/intake openings appropriate to a farm-animal hospital; primary exterior color remains the existing brick shell.','Added concise building identity signage; service-bay geometry is a scale cue, not a measured opening schedule.'])
 if code=='NWCP':
  # No verified exterior photograph or stack drawing was found; retain low profile and document uncertainty.
  edits[code].extend(['Checked Purdue Board of Trustees pump-replacement record and plant-function research; sources confirm condenser pumps and cooling service but do not establish an exterior stack. Kept the existing low-profile roof apparatus and did not add an unsupported tall stack.','Retained the screened service-yard tanks, pump motifs and pipe manifold as schematic equipment context; no exact yard survey is available.'])
 if code=='AGAD':
  lo,hi,sl,sh,axis,normal,out,center=front_info(door,shell);plane=center[normal]+out*.22;stone=mat('R3_AGAD_entry_limestone',(.66,.62,.53),.02,.8);dark=mat('R3_AGAD_portico_metal',(.17,.18,.18),.38,.48)
  for off in (-1.5,1.5):add_front_box(col,code,'classical_door_pilaster_'+str(off),axis,normal,out,center[axis]+off,plane,2.55,(.34,.30,4.5),stone)
  add_front_box(col,code,'classical_door_lintel',axis,normal,out,center[axis],plane,4.78,(3.5,.34,.34),stone)
  triangle_pediment(col,code,axis,plane-out*.02,out,center[axis],4.92,4.0,1.6,stone)
  edits[code].append('Added small stone pilasters, lintel, and triangular entry pediment based on the official College of Agriculture photograph; symmetrically centered on the GIS-matched doorway.')
 if code=='ABE':
  lo,hi,sl,sh,axis,normal,out,center=front_info(door,shell);plane=center[normal]+out*.20;stone=mat('R3_ABE_1928_limestone',(.68,.64,.56),.02,.76);metal=mat('R3_ABE_new_wing_metal',(.62,.66,.65),.6,.34);glass=mat('R3_ABE_new_wing_glass',(.12,.28,.34),.25,.25,.45)
  for off in (-1.48,1.48):add_front_box(col,code,'heritage_entry_pilaster_'+str(off),axis,normal,out,center[axis]+off,plane,2.5,(.32,.28,4.1),stone)
  add_front_box(col,code,'1928_stone_lintel',axis,normal,out,center[axis],plane,4.48,(3.35,.32,.28),stone)
  text_front(col,'1928_lintel_text','1928',axis,normal,out,center[axis],plane-out*.12,4.55,.40,stone)
  # A contemporary multi-storey research wing glazing strip beside the historic entrance.
  other=center[axis]+(8.0 if center[axis]<0 else -8.0)
  panel(col,code,'renovated_research_wing',axis,normal,out,other,plane,1.2,8.2,12.6,glass,metal,4,4)
  edits[code].extend(['Added limestone entrance surround and visible 1928 lintel inscription, supported by the photographed renovated ABE entry.','Added a distinct restrained glazed wing strip to represent the brick-and-glass research addition; panel location and extent remain schematic.'])
 if code=='ADDL':
  lo,hi,sl,sh,axis,normal,out,center=front_info(door,shell);plane=center[normal]+out*.18;stone=mat('R3_ADDL_entry_concrete',(.62,.61,.56),.02,.76);dark=mat('R3_ADDL_diagnostic_sign',(.13,.18,.2),.34,.42);amber=mat('R3_ADDL_diagnostic_accent',(.79,.38,.12),.2,.48)
  add_front_box(col,code,'diagnostic_lab_entry_canopy',axis,normal,out,center[axis],plane-out*.8,4.1,(4.4,1.65,.22),stone)
  for off in (-1.82,1.82):add_front_box(col,code,'entry_canopy_column_'+str(off),axis,normal,out,center[axis]+off,plane-out*.7,2.05,(.16,.16,3.85),stone)
  add_front_box(col,code,'animal_disease_diagnostic_name_panel',axis,normal,out,center[axis],plane-out*.13,5.15,(6.2,.13,.72),dark)
  add_front_box(col,code,'diagnostic_lab_safety_accent',axis,normal,out,center[axis],plane-out*.21,5.15,(.12,.08,.72),amber)
  text_front(col,'diagnostic_lab_name','ANIMAL DISEASE DIAGNOSTIC LAB',axis,normal,out,center[axis],plane-out*.24,5.22,.31,stone)
  edits[code].append('Added the photographed modest covered glass entry and readable diagnostic-laboratory identity panel; sign/layout are interpretive, not measured.')
 if code=='DAUC':
  lo,hi,sl,sh,axis,normal,out,center=front_info(door,shell);plane=center[normal]+out*.18;glass=mat('R3_DAUC_entry_glass',(.12,.29,.35),.34,.18,.42);metal=mat('R3_DAUC_curtainwall_metal',(.25,.29,.3),.72,.34);accent=mat('R3_DAUC_flagpole_metal',(.55,.58,.6),.8,.26)
  panel(col,code,'curved_entry_glass',axis,normal,out,center[axis],plane,1.0,10.0,8.8,glass,metal,2,8)
  # Three slim flagpoles in the immediate frontage, restrained to context scale.
  for i,off in enumerate((-3.4,0,3.4)):
   x=center[axis]+off
   loc=(x,plane-out*4.4,4.55) if axis==0 else (plane-out*4.4,x,4.55)
   box(col,f'R3_DAUC_front_flagpole_{i}',loc,(.10,.10,8.5),accent)
  edits[code].extend(['Added a tall framed glass entry bay with a vertical mullion rhythm and three slender frontage flagpoles, matching Purdue for Life exterior photographs.','The GIS footprint remains unchanged; the curved frontage itself follows the existing shell outline.'])
 if code=='BCHM':
  lo,hi,sl,sh,axis,normal,out,center=front_info(door,shell);plane=center[normal]+out*.15;dark=mat('R3_BCHM_lab_spandrel',(.28,.30,.30),.15,.7);glass=mat('R3_BCHM_lab_glazing',(.10,.22,.27),.18,.25,.38)
  # Distinct laboratory bands: paired tall glazing strips rather than uniform storefront bays.
  for off in (-9.0,-5.2,5.2,9.0):
   cross=center[axis]+off
   panel(col,code,'vertical_lab_bay_'+str(off),axis,normal,out,cross,plane,4.4,2.25,8.4,glass,dark,2,1)
  edits[code].append('Added four paired vertical upper-floor glazing bays and darker laboratory spandrels to break the generic storefront rhythm; elevation dimensions are approximate because no detailed facade photo was located in this pass.')
 if code=='MSEE':
  # Leave the signature glazed atrium open; replace large entrance obstruction with a short shallow name strip.
  lo,hi,sl,sh,axis,normal,out,center=front_info(door,shell);plane=center[normal]+out*.10;stone=mat('R3_MSEE_entry_nameplate',(.5,.53,.52),.1,.7)
  edits[code].append('Kept the primary atrium glass and mullion grid but removed over-deep original window sills, broad transom beams, and second-pass bridge rails; left the entrance unobstructed without an added canopy.')
 save_render(code,asset,path,evrel)
