import bpy, json, collections
from mathutils import Vector
p=r'modular/buildings/massing_house_1089876362_14ecd2c.blend'
bpy.ops.wm.open_mainfile(filepath=p)
sc=bpy.context.scene
out={'scene':sc.name,'file':bpy.data.filepath,'objects':[],'materials':[]}
for o in sc.objects:
    d={'name':o.name,'type':o.type,'loc':list(o.location),'rot':list(o.rotation_euler),'scale':list(o.scale)}
    if o.type=='MESH':
        v=[o.matrix_world @ x.co for x in o.data.vertices]
        d['dims']=list(o.dimensions)
        d['verts']=len(v)
        d['faces']=len(o.data.polygons)
        d['bounds']={a:[min(x[i] for x in v),max(x[i] for x in v)] for i,a in enumerate('xyz')}
        d['z_levels']=sorted(set(round(x.z,3) for x in v))
        d['materials']=[m.name if m else None for m in o.data.materials]
        # vertices at each lower tier, local XY
        d['low_xy']=[[round(x.x,3),round(x.y,3),round(x.z,3)] for x in v if x.z<=min(z.z for z in v)+0.03]
        d['face_normals']=[{'n':[round(c,3) for c in f.normal],'verts':list(f.vertices)} for f in o.data.polygons if abs(f.normal.z)<0.05][:30]
    out['objects'].append(d)
for m in bpy.data.materials:
    pbr=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.node_tree else None
    out['materials'].append({'name':m.name,'color':list(pbr.inputs['Base Color'].default_value) if pbr else list(m.diffuse_color),'roughness':pbr.inputs['Roughness'].default_value if pbr else None})
print(json.dumps(out))
