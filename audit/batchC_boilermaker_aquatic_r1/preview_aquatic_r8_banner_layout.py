import bpy
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap');ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend';AUD=ROOT/'audit/batchC_boilermaker_aquatic_r1'
bpy.ops.wm.open_mainfile(filepath=str(ASSET));scene=bpy.context.scene
# Render-only layout test. Do not save these temporary adjustments to the asset.
for i,(y,x) in enumerate(zip((-18.0,-10.0,-2.0,6.0,14.0,22.0),(22.60,22.80,23.00,23.20,23.40,23.60)),1):
    p=bpy.data.objects[f'AQUA R8 | wall-mounted Purdue banner panel {i}'];p.location.x=x;p.location.y=y;p.location.z=7.75;p.dimensions.z=3.8
    for o in bpy.data.objects:
        if o.name.startswith(f'AQUA R8 | PURDUE banner glyph {i}'):
            o.location.x=x-.12;o.location.y=y;o.location.z=7.75;o.data.body='EUDRUP'[i-1]
    for s in bpy.data.objects:
        if s.name.startswith(f'AQUA R8 | banner wall standoff {i}'):
            dy=s.location.y-( -15.0 + (i-1)*6.0 );s.location.x=x+.37;s.location.y=y+dy;s.location.z=6.12 if s.location.z<8 else 9.38
cam=bpy.data.objects['AQUA R8 | bleacher side detail camera'];cam.location=(-20,1,7.5);cam.rotation_euler=(Vector((24,1,6.8))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=27
ctx=bpy.data.collections['AQUA_R5_Context | approximate site dressing'];roof=bpy.data.collections['AQUA_Roof'];ctx.hide_render=True;roof.hide_render=True
scene.render.engine='BLENDER_EEVEE';scene.render.image_settings.file_format='PNG';scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=85;scene.camera=cam;scene.render.filepath=str(AUD/'aquatic_r8_banner_layout_wide_test.png');bpy.ops.render.render(write_still=True)
depsgraph=bpy.context.evaluated_depsgraph_get()
print('glyph-projections',[(o.name,tuple(round(v,3) for v in world_to_camera_view(scene,cam,o.matrix_world.translation))) for o in bpy.data.objects if o.name.startswith('AQUA R8 | PURDUE banner glyph')])
for o in bpy.data.objects:
    if o.name.startswith('AQUA R8 | wall-mounted Purdue banner panel'):
        v=o.matrix_world.translation-cam.location;hit,loc,norm,idx,hitobj,mat=scene.ray_cast(depsgraph,cam.location,v.normalized(),distance=v.length)
        print('banner-ray',o.name,hit,hitobj.name if hitobj else None,tuple(round(a,2) for a in loc) if hit else None)
print('Render-only R8 banner/aisle layout test complete; blend file was not saved.')
