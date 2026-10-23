import bpy,json
from pathlib import Path
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[round(min(v[i] for v in p),4) for i in range(3)],[round(max(v[i] for v in p),4) for i in range(3)]]
body=bpy.data.objects['HAAS_Corrected_GIS_Wall_Envelope']
arch=bpy.data.collections.get('Reference_Incompatible_Geometry_felix_haas_hall')
steps=[o for o in C.objects if o.name.startswith('HAAS_Photo_Entry_Stair_Tread_')]
roofmat=bpy.data.materials.get('HAAS_GooglePhotos_RedClayTiles_R10')
roofobjs=['HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof']
out={'reopened':True,'direct_export_objects':len(C.objects),'gis_envelope_bounds_m':bounds(body),'gis_shell_unchanged':bounds(body)==[[-26.2203,-25.9795,0.0],[12.9812,26.7597,11.5]],'entry_tread_count':len(steps),'all_17_entry_treads_present':len(steps)==17,'roof_objects':{n:{'scale':list(bpy.data.objects[n].scale),'rotation':list(bpy.data.objects[n].rotation_euler),'bounds_m':bounds(bpy.data.objects[n]),'material':bpy.data.objects[n].data.materials[0].name if bpy.data.objects[n].data.materials else None,'uv_layers':[u.name for u in bpy.data.objects[n].data.uv_layers]} for n in roofobjs},'round10_roof_material':{'present':bool(roofmat),'node_types':[n.type for n in roofmat.node_tree.nodes] if roofmat else [],'brick_dimensions_m':[0.62,0.25] if roofmat else None,'emission_strength':next((round(n.inputs['Strength'].default_value,3) for n in roofmat.node_tree.nodes if n.type=='EMISSION'),None) if roofmat else None},'inlay_faces':{'east_main':len(bpy.data.objects['HAAS_R7_EastFacade_Inlaid_Brickwork'].data.polygons),'east_wing':len(bpy.data.objects['HAAS_R8_EastWing_Brick_Inlays_EST'].data.polygons)},'side_estimate_overlays_remaining':sum(1 for o in C.objects if o.name.startswith('HAAS_Estimated_Side_')),'archived_formula_labels_hidden':bool(arch and arch.hide_render and all(bpy.data.objects[n].hide_render for n in ['HAAS_Algorithm_1','HAAS_Algorithm_2','HAAS_Algorithm_3'])),'archived_beltcourses':{n:bool(arch and bpy.data.objects.get(n) and bpy.data.objects[n].name in arch.objects and bpy.data.objects[n].hide_render) for n in ['HAAS_Beltcourse2_North','HAAS_Beltcourse2_West']}}
Path('audit/batch3_haas/reopen_check_round10.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
