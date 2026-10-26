import bpy, json
out = {'filepath':bpy.data.filepath,'objects':[], 'collections':[]}
for c in bpy.data.collections:
    if c.name == 'Asset_massing_mcdonald_s_ab77b70':
        out['collections'].append({'name':c.name, 'objects':[o.name for o in c.objects]})
for o in bpy.data.objects:
    if o.name == "McDonald's" or any(c.name == 'Asset_massing_mcdonald_s_ab77b70' for c in o.users_collection):
        out['objects'].append({'name':o.name,'type':o.type,'loc':list(o.location),'rot':list(o.rotation_euler),'scale':list(o.scale),'verts':len(o.data.vertices) if o.type=='MESH' else None,'faces':len(o.data.polygons) if o.type=='MESH' else None,'collections':[c.name for c in o.users_collection]})
print(json.dumps(out,indent=2))
