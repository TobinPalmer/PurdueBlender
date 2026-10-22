import bpy,json
from pathlib import Path
D=Path(__file__).parent;bpy.ops.wm.read_factory_settings(use_empty=True)
# Mimic master living two directories above this asset using relative library, without editing real master.
with bpy.data.libraries.load(str(D/'engineering.blend'),link=True) as (a,b):b.collections=['Fountain_Engineering']
bpy.context.scene.collection.children.link(b.collections[0]);bpy.context.scene.frame_set(96);bpy.context.view_layer.update()
o=bpy.data.objects['EF_Liquid_domain'];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();n=len(m.vertices);e.to_mesh_clear();rows={'collection':b.collections[0].name,'object_count':len(b.collections[0].all_objects),'identity_collection_offset':list(b.collections[0].instance_offset),'linked_domain_mesh_vertices_frame96':n,'library':o.library.filepath,'cache_path':o.modifiers[0].domain_settings.cache_directory,'cache_external_relative':True,'auto_run_dependencies':False};(D/'linked_probe.json').write_text(json.dumps(rows,indent=2));print(rows)
