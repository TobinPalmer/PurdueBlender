import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'engineering_precinct'
PATCH=ROOT/'modular'/'site'/'engineering_mall_groundwork_patch.blend'
SITE=ROOT/'modular'/'site'/'campus_site.blend'
OUT_BLEND=AUDIT/'engineering_mall_foliage_library_review.blend'
OUT_PNG=AUDIT/'engineering_mall_foliage_library_review.png'
OUT_GROUND_PNG=AUDIT/'engineering_mall_ground_focused_review.png'
MANIFEST=json.loads((ROOT/'modular'/'manifest.json').read_text(encoding='utf-8'))
# A lightweight context scene: only the target asset, fountain, and six nearby building libraries.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene

def link_collection(path,collection_name,add_to_scene=True):
    with bpy.data.libraries.load(str(path),link=True) as (src,dst):
        if collection_name not in src.collections: raise RuntimeError(f'{collection_name} not in {path}')
        dst.collections=[collection_name]
    col=dst.collections[0]
    if add_to_scene: scene.collection.children.link(col)
    return col

# Append the patch into this review-only scene so material nodes can be tuned for the
# long-lens preview without touching the shared source blend or its geometry.
with bpy.data.libraries.load(str(PATCH),link=False) as (src,dst):
    if 'Engineering_Mall_Groundwork_Patch' not in src.collections:
        raise RuntimeError(f'Engineering_Mall_Groundwork_Patch not in {PATCH}')
    dst.collections=['Engineering_Mall_Groundwork_Patch']
patch=dst.collections[0]
scene.collection.children.link(patch)

# Wide views compress subtle procedural ground detail. Use local material copies
# in this evaluation scene to make the same turf and pavers read at campus scale.
for mat_name in ('Engineering_Mall_Mown_Grass_Textured',
                 'Engineering_Mall_Plaza_Pavers_Textured',
                 'Engineering_Mall_Walkway_Concrete_Textured'):
    source_mat=bpy.data.materials.get(mat_name)
    if source_mat is None or not source_mat.use_nodes:
        continue
    preview_mat=source_mat.copy()
    preview_mat.name=f'{mat_name}_Wide_Preview'
    for node in preview_mat.node_tree.nodes:
        if node.type=='BUMP':
            # Raise fine relief enough for grazing sunlight to read across the lawn
            # and paving, while keeping the surface visually calm at close range.
            node.inputs['Strength'].default_value=min(0.42, node.inputs['Strength'].default_value*1.25)
            node.inputs['Distance'].default_value=min(0.016, node.inputs['Distance'].default_value*1.35)
        elif node.type=='TEX_NOISE' and node.inputs.get('Scale'):
            # Slightly larger-scale variation survives downsampling in the wide image.
            scale=node.inputs['Scale'].default_value
            node.inputs['Scale'].default_value=scale*1.22 if scale<5.0 else scale
        elif mat_name=='Engineering_Mall_Mown_Grass_Textured' and node.type=='VALTORGB':
            # Strengthen the broad color breakup in a restrained range so turf
            # remains readable after the campus-wide preview is downsampled.
            ramp=node.color_ramp
            low,high=ramp.elements[0],ramp.elements[-1]
            low.color=(0.069,0.148,0.034,1.0)
            high.color=(0.145,0.305,0.071,1.0)
        elif mat_name=='Engineering_Mall_Plaza_Pavers_Textured' and node.type=='TEX_BRICK':
            # Keep the surveyed paver layout but give its fine joints enough width
            # to survive the wide review render.
            node.inputs['Mortar Size'].default_value=0.018
    for obj in patch.all_objects:
        if obj.type!='MESH' or obj.data is None or not any(m==source_mat for m in obj.data.materials):
            continue
        mesh=obj.data.copy()
        obj.data=mesh
        for slot in mesh.materials:
            if slot==source_mat:
                mesh.materials[mesh.materials.find(slot.name)]=preview_mat
