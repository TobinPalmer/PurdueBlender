import bpy, os, math, bmesh
from mathutils import Vector
ROOT=os.path.abspath('.'); asset=os.path.join(ROOT,'modular','buildings','materials_science_and_electrical_engineering_msee.blend')
bpy.ops.wm.open_mainfile(filepath=asset)
shell=bpy.data.objects['materials_science_and_electrical_engineering_msee_official_GIS_shell']; screen=bpy.data.objects['MSEE_Max_W_Brown_two_story_glazed_atrium']
# Rebuild the original six-face GIS prism from its eight untouched extremity vertices.
coords=[shell.matrix_world@v.co for v in shell.data.vertices if abs(v.co.z-.3)<1e-3 or abs(v.co.z-15.0)<1e-3]
unique={tuple(round(x,5) for x in q) for q in coords}; corners=[Vector(p) for p in unique]
assert len(corners)==8, len(corners)
bottom=[p for p in corners if abs(p.z-.3)<1e-3]; top=[p for p in corners if abs(p.z-15.0)<1e-3]
assert len(bottom)==4 and len(top)==4
center_xy=Vector((sum(p.x for p in bottom)/4,sum(p.y for p in bottom)/4,0)); bottom.sort(key=lambda p:math.atan2(p.y-center_xy.y,p.x-center_xy.x)); top_by_xy={(round(p.x,5),round(p.y,5)):p for p in top}; top=[top_by_xy[(round(p.x,5),round(p.y,5))] for p in bottom]
verts=[tuple(p) for p in bottom+top]; faces=[tuple(reversed(range(4))),tuple(range(4,8))]
for i in range(4): j=(i+1)%4; faces.append((i,j,j+4,i+4))
newmesh=bpy.data.meshes.new('MSEE_source_GIS_shell_R5_reoriented');newmesh.from_pydata(verts,[],faces);newmesh.update(); old=shell.data; shell.data=newmesh
for m in old.materials:
 if m:shell.data.materials.append(m)
bm=bmesh.new(); bm.from_mesh(shell.data); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(shell.data); bm.free(); shell.data.update()
def status(mesh):
 b=bmesh.new(); b.from_mesh(mesh); res=(sum(not e.is_manifold for e in b.edges),round(b.calc_volume(signed=True),3)); b.free(); return res
print('PRECUT topology',len(shell.data.vertices),len(shell.data.polygons),status(shell.data))
# Accurate atrium panel plane basis (local tangent and inward normal), same footprint/origin.
pts=[screen.matrix_world@v.co for v in screen.data.vertices]; center=sum(pts,Vector())/len(pts); t=Vector((.627,-.779,0)).normalized(); inward=Vector((-t.y,t.x,0)); angle=math.atan2(t.y,t.x)
depth=18.0
bpy.ops.mesh.primitive_cube_add(size=1,location=center+inward*(depth/2)); cutter=bpy.context.object;cutter.dimensions=(22.25,depth,8.30);cutter.rotation_euler[2]=angle;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
mod=shell.modifiers.new('R5 two-storey atrium opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=shell;shell.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);shell.select_set(False);bpy.data.objects.remove(cutter,do_unlink=True)
print('POSTCUT topology',len(shell.data.vertices),len(shell.data.polygons),status(shell.data))
scene=bpy.context.scene; prevcam=scene.camera;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1300;scene.render.resolution_y=900;scene.render.resolution_percentage=100
# exterior close view
loc=center-inward*42+Vector((0,0,8));target=center+Vector((0,0,3.9));bpy.ops.object.camera_add(location=loc);cam=bpy.context.object;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=60;scene.camera=cam;scene.render.filepath=os.path.join(ROOT,'audit','rework_batch_a','materials_science_and_electrical_engineering_msee_revision5_entry_detail.png');bpy.ops.render.render(write_still=True)


