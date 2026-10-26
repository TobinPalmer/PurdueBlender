import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'audit/walc_refine'
scene=bpy.data.scenes['Building_walc']
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1100
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.background_type='WORLD'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='WORLD'
scene.display.shading.curvature_ridge_factor=1.2
scene.display.shading.curvature_valley_factor=0.8
scene.display.shading.show_specular_highlight=True
scene.world=scene.world or bpy.data.worlds.new('WALC_Review')
scene.world.color=(0.68,0.72,0.78)
asset=bpy.data.collections['Asset_walc']
meshobjs=[o for o in asset.all_objects if o.type=='MESH']
points=[]
for o in meshobjs:
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
    points.extend(ev.matrix_world@Vector(v) for v in ev.bound_box)
mins=[min(p[i] for p in points) for i in range(3)]; maxs=[max(p[i] for p in points) for i in range(3)]
center=Vector(((mins[0]+maxs[0])/2,(mins[1]+maxs[1])/2,(mins[2]+maxs[2])/2))
span=max(maxs[0]-mins[0],maxs[1]-mins[1])
views={'southwest':(center+Vector((-0.85,-1.1,0.62))*(span*2.25)), 'southeast':(center+Vector((1.0,-0.7,0.58))*(span*2.25)), 'north':(center+Vector((0.15,1.0,0.45))*(span*2.25)), 'roof':(center+Vector((0.1,-0.08,2.4))*(span*2.25))}
cam_data=bpy.data.cameras.new('Independent_Review_Camera');cam=bpy.data.objects.new('Independent_Review_Camera',cam_data);scene.collection.objects.link(cam);scene.camera=cam
cam_data.type='ORTHO';cam_data.ortho_scale=span*1.36
for name,position in views.items():
    cam.location=position
    direction=center-cam.location
    cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(OUT/f'{name}.png')
    bpy.ops.render.render(write_still=True)
print({'bounds': [mins,maxs], 'center':list(center),'rendered':list(views)})
