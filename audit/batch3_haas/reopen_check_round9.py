import bpy,json
from pathlib import Path
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']
def b(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[round(min(v[i] for v in p),4) for i in range(3)],[round(max(v[i] for v in p),4) for i in range(3)]]
body=bpy.data.objects['HAAS_Corrected_GIS_Wall_Envelope'];archive=bpy.data.collections.get('Reference_Incompatible_Geometry_felix_haas_hall')
steps=[o for o in C.objects if o.name.startswith('HAAS_Photo_Entry_Stair_Tread_')]
out={'reopened':True,'direct_export_objects':len(C.objects),'gis_envelope_bounds_m':b(body),'all_17_entry_treads_present':len(steps)==17,'entry_tread_count':len(steps),'main_roof_scale':list(bpy.data.objects['HAAS_Photo_Main_Hipped_Roof'].scale),'main_roof_rotation':list(bpy.data.objects['HAAS_Photo_Main_Hipped_Roof'].rotation_euler),'entry_roof_scale':list(bpy.data.objects['HAAS_Photo_Entrance_Hipped_Roof'].scale),'entry_roof_rotation':list(bpy.data.objects['HAAS_Photo_Entrance_Hipped_Roof'].rotation_euler),'estimated_side_overlays_remaining':sum(1 for o in C.objects if o.name.startswith('HAAS_Estimated_Side_')),'archived_formula_labels_hidden':bool(archive and archive.hide_render and all(bpy.data.objects[n].hide_render for n in ['HAAS_Algorithm_1','HAAS_Algorithm_2','HAAS_Algorithm_3'])),'east_main_inlay_faces':len(bpy.data.objects['HAAS_R7_EastFacade_Inlaid_Brickwork'].data.polygons),'east_wing_inlay_faces':len(bpy.data.objects['HAAS_R8_EastWing_Brick_Inlays_EST'].data.polygons),'roof_bump_strength':next(n.inputs['Strength'].default_value for n in bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated'].node_tree.nodes if n.type=='BUMP')}
Path('audit/batch3_haas/reopen_check_round9.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
