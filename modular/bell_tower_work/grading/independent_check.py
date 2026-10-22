import bpy,json,math
from mathutils import Vector
from pathlib import Path
p=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(p.parent.parent/'buildings'/'bell_tower.blend'))
c=bpy.data.collections.get('Asset_bell_tower')
obs=list(c.all_objects)
shaft=next(o for o in obs if o.name=='Shaft_Structural_Envelope')
pts=[o.matrix_world@Vector(v) for o in obs if o.type in {'MESH','FONT','CURVE'} for v in o.bound_box]
r={'opens':True,'collection':c.name,'objects':len(obs),'shaft_center':list(shaft.matrix_world.translation),'shaft_dimensions':list(shaft.dimensions),'shaft_rotation_z_degrees':math.degrees(shaft.matrix_world.to_euler().z),'max_z':max(v.z for v in pts),'libraries':[l.filepath for l in bpy.data.libraries],'image_dependencies':[i.filepath for i in bpy.data.images if i.source=='FILE'],'cameras_or_lights_in_export':[o.name for o in obs if o.type in {'CAMERA','LIGHT'}]}
(p/'independent_check.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r))
