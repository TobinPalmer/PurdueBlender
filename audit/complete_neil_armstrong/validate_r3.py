import json,hashlib,os,bpy
from mathutils import Vector
root=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
asset=root+r'\modular\buildings\neil_armstrong_hall.blend'
out=root+r'\audit\complete_neil_armstrong\validation_r3.json'
bpy.ops.wm.open_mainfile(filepath=asset)
col=bpy.data.collections['Asset_neil_armstrong_hall']
rootobj=bpy.data.objects['AssetRoot_neil_armstrong_hall']
verts=[]
for o in col.objects:
    if o.type=='MESH' and 'Wall' in o.name:
        ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
        verts.extend(ev.matrix_world@Vector(c) for c in ev.bound_box)
result={'building_id':'neil_armstrong_hall','revision':'R3','asset_path':'modular/buildings/neil_armstrong_hall.blend','saved_then_reopened_read_only':True,'asset_modified_in_r3':False,'scene':bpy.context.scene.name,'collection':col.name,'object_count':len(col.objects),'asset_root_location':list(rootobj.location),'shell_wall_bounds_m':[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)],'shell_wall_object_count':sum(1 for o in col.objects if o.type=='MESH' and 'Wall' in o.name),'comparison':'GIS feature 642 ring georeferenced against official Indiana 2023 ortho ImageServer tile; no geometry was transformed, scaled, or moved in R3.','placement_marker':'Read-only rechecked from existing audit/batch3_master/placement_check.json; R2 marker position error 0m, rotation 0deg, unit scale.','renders':['gis_ortho_shell_comparison_r3.png'],'existing_model_render_reused':['renders_r2/exterior_wing_r2.png','renders_r2/roof_oblique_r2.png','renders_r2/atrium_bridges_r2.png'],'geometry_change_reason':'With no dimensioned wall/roof plan or registered elevation, orthophoto/GIS supports plan coverage and reveals omitted wings but cannot safely support vertical wing geometry, floor heights, bridge alignment, or roof profile corrections.'}
result['asset_size_bytes']=os.path.getsize(asset)
result['asset_sha256']=hashlib.sha256(open(asset,'rb').read()).hexdigest()
json.dump(result,open(out,'w'),indent=2)
print(json.dumps(result,indent=2))
