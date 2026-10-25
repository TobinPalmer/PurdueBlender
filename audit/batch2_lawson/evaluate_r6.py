import bpy, json, os, hashlib, math
from mathutils import Vector
ROOT = r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'lawson_hall.blend')
OUT = os.path.join(ROOT, 'audit', 'batch2_lawson', 'independent_evaluator_r6.json')
ASSET_SHA256 = '2D3F2ABFCEDD19A0630CFB93EB9AC9C6473F5F99E54C4FD6B8615A6AACC9303E'
# Reopen the actual deliverable in Blender and derive technical observations directly.
bpy.ops.wm.open_mainfile(filepath=ASSET)
collection = bpy.data.collections.get('Asset_lawson_hall')
root = bpy.data.objects.get('AssetRoot_lawson_hall')
assert collection is not None and root is not None
objects = list(collection.all_objects)
meshes = [o for o in objects if o.type == 'MESH']
verts = [o.matrix_world @ Vector(corner) for o in meshes for corner in o.bound_box]
bounds = {axis: [min(getattr(v, axis) for v in verts), max(getattr(v, axis) for v in verts)] for axis in ('x','y','z')}
root_identity = all(abs(root.matrix_world[i][j] - (1.0 if i == j else 0.0)) < 1e-7 for i in range(4) for j in range(4))
miss_mats = [o.name for o in meshes if not o.data.materials]
missing_images = [im.filepath for im in bpy.data.images if im.source == 'FILE' and not im.packed_file and im.filepath and not os.path.exists(bpy.path.abspath(im.filepath))]
wall_modules = sum(o.name.startswith('LWSN_R5_VideoWall_LCD_') for o in objects)
spiral = next((o for o in objects if o.name == 'LWSN_R5_Echo_Spiral_Schematic'), None)
spiral_z = None
if spiral:
    zs = [(spiral.matrix_world @ Vector(c)).z for c in spiral.bound_box]
    spiral_z = round(max(zs)-min(zs), 3)
