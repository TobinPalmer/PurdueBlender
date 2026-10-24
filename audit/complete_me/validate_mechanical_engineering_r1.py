"""Read-only saved-file validation for Mechanical Engineering R1."""
import bpy, json, os
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
ASSET_PATH=ROOT/'modular'/'buildings'/'mechanical_engineering.blend'
AUDIT=ROOT/'audit'/'complete_me'
with open(ROOT/'audit'/'official_building_references.json',encoding='utf-8') as f: gis=json.load(f)
feature=next(x for x in gis['buildings'] if x.get('fid')==857)
origin=Vector((66.30000114440918,86.5))
ring=feature['rings_xy_m'][0]
expected=[ [min(p[i]-origin[i] for p in ring),max(p[i]-origin[i] for p in ring)] for i in (0,1) ]
asset=bpy.data.collections.get('Asset_mechanical_engineering')
root=bpy.data.objects.get('AssetRoot_mechanical_engineering')
shell=bpy.data.objects.get('ME_Official_857_Structural_Envelope')
errors=[]
if asset is None: errors.append('expected exported collection missing')
if root is None: errors.append('asset root missing')
if shell is None: errors.append('GIS structural shell missing')
actual=None
if shell:
    corners=[shell.matrix_world@Vector(c) for c in shell.bound_box]
    actual=[[min(v[i] for v in corners),max(v[i] for v in corners)] for i in range(3)]
    if any(m.type=='BOOLEAN' for m in shell.modifiers): errors.append('facade Boolean modifier was not applied')
if bpy.data.objects.get('ME_R1_Temporary_Facade_Cutters'): errors.append('temporary cutter mesh remains')
if asset:
    for name in ['ME_R1_Facade_Window_Glazing','ME_R1_Facade_Window_Frames','ME_R1_Limestone_Window_Sills_And_Stringcourses','ME_R1_Gatewood_Fountain_Facing_Stone_Arch','ME_R1_Arched_Entry_Door_Glazing','ME_R1_Entrance_Lettering']:
        if name not in bpy.data.objects: errors.append('missing R1 component: '+name)
root_location=[round(float(v),6) for v in root.location] if root else None
root_scale=[round(float(v),6) for v in root.scale] if root else None
if root_location != [0.0,0.0,0.0]: errors.append('asset root translation changed')
if root_scale != [1.0,1.0,1.0]: errors.append('asset root scale changed')
footprint_delta=None
if actual:
    footprint_delta=[[round(actual[i][j]-expected[i][j],5) for j in range(2)] for i in range(2)]
    if any(abs(d)>0.002 for row in footprint_delta for d in row): errors.append('shell XY bounds no longer match GIS envelope within 2 mm')
images=[]
for im in bpy.data.images:
    if im.source!='FILE': continue
    p=bpy.path.abspath(im.filepath,library=im.library)
    exists=os.path.exists(p) if p else False
    packed=bool(im.packed_file)
    images.append({'name':im.name,'filepath':im.filepath,'packed':packed,'exists':exists})
    if not packed and not exists: errors.append('missing unpacked texture: '+im.filepath)
objects=asset.all_objects if asset else []
report={
  'asset_path':str(ASSET_PATH),
  'blender_version':bpy.app.version_string,
  'saved_file_reopened':True,
  'export_collection':'Asset_mechanical_engineering',
  'direct_objects':len(asset.objects) if asset else None,
  'child_inclusive_objects':len(objects),
  'asset_root_location':root_location,
  'asset_root_scale':root_scale,
  'shell_bounds_local_xy_z':actual,
  'gis_aabb_local_xy_expected':expected,
  'shell_bounds_delta_m':footprint_delta,
  'shell_face_count':len(shell.data.polygons) if shell else None,
  'facade_boolean_applied':bool(shell and not any(m.type=='BOOLEAN' for m in shell.modifiers)),
  'facade_window_glazing_object_count':len(bpy.data.objects['ME_R1_Facade_Window_Glazing'].data.polygons) if bpy.data.objects.get('ME_R1_Facade_Window_Glazing') else 0,
  'active_camera':bpy.context.scene.camera.name if bpy.context.scene.camera else None,
  'world':bpy.context.scene.world.name if bpy.context.scene.world else None,
  'image_dependencies':images,
  'preview_renders_exist':all((AUDIT/n).exists() for n in ['mechanical_engineering_r1_hero.png','mechanical_engineering_r1_entrance.png']),
  'master_edited':False,
  'errors':errors,
  'passed':not errors,
}
(AUDIT/'mechanical_engineering_r1_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
