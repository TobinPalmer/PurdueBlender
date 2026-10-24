import bpy,os
p=os.path.abspath(r'modular/buildings/knoy_hall.blend');bpy.ops.wm.open_mainfile(filepath=p)
o=bpy.data.objects.get('KNOY_FloorSlab_L5')
if o:
 o['story_status']='UNVERIFIED / SOURCE CONFLICT'
 o['story_evidence']='The recovered Purdue Gateway study (2018-05-31), page 24, identifies existing Knoy Levels 1-4 and states 14 ft 8 in level-to-level. It does not document a fifth occupied level.'
 o['interpretation']='Retained as inherited roof/upper-slab geometry because available evidence cannot determine whether this slab is a misnamed roof slab or unsupported additional floor; do not count it as a verified story.'
sc=bpy.context.scene;sc['unverified_l5_status']='Inherited KNOY_FloorSlab_L5 is retained and explicitly labeled UNVERIFIED / SOURCE CONFLICT; the 2018 Purdue source shows only Levels 1-4.'
# The model now has a source-based upper-floor partition trace. Keep source file and scene metadata in sync.
sc['typical_upper_plan_trace_count_per_level']=len(__import__('json').load(open(r'C:\\Users\\Tobin\\Documents\\Blender\\PurdueMap\\audit\\complete_knoy\\upper_plan_wall_trace.json',encoding='utf-8'))['segments'])
sc['typical_upper_plan_trace_evidence']='audit/complete_knoy/upper_plan_wall_trace.json; raster extraction from 2018 Gateway PDF page 24.'
bpy.ops.wm.save_as_mainfile(filepath=p);print('saved L5 uncertainty label; status',o.get('story_status'))

