"""Render focused plan views around source-located typical-floor stair cores."""
import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap');OUT=ROOT/'audit/complete_knoy'
BLEND=ROOT/'modular/buildings/knoy_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(BLEND));scene=bpy.context.scene
for o in scene.objects:o.hide_render=True

def mat_color(name,color):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=color;m.use_nodes=True
    bsdf=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value=color;bsdf.inputs['Roughness'].default_value=.85
    bsdf.inputs['Emission Color'].default_value=color;bsdf.inputs['Emission Strength'].default_value=.35
    return m

wall=mat_color('R13_CorePlan_Walls',(.035,.085,.14,1));door=mat_color('R13_CorePlan_Doors',(.86,.25,.08,1))
stair=mat_color('R13_CorePlan_Stairs',(.95,.58,.12,1));fixture=mat_color('R13_CorePlan_Fixtures',(.12,.55,.52,1));floor=mat_color('R13_CorePlan_Floor',(.78,.80,.82,1))
camd=bpy.data.cameras.new('R13_CorePlan_Camera');cam=bpy.data.objects.new('R13_CorePlan_Camera',camd);scene.collection.objects.link(cam);camd.type='ORTHO';camd.ortho_scale=18;cam.location=(0,0,70);cam.rotation_euler=(0,0,0);scene.camera=cam
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.2;scene.display.shading.curvature_valley_factor=1.0;scene.display.shading.background_type='WORLD';scene.display.shading.background_color=(.96,.965,.97)
scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
specs=[('A',(4.283,39.682),'L2'),('B',(-14.349,-5.841),'L2'),('C',(13.041,-46.578),'L2')]
reports=[]
for core,(cx,cy),level in specs:
    part=bpy.data.objects[f'KNOY_{level}_TypicalPlan_InteriorPartitions'];part.hide_render=False;part.data.materials.clear();part.data.materials.append(wall)
    slab=bpy.data.objects[f'KNOY_FloorSlab_{level}'];slab.hide_render=False;slab.data.materials.clear();slab.data.materials.append(floor)
    doors=[]
    for o in bpy.data.collections['KNOY_TypicalPlan_Doors_L2-L4'].objects:
        if o.name.startswith(f'KNOY_{level}_'):
            o.hide_render=False;o.data.materials.clear();o.data.materials.append(door);doors.append(o.name)
    fixtures=[]
    for o in bpy.data.collections['KNOY_TypicalPlan_WashroomFixtures_L2-L4'].objects:
        if o.name.startswith(f'KNOY_{level}_'):
            o.hide_render=False;o.data.materials.clear();o.data.materials.append(fixture);fixtures.append(o.name)
    stairs=[]
    for o in bpy.data.collections['KNOY_TypicalPlan_StairRuns_L2-L4'].objects:
        if o.name.startswith('KNOY_Stair_L2_L3_') and f'Core_{core}' in o.name:
            o.hide_render=False;o.data.materials.clear();o.data.materials.append(stair);stairs.append(o.name)
    cam.location=(cx,cy,70);camd.ortho_scale=18
    out=OUT/f'knoy_l2_stair_core_{core}_plan_r13.png';scene.render.filepath=str(out);bpy.ops.render.render(write_still=True)
    reports.append({'core':core,'center_xy_m':[cx,cy],'image':out.name,'door_panels_in_scene':len(doors),'fixture_proxies_in_scene':len(fixtures),'stair_meshes':stairs,'method':'Top-down render-only crop of L2 plan-traced partitions and associated source-symbol core; colors are audit coding, not finishes.'})
    for o in scene.objects:o.hide_render=True
report={'blend_reopened':str(BLEND),'blend_saved':False,'source':'Purdue 2018 Gateway Formation Study, p.24, Typical Plan Levels 2-4','plan_registration':'Hand-affine estimate, approximately +/-1 m','details':reports,'limits':'Crop demonstrates source-plan relative positions of traced walls/door leaves/stair proxies; stair dimensions, landings, closed poses, complete route and code clearance are not verified.'}
(OUT/'stair_core_plan_validation_r13.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
