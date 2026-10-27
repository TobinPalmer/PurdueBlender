import bpy,bmesh,json,hashlib,os
from mathutils import Vector
path=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_house_301837281_58ead22.blend'
bpy.ops.wm.open_mainfile(filepath=path)
scene=bpy.data.scenes.get('Building_massing_house_301837281_58ead22')
col=bpy.data.collections.get('Asset_massing_house_301837281_58ead22')
assert scene and col
objs=list(col.all_objects)
meshobjs=[o for o in objs if o.type=='MESH']
report={'scene':scene.name,'collection':col.name,'object_count':len(objs),'mesh_objects':len(meshobjs),'object_types':{},'topology_totals':{'vertices':0,'edges':0,'faces':0,'nonmanifold_edges':0,'boundary_edges':0,'wire_edges':0},'materials':{},'assets':[]}
for o in objs: report['object_types'][o.type]=report['object_types'].get(o.type,0)+1
for o in meshobjs:
    me=o.data
    bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
    row={'name':o.name,'vertices':len(me.vertices),'edges':len(me.edges),'faces':len(me.polygons),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'boundary_edges':sum(e.is_boundary for e in bm.edges),'wire_edges':sum(len(e.link_faces)==0 for e in bm.edges),'materials':[m.name if m else None for m in me.materials]}
    report['topology_totals']['vertices']+=row['vertices']; report['topology_totals']['edges']+=row['edges']; report['topology_totals']['faces']+=row['faces']; report['topology_totals']['nonmanifold_edges']+=row['nonmanifold_edges']; report['topology_totals']['boundary_edges']+=row['boundary_edges']; report['topology_totals']['wire_edges']+=row['wire_edges']
    bm.free()
    report['assets'].append(row)
for m in bpy.data.materials:
    if any(any(slot and slot.name==m.name for slot in o.data.materials) for o in meshobjs):
      report['materials'][m.name]={'nodes':m.use_nodes,'diffuse_rgba':list(m.diffuse_color),'image_nodes':sum(n.type=='TEX_IMAGE' for n in m.node_tree.nodes) if m.use_nodes and m.node_tree else 0}
report['root']={'name':bpy.data.objects.get('House_301837281').name,'type':bpy.data.objects.get('House_301837281').type,'world_bounds':[[round(min((o.matrix_world@Vector(c))[i] for o in objs if o.type=='MESH' for c in o.bound_box),5),round(max((o.matrix_world@Vector(c))[i] for o in objs if o.type=='MESH' for c in o.bound_box),5)] for i in range(3)]}
with open(path,'rb') as f: report['sha256']=hashlib.sha256(f.read()).hexdigest().upper()
out=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\phi_gamma_delta\independent_grade\fresh_open_probe.json'
with open(out,'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='assets'},indent=2))