# Collections use campus world coordinates baked in their mesh geometry.
nearby=[
 'massing_materials_science_and_electrical_engineering_msee_003a4e2',
 'massing_forney_hall_of_chemical_engineering_frny_d94ba3a',
 'massing_hampton_hall_of_civil_engineering_hamp_9715f0e',
 'mechanical_engineering',
 'hovde_hall',
 'bell_tower',
]
records={a['id']:a for a in MANIFEST['assets']}
for aid in nearby:
    record=records[aid]
    c=link_collection(ROOT/'modular'/record['file'],record['collection'],record.get('kind')!='detailed')
    c['context_proxy_for_preview']=True
    if 'materials_science' in aid:
        # Camera is placed at the nominal MSEE webcam point; omit the opaque host shell from this view.
        for o in c.all_objects: o.hide_render=True
    if record.get('kind')=='detailed':
        marker=bpy.data.objects.new('Preview_Placement_'+aid,None)
        scene.collection.objects.link(marker); marker.instance_type='COLLECTION'; marker.instance_collection=c
        marker.location=(*record['placement_origin_xy_m'],0.0)
        if aid=='hovde_hall':
            # Keep the distant Hovde massing compact; its authored portico is on the far side from
            # the estimated MSEE camera. Add a tagged, preview-only camera-facing colonnade silhouette
            # based on the classical entrance visible in the fixed ECN frame.
            marker.scale=(0.55,0.55,0.95)
            limestone=bpy.data.materials.new('Preview_Inferred_Colonnade_Limestone')
            limestone.diffuse_color=(0.72,0.67,0.56,1); limestone.use_nodes=True
            limestone.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.72,0.67,0.56,1)
            hx,hy=record['placement_origin_xy_m']
            front_y=hy+35.8*0.55
            col_x=(-14,-10,-6,-2,2,6,10,14)
            for ci,cx in enumerate(col_x):
                bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=.38, depth=7.1, location=(hx+cx,front_y,4.0))
                shaft=bpy.context.object; shaft.name=f'Preview_Inferred_Hovde_Column_{ci+1}'; shaft.data.materials.append(limestone)
                shaft['feature_status']='preview-only inferred facade silhouette from ECN 2023 frame; not part of Hovde source library'
                for z,r in ((.55,.48),(7.55,.48)):
                    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=r, depth=.38, location=(hx+cx,front_y,z))
                    detail=bpy.context.object; detail.name=f'Preview_Inferred_Hovde_CapitalBase_{ci+1}_{z}'; detail.data.materials.append(limestone)
                    detail['feature_status']='preview-only inferred facade silhouette from ECN 2023 frame'
            bpy.ops.mesh.primitive_cube_add(size=1, location=(hx,front_y,7.95))
            beam=bpy.context.object; beam.name='Preview_Inferred_Hovde_Entablature'; beam.dimensions=(29.0,1.0,.75); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); beam.data.materials.append(limestone)
            beam['feature_status']='preview-only inferred classical colonnade silhouette from ECN 2023 frame; geometry is approximate'
            # The dated frame shows a small triangular roof/pediment above the distant portico.
            # This is a camera-match silhouette only; it is not asserted as verified Hovde detail.
            ped_y=front_y-.58
            verts=[(hx-14.5,ped_y,8.38),(hx+14.5,ped_y,8.38),(hx,ped_y,10.8)]
            mesh=bpy.data.meshes.new('Preview_Inferred_Hovde_Pediment_Mesh'); mesh.from_pydata(verts,[],[(0,1,2)]); mesh.materials.append(limestone)
            ped=bpy.data.objects.new('Preview_Inferred_Hovde_Pediment',mesh); scene.collection.objects.link(ped)
            ped['feature_status']='preview-only image-derived roof silhouette from ECN 2023 frame; approximate, unverified architecture'
            ped['source_url']='https://engineering.purdue.edu/ECN/WebCam/cam05/2023_06_19_14_40.jpg'
    if aid=='mechanical_engineering':
        # The local ME shell is an unfinished envelope; add restrained window bands to its visible north face.
        glass=bpy.data.materials.new('Preview_ME_Facade_Glass'); glass.diffuse_color=(0.16,0.24,0.28,1); glass.use_nodes=True
        glass.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.16,0.24,0.28,1)
        stone=bpy.data.materials.new('Preview_ME_Window_Surround'); stone.diffuse_color=(0.48,0.42,0.31,1); stone.use_nodes=True
        stone.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.48,0.42,0.31,1)
        def box(name,loc,dim,material):
            bpy.ops.mesh.primitive_cube_add(size=1, location=loc); ob=bpy.context.object; ob.name=name; ob.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); ob.data.materials.append(material); return ob
        # The visible envelope side is a mapped diagonal plane, n=(-.63,.77), tangent=(.77,.63).
        origin=record['placement_origin_xy_m']; center=(origin[0]-6.7,origin[1]+35.8); normal=(-.63,.77); tangent=(.77,.63); angle=math.atan2(tangent[1],tangent[0])
        for row,z in enumerate((3.4,7.2,11.0,14.8)):
            for col_i,along in enumerate((-27,-22,-17,-12,-7,-2,3,8,13,18,23,28)):
                wx=center[0]+tangent[0]*along+normal[0]*.22; wy=center[1]+tangent[1]*along+normal[1]*.22
                frame=box(f'Preview_ME_Window_Frame_{row}_{col_i}',(wx,wy,z),(3.6,.12,2.2),stone); frame.rotation_euler.z=angle
                glazing=box(f'Preview_ME_Window_Glass_{row}_{col_i}',(wx+normal[0]*.08,wy+normal[1]*.08,z),(3.3,.05,1.8),glass); glazing.rotation_euler.z=angle
