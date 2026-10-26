import bpy, sys, json, hashlib
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[0]) if args else Path('probe.json')
asset=Path(bpy.data.filepath)
expected_scene='Building_massing_university_church_84b2a1b'
expected_collection='Asset_massing_university_church_84b2a1b'
scene=bpy.data.scenes.get(expected_scene)
col=bpy.data.collections.get(expected_collection)
report={'fresh_open':True,'asset_path':str(asset),'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'expected_scene_present':scene is not None,'expected_collection_present':col is not None}
if scene and col:
 objs=list(col.all_objects)
 report.update({'object_count':len(objs),'mesh_count':sum(o.type=='MESH' for o in objs),'collection_scene_linked':any(c==col for c in scene.collection.children),'collection_objects_outside_root':sum(o.name not in col.objects and o.name not in scene.objects for o in objs)})
 shell=bpy.data.objects.get('University Church | GIS brick envelope')
 if shell and shell.type=='MESH':
  coords=[shell.matrix_world @ v.co for v in shell.data.vertices]
  report['shell_bounds_xyz']=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
  report['shell_vertex_count']=len(shell.data.vertices)
  report['shell_face_count']=len(shell.data.polygons)
 else: report['shell_missing']=True
 report['arch_window_head_count']=sum('arched window head' in o.name.lower() for o in objs)
 report['oculus_present']=any('oculus' in o.name.lower() for o in objs)
 report['tower_present']=any('bell tower shaft' in o.name.lower() for o in objs)
 report['portico_columns']=sum('portico column shaft' in o.name.lower() for o in objs)
 report['doors']=sum('timber double door' in o.name.lower() for o in objs)
 report['materialless_meshes']=[o.name for o in objs if o.type=='MESH' and not o.data.materials]
 report['external_images']=[{'name':im.name,'path':im.filepath} for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file]
 report['missing_library_paths']=[lib.filepath for lib in bpy.data.libraries if lib.filepath and not Path(bpy.path.abspath(lib.filepath)).exists()]
 report['scene_camera']=scene.camera.name if scene.camera else None
 report['scene_units']=scene.unit_settings.system
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))

