import bpy, json
bpy.ops.wm.open_mainfile(filepath=r'audit/alpha_gamma_delta_fid757/candidate_alpha_gamma_delta.blend')
o=bpy.data.objects['House_301841608'];m=o.data
xs=[v.co.x for v in m.vertices];ys=[v.co.y for v in m.vertices];mx=(min(xs)+max(xs))/2;my=(min(ys)+max(ys))/2
out={'xy_bounds':[min(xs),max(xs),min(ys),max(ys)],'mxmy':[mx,my],'near':{}}
for i,mat in enumerate(m.materials):
 ps=[p for p in m.polygons if p.material_index==i and p.center.z<3.45 and abs(p.center.x-(mx-7))<10 and abs(p.center.y-(my-6))<10]
 if ps:out['near'][mat.name]={'n':len(ps),'z':[min(p.center.z for p in ps),max(p.center.z for p in ps)],'xy':[[min(p.center.x for p in ps),max(p.center.x for p in ps)],[min(p.center.y for p in ps),max(p.center.y for p in ps)]]}
print(json.dumps(out,indent=2))
