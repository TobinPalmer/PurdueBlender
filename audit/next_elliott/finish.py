import bpy,pathlib,shutil,json,math
from mathutils import Vector
p=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');d=p/'audit/next_elliott';path=p/'modular/buildings/elliott_hall_of_music.blend';shutil.copy2(path,d/'before.blend');bpy.ops.wm.open_mainfile(filepath=str(path))
c=bpy.data.collections['Asset_elliott_hall_of_music'];w=bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls'];uv=w.data.uv_layers.get('Facade_Meters') or w.data.uv_layers.new(name='Facade_Meters')
# Map every vertical wall face by its own physical horizontal distance and elevation.
for f in w.data.polygons:
 inds=list(f.loop_indices);coords=[w.data.vertices[w.data.loops[i].vertex_index].co for i in inds];origin=min(coords,key=lambda v:(v.z,v.x,v.y));other=max(coords,key=lambda v:(v-origin).xy.length);axis=Vector((other.x-origin.x,other.y-origin.y,0));axis.normalize()
 for li,co in zip(inds,coords):uv.data[li].uv=((co-origin).dot(axis),co.z)
m=bpy.data.materials.new('ELLT_Meter_Scaled_Red_Brick');m.use_nodes=True;m.diffuse_color=(.32,.095,.055,1);n=m.node_tree.nodes;n.clear();lk=m.node_tree.links;out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.82;lk.new(bs.outputs['BSDF'],out.inputs['Surface']);tex=n.new('ShaderNodeUVMap');tex.uv_map=uv.name;br=n.new('ShaderNodeTexBrick');br.inputs['Scale'].default_value=1;br.inputs['Brick Width'].default_value=.215;br.inputs['Row Height'].default_value=.075;br.inputs['Mortar Size'].default_value=.007;br.inputs['Mortar Smooth'].default_value=.002;br.inputs['Color1'].default_value=(.32,.095,.055,1);br.inputs['Color2'].default_value=(.20,.052,.03,1);br.inputs['Mortar'].default_value=(.38,.32,.24,1);lk.new(tex.outputs['UV'],br.inputs['Vector']);lk.new(br.outputs['Color'],bs.inputs['Base Color']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.003;lk.new(br.outputs['Fac'],bump.inputs['Height']);lk.new(bump.outputs['Normal'],bs.inputs['Normal']);w.data.materials.clear();w.data.materials.append(m)
w['texture_status']='Meter-scale UV, nominal .215x.075m brick module and .007m mortar estimated; qualitative red brick supported by Purdue 2015.'
bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));c=bpy.data.collections['Asset_elliott_hall_of_music'];pts=[o.matrix_world@Vector(v) for o in c.all_objects for v in o.bound_box];lo=Vector(tuple(min(v[i]for v in pts)for i in range(3)));hi=Vector(tuple(max(v[i]for v in pts)for i in range(3)));ctr=(lo+hi)/2;span=max(hi-lo);s=bpy.context.scene
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render=o.name not in {ob.name for ob in c.all_objects}
camd=bpy.data.cameras.new('Review');cam=bpy.data.objects.new('Review',camd);s.collection.objects.link(cam);s.camera=cam;camd.type='ORTHO';camd.ortho_scale=span*1.5;s.render.engine='CYCLES';s.cycles.samples=16;s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('ReviewWorld');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.6,.6,.6,1)
ld=bpy.data.lights.new('ReviewSun','SUN');ld.energy=3;ob=bpy.data.objects.new('ReviewSun',ld);s.collection.objects.link(ob);ob.rotation_euler=(.4,-.5,-.4)
for name,vec in [('southeast',(1,-1, .8)),('northwest',(-1,1,.8))]:
 cam.location=ctr+Vector(vec)*span;cam.rotation_euler=(ctr-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(d/(name+'.png'));bpy.ops.render.render(write_still=True)
(d/'results.json').write_text(json.dumps({'save_reopen':True,'objects':len(c.all_objects),'bounds':[list(lo),list(hi)],'images':[im.filepath for im in bpy.data.images if im.source=='FILE']},indent=2))
