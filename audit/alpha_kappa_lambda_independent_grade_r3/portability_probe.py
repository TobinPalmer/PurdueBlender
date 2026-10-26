import bpy, json
from pathlib import Path
asset=Path(r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender\modular\buildings\massing_alpha_kappa_lambda_88dda6c.blend')
out=Path(r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender\audit\alpha_kappa_lambda_independent_grade_r3\portability_probe.json')
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(asset), link=True) as (data_from,data_to):
    data_to.collections=['Asset_massing_alpha_kappa_lambda_88dda6c']
linked=[c for c in data_to.collections if c]
for c in linked: bpy.context.scene.collection.children.link(c)
objs=[o for c in linked for o in c.objects]
r={'loaded_from_fresh_empty_file':True,'linked_collection_names':[c.name for c in linked],'linked_object_names':[o.name for o in objs],'linked_mesh_object_count':sum(o.type=='MESH' for o in objs),'linked_mesh_vertex_count':sum(len(o.data.vertices) for o in objs if o.type=='MESH'),'external_image_paths':[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]}
r['result']='PASS' if r['linked_collection_names']==['Asset_massing_alpha_kappa_lambda_88dda6c'] and r['linked_object_names']==['Alpha Kappa Lambda'] and not r['external_image_paths'] else 'FAIL'
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8'); print(json.dumps(r,indent=2))
