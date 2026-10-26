import bpy, math, os
from mathutils import Vector
root=os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath),'..','..'))
out=os.path.join(root,'audit','massing_fuse_39cf4b5','previews')
os.makedirs(out,exist_ok=True)
sc=bpy.context.scene
sc.render.engine='BLENDER_WORKBENCH'
sc.render.resolution_x=1200; sc.render.resolution_y=900; sc.render.resolution_percentage=100
sc.display.shading.light='STUDIO'; sc.display.shading.studio_light='paint.sl'; sc.display.shading.color_type='MATERIAL'; sc.display.shading.background_type='WORLD'; sc.display.shading.show_cavity=True; sc.display.shading.cavity_type='BOTH'; sc.display.shading.show_shadows=True
sc.world.color=(0.06,0.06,0.06)
# Temporary grade plane for previews only: it grounds the building and occludes
# the below-grade parking study, matching its documented underground position.
ground_mat=bpy.data.materials.new('TEMP_FUSE_Preview_Grade'); ground_mat.diffuse_color=(0.25,0.27,0.28,1)
ground_mesh=bpy.data.meshes.new('TEMP_FUSE_Preview_Grade_Mesh'); ground_mesh.from_pydata([(-140,-140,0),(140,-140,0),(140,140,0),(-140,140,0)],[],[(0,1,2,3)]); ground_mesh.materials.append(ground_mat)
ground=bpy.data.objects.new('TEMP_FUSE_Preview_Grade',ground_mesh); sc.collection.objects.link(ground); ground.location=(-65.813,602.647,-0.03)
# include the complete above-grade shell and the below-grade study in composition.
center=Vector((-65.813,602.647,4.2))
def camera(name,location,target,lens=50):
    data=bpy.data.cameras.new(name); obj=bpy.data.objects.new(name,data); sc.collection.objects.link(obj); obj.location=location; obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler(); data.lens=lens; sc.camera=obj; return obj
cam=camera('TEMP_FUSE_Exterior',(center.x+125,center.y-145,center.z+105),center,48)
sc.render.filepath=os.path.join(out,'exterior_axonometric.png'); bpy.ops.render.render(write_still=True)
cam.location=(center.x,center.y,center.z+190); cam.rotation_euler=(Vector((center.x,center.y,center.z))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=55
sc.render.filepath=os.path.join(out,'plan.png'); bpy.ops.render.render(write_still=True)
entry_cam=camera('TEMP_FUSE_Street_Entry',(center.x,561.496-43.0,5.0),(center.x,561.496,1.35),65)
sc.render.filepath=os.path.join(out,'street_entry.png'); bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(cam,do_unlink=True); bpy.data.objects.remove(entry_cam,do_unlink=True); bpy.data.objects.remove(ground,do_unlink=True)
print('FUSE_PREVIEWS_RENDERED',out)
