import bpy, json
c=bpy.data.collections.get('WLIS_Exterior_Shell')
print('EXTERIOR_OBJECTS='+json.dumps([{'name':o.name,'type':o.type,'verts':len(o.data.vertices) if o.type=='MESH' else None,'polys':len(o.data.polygons) if o.type=='MESH' else None,'loc':list(o.location),'scale':list(o.scale)} for o in c.objects],separators=(',',':')))
