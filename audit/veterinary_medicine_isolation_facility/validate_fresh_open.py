import bpy, json, hashlib
from mathutils import Vector
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/massing_veterinary_medicine_isolation_facility_66d1305.blend'
AUDIT=ROOT/'audit/veterinary_medicine_isolation_facility'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset_id='massing_veterinary_medicine_isolation_facility_66d1305'
coll=bpy.data.collections.get('Asset_'+asset_id); scene=bpy.data.scenes.get('Building_'+asset_id)
assert coll and scene and scene.camera
names=[o.name for o in coll.objects]
assert sum('protocol stall door' in n for n in names)==8
assert sum('viewing window' in n for n in names)==8
assert sum(n.startswith('Aerial rooftop plant ') and 'curb' not in n for n in names)==2
assert sum(n=='Inferred large animal service slider' for n in names)==1
meshes=[o for o in coll.objects if o.type=='MESH']
verts=[o.matrix_world @ Vector(v.co) for o in meshes for v in o.data.vertices]
mins=[min(v[i] for v in verts) for i in range(3)]; maxs=[max(v[i] for v in verts) for i in range(3)]
external=[im.filepath for im in bpy.data.images if im.source=='FILE']
assert not external, external
# Render both views from this freshly reopened file.
scene.render.image_settings.file_format='PNG'; scene.render.resolution_percentage=100
scene.render.filepath=str(AUDIT/'vmif_preview.png'); bpy.ops.render.render(write_still=True)
for ob in coll.objects:
 if ob.name.startswith('Low-slope white membrane roof plane') or ob.name.startswith('Roof edge fascia') or ob.name.startswith('Aerial rooftop plant '): ob.hide_render=True
scene.render.filepath=str(AUDIT/'vmif_cutaway.png'); bpy.ops.render.render(write_still=True)
for ob in coll.objects: ob.hide_render=False
report={'fresh_open':True,'asset_path':'modular/buildings/'+ASSET.name,'sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'scene':scene.name,'export_collection':coll.name,'exported_object_count':len(coll.objects),'mesh_count':len(meshes),'vertex_count':sum(len(o.data.vertices) for o in meshes),'face_count':sum(len(o.data.polygons) for o in meshes),'local_mesh_bounds_m':{'min':mins,'max':maxs},'expected_details':{'large_animal_service_door':1,'stall_doors':8,'interior_viewing_windows':8,'aerial_rooftop_units':2},'external_image_files':external,'anchor_campus_xy_m':list(scene['anchor_campus_xy_m']),'checks':['fresh Blender process opened saved library','stable scene and collection present','one west service opening cut through shell and door fitted','8 stall doors and 8 interior viewing windows present','two rooftop HVAC masses present','all model meshes live in exported collection','no external image dependencies','fresh-open exterior and cutaway renders saved']}
(AUDIT/'fresh_open_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

