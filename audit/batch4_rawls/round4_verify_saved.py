import bpy,json,os
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
g=bpy.data.objects['RAWL_North_Windows_Glass'];f=bpy.data.objects['RAWL_North_Windows_BronzeMullions'];w=bpy.data.objects['RAWL_Masonry_Exterior_Walls'];m=bpy.data.materials['RAWL_CurtainWall_Glass'];bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
report=json.load(open('audit/batch4_rawls/round4_model_changes.json'))
report['saved_material_values']={'base_color_rgba':list(bs.inputs['Base Color'].default_value),'roughness':bs.inputs['Roughness'].default_value,'metallic':bs.inputs['Metallic'].default_value,'transmission':bs.inputs['Transmission Weight'].default_value,'surface_render_method':m.surface_render_method}
report['saved_geometry_counts']={'wall_faces':len(w.data.polygons),'north_glass_quads':len(g.data.polygons),'north_frame_faces':len(f.data.polygons),'north_frames_location_y':f.location.y,'north_glass_location_y':g.location.y}
report['verification_artifacts']=['audit/batch4_rawls/round4_aperture_ray_checks.json','audit/batch4_rawls/checks.json','audit/batch4_rawls/exterior_round4.png','audit/batch4_rawls/north_aperture_after_rebuild.png','audit/batch4_rawls/north_glazing_closeup_round4.png','audit/batch4_rawls/north_glazing_oblique_round4.png']
with open('audit/batch4_rawls/round4_model_changes.json','w') as out:json.dump(report,out,indent=2)
print(json.dumps(report['saved_geometry_counts'],indent=2));print(json.dumps(report['saved_material_values'],indent=2))
