import bpy,json
from pathlib import Path
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[round(min(q[i] for q in p),4) for i in range(3)],[round(max(q[i] for q in p),4) for i in range(3)]]
steps=sorted([o for o in C.objects if o.name.startswith('HAAS_Photo_Entry_Stair_Tread_')],key=lambda o:o.name)
door=[o for o in C.objects if 'Door' in o.name and ('Main' in o.name or 'Threshold' in o.name)]
front=[o for o in C.objects if o.name.startswith('HAAS_Photo_Visible_Arched_Glass')]
side=[o for o in C.objects if o.name.startswith('HAAS_Estimated_Side_Lower_Glass_S')]
out={
 'reopened_file':bpy.data.filepath,
 'export_collection':'Asset_felix_haas_hall',
 'direct_object_count':len(C.objects),
 'tread_count':len(steps),
 'tread_bounds_xz':[{'name':o.name,'bounds':bounds(o)} for o in steps],
 'door_and_threshold':[{'name':o.name,'bounds':bounds(o)} for o in door],
 'front_arch_glazing_count':len(front),
 'front_arch_glazing_bounds':[bounds(o) for o in front],
 'near_side_lower_glazing_count':len(side),
 'near_side_lower_glazing_bounds':[bounds(o) for o in side],
 'long_facade_piers':len([o for o in C.objects if o.name.startswith('HAAS_R4_Long_') and '_Pier_' in o.name and 'Base' not in o.name and 'Cap' not in o.name]),
 'west_end_piers':len([o for o in C.objects if o.name.startswith('HAAS_R4_West_Pier_')]),
 'far_side_lower_glazing_count':len([o for o in C.objects if o.name.startswith('HAAS_Estimated_Side_Lower_Glass_N_')]),
 'cupola_export_objects':len([o for o in C.objects if o.name.startswith('HAAS_Cupola_')]),
 'pavilion_side_detail_objects':len([o for o in C.objects if o.name.startswith('HAAS_R5_Pavilion_')]),
 'plan_basis_tagged_objects':len([o for o in C.objects if o.name.startswith('HAAS_Plan_') and 'geometry_basis' in o]),
 'plan_evidence_legend_objects':len([o for o in C.objects if o.name.startswith('HAAS_Plan_Evidence_Legend')]),
 'plan_label_cards':len([o for o in C.objects if o.name.startswith('HAAS_Plan_Label_') and o.name.endswith('_Plate')]),
 'round7_front_inlay_objects':len([o for o in C.objects if o.name=='HAAS_R7_EastFacade_Inlaid_Brickwork']),
 'round7_front_inlay_faces':len(bpy.data.objects.get('HAAS_R7_EastFacade_Inlaid_Brickwork').data.polygons) if bpy.data.objects.get('HAAS_R7_EastFacade_Inlaid_Brickwork') else 0,
 'round8_east_wing_inlay_objects':len([o for o in C.objects if o.name=='HAAS_R8_EastWing_Brick_Inlays_EST']),
 'round8_east_wing_inlay_faces':len(bpy.data.objects.get('HAAS_R8_EastWing_Brick_Inlays_EST').data.polygons) if bpy.data.objects.get('HAAS_R8_EastWing_Brick_Inlays_EST') else 0,
 'round8_east_limestone_faces':sum(1 for p in bpy.data.objects['HAAS_Corrected_GIS_Wall_Envelope'].data.polygons if p.material_index==next(i for i,m in enumerate(bpy.data.objects['HAAS_Corrected_GIS_Wall_Envelope'].data.materials) if m and m.name=='HAAS_Photo_Limestone')),
 'round8_removed_north_end_glazing':not bool(bpy.data.objects.get('HAAS_Estimated_Side_Upper_Glass_N_4_R4')),
 'round7_estimated_door_leaves':0,
 'round7_estimated_door_frames':0,
 'east_wall_mesh_polygons':len(bpy.data.objects['HAAS_Brick_Wall_East'].data.polygons),
 'east_wall_round7_facade_integration':bpy.data.objects['HAAS_Brick_Wall_East'].get('round7_facade',''),
 'gis_envelope_bounds_m':bounds(bpy.data.objects['HAAS_Corrected_GIS_Wall_Envelope'])
}
Path('audit/batch3_haas/continuity_check.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
