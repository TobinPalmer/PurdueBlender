import bpy
from pathlib import Path
from mathutils import Vector
root=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); src=root/'modular/buildings/math_sciences.blend'; out=root/'audit/batch3_math'
bpy.ops.wm.open_mainfile(filepath=str(src)); asset=bpy.data.collections['Asset_math_sciences']
sc=bpy.data.scenes.new('Math Exterior Low Campus Eye Review'); sc.collection.children.link(asset); sc.render.engine='CYCLES'; sc.cycles.samples=24
sc.render.resolution_x=1200; sc.render.resolution_y=1200; sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Medium High Contrast'; sc.view_settings.exposure=.65
sc.world=bpy.data.worlds.new('Math low angle sky'); sc.world.use_nodes=True; sc.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.52,.55,.58,1); sc.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.8
sd=bpy.data.lights.new('Math low angle sun','SUN'); sd.energy=2.2; sd.angle=.2; so=bpy.data.objects.new('Math low angle sun',sd); sc.collection.objects.link(so); so.rotation_euler=(.35,-.45,-.5)
ld=bpy.data.lights.new('Math fill','AREA'); ld.energy=8500; ld.shape='DISK'; ld.size=55; lo=bpy.data.objects.new('Math fill',ld); sc.collection.objects.link(lo); lo.location=(60,-35,60); lo.rotation_euler=(Vector((0,-2,16))-lo.location).to_track_quat('-Z','Y').to_euler()
me=bpy.data.meshes.new('Review ground mesh'); me.from_pydata([(-150,-150,-.08),(150,-150,-.08),(150,150,-.08),(-150,150,-.08)],[],[(0,1,2,3)]); g=bpy.data.objects.new('Review ground',me); sc.collection.objects.link(g); mat=bpy.data.materials.new('Review ground mat'); mat.diffuse_color=(.38,.4,.41,1); mat.use_nodes=True; next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(.38,.4,.41,1); g.data.materials.append(mat)
cd=bpy.data.cameras.new('Low campus eye camera'); cd.type='ORTHO'; cd.ortho_scale=77; cam=bpy.data.objects.new('Low campus eye camera',cd); sc.collection.objects.link(cam); cam.location=(105,-65,29); cam.rotation_euler=(Vector((0,-2,17))-cam.location).to_track_quat('-Z','Y').to_euler(); sc.camera=cam
sc.render.image_settings.file_format='PNG'; sc.render.filepath=str(out/'exterior_round4.png'); bpy.context.window.scene=sc; bpy.ops.render.render(write_still=True); print('saved-file exterior render',len(asset.all_objects))
