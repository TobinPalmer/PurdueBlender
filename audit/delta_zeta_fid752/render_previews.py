import bpy,json,math,os
from mathutils import Vector
HERE=os.path.dirname(__file__);ROOT=os.path.abspath(os.path.join(HERE,'..','..'));cfg=json.load(open(os.path.join(HERE,'build_config.json'),encoding='utf-8'))
ASSET=os.path.join(ROOT,'modular','buildings','massing_house_301841601_7ae6159.blend');bpy.ops.wm.open_mainfile(filepath=ASSET);obj=bpy.data.objects[cfg['object_name']];scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
world=bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new('DZ Preview World');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.47,.55,.66,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.62
for o in list(scene.objects):
 if o.type in {'CAMERA','LIGHT'}:bpy.data.objects.remove(o,do_unlink=True)
ring=json.load(open(os.path.join(HERE,cfg['source_feature_file']),encoding='utf-8-sig'))['features'][0]['geometry']['rings'][0][:-1];R=6378137.;lat0=40.4274;lon0=-86.9137;pts=[]
for x,y in ring:
 lon=x/R*180/math.pi;lat=(2*math.atan(math.exp(y/R))-math.pi/2)*180/math.pi;pts.append(Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040,0)))
C=sum(pts,Vector((0,0,0)))/len(pts);entry_index=cfg['entry_edge_index'];a=pts[entry_index];b=pts[(entry_index+1)%len(pts)];edge=(b-a).normalized();out=Vector((edge.y,-edge.x,0));area2=sum(pts[i].x*pts[(i+1)%len(pts)].y-pts[(i+1)%len(pts)].x*pts[i].y for i in range(len(pts)));out*=1 if area2>0 else -1
xx=sum((p.x-C.x)**2 for p in pts);xy=sum((p.x-C.x)*(p.y-C.y) for p in pts);yy=sum((p.y-C.y)**2 for p in pts);ang=.5*math.atan2(2*xy,xx-yy);axis=Vector((math.cos(ang),math.sin(ang),0))
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size,target):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;aim(o,target)
def camera(name,loc,target,scale):
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;aim(o,target);scene.camera=o
target=C+Vector((0,0,4.5));area('Exterior Key',C+out*45+Vector((0,0,45)),13000,34,target);area('Exterior Fill',C+edge*35+Vector((0,0,24)),8500,30,target);area('Exterior Rim',C-out*25+Vector((0,0,34)),5500,28,target)
camera('Delta Zeta Exterior',C+out*58+edge*38+Vector((0,0,25)),target,72);scene.render.filepath=os.path.join(HERE,'exterior_three_quarter.png');bpy.ops.render.render(write_still=True)
# An entry close-up makes the qualitative source comparison legible.
entry_mid=pts[entry_index].lerp(pts[(entry_index+1)%len(pts)],.5)
area('Entry detail key',entry_mid+out*15+Vector((0,0,18)),11000,14,entry_mid+Vector((0,0,3.5)))
camera('Front Entry Detail',entry_mid+out*34+Vector((0,0,11)),entry_mid+Vector((0,0,3.6)),27)
scene.render.filepath=os.path.join(HERE,'entry_front_detail.png');bpy.ops.render.render(write_still=True)
# Render-only roof-open cutaway. Keep the complete footprint and upper-level slab.
src=obj.data;story=cfg['estimated_wall_eave_height_m']/2;verts=[];faces=[];mids=[]
for p in src.polygons:
 m=src.materials[p.material_index] if p.material_index<len(src.materials) else None;name=m.name if m else '';co=[src.vertices[i].co for i in p.vertices]
 if name.startswith('DELTAZETA_Estimated_Roof_Cap'):continue
 if name=='DELTAZETA_Schematic_Interior_Floor':
  if abs(sum(v.z for v in co)/len(co)-story)>.06:continue
  k=len(verts);verts.extend(tuple(v) for v in co);faces.append(tuple(range(k,k+len(co))));mids.append(p.material_index);continue
 if name.startswith('DELTAZETA_Schematic_'):
  k=len(verts);verts.extend(tuple(v) for v in co);faces.append(tuple(range(k,k+len(co))));mids.append(p.material_index);continue
 clipped=[]
 for i,v in enumerate(co):
  w=co[(i+1)%len(co)];iv=v.z<=story;iw=w.z<=story
  if iv:clipped.append(v.copy())
  if iv!=iw:clipped.append(v.lerp(w,(story-v.z)/(w.z-v.z)))
 if len(clipped)<3:continue
 k=len(verts);verts.extend(tuple(v) for v in clipped);faces.append(tuple(range(k,k+len(clipped))));mids.append(p.material_index)
mesh=bpy.data.meshes.new('DeltaZeta_RenderOnly_RoofOpen_Cutaway');mesh.from_pydata(verts,[],faces)
for m in src.materials:mesh.materials.append(m)
mesh.update()
for poly,mi in zip(mesh.polygons,mids):poly.material_index=mi
cut=bpy.data.objects.new('Render only - schematic cutaway',mesh);scene.collection.objects.link(cut);obj.hide_render=True
for o in list(scene.objects):
 if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
area('Cutaway Key',C+Vector((0,0,48))+out*32,26000,35,C+Vector((0,0,3)))
area('Cutaway Fill',C+edge*30+Vector((0,0,34)),18000,30,C+Vector((0,0,3)))
camera('Full Footprint Schematic Cutaway',C+out*34+edge*24+Vector((0,0,42)),C+Vector((0,0,3)),79);scene.render.filepath=os.path.join(HERE,'schematic_interior_cutaway.png')
# Render-only room names distinguish the sourced room categories from measured
# geometry. Text objects are temporary and are not saved into the asset library.
layout=json.load(open(os.path.join(HERE,'room_layout.json'),encoding='utf-8'))
label_mat=bpy.data.materials.new('Preview-only cutaway labels');label_mat.diffuse_color=(.015,.01,.008,1);label_mat.use_nodes=True;label_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.015,.01,.008,1);label_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value=(.015,.01,.008,1);label_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=.6
for entry_data in layout['rooms']:
 d=bpy.data.curves.new('Preview-only room label','FONT');d.body=entry_data['name'].upper();d.size=1.1;d.align_x='CENTER';d.align_y='CENTER';d.extrude=.004;d.materials.append(label_mat)
 label=bpy.data.objects.new('Preview-only '+entry_data['name'],d);scene.collection.objects.link(label);label.location=(entry_data['center_xy_m'][0],entry_data['center_xy_m'][1],story+1.45);label.rotation_euler[2]=math.atan2(axis.y,axis.x)
bpy.context.view_layer.update();scene.render.filepath=os.path.join(HERE,'schematic_interior_cutaway.png');bpy.ops.render.render(write_still=True)
print('DZ_PREVIEWS='+json.dumps({'exterior':scene.render.filepath,'collection_object_count':len(bpy.data.collections[cfg['collection_name']].objects)}))
