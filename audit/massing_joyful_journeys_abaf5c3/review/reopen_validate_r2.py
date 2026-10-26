import bpy,json,math
from mathutils import Vector
from pathlib import Path
asset=Path('modular/buildings/massing_joyful_journeys_abaf5c3.blend')
bpy.ops.wm.open_mainfile(filepath=str(asset))
sc=bpy.context.scene
obs=[]
for o in sc.objects:
 pts=[o.matrix_world@Vector(v) for v in o.bound_box]
 bounds=[[float(min(v[i] for v in pts)),float(max(v[i] for v in pts))] for i in range(3)]
 obs.append({'name':o.name,'type':o.type,'bounds_world_m':bounds,'vertex_count':len(o.data.vertices) if o.type=='MESH' else None,'face_count':len(o.data.polygons) if o.type=='MESH' else None,'modifiers':[m.name for m in o.modifiers],'matrix_world_translation':[float(v) for v in o.matrix_world.translation],'rotation_euler':[float(v) for v in o.rotation_euler],'scale':[float(v) for v in o.scale],'properties':{k:o[k] for k in o.keys()}})
report={'opened_directly':True,'validation_date':'2026-10-26','blender_version':bpy.app.version_string,'asset':str(asset),'scene':sc.name,'expected_scene':'Building_massing_joyful_journeys_abaf5c3','collections':[c.name for c in bpy.data.collections],'expected_collection':'Asset_massing_joyful_journeys_abaf5c3','scene_collection_children':[c.name for c in sc.collection.children],'object_count':len(sc.objects),'objects':obs,'linked_libraries':[l.filepath for l in bpy.data.libraries],'unpacked_external_images':[{'name':i.name,'path':i.filepath} for i in bpy.data.images if i.filepath and not i.packed_file]}
report['checks']={'expected_scene':report['scene']==report['expected_scene'],'expected_collection':report['expected_collection'] in report['collections'],'single_mesh_object':len(obs)==1 and obs[0]['type']=='MESH','identity_transform':obs[0]['matrix_world_translation']==[0.0,0.0,0.0] and obs[0]['rotation_euler']==[0.0,0.0,0.0] and obs[0]['scale']==[1.0,1.0,1.0],'no_modifiers':not obs[0]['modifiers'],'no_linked_libraries':not report['linked_libraries'],'no_external_images':not report['unpacked_external_images'],'asset_exists':asset.exists()}
report['checks']['all_pass']=all(report['checks'].values())
Path('audit/massing_joyful_journeys_abaf5c3/review/direct_reopen_r2.json').write_text(json.dumps(report,indent=2)+'\n')
