import bpy,json,hashlib
from pathlib import Path
P=Path('modular/buildings/felix_haas_hall.blend');D=Path('audit/batch3_haas')
BASE='e333a99e9b7bbb3288329afad7af177be62d73d9077146a4a579c4b123cb1ec1'
assert bpy.data.filepath.replace('\\','/').endswith(str(P).replace('\\','/'))
assert hashlib.sha256(P.read_bytes()).hexdigest()==BASE, 'Run once against the verified R11 asset only.'
C=bpy.data.collections['Asset_felix_haas_hall'];names=['HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof'];roofs=[bpy.data.objects[n] for n in names]
shell=json.loads((D/'reopen_check_round10.json').read_text())['gis_envelope_bounds_m'];(sminx,sminy,_),(smaxx,smaxy,_)=shell
pad=.25;target=[sminx-pad,sminy-pad,smaxx+pad,smaxy+pad]
def world_bounds():
 q=[o.matrix_world@v.co for o in roofs for v in o.data.vertices]
 return [min(p.x for p in q),min(p.y for p in q),max(p.x for p in q),max(p.y for p in q)]
source=world_bounds();sx=(target[2]-target[0])/(source[2]-source[0]);sy=(target[3]-target[1])/(source[3]-source[1]);cx=(source[0]+source[2])/2;cy=(source[1]+source[3])/2;tx=(target[0]+target[2])/2;ty=(target[1]+target[3])/2
for o in roofs:
 inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  p=o.matrix_world@v.co;p.x=tx+(p.x-cx)*sx;p.y=ty+(p.y-cy)*sy
  if p.z>11.7001:p.z=11.7+(p.z-11.7)/1.8
  v.co=inv@p
 o.data.update();o['R12_roof_note']='XY projection calibrated to unchanged GIS shell bounds plus 0.25 m eave; R11 1.8x rise reverted. Qualitative official image supports low-pitch red tile; absolute height still estimated.'
C['round12_roof']='GIS envelope plus 0.25 m roof eave; R11 unsupported 1.8x rise reverted. Official source visual review supports lower pitch; absolute ridge height remains unmeasured estimate.'
bpy.ops.wm.save_as_mainfile(filepath=str(P))
final=world_bounds();sha=hashlib.sha256(P.read_bytes()).hexdigest()
r={'round':12,'input_r11_sha256':BASE,'post_save_sha256':sha,'roof_objects':names,'gis_shell_bounds_m':shell,'source_roof_plan_bounds_xy_m':[[source[0],source[1]],[source[2],source[3]]],'target_and_final_roof_plan_bounds_xy_m':[[target[0],target[1]],[target[2],target[3]]],'world_xy_scale':[sx,sy],'eave_projection_m':pad,'original_r11_roof_rise_m':4.14,'r12_roof_rise_m':2.30,'eave_z_m':11.70,'main_ridge_z_m':14.0,'entry_roof_peak_z_m':13.2,'gis_shell_edited':False,'placement_origin_edited':False,'object_count_unchanged':len(C.all_objects),'note':'The unrelated far-positive X extent at 19.136 m belongs to entry steps and cheek walls, not the roof.'}
(D/'round12_changes.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r,indent=2))
