import bpy,hashlib,json,os
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/neil_armstrong_hall.blend'
OUT=ROOT/'audit/neil_armstrong_hall_refine/validation_r12_8.json'
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections.get('Asset_neil_armstrong_hall');root=bpy.data.objects.get('AssetRoot_neil_armstrong_hall');deck=bpy.data.objects.get('ARMS_Cantilever_Canopy_Deck')
if col is None or root is None or deck is None: raise RuntimeError('Required building collection/root/canopy missing')
objs=list(col.objects);meshes=[o for o in objs if o.type=='MESH']
missing=[o.name for o in meshes if not o.data.materials or all(m is None for m in o.data.materials)]
nulls=[o.name for o in meshes if any(m is None for m in o.data.materials)]
images=[];missing_images=[]
for im in bpy.data.images:
 if im.source=='FILE':
  p=bpy.path.abspath(im.filepath);exists=bool(im.packed_file or os.path.exists(p));images.append({'name':im.name,'path':im.filepath,'exists':exists})
  if not exists:missing_images.append(im.name)
coords=[deck.matrix_world@v.co for v in deck.data.vertices];seen=set();dups=[]
for p in deck.data.polygons:
 key=tuple(sorted(tuple(round(float(c),5) for c in coords[i]) for i in p.vertices))
 if key in seen:dups.append(p.index)
 seen.add(key)
matnames=[m.name if m else None for m in deck.data.materials]
soffit=bpy.data.materials.get('ARMS_R12_8_Wing_Soffit_ACM')
soffit_i=matnames.index(soffit.name) if soffit and soffit.name in matnames else -1
soffit_faces=sum(p.material_index==soffit_i for p in deck.data.polygons)
low_faces=sum(p.material_index==0 and max((deck.matrix_world@deck.data.vertices[i].co).z for i in p.vertices)<6 for p in deck.data.polygons)
pts=[deck.matrix_world@v.co for v in deck.data.vertices]
report={'asset':str(ASSET),'sha256':sha,'reopened_in_fresh_blender_process':True,'blender_version':bpy.app.version_string,'collection':'Asset_neil_armstrong_hall','collection_object_count':len(objs),'scene_object_count':len(bpy.data.objects),'mesh_object_count':len(meshes),'root_location':[round(float(v),6) for v in root.location],'root_matrix_world':[[round(float(v),6) for v in row] for row in root.matrix_world],'canopy':{'object':deck.name,'vertices':len(deck.data.vertices),'faces':len(deck.data.polygons),'world_bounds_m':{'min':[round(min(p[i] for p in pts),3) for i in range(3)],'max':[round(max(p[i] for p in pts),3) for i in range(3)]},'material_slots':matnames,'soffit_faces':soffit_faces,'retained_low_deck_faces':low_faces,'duplicate_coordinate_faces':dups,'R12_8_notes':{k:deck.get(k) for k in ('R12_8_duplicate_cleanup','R12_8_canopy_profile','R12_8_soffit_finish')}},'meshes_without_any_material':missing,'meshes_with_null_material_slot':nulls,'external_images':images,'missing_external_images':missing_images,'renders':'renders_independent_r12_8/'}
if len(objs)!=445 or len(meshes)!=415 or len(deck.data.vertices)!=371 or len(deck.data.polygons)!=342 or missing or nulls or missing_images or dups or soffit_faces<100 or low_faces!=6:
 raise RuntimeError('R12.8 validation failed: '+json.dumps(report))
OUT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
