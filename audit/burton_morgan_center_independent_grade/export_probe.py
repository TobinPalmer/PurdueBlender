import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
path=root/'audit/burton_morgan_center/burton_morgan_center_collection_export.blend'
manifest=json.loads((root/'modular/manifest.json').read_text(encoding='utf-8'))
contract=next(a for a in manifest['assets'] if a['id']=='burton_morgan_center')
with bpy.data.libraries.load(str(path),link=False) as (src,dst):
    assert contract['collection'] in src.collections
    dst.collections=[contract['collection']]
col=bpy.data.collections.get(contract['collection'])
assert col is not None
objects=list(col.all_objects)
mesh_count=sum(o.type=='MESH' for o in objects)
canonical={o.get('manifest_object_name',o.name) for o in objects}
external=[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]
result={'export_opened':True,'collection':col.name,'object_count':len(objects),'mesh_count':mesh_count,'manifest_object_count':contract['object_count'],'manifest_names_match':canonical==set(contract['objects']),'unpacked_external_images':external}
assert len(objects)==contract['object_count'] and canonical==set(contract['objects']) and not external
(root/'audit/burton_morgan_center_independent_grade/export_probe.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
