import bpy,os,json
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
rows=[]
for asset,colname in [('materials_science_and_electrical_engineering_msee','Asset_materials_science_and_electrical_engineering_msee'),('northwest_chiller_plant','Asset_northwest_chiller_plant')]:
 p=os.path.join(ROOT,'modular','buildings',asset+'.blend');bpy.ops.wm.open_mainfile(filepath=p);c=bpy.data.collections.get(colname);objs=list(c.all_objects) if c else [];meshes=[o for o in objs if o.type=='MESH'];coords=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];bounds=[[round(min(v[i] for v in coords),3),round(max(v[i] for v in coords),3)] for i in range(3)] if coords else [];mats={m for o in objs if hasattr(o.data,'materials') for m in o.data.materials if m};textures=[]
 for m in sorted(mats,key=lambda z:z.name):
  ns=list(m.node_tree.nodes) if m.use_nodes and m.node_tree else [];textures.append({'name':m.name,'noise':any(n.type=='TEX_NOISE' for n in ns),'bump':any(n.type=='BUMP' for n in ns),'principled':any(n.type=='BSDF_PRINCIPLED' for n in ns)})
 ex=[x.filepath for x in bpy.data.images if x.source=='FILE' and x.filepath];ok=bool(c and meshes and len(mats)>=7 and bounds and bounds[2][0]>-1 and all(t['noise'] and t['bump'] and t['principled'] for t in textures) and not ex);rows.append({'asset':asset,'collection':colname,'collection_found':bool(c),'objects':len(objs),'meshes':len(meshes),'materials':textures,'bounds_local_m':bounds,'external_image_paths':ex,'pass':ok});print(rows[-1],flush=True)
out=os.path.join(ROOT,'audit','build_batch_a2','reopen_validation.json');json.dump({'results':rows,'all_pass':all(x['pass'] for x in rows)},open(out,'w'),indent=2);print('VALIDATION',out,flush=True)
