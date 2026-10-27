import bpy,json
bpy.ops.wm.open_mainfile(filepath='modular/buildings/massing_house_301841602_8190d79.blend');o=bpy.data.objects['House_301841602']
p=[(round(v.co.x,6),round(v.co.y,6)) for v in o.data.vertices if v.co.z==0]
open('audit/alpha_chi_omega_fid765/source_massing_footprint_xy.json','w').write(json.dumps(p,indent=2))
