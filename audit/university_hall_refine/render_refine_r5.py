"""Render consistent R5 exterior views and a focused gallery cutaway."""
import bpy, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
out=root/'audit'/'university_hall_refine'
scene=bpy.context.scene
COL=bpy.data.collections['Asset_university_hall']
scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=16
scene.render.resolution_x=1000;scene.render.resolution_y=760;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
world=bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new('UH_R5_ReviewWorld')
scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.36,0.43,0.52,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.22
hidden_lights=[]
for obj in bpy.data.objects:
    if obj.type=='LIGHT':hidden_lights.append((obj,obj.hide_render));obj.hide_render=True

mat=bpy.data.materials.new('UH_R5_TemporaryGround');mat.diffuse_color=(0.20,0.23,0.21,1);mat.use_nodes=True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.20,0.23,0.21,1)
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.92
bpy.ops.mesh.primitive_plane_add(size=180,location=(0,0,-0.12));ground=bpy.context.object;ground.name='UH_R5_TemporaryGround';ground.data.materials.append(mat)
bpy.ops.object.light_add(type='SUN',location=(32,-44,55));sun=bpy.context.object;sun.name='UH_R5_TemporarySun';sun.data.energy=2.7
sun.rotation_euler=(math.radians(24),math.radians(-28),math.radians(-38))
bpy.ops.object.light_add(type='AREA',location=(-32,-18,38));fill=bpy.context.object;fill.name='UH_R5_TemporaryFill';fill.data.energy=760;fill.data.shape='DISK';fill.data.size=28
fill.rotation_euler=(Vector((-7.5,0,10))-fill.location).to_track_quat('-Z','Y').to_euler()

def temp_box(name,loc,dims,material):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
    return o

def render(name,location,target,scale,cutaway=False):
    changed=[];temporary=[]
    if cutaway:
        # Remove the envelope and broad floor plates from the explanatory view;
        # the actual saved asset remains fully enclosed and fully floored.
        hide_prefixes=('UNIV_Wall_','UNIV_R2_UNIV_Wall_','UNIV_Win_','UNIV_R2_UNIV_Win_','UNIV_R5_Window',
            'UNIV_WinSill','UNIV_R2_UNIV_WinSill','UNIV_WinHood','UNIV_R2_UNIV_WinHood',
            'UNIV_WinKeystone','UNIV_R2_UNIV_WinKeystone','UNIV_R2_Mansard','UNIV_R2_Dormer',
            'UNIV_R4_Mansard','UNIV_R4_Dormer','UNIV_R4_Belfry','UNIV_R4_Lantern','UNIV_R4_Weathervane',
            'UNIV_R4_Finial','UNIV_R4_Portico','UNIV_Tower_','UNIV_Belfry_','UNIV_Cupola_',
            'UNIV_Clock_','UNIV_Historic_Bronze','UNIV_Bell_Yoke_','UNIV_R4_ArchedWindowHeadMoulds',
            'UNIV_R4_EaveConsole_','UNIV_R4_North_Window','UNIV_R4_South_Window','UNIV_R4_East_Window','UNIV_R4_West_Window',
            'UNIV_WaterTable_','UNIV_Beltcourse_','UNIV_Quoin','UNIV_Portico','UNIV_East_Step',
            'UNIV_R4_GalleryFloor_')
        for o in bpy.data.objects:
            if o.hide_render:continue
            if o.name.startswith(hide_prefixes) or o.name=='UNIV_Interior_Ceiling_Second':
                changed.append((o,o.hide_render));o.hide_render=True
        # Isolate the documented gallery/stair relationship from unrelated
        # furniture and shell detail; the full model is retained outside this view.
        keep_prefixes=('UNIV_R4_Gallery_LibraryFeatureWall','UNIV_R4_Gallery_BookBay_',
            'UNIV_R4_Gallery_Book_','UNIV_R4_Gallery_InterpretivePlaque',
            'UNIV_R4_FirstGallery_Railing','UNIV_R4_AcademyOverlook_Railing',
            'UNIV_R4_Overlook_','UNIV_R4_StairFlight','UNIV_R4_StairLanding',
            'UNIV_R4_StairRail','UNIV_R4_StairHandrail','UNIV_R5_ReclaimedDisplayColumn_','UH_R5_TemporaryGround')
        for o in bpy.data.objects:
            if o.hide_render:continue
            if not o.name.startswith(keep_prefixes):
                changed.append((o,o.hide_render));o.hide_render=True
        print('R5_CUTAWAY_VISIBLE',[(o.name,o.type) for o in bpy.data.objects if not o.hide_render and o.type not in ('CAMERA','LIGHT')])
        floor=bpy.data.materials.get('Univ_Parquet_Wood')
        # Framing at the central two-story opening makes both guard edges legible.
        cx=-7.515;z_levels=(4.20,8.40);hx=3.8;hy=6.0;band=0.62
        for level,z in enumerate(z_levels):
            for side in (-1,1):
                temporary.append(temp_box(f'UH_R5_CutawayRingX_{level}_{side}',(cx+side*(hx+band/2),0,z),(band,2*(hy+band),0.12),floor))
                temporary.append(temp_box(f'UH_R5_CutawayRingY_{level}_{side}',(cx,side*(hy+band/2),z),(2*hx,band,0.12),floor))
        # Short floor bridges show the stairs meeting the gallery at both
        # landings; exact circulation dimensions remain a visual reconstruction.
        temporary.append(temp_box('UH_R5_CutawayGroundLandingBridge',(-11.40,-13.25,4.20),(3.25,2.05,0.12),floor))
        temporary.append(temp_box('UH_R5_CutawayUpperLandingBridge',(-11.25,-19.55,8.40),(2.55,1.80,0.12),floor))
    cd=bpy.data.cameras.new('UH_R5_TempCameraData');cam=bpy.data.objects.new('UH_R5_TempCamera',cd);scene.collection.objects.link(cam)
    cam.location=location;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cd.type='ORTHO';cd.ortho_scale=scale;scene.camera=cam
    scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(cd)
    for o in temporary:
        mesh=o.data;bpy.data.objects.remove(o,do_unlink=True)
        if mesh.users==0:bpy.data.meshes.remove(mesh)
    for o,val in changed:o.hide_render=val

render('ground_oblique_r5',(28,-62,23),(-7.5,0,11),66)
render('east_elevation_r5',(72,0,18),(-7.5,0,12.2),64)
render('entry_ground_r5',(27,-44,9),(2.5,0,4.3),25)
render('interior_cutaway_r5',(22,-34,25),(-7.5,-1.0,5.9),38,True)

for obj in (ground,sun,fill):
    data=obj.data;bpy.data.objects.remove(obj,do_unlink=True)
    if data.users==0:(bpy.data.meshes if isinstance(data,bpy.types.Mesh) else bpy.data.lights).remove(data)
for obj,val in hidden_lights:obj.hide_render=val
print('R5 views rendered to',out)
