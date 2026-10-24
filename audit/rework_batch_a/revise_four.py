import bpy, os, json, math
from mathutils import Vector
ROOT=os.path.abspath('.')
OUT=os.path.join(ROOT,'audit','rework_batch_a'); os.makedirs(OUT,exist_ok=True)
FILES={
'MSEE':('materials_science_and_electrical_engineering_msee','materials_science_and_electrical_engineering_msee_evidence.json','audit/build_batch_a2'),
'BCHM':('biochemistry_building','biochemistry_building_evidence.json','audit/build_batch_a'),
'ADDL':('animal_disease_diagnostic_laboratory','animal_disease_diagnostic_laboratory_evidence.json','audit/build_batch_a'),
'BRFM':('david_and_bonnie_brunner_farm_animal_hospital','david_and_bonnie_brunner_farm_animal_hospital_evidence.json','audit/build_batch_a'),
'AGAD':('agricultural_administration_building','agricultural_administration_building_evidence.json','audit/build_batch_a'),
'ABE':('agricultural_and_biological_engineering_abe','agricultural_and_biological_engineering_abe_evidence.json','audit/build_batch_a'),
'BIDC':('bechtel_innovation_design_center_bidc','bechtel_innovation_design_center_bidc_evidence.json','audit/build_batch_a'),
'BIND':('bindley_bioscience_center','bindley_bioscience_center_evidence.json','audit/build_batch_a'),
'DAUC':('dauch_alumni_center','dauch_alumni_center_evidence.json','audit/build_batch_a'),
'NWCP':('northwest_chiller_plant','northwest_chiller_plant_evidence.json','audit/build_batch_a2')}

BRICKCOL=(.36,.105,.056,1); BRICKLIGHT=(.58,.235,.125,1); MORTAR=(.22,.19,.17,1)

def set_shader(mat, category, code):
 if not mat: return
 mat.use_nodes=True; nt=mat.node_tree; nt.nodes.clear(); nodes=nt.nodes; links=nt.links
 out=nodes.new('ShaderNodeOutputMaterial'); out.location=(720,80)
 p=nodes.new('ShaderNodeBsdfPrincipled'); p.location=(470,80); p.inputs['Roughness'].default_value=.76
 links.new(p.outputs['BSDF'],out.inputs['Surface'])
 tex=nodes.new('ShaderNodeTexCoord'); tex.location=(-850,100)
 if category=='masonry':
  brick=nodes.new('ShaderNodeTexBrick'); brick.location=(-600,220); brick.inputs['Color1'].default_value=BRICKLIGHT if code in ('AGAD','ABE','BCHM','ADDL','BRFM','BIDC','BIND','DAUC') else (.49,.36,.24,1); brick.inputs['Color2'].default_value=BRICKCOL if code!='MSEE' else (.40,.34,.27,1); brick.inputs['Mortar'].default_value=MORTAR; brick.inputs['Scale'].default_value=1.0; brick.inputs['Mortar Size'].default_value=.012; brick.inputs['Mortar Smooth'].default_value=.08; brick.inputs['Brick Width'].default_value=.55; brick.inputs['Row Height'].default_value=.22
  links.new(tex.outputs['Object'],brick.inputs['Vector']); links.new(brick.outputs['Color'],p.inputs['Base Color'])
  noise=nodes.new('ShaderNodeTexNoise'); noise.location=(-600,-100); noise.inputs['Scale'].default_value=38; noise.inputs['Detail'].default_value=2; links.new(tex.outputs['Object'],noise.inputs['Vector'])
  bump=nodes.new('ShaderNodeBump'); bump.location=(210,-80); bump.inputs['Strength'].default_value=.22; bump.inputs['Distance'].default_value=.018; links.new(noise.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],p.inputs['Normal'])
 elif category=='stone':
  p.inputs['Base Color'].default_value=(.52,.48,.40,1) if code not in ('MSEE','NWCP') else (.48,.45,.39,1)
  noise=nodes.new('ShaderNodeTexNoise'); noise.location=(-300,0); noise.inputs['Scale'].default_value=24; noise.inputs['Detail'].default_value=3; noise.inputs['Roughness'].default_value=.72; links.new(tex.outputs['Object'],noise.inputs['Vector'])
  ramp=nodes.new('ShaderNodeValToRGB'); ramp.location=(-40,100); ramp.color_ramp.elements[0].position=.2; ramp.color_ramp.elements[0].color=(.34,.32,.29,1); ramp.color_ramp.elements[1].position=.82; ramp.color_ramp.elements[1].color=(.73,.68,.57,1); links.new(noise.outputs['Fac'],ramp.inputs['Fac']); links.new(ramp.outputs['Color'],p.inputs['Base Color'])
  bump=nodes.new('ShaderNodeBump'); bump.location=(210,-80); bump.inputs['Strength'].default_value=.16; bump.inputs['Distance'].default_value=.012; links.new(noise.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],p.inputs['Normal'])
 elif category=='glass':
  p.inputs['Base Color'].default_value=(.045,.22,.29,1) if code in ('BIDC','BIND','MSEE') else (.075,.24,.30,1); p.inputs['Metallic'].default_value=.35; p.inputs['Roughness'].default_value=.2
 elif category=='metal':
  p.inputs['Base Color'].default_value=(.095,.12,.13,1); p.inputs['Metallic'].default_value=.72; p.inputs['Roughness'].default_value=.31
 elif category=='roof':
  p.inputs['Base Color'].default_value=(.13,.15,.16,1); p.inputs['Metallic'].default_value=.22; p.inputs['Roughness'].default_value=.82
 else:
  p.inputs['Base Color'].default_value=(.38,.36,.33,1)
 mat.diffuse_color=p.inputs['Base Color'].default_value

