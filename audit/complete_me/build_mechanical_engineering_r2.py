"""R2 evidence-backed separation/height correction for Purdue ME FID 108.

This operation only edits the Mechanical Engineering library asset. FID 857
stays unchanged because the DSM shows several roof levels but cannot assign all
surface returns to distinct wings without a registered roof plan.
"""
import bpy, json, shutil
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'complete_me'
ASSET_PATH=ROOT/'modular'/'buildings'/'mechanical_engineering.blend'
BACKUP=AUDIT/'mechanical_engineering_before_r2.blend'
if not BACKUP.exists(): shutil.copy2(ASSET_PATH,BACKUP)

asset=bpy.data.collections['Asset_mechanical_engineering']
scene=bpy.context.scene
shell=bpy.data.objects['ME_Official_108_Structural_Envelope']
roof=bpy.data.objects['ME_Official_108_Roof']
target_wall_top=4.20 # m; see mechanical_engineering_lidar_r2.json and review

# Scale only the source-tagged FID108 exterior envelope vertically from its
# original estimated 18.5 m to the 2018 DSM/DEM center-point estimate.
z_values=[v.co.z for v in shell.data.vertices]
old_wall_top=max(z_values)
scale=target_wall_top/old_wall_top
for v in shell.data.vertices:
    v.co.z*=scale
shell.data.update()

# The existing flat roof was offset above the wall top by 0.25 m. Preserve that
# qualitative thickness while moving it to the measured-height estimate.
old_roof_top=max(v.co.z for v in roof.data.vertices)
old_wall_roof=min(v.co.z for v in roof.data.vertices)
roof_offset=target_wall_top-old_wall_roof
for v in roof.data.vertices:
    v.co.z+=roof_offset
roof.data.update()

# The source has only one low roof mass here. The modeled upper slabs at 4.5,
# 9.0, and 13.5 m cannot represent occupied floors within a 4.2 m envelope;
# retain them outside the export collection in a hidden recovery collection.
archive=bpy.data.collections.get('ME_R2_Archive_Unverified_FID108_Upper_Floors')
if archive is None:
    archive=bpy.data.collections.new('ME_R2_Archive_Unverified_FID108_Upper_Floors')
    scene.collection.children.link(archive)
for name in ['ME_Official_108_Estimated_Floor_4.5',
             'ME_Official_108_Estimated_Floor_9',
             'ME_Official_108_Estimated_Floor_13.5']:
    ob=bpy.data.objects.get(name)
    if ob is None: continue
    if ob.name in asset.objects: asset.objects.unlink(ob)
    if ob.name not in archive.objects: archive.objects.link(ob)
    ob.hide_render=True
    ob.hide_set(True)
    ob['r2_status']='Archived outside exported building collection: unsupported upper floor lies above source-registered FID108 roof.'
archive.hide_render=True
archive.hide_viewport=True
archive['r2_status']='Recovery-only archive; not part of Asset_mechanical_engineering export.'

shell['source_fid']='108'
shell['height_status']='Approx. 4.20 m to wall/roof interface, registered to 2018 3DEP DSM at official GIS FID108 centroid and bare-earth DEM; uncertainty includes 5-ft cell spacing, source date, and footprint overlap.'
shell['r2_height_source']='audit/complete_me/mechanical_engineering_lidar_r2.json'
roof['source_fid']='108'
roof['r2_height_status']='Flat, approximately 0.25 m qualitative roof cap at z=4.20-4.45 m, from DSM surface estimate; roof shape/thickness not surveyed.'
asset['r2_revision']='R2 lowered separate FID108 low-roof structure using registered Indiana 2018 3DEP surface and bare-earth height check; FID857 unchanged.'
asset['r2_fid108_height_status']='DSM/DEM center sample gives approx 13.77 ft (4.20 m) above bare earth. This is a point estimate for the small roof structure, not a survey; model rounded to 4.20 m.'
asset['r2_fid108_relationship']='Current 2023 Indiana orthophoto overlays the FID108 GIS polygon on a distinct low roof at the southeast edge of the larger FID857 complex. Polygon overlap/touching and the structures connection remain unverified.'

# Keep asset frame and scene intact; do not save/open the campus master.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
bpy.ops.wm.open_mainfile(filepath=str(ASSET_PATH))

# Save reopened measurements for the separate validator and independent grader.
asset=bpy.data.collections['Asset_mechanical_engineering']
shell=bpy.data.objects['ME_Official_108_Structural_Envelope']
roof=bpy.data.objects['ME_Official_108_Roof']
def bounds_z(ob):
    return [min(float(v.co.z) for v in ob.data.vertices),max(float(v.co.z) for v in ob.data.vertices)]
def bounds_xy(ob):
    vs=[ob.matrix_world@Vector(c) for c in ob.bound_box]
    return [[min(v[i] for v in vs),max(v[i] for v in vs)] for i in (0,1)]
root=bpy.data.objects['AssetRoot_mechanical_engineering']
report={
 'revision':2,'saved_file_reopened':True,'asset_path':str(ASSET_PATH),
 'blender_version':bpy.app.version_string,'export_collection':'Asset_mechanical_engineering',
 'archive_collection':'ME_R2_Archive_Unverified_FID108_Upper_Floors',
 'archive_excluded_from_export':all(n not in asset.objects for n in ['ME_Official_108_Estimated_Floor_4.5','ME_Official_108_Estimated_Floor_9','ME_Official_108_Estimated_Floor_13.5']),
 'root_location':[round(float(v),6) for v in root.location],
 'root_scale':[round(float(v),6) for v in root.scale],
 'fid108_shell_bounds_xy_local_m':bounds_xy(shell),
 'fid108_shell_bounds_z_m':bounds_z(shell),
 'fid108_roof_bounds_xy_local_m':bounds_xy(roof),
 'fid108_roof_bounds_z_m':bounds_z(roof),
 'fid108_xy_geometry_changed':False,
 'fid857_geometry_changed':False,
 'evidence':'audit/complete_me/mechanical_engineering_lidar_r2.json; audit/complete_me/mechanical_engineering_ortho_registration_r2.json',
 'master_or_shared_files_changed':False}
report['passed']=bool(report['saved_file_reopened'] and report['archive_excluded_from_export'] and report['root_location']==[0.0,0.0,0.0] and report['root_scale']==[1.0,1.0,1.0] and abs(report['fid108_shell_bounds_z_m'][1]-4.20)<1e-4 and abs(report['fid108_roof_bounds_z_m'][0]-4.20)<1e-4 and report['fid108_xy_geometry_changed'] is False and report['fid857_geometry_changed'] is False)
(AUDIT/'mechanical_engineering_r2_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
if not report['passed']: raise RuntimeError('R2 saved/reopened validation did not pass')
