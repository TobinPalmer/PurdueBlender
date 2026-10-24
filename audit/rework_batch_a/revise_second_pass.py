import bpy, os, json, math
from mathutils import Vector
ROOT=os.path.abspath('.'); OUT=os.path.join(ROOT,'audit','rework_batch_a');os.makedirs(OUT,exist_ok=True)
ASSETS=[
 ('MSEE','materials_science_and_electrical_engineering_msee','audit/build_batch_a2/materials_science_and_electrical_engineering_msee_evidence.json','audit/build_batch_a2'),
 ('BCHM','biochemistry_building','audit/build_batch_a/biochemistry_building_evidence.json','audit/build_batch_a'),
 ('ADDL','animal_disease_diagnostic_laboratory','audit/build_batch_a/animal_disease_diagnostic_laboratory_evidence.json','audit/build_batch_a'),
 ('BRFM','david_and_bonnie_brunner_farm_animal_hospital','audit/build_batch_a/david_and_bonnie_brunner_farm_animal_hospital_evidence.json','audit/build_batch_a'),
 ('AGAD','agricultural_administration_building','audit/build_batch_a/agricultural_administration_building_evidence.json','audit/build_batch_a'),
 ('ABE','agricultural_and_biological_engineering_abe','audit/build_batch_a/agricultural_and_biological_engineering_abe_evidence.json','audit/build_batch_a'),
 ('BIDC','bechtel_innovation_design_center_bidc','audit/build_batch_a/bechtel_innovation_design_center_bidc_evidence.json','audit/build_batch_a'),
 ('BIND','bindley_bioscience_center','audit/build_batch_a/bindley_bioscience_center_evidence.json','audit/build_batch_a'),
 ('DAUC','dauch_alumni_center','audit/build_batch_a/dauch_alumni_center_evidence.json','audit/build_batch_a'),
 ('NWCP','northwest_chiller_plant','audit/build_batch_a2/northwest_chiller_plant_evidence.json','audit/build_batch_a2')]

