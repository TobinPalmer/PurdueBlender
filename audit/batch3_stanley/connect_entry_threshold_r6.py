"""Extend the schematic hall floor under the main entry threshold."""
import bpy,hashlib,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];ASSET=ROOT/'modular/buildings/stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
o=bpy.data.objects['SC_R6_Circulation_Spine_Floor'];before=[];after=[]
inv=o.matrix_world.inverted()
for v in o.data.vertices:
 p=o.matrix_world@v.co;before.append(tuple(p))
 if p.x>27.6:p.x+=.20;v.co=inv@p
o.data.update();bpy.context.view_layer.update()
pts=[o.matrix_world@v.co for v in o.data.vertices]
bounds=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET));sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
door=bpy.data.objects['SC_Main_Door_Left'];dp=[door.matrix_world@Vector(c) for c in door.bound_box];door_min=min(p.x for p in dp);door_max=max(p.x for p in dp)
result={'asset':str(ASSET),'sha256':sha,'corridor_floor_world_bounds_m':bounds,'main_door_x_range_m':[door_min,door_max],'threshold_overlap_m':max(0,bounds[1][0]-door_min),'note':'The connected floor now extends beneath the modeled door plane to join the public entry and interior route.'}
(ROOT/'audit/batch3_stanley/corridor_threshold_r6.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
