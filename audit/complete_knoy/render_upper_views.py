import bpy,math,os
from mathutils import Vector
ROOT=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
BLEND=ROOT+r'\modular\buildings\knoy_hall.blend';OUT=ROOT+r'\audit\batch4_knoy'
bpy.ops.wm.open_mainfile(filepath=BLEND);s=bpy.context.scene
for o in s.objects:
    o.hide_render=True
for o in s.objects:
    if o.type=='LIGHT' and o.name.startswith('KNOY_TypicalPlanRender'):bpy.data.objects.remove(o,do_unlink=True)
for o in list(s.objects):
    if o.name.startswith(('KNOY_TypicalPlanRender','KNOY_TypicalPlanCamera')):bpy.data.objects.remove(o,do_unlink=True)
ld=bpy.data.lights.new('KNOY_TypicalPlanRender_Sun','SUN');light=bpy.data.objects.new('KNOY_TypicalPlanRender_Sun',ld);s.collection.objects.link(light);light.rotation_euler=(0,0,0);ld.energy=2.5;light.hide_render=False
# Render each source-traced floor as a clean plan-style isometric-independent top view.
for level,zbase in [('L2',4.481),('L3',8.961),('L4',13.442)]:
    target=bpy.data.objects.get(f'KNOY_{level}_TypicalPlan_InteriorPartitions')
    if target is None:raise RuntimeError('Missing upper-floor trace '+level)
    stair_prefixes={
        'L2':('KNOY_Stair_L2_L3_',),
        'L3':('KNOY_Stair_L2_L3_','KNOY_Stair_L3_L4_'),
        'L4':('KNOY_Stair_L3_L4_',),
    }[level]
    stairs=[o for o in s.objects if o.name.startswith(stair_prefixes)]
    for o in s.objects:o.hide_render=(o is not target and o is not light and o not in stairs)
    stairmat=bpy.data.materials.new(f'KNOY_PlanRender_{level}_Stairs')
    stairmat.diffuse_color=(.22,.19,.15,1);stairmat.use_nodes=True
    stairbs=next(n for n in stairmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    stairbs.inputs['Base Color'].default_value=(.22,.19,.15,1);stairbs.inputs['Roughness'].default_value=.9
    for stair in stairs:
      stair.data.materials.clear();stair.data.materials.append(stairmat)
    target.hide_render=False
    pm=target.data.materials[0] if target.data.materials else None
    if pm and pm.node_tree: next(n for n in pm.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(0.18,0.14,0.10,1)
    # Flat render-only ground for contrast; deliberately not saved in the library.
    bpy.ops.mesh.primitive_plane_add(size=110,location=(0,0,zbase-0.02));plane=bpy.context.object;plane.name='KNOY_TypicalPlanRender_Ground'
    g=bpy.data.materials.new('KNOY_TypicalPlanRender_GroundMat');g.diffuse_color=(.78,.76,.71,1);g.use_nodes=True
    bs=next(n for n in g.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.72,.70,.65,1);bs.inputs['Roughness'].default_value=.95;plane.data.materials.append(g);plane.hide_render=False
    # A single camera is used for all levels.
    cam=bpy.data.objects.get('KNOY_TypicalPlanCamera')
    if cam is None:
        d=bpy.data.cameras.new('KNOY_TypicalPlanCamera');cam=bpy.data.objects.new('KNOY_TypicalPlanCamera',d);s.collection.objects.link(cam)
    cam.location=(0,0,130);cam.data.type='ORTHO';cam.data.ortho_scale=102;cam.rotation_euler=(0,0,0);cam.hide_render=False;s.camera=cam
    s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1600;s.render.resolution_y=1600;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
    s.world.color=(.7,.7,.7)
    if s.world and s.world.use_nodes:
      bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.7,.7,.7,1);bg.inputs['Strength'].default_value=.6
    s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1
    s.render.filepath=OUT+f'\\knoy_typical_plan_{level}.png';bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(plane,do_unlink=True);bpy.data.materials.remove(g,do_unlink=True)
    bpy.data.materials.remove(stairmat,do_unlink=True)
print('rendered three upper-floor plan views')


