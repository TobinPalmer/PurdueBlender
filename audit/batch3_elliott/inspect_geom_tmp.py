import bpy,json,collections
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=p)
w=bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls']
vs=list(w.data.vertices); fs=list(w.data.polygons)
print('wall',len(vs),len(fs),'bounds', [min(v.co[i] for v in vs) for i in range(3)],[max(v.co[i] for v in vs) for i in range(3)])
print('z levels',collections.Counter(round(v.co.z,3) for v in vs))
print('first verts',[(round(v.co.x,2),round(v.co.y,2),round(v.co.z,2)) for v in vs[:20]])
print('face z samples',[(tuple(f.vertices),round(min(vs[i].co.z for i in f.vertices),2),round(max(vs[i].co.z for i in f.vertices),2)) for f in fs[:12]])
print('objects',[(o.name,o.type,tuple(round(x,2) for x in o.dimensions),len(o.data.polygons) if o.type=='MESH' else None) for o in bpy.data.collections['Asset_elliott_hall_of_music'].objects])
