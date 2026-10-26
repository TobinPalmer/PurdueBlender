import bpy,json,os
from mathutils import Vector
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
path=os.path.join(root,'modular','buildings','massing_yue_kong_pao_hall_a3cb766.blend')
bpy.ops.wm.open_mainfile(filepath=path)
col=bpy.data.collections['Asset_massing_yue_kong_pao_hall_a3cb766']
items=[]
for name in ['Low south wing roof slab','High north performance roof slab']:
    o=bpy.data.objects.get(name); assert o
    deps=bpy.context.evaluated_depsgraph_get(); ev=o.evaluated_get(deps); me=ev.to_mesh()
    top=max((o.matrix_world @ v.co).z for v in me.vertices)
    faces=[]
    for poly in me.polygons:
        coords=[o.matrix_world @ me.vertices[i].co for i in poly.vertices]
        if coords and all(abs(v.z-top)<1e-4 for v in coords) and len(coords)>=3:
            faces.append([[round(v.x,6),round(v.y,6)] for v in coords])
    items.append({'object':name,'top_z':top,'face_count':len(faces),'top_faces_xy':faces})
    ev.to_mesh_clear()
out={'asset':path,'objects':items}
outp=os.path.join(root,'audit','yue_kong_pao_hall','independent_grade_r1_roof_footprints.json')
with open(outp,'w') as f:json.dump(out,f,indent=2)
print(json.dumps({'file':outp,'objects':[(x['object'],x['top_z'],x['face_count'],[len(f) for f in x['top_faces_xy']]) for x in items]}))
