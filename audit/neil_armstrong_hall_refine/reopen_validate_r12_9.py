import bpy,hashlib,json,os
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap');ASSET=ROOT/'modular/buildings/neil_armstrong_hall.blend';OUT=ROOT/'audit/neil_armstrong_hall_refine/validation_r12_9.json'
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections.get('Asset_neil_armstrong_hall');root=bpy.data.objects.get('AssetRoot_neil_armstrong_hall');deck=bpy.data.objects.get('ARMS_Cantilever_Canopy_Deck');wall=bpy.data.objects.get('ARMS_West_Wall_North');sun=bpy.data.objects.get('ARMS_R12_9_Versoleil_Outriggers')
if any(x is None for x in (col,root,deck,wall,sun)):raise RuntimeError('Required R12.9 asset objects missing')
objs=list(col.objects);meshes=[o for o in objs if o.type=='MESH'];missing=[o.name for o in meshes if not o.data.materials or all(m is None for m in o.data.materials)];nulls=[o.name for o in meshes if any(m is None for m in o.data.materials)]
images=[];missing_images=[]
for im in bpy.data.images:
 if im.source=='FILE':
  p=bpy.path.abspath(im.filepath);exists=bool(im.packed_file or os.path.exists(p));images.append({'name':im.name,'path':im.filepath,'exists':exists})
  if not exists:missing_images.append(im.name)
coords=[deck.matrix_world@v.co for v in deck.data.vertices];seen=set();duplicates=[]
for p in deck.data.polygons:
 k=tuple(sorted(tuple(round(float(c),5) for c in coords[i]) for i in p.vertices))
 if k in seen:duplicates.append(p.index)
 seen.add(k)
materials=[m.name if m else None for m in deck.data.materials];soffit=bpy.data.materials['ARMS_R12_8_Wing_Soffit_ACM'];soffit_i=materials.index(soffit.name)
soffit_faces=sum(p.material_index==soffit_i for p in deck.data.polygons)
pts=[deck.matrix_world@v.co for v in deck.data.vertices]
glass_faces=[p for p in wall.data.polygons if p.material_index==1 and max((wall.matrix_world@wall.data.vertices[i].co).x for i in p.vertices)-min((wall.matrix_world@wall.data.vertices[i].co).x for i in p.vertices)>40 and min((wall.matrix_world@wall.data.vertices[i].co).z for i in p.vertices)<13]
report={'asset':str(ASSET),'sha256':sha,'reopened_in_fresh_blender_process':True,'blender_version':bpy.app.version_string,'collection':'Asset_neil_armstrong_hall','collection_object_count':len(objs),'scene_object_count':len(bpy.data.objects),'mesh_object_count':len(meshes),'root_location':[round(float(v),6) for v in root.location],'root_matrix_world':[[round(float(v),6) for v in row] for row in root.matrix_world],'canopy':{'vertices':len(deck.data.vertices),'faces':len(deck.data.polygons),'world_bounds_m':{'min':[round(min(p[i] for p in pts),3) for i in range(3)],'max':[round(max(p[i] for p in pts),3) for i in range(3)]},'material_slots':materials,'soffit_faces':soffit_faces,'duplicate_coordinate_faces':duplicates,'R12_9_folded_wing':deck.get('R12_9_folded_wing'),'eaves_limit':deck.get('R12_9_eaves_limit')},'upper_glazing':{'object':wall.name,'vertices':len(wall.data.vertices),'faces':len(wall.data.polygons),'broad_glass_faces_with_lower_extension':len(glass_faces),'note':wall.get('R12_9_photo_glazing')},'sunshades':{'object':sun.name,'vertices':len(sun.data.vertices),'faces':len(sun.data.polygons),'fins':len(sun.data.polygons)//6,'source_note':sun.get('source_note'),'material_slots':[m.name if m else None for m in sun.data.materials]},'meshes_without_any_material':missing,'meshes_with_null_material_slot':nulls,'external_images':images,'missing_external_images':missing_images,'renders':'renders_independent_r12_9/'}
if len(objs)!=446 or len(meshes)!=416 or len(deck.data.vertices)!=371 or len(deck.data.polygons)!=342 or len(sun.data.polygons)!=516 or duplicates or missing or nulls or missing_images or soffit_faces<100 or len(glass_faces)!=1:raise RuntimeError('R12.9 validation failed: '+json.dumps(report))
OUT.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
