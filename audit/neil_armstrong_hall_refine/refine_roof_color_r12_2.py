import bpy,hashlib,json
from pathlib import Path
ROOT=Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET=ROOT/"modular/buildings/neil_armstrong_hall.blend"
AUDIT=ROOT/"audit/neil_armstrong_hall_refine"
EXPECTED="0307f5d877e45d4cd3f88bdff1a2fcaf72da3cfe337e071ee92aba825ec334ec"
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
if sha(ASSET)!=EXPECTED:raise RuntimeError("Asset changed; refusing color update")
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
mat=bpy.data.materials["ARMS_R12_Wing_Red_ACM"]
bsdf=next(n for n in mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
before={"color":list(bsdf.inputs["Base Color"].default_value),"metallic":float(bsdf.inputs["Metallic"].default_value),"roughness":float(bsdf.inputs["Roughness"].default_value)}
bsdf.inputs["Base Color"].default_value=(0.12,0.045,0.03,1.0)
bsdf.inputs["Metallic"].default_value=0.22
bsdf.inputs["Roughness"].default_value=0.44
mat.diffuse_color=(0.12,0.045,0.03,1.0)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
after=sha(ASSET)
ev=json.loads((AUDIT/"evidence_r12_1.json").read_text(encoding="utf-8"))
ev["sha256_before_color_revision"]=EXPECTED
ev["sha256"]=after
ev["new_material"].update({"base_color_linear":[0.12,0.045,0.03,1],"metallic":0.22,"roughness":0.44,"previous_test_values":before,"color_revision":"R12.2, darkened/desaturated after side-by-side source comparison; matches dark red-brown metal more closely than the over-lit rosy R12.1 render."})
ev["validation_pending"]="Reopen, inspect color in source-matched views, run inventory/material/image validation."
(AUDIT/"evidence_r12_1.json").write_text(json.dumps(ev,indent=2),encoding="utf-8")
print(json.dumps({"sha256":after,"material":ev["new_material"]},indent=2))
