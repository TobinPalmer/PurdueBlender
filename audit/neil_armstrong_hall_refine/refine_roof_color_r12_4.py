import bpy,hashlib,json
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/neil_armstrong_hall.blend'
AUDIT=ROOT/'audit/neil_armstrong_hall_refine'
EXPECTED='345018f89068bee036c255bd60f28aad670f5d2e8a8f78786681bbe3b5de03b5'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
if sha(ASSET)!=EXPECTED: raise RuntimeError('Neil asset SHA changed; refusing edit')
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
obj=bpy.data.objects['ARMS_Cantilever_Canopy_Deck']
mat=bpy.data.materials['ARMS_R12_Wing_Red_ACM']
bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bsdf.inputs['Base Color'].default_value=(0.085,0.025,0.014,1)
bsdf.inputs['Metallic'].default_value=0.08
bsdf.inputs['Roughness'].default_value=0.50
mat.diffuse_color=(0.085,0.025,0.014,1)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
new=sha(ASSET)
ev=json.loads((AUDIT/'evidence_r12_1.json').read_text(encoding='utf-8'))
ev['sha256_before_color_revision_r12_4']=EXPECTED
ev['sha256']=new
ev['revision']='R12.4 canopy finish and NW pocket'
ev['new_material'].update({'base_color_linear':[0.085,0.025,0.014,1],'metallic':0.08,'roughness':0.50,'color_revision':'R12.4, darkened to match the muted red-brown appearance in the CC BY 4.0 2016 facade images and the 2023 orthophoto; previous R12.3 rendered too pink under the blue review world. Render value remains lighting-dependent, not a calibrated sample.'})
ev['validation_pending']='Reopen, inspect source-matched views, verify inventory/material/image dependencies, and record exact SHA.'
(AUDIT/'evidence_r12_1.json').write_text(json.dumps(ev,indent=2),encoding='utf-8')
print(json.dumps({'sha256':new,'objects':len(bpy.data.objects),'roof_vertices':len(obj.data.vertices),'roof_faces':len(obj.data.polygons),'base_color':list(bsdf.inputs['Base Color'].default_value),'metallic':float(bsdf.inputs['Metallic'].default_value),'roughness':float(bsdf.inputs['Roughness'].default_value)},indent=2))
