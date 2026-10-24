import bpy, hashlib, json
from pathlib import Path

ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/knoy_hall.blend'
OUT=ROOT/'audit/complete_knoy/independent_reopen_review_r17.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.context.scene
asset=bpy.data.collections.get('Asset_knoy_hall')
root=bpy.data.objects.get('AssetRoot_knoy_hall')
assert scene and scene.name=='Building_knoy_hall'
assert asset and root
desc=[]
stack=list(asset.objects)
while stack:
    obj=stack.pop()
    if obj not in desc:
        desc.append(obj)
        if obj.instance_type=='COLLECTION' and obj.instance_collection:
            stack.extend(list(obj.instance_collection.objects))
        stack.extend([c for c in obj.children if c not in desc])
meshes=[o for o in bpy.data.objects if o.type=='MESH']
missing_materials=[o.name for o in meshes if not o.data.materials]
unpacked=[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]
mesh=bpy.data.objects.get('KNOY_Facade_Brick_Spandrels_R17')
glass=bpy.data.objects.get('KNOY_Fenestration_Ribbon_Glass')
assert mesh and glass
bb=[(glass.matrix_world@v.co) for v in glass.data.vertices]
zbands=sorted(set(round(v.z,2) for v in bb))
result={
 'asset_reopened':True,'blender_version':bpy.app.version_string,
 'scene':scene.name,'asset_collection_present':bool(asset),'asset_root_present':bool(root),
 'direct_asset_objects':len(asset.objects),'descendants':len(desc),'scene_meshes':len(meshes),
 'unpacked_external_images':unpacked,'meshes_without_materials':missing_materials,
 'r17_spandrel_present':bool(mesh),'r17_spandrel_vertices':len(mesh.data.vertices),'r17_spandrel_faces':len(mesh.data.polygons),
 'ribbon_glass_vertices':len(glass.data.vertices),'ribbon_world_z_levels_m':zbands,
 'known_nested_asset_objects':{name:sum(1 for o in bpy.data.objects if o.name.startswith(name)) for name in ('KNOY_TypicalPlan_Doors_L2-L4','KNOY_TypicalPlan_WashroomFixtures_L2-L4','KNOY_TypicalPlan_StairRuns_L2-L4')},
 'result':'PASS' if not unpacked and not missing_materials and len(mesh.data.polygons)>0 else 'CHECK'
}
OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
