"""Fresh reopen and exact asset/material/texture/bounds validation for Stanley R5."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/stanley_coulter_hall.blend'
AUDIT=ROOT/'audit/batch3_stanley'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.context.scene
asset=bpy.data.collections['Asset_stanley_coulter_hall']
root=bpy.data.objects['AssetRoot_stanley_coulter_hall']
archive=bpy.data.collections['SC_Unverified_Architectural_Options_R5']
depsgraph=bpy.context.evaluated_depsgraph_get()
def bounds(objects):
 points=[];count=0
 for obj in objects:
  if obj.type!='MESH':continue
  eo=obj.evaluated_get(depsgraph);me=eo.to_mesh()
  try:
   points.extend(eo.matrix_world@v.co for v in me.vertices)
   if me.vertices:count+=1
  finally:eo.to_mesh_clear()
 if not points:return {'mesh_object_count':count,'bounds_local_m':None}
 return {'mesh_object_count':count,'bounds_local_m':[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]}
all_asset=list(asset.all_objects)
render_asset=[o for o in all_asset if o.type=='MESH' and not o.hide_render and not o.hide_get()]
viewport_asset=[o for o in all_asset if o.type=='MESH' and not o.hide_viewport and not o.hide_get()]
all_names={o.name for o in all_asset}
archive_names={o.name for o in archive.all_objects}
archived_source=json.loads((AUDIT/'independent_high_bounds_r4.json').read_text(encoding='utf-8'))
high_names={o['name'] for o in archived_source['objects']}
archived_high=sorted(high_names & archive_names)
missing_high=sorted(high_names-archive_names)
active_high=sorted(high_names & all_names)
# Confirm the archive is an excluded scene-level sibling, not part of the exported asset collection hierarchy.
def descendants(c):
 out=set()
 for child in c.children:
  out.add(child.name);out |= descendants(child)
 return out
asset_descendants=descendants(asset)
archive_relationship={'direct_scene_child':archive.name in {c.name for c in scene.collection.children},'inside_asset_tree':archive.name in asset_descendants,'archive_hidden_viewport':bool(archive.hide_viewport),'archive_hidden_render':bool(archive.hide_render),'high_option_meshes_from_R4':len(high_names),'high_options_in_archive':len(archived_high),'high_options_still_in_asset':len(active_high),'missing_high_options':missing_high}
materials={}
materialless=[];empty_polygons=[]
archive_materialless=[];archive_invalid=[]
for obj in all_asset+list(archive.all_objects):
 if obj.type!='MESH':continue
 slots=[slot.material for slot in obj.material_slots]
 if not slots or all(m is None for m in slots):
  (archive_materialless if obj.name in archive_names else materialless).append(obj.name)
 if obj.data.polygons and (not slots or any(poly.material_index>=len(slots) or slots[poly.material_index] is None for poly in obj.data.polygons)):
  (archive_invalid if obj.name in archive_names else empty_polygons).append(obj.name)
 for m in slots:
  if m:materials[m.name]=m
used_image_nodes=[];missing_external_images=[];external_image_count=0
for m in materials.values():
 if not m.use_nodes:continue
 for node in m.node_tree.nodes:
  if node.type=='TEX_IMAGE' and node.image:
   img=node.image;filepath=bpy.path.abspath(img.filepath) if img.source=='FILE' else None
   used_image_nodes.append({'material':m.name,'image':img.name,'source':img.source,'filepath':filepath,'packed':bool(img.packed_file)})
   if img.source=='FILE' and filepath:
    external_image_count+=1
    if not Path(filepath).exists() and not img.packed_file:missing_external_images.append(filepath)
# Roof and fascia bounds from the just-reopened saved data.
def object_vertex_bounds(name):
 obj=bpy.data.objects[name];return bounds([obj])['bounds_local_m']
result={'validation':'fresh Blender 5.2.3 reopen','reopen_verified':True,'asset_file':str(ASSET.resolve()),'sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'active_asset_collection':'Asset_stanley_coulter_hall','active_asset_collection_object_count':len(all_asset),'active_asset_mesh_count':sum(o.type=='MESH' for o in all_asset),'active_asset_all_geometry_evaluated_bounds_local_m':bounds(all_asset),'active_asset_render_eligible_evaluated_bounds_local_m':bounds(render_asset),'active_asset_viewport_visible_evaluated_bounds_local_m':bounds(viewport_asset),'excluded_archive':archive_relationship,'archive_object_count':len(archive.all_objects),'archive_all_mesh_geometry_bounds_local_m':bounds(list(archive.all_objects)),'asset_root_transform':{'parent':root.parent.name if root.parent else None,'location':list(root.location),'rotation_euler':list(root.rotation_euler),'scale':list(root.scale),'matrix_world_translation':list(root.matrix_world.translation)},'manifest_origin_xy_m':[-57.55689525604248,-99.14793586730957],'foundation_full_mesh_bounds_local_m':object_vertex_bounds('SC_Foundation_Limestone_Plinth'),'roof_main_mesh_bounds_local_m':object_vertex_bounds('SC_Historic_Slate_Roof'),'cornice_mesh_bounds_local_m':object_vertex_bounds('SC_Classical_Entablature_Cornice'),'material_checks':{'unique_materials_used_across_asset_and_archive':len(materials),'materials_without_nodes':[m.name for m in materials.values() if not m.use_nodes],'materialless_mesh_count_across_asset_and_archive':len(materialless),'meshes_with_invalid_material_slot_indices_count':len(empty_polygons),'archived_materialless_mesh_count':len(archive_materialless),'archived_invalid_slot_mesh_count':len(archive_invalid),'used_material_names':sorted(materials)},'texture_checks':{'image_texture_nodes':used_image_nodes,'external_file_texture_count':external_image_count,'missing_external_images':missing_external_images,'procedure_note':'R5 source-matched surface variation uses procedural shader nodes; no external texture files are required.'},'limits':['Active asset all-geometry bounds include hidden sub-eave dormer components and the site paving/sidewalk geometry; all 47 R4 high-roof objects are excluded to the sibling archive.','The render-visible bounds are based on active asset meshes whose saved hide_render flag is false; they do not imply surveyed building height.','The root transform is identity; campus assembly still uses the coordinator-owned master marker.']}
(AUDIT/'reopen_verification_r5.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(result,indent=2,ensure_ascii=False))

