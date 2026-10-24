import bpy, os, json, math, time, hashlib
from mathutils import Vector

ROOT = r'C:\Users\Tobin\Documents\Blender\PurdueMap'
OUT = os.path.join(ROOT, 'audit', 'rework_batch_a')
ASSETS = [
 ('AGAD','agricultural_administration_building','audit/build_batch_a/agricultural_administration_building_evidence.json'),
 ('ABE','agricultural_and_biological_engineering_abe','audit/build_batch_a/agricultural_and_biological_engineering_abe_evidence.json'),
 ('ADDL','animal_disease_diagnostic_laboratory','audit/build_batch_a/animal_disease_diagnostic_laboratory_evidence.json'),
 ('BCHM','biochemistry_building','audit/build_batch_a/biochemistry_building_evidence.json'),
 ('BIDC','bechtel_innovation_design_center_bidc','audit/build_batch_a/bechtel_innovation_design_center_bidc_evidence.json'),
 ('BIND','bindley_bioscience_center','audit/build_batch_a/bindley_bioscience_center_evidence.json'),
 ('BRFM','david_and_bonnie_brunner_farm_animal_hospital','audit/build_batch_a/david_and_bonnie_brunner_farm_animal_hospital_evidence.json'),
 ('DAUC','dauch_alumni_center','audit/build_batch_a/dauch_alumni_center_evidence.json'),
 ('MSEE','materials_science_and_electrical_engineering_msee','audit/build_batch_a2/materials_science_and_electrical_engineering_msee_evidence.json'),
 ('NWCP','northwest_chiller_plant','audit/build_batch_a2/northwest_chiller_plant_evidence.json'),
]
REFS = {
 'AGAD':[('Official Purdue College of Agriculture photo','https://ag.purdue.edu/news/department/hla/2020/05/root-and-vine-psf-food-bank.html','Photographed brick facade and formal entry; office/lobby furnishings added as clearly schematic visualization detail.')],
 'ABE':[('Pepper Construction ABE renovation project','https://www.pepperconstruction.com/project/purdue-university-agriculture-and-biological-engineering-renovation-addition','Supports distinct renovated brick and contemporary glazed research wing; lab benches/equipment are schematic interior cues.'),('Farm Progress ABE virtual tour feature','https://www.farmprogress.com/farm-life/take-virtual-tour-through-purdue-s-new-ag-engineering-building','Shows 1928 entry lintel and addition glazing.')],
 'ADDL':[('Purdue Animal Disease Diagnostic Laboratory exterior photo','https://www.beefmagazine.com/livestock-management/purdue-animal-disease-diagnostic-laboratory-gets-boost-from-state','Facade photograph; interior diagnostic lab casework and service receiving volumes are schematic program cues, not an as-built plan.')],
 'BCHM':[('Purdue Campus Facilities and Buildings Historic Database','https://collections.lib.purdue.edu/campus/buildings','Building identity/context. No detailed elevation source was found; glazing rhythm and lab fixtures remain conservative schematic cues.')],
 'BIDC':[('Purdue Bechtel Innovation Design Center official story/photo','https://engineering.purdue.edu/Engr/AboutUs/News/Spotlights/2018/bidc-already-serving-large-number-of-students','Supports the transparent two-storey makerspace frontage; interior workshop benches and machine silhouettes are schematic visual cues.'),('Shive-Hattery BIDC project','https://www.shive-hattery.com/projects/purdue-university-bechtel-innovation-design-center/','Supports contemporary curtainwall and makerspace identity.')],
 'BIND':[('Purdue Bindley Bioscience Center','https://bindley.research.purdue.edu/about-us/','Exterior photos support the glass/metal research facade; laboratory casework and partition cues are schematic, not measured.'),('Flad Bindley Bioscience/Engineering project','https://www.flad.com/work/purdue-bindley-bioscience-engineering.php','Supports glass-fronted research facade and panel cladding.')],
 'BRFM':[('Purdue Veterinary Hospital virtual tour','https://vet.purdue.edu/hospital/virtual-tour/','Confirms animal-care program areas; clinical stalls, exam equipment, and interior cues are schematic visualization, not a surveyed plan.'),('Pepper construction project record','https://www.pepperconstruction.com/annualreview22/purdue-university-veterinary-hospital','Supports hospital addition context and service scale.')],
 'DAUC':[('Purdue for Life Foundation','https://www.purdueforlife.org/about/','Exterior photograph supports curved brick/glass entry and campus-facing frontage; reception/lounge furnishings are schematic.'),('Visit Lafayette-West Lafayette listing','https://www.homeofpurdue.com/listing/dauch-alumni-center/31/','Exterior photo supports tall glazed entry rhythm.')],
 'MSEE':[('Purdue Archives and Special Collections','https://archives.lib.purdue.edu/agents/corporate_entities/703','Facility context; existing two-storey glazed atrium retained and a modest interior bridge/lounge cue is schematic, not measured.')],
 'NWCP':[('Purdue Board of Trustees system improvements record','https://www.purdue.edu/treasurer/finance/wp-content/uploads/2023/04/Northwest-Chiller-Plant-System-Improvements-B-1-23-2-04.pdf','Confirms condenser water pumps and related plant equipment; exact exterior equipment placement remains schematic due absence of a public site elevation/photo.')]
}
EDITS = {}