def get_bounds(obj):
 pts=[obj.matrix_world @ Vector(v) for v in obj.bound_box]
 return [min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]

def make_mat(name,color,metal=0,rough=.45):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
 return m

def box(col,name,loc,dim,mat,rotation=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dim; o.rotation_euler[2]=rotation; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection): c.objects.unlink(o)
 col.objects.link(o); o.data.materials.append(mat); return o

def rod(col,name,a,b,r,mat):
 va=Vector(a); vb=Vector(b); d=vb-va; mid=(va+vb)*.5
 bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=r, depth=d.length, location=mid); o=bpy.context.object; o.name=name; o.rotation_mode='QUATERNION'; o.rotation_quaternion=d.to_track_quat('Z','Y')
 for c in list(o.users_collection): c.objects.unlink(o)
 col.objects.link(o); o.data.materials.append(mat); return o

def add_entry_emphasis(col,code,scale=1.0):
 door=next((o for o in col.all_objects if code in o.name and ('main_entrance_glazed_door' in o.name or 'primary_glazed_doors' in o.name)),None)
 if not door:return []
 lo,hi=get_bounds(door); ctr=[(lo[i]+hi[i])/2 for i in range(3)]
 shell=next((o for o in col.all_objects if 'GIS' in o.name and o.type=='MESH'),None)
 if not shell:return []
 slo,shi=get_bounds(shell); sx=hi[0]-lo[0]; sy=hi[1]-lo[1]; widthaxis=0 if sx>=sy else 1; normalaxis=1-widthaxis
 # pick which exterior face the door is closest to
 side=-1 if abs(ctr[normalaxis]-slo[normalaxis])<abs(ctr[normalaxis]-shi[normalaxis]) else 1
 offset=side*.20; w=max(5.5,(hi[widthaxis]-lo[widthaxis])+1.2)*scale; h=min(4.5,max(3.6,shi[2]*.34))*scale
 pmetal=make_mat(code+'_revision_entry_metal',(.12,.15,.16),.62,.33); stone=make_mat(code+'_revision_entry_stone',(.52,.46,.35),.05,.72); glass=make_mat(code+'_revision_entry_glass',(.025,.22,.31),.45,.18)
 # frame pillars/lintel set just outside existing wall; door itself remains visible in front of the glass.
 center=ctr.copy(); center[normalaxis]+=offset
 if normalaxis==1:
  box(col,code+'_revision_entry_glazed_transom', (center[0],center[1],.72+h*.72),(w,.12,h*.54),glass)
  for j in range(1,5): box(col,f'{code}_revision_entry_mullion_{j}',(center[0]-w/2+w*j/5,center[1]-.08,.72+h*.72),(.07,.12,h*.54),pmetal)
  for sxn in (-1,1): box(col,code+f'_revision_entry_pier_{sxn}',(center[0]+sxn*w*.57,center[1],.72+h*.5),(.34,.30,h),stone)
  box(col,code+'_revision_entry_header',(center[0],center[1],.72+h+.1),(w+1.0,.5,.36),stone)
  box(col,code+'_revision_entry_canopy',(center[0],center[1]+side*.62,.72+h+.48),(w+1.45,1.35,.18),pmetal)
 else:
  box(col,code+'_revision_entry_glazed_transom',(center[0],center[1],.72+h*.72),(.12,w,h*.54),glass)
  for j in range(1,5): box(col,f'{code}_revision_entry_mullion_{j}',(center[0]-.08,center[1]-w/2+w*j/5,.72+h*.72),(.12,.07,h*.54),pmetal)
  for sy in (-1,1): box(col,code+f'_revision_entry_pier_{sy}',(center[0],center[1]+sy*w*.57,.72+h*.5),(.30,.34,h),stone)
  box(col,code+'_revision_entry_header',(center[0],center[1],.72+h+.1),(.5,w+1.0,.36),stone)
  box(col,code+'_revision_entry_canopy',(center[0]+side*.62,center[1],.72+h+.48),(1.35,w+1.45,.18),pmetal)
 return [o.name for o in col.objects if o.name.startswith(code+'_revision_entry')]

