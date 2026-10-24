"""Non-destructive side profile of one source-plan stair-symbol proxy."""
import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
BLEND=ROOT/'modular/buildings/knoy_hall.blend';OUT=ROOT/'audit/complete_knoy'
bpy.ops.wm.open_mainfile(filepath=str(BLEND));scene=bpy.context.scene
for o in scene.objects:o.hide_render=True
obj=bpy.data.objects['KNOY_Stair_L2_L3_Core_B'];obj.hide_render=False
obj.color=(.92,.46,.08,1)
mat=bpy.data.materials.new('R13_RenderOnly_Stair_Profile');mat.diffuse_color=obj.color;mat.use_nodes=True
bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bsdf.inputs['Base Color'].default_value=obj.color;bsdf.inputs['Roughness'].default_value=.8
obj.data.materials.clear();obj.data.materials.append(mat)
pts=[obj.matrix_world@Vector(c) for c in obj.bound_box]
x0=min(p.x for p in pts);x1=max(p.x for p in pts);y0=min(p.y for p in pts);y1=max(p.y for p in pts);z0=min(p.z for p in pts);z1=max(p.z for p in pts)
cx=(x0+x1)/2;cy=(y0+y1)/2;cz=(z0+z1)/2
# Small side-mounted datum marks, presentation-only and explicitly not slabs.
guide=bpy.data.materials.new('R13_RenderOnly_Stair_Datum');guide.diffuse_color=(.12,.62,.72,1)
for label,z in [('L2',z0),('L3',z1)]:
 mesh=bpy.data.meshes.new('R13_Datum_'+label);xx=cx+1.9;half=3.1;t=.025
 mesh.from_pydata([(xx-t,cy-half,z),(xx+t,cy-half,z),(xx+t,cy+half,z),(xx-t,cy+half,z)],[],[(0,1,2,3)])
 g=bpy.data.objects.new('R13_Datum_'+label,mesh);scene.collection.objects.link(g);g.data.materials.append(guide);g.hide_render=False
cd=bpy.data.cameras.new('R13_Stair_Profile_Camera');cam=bpy.data.objects.new('R13_Stair_Profile_Camera',cd);scene.collection.objects.link(cam)
target=Vector((cx,cy,cz));cam.location=target+Vector((14,-10,8));cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=8
scene.camera=cam;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=True;scene.display.shading.background_type='WORLD';scene.display.shading.background_color=(.95,.96,.97)
scene.render.resolution_x=1500;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';out=OUT/'knoy_core_b_l2_l3_stair_profile_r13.png';scene.render.filepath=str(out)
bpy.ops.render.render(write_still=True)
report={'asset_reopened':str(BLEND),'saved_by_renderer':False,'render':out.name,'source_plan':'Purdue 2018 Gateway Formation Study, page 24, Typical Plan Levels 2-4; stair core B masked location only.','dimensions_model_m':{'x':[x0,x1],'y':[y0,y1],'z':[z0,z1]},'geometry_status':'Two-floor interval proxy. Tread/riser count, landing sizes, enclosure, exact section dimensions and accessibility/egress are not given by the plan and remain estimated. Datums are render-only guides; model does not support connectivity to L1, basement, L5 or roof.'}
(OUT/'stair_profile_validation_r13.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
