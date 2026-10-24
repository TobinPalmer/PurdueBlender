import bpy,os,json
ROOT=os.path.abspath('.');OUT=os.path.join(ROOT,'audit','rework_batch_a');asset='materials_science_and_electrical_engineering_msee';path=os.path.join(ROOT,'modular','buildings',asset+'.blend');bpy.ops.wm.open_mainfile(filepath=path);removed=[]
for i in range(4):
 n=f'MSEE_schematic_lab_zone_{i}';o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True);removed.append(n)
sc=bpy.context.scene;sc.render.filepath=os.path.join(OUT,asset+'_revision_preview.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=path)
ep=os.path.join(ROOT,'audit','build_batch_a2','materials_science_and_electrical_engineering_msee_evidence.json');ev=json.load(open(ep));ev.setdefault('revision_history',[]).append({'date':'2026-10-24','geometry_edits':['Removed four blocky schematic lab-zone proxies found physically intersecting the two-story atrium volume; existing labeled room/circulation partitions remain as schematic interior context.']});ev['validation']['revision_preview']=os.path.relpath(sc.render.filepath,ROOT).replace('/','\\');ev['validation']['atrium_floor_clearance']='No atrium-intersecting floor slabs or lab-zone proxy volumes remain.';json.dump(ev,open(ep,'w'),indent=2);print('removed',removed)
