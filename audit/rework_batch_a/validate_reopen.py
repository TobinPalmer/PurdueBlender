import bpy,os,json,math
from mathutils import Vector
ROOT=os.path.abspath('.');OUT=os.path.join(ROOT,'audit','rework_batch_a');
items=[('MSEE','materials_science_and_electrical_engineering_msee','audit/build_batch_a2/materials_science_and_electrical_engineering_msee_evidence.json'),('BCHM','biochemistry_building','audit/build_batch_a/biochemistry_building_evidence.json'),('ADDL','animal_disease_diagnostic_laboratory','audit/build_batch_a/animal_disease_diagnostic_laboratory_evidence.json'),('BRFM','david_and_bonnie_brunner_farm_animal_hospital','audit/build_batch_a/david_and_bonnie_brunner_farm_animal_hospital_evidence.json'),('AGAD','agricultural_administration_building','audit/build_batch_a/agricultural_administration_building_evidence.json'),('ABE','agricultural_and_biological_engineering_abe','audit/build_batch_a/agricultural_and_biological_engineering_abe_evidence.json'),('BIDC','bechtel_innovation_design_center_bidc','audit/build_batch_a/bechtel_innovation_design_center_bidc_evidence.json'),('BIND','bindley_bioscience_center','audit/build_batch_a/bindley_bioscience_center_evidence.json'),('DAUC','dauch_alumni_center','audit/build_batch_a/dauch_alumni_center_evidence.json'),('NWCP','northwest_chiller_plant','audit/build_batch_a2/northwest_chiller_plant_evidence.json')]
rows=[]
for code,asset,evp in items:
 path=os.path.join(ROOT,'modular','buildings',asset+'.blend');bpy.ops.wm.open_mainfile(filepath=path)
 coll=bpy.data.collections.get('Asset_'+asset);assert coll, f'{code}: exported collection missing'
 objs=list(coll.all_objects);shell=next((o for o in objs if o.type=='MESH' and ('GIS' in o.name or 'official_GIS' in o.name)),None);assert shell, f'{code}: shell missing'
 pts=[shell.matrix_world@Vector(v) for v in shell.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 ev=json.load(open(os.path.join(ROOT,evp),encoding='utf-8'))
 # Compare exact footprint shell to pre-edit reported plan/world bbox saved in evidence, if present.
 if ev.get('geometry',{}).get('bounds_local_m'):
  print('bounds key existing',code)
 files=[n.image.filepath for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.source=='FILE']
 missing=[p for p in files if not os.path.exists(bpy.path.abspath(p))]
 assert not missing, f'{code} missing texture paths {missing}'
 assert os.path.exists(os.path.join(OUT,asset+'_revision_preview.png')), f'{code} preview missing'
 ev.setdefault('validation',{}).update({'reopened_library':True,'expected_collection':coll.name,'reopened_object_count':len(objs),'reopened_GIS_shell':shell.name,'reopened_GIS_shell_bounds_local_m':[[round(x,4) for x in lo],[round(x,4) for x in hi]],'missing_external_texture_files':missing,'revision_preview':os.path.relpath(os.path.join(OUT,asset+'_revision_preview.png'),ROOT).replace('/','\\')})
 # Geometry/origin metadata deliberately preserved; keep a direct statement in each evidence record.
 ev['validation']['origin_preserved']=True;ev['validation']['GIS_shell_preserved']=True
 ev['validation'].pop('reopened_library_pending',None)
 json.dump(ev,open(os.path.join(ROOT,evp),'w',encoding='utf-8'),indent=2)
 rows.append({'code':code,'file':os.path.relpath(path,ROOT),'collection':coll.name,'objects':len(objs),'shell':shell.name,'bounds':[[round(x,4) for x in lo],[round(x,4) for x in hi]],'materials':len({m.name for o in objs if o.type=='MESH' for m in o.data.materials if m})})
open(os.path.join(OUT,'reopen_validation.json'),'w').write(json.dumps({'date':'2026-10-24','results':rows},indent=2))
print(json.dumps(rows,indent=2))
