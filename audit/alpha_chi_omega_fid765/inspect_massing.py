import bpy,json
f='modular/buildings/massing_house_301841602_8190d79.blend';bpy.ops.wm.open_mainfile(filepath=f)
C=bpy.data.collections['Asset_massing_house_301841602_8190d79'];o=bpy.data.objects['House_301841602'];
verts=[o.matrix_world@v.co for v in o.data.vertices]
out={'filepath':bpy.data.filepath,'collection':C.name,'object':o.name,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'v':len(o.data.vertices),'edges':len(o.data.edges),'faces':len(o.data.polygons),'bounds_world':[[min(p[i] for p in verts) for i in range(3)],[max(p[i] for p in verts) for i in range(3)]],'sample_vertices':[list(map(float,v)) for v in [o.data.vertices[0].co,o.data.vertices[1].co,o.data.vertices[-1].co]]}
open('audit/alpha_chi_omega_fid765/source_massing_inspection.json','w').write(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