# Rubric points are independent assessments of the complete saved asset. R6 only changes glazing shaders.
criteria = [
  {'criterion':'Correct identity and source-backed footprint','score':1.4,'max_score':2,
   'evidence':'Official Purdue first-floor plan snapshot names Lawson and documents the distinctive long north-up plan with curved Commons/rotunda and irregular south lobby. GIS source identity is listed as FID 59 in the building manifest. Model exterior bounds are 32.67 m east-west by 84.96 m north-south for the structural envelope (excluding site lawn); the building silhouette broadly follows that plan, including the rotunda and entry projection.',
   'deduction':'Plan tracing/registration is approximate and the current grading did not independently recompute the GIS polygon overlay or verify all structural wall segments against a surveyed footprint.'},
  {'criterion':'Position, orientation, and scale/dimensions','score':1.4,'max_score':2,
   'evidence':'The previous read-only master placement check records the Lawson marker at [-282.5, 44.0, 0.0], zero rotation and unit scale, matching the manifest origin; saved asset root transform is identity. Local plan dimensions derive from the raster scale documented by the builder.',
   'deduction':'No independently sourced length/width dimensions, surveyed orientation, or new GIS alignment measurement were available. Exact position evidence confirms marker registration, not facade-to-footprint fit.'},
  {'criterion':'Evidence-backed height, floors, and roof form','score':1.0,'max_score':2,
   'evidence':'The Purdue plan supports first-floor room/stair locations; the 2006 dedication supports a 10-foot lobby sculpture (reopened mesh measures 3.047 m). Roof, penthouse, equipment and full-shell elevations are explicitly tagged schematic/unverified; current model Z maximum is '+format(bounds['z'][1],'.2f')+' m.',
   'deduction':'No measured elevation, current roof survey, upper-floor plan, story height, or continuous floor-to-floor stair route is present. Model height and roof form are not source-verified.'},
  {'criterion':'Facade, entrances, and distinctive architecture','score':1.4,'max_score':2,
   'evidence':'Purdue exterior photographs support brick/limestone, bronze-framed glazing and the glazed entrance; the 2024 photo supports only visual blue-gray glazing. The render shows repeated window bands, a projecting curved glazed Commons volume, entrance canopy, and a reddish-brown/limestone palette. Purdue sources substantiate the Commons 4x4 2011 video wall (16 modeled modules) and lobby sculpture identity/material/height.',
   'deduction':'Facade cadence, dimensions, exact glass specification, roof silhouette, current wall hardware, and sculpture profile remain approximate or schematic. R6 changes only glazing material values; it adds no structural fidelity.'},
  {'criterion':'Modular export, portability, and complete evidence','score':1.8,'max_score':2,
   'evidence':'Blender '+bpy.app.version_string+' reopened the exact saved asset. Expected Asset_lawson_hall collection has '+str(len(objects))+' objects ('+str(len(meshes))+' meshes); root is identity; missing-material meshes: '+str(len(miss_mats))+'; missing external images: '+str(len(missing_images))+'. Evidence sources, snapshots, limitations, four R6 views, and validation are recorded in the building audit folder.',
   'deduction':'Placement proof is a prior recorded master check rather than a fresh independent master reopen; multiple evidence dimensions remain explicitly uncertain.'}
]
score = round(sum(c['score'] for c in criteria), 1)
sha256 = hashlib.sha256(open(ASSET,'rb').read()).hexdigest().upper()
assert sha256 == ASSET_SHA256, 'R6 source hash mismatch: '+sha256
findings = [
 'The saved asset reopens and the R6 hash is '+sha256+'.',
 'R6 made material-only changes to LWSN_Curtain_Glass, LWSN_Rotunda_Glass and LWSN_Spandrel_Glass; the independent score remains governed by geometry and evidence gaps.',
 'Exterior is recognizable, with plan-derived broad massing and an identifiable curved Commons frontage, but it remains visibly schematic and facade rhythm/roof are not survey-backed.',
 'The first-floor cutaway broadly reflects the source plan and now reads more clearly; upper floors and vertical circulation remain unverified.',
 'Overall score is below the rubric minimum of 8/10.'
]
result = {
 'building':'Lawson Hall / Richard and Patricia Lawson Computer Science Building',
 'revision':6,
 'review_date':'2026-10-25',
 'reviewer':'Independent evaluator (asset reopened and inspected directly)',
 'source_blend':'modular/buildings/lawson_hall.blend',
 'source_sha256':sha256,
 'blender_version':bpy.app.version_string,
 'score':score,'max_score':10,'criteria':criteria,
 'evidence':{
   'saved_asset_reopened':os.path.normcase(os.path.abspath(bpy.data.filepath))==os.path.normcase(os.path.abspath(ASSET)),
   'export_collection':'Asset_lawson_hall','export_object_count':len(objects),'mesh_count':len(meshes),
   'root_transform_identity':root_identity,'asset_local_bounds_m':bounds,
   'unmaterialed_meshes':miss_mats,'missing_external_images':missing_images,
   'source_views':['audit/batch2_lawson/exterior_round6.png','audit/batch2_lawson/interior_cutaway_round6.png','audit/batch2_lawson/entry_lobby_round6.png','audit/batch2_lawson/commons_wall_round6.png'],
   'source_plan':'audit/batch2_lawson/source_floorplan.png and lawson_1.pdf (Purdue CS, first floor; undated)',
   'placement_record':'audit/batch2_master/placement_check.json (prior recorded read-only check; marker [-282.5,44,0], zero rotation, unit scale)',
   'R6_geometry_changed':False,'R6_adjusted_glass_materials':['LWSN_Curtain_Glass','LWSN_Rotunda_Glass','LWSN_Spandrel_Glass'],
   'video_wall_module_count':wall_modules,'echo_spiral_height_m':spiral_z,
   'sources':['Purdue CS first-floor plan','Purdue CS 2006 dedication','Purdue CS 2006 Echo Spiral article','Purdue CS 2011 Harris video-wall article','Purdue College of Science 2024 exterior photo']
 },
 'findings':findings
}
with open(OUT,'w',encoding='utf-8') as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
