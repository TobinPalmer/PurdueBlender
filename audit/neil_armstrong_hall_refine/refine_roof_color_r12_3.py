import bpy,hashlib,json
from pathlib import Path
ROOT=Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET=ROOT/"modular/buildings/neil_armstrong_hall.blend"
AUDIT=ROOT/"audit/neil_armstrong_hall_refine"
EXPECTED="a56b0b5c58d6c7de1bdbe2cc77845887a188ff92c41a0bb115c015100a625d6a"
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
if sha(ASSET)!=EXPECTED:raise RuntimeError("Asset changed; refusing material update")
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
m=bpy.data.materials["ARMS_R12_Wing_Red_ACM"]
b=next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
previous={"base_color":list(b.inputs["Base Color"].default_value),"metallic":float(b.inputs["Metallic"].default_value),"roughness":float(b.inputs["Roughness"].default_value)}
b.inputs["Base Color"].default_value=(0.24,0.11,0.075,1)
b.inputs["Metallic"].default_value=0.08
b.inputs["Roughness"].default_value=0.58
m.diffuse_color=(0.24,0.11,0.075,1)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
new=sha(ASSET)
ev=json.loads((AUDIT/"evidence_r12_1.json").read_text(encoding="utf-8"))
ev["sha256_before_color_revision"]=EXPECTED;ev["sha256"]=new
ev["new_material"].update({"base_color_linear":[0.24,0.11,0.075,1],"metallic":0.08,"roughness":0.58,"previous_test_values":previous,"color_revision":"R12.3, less blue-sky reflection after top-view pixel comparison. The linear terracotta base and low metallic keep the roof visibly red-brown under blue sky; measured photo color still varies with sunlight/shadow."})
ev["validation_pending"]="Reopen, inspect source-matched views, verify inventory/material/image dependencies, and record exact SHA."
(AUDIT/"evidence_r12_1.json").write_text(json.dumps(ev,indent=2),encoding="utf-8")
print(json.dumps({"sha256":new,"material":ev["new_material"]},indent=2))