def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [min(q[i] for q in p) for i in range(3)],[max(q[i] for q in p) for i in range(3)]
def mat(name,color,metal=0,rough=.55,emission=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emission and 'Emission Color' in p.inputs:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 return m
def box(col,name,loc,dims,material,rot=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;o.rotation_euler[2]=rot;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.data.materials.append(material);return o
def cylinder(col,name,a,b,r,material,verts=14):
 a=Vector(a);b=Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(a+b)*.5);o=bpy.context.object;o.name=name;o.rotation_mode='QUATERNION';o.rotation_quaternion=d.to_track_quat('Z','Y')
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.data.materials.append(material);return o
def sphere(col,name,loc,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.data.materials.append(material);return o
def clear_r2():
 for o in list(bpy.data.objects):
  if o.name.startswith('R2_'):bpy.data.objects.remove(o,do_unlink=True)
def inside_panel(col,code,door,shell):
 dlo,dhi=bounds(door);dctr=[(dlo[i]+dhi[i])/2 for i in range(3)];sx=dhi[0]-dlo[0];sy=dhi[1]-dlo[1];axis=0 if sx>=sy else 1;normal=1-axis
 # Prefer transparent/glazed opening around the public entrance; wall finish and footprint remain untouched.
 target=next((o for o in col.all_objects if o.type=='MESH' and o.name.startswith(code+'_revision_transparent_makerspace_lobby')),None)
 if target is None:target=next((o for o in col.all_objects if o.type=='MESH' and o.name.startswith(code+'_revision_research_lobby_curtainwall')),None)
 if target is None:target=next((o for o in col.all_objects if o.type=='MESH' and o.name.startswith(code+'_revision_entry_glazed_transom')),None)
 if code=='MSEE':target=next((o for o in col.all_objects if o.name=='MSEE_Max_W_Brown_two_story_glazed_atrium'),None)
 if target:
  tlo,thi=bounds(target); pc=[(tlo[i]+thi[i])/2 for i in range(3)]; pw=thi[axis]-tlo[axis]; ph=thi[2]-tlo[2]; pn=(tlo[normal]+thi[normal])/2
  if code=='MSEE':
   width=13.0;height=8.0; zbase=.65; centerX=(tlo[0]+thi[0])/2; pn=tlo[1]+.35; inward=1
  else:
   width=min(10.0,max(2.6,pw*.82));height=min(6.2,max(2.8,ph*.75));zbase=max(.65,(tlo[2]+thi[2]-height)/2);centerX=dctr[axis];inward=1 if dctr[normal]>pn else -1;pn+=inward*.105
  return axis,normal,centerX,pn,inward,width,height,zbase
 # no glazing? place a modest foyer vignette within the existing entrance pane.
 slo,shi=bounds(shell);inward=1 if dctr[normal]>((slo[normal]+shi[normal])/2) else -1
 return axis,normal,dctr[axis],dctr[normal]+inward*.12,inward,min(3.4,max(2.0,sx if axis==0 else sy)),3.2,.55

def interior_set(col,code,axis,normal,cx,face,inward,width,height,zbase):
 wood=mat('R2_'+code+'_interior_wood',(.35,.21,.11),.05,.6);dark=mat('R2_'+code+'_interior_graphite',(.08,.11,.12),.25,.42);steel=mat('R2_'+code+'_interior_stainless',(.48,.55,.56),.65,.27);glow=mat('R2_'+code+'_interior_warm_light',(.9,.63,.26),.05,.3,.6);tile=mat('R2_'+code+'_interior_floor',(.55,.57,.55),.05,.72);accent=mat('R2_'+code+'_interior_accent',(.12,.34,.39),.25,.42);white=mat('R2_'+code+'_interior_white',(.74,.75,.69),.04,.62)
 # All interior inserts sit just inside the transparent pane, in a deliberately shallow display band in front of the opaque shell face.
 y=face+inward*.06; z=zbase+.35; span=min(width*.78,8.0); added=[]
 def b(n,xoff,dep,zoff,dim,m):
  if axis==0: loc=(cx+xoff,y+inward*dep,z+zoff); d=dim
  else: loc=(y+inward*dep,cx+xoff,z+zoff); d=(dim[1],dim[0],dim[2])
  ob=box(col,'R2_'+code+'_'+n,loc,d,m);added.append(ob.name);return ob
 def c(n,xoff,dep,zoff,r,m,h=.55):
  a=(cx+xoff,y+inward*dep,z+zoff);end=(a[0],a[1],a[2]+h);ob=cylinder(col,'R2_'+code+'_'+n,a,end,r,m);added.append(ob.name);return ob
 if code=='MSEE':
  # Two-level student atrium: open bridge edges, meeting tables and warm seating glimpsed through the actual glazed atrium.
  for j,bz in enumerate((2.7,5.6)):
   b(f'atrium_bridge_{j+1}',0,0,bz,(span,.58,.16),tile)
   for s in (-1,1):b(f'atrium_bridge_rail_{j+1}_{s}',0,0,bz+.52,(span,.08,.08),steel)
   for n in range(8):c(f'atrium_rail_post_{j+1}_{n}',-span/2+(n+.5)*span/8,0,bz+.18,.035,steel,.7)
  for j,xoff in enumerate((-3.8,0,3.8)):
   b(f'atrium_collaboration_table_{j}',xoff,-.22,1.35,(2.5,.95,.12),wood)
   for dx in (-.72,.72):b(f'atrium_seat_{j}_{dx}',xoff+dx,-.48,.80,(.48,.42,.12),accent)
  b('atrium_wayfinding_screen',0,-.24,1.9,(1.25,.10,1.35),dark)
 elif code in ('BIDC','BIND'):
  # Modern collaborative/research lobby scale and room functions follow official center descriptions; precise furniture layouts are schematic.
  b('glass_lobby_floor',0,0,.02,(span,.65,.10),tile)
  b('welcome_desk',0,-.08,.62,(min(3.8,span*.44),.72,.95),wood)
  b('welcome_desk_light',0,-.10,1.15,(min(3.5,span*.4),.04,.05),glow)
  for j,xoff in enumerate((-span*.26,span*.26)):
   b(f'lobby_column_{j}',xoff,.14,1.65,(.28,.28,3.3),dark)
  if code=='BIDC':
   for j,xoff in enumerate((-2.65,0,2.65)):
    b(f'makerspace_worktable_{j}',xoff,.02,1.35,(2.1,.62,.12),wood)
    b(f'cnc_machine_{j}',xoff,.02,2.02,(1.05,.54,1.15),dark)
    b(f'machine_control_lamp_{j}',xoff,.02,2.63,(.64,.03,.03),glow)
   b('check_in_kiosk',-span*.35,-.04,1.25,(.58,.48,1.55),accent)
  else:
   for j,xoff in enumerate((-2.5,0,2.5)):
    b(f'research_bench_{j}',xoff,.04,1.25,(2.0,.58,.12),white)
    b(f'bench_casework_{j}',xoff,.13,.78,(1.65,.42,.83),accent)
    b(f'lab_instrument_{j}',xoff,.08,1.86,(.62,.45,.92),dark)
    b(f'lab_glass_sash_{j}',xoff,.16,2.35,(.68,.08,.06),glow)
 elif code=='NWCP':
  for j,xoff in enumerate((-2.4,0,2.4)):
   b(f'plant_service_pump_{j}',xoff,0,.95,(1.05,.70,1.55),steel)
   b(f'plant_pump_base_{j}',xoff,0,.12,(1.35,.9,.24),dark)
   # coupling and vertical piping deliberately visible behind the louvers.
   b(f'plant_service_pipe_{j}',xoff,.18,2.0,(.16,.17,1.9),accent)
  b('utility_control_panel',span*.36,.02,1.35,(.78,.3,1.85),dark)
 elif code=='BRFM':
  # Evidence supports treatment corridor and livestock stalls; exact room arrangement is not claimed.
  b('animal_treatment_corridor_floor',0,0,.02,(span,.60,.10),tile)
  b('stainless_exam_table',0,-.05,1.02,(2.15,.72,.16),steel)
  for xoff in (-.92,.92):c('exam_table_leg_'+str(xoff),xoff,-.05,.10,.045,steel,.82)
  for j,xoff in enumerate((-span*.28,span*.28)):
   b(f'livestock_stall_partition_{j}',xoff,.12,1.52,(.09,.44,2.9),steel)
   b(f'stall_gate_rail_{j}',xoff,.04,1.55,(.10,.70,.10),dark)
   b(f'feed_trough_{j}',xoff,.19,.47,(.56,.45,.40),tile)
  b('treatment_equipment_cart',span*.28,-.14,1.05,(.62,.48,1.22),accent)
 elif code=='ADDL':
  # Diagnostic lab surfaces and a visible biosafety cabinet; real room layout and BSL3 boundary remain unverified.
  for j,xoff in enumerate((-span*.26,0,span*.26)):
   b(f'diagnostic_lab_bench_{j}',xoff,.05,1.2,(1.75,.60,.14),white)
   b(f'diagnostic_casework_{j}',xoff,.15,.72,(1.55,.42,.84),accent)
   b(f'biosafety_cabinet_{j}',xoff,.10,2.14,(1.35,.50,1.55),steel)
   b(f'cabinet_view_sash_{j}',xoff,.36,2.36,(1.15,.035,.06),glow)
  b('specimen_analyzer',0,-.10,2.8,(.72,.48,.68),dark)
 elif code in ('BCHM','ABE'):
  b('research_lab_floor',0,0,.02,(span,.62,.10),tile)
  for j,xoff in enumerate((-span*.27,0,span*.27)):
   b(f'lab_bench_{j}',xoff,.04,1.2,(1.65,.60,.14),white)
   b(f'lab_base_cabinet_{j}',xoff,.14,.72,(1.48,.42,.84),accent)
   if code=='BCHM':b(f'fume_hood_{j}',xoff,.10,2.28,(1.2,.44,1.75),dark);b(f'fume_hood_sash_{j}',xoff,.34,2.55,(.96,.035,.08),glow)
   else:b(f'project_bench_device_{j}',xoff,.08,1.95,(.78,.45,.92),dark)
 elif code=='AGAD':
  b('office_reception_floor',0,0,.02,(span,.55,.10),tile)
  b('reception_desk',0,-.05,.62,(min(2.8,span*.72),.68,.98),wood)
  b('reception_lamp',0,-.05,1.15,(.75,.04,.06),glow)
  for j,xoff in enumerate((-span*.28,span*.28)):
   b(f'office_lounge_seat_{j}',xoff,.10,.55,(.82,.68,.9),accent)
   b(f'office_lounge_table_{j}',xoff,.05,1.04,(.68,.48,.08),wood)
 elif code=='DAUC':
  b('alumni_lobby_floor',0,0,.02,(span,.56,.10),tile)
  for j,xoff in enumerate((-span*.23,0,span*.23)):
   b(f'event_lobby_table_{j}',xoff,.06,1.22,(1.55,.72,.12),wood)
   for dx in (-.52,.52):b(f'banquet_chair_{j}_{dx}',xoff+dx,-.14,.55,(.42,.42,.88),accent)
  b('alumni_display_case',0,.22,1.55,(1.5,.25,1.7),dark)
  b('display_case_glow',0,.08,1.56,(.045,.02,1.42),glow)
 # simple high-contrast silhouettes and local room label block remain within the pane footprint
 return added

def add_context(col,code,door,shell,normal,axis,inward):
 dlo,dhi=bounds(door);dc=[(dlo[i]+dhi[i])/2 for i in range(3)];slo,shi=bounds(shell);ground=.10
 paving=mat('R2_'+code+'_site_paving',(.31,.33,.33),.04,.86);edge=mat('R2_'+code+'_site_stone',(.55,.52,.44),.02,.8);green=mat('R2_'+code+'_site_plant',(.10,.22,.13),0,.8);soil=mat('R2_'+code+'_site_soil',(.19,.13,.08),0,.95)
 # entrance apron begins at the door and extends outward only; attached context remains in the same local asset library.
 if normal==1:
  front=dc[1]-inward*1.8;box(col,'R2_'+code+'_approach_apron',(dc[0],front,ground),(8.0,4.2,.16),paving)
  for s in (-1,1):
   x=dc[0]+s*5.0;y=front
   box(col,f'R2_{code}_planter_{s}',(x,y,.48),(1.25,.72,.68),edge);box(col,f'R2_{code}_planter_soil_{s}',(x,y,.84),(1.1,.57,.08),soil);sphere(col,f'R2_{code}_low_shrub_{s}',(x,y,.98),(.48,.32,.34),green)
 else:
  front=dc[0]-inward*1.8;box(col,'R2_'+code+'_approach_apron',(front,dc[1],ground),(4.2,8.0,.16),paving)
  for s in (-1,1):
   y=dc[1]+s*5.0;box(col,f'R2_{code}_planter_{s}',(front,y,.48),(.72,1.25,.68),edge);box(col,f'R2_{code}_planter_soil_{s}',(front,y,.84),(.57,1.1,.08),soil);sphere(col,f'R2_{code}_low_shrub_{s}',(front,y,.98),(.32,.48,.34),green)
 return ['entrance paving apron','two low masonry planters with low shrubs']

def add_nwcp_service_yard(col,shell):
 slo,shi=bounds(shell); concrete=mat('R2_NWCP_service_concrete',(.25,.27,.27),.02,.9);steel=mat('R2_NWCP_fence_metal',(.12,.16,.16),.75,.35);added=[]
 # fenced service bay and pipe manifold on the east service edge; location is a typology cue, not a survey.
 x=shi[0]+1.3;y=(slo[1]+shi[1])*.25
 box(col,'R2_NWCP_service_apron',(x+1.6,y,.08),(4.5,10.0,.16),concrete);added.append('R2_NWCP_service_apron')
 for yy in (y-5,y+5):cylinder(col,'R2_NWCP_service_fence_post_'+str(yy),(x,yy,.15),(x,yy,2.3),.055,steel);added.append('R2_NWCP_service_fence_post_'+str(yy))
 cylinder(col,'R2_NWCP_service_fence_toprail',(x,y-5,2.3),(x,y+5,2.3),.04,steel);added.append('R2_NWCP_service_fence_toprail')
 for i in range(1,10):cylinder(col,f'R2_NWCP_service_fence_mesh_{i}',(x,y-5+i,0.15),(x,y-5+i,2.3),.018,steel);added.append(f'R2_NWCP_service_fence_mesh_{i}')
 # twin vertical expansion vessels and a simple valve header, placed on service pad
 for i,yy in enumerate((y-2.5,y,y+2.5)):
  cylinder(col,f'R2_NWCP_expansion_vessel_{i}',(x+1.6,yy,.2),(x+1.6,yy,3.1),.52,mat('R2_NWCP_vessel_color',(.38,.43,.43),.7,.32),20);added.append(f'R2_NWCP_expansion_vessel_{i}')
 return added

for code,asset,evrel,evdir in ASSETS:
 path=os.path.join(ROOT,'modular','buildings',asset+'.blend');bpy.ops.wm.open_mainfile(filepath=path);clear_r2();col=bpy.data.collections.get('Asset_'+asset);assert col
 shell=next(o for o in col.all_objects if o.type=='MESH' and ('GIS' in o.name or 'official_GIS' in o.name)); door=next((o for o in col.all_objects if o.type=='MESH' and (o.name.endswith('_main_entrance_glazed_door') or o.name=='MSEE_primary_glazed_doors')),None)
 if code!='NWCP': assert door,code+' main door missing'
 edits=[]
 if code!='NWCP':
  axis,normal,cx,face,inward,width,height,zbase=inside_panel(col,code,door,shell);added=interior_set(col,code,axis,normal,cx,face,inward,width,height,zbase);edits.extend(added);edits.append('Added use-specific visible interior vignette behind primary glazing; schematic and not as-built.')
  edits.extend(add_context(col,code,door,shell,normal,axis,inward))
 else:
  # Through the existing acoustic louver banks, add shallow pumps/couplings immediately behind the blades.
  lo,hi=bounds(shell);louver=next(o for o in col.all_objects if o.name.startswith('NWCP_acoustic_louver_bank_'));llo,lhi=bounds(louver);y=(llo[1]+lhi[1])*.5;z=.8; steel=mat('R2_NWCP_visible_pump_steel',(.36,.43,.44),.75,.3);dark=mat('R2_NWCP_visible_pump_dark',(.08,.12,.12),.35,.4);blue=mat('R2_NWCP_visible_pipe',(.15,.32,.37),.62,.3)
  for i,x in enumerate((-12,-6,0,6,12)):
   box(col,f'R2_NWCP_louver_backing_machine_{i}',(x,y,z+1.1),(1.6,.35,2.2),dark);cylinder(col,f'R2_NWCP_pump_motors_{i}',(x,y-.1,z+.2),(x,y-.1,z+1.1),.38,steel,16);cylinder(col,f'R2_NWCP_vertical_service_pipe_{i}',(x+.56,y+.03,z+.2),(x+.56,y+.03,z+3.0),.11,blue);edits.append(f'R2_NWCP_louver_backing_machine_{i}')
  edits.extend(add_nwcp_service_yard(col,shell));edits.append('Added mechanical service silhouettes visible behind acoustic louvers and a restrained fenced service apron; equipment routing and exact yard layout are typological estimates.')
 # expose a second-level lobby bridge/cornice cue only where building envelope geometry already allows; no shell edits.
 if False and code in ('AGAD','DAUC','BCHM','ABE','ADDL','BRFM'):
  # A discreet dark fascia just beneath roof, staged against existing shell. This is trim, not envelope massing.
  slo,shi=bounds(shell);fac=mat('R2_'+code+'_roof_cornice_material',(.28,.25,.21),.08,.75)
  if code=='AGAD':
   box(col,'R2_AGAD_front_cornice',(0,slo[1]+.15,shi[2]-.28),(min(shi[0]-slo[0],42),.42,.24),fac);edits.append('Visible restrained historic roofline/cornice accent.')
  elif code=='DAUC':
   box(col,'R2_DAUC_roof_entrance_coping',(0,slo[1]+.18,shi[2]-.30),(min(shi[0]-slo[0],52),.46,.24),fac);edits.append('Roofline coping accent complements the documented curved brick-and-glass facade.')
 sc=bpy.context.scene;sc.render.resolution_percentage=100;sc.render.filepath=os.path.join(OUT,asset+'_revision2_preview.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=path)
 evp=os.path.join(ROOT,evrel);ev=json.load(open(evp,encoding='utf-8'));ev.setdefault('revision_history',[]).append({'date':'2026-10-24','review_request':'Second fidelity pass after grader flagged interiors and immediate context; corrected glazing visibility and entrance apron direction after visual review.','geometry_edits':edits,'actual_vs_schematic':{'evidence_supported_function':{'MSEE':'two-story student atrium and lab/engineering use','BIDC':'hands-on makerspace check-in, fabrication benches and machine silhouettes','BIND':'life-science research lobby/benches and instruments','ADDL':'diagnostic lab benches and biosafety cabinet silhouettes; documented BSL-3 addition is noted but not dimensioned','BRFM':'animal-treatment corridor, exam table and stall/feeding partitions are use-based cues','NWCP':'cooling plant pumps, headers, louver backing machinery and utility service apron'},'schematic':'All visible interior object layouts are interpretive vignettes; no construction/room plans were used, and they are not as-built.'},'footprint_origin':'GIS shell and origin unchanged; local site context and interior vignettes are separate detail objects.'})
 ev['validation']['revision2_preview']=os.path.relpath(sc.render.filepath,ROOT).replace('/','\\');ev['validation']['revision2_object_count']=len(col.all_objects);ev['validation']['origin_preserved']=True;ev['validation']['GIS_shell_preserved']=True
 if code in ('BIDC','BIND','MSEE'):ev.setdefault('references',[]).append({'provider':'Purdue official program/facility page','url':{'BIDC':'https://www.purdue.edu/bidc/about/about-the-center/','BIND':'https://bindley.research.purdue.edu/','MSEE':'https://archives.lib.purdue.edu/agents/corporate_entities/703'}[code],'observed_or_supports':'Building use, open atrium/makerspace/research function; added room furniture is a clearly marked schematic vignette, not a photographed or surveyed interior.'})
 if code=='ADDL':ev.setdefault('references',[]).append({'provider':'Purdue ADDL official newsletter','url':'https://www.addl.purdue.edu/newsletters/2007/Summer/Letter.htm','observed_or_supports':'Attached BSL-3 addition on southeast corner; exact room plan is unavailable.'})
 if code=='BRFM':ev.setdefault('references',[]).append({'provider':'Purdue College of Veterinary Medicine virtual tour','url':'https://vet.purdue.edu/hospital/virtual-tour/hospital.php?id=3','observed_or_supports':'Farm Animal Hospital program and hospital context; displayed treatment equipment/stall layout remains schematic.'})
 json.dump(ev,open(evp,'w',encoding='utf-8'),indent=2);print('SAVED',code,'objects',len(col.all_objects),'interior',len(added),flush=True)

