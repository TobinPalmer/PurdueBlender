import bpy, os
from mathutils import Vector
bid=os.path.splitext(os.path.basename(bpy.data.filepath))[0]
mapdata={
 'hicks_library':('HIKS_Roof_Gravel_Ballast_Deck','audit/roof_surface_hicks_library.png'),
 'lawson_hall':('LWSN_Roof_Surface','audit/roof_surface_lawson_hall.png'),
 'krannert_building':('KRAN_FloorSlab_Roof_Deck','audit/roof_surface_krannert_building.png')}
name,out=mapdata[bid];obj=bpy.data.objects.get(name)
if obj is None: raise RuntimeError('missing roof mesh '+name)
sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE';sc.eevee.taa_render_samples=64
sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
world=sc.world or bpy.data.worlds.new('RoofReviewWorld');sc.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.22,.26,.32,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
corners=[obj.matrix_world@Vector(c) for c in obj.bound_box]; mn=Vector((min(v.x for v in corners),min(v.y for v in corners),min(v.z for v in corners)));mx=Vector((max(v.x for v in corners),max(v.y for v in corners),max(v.z for v in corners)));center=(mn+mx)*.5;dx=mx.x-mn.x;dy=mx.y-mn.y;d=max(dx,dy,2)
camdata=bpy.data.cameras.new('RoofMaterialReview');cam=bpy.data.objects.new('RoofMaterialReview',camdata);sc.collection.objects.link(cam);cam.location=center+Vector((-d*.8,-d*1.0,d*1.35));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=d*.40;sc.camera=cam
ld=bpy.data.lights.new('RakingRoofLight','SUN');lo=bpy.data.objects.new('RakingRoofLight',ld);sc.collection.objects.link(lo);lo.location=center+Vector((-d,-d*.2,d*.65));lo.rotation_euler=(center-lo.location).to_track_quat('-Z','Y').to_euler();ld.energy=2.0
sc.render.image_settings.file_format='PNG';sc.render.filepath=os.path.abspath(out);bpy.ops.render.render(write_still=True)
mat=obj.data.materials[0];nt=mat.node_tree;noise=next(n for n in nt.nodes if n.label=='Broad Roughness Variation');remap=next(n for n in nt.nodes if n.label=='Restrained Surface Roughness');print('RENDER',out,'object',obj.name,'size',(round(dx,1),round(dy,1)),'rough range',(remap.inputs['To Min'].default_value,remap.inputs['To Max'].default_value),'noise scale',noise.inputs['Scale'].default_value)


