from pathlib import Path
import bpy
from mathutils import Vector

root=Path(__file__).resolve().parents[2]
out=root/'audit'/'meredith_hall_south'/'preview_exterior.png'
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1100; scene.render.resolution_y=760; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=-0.65
scene.world.use_nodes=True
bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
bg.inputs['Color'].default_value=(0.018,0.026,0.038,1)
bg.inputs['Strength'].default_value=0.35
scene.render.filepath=str(out)
coll=bpy.data.collections.get('Asset_massing_meredith_hall_south_ffbc444')
objs=[o for o in coll.objects if o.type=='MESH']
corners=[o.matrix_world @ Vector(c) for o in objs if len(o.data.vertices) for c in o.bound_box]
mins=Vector((min(p.x for p in corners),min(p.y for p in corners),min(p.z for p in corners)))
maxs=Vector((max(p.x for p in corners),max(p.y for p in corners),max(p.z for p in corners)))
target=(mins+maxs)*0.5
cam_data=bpy.data.cameras.new('MRDS_PreviewCamera'); cam=bpy.data.objects.new('MRDS_PreviewCamera',cam_data); scene.collection.objects.link(cam)
cam.location=target+Vector((110,-185,115)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam_data.type='ORTHO'; cam_data.ortho_scale=184; scene.camera=cam
cam_data.clip_end=5000
def area(name,loc,power,size):
 d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size
 o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc; o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
area('MRDS_Key_Sunlit_Softbox',target+Vector((35,-65,85)),6500,70)
area('MRDS_Fill',target+Vector((-65,30,42)),1800,90)
from bpy_extras.object_utils import world_to_camera_view
bpy.context.view_layer.update()
print('MRDS_CAMERA',tuple(cam.location),tuple(target),tuple(world_to_camera_view(scene,cam,target)))
plate_render_states={}
for o in coll.objects:
    if o.name.startswith('MRDS_Interior_Floor_Plate_'):
        plate_render_states[o.name]=o.hide_render
        o.hide_render=True
bpy.ops.render.render(write_still=True)
cam.location=target+Vector((-110,185,115)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.context.view_layer.update()
scene.render.filepath=str(root/'audit'/'meredith_hall_south'/'preview_exterior_reverse.png')
bpy.ops.render.render(write_still=True)
for name,hidden in plate_render_states.items():
    obj=bpy.data.objects.get(name)
    if obj: obj.hide_render=hidden

# Produce an isolated level-3 schematic plan/cutaway. The saved library keeps
# the complete exterior and all floors; only this evidence render temporarily
# hides the shell and filters the multi-level interior meshes by elevation.
saved_hidden={o.name:o.hide_render for o in bpy.data.objects}
for o in bpy.data.objects:
    o.hide_render=True
for o in scene.objects:
    if o.type=='LIGHT': o.hide_render=False
interior_names={
    'MRDS_Interior_Corridor_Floor_L03',
    'MRDS_Interior_Room_Partitions_L03',
    'MRDS_Interior_Double_Room_Beds_L03',
    'MRDS_Interior_Desks_L03',
    'MRDS_Schematic_Interior_Corridor_Floor_Strips',
    'MRDS_Schematic_Interior_Bedroom_Partitions',
    'MRDS_Schematic_Double_Room_Beds',
    'MRDS_Schematic_Desks',
}
for name in interior_names:
    o=bpy.data.objects.get(name)
    if o is None: continue
    if name.startswith('MRDS_Interior_') and name.endswith('L03'):
        o.hide_render=False
        continue
    if o.type!='MESH': continue
    keep=[]
    for poly in o.data.polygons:
        z=sum((o.matrix_world @ o.data.vertices[i].co for i in poly.vertices),Vector((0,0,0)))/len(poly.vertices)
        # Level 3 runs from 6.60 m to 9.90 m. Keep the middle-floor plates,
        # partitions, beds and desks and omit identical geometry on other floors.
        if 6.45 <= z.z <= 9.45:
            keep.append(poly)
    if not keep: continue
    verts=[]; faces=[]; index_map={}
    for poly in keep:
        face=[]
        for i in poly.vertices:
            if i not in index_map:
                index_map[i]=len(verts)
                verts.append(tuple(o.data.vertices[i].co))
            face.append(index_map[i])
        faces.append(face)
    mesh=bpy.data.meshes.new(name+'_L03_TemporaryMesh')
    mesh.from_pydata(verts,[],faces); mesh.update()
    for material in o.data.materials: mesh.materials.append(material)
    temp=bpy.data.objects.new(name+'_L03_Temporary',mesh)
    scene.collection.objects.link(temp)
    temp.hide_render=False
floor=bpy.data.objects.get('MRDS_Interior_Floor_Plate_L02')
if floor:
    # Omit the opaque plate so the rooms, double beds, desks and corridor are
    # legible from above; the saved asset still contains the full plate.
    floor.hide_render=True
cam.location=Vector(((mins.x+maxs.x)/2,(mins.y+maxs.y)/2,105))
cam.rotation_euler=(0,0,0)
cam_data.type='ORTHO'; cam_data.ortho_scale=150
cam_data.lens=50
scene.render.resolution_x=1600; scene.render.resolution_y=1000
scene.render.filepath=str(root/'audit'/'meredith_hall_south'/'preview_interior_level3_plan.png')
scene.render.resolution_percentage=100
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(0.09,0.105,0.12,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=0.65
bpy.context.view_layer.update()
bpy.ops.render.render(write_still=True)
for o in bpy.data.objects:
    if o.name.endswith('_L03_Temporary'):
        mesh=o.data; bpy.data.objects.remove(o,do_unlink=True)
        if mesh.users==0: bpy.data.meshes.remove(mesh)
for name,hidden in saved_hidden.items():
    o=bpy.data.objects.get(name)
    if o: o.hide_render=hidden