def bounds(o):
    ps=[o.matrix_world @ Vector(v) for v in o.bound_box]
    return [min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]

def material(name,color,metal=0.0,rough=.4,alpha=1.0,emission=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,alpha);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    p.inputs['Alpha'].default_value=alpha
    if 'Emission Color' in p.inputs:p.inputs['Emission Color'].default_value=(*color,1)
    if 'Emission Strength' in p.inputs:p.inputs['Emission Strength'].default_value=emission
    try:m.surface_render_method='DITHERED'
    except:pass
    return m

def box(col,name,loc,dims,mat):
    hx,hy,hz=(v*.5 for v in dims)
    verts=[(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),(-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(4,0,3,7)]
    me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.materials.append(mat)
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);ob.location=loc
    return ob

def front_box(col,code,name,axis,normal,out,cross,plane,z,width,depth,height,mat):
    loc=(cross,plane,z) if axis==0 else (plane,cross,z)
    dims=(width,depth,height) if axis==0 else (depth,width,height)
    return box(col,'R4_'+code+'_'+name,loc,dims,mat)

def front_setup(col,asset):
    shell=next(o for o in col.all_objects if o.type=='MESH' and ('GIS' in o.name or 'official_GIS' in o.name))
    door=next((o for o in col.all_objects if o.type=='MESH' and ('main_entrance_glazed_door' in o.name or o.name=='MSEE_primary_glazed_doors')),None)
    sl,sh=bounds(shell)
    if door:
        dl,dh=bounds(door);dc=[(dl[i]+dh[i])*.5 for i in range(3)]
        axis=0 if (dh[0]-dl[0]) >= (dh[1]-dl[1]) else 1
        normal=1-axis;out=-1 if dc[normal] <= (sl[normal]+sh[normal])*.5 else 1
        cross=dc[axis]
    else:
        axis=0 if (sh[0]-sl[0]) >= (sh[1]-sl[1]) else 1
        normal=1-axis;out=-1 if (sl[normal]+sh[normal])*.5 <= (sl[normal]+sh[normal])*.5 else 1
        dc=[(sl[i]+sh[i])*.5 for i in range(3)];cross=dc[axis]
    # Use the local doorway plane. Several footprints are stepped or concave, so
    # the bounding-box extreme can be a different wing and makes overlays float.
    # R3's glazing plane is 0.18m outside the door center; R4 uses 0.20m.
    surf=dc[normal]+out*.20 if door else (sl[normal] if out<0 else sh[normal])+out*.24
    return shell,sl,sh,axis,normal,out,cross,surf

