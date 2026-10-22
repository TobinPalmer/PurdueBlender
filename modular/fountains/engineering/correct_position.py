import bpy,json
from pathlib import Path
from mathutils import Vector
D=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath=str(D/'engineering.blend'));s=bpy.context.scene;s.frame_set(72)
o=bpy.data.objects['EF_Liquid_domain']
def bounds():
 bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vv=[ev.matrix_world@v.co for v in me.vertices];n=len(vv);z=[sum(v[i] for v in vv)/n for i in range(3)] if n else None;ev.to_mesh_clear();return n,z
before=bounds();old=Vector(o.location);p=json.loads((D/'position_measurement.json').read_text());target=Vector((p['centroid_local_m'][0],p['centroid_local_m'][1],old.z));delta=target-old
for ob in s.objects:ob.location+=delta
bpy.context.view_layer.update();after=bounds();record={'attempt':2,'before':before,'after':after,'delta':list(delta),'target_osm':p};(D/'attempt2_position.json').write_text(json.dumps(record,indent=2));s['placement']='OSM polygon centroid, not surveyed; named feature283274213';bpy.ops.wm.save_as_mainfile(filepath=str(D/'engineering.blend'));print(record)
