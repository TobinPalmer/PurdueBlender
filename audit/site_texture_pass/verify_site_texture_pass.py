import bpy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SITE=ROOT/'modular'/'site'/'campus_site.blend'
bpy.ops.wm.open_mainfile(filepath=str(SITE))
updated=[m for m in bpy.data.materials if m.get('site_texture_pass')]
assert len(updated)==14, len(updated)
assert not [o for o in bpy.data.objects if o.name.startswith('QA_')]
lawn=bpy.data.materials['Manicured_Campus_Lawn']
assert not any(any(m==lawn for m in o.data.materials) for o in bpy.data.objects if o.type=='MESH')
assert bpy.data.materials['Manicured_Campus_Lawn'].use_fake_user
missing=[]
for m in updated:
 bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if not bs or not bs.inputs['Base Color'].is_linked or not bs.inputs['Normal'].is_linked or not bs.inputs['Roughness'].is_linked:
  missing.append(m.name)
assert not missing, missing
normal_targets=['Purdue_Road_Asphalt_Surface','Purdue_Elevated_Sidewalks_Wide','Purdue_Intersection_Crosswalk_Stripes','Purdue_Road_Yellow_Striping','Purdue_Dedicated_Green_Bike_Lanes']
downward={}
for name in normal_targets:
 obj=bpy.data.objects.get(name)
 assert obj and obj.type=='MESH', name
 downward[name]=sum(1 for p in obj.data.polygons if p.normal.z < -0.95)
assert not any(downward.values()), downward
print('REOPEN_OK',str(SITE))
print('TEXTURED_MATERIALS',len(updated),'OBJECT_COUNT',len(bpy.data.objects),'SCENES',len(bpy.data.scenes))
print('QA_OBJECTS_IN_SOURCE',sum(o.name.startswith('QA_') for o in bpy.data.objects))
print('ALL_MATERIAL_OUTPUTS_CONNECTED',not missing)
print('DOWNWARD_FACING_SURFACE_FACES',downward)

