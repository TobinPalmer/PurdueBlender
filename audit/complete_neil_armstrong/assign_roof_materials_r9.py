"""Correct R9 roof cap materials from registered 2023 orthophoto appearance."""
import bpy,json,os,hashlib
ROOT=r'C:\\Users\\Tobin\\Documents\\Blender\\PurdueMap'
BASE=os.path.join(ROOT,'audit','complete_neil_armstrong')
ASSET=os.path.join(ROOT,'modular','buildings','neil_armstrong_hall.blend')
EXPECTED='b5d28ea2579c7fd21837503b6c8c5f9006cfb6ac1020ce78223ad2e908a113f7'
if hashlib.sha256(open(ASSET,'rb').read()).hexdigest()!=EXPECTED: raise RuntimeError('Neil asset changed after R8 validation')
with open(os.path.join(BASE,'roof_surface_samples_r7_smooth.json'),encoding='utf-8') as f:samples=json.load(f)
bpy.ops.wm.open_mainfile(filepath=ASSET)
root=bpy.data.objects['AssetRoot_neil_armstrong_hall']; col=bpy.data.collections['Asset_neil_armstrong_hall']
assert len(col.objects)==445 and tuple(root.location)==(0.0,0.0,0.0)
mat=bpy.data.materials.get('ARMS_R9_Light_Roof_Surface')
if mat is None:
    mat=bpy.data.materials.new('ARMS_R9_Light_Roof_Surface'); mat.use_nodes=True
    mat.diffuse_color=(0.58,0.59,0.60,1.0)
    bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(0.48,0.50,0.52,1.0)
    bs.inputs['Roughness'].default_value=0.82
    if 'Metallic' in bs.inputs: bs.inputs['Metallic'].default_value=0.0
    mat['source_basis']='Visual color family from registered Indiana 2023 orthophoto; pale neutral roof surface. Substrate remains unknown.'
result=[]
for zone in samples['zones']:
    name=zone['object']; obj=bpy.data.objects[name]
    top_ids={int(row['index']) for row in zone['roof_surface_vertices']}
    if name in ('ARMS_R5_Coarse_LiDAR_wing_low','ARMS_R5_Coarse_LiDAR_roof_high'):
        if mat.name not in [m.name for m in obj.data.materials if m]: obj.data.materials.append(mat)
        index=next(i for i,m in enumerate(obj.data.materials) if m and m.name==mat.name)
        changed=0
        for poly in obj.data.polygons:
            if all(int(v) in top_ids for v in poly.vertices): poly.material_index=index; changed+=1
        assert changed>0
        obj['roof_surface_material_r9']='Pale neutral roof surface appearance from registered Indiana 2023 orthophoto; actual roof membrane/concrete substrate is not inferred.'
        result.append({'object':name,'surface_material':mat.name,'top_faces':changed})
    elif name=='ARMS_R5_Coarse_LiDAR_wing_mid':
        acm=bpy.data.materials['ARMS_R6_Mayflower_Red_ACM']
        index=next(i for i,m in enumerate(obj.data.materials) if m and m.name==acm.name)
        changed=0
        for poly in obj.data.polygons:
            if all(int(v) in top_ids for v in poly.vertices): poly.material_index=index; changed+=1
        assert changed>0
        obj['roof_surface_material_r9']='Mayflower Red ACM retained on 18–20m height band; the band follows red perimeter canopy appearance in registered Indiana 2023 orthophoto.'
        result.append({'object':name,'surface_material':acm.name,'top_faces':changed})
    obj.data.update()
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print(json.dumps({'revision':'R9','material_changes':result,'root_location':list(root.location),'object_count':len(col.objects),'asset_sha256':hashlib.sha256(open(ASSET,'rb').read()).hexdigest()},indent=2))
