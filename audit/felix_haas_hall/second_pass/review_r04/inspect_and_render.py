"""Independent review; reopens r04 via CLI; writes only review_r04; never saves blend."""
import bpy,json,hashlib,datetime,collections
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parent
P=Path(bpy.data.filepath)
EXPECTED='7c608ff383548bfb2159fba7734d4cf461813f06ab024117a7d3201d4ba045fb'
assert hashlib.sha256(P.read_bytes()).hexdigest()==EXPECTED
C=bpy.data.collections['Asset_felix_haas_hall']
objects=[]
for o in C.all_objects:
    coords=[o.matrix_world@Vector(v) for v in o.bound_box] if o.type=='MESH' else []
    objects.append({'name':o.name,'type':o.type,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'bbox_world':[[min(v[a] for v in coords),max(v[a] for v in coords)] for a in range(3)] if coords else None,'properties':dict(o.items())})
report={'asset_path':str(P),'asset_sha256':EXPECTED,'reopened':True,'collection':C.name,'collection_properties':dict(C.items()),'objects':objects,'object_count':len(objects),'libraries':[x.filepath for x in bpy.data.libraries],'unpacked_images':[x.filepath for x in bpy.data.images if x.filepath and not x.packed_file],'scene_units':bpy.context.scene.unit_settings.system,'source_saved':False}
(D/'independent_saved_inspection.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
S=bpy.context.scene
for o in bpy.data.objects:
    if o.type in ('LIGHT','CAMERA'):o.hide_render=True
for o in C.all_objects:
    if o.name.startswith(('HAAS_Plan_','HAAS_Plan_Label_')):o.hide_render=True
S.render.engine='CYCLES';S.cycles.samples=12;S.cycles.use_denoising=True
S.render.resolution_x=1000;S.render.resolution_y=800;S.render.resolution_percentage=100
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=.7;S.view_settings.gamma=1
w=bpy.data.worlds.new('IndependentNeutral');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.8,.8,.8,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.8;S.world=w
for name,loc,power,size in [('IndependentKey',(20,-35,55),15000,50),('IndependentFill',(-40,30,40),11000,40)]:
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-10,0,5))-o.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('IndependentPerspective');cam=bpy.data.objects.new('IndependentPerspective',cd);S.collection.objects.link(cam);S.camera=cam;cd.type='PERSP';cd.lens=44
views=[('east_eye_oblique',(49,-26,1.7),(11,0,5.3),44),('west_entry_eye',(-56,12,1.7),(-26,12,6.7),44),('northwest_eye',(-56,50,1.7),(-15,1,6.8),38),('west_elevated',(-77,0,26),(-14,0,7),38)]
settings=[]
for name,loc,target,lens in views:
    cd.lens=lens;cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();S.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True);settings.append({'name':name,'camera_position_m':loc,'target_m':target,'lens_mm':lens,'projection':'perspective','match_status':'Approximate photographic angle/height class; photo cameras not calibrated'})
assert hashlib.sha256(P.read_bytes()).hexdigest()==EXPECTED
(D/'additional_view_settings.json').write_text(json.dumps({'asset_sha256':EXPECTED,'source_saved':False,'samples':12,'exposure':.7,'world_strength':.8,'views':settings},indent=2)+'\n')
print('INDEPENDENT_REVIEW_REOPEN_AND_RENDER_DONE',EXPECTED)
