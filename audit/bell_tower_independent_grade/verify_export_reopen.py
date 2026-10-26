import bpy, json
from pathlib import Path
expected="Asset_bell_tower"
p=Path(__file__).with_name("collection_export_probe.blend")
bpy.ops.wm.open_mainfile(filepath=str(p))
c=bpy.data.collections.get(expected)
assert c is not None
assert len(c.objects)==578
assert all(o.type not in {"CAMERA","LIGHT"} for o in c.objects)
result={"reopened_collection":c.name,"object_count":len(c.objects),"camera_light_objects":[(o.name,o.type) for o in c.objects if o.type in {"CAMERA","LIGHT"}],"object_names":sorted(o.name for o in c.objects)}
Path(__file__).with_name("collection_export_probe_result.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in result.items() if k!="object_names"}))
