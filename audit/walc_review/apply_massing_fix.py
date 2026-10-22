import bpy,json,sys,bmesh
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[2]
aid=sys.argv[sys.argv.index('--')+1]
p=next(p for p in json.loads((ROOT/'audit/walc_review/massing_fix_plan.json').read_text()) if p['id']==aid)
if p['new']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    c=bpy.data.collections.new(p['collection']);bpy.context.scene.collection.children.link(c)
    o=bpy.data.objects.new(aid,bpy.data.meshes.new(aid+'_Initial'));c.objects.link(o)
else:
    c=bpy.data.collections.get(p['collection']);o=next(o for o in c.all_objects if o.type=='MESH')
materials=list(o.data.materials) if o.type=='MESH' else []
mesh=bpy.data.meshes.new(aid+'_OfficialFootprint');mesh.from_pydata(p['vertices'],[],p['faces']);mesh.update()
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
o.data=mesh;o.matrix_world=Matrix.Identity(4)
for mat in materials:mesh.materials.append(mat)
if not materials:
    mat=bpy.data.materials.new('PurdueBrick_Estimated');mat.diffuse_color=(.32,.14,.09,1);mesh.materials.append(mat)
o['official_code']=p['code'];o['official_feature_ids']=p['fids'];o['height_status']=p['height_status']
o['footprint_source']='Purdue BuildingShapesZip4 layer0, saved2026-10-22; project local conversion'
if p['new']:
    sc=bpy.context.scene;sc.name='Building_'+aid
    bpy.data.libraries.write(str(ROOT/'modular'/p['file']),{sc},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
else:bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('CORRECTED',aid,len(mesh.vertices),len(mesh.polygons))
