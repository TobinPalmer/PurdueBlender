import bpy, math
p='modular/buildings/knoy_hall.blend';bpy.ops.wm.open_mainfile(filepath=p);s=bpy.context.scene
mat=bpy.data.materials.get('KNOY_Ground_Painted_Partitions')
if mat and mat.node_tree: next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(0.55,0.58,0.62,1)
for o in s.objects:
 if o.type=='LIGHT': o.hide_render=True
 if o.name.startswith(('KNOY_FloorSlab_Basement','KNOY_FloorSlab_L1','KNOY_FloorSlab_L2','KNOY_FloorSlab_L3','KNOY_FloorSlab_L4','KNOY_FloorSlab_L5','KNOY_FloorSlab_RoofDeck','KNOY_Exterior_Masonry_Walls','KNOY_Fenestration','KNOY_Entrances','KNOY_Roof_','KNOY_Structural_Columns','KNOY_Plaza')): o.hide_render=True
for ob in list(s.objects):
 if ob.name.startswith('KNOY_EvidencePlan'): bpy.data.objects.remove(ob,do_unlink=True)
d=bpy.data.cameras.new('KNOY_EvidencePlanCamera');c=bpy.data.objects.new('KNOY_EvidencePlanCamera',d);s.collection.objects.link(c);c.location=(0,0,125);d.type='ORTHO';d.ortho_scale=102;s.camera=c
ld=bpy.data.lights.new('KNOY_EvidencePlanSun','SUN');lo=bpy.data.objects.new('KNOY_EvidencePlanSun',ld);s.collection.objects.link(lo);lo.rotation_euler=(0,0,0);ld.energy=2.0
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch4_knoy\knoy_ground_plan_readable.png'
s.world.color=(.7,.72,.74)
if s.world and s.world.use_nodes:
 b=s.world.node_tree.nodes.get('Background');b.inputs['Color'].default_value=(.7,.72,.74,1);b.inputs['Strength'].default_value=.4
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1
bpy.ops.render.render(write_still=True)
