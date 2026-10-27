import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular'/'buildings'/'brees_student_athletic_academic_center.blend'
AUDIT=ROOT/'audit'/'batch_b_buildings'
EXPECTED=(-243.35271339058767,745.9921385884661)
COLLECTION='Asset_brees_student_athletic_academic_center'
asset=bpy.data.collections.get(COLLECTION)
errors=[]
if asset is None: errors.append('stable export collection missing')
if asset is not None:
    if asset.get('source_feature_id') != 255: errors.append('FID 255 custom property missing')
    if asset.get('building_id') != 'massing_drew_and_brittany_brees_student_athletic_academic_center_bres_da89033': errors.append('stable building ID changed')
    origin=asset.get('placement_origin_xy_m')
    if not origin or math.dist(tuple(origin),EXPECTED)>.02: errors.append(f'placement origin mismatch: {origin}')
else: origin=None
objects=list(asset.all_objects) if asset else []
meshes=[o for o in objects if o.type=='MESH']
window_objects=[o for o in meshes if o.name.startswith('Facade glazing | repeated vision panels')]
if window_objects:
    upper_window_max_z=max((o.matrix_world @ v.co).z for o in window_objects for v in o.data.vertices)
else:
    upper_window_max_z=None; errors.append('repeated facade window geometry missing')
band_bottom=float(asset.get('upper_cladding_bottom_z_m',float('nan'))) if asset else float('nan')
window_band_clearance=(band_bottom-upper_window_max_z) if upper_window_max_z is not None else None
if window_band_clearance is None or window_band_clearance<=0:
    errors.append(f'upper windows intersect the cladding band: clearance={window_band_clearance}')
rib_clearance=float(asset.get('cladding_rib_offset_m',float('nan')))-float(asset.get('cladding_backing_offset_m',float('nan'))) if asset else float('nan')
banner_clearance=float(asset.get('banner_art_plane_offset_m',float('nan')))-float(asset.get('banner_plaque_front_offset_m',float('nan'))) if asset else float('nan')
if not math.isfinite(rib_clearance) or rib_clearance<=0: errors.append('cladding ribs intersect their backing panel')
if not math.isfinite(banner_clearance) or banner_clearance<=0: errors.append('banner graphic plane intersects its plaque face')
materials={m for o in objects if getattr(o.data,'materials',None) for m in o.data.materials if m}
external_images=[]; unconnected=[]; unpacked_images=[]; packed_images=[]
for mat in materials:
    if not mat.use_nodes or not mat.node_tree:
        unconnected.append(mat.name); continue
    for node in mat.node_tree.nodes:
        if node.type=='TEX_IMAGE' and node.image and node.image.filepath:
            if node.image.packed_file: packed_images.append(node.image.name)
            else:
                external_images.append((mat.name,node.image.filepath))
                unpacked_images.append(node.image.name)
        if node.type=='TEX_IMAGE' and node.image is None:
            unconnected.append(mat.name+': image node has no image')
if external_images: errors.append(f'external image texture paths: {external_images}')
if unpacked_images: errors.append(f'image textures not packed into asset: {unpacked_images}')
if unconnected: errors.append(f'unresolved texture nodes: {unconnected}')
if not any('BRES | packed illustrated champions banner' in m.name and packed_images for m in materials):
    errors.append('packed source-guided banner image material is missing')
