import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
asset_path=root/"modular/buildings/massing_st_thomas_aquinas_5535390.blend"
asset=bpy.data.collections.get("Asset_massing_st_thomas_aquinas_5535390")
removed=[]
for ob in list(asset.objects):
    if ob.name.startswith("SOTAC_Office_Interior_Partition_"):
        removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(asset_path))
path=Path(__file__).resolve().parent/"r3_design_evidence.json"
data=json.loads(path.read_text(encoding="utf-8"))
data["geometry_edits"].append("Removed the superseded room-spanning office partitions and replaced them with door-connected story partitions and a stairwell opening.")
path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"removed":removed,"asset":str(asset_path)}))
