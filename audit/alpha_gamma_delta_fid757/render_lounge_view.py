import bpy, os, bmesh
from mathutils import Vector

here=os.path.dirname(__file__)
bpy.ops.wm.open_mainfile(filepath=os.path.join(here,'candidate_alpha_gamma_delta.blend'))
obj=bpy.data.objects.get('House_301841608'); assert obj
mesh0=obj.data
xs=[v.co.x for v in mesh0.vertices]; ys=[v.co.y for v in mesh0.vertices]
mx=(min(xs)+max(xs))/2; my=(min(ys)+max(ys))/2
focus=Vector((mx-7.0,my-6.0,0.9))

# Preview only: hide the shell, upper floor slabs, and roof so the reference-based
# lounge furniture and circulation can be examined. This does not alter the asset.
cut=obj.copy(); cut.data=obj.data.copy(); bpy.context.scene.collection.objects.link(cut)
cut.name='AGD_Lounge_preview_only'; me=cut.data
keep={'AGD_wood','AGD_rug','AGD_upholstery','AGD_leather','AGD_gold'}
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
delete=[]
for f in bm.faces:
    mat=me.materials[f.material_index].name if f.material_index<len(me.materials) and me.materials[f.material_index] else ''
    c=f.calc_center_median()
    if mat not in keep or c.z>3.45 or abs(c.x-focus.x)>4.0 or abs(c.y-focus.y)>4.2: delete.append(f)
bmesh.ops.delete(bm,geom=delete,context='FACES_ONLY'); bm.to_mesh(me); bm.free(); me.update()
obj.hide_render=True

# Restrained warm floor tile under the lounge zone, only for the preview camera.
floor=bpy.data.materials.new('AGD_preview_lounge_floor'); floor.diffuse_color=(.07,.035,.018,1); floor.use_nodes=True
floor.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.07,.035,.018,1)
floor.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.88
bpy.ops.mesh.primitive_cube_add(size=1,location=(focus.x,focus.y,.12))
slab=bpy.context.object; slab.name='AGD_Lounge_preview_floor_only'; slab.dimensions=(8.2,8.2,.22); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); slab.data.materials.append(floor)

scene=bpy.context.scene
camd=bpy.data.cameras.new('AGD_LoungeCamera'); cam=bpy.data.objects.new('AGD_LoungeCamera',camd); scene.collection.objects.link(cam)
cam.location=focus+Vector((-6.5,-8.5,8.5)); cam.rotation_euler=(focus-cam.location).to_track_quat('-Z','Y').to_euler(); camd.type='ORTHO'; camd.ortho_scale=11.5; scene.camera=cam
for name,loc,power,area in [('LoungeKey',focus+Vector((-3,-3,8)),500,8),('LoungeFill',focus+Vector((6,4,8)),250,7)]:
    ld=bpy.data.lights.new(name,'AREA'); ld.energy=power; ld.shape='DISK'; ld.size=area; o=bpy.data.objects.new(name,ld); scene.collection.objects.link(o); o.location=loc; o.rotation_euler=(focus-o.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.eevee.taa_render_samples=64; scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(here,'preview_lounge_schematic.png'); scene.view_settings.view_transform='AgX'; scene.view_settings.exposure=-.5; scene.world.color=(.045,.045,.045); bpy.ops.render.render(write_still=True)
print('LOUNGE_VIEW='+scene.render.filepath+' removed_faces='+str(len(delete)))
