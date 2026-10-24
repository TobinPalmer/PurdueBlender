import bpy,json
from pathlib import Path
c=bpy.data.collections['Asset_mackey_arena'];deps=bpy.context.evaluated_depsgraph_get()
def bounds(objs):
    pts=[]
    for o in objs:
        if o.type!='MESH':continue
        ev=o.evaluated_get(deps);m=ev.to_mesh()
        if not m:continue
        pts.extend(o.matrix_world@v.co for v in m.vertices)
        ev.to_mesh_clear()
    return [[round(min(p[i] for p in pts),3),round(max(p[i] for p in pts),3)] for i in range(3)] if pts else None
sd=[o for o in c.objects if o.name.startswith('MACK_SDAC_')]
perim=[o for o in c.objects if o.name.startswith('MACK_PERIM_')]
owned=sd+perim
existing=[o for o in c.objects if o not in owned]
allobjs=list(c.objects)
must_have=['AssetRoot_mackey_arena','MACK_SDAC_Roof_Slab','MACK_SDAC_Ground_Foundation',
           'MACK_PERIM_East_Southeast_Roof','MACK_PERIM_West_Northwest_Roof']
materials=['MACK_SDAC_Brickwork_Procedural','MACK_SDAC_Insulated_Glazing','MACK_Keady_Hardwood_Maple']
brick_mesh=next((o for o in sd if o.type=='MESH' and any(m and m.name=='MACK_SDAC_Brickwork_Procedural' for m in o.data.materials)),None)
brick_uv=bool(brick_mesh and 'MACK_Facade_MetreUV' in brick_mesh.data.uv_layers)
result={
 'reopened_asset':bpy.data.filepath,
 'object_count':len(c.objects),
 'sdac_object_count':len(sd),
 'one_story_perimeter_component_count':len(perim),
 'existing_shell_bounds_local':bounds(existing),
 'new_sdac_and_perimeter_bounds_local':bounds(owned),
 'combined_asset_bounds_local':bounds(allobjs),
 'new_components_parented_to_asset_root':all(o.parent and o.parent.name=='AssetRoot_mackey_arena' for o in owned),
 'expected_objects_present':{n:n in bpy.data.objects for n in must_have},
 'expected_materials_present':{n:n in bpy.data.materials for n in materials},
 'brick_facade_meter_uv_present':brick_uv,
 'brick_facade_polygon_count':len(brick_mesh.data.polygons) if brick_mesh else 0,
 'linked_libraries':len(bpy.data.libraries),
 'room_layout_status':'full-size practice court plus three program-level breakout bays; partitions/circulation remain undocumented and are not claimed as verified',
 'height_uncertainty':'SDAC 14.3m and perimeter 4.6m are estimates, not surveyed heights',
}
result['validation_passed']=(result['new_components_parented_to_asset_root'] and all(result['expected_objects_present'].values()) and all(result['expected_materials_present'].values()) and brick_uv and not result['linked_libraries'])
out=Path(bpy.data.filepath).parents[2]/'audit'/'mackey_arena'/'validation_r3.json'
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
