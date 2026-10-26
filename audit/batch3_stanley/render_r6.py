"""Standalone review renders for the R6 Stanley Coulter asset."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit/batch3_stanley'
ASSET=ROOT/'modular/buildings/stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
s=bpy.context.scene
s.render.engine='BLENDER_EEVEE'
s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=80
s.eevee.taa_render_samples=96
s.view_settings.view_transform='AgX'
for nm,fn in [('Cam_SC_02_MemorialMall_East_Hero','SC_hero_r6.png'),('Cam_SC_03_East_Portico_Ground','SC_entry_r6.png')]:
    s.camera=bpy.data.objects[nm];s.render.filepath=str(AUDIT/fn);bpy.ops.render.render(write_still=True)

# Top-down cutaway plate: retain one floor, the actual Grad Hub furniture,
# lobby stair and the explicitly schematic connected circulation spine.
cam=bpy.data.objects['Cam_SC_06_Interior_Schematic']
cam.location=(22.2,-6.4,42);cam.rotation_euler=(0,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=18
s.camera=cam
for cn in ['SC_Exterior_Structure','SC_Fenestration','SC_Roof_and_Dormers','SC_Portico_and_Entrances','SC_Plaza_and_Site']:
    col=bpy.data.collections.get(cn)
    if col:
        for o in col.objects:o.hide_render=True
for o in bpy.data.collections['SC_Interior_Shell'].objects:
    keep=o.name.startswith(('SC_Shell_Floor_1','SC_GradHub_')) or o.name in ('SC_Lobby_Terrazzo_Floor','SC_Lobby_Reception_Desk','SC_Lobby_Staircase_Shell')
    o.hide_render=not keep
# Render new circulation walls and floor, as well as the opening to the modeled stair.
for o in bpy.data.collections['SC_R6_Interior_Circulation_Schematic'].objects:o.hide_render=False
# Remove long directional shadows from the plan plate; the wall/corridor geometry stays readable.
for obj in bpy.data.objects:
    if obj.type=='LIGHT' and obj.data.type=='SUN':
        obj.data.energy=1.0;obj.data.angle=0.35
        if hasattr(obj.data,'use_shadow'):obj.data.use_shadow=False
# Review-only captions identify the route as a diagram and avoid implying an as-built plan.
def label(name,body,loc,size,color=(.08,.10,.13,1)):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.extrude=0
    mat=bpy.data.materials.new(name+'_Ink');mat.diffuse_color=color;mat.use_nodes=True
    mat.node_tree.nodes.clear();em=mat.node_tree.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=color
    out=mat.node_tree.nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(em.outputs[0],out.inputs['Surface']);cu.materials.append(mat)
    ob=bpy.data.objects.new(name,cu);s.collection.objects.link(ob);ob.location=loc;ob.hide_render=False
label('R6_cutaway_title','STANLEY COULTER  |  CONNECTED CIRCULATION STUDY',(14.0,1.95,1.93),.36)
label('R6_cutaway_notice','SCHEMATIC ROUTE; ROOM LAYOUT NOT VERIFIED',(14.0,1.42,1.93),.25,(.46,.12,.04,1))
label('R6_cutaway_route','ENTRY  →  LOBBY / GRAD HUB',(21.3,-2.98,1.91),.24)
label('R6_cutaway_stair','STAIR',(18.45,-6.35,1.91),.22)
cam.data.lens=50
s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.filepath=str(AUDIT/'SC_interior_circulation_r6.png')
bpy.ops.render.render(write_still=True)
print('Rendered R6 exterior hero, entrance, and connected-circulation schematic.')
