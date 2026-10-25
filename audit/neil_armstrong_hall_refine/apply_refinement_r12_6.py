import bpy,hashlib,json
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/neil_armstrong_hall.blend'
EXPECTED='a90bb8c334da300d2c629db0ae18bc200edeb8b525552072dd4029cbd3d8a3ea'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(ASSET)!=EXPECTED:raise RuntimeError('Neil asset changed; refusing R12.6 edit: '+sha(ASSET))
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
# Attributed photos show brick-dominant lower stories on the exterior wings,
# with a continuous glazed upper band. Retain the top-level strips, and hide
# the unsourced lower-level ribbons on the two long facades. Objects stay in
# the asset inventory for review and reversible re-enabling.
hidden=[]
for o in bpy.data.objects:
 if o.type=='MESH' and '_Win_' in o.name and any(o.name.endswith('_'+z) for z in ('2','7','12')):
  o.hide_render=True
  o.hide_set(True)
  o['R12_6_visibility_note']='Lower-story ribbon window not supported by the attributed exterior photos; hidden, not deleted, for reversible review. Upper-story band retained.'
  hidden.append(o.name)
if len(hidden)!=12:raise RuntimeError(f'Expected 12 lower-story ribbons, found {len(hidden)}')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps({'sha256':sha(ASSET),'hidden_window_ribbons':hidden,'objects':len(bpy.data.objects)},indent=2))
