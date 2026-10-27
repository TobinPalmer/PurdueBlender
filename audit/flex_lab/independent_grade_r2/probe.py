import bpy, hashlib, json
from pathlib import Path
from mathutils import Vector
p=Path(bpy.data.filepath).resolve(); root=p.parents[2]
collection=bpy.data.collections.get('Asset_flex_lab')
shell=bpy.data.objects.get('FLEX structural shell | GIS outline')
assert collection is not None and shell is not None and bpy.context.scene is not None
objects=list(collection.all_objects)
meshes=[o for o in objects if o.type=='MESH']
points=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
bounds=[[min(q[i] for q in points),max(q[i] for q in points)] for i in range(3)]
root_obj=bpy.data.objects.get('AssetRoot_flex_lab')
canopies=[o for o in objects if 'canopy' in o.name.lower() or 'cantilever' in o.name.lower()]
curtain=[o for o in objects if 'curtainwall' in o.name.lower() or 'glass lite' in o.name.lower()]
brick=[o for o in objects if any(t in o.name.lower() for t in ('brick','masonry','pier','spandrel'))]
library_links_at_fresh_open=[str(lib.filepath) for lib in bpy.data.libraries if lib.filepath]
images=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:
  path=Path(bpy.path.abspath(im.filepath))
  if not im.packed_file and not path.exists(): images.append({'name':im.name,'path':im.filepath})
with bpy.data.libraries.load(str(root/'audit/flex_lab/flex_lab_before_r2.blend'),link=False) as (src,dst):
 dst.objects=['FLEX structural shell | GIS outline']
base=dst.objects[0]
base_delta=max((base.data.vertices[i].co-shell.data.vertices[i].co).length for i in range(min(len(base.data.vertices),len(shell.data.vertices)))) if len(base.data.vertices)==len(shell.data.vertices) else None
matdelta=max(abs(base.matrix_world[r][c]-shell.matrix_world[r][c]) for r in range(4) for c in range(4))
materials=sorted({m.name for o in meshes for m in o.data.materials if m})
feature_counts={}
for token in ['curtainwall','canopy','facade','brick','entry','mullion','spandrel','furniture','bench','lab','roof','glass']:
 feature_counts[token]=sum(token in o.name.lower() for o in objects)
shell_xy=sorted({(round(float(v.co.x),6),round(float(v.co.y),6)) for v in shell.data.vertices})
probe={'fresh_open':True,'blender_version':bpy.app.version_string,'asset':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'expected_sha256':'523426ab0f460b4bb7eca72aaf1f85a822300930388cba9e52ba6fa8620b82e9','sha_match':hashlib.sha256(p.read_bytes()).hexdigest()=='523426ab0f460b4bb7eca72aaf1f85a822300930388cba9e52ba6fa8620b82e9','scene':bpy.context.scene.name,'collection_present':collection is not None,'collection_scene_linked':collection in list(bpy.context.scene.collection.children),'object_count':len(objects),'mesh_count':len(meshes),'bounds_world_xyz':bounds,'root':{'name':root_obj.name if root_obj else None,'location':list(root_obj.location) if root_obj else None,'rotation':list(root_obj.rotation_euler) if root_obj else None,'scale':list(root_obj.scale) if root_obj else None},'shell':{'vertex_count':len(shell.data.vertices),'face_count_after_openings':len(shell.data.polygons),'baseline_face_count':len(base.data.polygons),'baseline_vertex_count':len(base.data.vertices),'max_vertex_delta_m':base_delta,'max_world_matrix_delta':matdelta,'world_bounds':[[min((shell.matrix_world @ v.co)[i] for v in shell.data.vertices),max((shell.matrix_world @ v.co)[i] for v in shell.data.vertices)] for i in range(3)],'south_opening_flag':shell.get('flex_r2_south_curtainwall_opening'),'side_bay_count_flag':shell.get('flex_r2_long_facade_curtainwall_bays')},'shell_unique_local_xy_vertices':shell_xy,'canopies':[{'name':o.name,'dimensions':list(o.dimensions),'location':list(o.location)} for o in canopies],'curtainwall_named_object_count':len(curtain),'brick_named_object_count':len(brick),'materials':materials,'named_feature_counts':feature_counts,'missing_external_images':images,'library_links_at_fresh_open':library_links_at_fresh_open,'library_links_after_comparison_load':[str(lib.filepath) for lib in bpy.data.libraries if lib.filepath]}
out=root/'audit/flex_lab/independent_grade_r2/probe.json'; out.write_text(json.dumps(probe,indent=2)+'\n',encoding='utf-8'); print(json.dumps(probe,indent=2))
