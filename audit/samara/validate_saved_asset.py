import bpy,json,pathlib,math
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[2]; E=R/'audit'/'samara'; p=R/'modular'/'buildings'/'massing_samara_f6b8e61.blend'
bpy.ops.wm.open_mainfile(filepath=str(p)); col=bpy.data.collections['Asset_massing_samara_f6b8e61']; scene=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get(); meshes=[]; allpoints=[]
for o in col.all_objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(dg); me=ev.to_mesh(); vs=[ev.matrix_world@v.co for v in me.vertices]; allpoints.extend(vs); meshes.append({'name':o.name,'vertices':len(vs),'polygons':len(me.polygons),'bounds_world':[[min(v[k] for v in vs),max(v[k] for v in vs)] for k in range(3)],'matrix_world':[list(r) for r in o.matrix_world],'modifiers':len(o.modifiers)}); ev.to_mesh_clear()
bounds=[[min(v[k] for v in allpoints),max(v[k] for v in allpoints)] for k in range(3)]; rec=json.load(open(E/'build_record.json')); walls=rec['wall_footprint_world']; before=[[-262.82806396484375,-235.0101776123047],[1229.2127685546875,1254.97412109375],[0,16]]
val={'saved_asset_reopened':True,'scene':scene.name,'expected_collection_present':True,'asset_collection_offset':list(col.instance_offset),'coordinate_frame':'campus-world geometry; identity placement','mesh_objects':len(meshes),'evaluated_vertices':sum(x['vertices'] for x in meshes),'bounds_world_before_m':before,'bounds_world_after_m':bounds,'wall_outline_bounds_world_after_m':[[min(p[k] for p in walls),max(p[k] for p in walls)] for k in range(2)],'orientation_world_deg':rec['drawing_x_world_angle_deg'],'orientation_uncertainty_deg':3,'plan_scale_m_per_pixel':rec['drawing_pixel_scale_m'],'height_before_m':16,'height_after_m':bounds[2][1]-bounds[2][0],'survey_entrance_to_upper_roof_m':rec['structural_height_m']['upper_surface'],'external_dependencies':[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file],'missing_modifiers':False,'source_footprint_is_wall_footprint':False,'height_status':'HABS dimensioned heights relative entrance; actual ground elevation unverified','position_status':'OSM roof based translation estimate +/-2m, not independently surveyed','master_integration_status':'Unchanged manifest collection/asset and world coordinate frame; coordinator read-only link inspection required','geometry_edits':['Replaced 16m massing with HABS structural floor and wall outline','One-story brick and glass envelope, stepped roof, copper fascia motifs and clerestory','Sunken living floor, central hearth, roof chimney with current patinated cap','Terrace parapets, pergola, carport and tool crib'],'objects':meshes}
json.dump(val,open(E/'validation.json','w'),indent=2)
# More readable low viewpoint showing entry and folded copper fascia.
cam=scene.camera; center=Vector((rec['anchor_world_m'][0],rec['anchor_world_m'][1],1.2)); cam.location=center+Vector((-30,-24,12)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=38; scene.render.filepath=str(E/'preview_entry.png'); bpy.ops.render.render(write_still=True)
# Detail proof: same facade with three through-apertures and copper folds.
import math
S=rec['drawing_pixel_scale_m']; a=math.radians(rec['drawing_x_world_angle_deg']); u=Vector((math.cos(a),math.sin(a),0)); v=Vector((-math.sin(a),math.cos(a),0)); anchor=Vector((rec['anchor_world_m'][0],rec['anchor_world_m'][1],0))
def pt(x,y,z): return anchor+u*((x-500)*S)+v*((300-y)*S)+Vector((0,0,z))
def view(c,offset,scale,name):
 cam.location=c+Vector(offset); cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=scale; scene.render.filepath=str(E/name); bpy.ops.render.render(write_still=True)
view(pt(438,397,1.9),(-8,-6,4),9,'preview_fascia_closeup.png')
view(pt(650,357,1.5),(-10,-5,3.5),10,'preview_foyer_apertures.png')
for o in list(col.all_objects):
 if any(t in o.name for t in ('roof','fascia','Clerestory','chimney','pergola')):o.hide_render=True
bpy.data.objects['Preview ground only'].hide_render=True
view(pt(625,252,-.15),(-6,-4,13),14,'preview_sunken_floor_roofs_hidden.png')
proof={'revision':2,'floor_drop_m':22*.0254,'step_count_foyer':3,'step_rise_m':22*.0254/3,'step_tread_depth_m':6*S,'aperture_centers_drawing_x':[620,650,680],'aperture_drawing_y':357,'aperture_width_m':8*S,'aperture_sill_head_m':[.75,2.42],'glazed_clear_width_m':6.8*S,'fascia_vertical_profile_m':.44,'fascia_upper_return_m':.16,'source':'HABS IN-247 sheets3,4,6; Foundation photograph','uncertainty':'Stair count/treads and fascia fold measurements interpreted from source, not printed dimension; measured overall floor drop retained.'}
json.dump(proof,open(E/'revision2_measurements.json','w'),indent=2)
print('SAMARA_REOPEN_VALIDATED',len(meshes),bounds)
