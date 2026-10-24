import bpy
for f in [r'C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend',r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\campus_site.blend']:
 print('\nFILE',f)
 with bpy.data.libraries.load(f,link=True) as (src,dst):
  print('libraries',src.libraries if hasattr(src,'libraries') else '')
  print('collections',len(src.collections),'scenes',src.scenes)
  dst.collections=list(src.collections)
 print('linked libs',[l.filepath for l in bpy.data.libraries if l.filepath])
 print('scenes',[(s.name,len(s.objects)) for s in bpy.data.scenes])
 print('collections',[c.name for c in bpy.data.collections if 'site' in c.name.lower() or 'campus' in c.name.lower()][:40])
