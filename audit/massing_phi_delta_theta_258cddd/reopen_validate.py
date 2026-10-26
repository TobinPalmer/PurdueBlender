from __future__ import annotations
import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector
root = Path(__file__).resolve().parents[2]
asset_path = root / 'modular/buildings/massing_phi_delta_theta_258cddd.blend'
gis_path = root / 'audit/massing_phi_delta_theta_258cddd/sources/purdue_gis_fid_796_current.json'
out_path = root / 'audit/massing_phi_delta_theta_258cddd/reopen_validation.json'
bpy.ops.wm.open_mainfile(filepath=str(asset_path))
scene_name = 'Building_massing_phi_delta_theta_258cddd'
coll_name = 'Asset_massing_phi_delta_theta_258cddd'
scene = bpy.data.scenes.get(scene_name)
coll = bpy.data.collections.get(coll_name)
assert scene is not None, f'Missing scene {scene_name}'
assert coll is not None, f'Missing collection {coll_name}'
objects = list(coll.objects)
assert objects, 'Asset collection is empty'
assert all(o.name not in {'PreviewCamera','PreviewKey','PreviewFill','PreviewRim'} for o in objects), 'Temporary render rig leaked into export'
main = bpy.data.objects.get('Phi Delta Theta')
assert main and main.type == 'MESH' and main.name in coll.objects, 'Expected footprint shell missing from export'
# World-space evaluated bounds and portable dependency report.
evaluated = []
mesh_count = curve_count = other_count = 0
for ob in objects:
    mesh_count += ob.type == 'MESH'
    curve_count += ob.type == 'FONT' or ob.type == 'CURVE'
    other_count += ob.type not in {'MESH','FONT','CURVE'}
    deps = bpy.context.evaluated_depsgraph_get()
    eo = ob.evaluated_get(deps)
    if ob.type == 'MESH':
        me = eo.to_mesh()
        pts = [ob.matrix_world @ v.co for v in me.vertices]
        if pts:
            evaluated.append({'name':ob.name,'type':ob.type,'bounds_m':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]], 'modifiers':[m.name for m in ob.modifiers], 'evaluated_vertices':len(me.vertices)})
        eo.to_mesh_clear()
    elif ob.type in {'FONT','CURVE'}:
        evaluated.append({'name':ob.name,'type':ob.type,'modifiers':[m.name for m in ob.modifiers]})
external=[]
for im in bpy.data.images:
    if im.source == 'FILE' and im.filepath and not im.packed_file:
        path = bpy.path.abspath(im.filepath)
        if not Path(path).exists(): external.append({'image':im.name,'path':path})
# Compare the base ring vertices from the opened mesh to official feature geometry.
feature=json.loads(gis_path.read_text(encoding='utf-8'))['features'][0]
ring=feature['geometry']['rings'][0][:-1]
expected=[]
for lon,lat in ring:
    expected.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)), (lat-40.4274)*111040.0))
xy=[(v.co.x,v.co.y) for v in main.data.vertices if abs(v.co.z)<1e-5]
nearest=[]
for x,y in expected:
    nearest.append(min(math.hypot(x-a,y-b) for a,b in xy))
actual_bounds=[min(x for x,y in xy),max(x for x,y in xy),min(y for x,y in xy),max(y for x,y in xy)]
expected_bounds=[min(x for x,y in expected),max(x for x,y in expected),min(y for x,y in expected),max(y for x,y in expected)]
result={
 'building_id':'massing_phi_delta_theta_258cddd','asset_path':str(asset_path.relative_to(root)).replace('\\','/'),'blender_version':bpy.app.version_string,
 'asset_sha256':hashlib.sha256(asset_path.read_bytes()).hexdigest(),'reopened_saved_asset':True,
 'scene':scene_name,'collection':coll_name,'collection_object_count':len(objects),'object_types':{'mesh':mesh_count,'curve_or_font':curve_count,'other':other_count},
 'main_shell':{'name':main.name,'vertices':len(main.data.vertices),'polygons':len(main.data.polygons),'source_ring_vertices':len(expected),'shell_base_ring_vertices':len(xy),'max_nearest_xy_error_m':max(nearest),'mean_nearest_xy_error_m':sum(nearest)/len(nearest),'expected_xy_bounds_m':expected_bounds,'actual_xy_bounds_m':actual_bounds,'z_bounds_m':[min(v.co.z for v in main.data.vertices),max(v.co.z for v in main.data.vertices)]},
 'unpacked_external_file_dependencies':external,'evaluated_mesh_object_bounds':evaluated,
 'checks':{'scene_present':True,'collection_present':True,'asset_nonempty':bool(objects),'exact_named_shell_present':True,'base_ring_matches_gis_within_0_001m':max(nearest)<0.001,'no_unpacked_external_dependencies':not external,'no_preview_rig_in_export':True}
}
assert result['checks']['base_ring_matches_gis_within_0_001m']
assert not external
out_path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ('blender_version','asset_sha256','collection_object_count','object_types','main_shell','checks')},indent=2))
