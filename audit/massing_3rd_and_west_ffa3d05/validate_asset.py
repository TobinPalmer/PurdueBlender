"""Reopen validation for the standalone 3rd and West Blender asset."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'audit'/'massing_3rd_and_west_ffa3d05'
ASSET=ROOT/'modular'/'buildings'/'massing_3rd_and_west_ffa3d05.blend'
COL='Asset_massing_3rd_and_west_ffa3d05'
waydata=json.loads((OUT/'sources'/'osm_way_1324500897_snapshot.json').read_text(encoding='utf-8'))
way=waydata['way']; nodes={n['id']:n for n in waydata['nodes']}
expected=[]
for nid in way['nodes'][:-1]:
 n=nodes[nid];lat=float(n['lat']);lon=float(n['lon'])
 expected.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0))
collection=bpy.data.collections.get(COL)
assert collection is not None, 'Expected exported collection missing'
objects=list(collection.all_objects)
assert objects and all(o.type=='MESH' for o in objects)
assert all(o.name.startswith('3rd and West |') for o in objects)
shell=next(o for o in objects if o.name.endswith('five story footprint shell'))
# The structural source ring appears at the base of the shell. Compare vertex pairs, ignoring repeated floor ring vertices.
actual=list(set((float(v.co.x),float(v.co.y)) for v in shell.data.vertices if abs(v.co.z)<1e-5))
assert len(actual)==len(expected), f'footprint vertex count differs: {len(actual)} != {len(expected)}'
nearest=[min(math.dist(p,q) for q in actual) for p in expected]
max_vertex_error=max(nearest)
assert max_vertex_error<0.001, f'footprint vertex mismatch {max_vertex_error} m'
# Structural footprint polygon area in the same local campus approximation.
area=sum(expected[i][0]*expected[(i+1)%len(expected)][1]-expected[(i+1)%len(expected)][0]*expected[i][1] for i in range(len(expected)))/2
assert area>0
xs=[x for x,y in expected];ys=[y for x,y in expected]
# No helper cameras or preview-only ground should be present in the saved library.
scene_objects=set(bpy.context.scene.objects)
assert scene_objects==set(objects), f'unexpected scene objects: {[o.name for o in scene_objects-set(objects)]}'
# Check that the shell and the full asset remain in the intended campus XY frame.
world=[]
for o in objects:
 for c in o.bound_box: world.append(o.matrix_world@Vector(c))
bounds=[[min(p[k] for p in world),max(p[k] for p in world)] for k in range(3)]
shell_bounds=[[min((shell.matrix_world@Vector(c))[k] for c in shell.bound_box),max((shell.matrix_world@Vector(c))[k] for c in shell.bound_box)] for k in range(3)]
assert abs(shell_bounds[0][0]-min(xs))<1e-4 and abs(shell_bounds[0][1]-max(xs))<1e-4
assert abs(shell_bounds[1][0]-min(ys))<1e-4 and abs(shell_bounds[1][1]-max(ys))<1e-4
assert abs(shell_bounds[2][0])<1e-5 and abs(shell_bounds[2][1]-18.0)<1e-4
assert bounds[2][1] <= 19.0 and bounds[2][1] > 18.8
# The asset has no external image, font, or linked-library requirements.
external_images=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath]
external_fonts=[f.filepath for f in bpy.data.fonts if f.filepath and not f.filepath.startswith('<')]
linked=[lib.filepath for lib in bpy.data.libraries if lib.filepath]
assert not external_images and not external_fonts and not linked
report={
 'status':'PASS','asset_path':str(ASSET),'reopened_file':bpy.data.filepath,
 'collection':COL,'scene_name':bpy.context.scene.name,'collection_object_count':len(objects),
 'mesh_object_count':sum(o.type=='MESH' for o in objects),'expected_osm_node_count':len(expected),
 'structural_shell_bounds_world_m':shell_bounds,'all_model_geometry_bounds_world_m':bounds,
 'gis_osm_way_id':way['id'],'footprint_area_m2':area,
 'footprint_vertex_set_match':'within 0.001 m; float32 mesh coordinate maximum vertex error %.8f m' % max_vertex_error,
 'campus_xy_transform':'X=(longitude+86.9137)*111412.84*cos(radians(40.4274)); Y=(latitude-40.4274)*111040',
 'stories_supported_by_source':5,'eave_height_m':'18.0 estimated from 5 x 3.6 m story module',
 'roof_parapet_m':'0.9 estimated','all_scene_objects_belong_to_asset_collection':True,
 'external_image_font_or_library_dependencies':{'images':external_images,'fonts':external_fonts,'libraries':linked}
}
(OUT/'reopen_validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2,ensure_ascii=False))
