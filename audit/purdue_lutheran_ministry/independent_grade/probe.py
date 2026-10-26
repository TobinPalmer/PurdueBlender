import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector
from datetime import date
root_path=Path.cwd(); asset=Path(bpy.data.filepath); evidence_dir=root_path/'audit/purdue_lutheran_ministry'; out=evidence_dir/'independent_grade'/'probe.json'
ASSET_ID='massing_purdue_lutheran_ministry_5425b3c'; collection=bpy.data.collections.get('Asset_'+ASSET_ID); scene=bpy.data.scenes.get('Building_'+ASSET_ID); root=bpy.data.objects.get('AssetRoot_'+ASSET_ID)
assert collection and scene and root
objects=list(collection.all_objects); meshes=[o for o in objects if o.type=='MESH']
root_inv=root.matrix_world.inverted(); points=[root_inv@o.matrix_world@v.co for o in meshes for v in o.data.vertices]
bounds=[[min(float(p[i]) for p in points),max(float(p[i]) for p in points)] for i in range(3)]
# Convert the raw OSM nodes independently using the documented project transform.
osm=json.loads((evidence_dir/'sources/osm_way_860901812_full_2026-10-26.json').read_text(encoding='utf-8'))
way=next(e for e in osm['elements'] if e['type']=='way' and e['id']==860901812); nodes={e['id']:e for e in osm['elements'] if e['type']=='node'}
lon0,lat0=-86.9137,40.4274; mx=111412.84*math.cos(math.radians(lat0)); my=111040.0
campus=[((nodes[n]['lon']-lon0)*mx,(nodes[n]['lat']-lat0)*my) for n in way['nodes'][:-1]]
anchor=[round(float(v),6) for v in root.get('campus_anchor_xy_m')]; local_osm=[[x-anchor[0],y-anchor[1]] for x,y in campus]
wall_objs=[o for o in meshes if o.name.startswith('PLM shell wall ')]
wall_pts=[root_inv@o.matrix_world@v.co for o in wall_objs for v in o.data.vertices if abs((root_inv@o.matrix_world@v.co).z-0.2)<1e-4]
nearest=[]
for target in local_osm:
 nearest.append(min(math.hypot(float(p.x)-target[0],float(p.y)-target[1]) for p in wall_pts))
materials=[m for m in bpy.data.materials if any(m==slot.material for o in meshes for slot in o.material_slots)]
image_paths=[img.filepath for img in bpy.data.images if img.source=='FILE']
node_types={m.name:[n.type for n in m.node_tree.nodes] for m in materials if m and m.use_nodes}
external_libraries=[lib.filepath for lib in bpy.data.libraries]
root_children=sum(1 for o in objects if o.parent==root)
review_col=bpy.data.collections.get('PLM | review-only camera and lights')
asset_camera_lights=[o.name for o in objects if o.type in {'CAMERA','LIGHT'}]
boolean_mods=[{'object':o.name,'modifier':m.name} for o in objects for m in o.modifiers if m.type=='BOOLEAN']
sha=hashlib.sha256(asset.read_bytes()).hexdigest()
probe={'asset_id':ASSET_ID,'asset_path':str(asset.relative_to(root_path)),'sha256':sha,'expected_sha256':'7af28c9b8afe5f84a21506b5de2661d9c08e5f8079dee29364ff91ac6e26d6ec','fresh_open':True,'scene':scene.name,'collection':collection.name,'asset_object_count':len(objects),'mesh_count':len(meshes),'root':{'name':root.name,'location_local':[round(float(v),6) for v in root.location],'anchor_xy_m':anchor,'children_parented_to_root':root_children},'local_bounds_m':bounds,'osm_way_id':way['id'],'osm_tag_name':way.get('tags',{}).get('name'),'osm_node_count':len(local_osm),'wall_shell_vertex_error_to_osm_ring_m':nearest,'max_osm_ring_nearest_vertex_error_m':max(nearest),'active_material_count':len(materials),'material_names':sorted(m.name for m in materials),'texture_image_paths':image_paths,'linked_blend_libraries':external_libraries,'review_camera_lights_inside_asset':asset_camera_lights,'boolean_modifiers_remaining':boolean_mods,'render_roof_visible_default':not bpy.data.collections['PLM | removable roof panels, hide to inspect interior'].hide_render,'review_cameras_outside_asset_collection':bool(review_col and not any(o in objects for o in review_col.objects)),'external_material_nodes':{name:types for name,types in node_types.items() if 'TEX_IMAGE' in types},'bounds_dimensions_m':[bounds[i][1]-bounds[i][0] for i in range(3)]}
out.write_text(json.dumps(probe,indent=2)+'\n',encoding='utf-8');print(json.dumps(probe,indent=2))
if sha!=probe['expected_sha256']:raise RuntimeError('Asset hash differs from assigned revision')