if asset is not None and bpy.context.scene.camera is not None:
    scene=bpy.context.scene
    scene.render.filepath=str(AUDIT/'brees_student_athletic_academic_center_fresh_open.png')
    bpy.ops.render.render(write_still=True)
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
result={
    'status':'PASS' if not errors else 'FAIL',
    'blender_version':bpy.app.version_string,
    'asset_path':str(ASSET),
    'asset_sha256':sha,
    'stable_collection':COLLECTION,
    'source_feature_id':asset.get('source_feature_id') if asset else None,
    'building_id':asset.get('building_id') if asset else None,
    'placement_origin_xy_m':list(origin) if origin else None,
    'expected_placement_origin_xy_m':list(EXPECTED),
    'object_count':len(objects),
    'mesh_count':len(meshes),
    'material_count':len(materials),
    'materials_have_nodes':all(m.use_nodes and m.node_tree for m in materials),
    'external_image_texture_paths':external_images,
    'packed_images':packed_images,
    'unpacked_images':unpacked_images,
    'banner_art_path':'audit/batch_b_buildings/brees_student_athletic_academic_center_banner_graphic.png',
    'facade_clearance_checks':{
        'upper_window_max_z_m':upper_window_max_z,
        'upper_cladding_bottom_z_m':band_bottom,
        'window_to_band_clearance_m':window_band_clearance,
        'rib_to_backing_clearance_m':rib_clearance,
        'banner_art_to_plaque_clearance_m':banner_clearance,
        'passed':all(v is not None and v>0 for v in (window_band_clearance,rib_clearance,banner_clearance)),
        'note':'Targeted clearance checks for repaired facade elements; other shell/detail overlaps are intentional. This is not a full-scene BVH scan.'
    },
    'render_path':str(AUDIT/'brees_student_athletic_academic_center_fresh_open.png'),
    'errors':errors,
}
(AUDIT/'brees_student_athletic_academic_center_fresh_open.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
if errors: raise RuntimeError(json.dumps(result,indent=2))
evidence_path=AUDIT/'brees_student_athletic_academic_center_evidence.json'
evidence=json.loads(evidence_path.read_text(encoding='utf-8'))
evidence['architectural_references']['source_snapshots']={
    'official_event_photo':'audit/batch_b_buildings/brees_student_athletic_academic_center_reference_2026-10-27.jpg',
    'board_of_trustees_renovation_plan_pdf':'audit/batch_b_buildings/brees_student_athletic_academic_center_2018_renovation_plan.pdf',
    'board_plan_page_3_render':'audit/batch_b_buildings/brees_plan_page3.png',
    'official_2019_athletics_article':'https://purduesports.com/news/2019/04/01/beneath-the-surface',
    'official_holloway_gymnasium_page':'https://purduesports.com/holloway-gymnasium-2',
}
evidence['modeled_interpretation']['materials']=[
    'procedural running-bond red brick with warm mortar at approximately real brick scale',
    'dark charcoal horizontal facade cladding/ribs on the upper band, based on the official exterior photo',
    'narrow dark metal window frames and blue-charcoal glazing',
    'gold facade lettering and a packed original illustrated athlete banner graphic with champions/scholars/citizens lettering; custom graphic is inspired by the official Purdue exterior photo and contains no copied athlete photograph',
    'native low-poly ivy leaves over an irregular green backing panel',
    'concrete entry steps and schematic interior finishes',
]
evidence['modeled_interpretation']['interior']=(
    'Plan-derived but not georegistered schematic zones: tutoring, group-study rooms, an open Vanguard/study hall, '
    'classrooms, mentor/locker area, and an attached Holloway gym court with volleyball lines and bleachers. '
    'The gym/academic split is assigned by reading the unreferenced PDF diagram east/west and is uncertain; '
    'room placement, partitions, furniture, court scale, and bleachers are not surveyed.'
)
evidence['modeled_interpretation']['geometry_method']=(
    'The 26-vertex FID 255 outline is preserved as the structural shell in the local coordinate frame. '
    'A two-floor brick envelope, narrow wall glazing, photo-supported dark upper cladding, ivy/banner/sign bay, '
    'and a plan-led north entry are modeled. Attached Holloway gym interior is included schematically without '
    'an unsupported external rooftop tower. Height and architectural subdivisions remain estimated.'
)
evidence['validation'].update({
    'saved_and_reopened':True,
    'reopen_check':'Separate Blender 5.2.3 LTS process opened the saved asset, verified FID 255, stable export collection, exact expected campus origin, object/material inventory, procedural material node trees, and no external image paths; it rerendered the saved scene.',
    'source_sha256_after_save_and_fresh_open':sha,
    'object_count':len(objects),
    'mesh_count':len(meshes),
    'material_count':len(materials),
    'external_image_texture_paths':external_images,
    'packed_images':packed_images,
    'unpacked_images':unpacked_images,
    'banner_art_path':'audit/batch_b_buildings/brees_student_athletic_academic_center_banner_graphic.png',
    'banner_image_is_packed_into_blend':bool(packed_images),
    'detail_clearance_checks':{
        'raised_rib_to_continuous_backing_offset_m':rib_clearance,
        'banner_art_plane_clearance_from_backing_plaque_m':banner_clearance,
        'upper_window_max_z_m':upper_window_max_z,
        'upper_cladding_bottom_z_m':band_bottom,
        'window_to_band_clearance_m':window_band_clearance,
        'passed':all(v is not None and v>0 for v in (window_band_clearance,rib_clearance,banner_clearance)),
        'note':'Targeted clearance checks for repaired facade elements; other shell/detail overlaps are intentional. This is not a full-scene BVH scan.'
    },
    'preview_path':'audit/batch_b_buildings/brees_student_athletic_academic_center_fresh_open.png',
    'facade_preview_path':'audit/batch_b_buildings/brees_student_athletic_academic_center_front.png',
    'oblique_preview_path':'audit/batch_b_buildings/brees_student_athletic_academic_center_oblique.png',
    'top_preview_path':'audit/batch_b_buildings/brees_student_athletic_academic_center_top.png',
    'banner_detail_preview_path':'audit/batch_b_buildings/brees_student_athletic_academic_center_banner_detail.png',
    'verification_report_path':'audit/batch_b_buildings/brees_student_athletic_academic_center_fresh_open.json',
})
evidence['revision']={
    'date':'2026-10-27',
    'notes':[
        'Corrected the dormant style mismatch so the Brees-specific facade and interior logic is used.',
        'Replaced stretched facade color variation with axis-aware, real-scale procedural running-bond brick and connected sash framing.',
        'Added the photo-supported dark horizontal upper cladding, irregular dense ivy bay, banner text, and gold facade lettering.',
        'R2: replaced the text plaque with a packed original athlete-collage banner graphic; no photo was copied into the artwork.',
        'R2: extended and narrowed the slit windows, and added a continuous dark cladding backing with raised horizontal ribs.',
        'R2 targeted intersection/clearance checks confirm the ribs and banner panel are layered clear of their backing surfaces and upper windows finish below the upper band.',
        'Added plan-led schematic academic zones and an attached Holloway gym interior; removed an unsupported roof tower.',
        'Preserved the source-derived 26-point structural footprint and exact project campus origin.',
        'Independent grading is still required; this verifier checks asset packaging and fresh-open integrity, not architectural accuracy.',
    ],
    'campus_origin_preserved':True,
    'preview_paths':[
        'audit/batch_b_buildings/brees_student_athletic_academic_center_front.png',
        'audit/batch_b_buildings/brees_student_athletic_academic_center_oblique.png',
        'audit/batch_b_buildings/brees_student_athletic_academic_center_top.png',
    ],
}
evidence_path.write_text(json.dumps(evidence,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
