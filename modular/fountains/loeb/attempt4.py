import bpy, os, json, math
R=os.path.dirname(os.path.abspath(__file__)); bpy.ops.wm.open_mainfile(filepath=R+'/loeb.blend'); s=bpy.context.scene; c=bpy.data.collections['Fountain_Loeb']; dom=bpy.data.objects['Loeb_Mantaflow_Liquid_Domain']; bpy.context.view_layer.objects.active=dom; bpy.ops.fluid.free_all()
d=dom.modifiers[0].domain_settings; d.cache_directory='//cache_attempt4'; d.resolution_max=128
for o in list(c.objects):
    if 'Solomon_Loeb' in o.name or 'Droplet' in o.name: bpy.data.objects.remove(o,do_unlink=True); continue
    if o.name.startswith('Loeb_Liquid_Inflow'):
        o.scale.x=o.scale.y=.0155/.19
        bpy.context.view_layer.objects.active=o; o.select_set(True); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.select_set(False)
        f=o.modifiers[0].flow_settings; f.surface_distance=1; f.subframes=2
bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.025,depth=.15,location=(-50,-255,.42)); o=bpy.context.object; o.name='Loeb_Center_Liquid_Inflow'
for co in list(o.users_collection): co.objects.unlink(o)
c.objects.link(o); m=o.modifiers.new('Center liquid inflow','FLUID'); m.fluid_type='FLOW'; f=m.flow_settings; f.flow_type='LIQUID'; f.flow_behavior='INFLOW'; f.use_initial_velocity=True; f.velocity_coord=(0,0,10); f.surface_distance=1; f.subframes=2
for name in ['FoundersPark_Brick_Inlay_Band','LoebFountain_Polished_Black_Granite_Ring']:
    ob=bpy.data.objects.get(name)
    if ob:
        mat=bpy.data.materials.new('Loeb_Photographic_Paving_'+name); mat.diffuse_color=(.34,.16,.12,1); ob.data.materials.clear(); ob.data.materials.append(mat)
s['nominal_geometric_Q_m3s']=24*math.pi*.0155**2*math.sqrt(4.8**2+4.5**2)+math.pi*.025**2*10
s['simulation_limitations']='128 cells/18.5m =0.145m voxels. Actual geometric radii .0155m perimeter and .025m center infer nominal~0.139m3/s from2200USGPM. Surface-distance1voxel numerical thickening inflates effective volume. No converged flow conservation/visual claim. Geometry and position unsurveyed.'
bpy.context.view_layer.objects.active=dom; s.frame_set(1); bpy.context.view_layer.update(); bpy.ops.wm.save_as_mainfile(filepath=R+'/loeb.blend'); bpy.ops.fluid.bake_all()
stats=[]
for fr in [12,24,48]:
    s.frame_set(fr); ev=dom.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh(); stats.append({'frame':fr,'vertices':len(me.vertices),'polygons':len(me.polygons)}); ev.to_mesh_clear(); s.render.filepath=R+'/attempt4_frame_%03d.png'%fr; bpy.ops.render.render(write_still=True)
json.dump(stats,open(R+'/attempt4_verification.json','w'),indent=2); bpy.ops.wm.save_as_mainfile(filepath=R+'/loeb.blend')