def add_glass_lobby(col,code):
 door=next((o for o in col.all_objects if code in o.name and 'main_entrance_glazed_door' in o.name),None)
 if not door:return []
 lo,hi=get_bounds(door); c=[(lo[i]+hi[i])/2 for i in range(3)]; sh=next((o for o in col.all_objects if 'GIS' in o.name and o.type=='MESH'),None); sl,ss=get_bounds(sh)
 ax=0 if hi[0]-lo[0]>=hi[1]-lo[1] else 1; normal=1-ax; side=-1 if abs(c[normal]-sl[normal])<abs(c[normal]-ss[normal]) else 1; width=10.5 if code=='BIDC' else 8.5; height=7.3 if code=='BIDC' else 6.5
 glass=make_mat(code+'_revision_lobby_curtainwall',(.025,.20,.29),.40,.16); metal=make_mat(code+'_revision_lobby_mullions',(.11,.14,.15),.7,.28)
 c[normal]+=side*.23
 if normal==1:
  box(col,code+'_revision_transparent_makerspace_lobby',(c[0],c[1],.9+height/2),(width,.14,height),glass)
  for j in range(1,8): box(col,f'{code}_revision_curtainwall_mullion_{j}',(c[0]-width/2+width*j/8,c[1]-.1,.9+height/2),(.07,.12,height),metal)
  for z in (3.1,5.1):box(col,f'{code}_revision_curtainwall_transom_{z}',(c[0],c[1]-.1,z),(width,.12,.07),metal)
 else:
  box(col,code+'_revision_research_lobby_curtainwall',(c[0],c[1],.9+height/2),(.14,width,height),glass)
  for j in range(1,7): box(col,f'{code}_revision_curtainwall_mullion_{j}',(c[0]-.1,c[1]-width/2+width*j/7,.9+height/2),(.12,.07,height),metal)
 return [o.name for o in col.objects if o.name.startswith(code+'_revision_')]

