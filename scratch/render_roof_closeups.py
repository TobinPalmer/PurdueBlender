import bpy,os
from mathutils import Vector
P=os.path.abspath('.')
items={'hovde_hall':'Hovde_Roof_Membrane','hansen_life_sciences':'Roof_Membrane_Gravel','knoy_hall':'KNOY_Roof_Gravel_Membrane'}
for f,mn in items.items():
 bpy.ops.wm.open_mainfile(filepath=os.path.join(P,'modular','buildings',f+'.blend'))
 objs=[o for o in bpy.context.scene.objects if o.type=='MESH' and any(s.material and s.material.name==mn for s in o.material_slots)]
 pts=[o.matrix_world@Vector(c) for o in objs for c in o.bound_box]
 lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts))); hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts))); center=(lo+hi)*.5; dim=hi-lo
 camd=bpy.data.cameras.new('RoofCloseupCamera'); cam=bpy.data.objects.new('RoofCloseupCamera',camd); bpy.context.scene.collection.objects.link(cam)
 cam.location=center+Vector((dim.x*.18,-max(dim.y*.45,8),max(dim.z+16,18))); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); camd.type='ORTHO'; camd.ortho_scale=max(min(dim.x,dim.y)*1.1,18); bpy.context.scene.camera=cam
 w=bpy.context.scene.world or bpy.data.worlds.new('RoofReviewWorld'); bpy.context.scene.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs['Color'].default_value=(.22,.27,.34,1); w.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
 for name,off,power,size in [('RoofKey',Vector((-12,-16,24)),1800,14),('RoofFill',Vector((15,-3,14)),700,12)]:
  ld=bpy.data.lights.new(name,'AREA'); ob=bpy.data.objects.new(name,ld); bpy.context.scene.collection.objects.link(ob); ob.location=center+off; ld.energy=power; ld.shape='DISK'; ld.size=size; ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler()
 sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE'; sc.eevee.taa_render_samples=32; sc.render.resolution_x=1000; sc.render.resolution_y=700; sc.render.resolution_percentage=100; sc.view_settings.view_transform='AgX'; sc.render.image_settings.file_format='PNG'; sc.render.filepath=os.path.join(P,'audit',f'material_roof_close_{f}.png')
 bpy.ops.render.render(write_still=True); print('ROOF_CLOSEUP',f,'bounds',tuple(round(x,1) for x in dim),'objects',len(objs))
