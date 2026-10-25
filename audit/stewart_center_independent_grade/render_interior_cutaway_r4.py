import bpy
from pathlib import Path
from mathutils import Vector

asset=bpy.data.collections['Asset_stewart_center']
groups=[('Loeb_','Loeb Theater'),('HSSE_','HSSE Library'),('Ringel_','Ringel Gallery')]
cut=bpy.data.scenes.new('Stewart_Interior_Cutaway_R4')
cut.render.engine='BLENDER_EEVEE'; cut.render.resolution_x=1800; cut.render.resolution_y=1250
cut.render.resolution_percentage=100; cut.render.image_settings.file_format='PNG'; cut.render.film_transparent=False
cut.view_settings.view_transform='AgX'; cut.view_settings.look='AgX - Medium High Contrast'
cut.world=bpy.data.worlds.new('Stewart_cutaway_review_world'); cut.world.use_nodes=True
cut.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.12,.15,.2,1)
cut.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.62

# Link only the three existing room/program modules into this temporary scene.
# The exterior shell and roof are deliberately omitted for a clean cutaway view.
pts_by_group=[]
for prefix,label in groups:
    pts=[]
    for obj in asset.all_objects:
        if obj is None or not obj.name.startswith(prefix) or 'Ceiling' in obj.name:
            continue
        cut.collection.objects.link(obj)
        if obj.type in {'MESH','CURVE','FONT'}:
            pts.extend(obj.matrix_world@Vector(c) for c in obj.bound_box)
    if not pts: raise RuntimeError(f'No interior objects found for {label}')
    pts_by_group.append((label,[[min(p[i] for p in pts) for i in range(3)],
                                [max(p[i] for p in pts) for i in range(3)]]))

bounds=[b for _,b in pts_by_group]
center=Vector(((min(b[0][0] for b in bounds)+max(b[1][0] for b in bounds))/2,
               (min(b[0][1] for b in bounds)+max(b[1][1] for b in bounds))/2,4.0))
lightdata=bpy.data.lights.new('Stewart_cutaway_key','AREA'); lightdata.energy=20000; lightdata.shape='DISK'; lightdata.size=75
light=bpy.data.objects.new('Stewart_cutaway_key',lightdata); cut.collection.objects.link(light)
light.location=center+Vector((-20,-55,85)); light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
camera_data=bpy.data.cameras.new('Stewart_cutaway_camera'); camera=bpy.data.objects.new('Stewart_cutaway_camera',camera_data)
cut.collection.objects.link(camera); camera.location=center+Vector((-78,-94,62))
camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
camera_data.type='ORTHO'; camera_data.ortho_scale=128; cut.camera=camera

labelmat=bpy.data.materials.new('Stewart_cutaway_label_R4'); labelmat.diffuse_color=(.95,.91,.79,1); labelmat.use_nodes=True
bs=labelmat.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(.95,.91,.79,1)
if 'Emission Color' in bs.inputs: bs.inputs['Emission Color'].default_value=(.95,.91,.79,1)
if 'Emission Strength' in bs.inputs: bs.inputs['Emission Strength'].default_value=2.5
legend=[('Stewart Center interiors — cutaway',2.1),
        ('Loeb Theater  |  auditorium seating',1.55),
        ('HSSE Library  |  shelving and study area',1.55),
        ('Ringel Gallery  |  open gallery space',1.55),
        ('Internal offsets are approximate; floor maps have no scale or north arrow.',1.2)]
for i,(body,size) in enumerate(legend):
    data=bpy.data.curves.new(f'Cutaway legend {i}','FONT'); data.body=body
    data.size=size; data.align_x='LEFT'; data.align_y='CENTER'
    obj=bpy.data.objects.new(f'Cutaway legend {i}',data); cut.collection.objects.link(obj)
    obj.parent=camera; obj.location=(-60,39-i*4.0,-25); obj.rotation_euler=(0,0,0); data.materials.append(labelmat)

out=Path(__file__).resolve().parent/'interior_modules_cutaway_r4.png'
cut.render.filepath=str(out)
bpy.ops.render.render(write_still=True,scene=cut.name)
print(f'Rendered {out}; modules retain their current approximate offsets because the 2024 map is unscaled and lacks a north arrow.')
