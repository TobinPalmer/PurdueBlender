import bpy, os, json, hashlib
from mathutils import Vector
asset=os.path.abspath('modular/buildings/rawls_hall.blend');bpy.ops.wm.open_mainfile(filepath=asset);s=bpy.context.scene;bpy.context.view_layer.update()
def mat4(m):return [[round(float(m[r][c]),8) for c in range(4)] for r in range(4)]
def bounds(o):
 p=[o.matrix_world@Vector(c) for c in o.bound_box];return [[round(min(v[i] for v in p),5),round(max(v[i] for v in p),5)] for i in range(3)]
def meshhash(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(('%0.9f,%0.9f,%0.9f;'%(v.co.x,v.co.y,v.co.z)).encode())
 for f in o.data.polygons:h.update((str(tuple(f.vertices))+';').encode())
 return h.hexdigest()
# Render-only scene illumination; these objects are not saved to the asset.
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
w=s.world or bpy.data.worlds.new('R8_RenderWorld');s.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.48,.57,.69,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
for j,(loc,power,size,target) in enumerate([((3,-8,6),1400,5,(3,-22,8)),((20,-10,8),1100,5,(15,-20,7)),((1,8,5),1300,4,(1,22,7))]):
 ld=bpy.data.lights.new('R8_Temp_Fill_'+str(j),'AREA');ld.energy=power;ld.shape='DISK';ld.size=size;lo=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(lo);lo.location=loc;lo.rotation_euler=(Vector(target)-lo.location).to_track_quat('-Z','Y').to_euler()
def render(name,eye,target,lens=46,res=(1200,900)):
 d=bpy.data.cameras.new('R8_Temp_'+name);c=bpy.data.objects.new(d.name,d);s.collection.objects.link(c);c.location=eye;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;s.camera=c;s.render.filepath=os.path.abspath('audit/batch4_rawls/'+name+'_round8.png');bpy.ops.render.render(write_still=True);bpy.data.objects.remove(c,do_unlink=True);bpy.data.cameras.remove(d);return s.render.filepath
# exterior elevations and apron relationship
paths={}
paths['north']=render('north_exterior',(12,69,28),(8,0,11),35)
paths['south']=render('south_exterior',(5,-63,26),(5,-2,10),35)
paths['sidewalk']=render('sidewalk_southwest',(22,-49,10),(2,-18,1),45)
# Read-only validation after file reopen, with evaluated object transforms.
fix_names=['Cam_RAWL_01_North_StateSt','Cam_RAWL_02_NW_Curved_Rotunda','Cam_RAWL_03_West_GrantSt_Skywalk','Cam_RAWL_04_SE_Diagonal_Facade','Cam_RAWL_05_Roof_Arched_Penthouse','Cam_RAWL_06_Ortho_Footprint_Top','RAWL_Site_Sidewalk_Apron','RAWL_South_Windows_South_BronzeMullions']
fixed=[bpy.data.objects[n] for n in fix_names]
report={'asset':asset,'asset_sha256':hashlib.sha256(open(asset,'rb').read()).hexdigest(),'root':{'matrix_world':mat4(bpy.data.objects['AssetRoot_rawls_hall'].matrix_world)},
 'structural_shell':{'matrix_world':mat4(bpy.data.objects['RAWL_Masonry_Exterior_Walls'].matrix_world),'world_bounds':bounds(bpy.data.objects['RAWL_Masonry_Exterior_Walls']),'mesh_sha256':meshhash(bpy.data.objects['RAWL_Masonry_Exterior_Walls'])},
 'fixed_objects':[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'matrix_parent_inverse':mat4(o.matrix_parent_inverse),'matrix_world':mat4(o.matrix_world),'bounds':bounds(o),'mesh_sha256':meshhash(o) if o.type=='MESH' else None} for o in fixed],
 'all_mesh_bounds':[{'name':o.name,'bounds':bounds(o)} for o in s.objects if o.type=='MESH'],
 'external_images':[{'name':i.name,'filepath':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE'],
 'render_paths':paths,'materialless_meshes':[o.name for o in s.objects if o.type=='MESH' and not o.data.materials]}
with open(os.path.abspath('audit/batch4_rawls/round8_reopen_render_validation.json'),'w') as f:json.dump(report,f,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='all_mesh_bounds'},indent=2))
