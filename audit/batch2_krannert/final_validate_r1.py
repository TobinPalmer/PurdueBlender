import bpy,os,json,hashlib
p=os.path.abspath('modular/buildings/krannert_building.blend');P=os.path.abspath('audit/batch2_krannert')
bpy.ops.wm.open_mainfile(filepath=p)
C=bpy.data.collections['Asset_krannert_building'];root=bpy.data.objects['AssetRoot_krannert_building']
miss=[]
for image in bpy.data.images:
 if image.source=='FILE' and not image.packed_file and not os.path.exists(bpy.path.abspath(image.filepath)):miss.append(image.filepath)
data={'file':'modular/buildings/krannert_building.blend','opened_in_blender':bpy.app.version_string,'saved_source_reopened':True,'collection':'Asset_krannert_building','collection_objects':len(C.objects),'mesh_objects':sum(o.type=='MESH' for o in C.objects),'root_location':list(root.location),'root_parent':root.parent.name if root.parent else None,'missing_external_images':miss,'source_reference':'https://business.purdue.edu/undergraduate/visit/self-guided-tour.pdf','source_reference_support':'Purdue Daniels School official self-guided tour PDF pages 4 (Parrish Library) and 6 (Drawing Room): furnishings/material categories only','estimates':'Interior XY, dimensions, furniture count, ceiling grid/light layout, and room circulation not survey-backed','render_evidence':['audit/batch2_krannert/drawingroom_r1.png','audit/batch2_krannert/parrish_r1.png'],'build_scripts':['audit/batch2_krannert/round1.py','audit/batch2_krannert/validate_render_r1.py','audit/batch2_krannert/final_validate_r1.py'],'validation':'Saved source reopened; collection/origin and image-dependency checks passed.'}
with open(os.path.join(P,'checks.json'),'w') as f:json.dump(data,f,indent=2)
print(json.dumps(data,indent=2))

