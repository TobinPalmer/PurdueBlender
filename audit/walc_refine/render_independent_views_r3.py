import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'audit/walc_refine'
scene=bpy.data.scenes['Building_walc']
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO'
scene.display.shading.studio_light='paint.sl'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.background_type='WORLD'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='WORLD'
scene.display.shading.curvature_ridge_factor=1.35
scene.display.shading.curvature_valley_factor=0.9
scene.display.shading.show_specular_highlight=True
scene.world=scene.world or bpy.data.worlds.new('WALC_R3_Review')
scene.world.color=(0.78,0.82,0.86)
asset=bpy.data.collections['Asset_walc']
meshobjs=[o for o in asset.all_objects if o.type=='MESH']
points=[]
deps=bpy.context.evaluated_depsgraph_get()
for o in meshobjs:
    ev=o.evaluated_get(deps)
    points.extend(ev.matrix_world@Vector(v) for v in ev.bound_box)
mins=[min(p[i] for p in points) for i in range(3)]; maxs=[max(p[i] for p in points) for i in range(3)]
center=Vector(((mins[0]+maxs[0])/2,(mins[1]+maxs[1])/2,(mins[2]+maxs[2])/2))
span=max(maxs[0]-mins[0],maxs[1]-mins[1])
views={'southwest':(-0.85,-1.1,0.48),'southeast':(1.0,-0.7,0.48),'north':(0.15,1.0,0.38)}
camera_data=bpy.data.cameras.new('WALC_R3_Review_Camera'); camera=bpy.data.objects.new('WALC_R3_Review_Camera',camera_data)
scene.collection.objects.link(camera); scene.camera=camera; camera_data.type='ORTHO'; camera_data.ortho_scale=span*1.37
for name,d in views.items():
    camera.location=center+Vector(d)*(span*2.15)
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(OUT/f'{name}_r3_daylight.png')
    bpy.ops.render.render(write_still=True)
print({'bounds': [mins,maxs], 'camera_center':list(center),'rendered':list(views)})
