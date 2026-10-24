import bpy, os, json
from mathutils import Vector
ROOT=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
OUT=os.path.join(ROOT,'audit','rework_batch_a')
items=[
 ('MSEE','materials_science_and_electrical_engineering_msee','audit/build_batch_a2/materials_science_and_electrical_engineering_msee_evidence.json'),
 ('BCHM','biochemistry_building','audit/build_batch_a/biochemistry_building_evidence.json'),
 ('ADDL','animal_disease_diagnostic_laboratory','audit/build_batch_a/animal_disease_diagnostic_laboratory_evidence.json'),
 ('BRFM','david_and_bonnie_brunner_farm_animal_hospital','audit/build_batch_a/david_and_bonnie_brunner_farm_animal_hospital_evidence.json'),
 ('AGAD','agricultural_administration_building','audit/build_batch_a/agricultural_administration_building_evidence.json'),
 ('ABE','agricultural_and_biological_engineering_abe','audit/build_batch_a/agricultural_and_biological_engineering_abe_evidence.json'),
 ('BIDC','bechtel_innovation_design_center_bidc','audit/build_batch_a/bechtel_innovation_design_center_bidc_evidence.json'),
 ('BIND','bindley_bioscience_center','audit/build_batch_a/bindley_bioscience_center_evidence.json'),
 ('DAUC','dauch_alumni_center','audit/build_batch_a/dauch_alumni_center_evidence.json'),
 ('NWCP','northwest_chiller_plant','audit/build_batch_a2/northwest_chiller_plant_evidence.json')]
prior=json.load(open(os.path.join(OUT,'reopen_validation.json'),encoding='utf-8'))
prior_by={r['code']:r for r in prior['results']}
rows=[]
for code,asset,evrel in items:
 path=os.path.join(ROOT,'modular','buildings',asset+'.blend')
 bpy.ops.wm.open_mainfile(filepath=path)
 col=bpy.data.collections.get('Asset_'+asset)
 assert col,code+' exported collection missing'
 objs=list(col.all_objects)
 shell=next((o for o in objs if o.type=='MESH' and ('GIS' in o.name or 'official_GIS' in o.name)),None)
 assert shell,code+' GIS shell missing'
 pts=[shell.matrix_world@Vector(v) for v in shell.bound_box]
 lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 bounds=[[round(v,4) for v in lo],[round(v,4) for v in hi]]
 prev=prior_by[code]['bounds']
 assert bounds==prev,(code,'GIS bounds changed',bounds,prev)
 external=[n.image.filepath for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.source=='FILE']
 missing=[p for p in external if not os.path.exists(bpy.path.abspath(p))]
 assert not missing,(code,'missing textures',missing)
 overview=os.path.join(OUT,asset+'_revision2_preview.png')
 detail=os.path.join(OUT,asset+'_revision2_detail_preview.png')
 assert os.path.exists(overview),code+' revision2 overview missing'
 if code!='NWCP': assert os.path.exists(detail),code+' revision2 detail preview missing'
 evpath=os.path.join(ROOT,evrel);ev=json.load(open(evpath,encoding='utf-8'))
 ev.setdefault('validation',{}).update({'revision2_reopened_library':True,'revision2_collection':col.name,'revision2_object_count':len(objs),'revision2_GIS_shell':shell.name,'revision2_GIS_shell_bounds_local_m':bounds,'revision2_bounds_match_previous':True,'missing_external_texture_files':missing,'revision2_overview_preview':os.path.relpath(overview,ROOT).replace('/','\\')})
 if os.path.exists(detail): ev['validation']['revision2_detail_preview']=os.path.relpath(detail,ROOT).replace('/','\\')
 ev['validation']['origin_preserved']=True;ev['validation']['GIS_shell_preserved']=True
 json.dump(ev,open(evpath,'w',encoding='utf-8'),indent=2)
 rows.append({'code':code,'file':os.path.relpath(path,ROOT),'collection':col.name,'objects':len(objs),'shell':shell.name,'bounds':bounds,'bounds_unchanged':True,'missing_textures':missing,'overview':os.path.relpath(overview,ROOT),'detail_preview':os.path.relpath(detail,ROOT) if os.path.exists(detail) else None})
result={'date':'2026-10-24','validation':'reopened all libraries; collection and GIS shell present; GIS shell bounds exactly match prior pass; no missing external image textures','results':rows}
open(os.path.join(OUT,'reopen_validation_second.json'),'w',encoding='utf-8').write(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