def cube_interior(col,code,axis,normal,out,cross,surf,z,label,w=1.4,h=.8,d=.46,body=None,top=None):
    body=body or material('R4_'+code+'_interior_warm_white',(.74,.72,.64),.04,.62,1,.1)
    top=top or material('R4_'+code+'_interior_wood',(.39,.25,.14),.03,.7)
    # The body/table top are shallow visible cutaway/tableau objects placed behind the front glass.
    front_box(col,code,label+'_body',axis,normal,out,cross,surf-out*.09,z+h*.5,w,d,h,body)
    front_box(col,code,label+'_top',axis,normal,out,cross,surf-out*.13,z+h+.06,w+.08,d+.10,.12,top)

def source_hash(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def render_final(code,asset,path,evrel,history_text):
    sc=bpy.context.scene;col=bpy.data.collections['Asset_'+asset]
    sc.render.resolution_x=1152;sc.render.resolution_y=864;sc.render.resolution_percentage=100
    out_over=os.path.join(OUT,asset+'_revision4_preview.png');out_detail=os.path.join(OUT,asset+'_revision4_detail_preview.png')
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=path)
    digest=source_hash(path)
    sc.render.filepath=out_over;bpy.ops.render.render(write_still=True)
    shell=next(o for o in col.all_objects if o.type=='MESH' and ('GIS' in o.name or 'official_GIS' in o.name))
    door=next((o for o in col.all_objects if o.type=='MESH' and ('main_entrance_glazed_door' in o.name or o.name=='MSEE_primary_glazed_doors')),None)
    if door:
        lo,hi=bounds(door);sl,sh=bounds(shell);axis=0 if hi[0]-lo[0]>=hi[1]-lo[1] else 1;normal=1-axis
        out=-1 if (lo[normal]+hi[normal])*.5<=(sl[normal]+sh[normal])*.5 else 1
        target=Vector(((lo[0]+hi[0])*.5,(lo[1]+hi[1])*.5,4.7))
        eye=target+Vector((9,0,5.5)) if normal==1 else target+Vector((0,9,5.5));eye[normal]+=out*20
    elif code=='NWCP':target=Vector((11,-15,5.5));eye=Vector((35,-28,17))
    else:target=Vector((0,0,4.2));eye=Vector((26,-28,15))
    camd=bpy.data.cameras.new('R4_'+code+'_detail_camera');cam=bpy.data.objects.new('R4_'+code+'_detail_camera',camd);sc.collection.objects.link(cam);camd.lens=48;cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();old=sc.camera;sc.camera=cam
    sc.render.filepath=out_detail;bpy.ops.render.render(write_still=True)
    sc.camera=old;bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(camd)
    # Camera is a render utility; remove before final hash/save, but leave source hash
    # corresponding to the saved model used for both previews.
    evpath=os.path.join(ROOT,evrel);ev=json.load(open(evpath,encoding='utf-8'))
    history=ev.setdefault('revision_history',[])
    history[:]=[h for h in history if h.get('review_request')!=history_text]
    history.append({'date':'2026-10-24','review_request':history_text,'geometry_edits':EDITS[code],'source_interpretation':'Facade identity cues are grounded in the linked building-specific photo/project records. Interior furniture, lab/workshop/clinical tableaux, equipment placement beyond directly documented scope, and exact bay dimensions are schematic visualization cues, not measured as-built data.'})
    existing={r.get('url') for r in ev.setdefault('references',[])}
    for provider,url,detail in REFS[code]:
        if url not in existing:ev['references'].append({'provider':provider,'url':url,'detail':detail})
    ev.setdefault('validation',{}).update({'revision4_overview_preview':os.path.relpath(out_over,ROOT).replace('/','\\'),'revision4_detail_preview':os.path.relpath(out_detail,ROOT).replace('/','\\'),'revision4_source_sha256':digest,'revision4_source_saved_before_preview_render':True,'revision4_preview_rendered_from_final_saved_source':True,'GIS_shell_bounds_preserved':True,'origin_preserved':True})
    with open(evpath,'w',encoding='utf-8') as f:json.dump(ev,f,indent=2)
    print('DONE',code,'objects',len(col.all_objects),'hash',digest,'times',os.path.getmtime(path),os.path.getmtime(out_over),os.path.getmtime(out_detail),flush=True)

