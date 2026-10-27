"""Fresh-open validation for The Caretaker's Cottage asset. Run with Blender --background --python this_file.py."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];SRC=HERE/'sources'
AID='massing_the_caretaker_s_cottage_6b24af9';ASSET=ROOT/'modular'/'buildings'/f'{AID}.blend';COLL='Asset_'+AID;SCENE='Building_'+AID

def xy(lon,lat):return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0)

def main():
 bpy.ops.wm.open_mainfile(filepath=str(ASSET));scene=bpy.context.scene;coll=bpy.data.collections.get(COLL);body=bpy.data.objects.get("The Caretaker's Cottage")
 if coll is None or body is None:raise RuntimeError('Missing expected scene collection or structural shell')
 osm=json.loads((SRC/'osm_full_953041335.json').read_text(encoding='utf-8'));els=osm['elements'];way=next(e for e in els if e['type']=='way' and e['id']==953041335);nodes={e['id']:(e['lon'],e['lat']) for e in els if e['type']=='node'};ring=[xy(*nodes[n]) for n in way['nodes'][:-1]]
 actual=[body.matrix_world@body.data.vertices[i].co for i in range(min(len(ring),len(body.data.vertices)))];errs=[math.dist((p.x,p.y),q) for p,q in zip(actual,ring)]
 deps=bpy.context.evaluated_depsgraph_get();allco=[];meshinfo=[]
 for ob in coll.objects:
  if ob.type!='MESH':continue
  ev=ob.evaluated_get(deps);me=ev.to_mesh()
  try:
   coords=[ev.matrix_world@v.co for v in me.vertices];allco+=coords
   meshinfo.append({'object':ob.name,'verts':len(me.vertices),'faces':len(me.polygons),'materials':len(ob.data.materials),'modifier_count':len(ob.modifiers),'transform_location':list(ob.location),'rotation':list(ob.rotation_euler),'scale':list(ob.scale)})
  finally:ev.to_mesh_clear()
 if not allco:raise RuntimeError('No meshes in expected collection')
 bounds=[[min(p.x for p in allco),min(p.y for p in allco),min(p.z for p in allco)],[max(p.x for p in allco),max(p.y for p in allco),max(p.z for p in allco)]]
 images=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and im.packed_file is None]
 transforms=all(all(abs(x-y)<1e-8 for x,y in zip(ob.location,(0,0,0))) and all(abs(x-y)<1e-8 for x,y in zip(ob.rotation_euler,(0,0,0))) and all(abs(x-y)<1e-8 for x,y in zip(ob.scale,(1,1,1))) for ob in coll.objects)
 result={'asset':str(ASSET),'reopened_saved_asset':True,'blender_version':bpy.app.version_string,'expected_scene':SCENE,'actual_scene':scene.name,'expected_collection':COLL,'collection_found':True,'collection_object_count':len(coll.objects),'mesh_count':sum(o.type=='MESH' for o in coll.objects),'body_mesh_vertices':len(body.data.vertices),'body_mesh_faces':len(body.data.polygons),'source_osm_way':953041335,'source_unique_ring_points':len(ring),'base_ring_vertices_compared':len(actual),'max_xy_ring_error_m':max(errs),'all_source_points_match':len(actual)==len(ring) and max(errs)<0.001,'asset_bounds_world_m':bounds,'asset_height_m':bounds[1][2]-bounds[0][2],'object_transforms_identity':transforms,'materialless_mesh_count':sum(not o.data.materials for o in coll.objects if o.type=='MESH'),'unpacked_external_images':images,'non_asset_presentation_collection':'Presentation_Only','checks':{'expected_scene_and_collection':scene.name==SCENE and coll.name==COLL,'named_shell_ring_matches_osm':len(actual)==10 and max(errs)<.001,'campus_world_coordinate_massing':transforms,'portable_procedural_materials':not images,'height_is_explicit_estimate':True},'limitations':['OSM and Indiana LiDAR footprints differ: OSM maps the wall/base footprint; Indiana 2018 polygon is larger and follows the roof envelope in the orthophoto (IoU 0.722).','Wall top (3.35 m), eaves (3.48 m), ridge (5.55 m), cross roof and window/entry positions are qualitative estimates; no measured elevation or roof plan was found.','Master integration and duplicate replacement are outside this building-library audit.'],'objects':meshinfo}
 result['passed']=all(result['checks'].values()) and result['all_source_points_match'] and result['materialless_mesh_count']==0
 (HERE/'reopen_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:result[k] for k in ['passed','actual_scene','collection_object_count','mesh_count','max_xy_ring_error_m','asset_bounds_world_m','asset_height_m','object_transforms_identity','materialless_mesh_count','unpacked_external_images']},indent=2))
if __name__=='__main__':main()

