import bpy, os
p=os.path.abspath(r'modular/buildings/knoy_hall.blend')
bpy.ops.wm.open_mainfile(filepath=p)
sc=bpy.context.scene
root=bpy.data.objects.get('AssetRoot_knoy_hall')
source_url='https://engineering.purdue.edu/~frosch/Renderings/Gateway/2018-05-31%20MASSING%20STUDIES%20DRAFT%20INCLUDING%20LANDSCAPE.pdf'
for owner in (sc,root):
    if owner is not None:
        owner['evidence_primary_plan_url']=source_url
        owner['evidence_primary_plan_date']='2018-05-31; source retrieved 2026-10-24'
        owner['evidence_primary_plan_sheet']='PDF page 24; Typical Plan Levels 2-4; adjacent Existing Knoy Elevations'
        owner['evidence_vertical_levels']='Purdue planning study labels existing Knoy Levels 1-4 at 14 ft 8 in floor-to-floor (4.4704 m). This is planning-study evidence, not as-built survey.'
        owner['evidence_vertical_uncertainty']='Current model has an additional slab named L5 and separate roof deck; this conflicts with the four numbered levels shown on the 2018 source. Do not treat the story count / roof slab interpretation as verified.'
        owner['evidence_plan_registration']='Plan crop manually matched to official Purdue GIS footprint using three perimeter controls; approx. +/-1 m; no printed plan scale or north arrow.'
        owner['evidence_plan_trace_status']='Typical upper-floor plan source is preserved in audit/complete_knoy/knoy_typical_plan_crop.png; current upper-floor partitions are not yet traced from that source.'
        owner['evidence_source_file']='audit/complete_knoy/2018-05-31_knoy_massing_studies.pdf'
# Preserve the current mesh while making the evidence linkage visible to reviewers.
for name in ('KNOY_FloorSlab_L1_Ground','KNOY_FloorSlab_L2','KNOY_FloorSlab_L3','KNOY_FloorSlab_L4','KNOY_FloorSlab_L5','KNOY_FloorSlab_RoofDeck'):
    o=bpy.data.objects.get(name)
    if o:
        o['source_height_reference']='Purdue College of Engineering Gateway Formation Study, PDF page 24, 2018-05-31; existing Knoy Levels 1-4 at 14 ft 8 in floor-to-floor.'
        o['height_status']='approximate model elevation; compare to the stated 4.4704 m interval and see scene custom properties for L5 ambiguity'
# Save only Knoy's dedicated source library.
bpy.ops.wm.save_as_mainfile(filepath=p)
print('saved',p,'root',root.name if root else None,'collection',bpy.data.collections.get('Asset_knoy_hall').name)
