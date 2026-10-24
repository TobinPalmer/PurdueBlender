import bpy, os
ASSET=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=ASSET)
slab=bpy.data.objects.get('KNOY_FloorSlab_L5')
assert slab is not None
slab['story_status']='UNVERIFIED / SOURCE CONFLICT — roof-slab interpretation plausible, not confirmed'
slab['story_evidence']='2018 Purdue Gateway page 24 labels existing Levels 1-4 at 14 ft 8 in intervals. 2018 Indiana 3DEP DSM comparison estimates representative roof surface about 59.9 ft above sampled bare earth, near this retained slab datum (58.8 ft), making a roof-level slab plausible. The DSM cannot establish occupancy, designation, exact level or vertical registration.'
slab['interpretation']='Retained as inherited, source-conflicted geometry. Do not count as a confirmed occupied story or relabel/delete without an as-built section. The 2018 LiDAR surface check is approximate and only supports a plausible roof-slab interpretation.'
scene=bpy.context.scene
scene['unverified_l5_status']='L5 remains source-conflicted. 2018 3DEP DSM roof-like median is about 59.9 ft above sampled bare earth, near the 58.8 ft slab datum; this makes roof-slab interpretation plausible but does not verify story use.'
scene['knoy_roof_height_assessment']='audit/complete_knoy/roof_height_assessment_r8.json'
scene['knoy_lidar_surface_height_estimate_ft_agl']=59.9
scene['knoy_lidar_surface_height_method']='Median 680.94 ft DSM within approximate KNOY GIS polygon minus median 621.06 ft bare-earth DEM from 21 interior point queries; 2018 surface product; not surveyed building height.'
notes=bpy.data.texts.get('EVIDENCE_AND_INTERIOR_NOTES.txt')
assert notes is not None
text=notes.as_string()
marker='ROUND 8 — INDIANA 3DEP ROOF-SURFACE CHECK'
if marker not in text:
 text += '''\n\nROUND 8 — INDIANA 3DEP ROOF-SURFACE CHECK\n------------------------------------------------------------\nThe Indiana GIO 2018 Tippecanoe 3DEP surface tile in2018_30001885_12 (5 ft cells; acquisition date 2018-04-20) has 1,126 valid cell centers inside the approximate project GIS footprint. The DSM median is 680.94 ft. Twenty-one point queries to the Indiana 2016-2020 bare-earth DEM service inside the footprint have median 621.06 ft, for an indicative median surface difference of about 59.9 ft. The full-footprint DSM p10-p90 span is about 30.4-63.9 ft AGL because it includes stepped surfaces, lower surfaces, edges/openings and rooftop objects. The project local-to-geographic conversion and 5 ft raster cells are approximate; the bare-earth surface under the building is modeled/interpolated; statewide QL2 accuracy does not constitute a Knoy-specific accuracy assessment. Do not read these values as a surveyed parapet, penthouse, or single roof plane.\n\nThe ~59.9 ft representative surface is near the inherited L5 slab datum (~58.8 ft), making a roof-level slab interpretation plausible. It does not prove whether L5 is an occupied fifth story or a roof slab, and the GIS 48 ft extrusion remains conflicting. The L5 slab, roof, penthouse and facade geometry remain unchanged. See audit/complete_knoy/roof_height_assessment_r8.json and knoy_roof_height_vertical_evidence_r8.svg. The 2023 orthophoto remains presence-only for PV; no modeled PV transform is registered to it. The cyan bounds overlay remains retracted and must not be used.\n'''
 notes.clear();notes.write(text)
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print('Saved Knoy L5 evidence note; no geometry changed; status:',slab['story_status'])
