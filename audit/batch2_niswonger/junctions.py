import bpy
c=bpy.data.collections['Asset_niswonger_aviation_tech']
for n in ['NISW_Walls_Purdue_Brick','NISW_Walls_Composite_Panel','NISW_Fenestration_Glazing']:
 o=bpy.data.objects[n]
 for v in o.data.vertices:
  if abs(v.co.z-.45)<.012:v.co.z=0
for y in [12,22,32,40]:
 ld=bpy.data.lights.new('NISW_Atrium_LinearLighting','AREA');ld.energy=450;ld.shape='RECTANGLE';ld.size=4;ld.size_y=1;ob=bpy.data.objects.new(ld.name,ld);c.objects.link(ob);ob.location=(12,y,7)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