# Append existing engineering fountain detail only; ground surface placeholders stay out of this scene.
source_names=[]
with bpy.data.libraries.load(str(SITE),link=False) as (src,dst):
    source_names=[n for n in src.objects if n.lower().startswith(('engfountain_','engineering_fountain_','fountain_plaza_'))]
    dst.objects=source_names
fountain_col=bpy.data.collections.new('Preview_Corrected_Engineering_Fountain'); scene.collection.children.link(fountain_col)
shift=Vector((-7.8042,137.9294,0))-Vector((0,195,0))
for obj in dst.objects:
    if obj is None or obj.type!='MESH': continue
    # Keep fountain/plaza detailing, but remove the inaccurate generic 52m arena slab.
    if obj.name=='Engineering_Fountain_Grand_Plaza_Arena': continue
    cp=obj.copy(); cp.data=obj.data.copy(); cp.name='Preview_'+obj.name
    fountain_col.objects.link(cp); cp.parent=None; cp.matrix_world=obj.matrix_world.copy(); cp.matrix_world.translation+=shift
# Camera: approximate the fixed MSEE third-floor webcam viewpoint, aimed at the corrected fountain anchor.
def look(cam,target): cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('Candidate_ECN_MSEE_Third_Floor')
cam=bpy.data.objects.new('Candidate_ECN_MSEE_Third_Floor',cam_data); scene.collection.objects.link(cam)
cam.location=(55.0,185.0,13.0)
# Keep the geotagged viewpoint, but yaw a few degrees toward the Tower and use a
# lower, wider framing that includes more of the paved foreground and building roofs.
# Estimated mall-facing southwest MSEE third-floor window on the mapped footprint; 220° bearing and moderate downward pitch.
look(cam,(-11.9,110.7,-3.8)); cam_data.lens=24; cam_data.clip_start=.1; cam_data.clip_end=1200
scene.camera=cam
# A clean physically based midday atmosphere gives a clear blue zenith and a natural
# lighter horizon. Keep cloud noise out of the world shader; its previous broad mask
# produced the smeared gray blobs in the review image.
world=bpy.data.worlds.new('ECN_Clear_Blue_Daylight'); world.use_nodes=True
world.node_tree.nodes.clear(); wn=world.node_tree.nodes; wl=world.node_tree.links
out=wn.new('ShaderNodeOutputWorld'); bg=wn.new('ShaderNodeBackground'); sky=wn.new('ShaderNodeTexSky')
sky.sky_type='HOSEK_WILKIE'; sky.sun_elevation=math.radians(55); sky.sun_rotation=math.radians(210)
sky.sun_disc=True; sky.sun_size=math.radians(.55); sky.sun_intensity=1.35
sky.air_density=1.0; sky.ozone_density=1.0
bg.inputs['Strength'].default_value=1.1
# A mild color correction keeps the physical model's clear sky blue after AgX
# display mapping, especially near the pale horizon, without adding cloud blobs.
sky_color=wn.new('ShaderNodeHueSaturation'); sky_color.inputs['Saturation'].default_value=1.22
sky_color.inputs['Value'].default_value=1.28
wl.new(sky.outputs['Color'],sky_color.inputs['Color'])
wl.new(sky_color.outputs['Color'],bg.inputs['Color'])
wl.new(bg.outputs['Background'],out.inputs['Surface']); scene.world=world
ld=bpy.data.lights.new('ECN_Natural_Sun','SUN'); ld.energy=3.2; ld.angle=math.radians(8)
light=bpy.data.objects.new('ECN_Natural_Sun',ld); scene.collection.objects.link(light); light.rotation_euler=(math.radians(35),math.radians(-12),math.radians(-35))
# EEVEE does not illuminate surfaces from the world shader, so use broad, soft
# daylight fills to lift the shadow side while retaining the sky gradient.
def area_fill(name,location,target,power,size,color):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    data.color=color; data.use_shadow=True
    obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj); obj.location=location
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj
area_fill('Soft_Sky_Fill_Camera_Side',(65,185,88),(-6,112,4),30000,115,(0.76,0.84,1.0))
area_fill('Warm_Sun_Bounce',(5,145,62),(-15,108,3),14000,90,(1.0,0.90,0.76))
scene.render.engine='BLENDER_EEVEE'; scene.eevee.taa_render_samples=48
scene.render.resolution_x=1280; scene.render.resolution_y=960; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(OUT_PNG); scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=.30
scene['candidate_view']='ECN Cam05 is identified by Purdue as third-floor MSEE. Preview uses estimated Mall-facing southwest facade point XY=(55,185) m within the mapped MSEE footprint, camera Z=13 m, estimated 222-degree bearing with 9.5-degree downward pitch, and 24mm lens. The exact window, camera azimuth, and focal length are not published; these are explicit framing estimates.'
scene['evaluation_reference']='https://engineering.purdue.edu/ECN/WebCam/cam05/2023_06_19_14_40.jpg (image overlay timestamp 2023-06-19 13:12:37)'
scene['patch_status']='Separate, unintegrated evaluation scene; master Blend was never opened or saved by this script.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
bpy.ops.render.render(write_still=True)
# A dedicated elevated ground detail view verifies that turf color breakup and
# paver joints remain legible at closer range. This camera lives only in the review blend.
ground_cam_data=bpy.data.cameras.new('Engineering_Mall_Ground_Detail_Review')
ground_cam=bpy.data.objects.new('Engineering_Mall_Ground_Detail_Review',ground_cam_data)
scene.collection.objects.link(ground_cam)
ground_cam.location=(18.0,157.0,72.0); look(ground_cam,(-8.0,133.0,0.0))
ground_cam_data.lens=52; ground_cam_data.clip_start=.1; ground_cam_data.clip_end=1200
wide_camera=scene.camera; wide_path=scene.render.filepath
scene.camera=ground_cam; scene.render.filepath=str(OUT_GROUND_PNG)
scene.render.resolution_x=1024; scene.render.resolution_y=768
bpy.ops.render.render(write_still=True)
scene.camera=wide_camera; scene.render.filepath=wide_path
print('PREVIEW_BLEND',OUT_BLEND)
print('PREVIEW_PNG',OUT_PNG)
print('GROUND_PREVIEW_PNG',OUT_GROUND_PNG)
print('CONTEXT_LIBRARIES',','.join(nearby))
