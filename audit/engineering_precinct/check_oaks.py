import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/site/engineering_mall_groundwork_patch.blend')
for oid in [7473,1938,2374,6267,8141]:
 o=next((ob for ob in bpy.data.objects if ob.get('source_objectid')==oid),None)
 if o: print(oid,o.name,'frame',o.get('reference_crown_x'),o.get('reference_crown_y'),'scale',o.get('visual_crown_scale_xy'), 'dist',o.get('preview_view_distance_m'),'spread',o.get('canopy_diameter_m'))
