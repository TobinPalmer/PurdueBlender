import bpy,os,math
from mathutils import Vector
OUT='audit/batch4_rawls';bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
for o in bpy.data.objects:o.hide_render=True
for o in bpy.data.objects:
 if o.name=='RAWL_FloorSlab_L1_Ground' or o.name.startswith('RAWL_2026_Plan') or '1086_Desk' in o.name or '1086_Chair' in o.name or '1086_ChairBack' in o.name or '1086_DeskLeg' in o.name or '1086_DeskSupport' in o.name:o.hide_render=False
# distinctly pale slab and dark wall tops for a readable plan diagram
slab=bpy.data.objects['RAWL_FloorSlab_L1_Ground']
mat=bpy.data.materials.new('RAWL_R3_Cutaway_Plan_Slab');mat.diffuse_color=(.78,.80,.79,1);mat.use_nodes=True;bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.78,.80,.79,1);bs.inputs['Roughness'].default_value=.85
slab.data.materials.clear();slab.data.materials.append(mat)
wall=bpy.data.materials.new('RAWL_R3_Plan_Wall_Contrast');wall.diffuse_color=(.105,.13,.16,1);wall.use_nodes=True;bs=next(n for n in wall.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.105,.13,.16,1);bs.inputs['Roughness'].default_value=.8
for o in bpy.data.objects:
 if o.name.startswith('RAWL_2026_Plan') and o.type=='MESH':o.data.materials.clear();o.data.materials.append(wall)
# camera: true plan view, framing full registered first-floor model extents
ld=bpy.data.lights.new('R3_Plan_Key','AREA');ld.energy=5500;ld.shape='DISK';ld.size=45;l=bpy.data.objects.new('R3_Plan_Key',ld);s.collection.objects.link(l);l.location=(-7,-11,48);l.rotation_euler=(0,0,0)
camd=bpy.data.cameras.new('R3_Plan_Camera');cam=bpy.data.objects.new('R3_Plan_Camera',camd);s.collection.objects.link(cam);cam.location=(-7,-11,65);cam.rotation_euler=(0,0,0);camd.type='ORTHO';camd.ortho_scale=27;s.camera=cam
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=os.path.abspath(OUT+'/core_plan_detail_round4.png')
s.world=bpy.data.worlds.new('R3_Plan_World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.82,.85,.88,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
bpy.ops.render.render(write_still=True)
