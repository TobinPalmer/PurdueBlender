"""R3 saved-file readback; this script does not write the blend file."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); P=ROOT/'audit/niswonger_aviation_tech_refine'; f=Path(bpy.data.filepath)
a=bpy.data.collections.get('Asset_niswonger_aviation_tech');assert a
objs=list(a.all_objects);root=bpy.data.objects.get('AssetRoot_niswonger_aviation_tech');assert root
missing=[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]
no_mat=[ob.name for ob in objs if ob.type=='MESH' and not ob.data.materials]
roof_names=['NISW_R2_Roof_Brick_Wing','NISW_R2_Roof_Classroom_Wing','NISW_Photographic_Sloping_Roof','NISW_Flat_Roof_Membrane']
roof_visibility={n:bpy.data.objects[n].hide_render for n in roof_names}
assert all(not x for x in roof_visibility.values()),roof_visibility
assert not missing and not no_mat,(missing,no_mat)
new_detail=sorted(ob.name for ob in objs if ob.name.startswith('NISW_R3_Roof_') and ob.name not in ('NISW_R3_Roof_Edge_Metal','NISW_R3_Roof_Lap_Seam'))
assert len(new_detail)==13,(len(new_detail),new_detail)
assert root.location.length<1e-8
assert not [ob.name for ob in objs if ob.name.startswith(('R3_Key','R3_Fill','R3_Camera'))]
mesh_objs=[ob for ob in objs if ob.type=='MESH']
lo=[round(min((ob.matrix_world@Vector(v))[i] for ob in mesh_objs for v in ob.bound_box),4) for i in range(3)]
hi=[round(max((ob.matrix_world@Vector(v))[i] for ob in mesh_objs for v in ob.bound_box),4) for i in range(3)]
sha=hashlib.sha256(f.read_bytes()).hexdigest()
summary={'reopened_in_fresh_blender':True,'asset_path':str(f),'sha256':sha,'asset_collection':a.name,'object_count':len(objs),'mesh_count':len(mesh_objs),'r3_roof_detail_meshes':len(new_detail),'r3_roof_detail_names':new_detail,'all_roof_shells_render_visible':roof_visibility,'unmaterialed_meshes':no_mat,'missing_external_images':missing,'root_location':list(root.location),'mesh_bounds_local':{'min':lo,'max':hi}}
(P/'reopen_validation_r3.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
