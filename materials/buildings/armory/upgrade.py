import bpy,sys,json
from pathlib import Path
ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');sys.path.insert(0,str(ROOT/'materials'));sys.path.insert(0,str(ROOT/'materials/buildings/armory'))
import pbr_upgrade as p
from secondary import secondary,setup,aim
col=bpy.data.collections['Asset_armory'];obs=list(col.all_objects)
before={o.name:list(sum((list(row) for row in o.matrix_world),[])) for o in obs}
p.upgrade_brick(bpy.data.materials['Purdue_Red_Brick'],tint=(.88,.84,.78,1))
brick=[]
for o in obs:
 if o.type=='MESH' and any(s.material and s.material.name=='Purdue_Red_Brick' for s in o.material_slots):p.metric_uv(o);brick.append(o.name)
secondary();p.pack_textures();cam=setup();aim(cam,(112,-135,70),(0,0,8),48)
assert before=={o.name:list(sum((list(row) for row in o.matrix_world),[])) for o in obs}
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'modular/buildings/armory.blend'))
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modular/buildings/armory.blend'))
s=bpy.context.scene;cam=s.camera
assert len(bpy.data.collections['Asset_armory'].all_objects)==967
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
(ROOT/'materials/buildings/armory/verification.json').write_text(json.dumps({'objects':967,'brick_objects':len(brick),'unchanged_matrices':True,'packed_images':len(bpy.data.images),'reopened':True},indent=2))
s.render.filepath=str(ROOT/'materials/buildings/armory/hero.png');bpy.ops.render.render(write_still=True)
aim(cam,(38,-29,7),(24.5,-22,6.5),55);s.render.filepath=str(ROOT/'materials/buildings/armory/closeup.png');bpy.ops.render.render(write_still=True)
