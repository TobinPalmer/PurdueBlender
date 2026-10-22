import bpy, os, math,json
from mathutils import Vector
R=os.path.dirname(os.path.abspath(__file__)); bpy.ops.wm.open_mainfile(filepath=R+'/loeb.blend'); s=bpy.context.scene; c=bpy.data.collections['Fountain_Loeb']; dom=bpy.data.objects['Loeb_Mantaflow_Liquid_Domain']; bpy.context.view_layer.objects.active=dom; bpy.ops.fluid.free_all(); d=dom.modifiers[0].domain_settings; d.cache_directory='//cache_attempt5'; d.resolution_max=128
def mat(name,color):
    m=bpy.data.materials.new(name); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=.65; return m
stone=mat('Loeb_Photo_Light_Limestone',(.58,.54,.46)); red=mat('Loeb_Photo_Red_Pavers',(.32,.105,.065)); dark=mat('Loeb_Photo_Mottled_Bollards',(.22,.21,.19))
for o in list(c.objects):
    if 'Peak_Spray' in o.name or (o.type=='MESH' and ('Light' in o.name or 'LED' in o.name)):
        bpy.data.objects.remove(o,do_unlink=True); continue
    if o.name.startswith('Loeb_Liquid_Inflow'):
        o.scale.x=o.scale.y=.065/.0155
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.modifiers[0].flow_settings.surface_distance=1
    if o.type=='MESH' and any(n in o.name for n in ['Paving','DryDeck','Inlay_Band','Granite_Ring','Seatwall','Teak_Slat']):
        o.data.materials.clear(); o.data.materials.append(red if any(n in o.name for n in ['DryDeck','Inlay_Band','Granite_Ring']) else stone)
    if o.name.startswith('Loeb_Limestone_Bollard'):
        o.data.materials.clear(); o.data.materials.append(dark)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=.28,location=(o.location.x,o.location.y,.945)); cap=bpy.context.object; cap.name=o.name+'_Rounded_Cap'; cap.scale.z=.35
        for co in list(cap.users_collection): co.objects.unlink(cap)
        c.objects.link(cap); cap.data.materials.append(stone)
setup=bpy.data.collections.new('Loeb_Review_Setup'); s.collection.children.link(setup)
for o in list(c.objects):
    if o.type in ['CAMERA','LIGHT']:
        c.objects.unlink(o); setup.objects.link(o)
s['simulation_limitations']='FINAL PREVIEW: true bore remains unresolved. Peripheral simulated radius0.065m numerically enlarged from inferred0.0155m to obtain resolved jets at128res/0.145m voxels, surface_distance1. Nominal hydraulic flow mismatch; no engineering/calibrated accuracy. Legacy position/dimensions unverified pending coordinator correction.'
bpy.context.view_layer.objects.active=dom; s.frame_set(1); bpy.context.view_layer.update(); bpy.ops.wm.save_as_mainfile(filepath=R+'/loeb.blend'); bpy.ops.fluid.bake_all()
stats=[]
for fr in [12,24,48]:
    s.frame_set(fr); ev=dom.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh(); stats.append({'frame':fr,'vertices':len(me.vertices),'polygons':len(me.polygons)}); ev.to_mesh_clear(); s.render.filepath=R+'/attempt5_frame_%03d.png'%fr; bpy.ops.render.render(write_still=True)
json.dump(stats,open(R+'/attempt5_verification.json','w'),indent=2); bpy.ops.wm.save_as_mainfile(filepath=R+'/loeb.blend')
