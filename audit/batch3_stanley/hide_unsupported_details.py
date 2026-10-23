import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
for o in bpy.data.collections['SC_Roof_and_Dormers'].objects:
 if o.name.startswith('SC_Chimney_'):
  o.hide_render=True;o.hide_set(True);o['display_note']='Chimney count, height, and condition unverified in checked current and historic imagery; retained for review only.'
t=bpy.data.objects.get('SC_Portico_3D_Text')
if t:t.hide_render=True;t.hide_set(True);t['display_note']='Building-name lettering is not visible in the checked entrance photograph; omitted from presentation pending evidence.'
bpy.context.scene['SC current render note']='Unverified chimneys and facade lettering are kept in the asset library but hidden in renders.'
bpy.ops.wm.save_as_mainfile(filepath=p);print('hid unsupported roof fixtures and sign')
