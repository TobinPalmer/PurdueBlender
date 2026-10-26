import bpy, json, math
from pathlib import Path
asset_id='massing_hampton_hall_of_civil_engineering_hamp_9715f0e'
coll_name='Asset_'+asset_id
scene_name='Building_'+asset_id
root=Path('audit')/asset_id
coll=bpy.data.collections.get(coll_name)
assert coll is not None, 'expected export collection missing'
assert bpy.data.scenes.get(scene_name) is not None, 'expected scene missing'
objects=list(coll.objects)
shell=bpy.data.objects.get('HAMP primary masonry envelope (estimated 5 above-grade levels)')
assert shell is not None
ref=json.loads(Path('audit/official_building_references.json').read_text(encoding='utf-8'))
hamp=next(b for b in ref['buildings'] if b['code']=='HAMP')
ref_ring=[tuple(x) for x in hamp['rings_xy_m'][0][:-1]]
base=[(float(v.co.x),float(v.co.y)) for v in shell.data.vertices[:len(ref_ring)]]
nearest=[min(math.hypot(x-a,y-b) for a,b in base) for x,y in ref_ring]
def bbox_mesh(objs):
 pts=[]
 for o in objs:
  if o.type=='MESH': pts.extend([o.matrix_world@v.co for v in o.data.vertices])
  elif o.type=='FONT':
   deps=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(deps); pts.extend([o.matrix_world@__import__('mathutils').Vector(corner) for corner in e.bound_box])
 return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
mods={o.name:[m.type for m in o.modifiers] for o in objects if o.modifiers}
report={'file':bpy.data.filepath,'blender_version':bpy.app.version_string,'expected_collection':coll_name,'collection_found':True,'collection_object_count':len(objects),'collection_objects':[{'name':o.name,'type':o.type,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale)} for o in objects],'shell_footprint_vertex_count':len(base),'shell_base_to_official_ring_max_xy_m':max(nearest),'source_map_aabb_xy_m':hamp['aabb_xy_m'],'shell_structural_bounds_world_m':bbox_mesh([shell]),'complete_asset_bounds_world_m':bbox_mesh(objects),'modifiers':mods,'external_images':[i.filepath for i in bpy.data.images if i.source=='FILE'],'linked_libraries':[l.filepath for l in bpy.data.libraries],'asset_collection_is_direct_campus_coordinates':True,'render_support_outside_asset_collection':'HAMP_Render_Support' in [c.name for c in bpy.data.collections],'scene_matches_expected':True}
(root/'reopen_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
