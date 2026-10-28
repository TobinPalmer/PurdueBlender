import bpy, os
from mathutils import Vector

folder=os.path.dirname(__file__)
obj=bpy.data.objects.get('Shoemaker Cooperative')
if obj is None: raise RuntimeError('Shoemaker asset object not found')
src=obj.data
mesh=bpy.data.meshes.new('Shoemaker_review_cutaway_mesh')
faces=[]; material_indices=[]
for poly in src.polygons:
    # Roof and floor plate materials are hidden only for this evidence render,
    # not in the asset, to expose the wall/room diagram from above.
    if poly.material_index in (3,7): continue
    faces.append(tuple(poly.vertices)); material_indices.append(poly.material_index)
mesh.from_pydata([v.co[:] for v in src.vertices],[],faces)
for mat in src.materials: mesh.materials.append(mat)
mesh.update()
for p,mi in zip(mesh.polygons,material_indices): p.material_index=mi
obj.data=mesh
scene=bpy.context.scene
for name in ('Shoemaker_Cutaway_Camera','Shoemaker_Cutaway_Light'):
    old=bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old,do_unlink=True)
world_pts=[obj.matrix_world@v.co for v in mesh.vertices]
cx=sum(p.x for p in world_pts)/len(world_pts); cy=sum(p.y for p in world_pts)/len(world_pts)
camdata=bpy.data.cameras.new('Shoemaker_Cutaway_Camera'); cam=bpy.data.objects.new('Shoemaker_Cutaway_Camera',camdata); scene.collection.objects.link(cam)
cam.location=(cx,cy,45); target=Vector((cx,cy,0)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); camdata.type='ORTHO'; camdata.ortho_scale=31; scene.camera=cam
ld=bpy.data.lights.new('Shoemaker_Cutaway_Light','AREA'); lo=bpy.data.objects.new('Shoemaker_Cutaway_Light',ld); scene.collection.objects.link(lo); lo.location=(cx-8,cy-8,32); ld.energy=5500; ld.shape='DISK'; ld.size=26; lo.rotation_euler=(target-lo.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1200; scene.render.resolution_y=1000; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(folder,'interior_cutaway_plan.png'); scene.view_settings.view_transform='AgX'; scene.view_settings.exposure=0.0; scene.world.color=(0.12,0.14,0.16)
bpy.ops.render.render(write_still=True)
print('INTERIOR_PLAN_RENDER='+scene.render.filepath)