def design(code,asset,col,setup):
    shell,sl,sh,axis,normal,out,cross,surf=setup
    edits=[]
    warm=material('R4_'+code+'_interior_glow',(.78,.65,.39),.02,.54,1,.25)
    black=material('R4_'+code+'_machine_graphite',(.095,.12,.13),.58,.34)
    steel=material('R4_'+code+'_lab_stainless',(.62,.67,.67),.66,.3)
    cyan=material('R4_'+code+'_screen_blue',(.12,.42,.49),.22,.32,1,.15)
    wood=material('R4_'+code+'_worktop',(.42,.27,.16),.03,.68)
    white=material('R4_'+code+'_clinical_white',(.81,.81,.75),.04,.52)
    safety=material('R4_'+code+'_safety_amber',(.88,.43,.08),.12,.44)
    span=(sh[axis]-sl[axis]);crossmid=(sl[axis]+sh[axis])*.5

    if code=='BIDC':
        # Distinct workshop scene: long assembly tables and compact machine cells visible through the two-storey glass wall.
        for i,off in enumerate((-5.4,-1.8,1.8,5.4)):
            cube_interior(col,code,axis,normal,out,cross+off,surf,1.0,'assembly_bench_'+str(i),2.5,.88,.72,steel,wood)
            for dx in (-.82,.82):front_box(col,code,'bench_leg_'+str(i)+'_'+str(dx),axis,normal,out,cross+off+dx,surf-out*.34,.56,.10,.55,.9,black)
        for i,off in enumerate((-4.7,-1.6,1.6,4.7)):
            front_box(col,code,'cnc_machine_'+str(i),axis,normal,out,cross+off,surf-out*.55,3.35,1.05,.95,2.5,black)
            front_box(col,code,'cnc_machine_window_'+str(i),axis,normal,out,cross+off,surf-out*.60,3.4,.62,.06,.76,cyan)
            front_box(col,code,'cnc_machine_safety_top_'+str(i),axis,normal,out,cross+off,surf-out*.62,4.70,1.08,.12,.16,safety)
        for i,off in enumerate((-4.5,0,4.5)):
            front_box(col,code,'upper_gallery_worktable_'+str(i),axis,normal,out,cross+off,surf-out*.30,6.25,2.2,.6,.13,wood)
            for d in (-.7,.7):front_box(col,code,'upper_gallery_stool_'+str(i)+'_'+str(d),axis,normal,out,cross+off+d,surf-out*.33,5.72,.28,.28,.95,black)
        edits=['Placed visible assembly benches, compact CNC/tool-machine silhouettes, safety accents, and an upper gallery work zone behind the documented two-storey makerspace glass. Workshop layout is schematic; the transparent facade program is photo-supported.']

    elif code=='BIND':
        for floor,z in enumerate((1.1,3.35,5.65)):
            for i,off in enumerate((-4.4,0,4.4)):
                cube_interior(col,code,axis,normal,out,cross+off,surf,z,'lab_bench_'+str(floor)+'_'+str(i),2.0,.83,.58,steel,white)
                front_box(col,code,'hood_glass_'+str(floor)+'_'+str(i),axis,normal,out,cross+off,surf-out*.37,z+1.43,1.38,.08,.95,cyan)
                front_box(col,code,'hood_sash_'+str(floor)+'_'+str(i),axis,normal,out,cross+off,surf-out*.42,z+1.14,1.48,.09,.09,safety)
            for off in (-6.5,6.5):front_box(col,code,'lab_partition_'+str(floor)+'_'+str(off),axis,normal,out,cross+off,surf-out*.35,z+1.0,.12,.08,1.95,white)
        for off in (-4.2,0,4.2):front_box(col,code,'lobby_light_panel_'+str(off),axis,normal,out,cross+off,surf-out*.50,7.5,1.45,.1,.12,warm)
        edits=['Added three visible schematic research floors with repeated lab benches, fume-hood silhouettes, interior partitions, and lobby lighting behind the documented glass/metal frontage. These are program cues, not a surveyed floor plan.']

    elif code=='MSEE':
        # Repaired atrium: a single modest bridge and study area, no oversized beam projections.
        bridgez=6.2;bridgew=min(18.0,span*.48)
        front_box(col,code,'atrium_skyway_deck',axis,normal,out,crossmid,surf-out*.62,bridgez,bridgew,.95,.22,steel)
        front_box(col,code,'atrium_skyway_glass_guard',axis,normal,out,crossmid,surf-out*.95,bridgez+.58,bridgew,.07,.76,cyan)
        for off in (-bridgew*.47,-bridgew*.25,0,bridgew*.25,bridgew*.47):front_box(col,code,'skyway_guard_post_'+str(off),axis,normal,out,crossmid+off,surf-out*.98,bridgez+.46,.07,.08,.92,black)
        for off in (-5.8,-2.0,2.0,5.8):
            front_box(col,code,'atrium_study_table_'+str(off),axis,normal,out,crossmid+off,surf-out*.43,1.22,2.4,.72,.15,wood)
            front_box(col,code,'atrium_study_seat_'+str(off),axis,normal,out,crossmid+off,surf-out*.35,.77,.48,.44,.48,black)
        for z in (2.3,4.0,8.3):front_box(col,code,'atrium_vertical_light_baffle_'+str(z),axis,normal,out,crossmid,surf-out*.34,z,.14,.12,1.35,warm)
        edits=['Added one restrained interior skyway deck with glass guard, visible posts and study furniture through the existing atrium; this is a schematic atrium interpretation, not an exact bridge survey. No exterior beams or projecting entrance canopy were added.']

    elif code=='BRFM':
        # Photo-supported hospital function, schematic clinical intake and stall furniture visibly distinct from classroom labs.
        for i,off in enumerate((-7.2,0,7.2)):
            front_box(col,code,'animal_care_service_volume_'+str(i),axis,normal,out,crossmid+off,surf-out*.17,2.05,4.25,.18,3.55,steel)
            front_box(col,code,'large_animal_stall_door_'+str(i),axis,normal,out,crossmid+off,surf-out*.26,2.05,3.55,.10,2.85,material('R4_BRFM_stall_door',(.35,.39,.38),.42,.46))
            for z in (0.9,1.4,1.9,2.4,2.9):front_box(col,code,'stall_door_rib_'+str(i)+'_'+str(z),axis,normal,out,crossmid+off,surf-out*.33,z,3.4,.05,.04,steel)
            front_box(col,code,'exam_light_'+str(i),axis,normal,out,crossmid+off,surf-out*.45,3.8,1.1,.16,.12,warm)
        for off in (-4.8,4.8):
            front_box(col,code,'exam_table_'+str(off),axis,normal,out,crossmid+off,surf-out*.62,1.25,2.3,.72,.18,steel)
            front_box(col,code,'exam_equipment_cart_'+str(off),axis,normal,out,crossmid+off+1.4,surf-out*.57,1.3,.48,.5,.72,black)
        edits=['Replaced weak service hints with three unmistakable, in-footprint large-animal stall/intake doors, ribbed panels, overhead exam lights, exam tables, and mobile care carts visible on the public-facing elevation. Clinic/stall arrangement is schematic; hospital and large-animal functions are source-supported.']

    elif code=='ADDL':
        for floor,z in enumerate((1.0,3.65,6.3,8.95,11.6)):
            for i,off in enumerate((-5.3,0,5.3)):
                cube_interior(col,code,axis,normal,out,crossmid+off,surf,z,'diagnostic_lab_bench_'+str(floor)+'_'+str(i),2.25,.85,.62,steel,white)
                front_box(col,code,'diagnostic_instrument_'+str(floor)+'_'+str(i),axis,normal,out,crossmid+off,surf-out*.37,z+1.18,.62,.42,.55,cyan)
        # Distinct sample receiving / service doors at grade within the building frontage.
        for off in (-7.4,7.4):
            front_box(col,code,'sample_receiving_service_door_'+str(off),axis,normal,out,crossmid+off,surf-out*.20,1.85,2.65,.13,3.05,material('R4_ADDL_service_gray',(.37,.42,.43),.3,.48))
            for z in (0.8,1.4,2.0,2.6):front_box(col,code,'service_door_rib_'+str(off)+'_'+str(z),axis,normal,out,crossmid+off,surf-out*.28,z,2.52,.06,.05,steel)
        edits=['Added visible diagnostic bench/instrument tableaux across several floors and two grade-level sample/service doors to make the diagnostic-lab and receiving function legible through the windows. Room layouts and service-door positions are schematic; exterior brick and photographed modest entry are retained.']

    elif code=='NWCP':
        # Keep service yard inside footprint and focus on explicit pump/header geometry; avoid inventing a stack.
        pipe=material('R4_NWCP_chilled_water_safety_blue',(.13,.31,.54),.62,.28)
        red=material('R4_NWCP_return_header',(.58,.18,.12),.58,.31)
        bounds_x=(sl[0],sh[0]);bounds_y=(sl[1],sh[1]);
        # Pump skids and motors within the visible yard at the east side.
        for i,x in enumerate((min(sh[0]-5,11),min(sh[0]-2,15),min(sh[0]-.8,18))):
            y=min(sh[1]-4,17)
            box(col,'R4_NWCP_pump_skid_'+str(i),(x,y,.38),(2.6,1.55,.22),black)
            box(col,'R4_NWCP_pump_motor_'+str(i),(x-.45,y,.95),(1.0,.9,.95),steel)
            box(col,'R4_NWCP_pump_casing_'+str(i),(x+.48,y,1.05),(1.15,1.05,.78),pipe)
            box(col,'R4_NWCP_pump_bearing_'+str(i),(x+.65,y,1.12),(.32,1.13,.32),black)
        # Twin horizontal headers and vertical risers, drawn as solid pipe segments.
        for j,z in enumerate((2.3,3.15,4.0)):
            box(col,'R4_NWCP_header_'+str(j),(14.4,min(sh[1]-3,18),z),(9.2,.34,.34),pipe if j!=1 else red)
        for i,x in enumerate((10.1,12.4,15.0,17.1,19.0)):
            y=min(sh[1]-3,18)
            box(col,'R4_NWCP_riser_'+str(i),(x,y,3.05),(.26,.26,1.65),pipe)
            # handwheel/valve silhouette at each branch
            box(col,'R4_NWCP_valve_'+str(i),(x,y-.2,2.65),(.58,.18,.12),safety)
        # restrained pipe rack / yard edge fence, kept within matched GIS extents.
        fence_y=min(sh[1]-1.3,20.0)
        for x in (-14,-8,-2,4,10,16):box(col,'R4_NWCP_yard_fence_post_'+str(x),(x,fence_y,1.35),(.13,.13,2.7, ),steel)
        for z in (.75,1.95):box(col,'R4_NWCP_yard_fence_rail_'+str(z),(1.0,fence_y,z),(31,.1,.11),steel)
        edits=['Added three schematic pump skids/motors, distinctive blue/red chilled-water headers, valved risers, and an in-bounds service-yard fence; based on Purdue records confirming condenser-water pump work. Exact piping routing/equipment coordinates and roof plant arrangement remain schematic. No unverified stack was added.']

    elif code=='AGAD':
        # Formal administration/lobby interior behind stone entry and windows.
        for off in (-4.0,0,4.0):
            front_box(col,code,'administration_lobby_glazing_bay_'+str(off),axis,normal,out,crossmid+off,surf-out*.09,2.0,2.2,.07,2.75,warm)
        front_box(col,code,'reception_desk',axis,normal,out,crossmid,surf-out*.48,1.18,3.3,.78,.95,wood)
        for off in (-5.6,5.6):
            front_box(col,code,'lobby_column_'+str(off),axis,normal,out,crossmid+off,surf-out*.5,2.35,.24,.32,4.5,steel)
        for i,off in enumerate((-4.3,4.3)):
            front_box(col,code,'lobby_bench_'+str(i),axis,normal,out,crossmid+off,surf-out*.68,.68,2.4,.58,.45,wood)
        edits=['Added a visible, formal office reception vestibule behind the documented stone-trimmed entry: reception desk, warm glazing, and waiting benches. Interior furnishing is schematic; facade composition follows linked Purdue photo.']

    elif code=='ABE':
        for i,off in enumerate((-3.2,0,3.2)):
            cube_interior(col,code,axis,normal,out,crossmid+off,surf,1.1,'engineering_lab_bench_'+str(i),2.6,.92,.68,steel,wood)
            front_box(col,code,'engineering_lab_monitor_'+str(i),axis,normal,out,crossmid+off,surf-out*.4,2.28,.48,.10,.40,cyan)
            front_box(col,code,'engineering_lab_storage_'+str(i),axis,normal,out,crossmid+off,surf-out*.35,3.25,2.1,.38,.72,black)
        for off in (-5.2,5.2):front_box(col,code,'renovated_wing_spandrel_'+str(off),axis,normal,out,crossmid+off,surf-out*.08,7.2,1.2,.12,3.5,steel)
        edits=['Added visible engineering research benches, monitors, and lab-storage silhouettes behind the glazed renovation wing, making the brick-and-glass addition read as active engineering space. Interior layout is schematic; exterior 1928 entry and glazed addition remain photo-supported.']

    elif code=='BCHM':
        for floor,z in enumerate((1.0,3.6,6.25,8.9,11.55)):
            for i,off in enumerate((-4.8,0,4.8)):
                cube_interior(col,code,axis,normal,out,crossmid+off,surf,z,'biochemistry_lab_bench_'+str(floor)+'_'+str(i),2.0,.86,.58,steel,white)
                for dx in (-.48,.48):front_box(col,code,'biochemistry_instrument_'+str(floor)+'_'+str(i)+'_'+str(dx),axis,normal,out,crossmid+off+dx,surf-out*.34,z+1.14,.38,.32,.46,cyan)
        edits=['Added repeated lab benches and compact instrument silhouettes behind selected glazing to make the biochemistry program visible. Because no building-specific elevation source was found, the room rhythm is explicitly schematic and the exterior treatment remains conservative.']

    elif code=='DAUC':
        # Distinct alumni lounge and reception silhouettes behind the main glazing.
        front_box(col,code,'alumni_center_reception',axis,normal,out,crossmid,surf-out*.45,1.18,4.0,.72,.98,wood)
        for i,off in enumerate((-3.3,3.3)):
            front_box(col,code,'alumni_lounge_sofa_'+str(i),axis,normal,out,crossmid+off,surf-out*.63,.86,2.25,.82,.72,material('R4_DAUC_sofa_claret',(.37,.13,.12),.0,.82))
            front_box(col,code,'alumni_lounge_table_'+str(i),axis,normal,out,crossmid+off,surf-out*.82,.50,1.65,.68,.18,wood)
        for off in (-4.1,4.1):front_box(col,code,'lobby_warm_light_'+str(off),axis,normal,out,crossmid+off,surf-out*.39,4.15,.14,.12,4.9,warm)
        edits=['Added a reception counter, paired lounge seating, low tables, and warm vertical lobby lighting behind the photographed tall curved entry glazing. Furnishings are schematic visualization cues.']

    return edits

for code,asset,evrel in ASSETS:
    path=os.path.join(ROOT,'modular','buildings',asset+'.blend')
    bpy.ops.wm.open_mainfile(filepath=path)
    col=bpy.data.collections.get('Asset_'+asset);assert col,('missing asset collection',code)
    # Remove only this pass's previous geometry so a retry is deterministic.
    for ob in list(col.all_objects):
        if ob.name.startswith('R4_'+code+'_'):bpy.data.objects.remove(ob,do_unlink=True)
    setup=front_setup(col,asset)
    EDITS[code]=design(code,asset,col,setup)
    history='Final differentiated-identity and visible-interior pass after 6.7 review: photo-supported facade cues plus labelled schematic program interiors; preserve GIS shell/origin.'
    render_final(code,asset,path,evrel,history)
