import bpy,os
from pathlib import Path
from mathutils import Vector
base=Path(r'audit/batch3_stanley').resolve();asset=Path(r'modular/buildings/stanley_coulter_hall.blend').resolve()
bpy.ops.wm.open_mainfile(filepath=str(asset));s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1500;s.render.resolution_y=850;s.render.resolution_percentage=80;s.eevee.taa_render_samples=80
for nm,fn in [('Cam_SC_02_MemorialMall_East_Hero','SC_hero_r5.png'),('Cam_SC_03_East_Portico_Ground','SC_entry_r5.png')]:
 s.camera=bpy.data.objects[nm];s.render.filepath=str(base/fn);bpy.ops.render.render(write_still=True)
# Clean, explicitly schematic top-down piano-nobile use/furniture plate.
cam=bpy.data.objects['Cam_SC_06_Interior_Schematic'];cam.location=(22.3,-6.8,40);cam.rotation_euler=(0,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=18;s.camera=cam
for cn in ['SC_Exterior_Structure','SC_Fenestration','SC_Roof_and_Dormers','SC_Portico_and_Entrances','SC_Plaza_and_Site']:
 for o in bpy.data.collections[cn].objects:o.hide_render=True
for o in bpy.data.collections['SC_Interior_Shell'].objects:
 keep=o.name.startswith(('SC_Shell_Floor_1','SC_GradHub_')) or o.name in ('SC_Lobby_Terrazzo_Floor','SC_Lobby_Reception_Desk')
 if not keep:o.hide_render=True
# Camera-facing floor-plan annotations sit over the schematic floor only in this review render.
def add_label(name,body,loc,size,color=(.08,.1,.12,1)):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.extrude=0
 mat=bpy.data.materials.new(name+'_Ink');mat.diffuse_color=color;mat.use_nodes=True
 nodes=mat.node_tree.nodes;nodes.clear();em=nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=color;out=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(em.outputs[0],out.inputs['Surface']);cu.materials.append(mat)
 ob=bpy.data.objects.new(name,cu);s.collection.objects.link(ob);ob.location=loc;ob.hide_render=False
add_label('R5 schematic title','STANLEY COULTER HALL  |  PIANO-NOBILE USE SCHEMATIC',(17.5,1.8,2.0),.42)
add_label('R5 schematic notice','ROOM LOCATIONS, PARTITIONS, AND FURNITURE ARE UNVERIFIED',(17.5,1.1,2.0),.30,(.45,.12,.06,1))
s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.filepath=str(base/'SC_interior_schematic_r5.png');bpy.ops.render.render(write_still=True)
print('Rendered R5 entrance, exterior, and plan-like schematic interior.')
