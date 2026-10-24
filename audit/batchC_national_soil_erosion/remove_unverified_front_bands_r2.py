import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
asset=root/'modular'/'buildings'/'national_soil_erosion_laboratory.blend'
removed=[]
for o in list(bpy.data.objects):
    if 'horizontal datum' in o.name.lower() and o.name.endswith('.008'):
        removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(asset))
(root/'audit'/'batchC_national_soil_erosion'/'nsel_r2_removed_front_bands.json').write_text(json.dumps({'removed':removed,'reason':'unverified raised floor-level strips crossed the photo-supported blank brick elevation'},indent=2)+'\n')
