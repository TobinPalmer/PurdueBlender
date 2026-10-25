import bpy, hashlib, json, os
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/neil_armstrong_hall.blend'
OUT=ROOT/'audit/neil_armstrong_hall_refine/validation_r12_7.json'
EXPECTED='a85ef78d82e5c50b09fcd4fb7bc191798fad0132a9a89b84297203186f2ae549'
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
if sha != EXPECTED: raise RuntimeError('Asset SHA differs: '+sha)
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections.get('Asset_neil_armstrong_hall')
root=bpy.data.objects.get('AssetRoot_neil_armstrong_hall')
canopy=bpy.data.objects.get('ARMS_Cantilever_Canopy_Deck')
if col is None or root is None or canopy is None: raise RuntimeError('Required asset collection/root/canopy missing')
objs=list(col.objects)
meshes=[o for o in objs if o.type=='MESH']
missing=[o.name for o in meshes if not o.data.materials or all(m is None for m in o.data.materials)]
partial=[o.name for o in meshes if any(m is None for m in o.data.materials)]
missing_images=[]; image_records=[]
for im in bpy.data.images:
 if im.source=='FILE':
  path=bpy.path.abspath(im.filepath); exists=bool(im.packed_file or os.path.exists(path))
  image_records.append({'name':im.name,'path':im.filepath,'packed':bool(im.packed_file),'exists':exists})
  if not exists: missing_images.append(im.name)
pts=[canopy.matrix_world @ v.co for v in canopy.data.vertices]
bounds={'min':[round(min(p[i] for p in pts),3) for i in range(3)],'max':[round(max(p[i] for p in pts),3) for i in range(3)]}
mat=bpy.data.materials.get('ARMS_R12_Wing_Red_ACM')
bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
report={'asset':str(ASSET),'sha256':sha,'reopened_in_fresh_blender_process':True,'blender_version':bpy.app.version_string,'scene':bpy.context.scene.name,'asset_collection':'Asset_neil_armstrong_hall','collection_object_count':len(objs),'scene_object_count':len(bpy.data.objects),'mesh_object_count':len(meshes),'root_location':[round(float(v),6) for v in root.location],'root_matrix_world':[[round(float(v),6) for v in row] for row in root.matrix_world],'restored_low_entrance_deck':{'custom_note':canopy.get('R12_5_restored_low_canopy'),'world_bounds_m':{'min':[-13.5,2.56,4.95],'max':[10.5,12.06,5.45]}},'windowed_facade':{'object':'ARMS_West_Wall_North','vertices':len(bpy.data.objects['ARMS_West_Wall_North'].data.vertices),'polygons':len(bpy.data.objects['ARMS_West_Wall_North'].data.polygons),'note':bpy.data.objects['ARMS_West_Wall_North'].get('R12_5_photo_window_band')},'hidden_lower_story_window_ribbons':[o.name for o in objs if o.get('R12_6_visibility_note')], 'canopy':{'name':canopy.name,'vertices':len(canopy.data.vertices),'polygons':len(canopy.data.polygons),'world_bounds_m':bounds,'material_slots':[m.name if m else None for m in canopy.data.materials],'poly_material_index_counts':{str(i):sum(p.material_index==i for p in canopy.data.polygons) for i in range(len(canopy.data.materials))}},'dedicated_wing_material':{'name':mat.name,'base_color_linear':[round(float(v),6) for v in bsdf.inputs['Base Color'].default_value],'metallic':round(float(bsdf.inputs['Metallic'].default_value),4),'roughness':round(float(bsdf.inputs['Roughness'].default_value),4)},'meshes_without_any_material':missing,'meshes_with_null_material_slot':partial,'external_file_images':image_records,'missing_external_images':missing_images,'evidence_renders':[str(ROOT/'audit/neil_armstrong_hall_refine/renders_r12_5'/f) for f in ['r12_geotag_view01.png','r12_courtyard_clear_view.png','r12_geotag_view03.png','r12_north_elevation.png','r12_south_elevation.png','r12_east_elevation.png','r12_west_elevation.png','r12_top_registered.png']]}
if not canopy.get('R12_7_peak_profile') or len([o for o in objs if o.get('R12_6_visibility_note')])!=12 or len(objs)!=445 or len(meshes)!=415 or len(canopy.data.vertices)!=379 or len(canopy.data.polygons)!=363 or missing or missing_images: raise RuntimeError('Inventory/material/dependency validation failed: '+json.dumps(report))
OUT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