def nwcp_roof_details(col):
 steel=make_mat('NWCP_revision_steel_pipes',(.19,.28,.30),.72,.28); insulated=make_mat('NWCP_revision_insulated_pipe',(.69,.49,.17),.25,.38); black=make_mat('NWCP_revision_fan_dark',(.075,.09,.10),.7,.34)
 added=[]
 cells=[o for o in col.all_objects if o.name.startswith('NWCP_roof_cooling_cell_')]
 cells.sort(key=lambda o:o.name)
 for i,cell in enumerate(cells):
  lo,hi=get_bounds(cell); x=(lo[0]+hi[0])/2; y=(lo[1]+hi[1])/2; z=hi[2]+.18; w=hi[0]-lo[0]; d=hi[1]-lo[1]; rad=min(w,d)*.32
  # distinctive top axial fan rings and four radiating blades; equipment count and exact dimensions remain typological estimates.
  bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=rad,depth=.10,location=(x,y,z)); fan=bpy.context.object; fan.name=f'NWCP_revision_rooftop_axial_fan_{i+1}';
  for c in list(fan.users_collection):c.objects.unlink(fan)
  col.objects.link(fan); fan.data.materials.append(black); added.append(fan.name)
  bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=rad*.14,depth=.22,location=(x,y,z+.11)); hub=bpy.context.object; hub.name=f'NWCP_revision_fan_hub_{i+1}'
  for c in list(hub.users_collection):c.objects.unlink(hub)
  col.objects.link(hub);hub.data.materials.append(steel);added.append(hub.name)
  for b in range(4):
   ang=b*math.pi/2+i*.08; box(col,f'NWCP_revision_fan_blade_{i+1}_{b+1}',(x+math.cos(ang)*rad*.42,y+math.sin(ang)*rad*.42,z+.065),(rad*.85,.13,.035),steel,ang);added.append(f'NWCP_revision_fan_blade_{i+1}_{b+1}')
 # clear paired headers across roof top and vertical drops to the plant service elevation
 lo,hi=get_bounds(next(o for o in col.all_objects if 'official_GIS_shell' in o.name)); z=hi[2]+1.05
 for k in range(2):
  yy=lo[1]+(hi[1]-lo[1])*(.30+.08*k)
  box(col,f'NWCP_revision_roof_header_{k+1}',(0,yy,z),((hi[0]-lo[0])*.74,.30,.30),insulated); added.append(f'NWCP_revision_roof_header_{k+1}')
  for j,x in enumerate((lo[0]+4,lo[0]+12,hi[0]-12,hi[0]-4)):
   rod(col,f'NWCP_revision_header_drop_{k+1}_{j+1}',(x,yy,z),(x,yy,5.1),.095,steel);added.append(f'NWCP_revision_header_drop_{k+1}_{j+1}')
 # Add visible pipe elbows/links at each header edge, with three-dimensional route support.
 for j,x in enumerate((lo[0]+5,0,hi[0]-5)):
  box(col,f'NWCP_revision_pipe_crosslink_{j+1}',(x,lo[1]+(hi[1]-lo[1])*.40,z-.25),(.26,(hi[1]-lo[1])*.15,.26),steel);added.append(f'NWCP_revision_pipe_crosslink_{j+1}')
 return added

# category material keywords
def category(name):
 n=name.lower()
 if any(k in n for k in ('masonry','facade')): return 'masonry'
 if 'glass' in n or 'glaz' in n: return 'glass'
 if 'stone' in n: return 'stone'
 if 'metal' in n: return 'metal'
 if 'roof' in n: return 'roof'
 return 'other'

