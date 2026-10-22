import bpy, json, math, os
from collections import Counter
p=bpy.data.filepath
r={'file':p,'version':bpy.app.version_string,'objects':len(bpy.data.objects),'types':dict(Counter(o.type for o in bpy.data.objects))}
r['scenes']=[{'name':s.name,'engine':s.render.engine,'camera':s.camera.name if s.camera else None} for s in bpy.data.scenes]
r['lights']=[{'name':l.name,'type':l.type,'energy':l.energy,'properties':{p.identifier:str(getattr(l,p.identifier)) for p in l.bl_rna.properties if 'shadow' in p.identifier}} for l in bpy.data.lights]
r['views']=[{'screen':s.name,'shading':a.spaces.active.shading.type,'clip_start':a.spaces.active.clip_start,'clip_end':a.spaces.active.clip_end} for s in bpy.data.screens for a in s.areas if a.type=='VIEW_3D']
r['invalid_transforms']=[o.name for o in bpy.data.objects if any(not math.isfinite(v) for row in o.matrix_world for v in row)]
r['mesh_totals']={'vertices':sum(len(m.vertices) for m in bpy.data.meshes),'faces':sum(len(m.polygons) for m in bpy.data.meshes)}
r['largest_meshes']=sorted([{'name':m.name,'verts':len(m.vertices),'faces':len(m.polygons)} for m in bpy.data.meshes],key=lambda x:x['verts'],reverse=True)[:10]
r['missing_files']=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not os.path.exists(bpy.path.abspath(i.filepath))]
open(os.path.join(os.path.dirname(p),'stability_audit.json'),'w').write(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
