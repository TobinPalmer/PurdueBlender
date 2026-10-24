import bpy, os, json, hashlib
from mathutils import Vector
ROOT=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
OUT=os.path.join(ROOT,'audit','rework_batch_a')
items=[
 ('AGAD','agricultural_administration_building','audit/build_batch_a/agricultural_administration_building_evidence.json'),
 ('ABE','agricultural_and_biological_engineering_abe','audit/build_batch_a/agricultural_and_biological_engineering_abe_evidence.json'),
 ('ADDL','animal_disease_diagnostic_laboratory','audit/build_batch_a/animal_disease_diagnostic_laboratory_evidence.json'),
 ('BCHM','biochemistry_building','audit/build_batch_a/biochemistry_building_evidence.json'),
 ('BIDC','bechtel_innovation_design_center_bidc','audit/build_batch_a/bechtel_innovation_design_center_bidc_evidence.json'),
 ('BIND','bindley_bioscience_center','audit/build_batch_a/bindley_bioscience_center_evidence.json'),
 ('BRFM','david_and_bonnie_brunner_farm_animal_hospital','audit/build_batch_a/david_and_bonnie_brunner_farm_animal_hospital_evidence.json'),
 ('DAUC','dauch_alumni_center','audit/build_batch_a/dauch_alumni_center_evidence.json'),
 ('MSEE','materials_science_and_electrical_engineering_msee','audit/build_batch_a2/materials_science_and_electrical_engineering_msee_evidence.json'),
 ('NWCP','northwest_chiller_plant','audit/build_batch_a2/northwest_chiller_plant_evidence.json'),]
prior=json.load(open(os.path.join(OUT,'reopen_validation.json'),encoding='utf-8'));prior_by={r['code']:r for r in prior['results']}
def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
rows=[]
for code,asset,evrel in items:
 path=os.path.join(ROOT,'modular','buildings',asset+'.blend');assert os.path.isfile(path),path
 bpy.ops.wm.open_mainfile(filepath=path)
 col=bpy.data.collections.get('Asset_'+asset);assert col,(code,'collection missing')
 objs=list(col.all_objects)
 shell=next((o for o in objs if o.type=='MESH' and ('GIS' in o.name or 'official_GIS' in o.name)),None);assert shell,(code,'GIS shell missing')
 ps=[shell.matrix_world@Vector(v) for v in shell.bound_box];lo=[min(p[i] for p in ps) for i in range(3)];hi=[max(p[i] for p in ps) for i in range(3)]
 bounds=[[round(v,4) for v in lo],[round(v,4) for v in hi]]
 old=prior_by[code]['bounds'];assert bounds==old,(code,'GIS shell bounds changed',bounds,old)
 mats={m.name for o in objs for m in getattr(o.data,'materials',[]) if m};assert mats,(code,'no linked materials')
 tex=[n.image.filepath for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.source=='FILE']
 missing=[p for p in tex if not os.path.exists(bpy.path.abspath(p))];assert not missing,(code,'missing texture files',missing)
 over=os.path.join(OUT,asset+'_revision4_preview.png');detail=os.path.join(OUT,asset+'_revision4_detail_preview.png')
 assert os.path.isfile(over) and os.path.isfile(detail),(code,'preview missing')
 sm=os.path.getmtime(path);om=os.path.getmtime(over);dm=os.path.getmtime(detail);assert om>sm and dm>sm,(code,'preview older than source',sm,om,dm)
 evpath=os.path.join(ROOT,evrel);ev=json.load(open(evpath,encoding='utf-8'));digest=sha(path)
 assert ev.get('validation',{}).get('revision4_source_sha256')==digest,(code,'source hash mismatch')
 ev['validation'].update({'revision4_reopened_library':True,'revision4_collection':col.name,'revision4_object_count':len(objs),'revision4_GIS_shell':shell.name,'revision4_GIS_shell_bounds_local_m':bounds,'revision4_bounds_match_initial':True,'revision4_linked_material_count':len(mats),'revision4_missing_external_textures':missing,'revision4_source_sha256_verified':digest,'revision4_overview_newer_than_source':True,'revision4_detail_newer_than_source':True})
 with open(evpath,'w',encoding='utf-8') as f:json.dump(ev,f,indent=2)
 rows.append({'code':code,'file':os.path.relpath(path,ROOT),'collection':col.name,'objects':len(objs),'linked_materials':len(mats),'GIS_shell':shell.name,'bounds':bounds,'bounds_unchanged':True,'missing_textures':missing,'source_sha256':digest,'overview':os.path.relpath(over,ROOT),'detail':os.path.relpath(detail,ROOT),'preview_timestamps_after_source':True})
result={'date':'2026-10-24','validation':'All 10 source libraries reopened; export collection/GIS shell present; GIS shell bounds match initial pass; linked materials and image paths checked; source hashes match evidence; final overview/detail previews postdate final saves.','results':rows}
with open(os.path.join(OUT,'reopen_validation_fourth.json'),'w',encoding='utf-8') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
