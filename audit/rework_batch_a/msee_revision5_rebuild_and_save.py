import bpy, os, math, bmesh
from mathutils import Vector
ROOT=os.path.abspath('.'); asset=os.path.join(ROOT,'modular','buildings','materials_science_and_electrical_engineering_msee.blend'); outdir=os.path.join(ROOT,'audit','rework_batch_a')
bpy.ops.wm.open_mainfile(filepath=asset); coll=bpy.data.collections['Asset_materials_science_and_electrical_engineering_msee']; shell=bpy.data.objects['materials_science_and_electrical_engineering_msee_official_GIS_shell']; screen=bpy.data.objects['MSEE_Max_W_Brown_two_story_glazed_atrium']
# Reconstruct the original source shell from retained GIS corner coordinates, correcting its inverted face winding.
coords=[shell.matrix_world@v.co for v in shell.data.vertices if abs(v.co.z-.3)<1e-3 or abs(v.co.z-15.0)<1e-3]
unique={tuple(round(x,5) for x in q) for q in coords}; corners=[Vector(p) for p in unique]; assert len(corners)==8, f'Expected 8 retained GIS corners; got {len(corners)}'
bottom=[p for p in corners if abs(p.z-.3)<1e-3]; top=[p for p in corners if abs(p.z-15.0)<1e-3]; assert len(bottom)==4 and len(top)==4
cxy=Vector((sum(p.x for p in bottom)/4,sum(p.y for p in bottom)/4,0)); bottom.sort(key=lambda p:math.atan2(p.y-cxy.y,p.x-cxy.x)); topmap={(round(p.x,5),round(p.y,5)):p for p in top}; top=[topmap[(round(p.x,5),round(p.y,5))] for p in bottom]
verts=[tuple(p) for p in bottom+top]; faces=[tuple(reversed(range(4))),tuple(range(4,8))]
for i in range(4): j=(i+1)%4; faces.append((i,j,j+4,i+4))
old=shell.data; new=bpy.data.meshes.new('MSEE_GIS_shell_R5_with_atrium_cut'); new.from_pydata(verts,[],faces); new.update(); shell.data=new
for m in old.materials:
 if m: new.materials.append(m)
bm=bmesh.new(); bm.from_mesh(new); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(new); bm.free(); new.update()
def topo(mesh):
 bm=bmesh.new();bm.from_mesh(mesh);t=(sum(not e.is_manifold for e in bm.edges),round(bm.calc_volume(signed=True),3));bm.free();return t
assert topo(new)[0]==0 and topo(new)[1]>0,topo(new)
# Apply a watertight 2-storey atrium excavation in the same GIS-local frame.
sp=[screen.matrix_world@v.co for v in screen.data.vertices]; center=sum(sp,Vector())/len(sp); tangent=Vector((.627,-.779,0)).normalized(); inward=Vector((-tangent.y,tangent.x,0)); angle=math.atan2(tangent.y,tangent.x); depth=18.0
bpy.ops.mesh.primitive_cube_add(size=1,location=center+inward*(depth/2)); cutter=bpy.context.object;cutter.name='TEMP_MSEE_R5_atrium_cut';cutter.dimensions=(22.25,depth,8.30);cutter.rotation_euler[2]=angle;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
mod=shell.modifiers.new('R5 watertight atrium opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=shell;shell.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);shell.select_set(False);bpy.data.objects.remove(cutter,do_unlink=True)
assert topo(shell.data)[0]==0 and topo(shell.data)[1]>0, f'Boolean shell not manifold: {topo(shell.data)}'
# Verify GIS envelope preserved.
pts=[shell.matrix_world@v.co for v in shell.data.vertices]; bounds=[[round(min(p[i] for p in pts),4),round(max(p[i] for p in pts),4)] for i in range(3)]
assert bounds[0][0]<-37 and bounds[0][1]>37 and bounds[1][0]<-40 and bounds[1][1]>40 and bounds[2]==[.3,15.0],bounds
# Render final saved-state previews.
scene=bpy.context.scene; origcam=scene.camera; scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.filepath=os.path.join(outdir,'materials_science_and_electrical_engineering_msee_revision5_preview.png');bpy.ops.render.render(write_still=True)
loc=center-inward*42+Vector((0,0,8));target=center+Vector((0,0,3.9));bpy.ops.object.camera_add(location=loc);cam=bpy.context.object;cam.name='TEMP_MSEE_R5_entry_camera';cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=60;scene.camera=cam;scene.render.resolution_x=1300;scene.render.resolution_y=900;scene.render.filepath=os.path.join(outdir,'materials_science_and_electrical_engineering_msee_revision5_entry_detail.png');bpy.ops.render.render(write_still=True);scene.camera=origcam;bpy.data.objects.remove(cam,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=asset)
print('SAVED clean R5 shell',len(coll.all_objects),'bounds',bounds,'topology',topo(shell.data),'volume',topo(shell.data)[1])
