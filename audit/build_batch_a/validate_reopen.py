import bpy,os,json,math
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
rows=[]
items=[
('agricultural_administration_building','Asset_agricultural_administration_building'),
('agricultural_and_biological_engineering_abe','Asset_agricultural_and_biological_engineering_abe'),
('animal_disease_diagnostic_laboratory','Asset_animal_disease_diagnostic_laboratory'),
('bechtel_innovation_design_center_bidc','Asset_bechtel_innovation_design_center_bidc'),
('bindley_bioscience_center','Asset_bindley_bioscience_center'),
('biochemistry_building','Asset_biochemistry_building'),
('david_and_bonnie_brunner_farm_animal_hospital','Asset_david_and_bonnie_brunner_farm_animal_hospital'),
('dauch_alumni_center','Asset_dauch_alumni_center')]
for asset,colname in items:
 path=os.path.join(ROOT,'modular','buildings',asset+'.blend');bpy.ops.wm.open_mainfile(filepath=path);col=bpy.data.collections.get(colname)
 objs=list(col.all_objects) if col else [];meshes=[o for o in objs if o.type=='MESH'];mats={m for o in objs if hasattr(o.data,'materials') for m in o.data.materials if m}
 coords=[]
 for o in meshes:
  for v in o.data.vertices: coords.append(o.matrix_world@v.co)
 if coords:
  bounds=[[round(min(v[i] for v in coords),3),round(max(v[i] for v in coords),3)] for i in range(3)]
 else:bounds=[]
 tex_mats=[]
 for m in sorted(mats,key=lambda x:x.name):
  nodes=list(m.node_tree.nodes) if m.use_nodes and m.node_tree else []
  tex_mats.append({'name':m.name,'noise':any(n.type=='TEX_NOISE' for n in nodes),'bump':any(n.type=='BUMP' for n in nodes),'principled':any(n.type=='BSDF_PRINCIPLED' for n in nodes)})
 ext=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath]
 rows.append({'asset':asset,'path':os.path.relpath(path,ROOT),'collection_found':bool(col),'collection':colname,'object_count':len(objs),'mesh_count':len(meshes),'bounds_local_m':bounds,'materials':tex_mats,'external_image_paths':ext,'pass':bool(col and meshes and len(mats)>=5 and bounds and bounds[2][0]>=-1.0 and all(m['noise'] and m['bump'] for m in tex_mats))})
 print(rows[-1],flush=True)
out=os.path.join(ROOT,'audit','build_batch_a','reopen_validation.json');json.dump({'retrieved':'2026-10-24','results':rows,'all_pass':all(r['pass'] and not r['external_image_paths'] for r in rows)},open(out,'w'),indent=2)
print('VALIDATION',out,flush=True)
