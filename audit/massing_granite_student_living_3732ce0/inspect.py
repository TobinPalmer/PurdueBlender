import bpy, json, math
from mathutils import Vector
p=bpy.data.filepath
out={'file':p,'objects':[],'collections':[]}
for o in bpy.data.objects:
    if o.type=='MESH':
      pts=[o.matrix_world @ Vector(c) for c in o.bound_box]
      out['objects'].append({'name':o.name,'type':o.type,'dims':list(o.dimensions),'loc':list(o.location),'bounds':[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)],'verts':len(o.data.vertices),'faces':len(o.data.polygons),'materials':[m.name if m else None for m in o.data.materials]})
for c in bpy.data.collections:
    out['collections'].append({'name':c.name,'objects':[o.name for o in c.objects],'children':[x.name for x in c.children]})
ref=r'C:/Users/gotse/Documents/Codex/2026-10-25/github-plugin-github-openai-curated-remote/outputs/PurdueBlender/audit/official_footprints_reference.blend'
try:
 with bpy.data.libraries.load(ref,link=False) as (src,dst): dst.collections=src.collections
 for c in list(bpy.data.collections):
    if c.name=='Official_Purdue_Footprints_Reference':
      for o in c.all_objects:
       pts=[o.matrix_world @ Vector(co) for co in o.bound_box]
       b=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
       if b[0][0]<500 and b[0][1]>425 and b[1][0]<-175 and b[1][1]>-255:
        out.setdefault('nearby_footprints',[]).append({'name':o.name,'bounds':b,'verts':len(o.data.vertices),'data':o.data.name})
except Exception as e: out['reference_error']=str(e)
open(r'C:/Users/gotse/Documents/Codex/2026-10-25/github-plugin-github-openai-curated-remote/outputs/PurdueBlender/audit/massing_granite_student_living_3732ce0/initial_geometry.json','w').write(json.dumps(out,indent=2))
