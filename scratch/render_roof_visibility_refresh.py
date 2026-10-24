import bpy, os, math
from mathutils import Vector
ROOT=os.path.abspath('.'); OUT=os.path.join(ROOT,'audit','material_review','roof_visibility_refresh'); os.makedirs(OUT,exist_ok=True)
files=['walc.blend','felix_haas_hall.blend','mccutcheon_hall.blend']
def bounds(objs):
 pts=[o.matrix_world@Vector(c) for o in objs for c in o.bound_box]
 lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
 hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
 return lo,hi,(lo+hi)*.5, max(hi-lo)
for fn in files:
 key=fn[:-6]; bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'modular','buildings',fn)); scene=bpy.context.scene
 roofmats=[m for m in bpy.data.materials if m.get('roof_grain_visibility_pass')]
 assert roofmats, f'no saved roof pass in {fn}'
 roofobjs=[o for o in bpy.data.objects if o.type=='MESH' and any(s.material in roofmats for s in o.material_slots)]
 meshes=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and not o.name.lower().startswith(('site_','tree','shrub'))]
 lo,hi,center,span=bounds(meshes)
 # Use controlled review lighting rather than stacking saved scene lights
 for oldlight in (o for o in scene.objects if o.type=='LIGHT'): oldlight.hide_render=True
 # consistent elevated campus overview
 camd=bpy.data.cameras.new('Roof Texture QA Overview'); cam=bpy.data.objects.new('Roof Texture QA Overview',camd); scene.collection.objects.link(cam)
 cam.location=center+Vector((1.55,-1.9,1.55))*span; cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); camd.type='ORTHO'; camd.ortho_scale=span*1.65; scene.camera=cam
 # controlled key and fill that show broad color/roughness drift without harsh hotspots
 sun_data=bpy.data.lights.new('Roof QA Sun','SUN'); sun=bpy.data.objects.new('Roof QA Sun',sun_data); scene.collection.objects.link(sun); sun.rotation_euler=(math.radians(27),math.radians(-24),math.radians(-35)); sun_data.energy=1.65; sun_data.angle=math.radians(12)
 area_data=bpy.data.lights.new('Roof QA Fill','AREA'); area=bpy.data.objects.new('Roof QA Fill',area_data); scene.collection.objects.link(area); area.location=center+Vector((-0.8,-0.5,1.4))*span; area_data.energy=span*span*.35; area_data.shape='DISK'; area_data.size=span*.9; area.rotation_euler=(center-area.location).to_track_quat('-Z','Y').to_euler()
 if scene.world is None: scene.world=bpy.data.worlds.new('Roof QA World')
 scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.2,.23,.28,1); bg.inputs['Strength'].default_value=.28
 scene.render.engine='CYCLES'; scene.cycles.samples=16; scene.cycles.use_denoising=True
 scene.render.resolution_x=1100; scene.render.resolution_y=720; scene.render.resolution_percentage=80; scene.render.image_settings.file_format='PNG'; scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=-.35
 scene.render.filepath=os.path.join(OUT,key+'_overview.png'); bpy.ops.render.render(write_still=True); print('RENDERED',scene.render.filepath)
 # close material shot framed from the actual roof faces
 rlo,rhi,rc,rspan=bounds(roofobjs)
 cam.location=rc+Vector((1.4,-1.8,1.65))*rspan; cam.rotation_euler=(rc-cam.location).to_track_quat('-Z','Y').to_euler(); camd.ortho_scale=rspan*.95
 scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
 scene.render.filepath=os.path.join(OUT,key+'_roof_close.png'); bpy.ops.render.render(write_still=True); print('RENDERED',scene.render.filepath)
 print('REOPEN_VERIFY',fn,'roof_objects',len(roofobjs),'materials',[(m.name,m.get('roof_grain_visibility_pass')) for m in roofmats])

