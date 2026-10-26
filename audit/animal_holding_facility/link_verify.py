"""Run with Blender -b --factory-startup --python this_file.py."""
import bpy
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset = root / "modular/buildings/massing_animal_holding_facility_4733f46.blend"
out = Path(__file__).resolve().parent / "link_verification.json"
expected = "Asset_massing_animal_holding_facility_4733f46"
with bpy.data.libraries.load(str(asset), link=True) as (data_from, data_to):
    assert expected in data_from.collections
    data_to.collections = [expected]
linked = data_to.collections[0]
assert linked is not None and linked.name == expected
bpy.context.scene.collection.children.link(linked)
members = list(linked.objects)
assert len(members) == 1 and members[0].name == "Animal Holding Facility"
assert all(abs(float(x)) < 1200 for x in members[0].location)
result = {"linked_asset": str(asset), "collection": linked.name,
          "collection_object_count": len(members), "object": members[0].name,
          "object_location": list(members[0].location), "result": "PASS"}
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