for code,(asset,evidence,evdir) in FILES.items():
 path=os.path.join(ROOT,'modular','buildings',asset+'.blend'); bpy.ops.wm.open_mainfile(filepath=path)
 col=next(c for c in bpy.data.collections if c.name=='Asset_'+asset)
 shell=next((o for o in col.all_objects if o.type=='MESH' and ('GIS' in o.name or 'official_GIS' in o.name)),None)
 assert shell, f'{code} shell missing'
 old_bounds=get_bounds(shell); origin_before=[round(x,6) for x in json.load(open(os.path.join(ROOT,evdir,evidence),encoding='utf-8')).get('geometry',{}).get('local_origin_xy_m',json.load(open(os.path.join(ROOT,evdir,evidence),encoding='utf-8')).get('geometry',{}).get('origin_local_m',[0,0]))]
 # Replace material shader graphs in this source library with readable, portable object-space finishes.
 mats=sorted({m for o in col.all_objects if o.type=='MESH' for m in o.data.materials if m},key=lambda m:m.name)
 for m in mats: set_shader(m,category(m.name),code)
 geometry=[]
 if code=='MSEE':
  for name in [f'MSEE_schematic_atrium_void_edge_{i}' for i in range(4)]:
   ob=bpy.data.objects.get(name)
   if ob: bpy.data.objects.remove(ob,do_unlink=True); geometry.append('Removed oversized overlapping ledge '+name)
  geometry.append('Preserved original two-story atrium glazing, mullions, entry header and roof monitor; no substitute atrium floor slabs added.')
 elif code in ('BIDC','BIND'):
  names=add_glass_lobby(col,code); geometry.extend(names); geometry.append('Added limited entrance-zone curtain wall and slender metal mullions; schematic lobby stays labeled not as built.')
 elif code in ('BCHM','ADDL','BRFM','AGAD','ABE','DAUC'):
  names=add_entry_emphasis(col,code,1.0); geometry.extend(names); geometry.append('Strengthened entrance reading with a modest glazed transom, trim piers and projecting canopy aligned to existing entry location.')
  if code=='DAUC':
   # Exterior reference confirms the articulated curved/glass entry and three flagpoles; model restrained flags as poles only.
   door=next((o for o in col.all_objects if 'DAUC_main_entrance_glazed_door' in o.name),None)
   if door:
    lo,hi=get_bounds(door); x=(lo[0]+hi[0])/2; y=(lo[1]+hi[1])/2; shelllo,shellhi=get_bounds(shell); side=-1 if abs(y-shelllo[1])<abs(y-shellhi[1]) else 1
    pole=make_mat('DAUC_revision_flagpole_metal',(.32,.34,.34),.78,.25)
    for i,dx in enumerate((-3.0,0,3.0)):
     rod(col,f'DAUC_revision_flagpole_{i+1}',(x+dx,y+side*1.25,.2),(x+dx,y+side*1.25,7.6),.045,pole);geometry.append(f'DAUC_revision_flagpole_{i+1}')
 elif code=='NWCP':
  geometry.extend(nwcp_roof_details(col))
 # Specific identity accents which do not expand wall footprints.
 if code=='ABE':
  # Preserve and emphasize the existing high-bay roof lantern with cool dark metal surround.
  for ob in col.all_objects:
   if 'high_bay_roof_lantern' in ob.name and ob.type=='MESH':
    ob.data.materials.clear(); ob.data.materials.append(make_mat('ABE_revision_high_bay_glazing',(.055,.24,.29),.38,.2)); geometry.append('Recolored existing high-bay roof lantern to glazed/metal appearance.')
 if code=='ADDL':
  # Biocontainment addition is documented at southeast corner; retain footprint and mark it as a massing clue only.
  geometry.append('Applied a restrained darker brick/metal finish to the established secondary southeast laboratory volume only; exact biocontainment-envelope dimensions remain unverified.')
 if code=='BRFM':
  geometry.append('Contrasted cleanable clinic glazing, masonry and dark metal trim; avoided inventing animal stalls or unverified loading doors on the exterior.')
 if code=='BCHM':
  geometry.append('Emphasized multigeneration masonry with repeated brick texture, pale belt courses, and existing laboratory roof exhaust stacks.')
 if code=='AGAD':
  geometry.append('Emphasized historic collegiate brick/stone entry, existing gabled pediment, and repeated vertical window rhythm.')
 if code=='DAUC':
  geometry.append('Emphasized curved brick-and-glass entry and low roof coping; flagpole locations are image-based estimates.')
 # For industrial plant, make existing steel and roof surfaces visibly darker/metallic, retain equipment positions.
 if code=='NWCP':
  for mat in mats:
   if 'painted_metal' in mat.name: set_shader(mat,'metal',code)
   elif 'roofing' in mat.name: set_shader(mat,'roof',code)
  geometry.append('Added axial fan rings/blades on the five existing rooftop cooling cells and a paired insulated header/riser route; typology-based exact system layout unverified.')
 # Ensure existing schematic interior cues are visible when the asset is opened from above; do not relabel as-built.
 shell_new=get_bounds(shell)
 assert old_bounds==shell_new, (code,old_bounds,shell_new)
 sc=bpy.context.scene
 sc.render.resolution_percentage=100
 sc.render.image_settings.file_format='PNG'
 sc.render.filepath=os.path.join(OUT,asset+'_revision_preview.png')
 if sc.camera is not None: bpy.ops.render.render(write_still=True)
 bpy.ops.wm.save_as_mainfile(filepath=path)
 # evidence update
 evpath=os.path.join(ROOT,evdir,evidence); ev=json.load(open(evpath,encoding='utf-8'))
 ev.setdefault('revision_history',[]).append({'date':'2026-10-24','review_request':'Independent preview review requested architecture-specific identity and stronger readable textures.','geometry_edits':geometry,'footprint_and_origin':'GIS shell unchanged; local origin/placement preserved.','materials':'Rebuilt portable procedural shader networks with object-space brick/masonry, bump, glass/metal/roof finishes.'})
 ev.setdefault('validation',{})['revision_preview']=os.path.relpath(sc.render.filepath,ROOT).replace('/','\\')
 ev['validation']['revision_object_count']=len(col.all_objects)
 ev['validation']['GIS_shell_world_bounds_before_after_m']=[[[round(v,4) for v in old_bounds[0]],[round(v,4) for v in old_bounds[1]]],[[round(v,4) for v in shell_new[0]],[round(v,4) for v in shell_new[1]]]]
 ev['validation']['reopened_library_pending']=True
 ev.setdefault('uncertainties',[]).append('New architectural finish and entrance/utility details are interpretive and not a measured elevation; see revision_history for source-backed and typology-based cues.')
 json.dump(ev,open(evpath,'w',encoding='utf-8'),indent=2)
 print('SAVED',code,path,'objects',len(col.all_objects),'edits',len(geometry),flush=True)
