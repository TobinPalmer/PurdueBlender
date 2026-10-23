"""Consolidate repeated exterior detail by material for modular linking."""
import bpy, pathlib, json, shutil
ROOT=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');SRC=ROOT/'modular/buildings/elliott_hall_of_music.blend';AUD=ROOT/'audit/batch3_elliott'
shutil.copy2(SRC,AUD/'before_exterior_consolidation.blend');bpy.ops.wm.open_mainfile(filepath=str(SRC));COL=bpy.data.collections['Asset_elliott_hall_of_music']
targets=[o for o in COL.objects if o.name.startswith(('ELLT_EXT_','ELLT_FIN_')) and o.type=='MESH']
before=len(targets);groups={}
for o in targets:
    key=o.data.materials[0].name if o.data.materials and o.data.materials[0] else 'Unassigned'
    groups.setdefault(key,[]).append(o)
result=[]
for key,obs in groups.items():
    # Bake each local architectural position into vertices before joining.
    for o in obs:
        o.data.transform(o.matrix_world);o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)
    if len(obs)>1:
        bpy.ops.object.select_all(action='DESELECT')
        for o in obs:o.select_set(True)
        active=obs[0];bpy.context.view_layer.objects.active=active;bpy.ops.object.join();active.name='ELLT_EXT_Combined_'+''.join(c if c.isalnum() else '_' for c in key)
        merged=active
    else:merged=obs[0]
    merged['combined_material_group']=key
    merged['source_piece_count']=len(obs)
    result.append({'material':key,'pieces':len(obs),'combined_name':merged.name,'vertices':len(merged.data.vertices),'faces':len(merged.data.polygons)})
bpy.ops.wm.save_as_mainfile(filepath=str(SRC));bpy.ops.wm.open_mainfile(filepath=str(SRC));COL=bpy.data.collections['Asset_elliott_hall_of_music']
rep={'saved_and_reopened':True,'exterior_meshes_before':before,'exterior_meshes_after':sum(o.name.startswith(('ELLT_EXT_','ELLT_FIN_')) and o.type=='MESH' for o in COL.objects),'export_mesh_objects':sum(o.type=='MESH' for o in COL.objects),'export_total_objects':len(COL.objects),'groups':result}
(AUD/'exterior_consolidation_result.json').write_text(json.dumps(rep,indent=2));print(json.dumps(rep,indent=2))
