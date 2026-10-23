import bpy,json,bmesh,os
P='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_hicks/'
r={}
for name in ['HIKS_Roof_Gravel_Ballast_Deck','HIKS_FloorSlab_Ground_Subterranean']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);r[name]={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'vertices':len(bm.verts),'faces':len(bm.faces)};bm.free()
c=bpy.data.collections['Asset_hicks_library'];r['export_objects']=len(c.all_objects);r['missing_images']=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not os.path.exists(bpy.path.abspath(i.filepath))];r['reopened']=True;json.dump(r,open(P+'technical.json','w'),indent=2);print(r)
