import bpy,json,bmesh
from pathlib import Path
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/complete_potter';P=R/'modular/buildings/potter_engineering.blend';bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];material=bpy.data.materials['POTR_Historic2016_Partition_Paint']
for o in list(c.objects):
 if 'Historic2016_Plan' in o.name:bpy.data.objects.remove(o,do_unlink=True)
a=json.loads((D/'merged_interior.json').read_text())
for page,base in [(51,-4.064),(53,.6096),(54,4.8768),(55,9.144)]:
 d=a[str(page)];me=bpy.data.meshes.new('POTR_Historic2016_Merged_Partitions');me.from_pydata(d['vertices'],[],d['faces']);me.materials.append(material);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new('POTR_Historic2016_Plan%d_MergedPartitions'%page,me);c.objects.link(ob);ob.location.z=base;ob['source']='2016 existing plan, raster trace, approximate registration';ob['registration_iou']=d['registration_iou']
bpy.ops.wm.save_as_mainfile(filepath=str(P))
