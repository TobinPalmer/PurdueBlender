"""Render source-traced interior plans and a bounded L2-L4 stair section.

This is a non-destructive audit render. It opens the saved source blend and never
saves scene or object changes. Stair geometry remains illustrative; only core
locations are traced from Purdue's 2018 typical plan.
"""
import bpy, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
BLEND=ROOT/'modular/buildings/knoy_hall.blend'
OUT=ROOT/'audit/complete_knoy'
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
scene=bpy.context.scene

for obj in scene.objects:
    obj.hide_render=True

def color(obj,rgba):
    obj.color=rgba
    if obj.type=='MESH':
        obj.data.materials.clear()
        mat=bpy.data.materials.get('R13_RenderOnly_'+obj.name)
        if mat is None:
            mat=bpy.data.materials.new('R13_RenderOnly_'+obj.name)
        mat.diffuse_color=rgba
        mat.use_nodes=True
        bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        bsdf.inputs['Base Color'].default_value=rgba
        bsdf.inputs['Roughness'].default_value=.85
        bsdf.inputs['Emission Color'].default_value=rgba
        bsdf.inputs['Emission Strength'].default_value=.35
        obj.data.materials.append(mat)

wall_col=(.035,.085,.14,1)
door_col=(.86,.25,.08,1)
stair_col=(.95,.58,.12,1)
fixture_col=(.12,.55,.52,1)
floor_col=(.78,.80,.82,1)

cam_data=bpy.data.cameras.new('R13_Interior_Plan_Camera')
cam=bpy.data.objects.new('R13_Interior_Plan_Camera',cam_data)
scene.collection.objects.link(cam)
cam_data.type='ORTHO';cam_data.ortho_scale=112
cam.location=(0,-1,80)
cam.rotation_euler=(0,0,0)
scene.camera=cam

scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=False
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.2
scene.display.shading.curvature_valley_factor=1.0
scene.display.shading.background_type='WORLD'
scene.display.shading.background_color=(.96,.965,.97)
scene.render.resolution_x=1650;scene.render.resolution_y=2900
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGBA'

plan_reports=[]
for level,zfloor in [('L2',4.481),('L3',8.961),('L4',13.442)]:
    part=bpy.data.objects[f'KNOY_{level}_TypicalPlan_InteriorPartitions']
    part.hide_render=False;color(part,wall_col)
    slab=bpy.data.objects[f'KNOY_FloorSlab_{level}']
    slab.hide_render=False;color(slab,floor_col)
    included={'partitions':1,'doors':0,'fixtures':0,'stairs':0}
    for obj in bpy.data.collections['KNOY_TypicalPlan_Doors_L2-L4'].objects:
        if obj.name.startswith(f'KNOY_{level}_'):
            obj.hide_render=False;color(obj,door_col);included['doors']+=1
    for obj in bpy.data.collections['KNOY_TypicalPlan_WashroomFixtures_L2-L4'].objects:
        if obj.name.startswith(f'KNOY_{level}_'):
            obj.hide_render=False;color(obj,fixture_col);included['fixtures']+=1
    src,dst=(('L2','L3') if level=='L2' else ('L3','L4'))
    for obj in bpy.data.collections['KNOY_TypicalPlan_StairRuns_L2-L4'].objects:
        if obj.name.startswith(f'KNOY_Stair_{src}_{dst}_'):
            obj.hide_render=False;color(obj,stair_col);included['stairs']+=1
    out=OUT/f'knoy_{level.lower()}_interior_plan_spatial_r13.png'
    scene.render.filepath=str(out)
    bpy.ops.render.render(write_still=True)
    plan_reports.append({'level':level,'render':out.name,'included':included,'camera_scale_m':112,
      'interpretation':'Full-floor, top-down evidence render. Temporary colors distinguish source-traced walls, plan-positioned illustrative doors, stair proxies, and symbol-interpreted fixture stand-ins. They are not actual finishes.'})
    for obj in scene.objects: obj.hide_render=True

report={
 'source_blend_reopened':str(BLEND),
 'source_blend_saved_by_renderer':False,
 'typical_level_views':plan_reports,
 'stair_profile_view':'knoy_core_b_l2_l3_stair_profile_r13.png (rendered by the companion profile script)',
 'stair_core':'Core B, L2-L3 interval; source-symbol location only',
 'stair_geometry_limit':'Flights, treads, landings, dimensions and continuity are illustrative estimates. The plan supports symbol locations, not a verified section or complete egress route.',
 'nonclaims':['no verified basement/L1/L5/roof stair route','no accessibility/code clearance claim','temporary render colors are not finishes']
}
(OUT/'interior_spatial_render_audit_r13.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
