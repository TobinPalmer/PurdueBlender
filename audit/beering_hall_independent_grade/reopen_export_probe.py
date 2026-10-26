import bpy,json
from pathlib import Path
root=Path(r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender')
out=root/'audit/beering_hall_independent_grade'
probe=out/'collection_export_probe.blend'
bpy.ops.wm.open_mainfile(filepath=str(probe))
coll=bpy.data.collections.get('Asset_beering_hall')
assert coll is not None and len(coll.all_objects)==1162
assert all(o.type not in {'CAMERA','LIGHT'} for o in coll.all_objects)
external=[]
for obj in coll.all_objects:
 for slot in obj.material_slots:
  mat=slot.material
  if mat and mat.use_nodes:
   for node in mat.node_tree.nodes:
    if node.type=='TEX_IMAGE' and node.image and node.image.filepath and not node.image.packed_file:
     external.append(node.image.filepath)
assert not external
result={'reopened_export':str(probe),'collection':coll.name,'object_count':len(coll.all_objects),'object_names':sorted(o.name for o in coll.all_objects),'camera_light_objects':[o.name for o in coll.all_objects if o.type in {'CAMERA','LIGHT'}],'external_unpacked_images':external,'linked_library_paths':[lib.filepath for lib in bpy.data.libraries if lib.filepath]}
(out/'export_probe_result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in {'object_names'}},indent=2))
