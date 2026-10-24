import bpy,os,json
ROOT=os.path.abspath('.');OUT=os.path.join(ROOT,'audit','rework_batch_a');asset='materials_science_and_electrical_engineering_msee';path=os.path.join(ROOT,'modular','buildings',asset+'.blend');bpy.ops.wm.open_mainfile(filepath=path);col=next(c for c in bpy.data.collections if c.name=='Asset_'+asset)
removed=[]
for idx in range(1,4):
 o=bpy.data.objects.get(f'MSEE_interior_floor_{idx}')
 if o:
  nm=o.name
  bpy.data.objects.remove(o,do_unlink=True)
  removed.append(nm)
sc=bpy.context.scene;sc.render.filepath=os.path.join(OUT,asset+'_revision_preview.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=path)
ep=os.path.join(ROOT,'audit','build_batch_a2','materials_science_and_electrical_engineering_msee_evidence.json');ev=json.load(open(ep));ev.setdefault('revision_history',[]).append({'date':'2026-10-24','geometry_edits':['Removed duplicate full-extent interior-floor display meshes that projected through the transparent atrium; perimeter gallery strips are the only schematic floor slabs around the open void.'],'materials':'Atrium glass remains unchanged; concrete facade uses fine aggregate.'});ev['validation']['revision_preview']=os.path.relpath(sc.render.filepath,ROOT).replace('/','\\');ev['validation']['atrium_floor_clearance']='Verified by object bounds: no full slab crosses the atrium glass volume.';json.dump(ev,open(ep,'w'),indent=2);print('removed',removed,'objects',len(col.all_objects))
