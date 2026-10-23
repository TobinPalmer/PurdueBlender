import bpy,json,math,os
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
root=bpy.data.objects['AssetRoot_stanley_coulter_hall']; asset=bpy.data.collections['Asset_stanley_coulter_hall']
def bounds(n):
 o=bpy.data.objects[n];pts=[o.matrix_world@Vector(c) for c in o.bound_box]
 return [[min(q[i] for q in pts) for i in range(3)],[max(q[i] for q in pts) for i in range(3)]]
out={'reopen_verified':True,'file':p,'scene':bpy.context.scene.name,'asset_objects':len(asset.all_objects),'root_transform':{'location':list(root.location),'rotation_euler':list(root.rotation_euler),'scale':list(root.scale)},'structural_wall_bounds_local_m':bounds('SC_Brick_Masonry_Exterior_Walls'),'asset_fid':56,'manifest_origin_xy_m':[-57.5568952560,-99.1479358673],'comparison_polygon_centroid_xy_m':[-57.5958827888,-96.6482404671],'source_aabb_extrema_error_m':'<0.004 (prior GIS audit; footprint overlay is comparison-only, hidden from renders)','height':'unverified; inferred from visual/source evidence only','google_maps':{'satellite_seen':True,'streetview':'indoor panorama, Kaho Sakaue, capture Jun 2021; no street-facing panorama exposed in checked view','checked':'2026-10-23'}}
with open(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch3_stanley\final_verification.json','w') as f: json.dump(out,f,indent=2)
print(json.dumps(out))
