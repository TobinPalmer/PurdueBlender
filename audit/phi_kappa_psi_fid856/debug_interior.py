import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\phi_kappa_psi_fid856.blend')
for c in bpy.data.collections:
 if c.name in ('Asset_phi_kappa_psi_fid856','Interior_Schematic'):
  print(c.name,'hide',c.hide_render,'objects',len(c.objects),'children',[x.name for x in c.children])
for name in ['Leather lounge sofa lower frame','Leather lounge sofa seat cushion','Main stair tread 01','Wall-to-wall lounge carpet','Lounge east partition wall','Lounge west partition wall','Camera_schematic_lounge_cutaway']:
 o=bpy.data.objects.get(name)
 if o:print(name,'hide',o.hide_render,'loc',tuple(round(x,2) for x in o.location),'users', [c.name for c in o.users_collection])
