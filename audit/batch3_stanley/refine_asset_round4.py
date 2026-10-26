import bpy, hashlib, json
from pathlib import Path
p=Path(r'modular/buildings/stanley_coulter_hall.blend').resolve()
bpy.ops.wm.open_mainfile(filepath=str(p))
root=bpy.data.objects['AssetRoot_stanley_coulter_hall']
roof_collection=bpy.data.collections['SC_Roof_and_Dormers']
cornice=bpy.data.objects['SC_Classical_Entablature_Cornice']
def z_bounds(obj):
 pts=[obj.matrix_world@v.co for v in obj.data.vertices]
 return min(v.z for v in pts), max(v.z for v in pts)
c0,c1=z_bounds(cornice)
factor=0.50
inv=cornice.matrix_world.inverted()
for v in cornice.data.vertices:
 w=cornice.matrix_world@v.co
 w.z=c0+(w.z-c0)*factor
 v.co=inv@w
cornice.data.update()
# Bring the shallow hipped eave down to the narrower photo-supported cornice.
# Full height/roof form are still estimates; this only removes the oversized pale fascia band.
shift=-0.45
for obj in roof_collection.objects:
 if obj.type=='MESH':
  for v in obj.data.vertices:
   v.co.z += shift
  obj.data.update()
 obj['R4_roof_profile_note']='Shallow roof retained; eave shifted to meet reduced cornice based on undated PPBUC01117 and current CLA photo. Exact roof dimensions remain unverified.'
cornice['R4_note']='Vertical thickness reduced by half from its lower edge to match the restrained cornice visible in the Purdue archival photograph; dimensions estimated, not measured.'
if list(root.location)!=[0.,0.,0.] or any(abs(v-1)>1e-6 for v in root.scale):
 raise RuntimeError('root transform changed')
bpy.ops.wm.save_as_mainfile(filepath=str(p))
print(json.dumps({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'roof_collection_shift_m':shift,'cornice_z_before':[c0,c1],'cornice_factor':factor,'cornice_z_after':list(z_bounds(cornice)),'roof_bounds_after':list(z_bounds(bpy.data.objects['SC_Historic_Slate_Roof'])),'root':{'location':list(root.location),'rotation':list(root.rotation_euler),'scale':list(root.scale)}},indent=2))
