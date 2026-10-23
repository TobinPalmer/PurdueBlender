import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
def ext(o):
    pts=[o.matrix_world@Vector(p) for p in o.bound_box]
    return ([round(min(v[i] for v in pts),6) for i in range(3)],[round(max(v[i] for v in pts),6) for i in range(3)])
rows=[]
for label,path in [('before',P/'audit/batch4_cl50/before.blend'),('current',P/'modular/buildings/class_of_1950.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(path));c=bpy.data.collections['Asset_class_of_1950'];meshes=[o for o in c.all_objects if o.type=='MESH']
    unmat=[o.name for o in meshes if not o.data.materials or all(m is None for m in o.data.materials)]
    root=bpy.data.objects['CL50_Root'];shell=bpy.data.objects['CL50_Corrected_GIS_Wall_Envelope'];roof=bpy.data.objects['CL50_Corrected_GIS_Roof_Slab']
    rows.append({'label':label,'object_count':len(c.all_objects),'mesh_count':len(meshes),'unmaterialed_meshes':unmat,'seats':sum('CL50_New_Seat_' in o.name for o in c.all_objects),'supported_tier_segments':sum('CL50_New_SupportedTier_' in o.name for o in c.all_objects),'root_location':tuple(round(x,6) for x in root.location),'root_rotation':tuple(round(x,6) for x in root.rotation_euler),'root_scale':tuple(round(x,6) for x in root.scale),'GIS_shell_bounds':ext(shell),'GIS_roof_bounds':ext(roof)})
a,b=rows
assert (a['root_location'],a['root_rotation'],a['root_scale'])==(b['root_location'],b['root_rotation'],b['root_scale'])
assert (a['GIS_shell_bounds'],a['GIS_roof_bounds'])==(b['GIS_shell_bounds'],b['GIS_roof_bounds'])
assert b['seats']==470 and b['supported_tier_segments']==480 and not b['unmaterialed_meshes']
(P/'audit/batch4_cl50/reopen_check.json').write_text(json.dumps({'result':'PASS','checks':['saved source re-opened','root transform unchanged','source GIS shell and roof bounds unchanged','470 auditorium seat meshes','480 supported tier segments','no unmaterialed mesh objects'],'buildings':rows,'overall_bounds_note':'Overall object bounds expand only through source-photo-informed column base/capital/soffit additions.'},indent=2))
print('PASS',json.dumps(rows,indent=2))
