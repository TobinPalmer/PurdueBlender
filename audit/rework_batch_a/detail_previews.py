import bpy,os,json,math
from mathutils import Vector
ROOT=os.path.abspath('.');OUT=os.path.join(ROOT,'audit','rework_batch_a')
assets=[('MSEE','materials_science_and_electrical_engineering_msee','audit/build_batch_a2/materials_science_and_electrical_engineering_msee_evidence.json'),('BCHM','biochemistry_building','audit/build_batch_a/biochemistry_building_evidence.json'),('ADDL','animal_disease_diagnostic_laboratory','audit/build_batch_a/animal_disease_diagnostic_laboratory_evidence.json'),('BRFM','david_and_bonnie_brunner_farm_animal_hospital','audit/build_batch_a/david_and_bonnie_brunner_farm_animal_hospital_evidence.json'),('AGAD','agricultural_administration_building','audit/build_batch_a/agricultural_administration_building_evidence.json'),('ABE','agricultural_and_biological_engineering_abe','audit/build_batch_a/agricultural_and_biological_engineering_abe_evidence.json'),('BIDC','bechtel_innovation_design_center_bidc','audit/build_batch_a/bechtel_innovation_design_center_bidc_evidence.json'),('BIND','bindley_bioscience_center','audit/build_batch_a/bindley_bioscience_center_evidence.json'),('DAUC','dauch_alumni_center','audit/build_batch_a/dauch_alumni_center_evidence.json'),('NWCP','northwest_chiller_plant','audit/build_batch_a2/northwest_chiller_plant_evidence.json')]
def bnd(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box];return [min(q[i] for q in p) for i in range(3)],[max(q[i] for q in p) for i in range(3)]
for code,asset,evrel in assets:
 path=os.path.join(ROOT,'modular','buildings',asset+'.blend');bpy.ops.wm.open_mainfile(filepath=path);col=bpy.data.collections.get('Asset_'+asset)
 # Partly transparent architectural glazing reveals shallow, clearly schematic room cues in front of the existing solid GIS shell.
 for m in bpy.data.materials:
  if m.name in (code+'_revision_lobby_curtainwall',code+'_revision_entry_glass',code+'_revision_lobby_curtainwall'):
   p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Alpha'].default_value=.34
   if 'Transmission Weight' in p.inputs:p.inputs['Transmission Weight'].default_value=.28
   p.inputs['Roughness'].default_value=.2
   try:m.surface_render_method='DITHERED'
   except:pass
 door=next((o for o in col.all_objects if o.type=='MESH' and (o.name.endswith('_main_entrance_glazed_door') or o.name=='MSEE_primary_glazed_doors')),None)
 if door:
  lo,hi=bnd(door);dc=[(lo[i]+hi[i])/2 for i in range(3)];widths=[hi[i]-lo[i] for i in range(3)];normal=1 if widths[0]>=widths[1] else 0
  shell=next(o for o in col.all_objects if o.type=='MESH' and ('GIS' in o.name or 'official_GIS' in o.name));slo,shi=bnd(shell);side=-1 if abs(dc[normal]-slo[normal])<abs(dc[normal]-shi[normal]) else 1
  target=(dc[0],dc[1],3.8)
  if code=='MSEE':target=(-13.5,-19.4,4.2)
  camdata=bpy.data.cameras.new('R2_'+code+'_detail_camera');cam=bpy.data.objects.new('R2_'+code+'_detail_camera',camdata);bpy.context.scene.collection.objects.link(cam);camdata.lens=45
  if normal==1:cam.location=(target[0]+8,target[1]+side*17,target[2]+4.2)
  else:cam.location=(target[0]+side*17,target[1]+8,target[2]+4.2)
  direction=Vector(target)-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();scene=bpy.context.scene;old=scene.camera;scene.camera=cam;scene.render.filepath=os.path.join(OUT,asset+'_revision2_detail_preview.png');bpy.ops.render.render(write_still=True);scene.camera=old;bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(camdata)
 bpy.ops.wm.save_as_mainfile(filepath=path)
 evpath=os.path.join(ROOT,evrel);ev=json.load(open(evpath,encoding='utf-8'));ev.setdefault('validation',{})['revision2_detail_preview']=os.path.relpath(os.path.join(OUT,asset+'_revision2_detail_preview.png'),ROOT).replace('/','\\');ev.setdefault('revision_history',[]).append({'date':'2026-10-24','geometry_edits':['Rendered a separate close view of the entry and visible interior vignette for review.'],'materials':'Entrance/modern lobby glazing is partially transparent to improve visibility of the clearly schematic room cues; the underlying shell and plan outline remain intact.'});json.dump(ev,open(evpath,'w',encoding='utf-8'),indent=2)
 print('DETAIL',code,flush=True)
