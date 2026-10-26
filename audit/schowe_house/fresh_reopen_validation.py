"""Fresh-process structural and portability validation for the Schowe House asset."""
from pathlib import Path
import bpy,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/massing_purdue_center_for_regional_development_scho_a2375c9.blend'
AUDIT=ROOT/'audit/schowe_house'
COLL='Asset_massing_purdue_center_for_regional_development_scho_a2375c9'
SCENE='Building_massing_purdue_center_for_regional_development_scho_a2375c9'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
errors=[]
scene=bpy.data.scenes.get(SCENE)
coll=bpy.data.collections.get(COLL)
if not scene:errors.append('required building scene missing')
if not coll:errors.append('required export collection missing')
if scene and coll and coll.name not in [c.name for c in scene.collection.children]:errors.append('export collection is not a direct scene child')
if coll:
    objs=list(coll.objects); meshes=[o for o in objs if o.type=='MESH']
    if len(meshes)<20:errors.append(f'expected detailed asset geometry, found only {len(meshes)} meshes')
    if not any('Cross_Gable_Slate_Planes' in o.name for o in meshes):errors.append('cross-gable slate roof planes missing')
    if not any('Perimeter_Brickwork' in o.name for o in meshes):errors.append('GIS-aligned perimeter masonry missing')
    deps=bpy.context.evaluated_depsgraph_get();pts=[]
    for o in meshes:
        ev=o.evaluated_get(deps);me=ev.to_mesh();pts.extend([ev.matrix_world@v.co for v in me.vertices]);ev.to_mesh_clear()
    bounds={'x':[min(v.x for v in pts),max(v.x for v in pts)],'y':[min(v.y for v in pts),max(v.y for v in pts)],'z':[min(v.z for v in pts),max(v.z for v in pts)]} if pts else None
    matnames=sorted({m.name for o in meshes for m in o.data.materials if m})
else: objs=[];meshes=[];bounds=None;matnames=[]
images=[]
for im in bpy.data.images:
    images.append({'name':im.name,'packed':bool(im.packed_file),'filepath':im.filepath})
    if im.name.startswith('SCHO_') and not im.packed_file:errors.append('generated model texture is not packed: '+im.name)
summary={'pass':not errors,'errors':errors,'asset_path':str(ASSET.relative_to(ROOT)).replace('\\','/'),'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,'scene':scene.name if scene else None,'collection':coll.name if coll else None,'object_count':len(objs),'mesh_object_count':len(meshes),'evaluated_bounds_m':bounds,'material_names':matnames,'images':images,'linked_library_paths':[l.filepath for l in bpy.data.libraries if l.filepath]}
(AUDIT/'fresh_reopen_validation.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
if errors:sys.exit(1)
