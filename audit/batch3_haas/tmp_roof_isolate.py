import bpy
from mathutils import Vector
S=bpy.context.scene; names={'HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof'}
for o in bpy.data.objects:o.hide_render=o.name not in names
# all area/point illumination excluded by hiding lights; emission-only patch exposes whether the shading is from the material.
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
camd=bpy.data.cameras.new('Roof isolation cam');cam=bpy.data.objects.new('Roof isolation cam',camd);S.collection.objects.link(cam);S.camera=cam;camd.type='ORTHO';cam.location=(55,-55,38);cam.rotation_euler=(Vector((-6,0,6))-cam.location).to_track_quat('-Z','Y').to_euler();camd.ortho_scale=82
S.render.resolution_x=1000;S.render.resolution_y=800;S.cycles.samples=2;S.render.filepath='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/roof_isolated_emission.png';bpy.ops.render.render(write_still=True)
