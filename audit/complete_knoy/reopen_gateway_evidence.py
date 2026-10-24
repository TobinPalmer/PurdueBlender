import bpy, json, os
from mathutils import Vector
f=bpy.data.filepath
scene=bpy.context.scene; col=bpy.data.collections.get('Asset_knoy_hall'); root=bpy.data.objects.get('AssetRoot_knoy_hall')
def zrange(name):
 o=bpy.data.objects.get(name)
 if not o:return None
 z=[(o.matrix_world@Vector(c))[2] for c in o.bound_box]
 return [round(min(z),4),round(max(z),4)]
report={'reopen':'PASS','blend_file':f,'asset_collection_present':col is not None,'asset_collection_direct_object_count':len(col.objects) if col else 0,'root_identity':bool(root and all(abs(root.matrix_world[i][j]-(1 if i==j else 0))<1e-6 for i in range(4) for j in range(4))),'primary_plan_source':scene.get('evidence_primary_plan_url'),'primary_plan_sheet':scene.get('evidence_primary_plan_sheet'),'vertical_levels_note':scene.get('evidence_vertical_levels'),'vertical_uncertainty':scene.get('evidence_vertical_uncertainty'),'slab_bounds_z_m':{n:zrange(n) for n in ['KNOY_FloorSlab_Basement','KNOY_FloorSlab_L1_Ground','KNOY_FloorSlab_L2','KNOY_FloorSlab_L3','KNOY_FloorSlab_L4','KNOY_FloorSlab_L5','KNOY_FloorSlab_RoofDeck']}}
out=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_knoy\gateway_evidence_reopen.json'
with open(out,'w',encoding='utf-8') as w:json.dump(report,w,indent=2)
print(json.dumps(report,indent=2))
