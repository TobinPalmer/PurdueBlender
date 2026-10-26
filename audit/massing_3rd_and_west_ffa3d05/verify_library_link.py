import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular'/'buildings'/'massing_3rd_and_west_ffa3d05.blend'
OUT=ROOT/'audit'/'massing_3rd_and_west_ffa3d05'/'linked_collection_probe.json'
expected='Asset_massing_3rd_and_west_ffa3d05'
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(ASSET),link=True) as (src,dst):
 assert expected in src.collections, f'{expected} not exported; found {src.collections}'
 dst.collections=[expected]
linked=next((c for c in bpy.data.collections if c.name.startswith(expected)),None)
assert linked is not None
objects=list(linked.all_objects)
assert len(objects)==19 and all(o.type=='MESH' for o in objects)
result={'status':'PASS','asset_path':str(ASSET),'collection':linked.name,'linked_object_count':len(objects),'mesh_object_count':sum(o.type=='MESH' for o in objects),'linked_collection_path':linked.library.filepath if linked.library else None}
OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
